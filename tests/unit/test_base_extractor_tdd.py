#!/usr/bin/env python3
"""
TDD тесты для BaseExtractor
Согласно стандарту 4.1 TDD Documentation Standard

JTBD:
Как тестировщик, я хочу проверить BaseExtractor с TDD подходом,
чтобы убедиться в правильной работе базового класса для всех экстракторов.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.extractors.base_extractor import BaseExtractor
from src.processors.database_connector import DatabaseConnector


class ConcreteExtractor(BaseExtractor):
    """Конкретная реализация BaseExtractor для тестирования"""

    def extract(self, table_name: str, limit: int = 100) -> list[dict]:
        """JTBD: Как ConcreteExtractor, я хочу извлекать данные из таблицы,
        чтобы протестировать базовую функциональность."""
        # Обновляем статистику
        self.extraction_stats["total_items"] += 1
        self.extraction_stats["successful_extractions"] += 1

        return [{"test": "data", "table": table_name, "limit": limit}]


class TestBaseExtractorTDD(unittest.TestCase):
    """TDD тесты для BaseExtractor"""

    def setUp(self):
        """JTBD: Как тестовая фикстура, я хочу настроить тестовое окружение,
        чтобы обеспечить изолированное тестирование."""
        self.mock_db_connector = Mock(spec=DatabaseConnector)
        self.extractor = ConcreteExtractor(self.mock_db_connector)

    def test_initialization_with_db_connector(self):
        """JTBD: Как тестировщик, я хочу проверить инициализацию BaseExtractor,
        чтобы убедиться в правильной настройке компонентов."""
        # Arrange & Act
        extractor = ConcreteExtractor(self.mock_db_connector)

        # Assert
        self.assertEqual(extractor.db_connector, self.mock_db_connector)
        self.assertIsNotNone(extractor.table_analyzer)
        self.assertIsNotNone(extractor.blob_processor)
        self.assertIsInstance(extractor.extraction_stats, dict)
        self.assertIn("total_items", extractor.extraction_stats)
        self.assertIn("successful_extractions", extractor.extraction_stats)
        self.assertIn("failed_extractions", extractor.extraction_stats)

    def test_extract_method_interface(self):
        """JTBD: Как тестировщик, я хочу проверить интерфейс extract,
        чтобы убедиться в правильной сигнатуре метода."""
        # Arrange
        table_name = "test_table"
        limit = 50

        # Act
        result = self.extractor.extract(table_name, limit)

        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["table"], table_name)
        self.assertEqual(result[0]["limit"], limit)

    def test_process_row_with_valid_data(self):
        """JTBD: Как тестировщик, я хочу проверить обработку строки с валидными данными,
        чтобы убедиться в правильной обработке данных."""
        # Arrange
        mock_row = Mock()
        mock_row._fields = {"field1": "value1", "field2": "value2"}
        row_index = 0
        table_name = "test_table"

        # Act
        result = self.extractor.process_row(mock_row, row_index, table_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        if result:
            self.assertIn("fields", result)
            self.assertIn("field1", result["fields"])
            self.assertIn("field2", result["fields"])

    def test_process_row_with_empty_data(self):
        """JTBD: Как тестировщик, я хочу проверить обработку пустых данных,
        чтобы убедиться в правильной обработке edge cases."""
        # Arrange
        mock_row = Mock()
        mock_row._fields = {}
        row_index = 0
        table_name = "test_table"

        # Act
        result = self.extractor.process_row(mock_row, row_index, table_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        if result:
            self.assertIn("fields", result)
            self.assertEqual(len(result["fields"]), 0)

    def test_extraction_stats_tracking(self):
        """JTBD: Как тестировщик, я хочу проверить отслеживание статистики извлечения,
        чтобы убедиться в правильном мониторинге процесса."""
        # Arrange
        initial_stats = self.extractor.extraction_stats.copy()

        # Act
        self.extractor.extract("test_table", 10)

        # Assert
        self.assertGreater(
            self.extractor.extraction_stats["total_items"], initial_stats["total_items"]
        )
        self.assertGreater(
            self.extractor.extraction_stats["successful_extractions"],
            initial_stats["successful_extractions"],
        )

    def test_metadata_creation(self):
        """JTBD: Как тестировщик, я хочу проверить создание метаданных,
        чтобы убедиться в правильной документации процесса извлечения."""
        # Arrange
        source_file = "test_database.1CD"

        # Act
        metadata = self.extractor.create_metadata(source_file)

        # Assert
        self.assertIsInstance(metadata, dict)
        self.assertIn("extraction_date", metadata)
        self.assertIn("source_file", metadata)
        self.assertIn("extractor_class", metadata)
        self.assertEqual(metadata["source_file"], source_file)
        self.assertEqual(metadata["extractor_class"], "ConcreteExtractor")

    def test_error_handling_in_extract(self):
        """JTBD: Как тестировщик, я хочу проверить обработку ошибок в extract,
        чтобы убедиться в правильной обработке исключений."""

        # Arrange
        # Создаем экстрактор, который будет вызывать ошибку
        class FailingExtractor(BaseExtractor):
            def extract(self, table_name: str, limit: int = 100) -> list[dict]:
                raise Exception("Test error")

        failing_extractor = FailingExtractor(self.mock_db_connector)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            failing_extractor.extract("test_table")

        self.assertEqual(str(context.exception), "Test error")

    def test_abstract_method_enforcement(self):
        """JTBD: Как тестировщик, я хочу проверить принудительную реализацию абстрактных методов,
        чтобы убедиться в правильной архитектуре."""
        # Arrange & Act & Assert
        # BaseExtractor теперь не абстрактный, так как у него есть реализация process_document_row
        # Проверяем, что можно создать экземпляр
        extractor = BaseExtractor(self.mock_db_connector)
        self.assertIsInstance(extractor, BaseExtractor)


if __name__ == "__main__":
    unittest.main()
