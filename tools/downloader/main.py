#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
政治資金収支報告書ダウンロードスクリプト

総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードします。
指定された条件（公表年、団体種別、団体名など）に基づいて対象となる報告書を特定し、
効率的かつサーバーに負荷をかけないようにダウンロードします。

使用方法:
    python -m downloader.main [オプション]

オプション:
    -h, --help                ヘルプメッセージを表示
    -o, --output-dir DIR      保存先ディレクトリ（デフォルト: downloaded_pdfs）
    -y, --year YEAR           公表年（例: R5, R4）、複数指定可能（カンマ区切り）
    -c, --category CATEGORY   団体種別（政党本部,政党支部,政治資金団体,その他）、複数指定可能
    -n, --name NAME           団体名（部分一致で検索）
    -e, --exact-match         団体名の完全一致で検索
    -d, --delay SECONDS       リクエスト間の待機時間（秒、デフォルト: 5、最小: 3）
    -f, --force               既存ファイルを上書き
    -l, --log-level LEVEL     ログレベル（DEBUG, INFO, WARNING, ERROR、デフォルト: INFO）
    -v, --verbose             詳細な出力を表示（--log-level DEBUGと同等）
    --dry-run                 実際にダウンロードせずに何が行われるかを表示
    --metadata-only           PDFをダウンロードせずメタデータのみ収集
"""

import sys
import argparse
import logging
from argparse import Namespace

from .utils import setup_logger
from .config import DEFAULT_OUTPUT_DIR, DEFAULT_DELAY, MIN_DELAY
from .downloader import SeijishikinDownloader

# ロガーの設定
logger = logging.getLogger(__name__)


def parse_arguments() -> Namespace:
    """コマンドライン引数を解析する

    Returns:
        Namespace: 解析された引数
    """
    parser = argparse.ArgumentParser(
        description="総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードします。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="保存先ディレクトリ"
    )
    
    parser.add_argument(
        "-y", "--year",
        help="公表年（例: R5, R4）、複数指定可能（カンマ区切り）"
    )
    
    parser.add_argument(
        "-c", "--category",
        help="団体種別（政党本部,政党支部,政治資金団体,その他）、複数指定可能（カンマ区切り）"
    )
    
    parser.add_argument(
        "-n", "--name",
        help="団体名（部分一致で検索）"
    )
    
    parser.add_argument(
        "-e", "--exact-match",
        action="store_true",
        help="団体名の完全一致で検索"
    )
    
    parser.add_argument(
        "-d", "--delay",
        type=int,
        default=DEFAULT_DELAY,
        help=f"リクエスト間の待機時間（秒、最小: {MIN_DELAY}）"
    )
    
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="既存ファイルを上書き"
    )
    
    parser.add_argument(
        "-l", "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="ログレベル"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細な出力を表示（--log-level DEBUGと同等）"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際にダウンロードせずに何が行われるかを表示"
    )
    
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="PDFをダウンロードせずメタデータのみ収集"
    )
    
    args = parser.parse_args()
    
    # verboseフラグが指定された場合はログレベルをDEBUGに設定
    if args.verbose:
        args.log_level = "DEBUG"
    
    # 待機時間が最小値未満の場合はエラー
    if args.delay < MIN_DELAY:
        parser.error(f"待機時間は {MIN_DELAY} 秒以上である必要があります")
    
    return args


def main() -> int:
    """メイン関数

    Returns:
        int: 終了コード（成功時は0、失敗時は1）
    """
    # 引数を解析
    args = parse_arguments()

    # validate arguments
    if args.delay < MIN_DELAY:
        parser.error(f"待機時間は {MIN_DELAY} 秒以上である必要があります")
    
    # ロガーを設定
    setup_logger(args.log_level)
    
    logger.info("政治資金収支報告書ダウンロードスクリプトを開始します")
    
    # ダウンローダーを初期化
    downloader = SeijishikinDownloader(args)
    
    # ダウンロード実行
    success = downloader.download_all()
    
    # 終了コードを設定
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())