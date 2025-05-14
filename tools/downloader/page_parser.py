"""
ページ解析モジュール

政治資金収支報告書のウェブページを解析するクラスを提供します。
"""

import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Union
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .config import BASE_URL, YEAR_PATTERNS
from .utils import extract_year_from_url

# ロガーの設定
logger = logging.getLogger(__name__)


@dataclass
class NameFilter:
    name: str
    exact_match: bool

@dataclass
class YearPageUrl:
    """年度URL"""
    url: str
    year: str

@dataclass
class ReportListPageUrl:
    """報告書一覧URL"""
    url: str
    text: str
    category: str
    year: str

@dataclass
class PageLink:
    """ページリンク"""
    url: str
    text: str

class Category(Enum):
    """カテゴリ名"""
    POLITICAL_PARTY_HEADQUARTER = '政党本部'
    POLITICAL_PARTY_BRANCH = '政党支部'
    POLITICAL_FUND_GROUP = '政治資金団体'
    POLITICAL_GROUP = '国会議員関係政治団体'
    OTHER_POLITICAL_GROUP = 'その他の政治団体'
    UNKNOWN = '不明'

@dataclass
class PdfLink:
    """PDFリンク"""
    url: str
    text: str

    # PDFリンクURLに含まれるコード値からカテゴリを取得する
    def category_id(self) -> str:
        org_id = self.url.split('/')[-1]
        return org_id[0:3]
    
    def category_name(self) -> str:
        return self.category().value

    def category(self) -> Category:
        category_id = self.category_id()

        match category_id:
            case '000':
                return Category.POLITICAL_PARTY_HEADQUARTER
            case '001' | '002' | '003' | '004' | '005' | '006' | '007' | '008' | '009':
                return Category.POLITICAL_PARTY_BRANCH
            case '006':
                return Category.POLITICAL_FUND_GROUP
            case '100':
                return Category.POLITICAL_GROUP
            case '200':
                return Category.OTHER_POLITICAL_GROUP
            case _:
                return Category.UNKNOWN




