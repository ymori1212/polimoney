"""
政治資金収支報告書ダウンロードクラスモジュール

総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードするクラスを提供します。
"""

import logging
import time
from argparse import Namespace
from typing import List, Optional

import requests

from .config import FULL_USER_AGENT, MIN_DELAY
from .metadata import MetadataManager
from .page_parser import NameFilter, PageParser, PdfLink, ReportListPageUrl
from .pdf_downloader import PDFDownloader
from .robotparser import RobotsChecker

# ロガーの設定
logger = logging.getLogger(__name__)


class SeijishikinDownloader:
    """政治資金収支報告書ダウンロードを管理するクラス"""

    def __init__(self, args: Namespace) -> None:
        """初期化

        Args:
            args: コマンドライン引数
        """
        self.args = args
        self.output_dir: str = args.output_dir
        self.years: List[str] = args.year.split(",") if args.year else []
        self.categories: List[str] = args.category.split(",") if args.category else []
        self.name_filter: Optional[NameFilter] = (
            NameFilter(args.name, args.exact_match) if args.name else None
        )
        self.delay: int = max(args.delay, MIN_DELAY)  # 最小待機時間を保証
        self.force: bool = args.force
        self.dry_run: bool = args.dry_run
        self.metadata_only: bool = args.metadata_only

        # セッションの初期化
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": FULL_USER_AGENT})

        # robots.txtチェッカーの初期化
        self.robots_checker = RobotsChecker(FULL_USER_AGENT)

        # 各コンポーネントの初期化
        self.page_parser = PageParser(
            session=self.session,
            name_filter=self.name_filter,
            years=self.years,
            delay=self.delay,
            robots_checker=self.robots_checker,
        )

        self.pdf_downloader = PDFDownloader(
            session=self.session,
            output_dir=self.output_dir,
            force=self.force,
            dry_run=self.dry_run,
            metadata_only=self.metadata_only,
            delay=self.delay,
            robots_checker=self.robots_checker,
        )

        self.metadata_manager = MetadataManager(
            output_dir=self.output_dir,
            years=self.years,
            categories=self.categories,
            name_filter=self.name_filter.name if self.name_filter else None,
            exact_match=self.name_filter.exact_match if self.name_filter else False,
        )

        logger.info("SeijishikinDownloader を初期化しました")
        logger.debug(
            "設定: 出力先=%s, 年度=%s, カテゴリ=%s, 名前フィルタ=%s, 待機時間=%s秒, 強制上書き=%s, ドライラン=%s, メタデータのみ=%s",
            self.output_dir,
            self.years,
            self.categories,
            self.name_filter,
            self.delay,
            self.force,
            self.dry_run,
            self.metadata_only,
        )

    def download_all(self) -> bool:
        """指定された条件に基づいて全てのファイルをダウンロード

        Returns:
            bool: ダウンロード成功時はTrue、失敗時はFalse
        """
        logger.info("ダウンロード処理を開始します")

        # 年度ごとのURLを取得
        report_urls = self.page_parser.get_year_and_report_urls()
        if not report_urls:
            logger.error("ダウンロード対象の年度URLが見つかりませんでした")
            return False

        logger.info("%d 件の年度URLを取得しました", len(report_urls))

        # 各年度のページを処理
        for report_url in report_urls:
            if isinstance(report_url, ReportListPageUrl):
                logger.info(
                    "報告書一覧 %s の処理を開始します: %s",
                    report_url.year,
                    report_url.url,
                )
                self.process_report_list_page(report_url, report_url.year)
            else:
                logger.info(
                    "年度 %s の処理を開始します: %s", report_url.year, report_url.url
                )
                self.process_year_page(report_url.url, report_url.year)

            # 年度ページ処理後にインターバルを設ける
            if not self.dry_run:
                time.sleep(self.delay)

        # メタデータを保存
        self.metadata_manager.save()

        # 統計情報を表示
        stats = self.metadata_manager.get_statistics()
        logger.info(
            "ダウンロード完了: 合計=%d, ダウンロード=%d, スキップ=%d, 失敗=%d, 合計サイズ=%d バイト",
            stats.total_files,
            stats.downloaded_files,
            stats.skipped_files,
            stats.failed_files,
            stats.total_size,
        )

        return True

    def process_year_page(self, year_url: str, year: str) -> None:
        """年度ページを処理

        Args:
            year_url: 年度ページのURL
            year: 公表年（例: R5）
        """
        # 年度ページを解析
        links = self.page_parser.parse_year_page(year_url)

        # 各リンクを処理
        for link in links:
            self.process_report_list_page(link, year)

    def process_report_list_page(
        self, report_list_url: ReportListPageUrl, year: str
    ) -> None:
        """報告書一覧ページを処理

        Args:
            report_list_url: 報告書一覧ページのURL
            year: 公表年
        """
        # 報告書一覧ページを解析してリンクを取得
        pdf_links = self.page_parser.parse_report_list_page(report_list_url)

        # 各リンクを処理
        for pdf_link in pdf_links:
            if isinstance(pdf_link, PdfLink):
                if self.process_pdf_link(pdf_link, year):
                    # インターバルを設ける
                    if not self.dry_run:
                        time.sleep(self.delay)
            else:
                raise ValueError(f"想定外のリンク: {pdf_link.url}")

    def process_pdf_link(self, pdf_link: PdfLink, year: str) -> bool:
        """PDFリンクを処理

        Args:
            pdf_link: PDFファイルのURL
        """
        # カテゴリフィルタリング
        category_name = pdf_link.category_name()
        if self.categories and category_name not in self.categories:
            logger.debug("カテゴリをスキップ: %s", pdf_link.category_name())
            return False

        # ダウンロードの準備
        result = self.pdf_downloader.prepare_download(pdf_link, year)

        # 既存ファイルのチェック
        existing_metadata = self.pdf_downloader.check_existing_file(
            result.save_path, result.metadata
        )
        if existing_metadata:
            self.metadata_manager.add_file(existing_metadata)
            return False

        # PDFをダウンロード
        updated_metadata = self.pdf_downloader.download_pdf(
            pdf_link.url, result.save_path, result.metadata
        )

        # メタデータを追加
        self.metadata_manager.add_file(updated_metadata)

        return True
