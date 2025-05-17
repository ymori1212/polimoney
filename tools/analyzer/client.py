"""Gemini APIとやり取りするためのクライアントモジュール"""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING, Any, NoReturn, Protocol

import google.api_core.exceptions
import google.generativeai as genai
import PIL.Image
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from pathlib import Path

# 出力ディレクトリ名を定数化
ERROR_LOG_FILE = "error_log.json"

# ロガーの設定
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


class ImageLoader(Protocol):
    """画像ローダーのインターフェース"""

    def load_image(self, image_path: Path) -> PIL.Image.Image:
        """
        画像ファイルを読み込みます。

        Args:
            image_path: 画像ファイルのパス

        Returns:
            読み込まれた画像オブジェクト

        Raises:
            FileNotFoundError: 画像ファイルが見つからない場合
            PIL.UnidentifiedImageError: 画像形式が認識できない場合
            OSError: その他のI/Oエラーが発生した場合

        """
        ...


class FileWriter(Protocol):
    """ファイル書き込みのインターフェース"""

    def write_file(self, path: Path, content: str) -> None:
        """
        ファイルに内容を書き込みます。

        Args:
            path: 書き込み先のファイルパス
            content: 書き込む内容

        Raises:
            OSError: ファイル書き込みエラーが発生した場合

        """
        ...


class GeminiClient:
    """Gemini APIとやり取りするためのクライアントクラス。"""

    def __init__(
        self,
        key: str,
        image_loader: ImageLoader | None = None,
        file_writer: FileWriter | None = None,
    ) -> None:
        """
        GeminiClientを初期化します。

        Args:
            key: Gemini APIキー。
            image_loader: 画像読み込みのためのローダー(テスト用)
            file_writer: ファイル書き込みのためのライター（テスト用）

        """  # noqa: RUF002
        self.key = key
        genai.configure(api_key=self.key)
        self.model_name = "gemini-2.5-pro-preview-05-06"
        self.model = genai.GenerativeModel(self.model_name)
        self.rate_limit_error_additional_wait_time = 30
        self.error_items: list[dict[str, Any]] = []
        self.image_loader = image_loader
        self.file_writer = file_writer

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
            multiplier=1,
            min=2,
            max=60,
        ),  # 指数バックオフ: 2秒、4秒、8秒、16秒、32秒
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def _generate_content_with_retry(
        self,
        prompt: str,
        img: PIL.Image.Image,
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
        except RuntimeError as e:  # その他の予期せぬ実行時エラー
            logger.warning(
                "予期せぬAPI呼び出しエラー (RuntimeError): %s: %s. リトライします...",
                type(e).__name__,
                e,
            )
            raise

    def _process_gemini_response(
        self,
        response: genai.types.GenerateContentResponse,
        image_filename: str,
    ) -> str:
        """Gemini APIの応答を処理し、テキスト結果またはエラーを処理します。"""
        raw_result = None
        if hasattr(response, "text") and response.text:
            raw_result = response.text
        elif hasattr(response, "parts") and response.parts:
            raw_result = "".join(part.text for part in response.parts if hasattr(part, "text"))

        if raw_result:
            return self.clean_response(raw_result)

        # 有効なテキスト応答がない場合のエラー処理
        error_message_detail = "Gemini APIから有効なテキスト応答を取得できませんでした。"
        if (
            hasattr(response, "prompt_feedback")
            and response.prompt_feedback is not None
            and hasattr(response.prompt_feedback, "block_reason")
            and response.prompt_feedback.block_reason
        ):
            error_message_detail += f" ブロック理由: {response.prompt_feedback.block_reason}"
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
                error_message_detail += f" 不明な応答形式 (候補あり、終了理由STOP): {response.candidates[0]}"
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
        from analyzer.prompt import prompt

        image_filename = image_path.name
        try:
            # 依存性注入されたimage_loaderがあれば使用、なければデフォルトの動作
            img = self.image_loader.load_image(image_path) if self.image_loader else PIL.Image.open(image_path)

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
        except (PIL.UnidentifiedImageError, OSError, RuntimeError) as e:  # より具体的な例外を捕捉
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
            # 依存性注入されたfile_writerがあれば使用、なければデフォルトの動作
            if self.file_writer:
                self.file_writer.write_file(
                    error_log_path,
                    json.dumps({"errors": self.error_items}, ensure_ascii=False, indent=2),
                )
            else:
                with error_log_path.open("w", encoding="utf-8") as f:
                    json.dump({"errors": self.error_items}, f, ensure_ascii=False, indent=2)
            logger.info("エラーログを保存しました: %s", error_log_path)
        except OSError:
            logger.exception("エラーログの保存に失敗しました:")
