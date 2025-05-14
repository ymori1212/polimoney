"""
PDFダウンロードモジュール

政治資金収支報告書のPDFファイルをダウンロードするクラスを提供します。
"""

import os
import time
import logging
import requests
from typing import Dict, Optional
from dataclasses import dataclass
from tqdm import tqdm

from .utils import create_directory, sanitize_filename
from .metadata import FileMetadata

# ロガーの設定
logger = logging.getLogger(__name__)


@dataclass
class DownloadPrepareResult:
    """ダウンロード準備結果"""
    save_path: str
    category_dir: str
    metadata: FileMetadata


class PDFDownloader:
    """PDFダウンロードクラス"""

    def __init__(self, session: requests.Session, output_dir: str,
                 force: bool = False, dry_run: bool = False,
                 metadata_only: bool = False, delay: int = 5,
                 robots_checker = None) -> None:
        """初期化

        Args:
            session: リクエストセッション
            output_dir: 出力ディレクトリ
            force: 強制上書きフラグ
            dry_run: ドライランフラグ
            metadata_only: メタデータのみフラグ
            delay: リクエスト間の待機時間（秒）
        """
        self.session = session
        self.output_dir = output_dir
        self.force = force
        self.dry_run = dry_run
        self.metadata_only = metadata_only
        self.delay = delay
        self.robots_checker = robots_checker

    def prepare_download(self, pdf_url: str, org_name: str, year: str, 
                        category: str) -> DownloadPrepareResult:
        """ダウンロードの準備

        Args:
            pdf_url: PDFファイルのURL
            org_name: 団体名
            year: 公表年
            category: 団体カテゴリ

        Returns:
            DownloadPrepareResult: ダウンロード準備結果
        """
        logger.info("PDFダウンロードを準備しています: %s", org_name)
        
        # ファイル名を生成
        filename = f"{org_name}.pdf"
        safe_filename = sanitize_filename(filename)
        
        # 保存先パスを生成
        year_dir = os.path.join(self.output_dir, f"{year}年分")
        category_dir = os.path.join(year_dir, category)
        save_path = os.path.join(category_dir, safe_filename)
        
        # メタデータを準備
        file_metadata = FileMetadata(
            filename=os.path.join(f"{year}年分", category, safe_filename),
            original_url=pdf_url,
            organization=org_name,
            category=category,
            year=year
        )
        
        return DownloadPrepareResult(
            save_path=save_path,
            category_dir=category_dir,
            metadata=file_metadata
        )

    def check_existing_file(self, save_path: str, metadata: FileMetadata) -> Optional[FileMetadata]:
        """既存ファイルをチェック

        Args:
            save_path: 保存先パス
            metadata: ファイルメタデータ

        Returns:
            Optional[FileMetadata]: 既存ファイルがある場合は更新されたメタデータ、ない場合はNone
        """
        # 既存ファイルのチェック
        if os.path.exists(save_path) and not self.force:
            logger.info("ファイルが既に存在するためスキップします: %s", save_path)
            metadata.download_status = 'skipped'
            metadata.file_size = os.path.getsize(save_path)
            return metadata
        
        return None

    def download_pdf(self, pdf_url: str, save_path: str, category_dir: str, 
                    metadata: FileMetadata) -> FileMetadata:
        """PDFファイルをダウンロード

        Args:
            pdf_url: PDFファイルのURL
            save_path: 保存先パス
            category_dir: カテゴリディレクトリ
            metadata: ファイルメタデータ

        Returns:
            FileMetadata: 更新されたファイルメタデータ
        """
        # ドライランの場合は実際にダウンロードしない
        if self.dry_run:
            logger.info("ドライラン: %s をダウンロードします", save_path)
            metadata.download_status = 'dry_run'
            return metadata
        
        # メタデータのみの場合もダウンロードしない
        if self.metadata_only:
            logger.info("メタデータのみ: %s", save_path)
            metadata.download_status = 'metadata_only'
            return metadata
        
        # ディレクトリを作成
        if not create_directory(category_dir):
            logger.error("ディレクトリの作成に失敗したためスキップします: %s", category_dir)
            metadata.download_status = 'failed'
            metadata.error = 'ディレクトリの作成に失敗しました'
            return metadata
        
        # PDFをダウンロード
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info("PDFをダウンロードしています: %s", pdf_url)
                
                # robots.txtを確認
                if self.robots_checker and not self.robots_checker.can_fetch(pdf_url):
                    logger.warning("robots.txtによりアクセスが禁止されています: %s", pdf_url)
                    metadata.download_status = 'failed'
                    metadata.error = 'robots.txtによりアクセスが禁止されています'
                    return metadata
                
                # ストリーミングダウンロード
                response = self.session.get(pdf_url, stream=True)
                response.raise_for_status()
                
                # ファイルサイズを取得
                total_size = int(response.headers.get('content-length', 0))
                
                # プログレスバーを設定
                progress_bar = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=os.path.basename(save_path)
                )
                
                # ファイルに保存
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress_bar.update(len(chunk))
                
                progress_bar.close()
                
                # メタデータを更新
                metadata.download_status = 'success'
                metadata.file_size = os.path.getsize(save_path)
                metadata.download_date = time.strftime('%Y-%m-%dT%H:%M:%S')
                
                logger.info("ダウンロード完了: %s", save_path)
                
                # 成功時にもインターバルを設ける
                time.sleep(self.delay)
                break
                
            except requests.RequestException as e:
                retry_count += 1
                logger.warning("ダウンロード中にエラーが発生しました（リトライ %d/%d）: %s, エラー: %s",
                              retry_count, max_retries, pdf_url, e)
                
                if retry_count >= max_retries:
                    logger.error("最大リトライ回数に達しました: %s", pdf_url)
                    metadata.download_status = 'failed'
                    metadata.error = str(e)
                
                # 指数バックオフ
                time.sleep(self.delay * (2 ** (retry_count - 1)))
            
            except Exception as e:
                logger.error("ファイルの保存中にエラーが発生しました: %s, エラー: %s", save_path, e)
                metadata.download_status = 'failed'
                metadata.error = str(e)
                break
        
        return metadata