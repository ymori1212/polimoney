"""
政治資金収支報告書ダウンロードクラスモジュール

総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードするクラスを提供します。
"""

import time
import logging
import requests
from typing import List, Dict, Optional, Any, Set
from argparse import Namespace

from .config import DEFAULT_OUTPUT_DIR, DEFAULT_DELAY, MIN_DELAY, DEFAULT_PARALLEL, FULL_USER_AGENT
from .robotparser import RobotsChecker
from .page_parser import PageParser, LinkType
from .pdf_downloader import PDFDownloader, DownloadPrepareResult
from .metadata import MetadataManager, FileMetadata

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
        self.years: List[str] = args.year.split(',') if args.year else []
        self.categories: List[str] = args.category.split(',') if args.category else []
        self.name_filter: Optional[str] = args.name
        self.exact_match: bool = args.exact_match
        self.delay: int = max(args.delay, MIN_DELAY)  # 最小待機時間を保証
        self.parallel: int = args.parallel
        self.force: bool = args.force
        self.dry_run: bool = args.dry_run
        self.metadata_only: bool = args.metadata_only
        
        # セッションの初期化
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': FULL_USER_AGENT})
        
        # robots.txtチェッカーの初期化
        self.robots_checker = RobotsChecker(FULL_USER_AGENT)
        
        # 各コンポーネントの初期化
        self.page_parser = PageParser(
            session=self.session,
            name_filter=self.name_filter,
            exact_match=self.exact_match,
            years=self.years,
            delay=self.delay,
            robots_checker=self.robots_checker
        )
        
        self.pdf_downloader = PDFDownloader(
            session=self.session,
            output_dir=self.output_dir,
            force=self.force,
            dry_run=self.dry_run,
            metadata_only=self.metadata_only,
            delay=self.delay,
            robots_checker=self.robots_checker
        )
        
        self.metadata_manager = MetadataManager(
            output_dir=self.output_dir,
            years=self.years,
            categories=self.categories,
            name_filter=self.name_filter,
            exact_match=self.exact_match
        )
        
        logger.info("SeijishikinDownloader を初期化しました")
        logger.debug("設定: 出力先=%s, 年度=%s, カテゴリ=%s, 名前フィルタ=%s, 完全一致=%s, 待機時間=%s秒, 並列数=%s, 強制上書き=%s, ドライラン=%s, メタデータのみ=%s",
                    self.output_dir, self.years, self.categories, self.name_filter, self.exact_match,
                    self.delay, self.parallel, self.force, self.dry_run, self.metadata_only)
    
    def download_all(self) -> bool:
        """指定された条件に基づいて全てのファイルをダウンロード

        Returns:
            bool: ダウンロード成功時はTrue、失敗時はFalse
        """
        logger.info("ダウンロード処理を開始します")
        
        # 年度ごとのURLを取得
        year_urls = self.page_parser.get_year_urls()
        if not year_urls:
            logger.error("ダウンロード対象の年度URLが見つかりませんでした")
            return False
        
        logger.info("%d 件の年度URLを取得しました", len(year_urls))
        
        # 各年度のページを処理
        for year_url in year_urls:
            logger.info("年度 %s の処理を開始します: %s", year_url.year, year_url.url)
            self.process_year_page(year_url.url, year_url.year)
            
            # 年度ページ処理後にインターバルを設ける
            if not self.dry_run:
                time.sleep(self.delay)
            
        # メタデータを保存
        self.metadata_manager.save()
        
        # 統計情報を表示
        stats = self.metadata_manager.get_statistics()
        logger.info("ダウンロード完了: 合計=%d, ダウンロード=%d, スキップ=%d, 失敗=%d, 合計サイズ=%d バイト",
                   stats.total_files, stats.downloaded_files, stats.skipped_files,
                   stats.failed_files, stats.total_size)
        
        return True
    
    def process_year_page(self, year_url: str, year: str) -> None:
        """年度ページを処理

        Args:
            year_url: 年度ページのURL
            year: 公表年（例: R5）
        """
        # 年度ページを解析してリンクを取得
        links = self.page_parser.parse_year_page(year_url)
        
        # 各リンクを処理
        for link in links:
            # カテゴリをチェック（PDFリンクの場合はデフォルトで「政党支部」とする）
            category = "政党支部"
            
            # リンクタイプに応じて処理
            if link.link_type == LinkType.PDF:
                self.process_pdf_link(link.url, year, category, link.text)
            elif link.link_type == LinkType.ORGANIZATION:
                self.process_organization_page(link.url, year, category, link.text)
            
            # 待機
            if not self.dry_run:
                time.sleep(self.delay)
    
    def process_organization_page(self, org_url: str, year: str, category: str, org_name: str) -> None:
        """団体ページを処理

        Args:
            org_url: 団体ページのURL
            year: 公表年
            category: 団体カテゴリ
            org_name: 団体名
        """
        # 団体ページを解析してPDFリンクを取得
        pdf_links = self.page_parser.parse_organization_page(org_url, org_name)
        
        # 各PDFリンクを処理
        for pdf_link in pdf_links:
            # PDFをダウンロード
            self.process_pdf_link(pdf_link.url, year, category, pdf_link.text or org_name)
            
            # 待機
            if not self.dry_run:
                time.sleep(self.delay)
    
    def process_pdf_link(self, pdf_url: str, year: str, category: str, org_name: str) -> None:
        """PDFリンクを処理

        Args:
            pdf_url: PDFファイルのURL
            year: 公表年
            category: 団体カテゴリ
            org_name: 団体名
        """
        # カテゴリフィルタリング
        if self.categories and category not in self.categories:
            logger.debug("カテゴリをスキップ: %s", category)
            return
        
        # ダウンロードの準備
        result = self.pdf_downloader.prepare_download(
            pdf_url, org_name, year, category
        )
        
        # 既存ファイルのチェック
        existing_metadata = self.pdf_downloader.check_existing_file(result.save_path, result.metadata)
        if existing_metadata:
            self.metadata_manager.add_file(existing_metadata)
            return
        
        # PDFをダウンロード
        updated_metadata = self.pdf_downloader.download_pdf(
            pdf_url, result.save_path, result.category_dir, result.metadata
        )
        
        # メタデータを追加
        self.metadata_manager.add_file(updated_metadata)