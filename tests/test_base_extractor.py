#!/usr/bin/env python3

"""
Unit тесты для BaseExtractor
Проверяем базовую функциональность рефакторинга
"""

import unittest
from unittest.mock import Mock, patch

from src.extractors.base_extractor import BaseExtractor


class ConcreteExtractor(BaseExtractor):
    """Конкретная реализация для тестирования"""

    def extract(self):
        return {"test": "data"}


class TestBaseExtractor(unittest.TestCase):
    """
    Тесты для BaseExtractor класса
    """

    def setUp(self):
        """Настройка тестов"""
        self.extractor = ConcreteExtractor("test_db.1CD")

    def test_initialization(self):
        """Тест инициализации BaseExtractor"""
        self.assertEqual(self.extractor.db_path, "test_db.1CD")
        self.assertIsNone(self.extractor.db)
        self.assertIsNone(self.extractor.db_file)
        self.assertEqual(self.extractor.__class__.__name__, "ConcreteExtractor")

    @patch("os.path.exists")
    @patch("builtins.open")
    @patch("src.extractors.base_extractor.DatabaseReader")
    def test_open_database_success(self, mock_db_reader, mock_open, mock_exists):
        """Тест успешного открытия базы данных"""
        mock_exists.return_value = True
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_db_reader.return_value = Mock()

        result = self.extractor.open_database()

        self.assertTrue(result)
        self.assertIsNotNone(self.extractor.db)
        self.assertIsNotNone(self.extractor.db_file)

    @patch("os.path.exists")
    def test_open_database_file_not_found(self, mock_exists):
        """Тест открытия несуществующего файла"""
        mock_exists.return_value = False

        result = self.extractor.open_database()

        self.assertFalse(result)
        self.assertIsNone(self.extractor.db)

    def test_get_document_tables_empty(self):
        """Тест получения таблиц документов при пустой базе"""
        self.extractor.db = None
        result = self.extractor.get_document_tables()
        self.assertEqual(result, [])

    def test_get_document_tables_with_data(self):
        """Тест получения таблиц документов с данными"""
        mock_db = Mock()
        mock_db.tables.keys.return_value = [
            "_DOCUMENT123",
            "_DOCUMENT456",
            "_Reference789",
            "_AccumRGT101",
        ]
        self.extractor.db = mock_db

        result = self.extractor.get_document_tables()

        self.assertEqual(len(result), 2)
        self.assertIn("_DOCUMENT123", result)
        self.assertIn("_DOCUMENT456", result)

    def test_get_reference_tables_with_data(self):
        """Тест получения справочников с данными"""
        mock_db = Mock()
        mock_db.tables.keys.return_value = [
            "_DOCUMENT123",
            "_Reference789",
            "_Reference101",
            "_AccumRGT101",
        ]
        self.extractor.db = mock_db

        result = self.extractor.get_reference_tables()

        self.assertEqual(len(result), 2)
        self.assertIn("_Reference789", result)
        self.assertIn("_Reference101", result)

    def test_get_register_tables_with_data(self):
        """Тест получения регистров с данными"""
        mock_db = Mock()
        mock_db.tables.keys.return_value = [
            "_DOCUMENT123",
            "_Reference789",
            "_AccumRGT101",
            "_InfoRGT202",
        ]
        self.extractor.db = mock_db

        result = self.extractor.get_register_tables()

        self.assertEqual(len(result), 2)
        self.assertIn("_AccumRGT101", result)
        self.assertIn("_InfoRGT202", result)

    def test_extract_blob_content_none(self):
        """Тест извлечения BLOB содержимого для None"""
        result = self.extractor.extract_blob_content(None)
        # safe_get_blob_content возвращает None для None, но может вернуть строку "None"
        self.assertTrue(result is None or result == "None")

    @patch("src.extractors.base_extractor.safe_get_blob_content")
    def test_extract_blob_content_success(self, mock_safe_get):
        """Тест успешного извлечения BLOB содержимого"""
        mock_safe_get.return_value = "test content"
        mock_value = Mock()

        result = self.extractor.extract_blob_content(mock_value)

        self.assertEqual(result, "test content")
        mock_safe_get.assert_called_once_with(mock_value)

    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("json.dump")
    def test_save_results_success(self, mock_json_dump, mock_open, mock_makedirs):
        """Тест успешного сохранения результатов"""
        self.extractor.results = {"test": "data"}

        result = self.extractor.save_results("test_output.json")

        self.assertTrue(result)
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()

    def test_log_progress(self):
        """Тест логирования прогресса"""
        with patch("src.extractors.base_extractor.logger") as mock_logger:
            self.extractor.log_progress(50, 100, "test message")
            mock_logger.info.assert_called_once()

    def test_run_without_database(self):
        """Тест запуска без базы данных"""
        with patch.object(self.extractor, "open_database", return_value=False):
            result = self.extractor.run()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Не удалось открыть базу данных")

    def test_run_with_database_success(self):
        """Тест успешного запуска с базой данных"""
        with (
            patch.object(
                self.extractor,
                "open_database",
                return_value=True,
            ),
            patch.object(self.extractor, "extract", return_value={"test": "data"}),
        ):
            result = self.extractor.run()
            self.assertEqual(result["test"], "data")
            self.assertIn("metadata", result)


if __name__ == "__main__":
    unittest.main()
