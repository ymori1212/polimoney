"""
メタデータ管理モジュール

ダウンロードしたファイルのメタデータを管理するクラスを提供します。
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .utils import create_directory

# ロガーの設定
logger = logging.getLogger(__name__)


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
    download_date: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        """辞書に変換"""
        return asdict(self)


@dataclass
class Parameters:
    """パラメータ"""

    years: list[str]
    categories: list[str]
    name_filter: str | None = None
    exact_match: bool = False

    def to_dict(self) -> dict[str, Any]:
        """辞書に変換"""
        return asdict(self)


class MetadataManager:
    """メタデータ管理クラス"""

    def __init__(
        self,
        output_dir: str,
        years: list[str],
        categories: list[str],
        name_filter: str | None,
        *,
        exact_match: bool,
    ) -> None:
        """
        初期化

        Args:
            output_dir: 出力ディレクトリ
            years: 対象年度のリスト
            categories: 対象カテゴリのリスト
            name_filter: 団体名フィルタ
            exact_match: 完全一致フラグ

        """
        self.output_dir = output_dir
        # Pathオブジェクトを使用
        self.metadata_path = Path(output_dir) / "metadata.json"

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
        self.files: list[FileMetadata] = []

        # メタデータの初期化
        self.metadata: dict[str, Any] = {
            "download_date": datetime.datetime.now(
                tz=datetime.timezone.utc,
            ).isoformat(),
            "parameters": self.parameters.to_dict(),
            "files": [],
            "statistics": self.statistics.to_dict(),
        }

    def add_file(self, metadata: FileMetadata) -> None:
        """
        ファイルメタデータを追加

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
        """
        メタデータをJSONファイルとして保存

        Returns:
            bool: 保存成功時はTrue、失敗時はFalse

        """
        try:
            # ディレクトリを作成
            if not create_directory(self.output_dir):
                logger.error("出力ディレクトリの作成に失敗しました")
                return False

            # JSONファイルに書き込み
            with self.metadata_path.open("w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                return True
        except OSError:
            logger.exception("メタデータの保存に失敗しました")
            return False
        except json.JSONDecodeError:
            logger.exception("JSONのエンコードに失敗しました")
            return False

    def get_statistics(self) -> Statistics:
        """
        統計情報を取得

        Returns:
            Statistics: 統計情報

        """
        return self.statistics