class PageParser:
    """ページ解析クラス"""

    def __init__(self, session: requests.Session, name_filter: Optional[NameFilter] = None,
                 years: Optional[List[str]] = None,
                 delay: int = 5, robots_checker = None, 
                 sleep_func: Callable[[int], None] = time.sleep,
                 soup_factory: Callable[[str, str], BeautifulSoup] = None) -> None:
        """初期化

        Args:
            session: リクエストセッション
            name_filter: 団体名フィルタ
            exact_match: 完全一致フラグ
            years: 対象年度のリスト
            delay: リクエスト間の待機時間（秒）
            robots_checker: robots.txtチェッカー
            sleep_func: 待機処理を行う関数（テスト時にモック可能）
            soup_factory: BeautifulSoupオブジェクトを生成する関数（テスト時にモック可能）
        """
        self.session = session
        self.name_filter = name_filter
        self.years = years or []
        self.delay = delay
        self.robots_checker = robots_checker
        self.sleep_func = sleep_func
        self.soup_factory = soup_factory or (lambda text, parser: BeautifulSoup(text, parser))

    def _ensure_url_ends_with_slash(self, url: str) -> str:
        """URLの末尾にスラッシュがない場合は追加する

        Args:
            url: URL

        Returns:
            str: スラッシュで終わるURL
        """
        if not url.endswith('/'):
            return url + '/'
        return url

    def _fetch_url(self, url: str) -> Optional[str]:
        """URLからHTMLを取得

        Args:
            url: 取得するURL

        Returns:
            Optional[str]: 取得したHTML、失敗した場合はNone
        """
        try:
            # robots.txtを確認
            if self.robots_checker and not self.robots_checker.can_fetch(url):
                logger.warning("robots.txtによりアクセスが禁止されています: %s", url)
                return None
                
            # ページを取得
            response = self.session.get(url)
            response.raise_for_status()
            
            # インターバルを設ける
            self.sleep_func(self.delay)
            
            # 文字コードを設定
            response.encoding = 'shift_jis'
            
            return response.text
            
        except requests.RequestException as e:
            logger.error("ページの取得に失敗しました: %s, エラー: %s", url, e)
            return None

    def _create_soup(self, html: str) -> BeautifulSoup:
        """HTMLからBeautifulSoupオブジェクトを生成

        Args:
            html: HTML文字列

        Returns:
            BeautifulSoup: 生成したBeautifulSoupオブジェクト
        """
        return self.soup_factory(html, 'html.parser')

    def _should_include_year(self, year: str) -> bool:
        """指定された年度を含めるべきかどうかを判断

        Args:
            year: 年度

        Returns:
            bool: 含める場合はTrue、そうでない場合はFalse
        """
        return not self.years or year in self.years

    def _extract_year_urls_from_soup(self, soup: BeautifulSoup, base_url: str, seasonal_report_only: bool) -> List[YearPageUrl]:
        """BeautifulSoupオブジェクトから年度URLを抽出

        Args:
            soup: BeautifulSoupオブジェクト
            base_url: ベースURL
            seasonal_report_only: 定期公表のみをチェックするかどうか

        Returns:
            List[YearUrl]: 年度URLのリスト
        """
        year_urls: List[YearPageUrl] = []
        
        # 「令和X年分」などのパターンを含むリンクを探す
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text()
            
            if not href:
                continue
            
            # デバッグ: すべてのリンクを表示
            logger.debug("リンク: %s, テキスト: %s", href, text)
            
            # 特定のURLパターンを直接チェック
            if '/reports/' in href and any(re.search(pattern, text) for pattern in YEAR_PATTERNS):
                if seasonal_report_only and not '/reports/SS' in href:
                    continue

                # 例: /senkyo/seiji_s/seijishikin/reports/SS20241129/
                full_url = urljoin(base_url, href)
                year = extract_year_from_url(text)
                
                if year and self._should_include_year(year):
                    if '/reports/SS' in href:
                        year_urls.append(YearPageUrl(url=full_url, year=year))
                        logger.debug("年度URLを追加: %s (%s)", full_url, year)
                    else:
                        year_urls.append(ReportListPageUrl(url=full_url, year=year))
                        logger.debug("報告書一覧URLを追加: %s (%s)", full_url, year)
        
        return year_urls

    def get_year_and_report_urls(self) -> List[Union[YearPageUrl, ReportListPageUrl]]:
        """公表年ごとのURLを取得

        Returns:
            List[YearUrl]: 年度URLのリスト
        """
        logger.info("公表年ごとのURLを取得しています")
        
        html = self._fetch_url(BASE_URL)
        if not html:
            return []
            
        soup = self._create_soup(html)
        return self._extract_year_urls_from_soup(soup, BASE_URL, seasonal_report_only=True)

    def _extract_report_list_links(self, soup: BeautifulSoup, base_url: str) -> List[PageLink]:
        """BeautifulSoupオブジェクトから報告書一覧リンクを抽出

        Args:
            soup: BeautifulSoupオブジェクト
            base_url: ベースURL

        Returns:
            List[PageLink]: ページリンクのリスト
        """
        # URLの末尾にスラッシュがあることを確認
        base_url = self._ensure_url_ends_with_slash(base_url)
        links: List[PageLink] = []
        
        report_link_regex = re.compile(r'.*/reports/[A-Z]+[0-9]+/[A-Z]+/[a-zA-Z0-9]+\.html$')
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text().strip()
            
            if not href or not text:
                continue
            
            if report_link_regex.match(href):
                report_url = urljoin(base_url, href)
                links.append(PageLink(url=report_url, text=text))
        
        return links

    def _extract_direct_pdf_links(self, soup: BeautifulSoup, base_url: str) -> List[PageLink]:
        """BeautifulSoupオブジェクトから直接PDFリンクを抽出

        Args:
            soup: BeautifulSoupオブジェクト
            base_url: ベースURL

        Returns:
            List[PageLink]: ページリンクのリスト
        """
        # URLの末尾にスラッシュがあることを確認
        base_url = self._ensure_url_ends_with_slash(base_url)
        links: List[PageLink] = []
        
        for link in soup.find_all('a'):
            href = link.get('href')
            text = link.get_text().strip()
            
            if not href or not text:
                continue
            
            # PDFへの直接リンクかどうかを確認
            if href.lower().endswith('.pdf'):
                pdf_url = urljoin(base_url, href)
                links.append(PdfLink(url=pdf_url, text=text))
        
        return links

    def _find_category_header(self, soup: BeautifulSoup, section_text: str) -> Optional[object]:
        """カテゴリ見出しを探す

        Args:
            soup: BeautifulSoupオブジェクト
            section_text: セクションテキスト

        Returns:
            Optional[object]: 見つかった場合はBeautifulSoupオブジェクト、見つからない場合はNone
        """
        # 方法1: 見出しタグ内のテキスト
        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if section_text in header.get_text():
                logger.debug("カテゴリ見出しを見つけました(見出しタグ): %s", section_text)
                return header
        
        # 方法2: テキストを含む要素
        for element in soup.find_all(string=re.compile(section_text)):
            logger.debug("カテゴリ見出しを見つけました(テキスト要素): %s", section_text)
            return element.parent
        
        # 方法3: リンクテキスト
        for link in soup.find_all('a'):
            if section_text in link.get_text():
                logger.debug("カテゴリ見出しを見つけました(リンク): %s", section_text)
                return link
        
        # 方法4: 特定のクラスやIDを持つ要素
        for div in soup.find_all('div', class_=re.compile('(category|section|title)')):
            if section_text in div.get_text():
                logger.debug("カテゴリ見出しを見つけました(div): %s", section_text)
                return div
        
        return None

    def parse_year_page(self, year_url: str) -> List[PageLink]:
        """年度ページを解析し、PDFリンクまたは団体ページへのリンクを取得

        Args:
            year_url: 年度ページのURL

        Returns:
            List[PageLink]: ページリンクのリスト
        """
        logger.info("年度ページを解析しています: %s", year_url)
        
        html = self._fetch_url(year_url)
        if not html:
            return []
            
        soup = self._create_soup(html)
        
        report_list_links = self._extract_report_list_links(soup, year_url)
        if report_list_links:
            logger.info("報告書一覧リンクを見つけました: %d件", len(report_list_links))
            return report_list_links
        else:
            logger.warning("報告書一覧リンクが見つかりませんでした: %s", year_url)
        
        return []

    def parse_report_list_page(self, report_list_url: ReportListPageUrl) -> List[PageLink]:
        """報告書一覧ページを解析し、PDFリンクを取得

        Args:
            report_list_url: 報告書一覧ページのURL

        Returns:
            List[PageLink]: ページリンクのリスト
        """
        logger.info("報告書一覧ページを解析しています: %s", report_list_url.url)
        
        html = self._fetch_url(report_list_url.url)
        if not html:
            return []
            
        soup = self._create_soup(html)
        
        pdf_links = self._extract_direct_pdf_links(soup, report_list_url.url)
        if self.name_filter:
            if self.name_filter.exact_match:
                pdf_links = [link for link in pdf_links if self.name_filter.name == link.text]
            else:
                pdf_links = [link for link in pdf_links if self.name_filter.name in link.text]

        return pdf_links
