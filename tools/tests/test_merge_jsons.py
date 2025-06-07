# ruff: noqa
import pytest
import sys
import os

# toolsディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merge_jsons import (
    fix_duplicate_categories,
    flatten_categories_with_mixed_children,
    remove_empty_categories,
    ROOT_CATEGORY_ID,
)


class TestFixDuplicateCategories:
    """fix_duplicate_categories関数のテストクラス"""

    def test_duplicate_category_names(self):
        """同じ名前で異なるIDのカテゴリがある場合のテスト"""
        # テストデータ
        input_data = {
            "year": "2023",
            "basic_info": {"name": "テスト組織"},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": None},
                {"id": "cat2", "name": "支出", "parent": None},
                {"id": "cat3", "name": "収入", "parent": None},  # 重複
            ],
            "transactions": [
                {"id": "t1", "name": "会費", "category_id": "cat1", "amount": 1000, "value": 1000},
                {"id": "t2", "name": "事務費", "category_id": "cat2", "amount": 500, "value": 500},
                {"id": "t3", "name": "寄付金", "category_id": "cat3", "amount": 2000, "value": 2000},  # 重複カテゴリID
            ],
        }

        # 関数実行
        result = fix_duplicate_categories(input_data)

        # 検証
        # カテゴリは3つ（ROOT_CATEGORY_ID, cat1, cat2）
        assert len(result["categories"]) == 3
        category_ids = [cat["id"] for cat in result["categories"]]
        assert ROOT_CATEGORY_ID in category_ids
        assert "cat1" in category_ids
        assert "cat2" in category_ids

        # transactionのcat3はcat1に置き換えられる
        assert result["transactions"][2]["category_id"] == "cat1"
        assert result["transactions"][2]["name"] == "寄付金"
        assert result["transactions"][2]["amount"] == 2000

    def test_id_equals_parent(self):
        """idとparentが同じ値の場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": "cat1"},  # id == parent
                {"id": "cat2", "name": "支出", "parent": None},
            ],
            "transactions": [],
        }

        result = fix_duplicate_categories(input_data)

        # id == parentの場合、parentはNoneに置き換えられ、その後ROOT_CATEGORY_IDに置き換えられる
        # ただし空のカテゴリは削除される
        assert len(result["categories"]) == 1
        assert result["categories"][0]["id"] == ROOT_CATEGORY_ID

    def test_complex_scenario(self):
        """複雑なシナリオのテスト（重複とid=parentの両方）"""
        input_data = {
            "year": "2023",
            "basic_info": {"organization": "テスト"},
            "categories": [
                {"id": "cat1", "name": "収入", "parent": None},
                {"id": "cat2", "name": "支出", "parent": "cat2"},  # id == parent
                {"id": "cat3", "name": "収入", "parent": "cat1"},  # 重複名
                {"id": "cat4", "name": "その他", "parent": "cat4"},  # id == parent
                {"id": "cat5", "name": "支出", "parent": None},  # 重複名
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "amount": 100, "value": 100},
                {"id": "t2", "category_id": "cat2", "amount": 200, "value": 200},
                {"id": "t3", "category_id": "cat3", "amount": 300, "value": 300},  # 重複カテゴリ
                {"id": "t4", "category_id": "cat4", "amount": 400, "value": 400},
                {"id": "t5", "category_id": "cat5", "amount": 500, "value": 500},  # 重複カテゴリ
            ],
        }

        result = fix_duplicate_categories(input_data)

        # カテゴリは3つだけ（cat1, cat2, cat4）
        assert len(result["categories"]) == 3
        category_ids = [cat["id"] for cat in result["categories"]]
        assert "cat1" in category_ids
        assert "cat2" in category_ids
        assert "cat4" in category_ids

        # id == parentの場合、parentはNoneに置き換えられ、その後ROOT_CATEGORY_IDに置き換えられる
        for cat in result["categories"]:
            if cat["id"] in ["cat2", "cat4"]:
                assert cat["parent"] == ROOT_CATEGORY_ID

        # transactionsのカテゴリIDが正しく置き換えられる
        transactions_by_id = {t["id"]: t for t in result["transactions"]}
        assert transactions_by_id["t3"]["category_id"] == "cat1"  # cat3 -> cat1
        assert transactions_by_id["t5"]["category_id"] == "cat2"  # cat5 -> cat2

    def test_empty_data(self):
        """空のデータの場合のテスト"""
        input_data = {"year": "2023", "basic_info": {}, "categories": [], "transactions": []}

        result = fix_duplicate_categories(input_data)

        assert result["year"] == "2023"
        assert result["categories"] == []
        assert result["transactions"] == []

    def test_missing_fields(self):
        """必要なフィールドが欠けている場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            # categoriesとtransactionsが存在しない
        }

        result = fix_duplicate_categories(input_data)

        assert result["year"] == "2023"
        assert result["basic_info"] == {}
        assert result["categories"] == []
        assert result["transactions"] == []

    def test_category_without_name_or_id(self):
        """nameやidが欠けているカテゴリの場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "cat1", "name": "収入"},
                {"id": "cat2"},  # nameなし
                {"name": "支出"},  # idなし
                {"id": "cat3", "name": "収入"},  # 重複
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat2", "value": 100},
                {"id": "t2", "category_id": "", "value": 200},  # 空のcategory_id
                {"id": "t3", "value": 300},  # category_idなし
            ],
        }

        result = fix_duplicate_categories(input_data)

        # nameやidが欠けていても処理は続行される
        # cat1が削除される（空のカテゴリ）
        assert len(result["categories"]) == 2  # cat2とnameなしのカテゴリのみ
        assert len(result["transactions"]) == 3

    def test_parent_with_removed_category_id(self):
        """parentに削除されたカテゴリIDが指定されている場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": None},
                {"id": "cat2", "name": "支出", "parent": "cat3"},  # cat3は後で削除される
                {"id": "cat3", "name": "収入", "parent": None},  # 重複で削除される
                {"id": "cat4", "name": "その他", "parent": "cat5"},  # cat5は後で削除される
                {"id": "cat5", "name": "支出", "parent": None},  # 重複で削除される
            ],
            "transactions": [],
        }

        result = fix_duplicate_categories(input_data)

        # transactionがないため、ROOT_CATEGORY_ID以外は全て削除される
        assert len(result["categories"]) == 1  # ROOT_CATEGORY_IDのみ
        assert result["categories"][0]["id"] == ROOT_CATEGORY_ID

    def test_complex_parent_replacement(self):
        """複雑なparent置き換えのテスト（階層構造）"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "総収入", "parent": None},
                {"id": "cat2", "name": "会費", "parent": "cat1"},
                {"id": "cat3", "name": "総収入", "parent": None},  # 重複で削除
                {"id": "cat4", "name": "年会費", "parent": "cat3"},  # parent削除
                {"id": "cat5", "name": "会費", "parent": "cat3"},  # 重複で削除、parent削除
                {"id": "cat6", "name": "月会費", "parent": "cat5"},  # parent削除
            ],
            "transactions": [],
        }

        result = fix_duplicate_categories(input_data)

        # transactionがないため、ROOT_CATEGORY_ID以外は全て削除される
        assert len(result["categories"]) == 1  # ROOT_CATEGORY_IDのみ
        assert result["categories"][0]["id"] == ROOT_CATEGORY_ID

    def test_parent_null_to_root_category(self):
        """parentがnullのカテゴリをROOT_CATEGORY_IDに置き換えるテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},  # これはNoneのまま
                {"id": "cat1", "name": "収入", "parent": None},  # ROOT_CATEGORY_IDに置き換え
                {"id": "cat2", "name": "支出", "parent": None},  # ROOT_CATEGORY_IDに置き換え
                {"id": "cat3", "name": "その他", "parent": "cat1"},  # そのまま
            ],
            "transactions": [],
        }

        result = fix_duplicate_categories(input_data)

        # transactionがないため、cat1, cat2, cat3は全て削除される
        assert len(result["categories"]) == 1
        assert result["categories"][0]["id"] == ROOT_CATEGORY_ID
        assert result["categories"][0]["parent"] is None

    def test_parent_null_with_duplicates(self):
        """重複処理とparent=null処理の組み合わせテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": None},
                {"id": "cat2", "name": "収入", "parent": None},  # 重複で削除
                {"id": "cat3", "name": "支出", "parent": "cat3"},  # id=parent
                {"id": "cat4", "name": "その他", "parent": "cat2"},  # parent削除
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat2", "amount": 100, "value": 100},  # cat2 -> cat1
            ],
        }

        result = fix_duplicate_categories(input_data)

        # cat3とcat4は空なので削除される
        # カテゴリはROOT_CATEGORY_ID, cat1の2つ
        assert len(result["categories"]) == 2

        categories_by_id = {cat["id"]: cat for cat in result["categories"]}

        # ROOT_CATEGORY_IDはparentがNoneのまま
        assert categories_by_id[ROOT_CATEGORY_ID]["parent"] is None

        # cat1のparentはNone -> ROOT_CATEGORY_ID
        assert categories_by_id["cat1"]["parent"] == ROOT_CATEGORY_ID

        # transactionのカテゴリIDも正しく置き換えられる
        assert result["transactions"][0]["category_id"] == "cat1"

    def test_remove_zero_value_transactions(self):
        """valueが0のトランザクションを削除するテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "cat1", "name": "収入", "parent": None},
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 1000},
                {"id": "t2", "category_id": "cat1", "value": 0},  # 削除される
                {"id": "t3", "category_id": "cat1", "value": -500},
                {"id": "t4", "category_id": "cat1"},  # valueフィールドなし（0として扱われる）
                {"id": "t5", "category_id": "cat1", "value": 0.0},  # 削除される
            ],
        }

        result = fix_duplicate_categories(input_data)

        # valueが0でないトランザクションのみ残る
        assert len(result["transactions"]) == 2
        transaction_ids = [t["id"] for t in result["transactions"]]
        assert "t1" in transaction_ids
        assert "t3" in transaction_ids
        assert "t2" not in transaction_ids
        assert "t4" not in transaction_ids
        assert "t5" not in transaction_ids

    def test_all_zero_value_transactions(self):
        """全てのトランザクションのvalueが0の場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "cat1", "name": "収入", "parent": None},
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 0},
                {"id": "t2", "category_id": "cat1", "value": 0.0},
                {"id": "t3", "category_id": "cat1"},  # valueなし
            ],
        }

        result = fix_duplicate_categories(input_data)

        # 全てのトランザクションが削除される
        assert len(result["transactions"]) == 0

    def test_replace_none_date_with_empty_string(self):
        """dateがNoneの場合は空文字列に置き換えるテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": None},
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 1000, "date": "2023-01-01"},
                {"id": "t2", "category_id": "cat1", "value": 2000, "date": None},  # Noneをunknownに
                {"id": "t3", "category_id": "cat1", "value": 3000},  # dateフィールドなし
                {"id": "t4", "category_id": "cat1", "value": 4000, "date": ""},  # 既に空文字列
            ],
        }

        result = fix_duplicate_categories(input_data)

        # ROOT_CATEGORY_IDが追加されているはず
        assert len(result["categories"]) == 2

        # 各トランザクションのdateフィールドを確認
        transactions_by_id = {t["id"]: t for t in result["transactions"]}

        # 既存の日付は変更されない
        assert transactions_by_id["t1"]["date"] == "2023-01-01"

        # Noneはunknownに置き換えられる
        assert transactions_by_id["t2"]["date"] == "unknown"

        # dateフィールドがない場合もunknownが設定される
        assert transactions_by_id["t3"]["date"] == "unknown"

        # 既に空文字列の場合はそのまま
        assert transactions_by_id["t4"]["date"] == ""

    def test_complex_with_none_dates(self):
        """複雑なケースでのdate置き換えテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "cat1", "name": "収入", "parent": None},
                {"id": "cat2", "name": "収入", "parent": None},  # 重複で削除
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 1000, "date": None},
                {"id": "t2", "category_id": "cat2", "value": 0, "date": None},  # value=0で削除
                {"id": "t3", "category_id": "cat2", "value": 2000, "date": None},  # cat2->cat1, date置き換え
            ],
        }

        result = fix_duplicate_categories(input_data)

        # t2は削除される（value=0）
        assert len(result["transactions"]) == 2

        # 残ったトランザクションのdateはすべてunknownに
        for transaction in result["transactions"]:
            if "date" in transaction:
                assert transaction["date"] == "unknown"


class TestFlattenCategoriesWithMixedChildren:
    """flatten_categories_with_mixed_children関数のテストクラス"""

    def test_simple_flattening(self):
        """単純なカテゴリの削除とtransaction移動テスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "catA", "name": "カテゴリA", "parent": None},
                {"id": "catB", "name": "カテゴリB", "parent": "catA"},
                {"id": "catC", "name": "カテゴリC", "parent": "catB"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "catB", "amount": 100},  # catBの直接transaction
                {"id": "t2", "category_id": "catC", "amount": 200},  # catCのtransaction
            ],
        }

        # catBは直接transactionと子カテゴリ(catC)を両方持つ
        result = flatten_categories_with_mixed_children(input_data)

        category_ids = [cat["id"] for cat in result["categories"]]

        # catCは削除される
        assert "catC" not in category_ids
        assert "catB" in category_ids
        assert "catA" in category_ids

        # catCのtransactionはcatBに移動される
        transactions_by_id = {t["id"]: t for t in result["transactions"]}
        assert transactions_by_id["t1"]["category_id"] == "catB"  # 変わらない
        assert transactions_by_id["t2"]["category_id"] == "catB"  # catCからcatBに移動

    def test_multi_level_flattening(self):
        """多階層の削除とtransaction移動テスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "catA", "name": "カテゴリA", "parent": None},
                {"id": "catB", "name": "カテゴリB", "parent": "catA"},
                {"id": "catC", "name": "カテゴリC", "parent": "catB"},
                {"id": "catD", "name": "カテゴリD", "parent": "catC"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "catA", "amount": 100},  # catAの直接transaction
                {"id": "t2", "category_id": "catB", "amount": 200},  # catBの直接transaction
                {"id": "t3", "category_id": "catC", "amount": 300},  # catCの直接transaction
                {"id": "t4", "category_id": "catD", "amount": 400},  # catDのtransaction
            ],
        }

        # catA, catB, catCすべてが直接transactionと子カテゴリを持つ
        result = flatten_categories_with_mixed_children(input_data)

        category_ids = [cat["id"] for cat in result["categories"]]

        # catAは直接transactionと子カテゴリを持つので、catBとその子孫が削除される
        assert "catA" in category_ids
        assert "catB" not in category_ids
        assert "catC" not in category_ids
        assert "catD" not in category_ids

        # 全てのtransactionがcatAに移動される
        transactions_by_id = {t["id"]: t for t in result["transactions"]}
        assert transactions_by_id["t1"]["category_id"] == "catA"
        assert transactions_by_id["t2"]["category_id"] == "catA"  # catBからcatAに移動
        assert transactions_by_id["t3"]["category_id"] == "catA"  # catCからcatAに移動
        assert transactions_by_id["t4"]["category_id"] == "catA"  # catDからcatAに移動

    def test_no_mixed_children(self):
        """混在する子要素がない場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "catA", "name": "カテゴリA", "parent": None},
                {"id": "catB", "name": "カテゴリB", "parent": "catA"},
                {"id": "catC", "name": "カテゴリC", "parent": "catA"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "catB", "amount": 100},
                {"id": "t2", "category_id": "catC", "amount": 200},
            ],
        }

        # catAは子カテゴリのみ、catBとcatCは直接transactionのみ
        result = flatten_categories_with_mixed_children(input_data)

        categories_by_id = {cat["id"]: cat for cat in result["categories"]}

        # 変更されない
        assert categories_by_id["catB"]["parent"] == "catA"
        assert categories_by_id["catC"]["parent"] == "catA"

    def test_complex_hierarchy(self):
        """複雑な階層構造のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "root", "name": "ルート", "parent": None},
                {"id": "catA", "name": "カテゴリA", "parent": "root"},
                {"id": "catA1", "name": "カテゴリA1", "parent": "catA"},
                {"id": "catA2", "name": "カテゴリA2", "parent": "catA"},
                {"id": "catB", "name": "カテゴリB", "parent": "root"},
                {"id": "catB1", "name": "カテゴリB1", "parent": "catB"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "catA", "amount": 100},  # catAの直接transaction
                {"id": "t2", "category_id": "catA1", "amount": 200},
                {"id": "t3", "category_id": "catA2", "amount": 300},
                {"id": "t4", "category_id": "catB1", "amount": 400},
            ],
        }

        # catAは直接transactionと子カテゴリを持つ、catBは子カテゴリのみ
        result = flatten_categories_with_mixed_children(input_data)

        category_ids = [cat["id"] for cat in result["categories"]]

        # catAは直接transactionと子カテゴリを持つので、catA1とcatA2が削除される
        assert "catA" in category_ids
        assert "catA1" not in category_ids
        assert "catA2" not in category_ids
        # catBとcatB1は残る（catBに直接transactionがないため）
        assert "catB" in category_ids
        assert "catB1" in category_ids

        # catA1とcatA2のtransactionはcatAに移動される
        transactions_by_id = {t["id"]: t for t in result["transactions"]}
        assert transactions_by_id["t1"]["category_id"] == "catA"
        assert transactions_by_id["t2"]["category_id"] == "catA"  # catA1からcatAに移動
        assert transactions_by_id["t3"]["category_id"] == "catA"  # catA2からcatAに移動
        assert transactions_by_id["t4"]["category_id"] == "catB1"  # 変わらない

    def test_deep_hierarchy_deletion(self):
        """深い階層での削除とtransaction移動のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": "catA", "name": "カテゴリA", "parent": None},
                {"id": "catB", "name": "カテゴリB", "parent": "catA"},
                {"id": "catC", "name": "カテゴリC", "parent": "catB"},
                {"id": "catD", "name": "カテゴリD", "parent": "catC"},
                {"id": "catE", "name": "カテゴリE", "parent": "catC"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "catB", "amount": 100},  # catBの直接transaction
                {"id": "t2", "category_id": "catC", "amount": 200},
                {"id": "t3", "category_id": "catD", "amount": 300},
                {"id": "t4", "category_id": "catE", "amount": 400},
            ],
        }

        # catBは直接transactionと子カテゴリ（catC）を持つ
        # catCとその子孫（catD, catE）が削除される
        result = flatten_categories_with_mixed_children(input_data)

        category_ids = [cat["id"] for cat in result["categories"]]

        # catAとcatBのみ残る
        assert len(category_ids) == 2
        assert "catA" in category_ids
        assert "catB" in category_ids
        assert "catC" not in category_ids
        assert "catD" not in category_ids
        assert "catE" not in category_ids

        # 全ての子孫のtransactionがcatBに移動される
        transactions_by_id = {t["id"]: t for t in result["transactions"]}
        assert transactions_by_id["t1"]["category_id"] == "catB"  # 変わらない
        assert transactions_by_id["t2"]["category_id"] == "catB"  # catCからcatBに移動
        assert transactions_by_id["t3"]["category_id"] == "catB"  # catDからcatBに移動
        assert transactions_by_id["t4"]["category_id"] == "catB"  # catEからcatBに移動


