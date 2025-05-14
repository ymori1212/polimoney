"""
メタデータ管理モジュール

ダウンロードしたファイルのメタデータを管理するクラスを提供します。
"""

import datetime
import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .utils import create_directory


@dataclass
class FileMetadata:
    """ファイルメタデータ"""

    filename: str
    original_url: str
    organization: str
    category: str
    year: str
    file_size: int = 0
    download_status: str = "pending"
    download_date: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return asdict(self)


@dataclass
class Statistics:
    """統計情報"""

    total_files: int = 0
    downloaded_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    total_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return asdict(self)


@dataclass
class Parameters:
    """パラメータ"""

    years: List[str]
    categories: List[str]
    name_filter: Optional[str] = None
    exact_match: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return asdict(self)


class MetadataManager:
    """メタデータ管理クラス"""

    def __init__(
        self,
        output_dir: str,
        years: List[str],
        categories: List[str],
        name_filter: Optional[str],
        exact_match: bool,
    ) -> None:
        """初期化

        Args:
            output_dir: 出力ディレクトリ
            years: 対象年度のリスト
            categories: 対象カテゴリのリスト
            name_filter: 団体名フィルタ
            exact_match: 完全一致フラグ
        """
        self.output_dir = output_dir
        self.metadata_path = os.path.join(output_dir, "metadata.json")

        # パラメータの初期化
        self.parameters = Parameters(
            years=years,
            categories=categories,
            name_filter=name_filter,
            exact_match=exact_match,
        )

        # 統計情報の初期化
        self.statistics = Statistics()

        # ファイルリストの初期化
        self.files: List[FileMetadata] = []

        # メタデータの初期化
        self.metadata: Dict[str, Any] = {
            "download_date": datetime.datetime.now().isoformat(),
            "parameters": self.parameters.to_dict(),
            "files": [],
            "statistics": self.statistics.to_dict(),
        }

    def add_file(self, metadata: FileMetadata) -> None:
        """ファイルメタデータを追加

        Args:
            metadata: ファイルメタデータ
        """
        self.files.append(metadata)
        self.metadata["files"].append(metadata.to_dict())

        # 統計情報を更新
        self.statistics.total_files += 1

        if metadata.download_status == "success":
            self.statistics.downloaded_files += 1
            self.statistics.total_size += metadata.file_size
        elif metadata.download_status == "skipped":
            self.statistics.skipped_files += 1
        elif metadata.download_status == "failed":
            self.statistics.failed_files += 1

        # メタデータの統計情報を更新
        self.metadata["statistics"] = self.statistics.to_dict()

    def save(self) -> bool:
        """メタデータをJSONファイルとして保存

        Returns:
            bool: 保存成功時はTrue、失敗時はFalse
        """
        try:
            # ディレクトリを作成
            if not create_directory(self.output_dir):
                print("出力ディレクトリの作成に失敗しました")
                return False

            # JSONファイルに書き込み
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"メタデータの保存に失敗しました: {e}")
            return False

    def get_statistics(self) -> Statistics:
        """統計情報を取得

        Returns:
            Statistics: 統計情報
        """
        return self.statistics
