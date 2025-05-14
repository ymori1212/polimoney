"""
pytestの設定ファイル
"""

import pytest
from unittest.mock import Mock, MagicMock
import requests
from bs4 import BeautifulSoup

from downloader.page_parser import PageParser, YearUrl, PageLink, PdfLink, LinkType


@pytest.fixture
def mock_session():
    """モックセッションを提供するフィクスチャ"""
    mock = Mock(spec=requests.Session)
    mock_response = Mock(spec=requests.Response)
    mock_response.text = ""
    mock_response.encoding = None
    mock.get.return_value = mock_response
    return mock, mock_response


@pytest.fixture
def mock_robots_checker():
    """モックrobots_checkerを提供するフィクスチャ"""
    mock = Mock()
    mock.can_fetch.return_value = True
    return mock


@pytest.fixture
def mock_sleep():
    """モックsleep関数を提供するフィクスチャ"""
    return Mock()


@pytest.fixture
def page_parser(mock_session, mock_robots_checker, mock_sleep):
    """PageParserインスタンスを提供するフィクスチャ"""
    session, _ = mock_session
    parser = PageParser(
        session=session,
        delay=0,
        robots_checker=mock_robots_checker,
        sleep_func=mock_sleep
    )
    return parser


@pytest.fixture
def soup_factory():
    """BeautifulSoupファクトリ関数を提供するフィクスチャ"""
    def factory(text, parser):
        return BeautifulSoup(text, parser)
    return factory