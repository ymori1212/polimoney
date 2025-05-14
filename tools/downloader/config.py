"""
政治資金収支報告書ダウンロード設定モジュール

ダウンロードに関する定数や設定を提供します。
"""

from typing import Dict, List, Final

# 基本設定
DEFAULT_OUTPUT_DIR: Final[str] = "downloaded_pdfs"
DEFAULT_DELAY: Final[int] = 5
MIN_DELAY: Final[int] = 3
DEFAULT_PARALLEL: Final[int] = 1

# URL設定
BASE_URL: Final[str] = "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/"
USER_AGENT: Final[str] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
BOT_NAME: Final[str] = "SeijishikinDownloaderBot"
FULL_USER_AGENT: Final[str] = f"{BOT_NAME}/1.0 ({USER_AGENT})"

# カテゴリマッピング
CATEGORY_MAPPING: Final[Dict[str, str]] = {
    '政党本部': '政党本部',
    '政党支部': '政党支部',
    '政党の支部': '政党支部',
    '政治資金団体': '政治資金団体',
    '国会議員関係政治団体': 'その他',
    'その他の政治団体': 'その他'
}

# 年度パターン
YEAR_PATTERNS: Final[List[str]] = [
    r'令和\d+年分.*定期公表',  # 令和X年分 定期公表
    r'令和\d+～\d+年分',  # 令和X～Y年分
    r'令和\d+年分.*解散分',  # 令和X年分 解散分
    r'令和\d+年分.*追加分',  # 令和X年分 追加分
    r'（令和\d+年分）',  # （令和X年分）
    r'（令和\d+～\d+年分）',  # （令和X～Y年分）
    r'令和\d+年分',  # 令和X年分
    r'R\d+',  # RX
]

# 特定の年度URLマッピング
SPECIFIC_YEAR_MAPPING: Final[Dict[str, str]] = {
    'SS20241129': 'R5',  # 令和5年分
    'SS20231124': 'R4',  # 令和4年分
    'SS20221125': 'R3',  # 令和3年分
}