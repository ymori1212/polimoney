"""
政治資金収支報告書ダウンロードパッケージ

総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードするためのパッケージです。
"""

from .config import DEFAULT_DELAY, DEFAULT_OUTPUT_DIR, FULL_USER_AGENT, MIN_DELAY
from .downloader import SeijishikinDownloader
from .metadata import MetadataManager
from .page_parser import PageParser
from .pdf_downloader import PDFDownloader
from .robotparser import RobotsChecker

__all__ = [
    "DEFAULT_DELAY",
    "DEFAULT_OUTPUT_DIR",
    "FULL_USER_AGENT",
    "MIN_DELAY",
    "MetadataManager",
    "PDFDownloader",
    "PageParser",
    "RobotsChecker",
    "SeijishikinDownloader",
]
