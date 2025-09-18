#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit тесты для BaseExtractor
Проверяет базовую функциональность всех extractors
"""

import os
import sys
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, mock_open, patch

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.utils.base_extractor import BaseExtractor


class TestBaseExtractor(unittest.TestCase):
    """Тесты для BaseExtractor"""

    def setUp(self) -> None:
        """Настройка тестов"""

        # Создаем конкретную реализацию BaseExtractor для тестов
        class TestExtractor(BaseExtractor):
            def extract(self) -> Dict[str, Any]:
                return {"test": "data"}

        self.extractor: TestExtractor = TestExtractor()

    def test_init(self) -> None:
        """Тест инициализации BaseExtractor"""
        self.assertIsNotNone(self.extractor.blob_processor)
        self.assertIsNotNone(self.extractor.keyword_searcher)
        self.assertIsNotNone(self.extractor.document_analyzer)
        self.assertIsNone(self.extractor.db)
        self.assertEqual(self.extractor.results, {})

    @patch("builtins.open", mock_open(read_data=b"test data"))
    @patch("src.utils.base_extractor.DatabaseReader")
    def test_open_database_success(self, mock_db_reader: Any) -> None:
        """Тест успешного открытия базы данных"""
        mock_db = MagicMock()
        mock_db_reader.return_value = mock_db

        result = self.extractor.open_database("test.1CD")

        self.assertTrue(result)
        self.assertEqual(self.extractor.db, mock_db)

    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    def test_open_database_file_not_found(self, mock_open: Any) -> None:
        """Тест ошибки открытия файла"""
        result = self.extractor.open_database("nonexistent.1CD")

        self.assertFalse(result)
        self.assertIsNone(self.extractor.db)

    def test_get_document_tables_no_db(self) -> None:
        """Тест получения таблиц документов без открытой БД"""
        result = self.extractor.get_document_tables()
        self.assertEqual(result, [])

    def test_get_document_tables_with_db(self) -> None:
        """Тест получения таблиц документов с открытой БД"""
        # Мокаем базу данных
        mock_db = MagicMock()
        mock_table1 = MagicMock()
        mock_table1.__len__ = MagicMock(return_value=100)
        mock_table2 = MagicMock()
        mock_table2.__len__ = MagicMock(return_value=50)

        mock_db.tables = {
            "_DOCUMENT123": mock_table1,
            "_DOCUMENT456": mock_table2,
            "_DOCUMENT123_VT": mock_table1,  # Должна быть исключена
            "_Reference123": mock_table1,  # Должна быть исключена
        }

        self.extractor.db = mock_db

        result = self.extractor.get_document_tables()

        # Проверяем, что возвращены только таблицы документов
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "_DOCUMENT123")
        self.assertEqual(result[0][1], 100)
        self.assertEqual(result[1][0], "_DOCUMENT456")
        self.assertEqual(result[1][1], 50)

    def test_get_reference_tables_no_db(self) -> None:
        """Тест получения справочников без открытой БД"""
        result = self.extractor.get_reference_tables()
        self.assertEqual(result, [])

    def test_get_reference_tables_with_db(self) -> None:
        """Тест получения справочников с открытой БД"""
        # Мокаем базу данных
        mock_db = MagicMock()
        mock_table1 = MagicMock()
        mock_table1.__len__ = MagicMock(return_value=200)
        mock_table2 = MagicMock()
        mock_table2.__len__ = MagicMock(return_value=100)

        mock_db.tables = {
            "_Reference123": mock_table1,
            "_Reference456": mock_table2,
            "_DOCUMENT123": mock_table1,  # Должна быть исключена
        }

        self.extractor.db = mock_db

        result = self.extractor.get_reference_tables()

        # Проверяем, что возвращены только справочники
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "_Reference123")
        self.assertEqual(result[0][1], 200)
        self.assertEqual(result[1][0], "_Reference456")
        self.assertEqual(result[1][1], 100)

    def test_analyze_table_records_no_db(self) -> None:
        """Тест анализа записей без открытой БД"""
        result = self.extractor.analyze_table_records("test_table")
        self.assertEqual(result, [])

    def test_analyze_table_records_table_not_found(self) -> None:
        """Тест анализа записей несуществующей таблицы"""
        mock_db = MagicMock()
        mock_db.tables = {}
        self.extractor.db = mock_db

        result = self.extractor.analyze_table_records("nonexistent_table")
        self.assertEqual(result, [])

    def test_analyze_table_records_success(self) -> None:
        """Тест успешного анализа записей"""
        # Мокаем базу данных и таблицу
        mock_db = MagicMock()
        mock_table = MagicMock()

        # Мокаем записи
        mock_row1 = MagicMock()
        mock_row1.is_empty = False
        mock_row1.as_dict.return_value = {"field1": "value1", "field2": "value2"}

        mock_row2 = MagicMock()
        mock_row2.is_empty = False
        mock_row2.as_dict.return_value = {"field1": "value3", "field2": "value4"}

        mock_table.__len__ = MagicMock(return_value=2)
        mock_table.__getitem__ = MagicMock(side_effect=[mock_row1, mock_row2])

        mock_db.tables = {"test_table": mock_table}
        self.extractor.db = mock_db

        result = self.extractor.analyze_table_records("test_table", max_records=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["field1"], "value1")
        self.assertEqual(result[1]["field1"], "value3")

    @patch("builtins.open", mock_open())
    @patch("json.dump")
    def test_save_results_success(self, mock_json_dump: Any) -> None:
        """Тест успешного сохранения результатов"""
        results = {"test": "data", "number": 123}

        result = self.extractor.save_results("test.json", results)

        self.assertTrue(result)
        mock_json_dump.assert_called_once()

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_save_results_permission_error(self, mock_open: Any) -> None:
        """Тест ошибки сохранения результатов"""
        results = {"test": "data"}

        result = self.extractor.save_results("test.json", results)

        self.assertFalse(result)

    def test_create_metadata(self) -> None:
        """Тест создания метаданных"""
        metadata = self.extractor.create_metadata("test.1CD")

        self.assertIn("extraction_date", metadata)
        self.assertIn("source_file", metadata)
        self.assertIn("extractor_class", metadata)
        self.assertIn("total_tables_analyzed", metadata)
        self.assertIn("documents_analyzed", metadata)
        self.assertEqual(metadata["source_file"], "test.1CD")
        self.assertEqual(metadata["extractor_class"], "TestExtractor")

    def test_extract_abstract(self) -> None:
        """Тест что extract является абстрактным методом"""
        with self.assertRaises(TypeError):
            # Попытка создать экземпляр абстрактного класса должна вызвать ошибку
            BaseExtractor()  # type: ignore

    @patch("src.utils.base_extractor.BaseExtractor.open_database")
    def test_run_success(self, mock_open_db: Any) -> None:
        """Тест успешного запуска extractor"""

        # Создаем конкретную реализацию BaseExtractor
        class TestExtractor(BaseExtractor):
            def extract(self) -> Dict[str, Any]:
                return {"test": "data"}

        extractor = TestExtractor()
        mock_open_db.return_value = True

        result = extractor.run("test.1CD")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["test"], "data")
        mock_open_db.assert_called_once_with("test.1CD")

    @patch("src.utils.base_extractor.BaseExtractor.open_database")
    def test_run_database_open_failed(self, mock_open_db: Any) -> None:
        """Тест запуска extractor с ошибкой открытия БД"""

        class TestExtractor(BaseExtractor):
            def extract(self) -> Dict[str, Any]:
                return {"test": "data"}

        extractor = TestExtractor()
        mock_open_db.return_value = False

        result = extractor.run("test.1CD")

        self.assertIsNone(result)
        mock_open_db.assert_called_once_with("test.1CD")


if __name__ == "__main__":
    unittest.main()
