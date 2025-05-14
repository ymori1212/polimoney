"""
政治資金収支報告書ダウンロードパッケージ

総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードするためのパッケージです。
"""

from .config import DEFAULT_OUTPUT_DIR, DEFAULT_DELAY, MIN_DELAY, DEFAULT_PARALLEL, FULL_USER_AGENT
from .downloader import SeijishikinDownloader
from .page_parser import PageParser
from .pdf_downloader import PDFDownloader
from .metadata import MetadataManager
from .robotparser import RobotsChecker

__all__ = [
    'SeijishikinDownloader',
    'PageParser',
    'PDFDownloader',
    'MetadataManager',
    'RobotsChecker',
    'DEFAULT_OUTPUT_DIR',
    'DEFAULT_DELAY',
    'MIN_DELAY',
    'DEFAULT_PARALLEL',
    'FULL_USER_AGENT'
]