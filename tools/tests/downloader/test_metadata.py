# ruff: noqa
"""MetadataManagerクラスのテスト"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from downloader.metadata import FileMetadata, MetadataManager, Parameters, Statistics


def test_file_metadata_creation() -> None:
    """FileMetadataの作成テスト"""
    metadata = FileMetadata(
        filename="test.pdf",
        original_url="https://example.com/test.pdf",
        organization="テスト団体",
        category="政党支部",
        year="R5",
    )

    assert metadata.filename == "test.pdf"
    assert metadata.original_url == "https://example.com/test.pdf"
    assert metadata.organization == "テスト団体"
    assert metadata.category == "政党支部"
    assert metadata.year == "R5"
    assert metadata.file_size == 0
    assert metadata.download_status == "pending"
    assert metadata.download_date is None
    assert metadata.error is None


def test_file_metadata_to_dict() -> None:
    """FileMetadataのto_dictメソッドのテスト"""
    metadata = FileMetadata(
        filename="test.pdf",
        original_url="https://example.com/test.pdf",
        organization="テスト団体",
        category="政党支部",
        year="R5",
        file_size=1000,
        download_status="success",
        download_date="2023-01-01T00:00:00",
        error=None,
    )

    metadata_dict = metadata.to_dict()

    assert isinstance(metadata_dict, dict)
    assert metadata_dict["filename"] == "test.pdf"
    assert metadata_dict["original_url"] == "https://example.com/test.pdf"
    assert metadata_dict["organization"] == "テスト団体"
    assert metadata_dict["category"] == "政党支部"
    assert metadata_dict["year"] == "R5"
    assert metadata_dict["file_size"] == 1000
    assert metadata_dict["download_status"] == "success"
    assert metadata_dict["download_date"] == "2023-01-01T00:00:00"
    assert metadata_dict["error"] is None


def test_statistics_creation() -> None:
    """Statisticsの作成テスト"""
    stats = Statistics()

    assert stats.total_files == 0
    assert stats.downloaded_files == 0
    assert stats.skipped_files == 0
    assert stats.failed_files == 0
    assert stats.total_size == 0


def test_statistics_to_dict() -> None:
    """Statisticsのto_dictメソッドのテスト"""
    stats = Statistics(
        total_files=10,
        downloaded_files=5,
        skipped_files=3,
        failed_files=2,
        total_size=5000,
    )

    stats_dict = stats.to_dict()

    assert isinstance(stats_dict, dict)
    assert stats_dict["total_files"] == 10
    assert stats_dict["downloaded_files"] == 5
    assert stats_dict["skipped_files"] == 3
    assert stats_dict["failed_files"] == 2
    assert stats_dict["total_size"] == 5000


def test_parameters_creation() -> None:
    """Parametersの作成テスト"""
    params = Parameters(years=["R5", "R6"], categories=["政党支部", "政党本部"])

    assert params.years == ["R5", "R6"]
    assert params.categories == ["政党支部", "政党本部"]
    assert params.name_filter is None
    assert params.exact_match is False


def test_parameters_to_dict() -> None:
    """Parametersのto_dictメソッドのテスト"""
    params = Parameters(
        years=["R5", "R6"],
        categories=["政党支部", "政党本部"],
        name_filter="テスト",
        exact_match=True,
    )

    params_dict = params.to_dict()

    assert isinstance(params_dict, dict)
    assert params_dict["years"] == ["R5", "R6"]
    assert params_dict["categories"] == ["政党支部", "政党本部"]
    assert params_dict["name_filter"] == "テスト"
    assert params_dict["exact_match"] is True


@pytest.fixture
def metadata_manager() -> MetadataManager:
    """MetadataManagerのフィクスチャ"""
    return MetadataManager(
        output_dir="test_output",
        years=["R5", "R6"],
        categories=["政党支部", "政党本部"],
        name_filter="テスト",
        exact_match=True,
    )


def test_init(metadata_manager: MetadataManager) -> None:
    """初期化のテスト"""
    assert metadata_manager.output_dir == "test_output"
    assert str(metadata_manager.metadata_path) == str(
        Path("test_output") / "metadata.json",
    )

    assert isinstance(metadata_manager.parameters, Parameters)
    assert metadata_manager.parameters.years == ["R5", "R6"]
    assert metadata_manager.parameters.categories == ["政党支部", "政党本部"]
    assert metadata_manager.parameters.name_filter == "テスト"
    assert metadata_manager.parameters.exact_match is True

    assert isinstance(metadata_manager.statistics, Statistics)
    assert metadata_manager.statistics.total_files == 0

    assert isinstance(metadata_manager.files, list)
    assert len(metadata_manager.files) == 0

    assert isinstance(metadata_manager.metadata, dict)
    assert "download_date" in metadata_manager.metadata
    assert "parameters" in metadata_manager.metadata
    assert "files" in metadata_manager.metadata
    assert "statistics" in metadata_manager.metadata


def test_add_file_success(metadata_manager: MetadataManager) -> None:
    """add_fileメソッドが成功ファイルを追加する場合のテスト"""
    metadata = FileMetadata(
        filename="test.pdf",
        original_url="https://example.com/test.pdf",
        organization="テスト団体",
        category="政党支部",
        year="R5",
        file_size=1000,
        download_status="success",
    )

    metadata_manager.add_file(metadata)

    assert len(metadata_manager.files) == 1
    assert metadata_manager.files[0] == metadata
    assert len(metadata_manager.metadata["files"]) == 1

    assert metadata_manager.statistics.total_files == 1
    assert metadata_manager.statistics.downloaded_files == 1
    assert metadata_manager.statistics.total_size == 1000


def test_add_file_skipped(metadata_manager: MetadataManager) -> None:
    """add_fileメソッドがスキップファイルを追加する場合のテスト"""
    metadata = FileMetadata(
        filename="test.pdf",
        original_url="https://example.com/test.pdf",
        organization="テスト団体",
        category="政党支部",
        year="R5",
        download_status="skipped",
    )

    metadata_manager.add_file(metadata)

    assert metadata_manager.statistics.total_files == 1
    assert metadata_manager.statistics.skipped_files == 1


def test_add_file_failed(metadata_manager: MetadataManager) -> None:
    """add_fileメソッドが失敗ファイルを追加する場合のテスト"""
    metadata = FileMetadata(
        filename="test.pdf",
        original_url="https://example.com/test.pdf",
        organization="テスト団体",
        category="政党支部",
        year="R5",
        download_status="failed",
        error="テストエラー",
    )

    metadata_manager.add_file(metadata)

    assert metadata_manager.statistics.total_files == 1
    assert metadata_manager.statistics.failed_files == 1


def test_save(metadata_manager: MetadataManager) -> None:
    """saveメソッドのテスト"""
    # 必要なモックをセットアップ
    with (
        patch("pathlib.Path.open", new_callable=mock_open()) as mock_file,
        patch("json.dump") as mock_json_dump,
    ):
        # メソッドの実行
        result = metadata_manager.save()

        # 検証
        assert result is True
        mock_file.assert_called_once_with("w", encoding="utf-8")
        mock_json_dump.assert_called_once()


def test_get_statistics(metadata_manager: MetadataManager) -> None:
    """get_statisticsメソッドのテスト"""
    # 統計情報を設定
    metadata_manager.statistics.total_files = 10
    metadata_manager.statistics.downloaded_files = 5
    metadata_manager.statistics.skipped_files = 3
    metadata_manager.statistics.failed_files = 2
    metadata_manager.statistics.total_size = 5000

    # メソッドの実行
    stats = metadata_manager.get_statistics()

    # 検証
    assert stats.total_files == 10
    assert stats.downloaded_files == 5
    assert stats.skipped_files == 3
    assert stats.failed_files == 2
    assert stats.total_size == 5000
