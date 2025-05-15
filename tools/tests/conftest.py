"""pytestの設定ファイル"""

from typing import Callable
from unittest.mock import Mock

import pytest
import requests
from bs4 import BeautifulSoup

from downloader.page_parser import PageParser


@pytest.fixture
def mock_session() -> tuple[Mock, Mock]:
    """モックセッションを提供するフィクスチャ"""
    mock = Mock(spec=requests.Session)
    mock_response = Mock(spec=requests.Response)
    mock_response.text = ""
    mock_response.encoding = None
    mock.get.return_value = mock_response
    return mock, mock_response


@pytest.fixture
def mock_robots_checker() -> Mock:
    """モックrobots_checkerを提供するフィクスチャ"""
    mock = Mock()
    mock.can_fetch.return_value = True
    return mock


@pytest.fixture
def mock_sleep() -> Mock:
    """モックsleep関数を提供するフィクスチャ"""
    return Mock()


@pytest.fixture
def page_parser(
    mock_session: tuple[Mock, Mock],
    mock_robots_checker: Mock,
    mock_sleep: Mock,
) -> PageParser:
    """PageParserインスタンスを提供するフィクスチャ"""
    session, _ = mock_session
    return PageParser(
        session=session,
        delay=0,
        robots_checker=mock_robots_checker,
        sleep_func=mock_sleep,
    )


@pytest.fixture
def soup_factory() -> Callable[[str, str], BeautifulSoup]:
    """BeautifulSoupファクトリ関数を提供するフィクスチャ"""

    def factory(text: str, parser: str) -> BeautifulSoup:
        return BeautifulSoup(text, parser)

    return factory
