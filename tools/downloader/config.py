# flake8: noqa: RUF001
"""
政治資金収支報告書ダウンロード設定モジュール

ダウンロードに関する定数や設定を提供します。
"""

from typing import Final

# 基本設定
DEFAULT_OUTPUT_DIR: Final[str] = "downloaded_pdfs"
DEFAULT_DELAY: Final[int] = 5
MIN_DELAY: Final[int] = 3

# URL設定
BASE_URL: Final[str] = "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/"
USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)
BOT_NAME: Final[str] = "SeijishikinDownloaderBot"
FULL_USER_AGENT: Final[str] = f"{BOT_NAME}/1.0 ({USER_AGENT})"

# 年度パターン
YEAR_PATTERNS: Final[list[str]] = [
    r"令和(\d+)年分.*定期公表",
    r"令和(\d+～\d+)年分",
    r"令和(\d+)年分.*解散分",
    r"令和(\d+)年分.*追加分",
    r"（令和(\d+)年分）",
    r"（令和(\d+～\d+)年分）",
    r"令和(\d+)年分",
    r"R(\d+)",
]
