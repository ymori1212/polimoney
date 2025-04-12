import google.generativeai as genai
import PIL.Image
import os
import argparse
import sys
import json # JSONの検証や整形のためにインポート

# 出力ディレクトリ名を定数化
OUTPUT_JSON_DIR = "output_json"

def clean_gemini_response(text):
    """Gemini応答からマークダウンコードブロック指示子を削除する"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"): # ``` だけの場合も考慮
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-len("```")].strip()
    return text

def analyze_image_with_gemini(image_path, prompt, api_key):
    """
    Uses the Gemini API to analyze an image based on a prompt.

    Args:
        image_path (str): Path to the image file.
        prompt (str): The prompt to guide the analysis.
        api_key (str): Your Google API Key.

    Returns:
        str: The cleaned analysis result from Gemini (expected JSON string), or an error message starting with "エラー:".
    """
    if not api_key:
        return "エラー: APIキーが設定されていません。環境変数 GOOGLE_API_KEY を設定してください。"

    genai.configure(api_key=api_key)

    model_name = 'gemini-1.5-pro-latest'
    try:
        model = genai.GenerativeModel(model_name)
        print(f"使用モデル: {model_name}", file=sys.stderr)
    except Exception as e:
        return f"エラー: モデル '{model_name}' の初期化に失敗しました。利用可能なモデル名を確認してください。詳細: {e}"

    try:
        print(f"画像を読み込み中: {image_path}", file=sys.stderr)
        img = PIL.Image.open(image_path)
        print("Gemini APIにリクエストを送信中...", file=sys.stderr)

        response = model.generate_content([prompt, img])

        raw_result = None
        # response.text が存在するか確認
        if hasattr(response, 'text') and response.text:
             raw_result = response.text
        # response.parts が存在し、テキスト部分があるか確認
        elif hasattr(response, 'parts') and response.parts:
             # 全てのテキスト部分を結合
             raw_result = "".join(part.text for part in response.parts if hasattr(part, 'text'))

        if raw_result:
            cleaned_result = clean_gemini_response(raw_result)
            # print(f"デバッグ情報 (整形後): {cleaned_result[:100]}...", file=sys.stderr) # デバッグ用
            return cleaned_result
        else:
            # 有効なテキスト応答がない場合のエラー処理
            print(f"デバッグ情報: response object: {response}", file=sys.stderr)
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                 print(f"プロンプトフィードバック: ブロック理由 - {response.prompt_feedback.block_reason}", file=sys.stderr)
            if hasattr(response, 'candidates') and not response.candidates:
                 print("警告: Gemini APIから候補となる応答が返されませんでした。", file=sys.stderr)
            return "エラー: Gemini APIから有効なテキスト応答を取得できませんでした。"

    except FileNotFoundError:
        return f"エラー: 画像ファイルが見つかりません: {image_path}"
    except Exception as e:
        print(f"予期せぬエラー発生: {type(e).__name__} - {e}", file=sys.stderr)
        if 'response' in locals():
            print(f"デバッグ情報 (エラー発生時のresponse): {response}", file=sys.stderr)
        return f"エラーが発生しました: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini APIを使用して画像の内容を解析し、結果をJSONファイルとして保存します。")
    parser.add_argument("image_file", help="解析する画像ファイルのパス。")
    parser.add_argument(
        "-p",
        "--prompt",
        default=(
            "これは日本の政治資金収支報告書の一部です。"
            "この画像から読み取れる全てのテキスト情報を抽出し、"
            "収入、支出、寄付、日付、氏名、住所、職業、金額などの項目を"
            "可能な限り正確に構造化されたJSON形式で出力してください。"
            "不明瞭な箇所や読み取れない箇所は無理に推測せず、その旨を示すか省略してください。"
            "{\n  \"収入\": [],\n  \"支出\": [],\n  \"寄付\": []\n}" # 出力形式の例をさらにシンプルに
            "上記のようなJSONオブジェクトのみを出力し、前後の説明文やマークダウンの```json ```や```は絶対に含めないでください。" # 指示を強化
            "例: {\"収入\": {\"寄付\": [{\"日付\": \"R4.5.1\", \"氏名\": \"山田太郎\", \"金額\": 10000, \"住所\": \"東京都千代田区\", \"職業\": \"会社員\"}]}}"
        ),
        help="Geminiに与えるプロンプト。"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=OUTPUT_JSON_DIR,
        help=f"解析結果のJSONファイルを保存するディレクトリ。デフォルト: '{OUTPUT_JSON_DIR}'"
    )

    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")

    # 出力ディレクトリを作成 (存在しない場合)
    try:
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"出力ディレクトリ: {args.output_dir}", file=sys.stderr)
    except OSError as e:
        print(f"エラー: 出力ディレクトリ '{args.output_dir}' の作成に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"画像を解析中: {args.image_file}", file=sys.stderr)
    result = analyze_image_with_gemini(args.image_file, args.prompt, api_key)

    # エラーメッセージと解析結果を区別
    if result.startswith("エラー:"):
        # エラーメッセージは標準エラー出力に表示するのみ
        print(result, file=sys.stderr)
    else:
        # 解析結果（JSON想定）をファイルに保存
        base_name = os.path.splitext(os.path.basename(args.image_file))[0]
        output_filename = os.path.join(args.output_dir, f"{base_name}.json")

        try:
            # オプション: 保存前にJSONとして妥当か検証
            try:
                json.loads(result)
                # print(f"デバッグ情報: 有効なJSONとしてパース成功。", file=sys.stderr) # デバッグ用
            except json.JSONDecodeError as json_err:
                print(f"警告: Geminiからの応答は有効なJSONではありません。そのままファイルに保存します。エラー: {json_err}", file=sys.stderr)
                print(f"応答内容(最初の200文字): {result[:200]}...", file=sys.stderr)

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"解析結果を保存しました: {output_filename}", file=sys.stderr)
        except IOError as e:
            print(f"エラー: 解析結果のファイル書き込みに失敗しました: {output_filename} - {e}", file=sys.stderr)
        except Exception as e:
             print(f"エラー: 不明なエラーが発生しました（ファイル書き込み時）: {e}", file=sys.stderr)