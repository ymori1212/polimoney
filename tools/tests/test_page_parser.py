"""
PageParserクラスのテスト
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import requests
from bs4 import BeautifulSoup

from downloader.page_parser import PageParser, YearUrl, PageLink, PdfLink, LinkType
from downloader.config import BASE_URL


class TestPageParser(unittest.TestCase):
    """PageParserクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        # モックセッションの作成
        self.mock_session = Mock(spec=requests.Session)
        
        # モックレスポンスの作成
        self.mock_response = Mock(spec=requests.Response)
        self.mock_response.text = ""
        self.mock_response.encoding = None
        
        # モックsleep関数の作成（待機処理をスキップ）
        self.mock_sleep = Mock()
        
        # モックrobots_checkerの作成
        self.mock_robots_checker = Mock()
        self.mock_robots_checker.can_fetch.return_value = True
        
        # PageParserインスタンスの作成
        self.parser = PageParser(
            session=self.mock_session,
            delay=0,
            robots_checker=self.mock_robots_checker,
            sleep_func=self.mock_sleep
        )
        
        # モックレスポンスをセッションのgetメソッドの戻り値として設定
        self.mock_session.get.return_value = self.mock_response

    def test_fetch_url_success(self):
        """_fetch_urlメソッドが成功した場合のテスト"""
        # モックレスポンスの設定
        self.mock_response.text = "<html><body>テストページ</body></html>"
        
        # メソッドの実行
        result = self.parser._fetch_url("https://example.com")
        
        # 検証
        self.assertEqual(result, "<html><body>テストページ</body></html>")
        self.mock_session.get.assert_called_once_with("https://example.com")
        self.mock_sleep.assert_called_once_with(0)
        self.assertEqual(self.mock_response.encoding, "shift_jis")

    def test_fetch_url_robots_denied(self):
        """_fetch_urlメソッドがrobots.txtによりアクセス拒否された場合のテスト"""
        # robots_checkerの設定
        self.mock_robots_checker.can_fetch.return_value = False
        
        # メソッドの実行
        result = self.parser._fetch_url("https://example.com")
        
        # 検証
        self.assertIsNone(result)
        self.mock_session.get.assert_not_called()

    def test_fetch_url_request_exception(self):
        """_fetch_urlメソッドがリクエスト例外を発生させた場合のテスト"""
        # セッションのgetメソッドが例外を発生させるように設定
        self.mock_session.get.side_effect = requests.RequestException("テストエラー")
        
        # メソッドの実行
        result = self.parser._fetch_url("https://example.com")
        
        # 検証
        self.assertIsNone(result)

    def test_should_include_year_with_filter(self):
        """_should_include_yearメソッドが年度フィルタを適用する場合のテスト"""
        # 年度フィルタを設定
        self.parser.years = ["R5", "R6"]
        
        # 検証
        self.assertTrue(self.parser._should_include_year("R5"))
        self.assertTrue(self.parser._should_include_year("R6"))
        self.assertFalse(self.parser._should_include_year("R4"))

    def test_should_include_year_without_filter(self):
        """_should_include_yearメソッドが年度フィルタを適用しない場合のテスト"""
        # 年度フィルタを設定しない
        self.parser.years = []
        
        # 検証
        self.assertTrue(self.parser._should_include_year("R5"))
        self.assertTrue(self.parser._should_include_year("R4"))

    def test_should_include_organization_with_exact_match(self):
        """_should_include_organizationメソッドが完全一致フィルタを適用する場合のテスト"""
        # 団体名フィルタと完全一致フラグを設定
        self.parser.name_filter = "テスト団体"
        self.parser.exact_match = True
        
        # 検証
        self.assertTrue(self.parser._should_include_organization("テスト団体"))
        self.assertFalse(self.parser._should_include_organization("テスト団体A"))

    def test_should_include_organization_with_partial_match(self):
        """_should_include_organizationメソッドが部分一致フィルタを適用する場合のテスト"""
        # 団体名フィルタと部分一致フラグを設定
        self.parser.name_filter = "テスト"
        self.parser.exact_match = False
        
        # 検証
        self.assertTrue(self.parser._should_include_organization("テスト団体"))
        self.assertTrue(self.parser._should_include_organization("テスト団体A"))
        self.assertFalse(self.parser._should_include_organization("サンプル団体"))

    def test_should_include_organization_without_filter(self):
        """_should_include_organizationメソッドが団体名フィルタを適用しない場合のテスト"""
        # 団体名フィルタを設定しない
        self.parser.name_filter = None
        
        # 検証
        self.assertTrue(self.parser._should_include_organization("テスト団体"))
        self.assertTrue(self.parser._should_include_organization("サンプル団体"))

    def test_get_year_urls(self):
        """get_year_urlsメソッドのテスト"""
        # モックHTMLの作成
        html = """
        <html>
        <body>
            <a href="/senkyo/seiji_s/seijishikin/reports/SS20241129/">令和5年分</a>
            <a href="/senkyo/seiji_s/seijishikin/reports/SS20231124/">令和4年分</a>
            <a href="/senkyo/seiji_s/seijishikin/reports/SS20221125/">令和3年分</a>
            <a href="other.html">その他のリンク</a>
        </body>
        </html>
        """
        self.mock_response.text = html
        
        # モックBeautifulSoupファクトリの作成
        def mock_soup_factory(text, parser):
            soup = BeautifulSoup(text, parser)
            return soup
        
        self.parser.soup_factory = mock_soup_factory
        
        # メソッドの実行
        result = self.parser.get_year_urls()
        
        # 検証
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].url, "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/reports/SS20241129/")
        self.assertEqual(result[0].year, "R5")
        self.assertEqual(result[1].url, "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/reports/SS20231124/")
        self.assertEqual(result[1].year, "R4")
        self.assertEqual(result[2].url, "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/reports/SS20221125/")
        self.assertEqual(result[2].year, "R3")

    def test_get_year_urls_with_year_filter(self):
        """get_year_urlsメソッドが年度フィルタを適用する場合のテスト"""
        # 年度フィルタを設定
        self.parser.years = ["R5"]
        
        # モックHTMLの作成
        html = """
        <html>
        <body>
            <a href="/senkyo/seiji_s/seijishikin/reports/SS20241129/">令和5年分</a>
            <a href="/senkyo/seiji_s/seijishikin/reports/SS20231124/">令和4年分</a>
            <a href="/senkyo/seiji_s/seijishikin/reports/SS20221125/">令和3年分</a>
        </body>
        </html>
        """
        self.mock_response.text = html
        
        # モックBeautifulSoupファクトリの作成
        def mock_soup_factory(text, parser):
            soup = BeautifulSoup(text, parser)
            return soup
        
        self.parser.soup_factory = mock_soup_factory
        
        # メソッドの実行
        result = self.parser.get_year_urls()
        
        # 検証
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].url, "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/reports/SS20241129/")
        self.assertEqual(result[0].year, "R5")

    def test_parse_year_page_with_direct_pdf_links(self):
        """parse_year_pageメソッドが直接PDFリンクを見つける場合のテスト"""
        # モックHTMLの作成
        html = """
        <html>
        <body>
            <a href="test1.pdf">テスト団体1</a>
            <a href="test2.pdf">テスト団体2</a>
            <a href="other.html">その他のリンク</a>
        </body>
        </html>
        """
        self.mock_response.text = html
        
        # モックBeautifulSoupファクトリの作成
        def mock_soup_factory(text, parser):
            soup = BeautifulSoup(text, parser)
            return soup
        
        self.parser.soup_factory = mock_soup_factory
        
        # メソッドの実行
        result = self.parser.parse_year_page("https://example.com/year")
        
        # 検証
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].url, "https://example.com/year/test1.pdf")
        self.assertEqual(result[0].text, "テスト団体1")
        self.assertEqual(result[0].link_type, LinkType.PDF)
        self.assertEqual(result[1].url, "https://example.com/year/test2.pdf")
        self.assertEqual(result[1].text, "テスト団体2")
        self.assertEqual(result[1].link_type, LinkType.PDF)

    def test_parse_year_page_with_category_links(self):
        """parse_year_pageメソッドがカテゴリリンクを見つける場合のテスト"""
        # モックHTMLの作成
        html = """
        <html>
        <body>
            <h2>政党本部</h2>
            <a href="party1.html">テスト政党1</a>
            <a href="party2.pdf">テスト政党2</a>
            
            <h2>政党支部</h2>
            <a href="branch1.html">テスト支部1</a>
            <a href="branch2.pdf">テスト支部2</a>
        </body>
        </html>
        """
        self.mock_response.text = html
        
        # モックBeautifulSoupファクトリの作成
        def mock_soup_factory(text, parser):
            soup = BeautifulSoup(text, parser)
            return soup
        
        self.parser.soup_factory = mock_soup_factory
        
        # メソッドの実行
        result = self.parser.parse_year_page("https://example.com/year")
        
        # 検証
        self.assertEqual(len(result), 4)
        # 政党本部カテゴリのリンク
        self.assertEqual(result[0].url, "https://example.com/year/party1.html")
        self.assertEqual(result[0].text, "テスト政党1")
        self.assertEqual(result[0].link_type, LinkType.ORGANIZATION)
        self.assertEqual(result[1].url, "https://example.com/year/party2.pdf")
        self.assertEqual(result[1].text, "テスト政党2")
        self.assertEqual(result[1].link_type, LinkType.PDF)
        # 政党支部カテゴリのリンク
        self.assertEqual(result[2].url, "https://example.com/year/branch1.html")
        self.assertEqual(result[2].text, "テスト支部1")
        self.assertEqual(result[2].link_type, LinkType.ORGANIZATION)
        self.assertEqual(result[3].url, "https://example.com/year/branch2.pdf")
        self.assertEqual(result[3].text, "テスト支部2")
        self.assertEqual(result[3].link_type, LinkType.PDF)

    def test_parse_organization_page(self):
        """parse_organization_pageメソッドのテスト"""
        # モックHTMLの作成
        html = """
        <html>
        <body>
            <a href="report1.pdf">収支報告書1</a>
            <a href="report2.pdf">収支報告書2</a>
            <a href="other.html">その他のリンク</a>
        </body>
        </html>
        """
        self.mock_response.text = html
        
        # モックBeautifulSoupファクトリの作成
        def mock_soup_factory(text, parser):
            soup = BeautifulSoup(text, parser)
            return soup
        
        self.parser.soup_factory = mock_soup_factory
        
        # メソッドの実行
        result = self.parser.parse_organization_page("https://example.com/org", "テスト団体")
        
        # 検証
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].url, "https://example.com/org/report1.pdf")
        self.assertEqual(result[0].text, "収支報告書1")
        self.assertEqual(result[1].url, "https://example.com/org/report2.pdf")
        self.assertEqual(result[1].text, "収支報告書2")

    def test_parse_organization_page_with_name_filter(self):
        """parse_organization_pageメソッドが団体名フィルタを適用する場合のテスト"""
        # 団体名フィルタを設定
        self.parser.name_filter = "収支報告書1"
        self.parser.exact_match = True
        
        # モックHTMLの作成
        html = """
        <html>
        <body>
            <a href="report1.pdf">収支報告書1</a>
            <a href="report2.pdf">収支報告書2</a>
        </body>
        </html>
        """
        self.mock_response.text = html
        
        # モックBeautifulSoupファクトリの作成
        def mock_soup_factory(text, parser):
            soup = BeautifulSoup(text, parser)
            return soup
        
        self.parser.soup_factory = mock_soup_factory
        
        # メソッドの実行
        result = self.parser.parse_organization_page("https://example.com/org", "テスト団体")
        
        # 検証
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].url, "https://example.com/org/report1.pdf")
        self.assertEqual(result[0].text, "収支報告書1")


if __name__ == "__main__":
    unittest.main()