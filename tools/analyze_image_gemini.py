import google.generativeai as genai
import google.api_core.exceptions
import PIL.Image
import os
import argparse
import sys
import json  # JSONの検証や整形のためにインポート
import glob  # ディレクトリ内のファイル検索のため
import concurrent.futures  # 並列処理のため
import logging  # ログ記録のため
from logging.handlers import QueueHandler, QueueListener
import time  # リトライ間隔の制御のため
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
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
    """分析エラーを表す例外"""

    def __init__(self, message: str, details: dict):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.details}"


class GeminiClient:
    def __init__(self, key):
        self.key = key
        self.model_name = "gemini-2.5-pro-preview-05-06"
        self.model = genai.GenerativeModel(self.model_name)
        self.rate_limit_error_additional_wait_time = 30
        self.error_items = []

    def clean_response(self, text):
        """Gemini応答からマークダウンコードブロック指示子を削除する"""
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
            multiplier=1, min=2, max=60
        ),  # 指数バックオフ: 2秒、4秒、8秒、16秒、32秒
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def _generate_content_with_retry(self, prompt, img):
        """
        リトライロジックを実装したGemini API呼び出し。
        generate_content()のrequest_optionsにretryパラメータを渡してリトライを実装すると
        エラー種別ごとのハンドリングが難しいため、tenacityのretryを使用している。

        Args:
            prompt: プロンプト
            img: 画像

        Returns:
            response: Gemini APIからのレスポンス
        """
        try:
            response = self.model.generate_content(
                contents=[prompt, img],
                generation_config={
                    "response_mime_type": "application/json",
                },
            )
            return response
        except Exception as e:
            # HTTP 429エラー（レートリミット）の場合は特別な処理
            if isinstance(e, google.api_core.exceptions.TooManyRequests):
                logger.warning(f"レートリミットエラー発生: {e}. リトライします...")
                time.sleep(self.rate_limit_error_additional_wait_time)
            # その他のネットワークエラーなど
            logger.warning(
                f"API呼び出しエラー: {type(e).__name__}: {e}. リトライします..."
            )
            raise  # 例外を再度発生させてリトライロジックに処理させる

    def analyze_image_with_gemini(self, image_path: str) -> str:
        """
        指定した画像ファイルをGemini APIで解析し、Google推奨のJSON形式でテキスト情報を返します。

        Args:
            image_path (str): 解析対象の画像ファイルのパス。

        Returns:
            str: Geminiからの解析結果（JSON文字列を想定）。エラーの場合は "エラー:" で始まるメッセージを返します。
        Raises:
            AnalysisError: 解析エラーが発生した場合
        """
        # genai.configure(api_key=api_key)
        # モデルはgemini-2.5-pro-preview-05-06です。これが現在の最新なのでいじらないでください。

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

- idは任意の文字列で構いません（例: "xxx1", "xxx2"など）
- parentは親カテゴリのidを指定します。最上位カテゴリの場合はnullを指定してください
- nameは以下のカテゴリから選んでください。ただし、当てはまるものがなく、明らかにカテゴリとして適切な物があった場合は、その他（{{読み取れたカテゴリ}}）として立項して構いません。

## categoryについて

categoryは以下の中から選んでください。
ただし、当てはまるものがなく、明らかにカテゴリとして適切な物があった場合は、その他（{{読み取れたカテゴリ}}）として立項して構いません。

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
- その他（{{読み取れたカテゴリ}}）

## transactionsについて

