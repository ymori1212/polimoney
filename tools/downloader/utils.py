"""
ユーティリティ関数モジュール

政治資金収支報告書ダウンロードスクリプトで使用するユーティリティ関数を提供します。
"""

import logging
import os
import re

# ロガーの設定
logger = logging.getLogger(__name__)


def setup_logger(log_level):
    """ロガーを設定する

    Args:
        log_level (str): ログレベル（DEBUG, INFO, WARNING, ERROR）
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    # フォーマッタの設定
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # ハンドラの追加（既存のハンドラがあれば削除）
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(console_handler)

    logger.debug("ロガーを設定しました。レベル: %s", log_level.upper())


def create_directory(directory):
    """ディレクトリを作成する（存在しない場合）

    Args:
        directory (str): 作成するディレクトリのパス

    Returns:
        bool: 作成成功時はTrue、失敗時はFalse
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.debug("ディレクトリを作成しました: %s", directory)
        return True
    except Exception as e:
        logger.error("ディレクトリの作成に失敗しました: %s, エラー: %s", directory, e)
        return False


def sanitize_filename(filename):
    """ファイル名を安全な形式に変換する

    Args:
        filename (str): 元のファイル名

    Returns:
        str: 安全な形式に変換されたファイル名
    """
    # 不正な文字を置換
    invalid_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # 長すぎる場合は切り詰め（Windows の制限は 255 文字）
    max_length = 240  # 拡張子や区切り文字のための余裕を持たせる
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext
    
    return sanitized


def extract_year_from_url(url):
    """URLから公表年を抽出する

    Args:
        url (str): 公表ページのURL

    Returns:
        str: 抽出された公表年（例: R5）、抽出できない場合はNone
    """
    # URLから年度を抽出するパターン
    patterns = [
        r'令和(\d+)年分.*解散分',  # 令和X年分 解散分
        r'令和(\d+)年分.*追加分',  # 令和X年分 追加分
        r'令和(\d+)年分.*定期公表',  # 令和X年分 定期公表
        r'令和(\d+)～(\d+)年分',  # 令和X～Y年分
        r'（令和(\d+)年分）',  # （令和X年分）
        r'（令和(\d+)～(\d+)年分）',  # （令和X～Y年分）
        r'令和(\d+)年分',  # 令和X年分
        r'R(\d+)',  # RX
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            # 令和X年分 の場合
            if len(match.groups()) == 1:
                year_num = int(match.group(1))
                return f"R{year_num}"
            # 令和X～Y年分 の場合は最新の年を使用
            elif len(match.groups()) == 2:
                year_num = max(int(match.group(1)), int(match.group(2)))
                return f"R{year_num}"
    
    # パターンにマッチしない場合はURLから年を推測
    # SS20241129 のような形式から年を推測（2024年の場合はR6）
    ss_match = re.search(r'SS(\d{4})', url)
    if ss_match:
        year = int(ss_match.group(1))
        reiwa_year = year - 2018  # 2019年が令和元年
        return f"R{reiwa_year}"
    
    logger.warning("URLから公表年を抽出できませんでした: %s", url)
    return None