class TestRemoveEmptyCategories:
    """remove_empty_categories関数のテストクラス"""

    def test_remove_empty_leaf_categories(self):
        """子要素を持たない葉カテゴリの削除テスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": ROOT_CATEGORY_ID},
                {"id": "cat2", "name": "支出", "parent": ROOT_CATEGORY_ID},
                {"id": "cat3", "name": "空カテゴリ", "parent": "cat1"},  # 削除される
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 1000},
                {"id": "t2", "category_id": "cat2", "value": 500},
            ],
        }

        result = remove_empty_categories(input_data)

        # cat3は子カテゴリもtransactionも持たないので削除される
        assert len(result["categories"]) == 3
        category_ids = [cat["id"] for cat in result["categories"]]
        assert ROOT_CATEGORY_ID in category_ids
        assert "cat1" in category_ids
        assert "cat2" in category_ids
        assert "cat3" not in category_ids

    def test_cascade_removal(self):
        """カスケード削除のテスト（親が削除されると子も空になる）"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": ROOT_CATEGORY_ID},
                {"id": "cat2", "name": "空親", "parent": "cat1"},  # 削除される
                {"id": "cat3", "name": "空子", "parent": "cat2"},  # 親が削除されるので削除される
                {"id": "cat4", "name": "空孫", "parent": "cat3"},  # 親が削除されるので削除される
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 1000},
            ],
        }

        result = remove_empty_categories(input_data)

        # cat2, cat3, cat4は全て削除される
        assert len(result["categories"]) == 2
        category_ids = [cat["id"] for cat in result["categories"]]
        assert ROOT_CATEGORY_ID in category_ids
        assert "cat1" in category_ids
        assert "cat2" not in category_ids
        assert "cat3" not in category_ids
        assert "cat4" not in category_ids

    def test_keep_categories_with_children(self):
        """子カテゴリを持つカテゴリは削除されないテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "親（transactionなし）", "parent": ROOT_CATEGORY_ID},
                {"id": "cat2", "name": "子", "parent": "cat1"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat2", "value": 1000},
            ],
        }

        result = remove_empty_categories(input_data)

        # cat1は直接transactionを持たないが、子カテゴリがあるので削除されない
        assert len(result["categories"]) == 3
        category_ids = [cat["id"] for cat in result["categories"]]
        assert ROOT_CATEGORY_ID in category_ids
        assert "cat1" in category_ids
        assert "cat2" in category_ids

    def test_keep_root_category(self):
        """ROOT_CATEGORY_IDは削除されないテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
            ],
            "transactions": [],
        }

        result = remove_empty_categories(input_data)

        # ROOT_CATEGORY_IDは子要素がなくても削除されない
        assert len(result["categories"]) == 1
        assert result["categories"][0]["id"] == ROOT_CATEGORY_ID

    def test_complex_hierarchy_removal(self):
        """複雑な階層構造での削除テスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": ROOT_CATEGORY_ID},
                {"id": "cat2", "name": "支出", "parent": ROOT_CATEGORY_ID},
                {"id": "cat1-1", "name": "会費", "parent": "cat1"},
                {"id": "cat1-2", "name": "寄付", "parent": "cat1"},  # 削除される
                {"id": "cat2-1", "name": "事務費", "parent": "cat2"},  # 削除される
                {"id": "cat2-2", "name": "活動費", "parent": "cat2"},
                {"id": "cat1-1-1", "name": "年会費", "parent": "cat1-1"},
                {"id": "cat1-2-1", "name": "個人寄付", "parent": "cat1-2"},  # 親が削除されるので削除
                {"id": "cat2-2-1", "name": "交通費", "parent": "cat2-2"},
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1-1", "value": 1000},
                {"id": "t2", "category_id": "cat1-1-1", "value": 2000},
                {"id": "t3", "category_id": "cat2-2", "value": 3000},
                {"id": "t4", "category_id": "cat2-2-1", "value": 4000},
            ],
        }

        result = remove_empty_categories(input_data)

        # cat1-2, cat2-1, cat1-2-1は削除される
        assert len(result["categories"]) == 7
        category_ids = [cat["id"] for cat in result["categories"]]
        assert "cat1-2" not in category_ids
        assert "cat2-1" not in category_ids
        assert "cat1-2-1" not in category_ids
        # その他は残る
        assert ROOT_CATEGORY_ID in category_ids
        assert "cat1" in category_ids
        assert "cat2" in category_ids
        assert "cat1-1" in category_ids
        assert "cat2-2" in category_ids
        assert "cat1-1-1" in category_ids
        assert "cat2-2-1" in category_ids

    def test_all_empty_except_root(self):
        """ROOT_CATEGORY_ID以外全て空の場合のテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "空1", "parent": ROOT_CATEGORY_ID},
                {"id": "cat2", "name": "空2", "parent": ROOT_CATEGORY_ID},
                {"id": "cat3", "name": "空3", "parent": "cat1"},
            ],
            "transactions": [],
        }

        result = remove_empty_categories(input_data)

        # ROOT_CATEGORY_ID以外全て削除される
        assert len(result["categories"]) == 1
        assert result["categories"][0]["id"] == ROOT_CATEGORY_ID

    def test_partial_removal_in_branch(self):
        """ブランチの一部のみ削除されるテスト"""
        input_data = {
            "year": "2023",
            "basic_info": {},
            "categories": [
                {"id": ROOT_CATEGORY_ID, "name": "総収入", "parent": None},
                {"id": "cat1", "name": "収入", "parent": ROOT_CATEGORY_ID},
                {"id": "cat1-1", "name": "会費", "parent": "cat1"},
                {"id": "cat1-2", "name": "その他", "parent": "cat1"},
                {"id": "cat1-1-1", "name": "年会費", "parent": "cat1-1"},
                {"id": "cat1-1-2", "name": "月会費", "parent": "cat1-1"},  # 削除される
                {"id": "cat1-2-1", "name": "雑収入", "parent": "cat1-2"},  # 削除される
            ],
            "transactions": [
                {"id": "t1", "category_id": "cat1", "value": 1000},
                {"id": "t2", "category_id": "cat1-1", "value": 2000},
                {"id": "t3", "category_id": "cat1-1-1", "value": 3000},
                {"id": "t4", "category_id": "cat1-2", "value": 4000},
            ],
        }

        result = remove_empty_categories(input_data)

        # cat1-1-2とcat1-2-1のみ削除される
        assert len(result["categories"]) == 5
        category_ids = [cat["id"] for cat in result["categories"]]
        assert "cat1-1-2" not in category_ids
        assert "cat1-2-1" not in category_ids
        # その他は残る
        assert ROOT_CATEGORY_ID in category_ids
        assert "cat1" in category_ids
        assert "cat1-1" in category_ids
        assert "cat1-2" in category_ids
        assert "cat1-1-1" in category_ids
