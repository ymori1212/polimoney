# ruff: noqa
import os
import glob
import json
import re
import pandas as pd
import argparse

ROOT_CATEGORY_ID = "category-0"


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
    root_category = {
        "id": ROOT_CATEGORY_ID,
        "name": "総収入",
        "parent": None,
        "direction": "income",
    }
    categories = []
    categories.append(root_category)

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


def fix_duplicate_categories(all_json):
    """
    load_all_json()の結果を補正する関数

    1. categoriesに同じnameでidが異なる要素があった場合、その要素を記録して、categoriesからは除く
    2. transactionsに除かれたカテゴリのIDが指定されていた場合、categoriesに残った同一名称のカテゴリのIDに置き換える
    3. categoriesにidとparentの値が同じ要素があった場合、parentをnullで置き換える
    4. categoriesのparentに削除されたカテゴリIDが指定されていた場合、残ったカテゴリのIDに置き換える
    5. parentがnullのカテゴリはparentをROOT_CATEGORY_IDに置き換える（idがROOT_CATEGORY_IDのカテゴリを除く）
    6. valueが0のtransactionを削除する
    7. transactionのdateがNoneの場合は空文字列に置き換える

    Args:
        all_json (dict): load_all_json()の戻り値

    Returns:
        dict: 補正後のjsonデータ
    """
    # 結果をコピーして変更
    result = {"year": all_json["year"], "basic_info": all_json["basic_info"], "categories": [], "transactions": []}

    # カテゴリ名ごとに最初のIDを記録
    category_name_to_id = {}
    # 削除されたカテゴリIDから正しいIDへのマッピング
    removed_id_to_correct_id = {}

    # 1. categoriesの重複を処理
    for category in all_json.get("categories", []):
        name = category.get("name", "")
        category_id = category.get("id", "")

        if name in category_name_to_id:
            # 同じ名前のカテゴリが既に存在する場合、このカテゴリは除外
            # 削除されたIDから正しいIDへのマッピングを記録
            removed_id_to_correct_id[category_id] = category_name_to_id[name]
        else:
            # 初めて見る名前の場合、記録して結果に追加
            category_name_to_id[name] = category_id
            # カテゴリをコピーして追加
            new_category = category.copy()

            # 3. idとparentが同じ場合の処理
            if new_category.get("id") == new_category.get("parent"):
                new_category["parent"] = None

            result["categories"].append(new_category)

    # 2. categoriesのparentフィールドを修正
    # parentに削除されたカテゴリIDが指定されている場合の処理
    for category in result["categories"]:
        parent_id = category.get("parent")
        if parent_id and parent_id in removed_id_to_correct_id:
            # 削除されたカテゴリIDの場合、正しいIDに置き換え
            category["parent"] = removed_id_to_correct_id[parent_id]

    # 5. parentがNoneのカテゴリをROOT_CATEGORY_IDに置き換える
    for category in result["categories"]:
        # idがROOT_CATEGORY_IDのカテゴリはparentがNoneのままでよい
        if category.get("id") != ROOT_CATEGORY_ID and category.get("parent") is None:
            category["parent"] = ROOT_CATEGORY_ID

    # 3. transactionsのカテゴリIDを修正
    for transaction in all_json.get("transactions", []):
        new_transaction = transaction.copy()
        category_id = new_transaction.get("category_id", "")

        # 削除されたカテゴリIDの場合、正しいIDに置き換え
        if category_id in removed_id_to_correct_id:
            new_transaction["category_id"] = removed_id_to_correct_id[category_id]

        result["transactions"].append(new_transaction)

    # 6. カテゴリが直接子transactionと子カテゴリを同時に持つ場合の処理
    result = flatten_categories_with_mixed_children(result)

    # 7. valueが0のトランザクションを削除
    result["transactions"] = [t for t in result["transactions"] if t.get("value", 0) != 0]

    # 8. transactionのdateがNoneの場合は空文字列に置き換える
    for transaction in result["transactions"]:
        if transaction.get("date", None) is None:
            transaction["date"] = "unknown"

    # 9. 子カテゴリも子transactionsも持たないカテゴリを削除
    result = remove_empty_categories(result)

    return result


