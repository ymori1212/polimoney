# ruff: noqa
import os
import glob
import json
import re
import pandas as pd
import argparse


def load_all_json(file_paths):
    """
    指定されたjsonファイルをマージして、all.jsonを作成する関数

    Args:
        file_paths (list): マージするjsonファイルのパス

    Returns:
        dict: マージしたjsonデータ
    """
    # まずすべてのjsonファイルを読み込む
    jsons = []
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            jsons.append(json_data)

    # 一番最初のjsonファイルから、年度を読み取る(表紙の年)
    year = jsons[0]["year"]
    basic_info = jsons[0].get("basic_info", {})

    # 次に、categoriesをマージする
    categories = []

    # 数字から始まる部分を削除するための正規表現
    # ^\(\d+\)\s* : 先頭の(数字)を削除
    # |\d+\s+ : または、先頭の数字とスペースを削除
    # 例：(1) 田中太郎 -> 田中太郎
    # 例：1 田中太郎 -> 田中太郎
    number_pattern = r"^\(\d+\)\s*|\d+\s+"

    for file in jsons:
        if "categories" in file:
            for category in file["categories"]:
                if "name" in category:
                    category["name"] = re.sub(number_pattern, "", category["name"])
                categories.append(category)

    # 次に、transactionsをマージする
    transactions = []
    for file in jsons:
        if "transactions" in file:
            for transaction in file["transactions"]:
                if "name" in transaction:
                    transaction["name"] = re.sub(number_pattern, "", transaction["name"])
                transactions.append(transaction)

    # all.jsonを作成する
    all_json = {
        "year": year,
        "basic_info": basic_info,
        "categories": categories,
        "transactions": transactions,
    }

    return all_json


def main():
    parser = argparse.ArgumentParser(description="JSONファイルをマージしてall.jsonを作成します")
    parser.add_argument(
        "-t",
        "--target-dir",
        default=os.path.join(os.getcwd(), "output_json"),
        help="マージするJSONファイルがあるディレクトリ (デフォルト: ./output_json)",
    )
    parser.add_argument(
        "-m",
        "--merged-dir",
        default=os.path.join(os.getcwd(), "tools", "merged_files"),
        help="マージしたall.jsonを保存するディレクトリ (デフォルト: ./tools/merged_files)",
    )

    args = parser.parse_args()

    target_dir = args.target_dir
    merged_dir = args.merged_dir

    # ディレクトリが存在しない場合は作成
    os.makedirs(merged_dir, exist_ok=True)

    file_paths = glob.glob(os.path.join(target_dir, "*.json"))

    file_paths = sorted(file_paths)
    print(f"対象ファイル: {file_paths}")

    if not file_paths:
        print(f"警告: {target_dir} にJSONファイルが見つかりませんでした")
        return

    all_json = load_all_json(file_paths)

    output_path = os.path.join(merged_dir, "all.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_json, f, ensure_ascii=False, indent=2)

    print(f"マージ完了: {output_path}")


if __name__ == "__main__":
    main()
