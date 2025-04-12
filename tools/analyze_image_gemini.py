import google.generativeai as genai
import PIL.Image
import os
import argparse
import sys

def analyze_image_with_gemini(image_path, prompt, api_key):
    """
    Uses the Gemini API to analyze an image based on a prompt.

    Args:
        image_path (str): Path to the image file.
        prompt (str): The prompt to guide the analysis.
        api_key (str): Your Google API Key.

    Returns:
        str: The analysis result from Gemini, or an error message.
    """
    if not api_key:
        return "エラー: APIキーが設定されていません。環境変数 GOOGLE_API_KEY を設定してください。"

    genai.configure(api_key=api_key)

    # モデルの選択 (Gemini Pro Vision)
    # 最新のモデル名を確認してください (例: 'gemini-1.5-flash', 'gemini-1.5-pro')
    # ここでは 'gemini-pro-vision' を使用しますが、利用可能なモデルに合わせて変更してください。
    model_name = 'gemini-2.5-pro-preview-03-25'
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        return f"エラー: モデル '{model_name}' の初期化に失敗しました。利用可能なモデル名を確認してください。詳細: {e}"

    try:
        print(f"画像を読み込み中: {image_path}", file=sys.stderr)
        img = PIL.Image.open(image_path)
        print("Gemini APIにリクエストを送信中...", file=sys.stderr)
        # stream=False に変更して、完全なレスポンスを一度に受け取る
        response = model.generate_content([prompt, img])

        # response.text が存在するか確認
        if hasattr(response, 'text'):
            return response.text
        # response.parts が存在し、テキスト部分があるか確認
        elif hasattr(response, 'parts') and response.parts:
             # 全てのテキスト部分を結合
            return "".join(part.text for part in response.parts if hasattr(part, 'text'))
        else:
            # 有効なテキスト応答がない場合のエラー処理
            # 必要であれば、responseオブジェクト全体をログに出力してデバッグ
            print(f"デバッグ情報: response object: {response}", file=sys.stderr)
            return "エラー: Gemini APIから有効なテキスト応答を取得できませんでした。"

    except FileNotFoundError:
        return f"エラー: 画像ファイルが見つかりません: {image_path}"
    except Exception as e:
        # API呼び出しやその他の予期せぬエラー
        return f"エラーが発生しました: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini APIを使用して画像の内容を解析し、JSON形式で出力します。")
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
            "JSONオブジェクトのみを出力し、前後の説明文は不要です。"
            "例: {'収入': {'寄付': [{'日付': 'R4.5.1', '氏名': '山田太郎', '金額': 10000, '住所': '東京都千代田区', '職業': '会社員'}]}}"
        ),
        help="Geminiに与えるプロンプト。"
    )

    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")

    print(f"画像を解析中: {args.image_file}", file=sys.stderr)
    result = analyze_image_with_gemini(args.image_file, args.prompt, api_key)

    # エラーメッセージと解析結果を区別して出力
    if result.startswith("エラー:"):
        print(result, file=sys.stderr)
    else:
        # 解析結果（JSON想定）のみを標準出力へ
        print(result)