"""
PDFダウンロードモジュール

政治資金収支報告書のPDFファイルをダウンロードするクラスを提供します。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import requests
from tqdm import tqdm

from .metadata import FileMetadata
from .utils import create_directory, sanitize_filename

# 型チェック用のインポート
if TYPE_CHECKING:
    from .page_parser import PdfLink

# ロガーの設定
logger = logging.getLogger(__name__)


class RobotsChecker(Protocol):
    """robots.txtチェッカーのプロトコル"""

    def can_fetch(self, url: str) -> bool:
        """URLがアクセス可能かどうかを確認する"""
        ...


@dataclass
class DownloadPrepareResult:
    """ダウンロード準備結果"""

    save_path: str
    metadata: FileMetadata


@dataclass
class DownloaderConfig:
    """ダウンローダー設定"""

    force: bool = False
    dry_run: bool = False
    metadata_only: bool = False
    delay: int = 5
    robots_checker: RobotsChecker | None = None


class PDFDownloader:
    """PDFダウンロードクラス"""

    def __init__(  # noqa: PLR0913
        self,
        session: requests.Session,
        output_dir: str,
        *,
        config: DownloaderConfig | None = None,
        force: bool = False,
        dry_run: bool = False,
        metadata_only: bool = False,
        delay: int = 5,
        robots_checker: RobotsChecker | None = None,
    ) -> None:
        """
        初期化

        Args:
            session: リクエストセッション
            output_dir: 出力ディレクトリ
            config: ダウンローダー設定
            force: 強制上書きフラグ
            dry_run: ドライランフラグ
            metadata_only: メタデータのみフラグ
            delay: リクエスト間の待機時間(秒)
            robots_checker: robots.txtチェッカー

        """
        self.session = session
        self.output_dir = output_dir

        if config is not None:
            self.force = config.force
            self.dry_run = config.dry_run
            self.metadata_only = config.metadata_only
            self.delay = config.delay
            self.robots_checker = config.robots_checker
        else:
            # 個別のパラメータを使用
            self.force = force
            self.dry_run = dry_run
            self.metadata_only = metadata_only
            self.delay = delay
            self.robots_checker = robots_checker

    def prepare_download(self, pdf_link: PdfLink, year: str) -> DownloadPrepareResult:
        """
        ダウンロードの準備

        Args:
            pdf_link: PDFファイルのリンク
            year: 公表年

        Returns:
            DownloadPrepareResult: ダウンロード準備結果

        """
        logger.info("PDFダウンロードを準備しています: %s", pdf_link.text)

        # ファイル名を生成
        link_name = f"{pdf_link.text}.pdf"
        safe_link_name = sanitize_filename(link_name)
        file_name = f"{year}_{pdf_link.category_name()}_{safe_link_name}"

        # 保存先パスを生成
        save_path = str(Path(self.output_dir) / file_name)

        # メタデータを準備
        file_metadata = FileMetadata(
            filename=file_name,
            original_url=pdf_link.url,
            organization=pdf_link.text,
            category=pdf_link.category_name(),
            year=year,
        )

        return DownloadPrepareResult(save_path=save_path, metadata=file_metadata)

    def check_existing_file(
        self,
        save_path: str,
        metadata: FileMetadata,
    ) -> FileMetadata | None:
        """
        既存ファイルをチェック

        Args:
            save_path: 保存先パス
            metadata: ファイルメタデータ

        Returns:
            FileMetadata | None: 既存ファイルがある場合は更新されたメタデータ、
                ない場合はNone

        """
        # 既存ファイルのチェック
        path_obj = Path(save_path)
        if path_obj.exists() and not self.force:
            logger.info("ファイルが既に存在するためスキップします: %s", save_path)
            metadata.download_status = "skipped"
            metadata.file_size = path_obj.stat().st_size
            return metadata

        return None

    def _handle_dry_run_metadata_only(
        self,
        save_path: str,
        metadata: FileMetadata,
    ) -> FileMetadata | None:
        """
        ドライランとメタデータのみの処理を行う

        Args:
            save_path: 保存先パス
            metadata: ファイルメタデータ

        Returns:
            FileMetadata | None: 処理された場合はメタデータ、そうでない場合はNone

        """
        # ドライランの場合は実際にダウンロードしない
        if self.dry_run:
            logger.info("ドライラン: %s をダウンロードします", save_path)
            metadata.download_status = "dry_run"
            return metadata

        # メタデータのみの場合もダウンロードしない
        if self.metadata_only:
            logger.info("メタデータのみ: %s", save_path)
            metadata.download_status = "metadata_only"
            return metadata

        return None

    def _download_with_progress(
        self,
        pdf_url: str,
        save_path: str,
    ) -> None:
        """単一のダウンロード試行を実行"""
        response = self.session.get(pdf_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        progress_bar = tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=Path(save_path).name,
        )

        with Path(save_path).open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

        progress_bar.close()

    def download_pdf(
        self,
        pdf_url: str,
        save_path: str,
        metadata: FileMetadata,
    ) -> FileMetadata:
        """
        PDFファイルをダウンロード

        Args:
            pdf_url: PDFファイルのURL
            save_path: 保存先パス
            metadata: ファイルメタデータ

        Returns:
            FileMetadata: 更新されたファイルメタデータ

        """
        # ドライランとメタデータのみの処理
        result = self._handle_dry_run_metadata_only(save_path, metadata)
        if result:
            return result

        # ディレクトリを作成
        if not create_directory(Path(save_path).parent):
            logger.error(
                "ディレクトリの作成に失敗したためスキップします: %s",
                save_path,
            )
            metadata.download_status = "failed"
            metadata.error = "ディレクトリの作成に失敗しました"
            return metadata

        # robots.txtを確認
        if self.robots_checker and not self.robots_checker.can_fetch(pdf_url):
            logger.warning(
                "robots.txtによりアクセスが禁止されています: %s",
                pdf_url,
            )
            metadata.download_status = "failed"
            metadata.error = "robots.txtによりアクセスが禁止されています"
            return metadata

        max_retries = 3
        success = False
        try:
            for retry_count in range(max_retries):
                try:
                    logger.info("PDFをダウンロードしています: %s", pdf_url)
                    self._download_with_progress(pdf_url, save_path)

                    # メタデータを更新
                    metadata.download_status = "success"
                    metadata.file_size = Path(save_path).stat().st_size
                    metadata.download_date = time.strftime("%Y-%m-%dT%H:%M:%S")

                    logger.info("ダウンロード完了: %s", save_path)
                    time.sleep(self.delay)
                    success = True
                    break
                except requests.RequestException as e:
                    logger.warning(
                        "ダウンロード中にエラーが発生しました(リトライ %d/%d): %s",
                        retry_count + 1,
                        max_retries,
                        pdf_url,
                    )
                    logger.warning("エラー詳細: %s", e)

                    if retry_count >= max_retries - 1:
                        logger.exception("最大リトライ回数に達しました: %s", pdf_url)
                        raise  # 最後のリトライでも失敗した場合は例外を再スロー
                    time.sleep(self.delay * (2**retry_count))
            if success:
                return metadata
        except requests.RequestException as e:
            # 最大リトライ回数に達した場合の処理
            metadata.download_status = "failed"
            metadata.error = str(e)
        except OSError as e:
            logger.exception(
                "ファイルの保存中にエラーが発生しました: %s",
                save_path,
            )
            metadata.download_status = "failed"
            metadata.error = str(e)
        return metadata