- idは任意の文字列で構いません（例: "xxx1", "xxx2"など）
- category_idは、categoriesで定義したidのいずれかを指定してください
- dateは年月日という項目に 6 9 30 などの区分で入っています。これは令和6年9月30日を示すので、 R6.9.30 という文字列に変換してください
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

        try:
            # print(f"画像を読み込み中: {image_path}", file=sys.stderr) # ループ内で冗長なのでコメントアウト
            img = PIL.Image.open(image_path)
            # print("Gemini APIにリクエストを送信中...", file=sys.stderr) # ループ内で冗長なのでコメントアウト

            # リトライロジックを実装したAPI呼び出し
            try:
                response = self._generate_content_with_retry(prompt, img)
            except Exception as e:
                # 最大リトライ回数を超えた場合
                error_info = {
                    "file": os.path.basename(image_path),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                self.error_items.append(error_info)
                logger.error(f"最大リトライ回数を超えました: {error_info}")
                raise AnalysisError(
                    f"最大リトライ回数を超えました: {os.path.basename(image_path)} {type(e).__name__} - {e}",
                    error_info,
                )

            raw_result = None
            if hasattr(response, "text") and response.text:
                raw_result = response.text
            elif hasattr(response, "parts") and response.parts:
                raw_result = "".join(
                    part.text for part in response.parts if hasattr(part, "text")
                )

            if raw_result:
                cleaned_result = self.clean_response(raw_result)
                return cleaned_result
            else:
                # エラー詳細表示
                error_message = f"エラー ({os.path.basename(image_path)}): Gemini APIから有効なテキスト応答を取得できませんでした。"  # ファイル名を追加
                if (
                    hasattr(response, "prompt_feedback")
                    and response.prompt_feedback.block_reason
                ):
                    error_message += (
                        f" ブロック理由: {response.prompt_feedback.block_reason}"
                    )
                # candidates が存在しない場合や finish_reason が RECITATION や SAFETY の場合も考慮
                elif hasattr(response, "candidates") and response.candidates:
                    finish_reason = (
                        response.candidates[0].finish_reason.name
                        if hasattr(response.candidates[0], "finish_reason")
                        else "不明"
                    )
                    if finish_reason != "STOP":
                        error_message += f" 応答終了理由: {finish_reason}"
                    else:
                        error_message += f" 不明な応答形式: {response}"  # STOPなのにテキストがない場合
                elif hasattr(response, "candidates") and not response.candidates:
                    error_message += " 候補応答なし。"
                else:
                    error_message += f" Response: {response}"  # 詳細不明な場合、レスポンス全体を一部表示
                # print(f"デバッグ情報: {error_message}", file=sys.stderr) # process_single_image で表示するので不要
                error_info = {
                    "file": os.path.basename(image_path),
                    "error_type": "Gemini API Response Error",
                    "error_message": error_message,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                self.error_items.append(error_info)
                raise AnalysisError(error_message, error_info)

        except AnalysisError as e:
            raise e
        except FileNotFoundError:
            error_info = {
                "file": os.path.basename(image_path),
                "error_type": "FileNotFoundError",
                "error_message": f"画像ファイルが見つかりません: {image_path}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.error_items.append(error_info)
            logger.error(f"ファイルが見つかりません: {error_info}")
            raise AnalysisError(
                f"画像ファイルが見つかりません: {image_path}", error_info
            )
        except Exception as e:
            # エラー情報を記録
            error_info = {
                "file": os.path.basename(image_path),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.error_items.append(error_info)
            logger.error(f"予期せぬエラー発生: {error_info}")
            raise AnalysisError(
                f"予期せぬエラー発生: {os.path.basename(image_path)} {type(e).__name__} - {e}",
                error_info,
            )

    def save_error_log(self, output_dir):
        """
        エラー項目をJSONファイルとして保存します。

        Args:
            output_dir: 出力ディレクトリ
        """
        if not self.error_items:
            return

        error_log_path = os.path.join(output_dir, ERROR_LOG_FILE)
        try:
            with open(error_log_path, "w", encoding="utf-8") as f:
                json.dump({"errors": self.error_items}, f, ensure_ascii=False, indent=2)
            logger.info(f"エラーログを保存しました: {error_log_path}")
        except Exception as e:
            logger.error(f"エラーログの保存に失敗しました: {e}")


def process_single_image(image_path, gemini_client, output_dir):
    """単一の画像ファイルを処理し、結果をJSONファイルに保存する"""
    logger.info(
        f"画像を解析中: {os.path.basename(image_path)}"
    )  # フルパスでなくファイル名表示に
    try:
        result = gemini_client.analyze_image_with_gemini(image_path)
    except AnalysisError as e:
        logger.error(f"エラー: {e.message}")
        return False

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = os.path.join(output_dir, f"{base_name}.json")

    try:
        json.loads(result)
    except json.JSONDecodeError as json_err:
        logger.warning(
            f"警告 ({os.path.basename(image_path)}): Geminiからの応答は有効なJSONではありません。エラー: {json_err}"
        )
        logger.warning(f"応答内容(最初の200文字): {result[:200]}...")

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result)
        logger.info(f"解析結果を保存しました: {output_filename}")
        return True  # 処理成功を示す
    except IOError as e:
        error_info = {
            "file": os.path.basename(image_path),
            "error_type": "IOError",
            "error_message": f"解析結果のファイル書き込みに失敗しました: {output_filename} - {e}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        gemini_client.error_items.append(error_info)
        logger.error(
            f"エラー: {os.path.basename(image_path)} 解析結果のファイル書き込みに失敗しました: {output_filename} - {e}"
        )
        return False  # 処理失敗を示す


def get_png_files_to_process(args):
    """
    ディレクトリまたは単一ファイルから処理対象のPNGファイルリストを取得する

    Args:
        args: コマンドライン引数オブジェクト

    Returns:
        list: 処理対象のPNGファイルパスのリスト

    Raises:
        SystemExit: ディレクトリやファイルが存在しない場合
    """
    png_files = []

    if args.directory:
        # ディレクトリ内のPNGファイルを処理
        target_dir = args.directory
        if not os.path.isdir(target_dir):
            logger.error(
                f"エラー: 指定されたディレクトリが見つかりません: {target_dir}"
            )
            sys.exit(1)

        logger.info(f"ディレクトリ '{target_dir}' 内のPNGファイルを処理します...")
        # glob を使って PNG ファイルを検索
        png_files = glob.glob(os.path.join(target_dir, "*.png"))
        png_files.sort()  # ファイル順を安定させる

        if not png_files:
            logger.warning(
                f"警告: ディレクトリ '{target_dir}' 内にPNGファイルが見つかりませんでした。"
            )
        return png_files

    elif args.image_file:
        # 単一ファイルを処理
        if not os.path.isfile(args.image_file):
            logger.error(
                f"エラー: 指定されたファイルが見つかりません: {args.image_file}"
            )
            sys.exit(1)
        png_files = [args.image_file]

        return png_files
    else:
        # このケースは mutually_exclusive_group(required=True) により発生しないはず
        logger.error("エラー: 解析対象のファイルまたはディレクトリを指定してください。")
        sys.exit(1)


def main():
    """スクリプトのエントリーポイント。

    コマンドライン引数をパースし、指定されたPNG画像ファイルまたはディレクトリ内の全PNGファイルをGemini APIで解析し、
    その結果をJSONファイルとして保存します。

    Args:
        なし（コマンドライン引数で指定）

    Returns:
        なし（標準出力・標準エラー出力、およびファイル出力）

    Raises:
        SystemExit: 必要な環境変数が未設定、またはファイル/ディレクトリが存在しない場合。

    注意:
        - GOOGLE_API_KEY環境変数が必要です。
        - 画像ファイルはPNG形式のみ対応しています。
        - 解析結果は指定した出力ディレクトリにJSONファイルとして保存されます。
    """
    parser = argparse.ArgumentParser(
        description="Gemini APIを使用して画像の内容を解析し、結果をJSONファイルとして保存します。単一ファイルまたはディレクトリ内の全PNGファイルを処理できます。"
    )

    # 入力ソースの排他グループ
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "image_file", nargs="?", default=None, help="解析する単一の画像ファイルのパス。"
    )  # nargs='?' と default=None でオプション扱いに
    input_group.add_argument(
        "-d", "--directory", help="解析するPNG画像が含まれるディレクトリのパス。"
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default=OUTPUT_JSON_DIR,
        help=f"解析結果のJSONファイルを保存するディレクトリ。デフォルト: '{OUTPUT_JSON_DIR}'",
    )

    args = parser.parse_args()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
        sys.exit(1)

    gemini_client = GeminiClient(api_key)

    # 出力ディレクトリを作成 (存在しない場合)
    try:
        os.makedirs(args.output_dir, exist_ok=True)
        logger.info(f"出力ディレクトリ: {args.output_dir}")
    except OSError as e:
        logger.error(
            f"エラー: 出力ディレクトリ '{args.output_dir}' の作成に失敗しました: {e}"
        )
        sys.exit(1)

    # --- 処理の実行 ---
    png_files = get_png_files_to_process(args)
    total_files = len(png_files)

    if total_files == 0:
        logger.error("エラー: 処理対象のPNGファイルが見つかりませんでした。")
        sys.exit(1)

    logger.info(f"{total_files} 個のPNGファイルを処理します。")

    # 並列処理の実装
    def process_with_index(args_tuple):
        i, png_file_path = args_tuple
        logger.info(f"--- Processing file {i + 1}/{total_files} ---")
        success = process_single_image(png_file_path, gemini_client, args.output_dir)
        return (png_file_path, success)

    # ThreadPoolExecutorを使用して並列処理
    # max_workersはCPUコア数の2倍程度が一般的な目安（I/O待ちが多いため）
    cpu_count = os.cpu_count() or 1
    max_workers = min(32, cpu_count * 2)  # CPUコア数の2倍、最大32
    logger.info(f"並列処理を開始します（最大 {max_workers} スレッド）")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # ファイルとインデックスのタプルのリストを作成
        indexed_files = list(enumerate(png_files))
        # 並列実行して結果を取得
        results = list(executor.map(process_with_index, indexed_files))

        # 成功・失敗の集計
        success_count = sum(1 for _, success in results if success)
        failed_count = total_files - success_count

        # エラーログを保存
        gemini_client.save_error_log(args.output_dir)

    logger.info(f"--- 全 {total_files} ファイルの処理が完了しました ---")
    logger.info(f"成功: {success_count} ファイル, 失敗: {failed_count} ファイル")

    if failed_count > 0:
        logger.error(
            f"エラーログは {os.path.join(args.output_dir, ERROR_LOG_FILE)} に保存されました"
        )


if __name__ == "__main__":
    main()