def flatten_categories_with_mixed_children(all_json):
    """
    カテゴリが直接子transactionと子カテゴリを同時に持つ場合、
    子カテゴリを削除して、その子カテゴリのtransactionを親カテゴリに移動する処理

    Args:
        all_json (dict): 処理対象のjsonデータ

    Returns:
        dict: 処理後のjsonデータ
    """
    # カテゴリをIDでインデックス化（idがないカテゴリはスキップ）
    categories_by_id = {cat["id"]: cat for cat in all_json["categories"] if "id" in cat}

    # 各カテゴリの子カテゴリを記録
    children_by_parent = {}
    for cat in all_json["categories"]:
        if "id" not in cat:  # idがないカテゴリはスキップ
            continue
        parent = cat.get("parent")
        if parent:
            if parent not in children_by_parent:
                children_by_parent[parent] = []
            children_by_parent[parent].append(cat["id"])

    # 各カテゴリの直接のトランザクションを記録
    transactions_by_category = {}
    for trans in all_json["transactions"]:
        cat_id = trans.get("category_id")
        if cat_id:
            if cat_id not in transactions_by_category:
                transactions_by_category[cat_id] = []
            transactions_by_category[cat_id].append(trans["id"])

    # 削除するカテゴリを記録
    categories_to_delete = set()

    # 変更が必要なくなるまで繰り返す
    changed = True
    while changed:
        changed = False

        for cat_id in list(categories_by_id.keys()):
            if cat_id in categories_to_delete:
                continue

            # このカテゴリが子カテゴリと直接のトランザクションを両方持つか確認
            active_children = []
            if cat_id in children_by_parent:
                active_children = [child for child in children_by_parent[cat_id] if child not in categories_to_delete]
            has_children = len(active_children) > 0
            has_transactions = cat_id in transactions_by_category and len(transactions_by_category[cat_id]) > 0

            if has_children and has_transactions:
                # 子カテゴリとその子孫を全て削除対象に追加
                def collect_descendants(parent_id):
                    descendants = set()
                    if parent_id in children_by_parent:
                        for child_id in children_by_parent[parent_id]:
                            if child_id not in categories_to_delete:
                                descendants.add(child_id)
                                descendants.update(collect_descendants(child_id))
                    return descendants

                descendants_to_delete = collect_descendants(cat_id)
                categories_to_delete.update(descendants_to_delete)

                # 削除される子カテゴリのtransactionを親カテゴリに移動
                for trans in all_json["transactions"]:
                    if trans.get("category_id") in descendants_to_delete:
                        trans["category_id"] = cat_id

                changed = True

    # 結果を構築
    result = all_json.copy()

    # 削除対象のカテゴリを除外
    result["categories"] = [cat for cat in all_json["categories"] if cat.get("id") not in categories_to_delete]

    return result


def remove_empty_categories(all_json):
    """
    子カテゴリも子transactionsも持たないカテゴリを削除する

    Args:
        all_json (dict): 処理対象のjsonデータ

    Returns:
        dict: 処理後のjsonデータ
    """
    # カテゴリごとの子カテゴリを記録
    children_by_parent = {}
    for cat in all_json["categories"]:
        parent_id = cat.get("parent")
        if parent_id:
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = set()
            children_by_parent[parent_id].add(cat.get("id"))

    # カテゴリごとのトランザクションを記録
    transactions_by_category = {}
    for trans in all_json["transactions"]:
        cat_id = trans.get("category_id")
        if cat_id:
            if cat_id not in transactions_by_category:
                transactions_by_category[cat_id] = []
            transactions_by_category[cat_id].append(trans)

    # 削除対象のカテゴリIDを記録
    categories_to_remove = set()

    # 変更があるまで繰り返す（親カテゴリが削除されると子カテゴリも空になる可能性があるため）
    changed = True
    while changed:
        changed = False

        for cat in all_json["categories"]:
            cat_id = cat.get("id")
            if not cat_id or cat_id in categories_to_remove:
                continue

            # ROOT_CATEGORY_IDは削除しない
            if cat_id == ROOT_CATEGORY_ID:
                continue

            # 子カテゴリがあるか確認（削除予定のカテゴリは除外）
            has_children = False
            if cat_id in children_by_parent:
                active_children = [child for child in children_by_parent[cat_id] if child not in categories_to_remove]
                has_children = len(active_children) > 0

            # トランザクションがあるか確認
            has_transactions = cat_id in transactions_by_category and len(transactions_by_category[cat_id]) > 0

            # 子要素がない場合は削除対象に追加
            if not has_children and not has_transactions:
                categories_to_remove.add(cat_id)
                changed = True

    # 削除対象のカテゴリを除外
    result = all_json.copy()
    result["categories"] = [cat for cat in all_json["categories"] if cat.get("id") not in categories_to_remove]

    return result


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
    all_json = fix_duplicate_categories(all_json)

    output_path = os.path.join(merged_dir, "all.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_json, f, ensure_ascii=False, indent=2)

    print(f"マージ完了: {output_path}")


if __name__ == "__main__":
    main()
