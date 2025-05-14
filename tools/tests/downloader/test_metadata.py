"""
MetadataManagerクラスのテスト
"""

import os
import json
import unittest
from unittest.mock import Mock, MagicMock, patch
import datetime

from downloader.metadata import MetadataManager, FileMetadata, Statistics, Parameters


class TestFileMetadata(unittest.TestCase):
    """FileMetadataクラスのテスト"""

    def test_file_metadata_creation(self):
        """FileMetadataの作成テスト"""
        metadata = FileMetadata(
            filename="test.pdf",
            original_url="https://example.com/test.pdf",
            organization="テスト団体",
            category="政党支部",
            year="R5"
        )
        
        self.assertEqual(metadata.filename, "test.pdf")
        self.assertEqual(metadata.original_url, "https://example.com/test.pdf")
        self.assertEqual(metadata.organization, "テスト団体")
        self.assertEqual(metadata.category, "政党支部")
        self.assertEqual(metadata.year, "R5")
        self.assertEqual(metadata.file_size, 0)
        self.assertEqual(metadata.download_status, "pending")
        self.assertIsNone(metadata.download_date)
        self.assertIsNone(metadata.error)

    def test_file_metadata_to_dict(self):
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
            error=None
        )
        
        metadata_dict = metadata.to_dict()
        
        self.assertIsInstance(metadata_dict, dict)
        self.assertEqual(metadata_dict["filename"], "test.pdf")
        self.assertEqual(metadata_dict["original_url"], "https://example.com/test.pdf")
        self.assertEqual(metadata_dict["organization"], "テスト団体")
        self.assertEqual(metadata_dict["category"], "政党支部")
        self.assertEqual(metadata_dict["year"], "R5")
        self.assertEqual(metadata_dict["file_size"], 1000)
        self.assertEqual(metadata_dict["download_status"], "success")
        self.assertEqual(metadata_dict["download_date"], "2023-01-01T00:00:00")
        self.assertIsNone(metadata_dict["error"])


class TestStatistics(unittest.TestCase):
    """Statisticsクラスのテスト"""

    def test_statistics_creation(self):
        """Statisticsの作成テスト"""
        stats = Statistics()
        
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.downloaded_files, 0)
        self.assertEqual(stats.skipped_files, 0)
        self.assertEqual(stats.failed_files, 0)
        self.assertEqual(stats.total_size, 0)

    def test_statistics_to_dict(self):
        """Statisticsのto_dictメソッドのテスト"""
        stats = Statistics(
            total_files=10,
            downloaded_files=5,
            skipped_files=3,
            failed_files=2,
            total_size=5000
        )
        
        stats_dict = stats.to_dict()
        
        self.assertIsInstance(stats_dict, dict)
        self.assertEqual(stats_dict["total_files"], 10)
        self.assertEqual(stats_dict["downloaded_files"], 5)
        self.assertEqual(stats_dict["skipped_files"], 3)
        self.assertEqual(stats_dict["failed_files"], 2)
        self.assertEqual(stats_dict["total_size"], 5000)


class TestParameters(unittest.TestCase):
    """Parametersクラスのテスト"""

    def test_parameters_creation(self):
        """Parametersの作成テスト"""
        params = Parameters(
            years=["R5", "R6"],
            categories=["政党支部", "政党本部"]
        )
        
        self.assertEqual(params.years, ["R5", "R6"])
        self.assertEqual(params.categories, ["政党支部", "政党本部"])
        self.assertIsNone(params.name_filter)
        self.assertFalse(params.exact_match)

    def test_parameters_to_dict(self):
        """Parametersのto_dictメソッドのテスト"""
        params = Parameters(
            years=["R5", "R6"],
            categories=["政党支部", "政党本部"],
            name_filter="テスト",
            exact_match=True
        )
        
        params_dict = params.to_dict()
        
        self.assertIsInstance(params_dict, dict)
        self.assertEqual(params_dict["years"], ["R5", "R6"])
        self.assertEqual(params_dict["categories"], ["政党支部", "政党本部"])
        self.assertEqual(params_dict["name_filter"], "テスト")
        self.assertTrue(params_dict["exact_match"])


