"""
Gemini APIを使用して画像の内容を解析し、
結果をJSONファイルとして保存するスクリプト。
"""
from __future__ import annotations

import argparse
import concurrent.futures  # 並列処理のため
import json  # JSONの検証や整形のためにインポート
import logging  # ログ記録のため
import os
import sys
import time  # リトライ間隔の制御のため
from pathlib import Path
from typing import Any, NoReturn

import google.api_core.exceptions
import google.generativeai as genai
import PIL.Image
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)  # リトライロジックのため

# 出力ディレクトリ名を定数化
OUTPUT_JSON_DIR = "output_json"
ERROR_LOG_FILE = "error_log.json"

# ロガーの設定
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("analyzer")

# リトライ可能なエラーの定義
RETRYABLE_EXCEPTIONS = (
    google.api_core.exceptions.TooManyRequests,
    google.api_core.exceptions.DeadlineExceeded,
    google.api_core.exceptions.GatewayTimeout,
    google.api_core.exceptions.ServiceUnavailable,
)


class AnalysisError(Exception):
    """分析エラーを表す例外。"""

    def __init__(self, message: str, details: dict[str, Any]) -> None:
        """
        AnalysisErrorを初期化します。

        Args:
            message: エラーメッセージ。
            details: エラーの詳細情報。

        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """エラーメッセージと詳細を文字列として返します。"""
        return f"{self.message}: {self.details}"


class GeminiClient:
    """Gemini APIとやり取りするためのクライアントクラス。"""

    def __init__(self, key: str) -> None:
        """
        GeminiClientを初期化します。

        Args:
            key: Gemini APIキー。

        """
        self.key = key
        genai.configure(api_key=self.key)
        self.model_name = "gemini-2.5-pro-preview-05-06"
        self.model = genai.GenerativeModel(self.model_name)
        self.rate_limit_error_additional_wait_time = 30
        self.error_items: list[dict[str, Any]] = []

    def _handle_analysis_error(
        self,
        image_filename: str,
        error_type: str,
        error_message_detail: str,
        original_exception: Exception | None = None,
    ) -> NoReturn:
        """エラー情報を記録し、AnalysisErrorを送出するヘルパーメソッド。"""
        error_info = {
            "file": image_filename,
            "error_type": error_type,
            "error_message": error_message_detail,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.error_items.append(error_info)
        log_message = f"{error_type} ({image_filename}): {error_message_detail}"
        if original_exception:
            logger.exception(log_message, exc_info=original_exception)
            raise AnalysisError(log_message, error_info) from original_exception
        # original_exception が None の場合
        logger.error(log_message)  # logger.exceptionはtracebackを出すためerrorを使用
        raise AnalysisError(log_message, error_info)

    def clean_response(self, text: str) -> str:
        """Gemini応答からマークダウンコードブロック指示子を削除する。"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[len("```json") :].strip()
        elif text.startswith("```"):
            text = text[len("```") :].strip()

        if text.endswith("```"):
            text = text[: -len("```")].strip()

        return text

    @retry(
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        stop=stop_after_attempt(5),  # 最大5回リトライ
        wait=wait_exponential(
            multiplier=1, min=2, max=60,
        ),  # 指数バックオフ: 2秒、4秒、8秒、16秒、32秒
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def _generate_content_with_retry(
        self, prompt: str, img: PIL.Image.Image,
    ) -> genai.types.GenerateContentResponse:
        """
        リトライロジックを実装したGemini API呼び出し。

        generate_content()のrequest_optionsにretryパラメータを渡してリトライを実装すると
        エラー種別ごとのハンドリングが難しいため、tenacityのretryを使用している。

        Args:
            prompt: プロンプト。
            img: 画像。

        Returns:
            Gemini APIからのレスポンス。

        """
        try:
            return self.model.generate_content(
                contents=[prompt, img],
                generation_config={
                    "response_mime_type": "application/json",
                },
            )
        except google.api_core.exceptions.GoogleAPIError as e:
            # HTTP 429エラー (レートリミット) の場合は特別な処理
            if isinstance(e, google.api_core.exceptions.TooManyRequests):
                logger.warning("レートリミットエラー発生: %s. リトライします...", e)
                time.sleep(self.rate_limit_error_additional_wait_time)
            # その他のネットワークエラーなど
            logger.warning(
                "API呼び出しエラー: %s: %s. リトライします...",
                type(e).__name__,
                e,
            )
            raise  # 例外を再度発生させてリトライロジックに処理させる
        except RuntimeError as e: # その他の予期せぬ実行時エラー
            logger.warning(
                "予期せぬAPI呼び出しエラー (RuntimeError): %s: %s. リトライします...",
                type(e).__name__,
                e,
            )
            raise


    def _process_gemini_response(
        self, response: genai.types.GenerateContentResponse, image_filename: str,
    ) -> str:
        """Gemini APIの応答を処理し、テキスト結果またはエラーを処理します。"""
        raw_result = None
        if hasattr(response, "text") and response.text:
            raw_result = response.text
        elif hasattr(response, "parts") and response.parts:
            raw_result = "".join(
                part.text for part in response.parts if hasattr(part, "text")
            )

        if raw_result:
            return self.clean_response(raw_result)

        # 有効なテキスト応答がない場合のエラー処理
        error_message_detail = "Gemini APIから有効なテキスト応答を取得できませんでした。"
        if (
            hasattr(response, "prompt_feedback")
            and response.prompt_feedback.block_reason
        ):
            error_message_detail += (
                f" ブロック理由: {response.prompt_feedback.block_reason}"
            )
        elif hasattr(response, "candidates") and response.candidates:
            finish_reason = (
                response.candidates[0].finish_reason.name
                if hasattr(response.candidates[0], "finish_reason")
                else "不明"
            )
            if finish_reason != "STOP":
                error_message_detail += f" 応答終了理由: {finish_reason}"
            else:
                # 応答全体ではなく、関連性の高い候補情報に絞る
                error_message_detail += (
                    f" 不明な応答形式 (候補あり、終了理由STOP): {response.candidates[0]}"
                )
        elif hasattr(response, "candidates") and not response.candidates:
            error_message_detail += " 候補応答なし。"
        else:
            error_message_detail += " 不明なAPI応答形式です。"

        # _handle_analysis_error は NoReturn なので、この呼び出しで関数は終了する
        self._handle_analysis_error(
            image_filename,
            "GeminiAPIResponseError",
            error_message_detail,
        )
        
        return ""  # この行は実際には実行されません

    def analyze_image_with_gemini(self, image_path: Path) -> str:
        """
        指定した画像ファイルをGemini APIで解析し、Google推奨のJSON形式でテキスト情報を返します。

        Args:
            image_path: 解析対象の画像ファイルのパス。

        Returns:
            Geminiからの解析結果 (JSON文字列を想定)。
            エラーの場合は "エラー:" で始まるメッセージを返します。

        Raises:
            AnalysisError: 解析エラーが発生した場合。

        """
        prompt = """
# 依頼内容

これは日本の政治資金収支報告書の一部です。
この画像から読み取れる全てのテキスト情報を抽出し、正確に構造化されたJSON形式で出力してください。
不明瞭な箇所や読み取れない箇所は無理に推測せず、その旨を示すか省略してください。

# 期待するデータ形式

{
  "year": 2025,
  "categories": [
    {
      "id": "xxx1",
      "name": "個人からの寄付",
      "parent": "xxx66",
      "direction": "income"
    },
    ...
  ],
  "transactions": [
    {
      "id": "xxx1",
      "category_id": "xxxcc",
      "name": "飲食代",
      "date": "R5/6/28",
      "value": 10200
    },
    ...
  ]
}

# 抽出時の注意事項

## directionについて

directionは "income", "expense" のどちらかを指定してください。

## categoriesについて

- idは任意の文字列で構いません (例: "xxx1", "xxx2"など)
- parentは親カテゴリのidを指定します。最上位カテゴリの場合はnullを指定してください
- nameは以下のカテゴリから選んでください。ただし、当てはまるものがなく、
  明らかにカテゴリとして適切な物があった場合は、
  その他 ({{読み取れたカテゴリ}}) として立項して構いません。

## categoryについて

categoryは以下の中から選んでください。
ただし、当てはまるものがなく、明らかにカテゴリとして適切な物があった場合は、
その他 ({{読み取れたカテゴリ}}) として立項して構いません。

categoryの候補
- 個人からの寄附
- 政治団体からの寄附
- 法人その他の団体からの寄附
- 組織活動費
- 選挙関係費
- 機関紙誌の発行事業費
- 宣伝事業費
- 政治資金パーティ開催事業費
- その他の事業費
- 調査研究費
- 寄附・交付金
- 光熱水費
- 事務所費
- 借入金
- 人件費
- 前年からの繰越額
- 党費・会費
- 備品・消耗品費
- 翌年への繰越額
- その他の経費
- その他 ({{読み取れたカテゴリ}})

## transactionsについて

- idは任意の文字列で構いません (例: "xxx1", "xxx2"など)
- category_idは、categoriesで定義したidのいずれかを指定してください
- dateは年月日という項目に 6 9 30 などの区分で入っています。
  これは令和6年9月30日を示すので、 R6.9.30 という文字列に変換してください
- nameは具体的な項目を、画像に記載の通り入力してください
- valueは金額を数値で入力してください

# 具体例

{
  "year": 2025,
  "categories": [
    {
      "id": "xxx1",
      "name": "個人からの寄付",
      "parent": "xxx66",
      "direction": "income"
    },
    {
      "id": "xxx66",
      "name": "総収入",
      "parent": null,
      "direction": "income"
    }
  ],
  "transactions": [
    {
      "id": "xxx1",
      "category_id": "xxx1",
      "name": "田中太郎",
      "date": "R6.6.29",
      "value": 10000
    }
  ]
}
        """
        image_filename = image_path.name
        try:
            img = PIL.Image.open(image_path)

            try:
                response = self._generate_content_with_retry(prompt, img)
                return self._process_gemini_response(response, image_filename)
            except google.api_core.exceptions.GoogleAPIError as e:
                self._handle_analysis_error(
                    image_filename,
                    type(e).__name__,
                    f"最大リトライ回数を超えました: {e}",
                    original_exception=e,
                )
            except RuntimeError as e:  # 予期せぬ実行時エラー
                self._handle_analysis_error(
                    image_filename,
                    type(e).__name__,
                    f"予期せぬAPIエラー (RuntimeError): {e}",
                    original_exception=e,
                )

        except AnalysisError:  # _handle_analysis_error で処理済のため再raise
            raise
        except FileNotFoundError as e:
            self._handle_analysis_error(
                image_filename,
                "FileNotFoundError",
                f"画像ファイルが見つかりません: {image_path}",
                original_exception=e,
            )
        except (PIL.UnidentifiedImageError, OSError, RuntimeError) as e: # より具体的な例外を捕捉
            self._handle_analysis_error(
                image_filename,
                type(e).__name__,
                f"予期せぬエラー発生 ({type(e).__name__}): {e}",
                original_exception=e,
            )
        
        return ""  # この行は実際には実行されません

    def save_error_log(self, output_dir: Path) -> None:
        """
        エラー項目をJSONファイルとして保存します。

        Args:
            output_dir: 出力ディレクトリ。

        """
        if not self.error_items:
            return

        error_log_path = output_dir / ERROR_LOG_FILE
        try:
            with error_log_path.open("w", encoding="utf-8") as f:
                json.dump({"errors": self.error_items}, f, ensure_ascii=False, indent=2)
            logger.info("エラーログを保存しました: %s", error_log_path)
        except OSError:
            logger.exception("エラーログの保存に失敗しました:")


def process_single_image(
    image_path: Path, gemini_client: GeminiClient, output_dir: Path,
) -> bool:
    """単一の画像ファイルを処理し、結果をJSONファイルに保存する。"""
    image_filename = image_path.name
    logger.info("画像を解析中: %s", image_filename)
    try:
        result = gemini_client.analyze_image_with_gemini(image_path)
    except AnalysisError as e:
        logger.exception("エラー: %s", e.message) # logging.exception に変更
        return False

    output_filename = output_dir / f"{image_path.stem}.json"

    try:
        json.loads(result)
    except json.JSONDecodeError as json_err:
        logger.warning(
            "警告 (%s): Geminiからの応答は有効なJSONではありません。エラー: %s",
            image_filename,
            json_err,
        )
        logger.warning("応答内容(最初の200文字): %s...", result[:200])

    try:
        with output_filename.open("w", encoding="utf-8") as f:
            f.write(result)
    except OSError as e:
        error_info = {
            "file": image_filename,
            "error_type": "IOError",
            "error_message": (
                f"解析結果のファイル書き込みに失敗しました: {output_filename} - {e}"
            ),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        gemini_client.error_items.append(error_info)
        logger.exception(
            "エラー: %s 解析結果のファイル書き込みに失敗しました: %s",
            image_filename,
            output_filename,
        )
        return False  # 処理失敗を示す
    else:
        logger.info("解析結果を保存しました: %s", output_filename)
        return True  # 処理成功を示す


def get_png_files_to_process(args: argparse.Namespace) -> list[Path]:
    """
    ディレクトリまたは単一ファイルから処理対象のPNGファイルリストを取得する。

    Args:
        args: コマンドライン引数オブジェクト。

    Returns:
        処理対象のPNGファイルパスのリスト。

    Raises:
        SystemExit: ディレクトリやファイルが存在しない場合。

    """
    png_files: list[Path] = []

    if args.directory:
        target_dir = Path(args.directory)
        if not target_dir.is_dir():
            logger.error(
                "エラー: 指定されたディレクトリが見つかりません: %s", target_dir,
            )
            sys.exit(1)

        logger.info("ディレクトリ '%s' 内のPNGファイルを処理します...", target_dir)
        png_files = sorted(target_dir.glob("*.png"))

        if not png_files:
            logger.warning(
                "警告: ディレクトリ '%s' 内にPNGファイルが見つかりませんでした。",
                target_dir,
            )
        return png_files

    if args.image_file:
        image_file_path = Path(args.image_file)
        if not image_file_path.is_file():
            logger.error(
                "エラー: 指定されたファイルが見つかりません: %s", image_file_path,
            )
            sys.exit(1)
        return [image_file_path]

    logger.error("エラー: 解析対象のファイルまたはディレクトリを指定してください。")
    sys.exit(1)  # この行は到達不能のはず


def main() -> None:
    """
    スクリプトのエントリーポイント。

    コマンドライン引数をパースし、指定されたPNG画像ファイルまたは
    ディレクトリ内の全PNGファイルをGemini APIで解析し、
    その結果をJSONファイルとして保存します。

    Args:
        なし (コマンドライン引数で指定)

    Returns:
        なし (標準出力・標準エラー出力、およびファイル出力)

    Raises:
        SystemExit: 必要な環境変数が未設定、またはファイル/ディレクトリが
                    存在しない場合。

    注意:
        - GOOGLE_API_KEY環境変数が必要です。
        - 画像ファイルはPNG形式のみ対応しています。
        - 解析結果は指定した出力ディレクトリにJSONファイルとして保存されます。

    """
    parser = argparse.ArgumentParser(
        description=(
            "Gemini APIを使用して画像の内容を解析し、"
            "結果をJSONファイルとして保存します。"
            " 単一ファイルまたはディレクトリ内の全PNGファイルを処理できます。"
        ),
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "image_file",
        nargs="?",
        default=None,
        help="解析する単一の画像ファイルのパス。",
    )
    input_group.add_argument(
        "-d",
        "--directory",
        help="解析するPNG画像が含まれるディレクトリのパス。",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default=OUTPUT_JSON_DIR,
        help=(
            "解析結果のJSONファイルを保存するディレクトリ。\n"
            f"デフォルト: '{OUTPUT_JSON_DIR}'"
        ),
    )

    args = parser.parse_args()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
        sys.exit(1)

    gemini_client = GeminiClient(api_key)
    output_dir = Path(args.output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("出力ディレクトリ: %s", output_dir)
    except OSError:
        logger.exception(
            "エラー: 出力ディレクトリ '%s' の作成に失敗しました。", output_dir,
        )
        sys.exit(1)

    png_files = get_png_files_to_process(args)
    total_files = len(png_files)

    if total_files == 0:
        logger.error("エラー: 処理対象のPNGファイルが見つかりませんでした。")
        sys.exit(1)

    logger.info("%s 個のPNGファイルを処理します。", total_files)

    def process_with_index(
        args_tuple: tuple[int, Path],
    ) -> tuple[Path, bool]:
        i, png_file_path = args_tuple
        logger.info("--- Processing file %s/%s ---", i + 1, total_files)
        success = process_single_image(
            png_file_path, gemini_client, output_dir,
        )
        return png_file_path, success

    cpu_count = os.cpu_count() or 1
    max_workers = min(32, cpu_count * 2)
    logger.info("並列処理を開始します (最大 %s スレッド)", max_workers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        indexed_files = list(enumerate(png_files))
        results = list(executor.map(process_with_index, indexed_files))

        success_count = sum(1 for _, success in results if success)
        failed_count = total_files - success_count

        gemini_client.save_error_log(output_dir)

    logger.info("--- 全 %s ファイルの処理が完了しました ---", total_files)
    logger.info("成功: %s ファイル, 失敗: %s ファイル", success_count, failed_count)

    if failed_count > 0:
        logger.error(
            "エラーログは %s に保存されました", output_dir / ERROR_LOG_FILE,
        )


if __name__ == "__main__":
    main()