class TestMetadataManager(unittest.TestCase):
    """MetadataManagerクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.manager = MetadataManager(
            output_dir="test_output",
            years=["R5", "R6"],
            categories=["政党支部", "政党本部"],
            name_filter="テスト",
            exact_match=True
        )

    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.manager.output_dir, "test_output")
        self.assertEqual(self.manager.metadata_path, os.path.join("test_output", "metadata.json"))
        
        self.assertIsInstance(self.manager.parameters, Parameters)
        self.assertEqual(self.manager.parameters.years, ["R5", "R6"])
        self.assertEqual(self.manager.parameters.categories, ["政党支部", "政党本部"])
        self.assertEqual(self.manager.parameters.name_filter, "テスト")
        self.assertTrue(self.manager.parameters.exact_match)
        
        self.assertIsInstance(self.manager.statistics, Statistics)
        self.assertEqual(self.manager.statistics.total_files, 0)
        
        self.assertIsInstance(self.manager.files, list)
        self.assertEqual(len(self.manager.files), 0)
        
        self.assertIsInstance(self.manager.metadata, dict)
        self.assertIn("download_date", self.manager.metadata)
        self.assertIn("parameters", self.manager.metadata)
        self.assertIn("files", self.manager.metadata)
        self.assertIn("statistics", self.manager.metadata)

    def test_add_file_success(self):
        """add_fileメソッドが成功ファイルを追加する場合のテスト"""
        metadata = FileMetadata(
            filename="test.pdf",
            original_url="https://example.com/test.pdf",
            organization="テスト団体",
            category="政党支部",
            year="R5",
            file_size=1000,
            download_status="success"
        )
        
        self.manager.add_file(metadata)
        
        self.assertEqual(len(self.manager.files), 1)
        self.assertEqual(self.manager.files[0], metadata)
        self.assertEqual(len(self.manager.metadata["files"]), 1)
        
        self.assertEqual(self.manager.statistics.total_files, 1)
        self.assertEqual(self.manager.statistics.downloaded_files, 1)
        self.assertEqual(self.manager.statistics.total_size, 1000)

    def test_add_file_skipped(self):
        """add_fileメソッドがスキップファイルを追加する場合のテスト"""
        metadata = FileMetadata(
            filename="test.pdf",
            original_url="https://example.com/test.pdf",
            organization="テスト団体",
            category="政党支部",
            year="R5",
            download_status="skipped"
        )
        
        self.manager.add_file(metadata)
        
        self.assertEqual(self.manager.statistics.total_files, 1)
        self.assertEqual(self.manager.statistics.skipped_files, 1)

    def test_add_file_failed(self):
        """add_fileメソッドが失敗ファイルを追加する場合のテスト"""
        metadata = FileMetadata(
            filename="test.pdf",
            original_url="https://example.com/test.pdf",
            organization="テスト団体",
            category="政党支部",
            year="R5",
            download_status="failed",
            error="テストエラー"
        )
        
        self.manager.add_file(metadata)
        
        self.assertEqual(self.manager.statistics.total_files, 1)
        self.assertEqual(self.manager.statistics.failed_files, 1)

    def test_save(self):
        """saveメソッドのテスト"""
        # 必要なモックをセットアップ
        with patch('builtins.open', new_callable=unittest.mock.mock_open) as mock_open, \
             patch('json.dump') as mock_json_dump:
            
            # メソッドの実行
            result = self.manager.save()
            
            # 検証
            self.assertTrue(result)
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()
        mock_open.assert_called_once_with(os.path.join("test_output", "metadata.json"), "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    def test_get_statistics(self):
        """get_statisticsメソッドのテスト"""
        # 統計情報を設定
        self.manager.statistics.total_files = 10
        self.manager.statistics.downloaded_files = 5
        self.manager.statistics.skipped_files = 3
        self.manager.statistics.failed_files = 2
        self.manager.statistics.total_size = 5000
        
        # メソッドの実行
        stats = self.manager.get_statistics()
        
        # 検証
        self.assertEqual(stats.total_files, 10)
        self.assertEqual(stats.downloaded_files, 5)
        self.assertEqual(stats.skipped_files, 3)
        self.assertEqual(stats.failed_files, 2)
        self.assertEqual(stats.total_size, 5000)


if __name__ == "__main__":
    unittest.main()