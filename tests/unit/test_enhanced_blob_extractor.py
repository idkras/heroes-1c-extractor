#!/usr/bin/env python3

"""
Unit тесты для Enhanced Blob Extractor
Тестирует все 7 методов извлечения BLOB данных
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src", "utils"))

from src.utils.enhanced_blob_extractor import (
    BlobExtractionResult,
    EnhancedBlobExtractor,
    enhanced_safe_get_blob_content,
    extract_financial_data,
    extract_flower_data,
    extract_temporal_data,
)


class TestBlobExtractionResult(unittest.TestCase):
    """Тесты для BlobExtractionResult"""

    def test_init(self) -> None:
        """Тест инициализации результата"""
        result = BlobExtractionResult()

        self.assertIsNone(result.content)
        self.assertEqual(result.extraction_methods, [])
        self.assertEqual(result.content_length, 0)
        self.assertEqual(result.quality_score, 0.0)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.metadata, {})

    def test_post_init(self) -> None:
        """Тест post_init"""
        result = BlobExtractionResult()

        # Проверяем, что списки инициализированы
        self.assertIsInstance(result.extraction_methods, list)
        self.assertIsInstance(result.errors, list)
        self.assertIsInstance(result.metadata, dict)


class TestEnhancedBlobExtractor(unittest.TestCase):
    """Тесты для EnhancedBlobExtractor"""

    def setUp(self) -> None:
        """Настройка тестов"""
        self.extractor = EnhancedBlobExtractor()

    def test_init(self) -> None:
        """Тест инициализации извлекателя"""
        self.assertEqual(len(self.extractor.methods), 7)
        self.assertIn("value", self.extractor.methods)
        self.assertIn("iterator", self.extractor.methods)
        self.assertIn("bytes", self.extractor.methods)
        self.assertIn("str", self.extractor.methods)
        self.assertIn("direct_data", self.extractor.methods)
        self.assertIn("hexdump", self.extractor.methods)
        self.assertIn("strings", self.extractor.methods)

    def test_extract_blob_content_basic(self) -> None:
        """Тест базового извлечения"""
        # Создаем мок объект с value атрибутом
        mock_blob = Mock()
        mock_blob.value = "Тестовое содержимое"

        result = self.extractor.extract_blob_content(mock_blob)

        self.assertIsInstance(result, BlobExtractionResult)
        self.assertEqual(result.content, "Тестовое содержимое")
        self.assertIn("onec_dtools", result.extraction_methods)
        self.assertGreater(result.quality_score, 0)

    def test_extract_blob_content_with_data_type(self) -> None:
        """Тест извлечения с типом данных"""
        # Создаем мок объект с данными о цветах
        mock_blob = Mock()
        mock_blob.value = "Розы красные 50 штук по 174 рубля"

        result = self.extractor.extract_blob_content(mock_blob, "flower")

        self.assertEqual(result.content, "Розы красные 50 штук по 174 рубля")
        self.assertIn("onec_dtools", result.extraction_methods)
        self.assertGreater(result.quality_score, 0)
        self.assertEqual(result.metadata["data_type"], "flower")

    def test_try_value_method_success(self) -> None:
        """Тест успешного value метода"""
        mock_blob = Mock()
        mock_blob.value = "Тестовое содержимое"

        result = BlobExtractionResult()
        success = self.extractor._try_value_method(mock_blob, result)

        self.assertTrue(success)
        self.assertEqual(result.content, "Тестовое содержимое")

    def test_try_value_method_failure(self) -> None:
        """Тест неудачного value метода"""
        mock_blob = Mock()
        mock_blob.value = None
        mock_blob.__len__ = Mock(return_value=0)  # Пустой BLOB

        result = BlobExtractionResult()
        success = self.extractor._try_value_method(mock_blob, result)

        # Для пустого BLOB метод возвращает True с пустым содержимым
        self.assertTrue(success)
        self.assertEqual(result.content, "")

    def test_try_iterator_method_success(self) -> None:
        """Тест успешного iterator метода"""
        mock_blob = Mock()
        mock_blob.__iter__ = Mock(return_value=iter(["Тестовое содержимое"]))

        result = BlobExtractionResult()
        success = self.extractor._try_iterator_method(mock_blob, result)

        self.assertTrue(success)
        self.assertEqual(result.content, "Тестовое содержимое")

    def test_try_iterator_method_stop_iteration(self) -> None:
        """Тест iterator метода с StopIteration"""
        mock_blob = Mock()
        mock_blob.__iter__ = Mock(return_value=iter([]))

        result = BlobExtractionResult()
        success = self.extractor._try_iterator_method(mock_blob, result)

        self.assertFalse(success)
        self.assertIn("empty iterator", result.errors[0])

    def test_try_bytes_method_success(self) -> None:
        """Тест успешного bytes метода"""
        mock_blob = Mock()
        mock_blob.__bytes__ = Mock(return_value=b"Test content")

        result = BlobExtractionResult()
        success = self.extractor._try_bytes_method(mock_blob, result)

        self.assertTrue(success)
        self.assertEqual(result.content, "Test content")

    def test_try_str_method_success(self) -> None:
        """Тест успешного str метода"""
        mock_blob = Mock()
        # Используем patch для __str__ метода
        with patch.object(mock_blob, "__str__", return_value="Тестовое содержимое"):
            result = BlobExtractionResult()
            success = self.extractor._try_str_method(mock_blob, result)

            self.assertTrue(success)
            self.assertEqual(result.content, "Тестовое содержимое")

    def test_try_direct_data_method_success(self) -> None:
        """Тест успешного direct_data метода"""
        mock_blob = Mock()
        mock_blob._data = "Тестовое содержимое"

        result = BlobExtractionResult()
        success = self.extractor._try_direct_data_method(mock_blob, result)

        self.assertTrue(success)
        self.assertEqual(result.content, "Тестовое содержимое")

    def test_calculate_quality_score_flower_data(self) -> None:
        """Тест расчета качества для данных о цветах"""
        result = BlobExtractionResult()
        result.content = "Розы красные 50 штук по 174 рубля"
        result.content_length = len(result.content)
        result.extraction_methods = ["value"]

        score = self.extractor._calculate_quality_score(result, "flower")

        self.assertGreater(score, 0.4)  # Должен быть высокий счет для данных о цветах

    def test_calculate_quality_score_temporal_data(self) -> None:
        """Тест расчета качества для временных данных"""
        result = BlobExtractionResult()
        result.content = "Дата поступления 15.01.2025 время 14:30"
        result.content_length = len(result.content)
        result.extraction_methods = ["value"]

        score = self.extractor._calculate_quality_score(result, "temporal")

        self.assertGreaterEqual(
            score,
            0.5,
        )  # Должен быть высокий счет для временных данных

    def test_calculate_quality_score_financial_data(self) -> None:
        """Тест расчета качества для финансовых данных"""
        result = BlobExtractionResult()
        result.content = "Сумма 8700 рублей НДС 0 рублей"
        result.content_length = len(result.content)
        result.extraction_methods = ["value"]

        score = self.extractor._calculate_quality_score(result, "financial")

        self.assertGreater(score, 0.4)  # Должен быть высокий счет для финансовых данных

    def test_detect_content_type_json(self) -> None:
        """Тест определения типа JSON"""
        content = '{"name": "test", "value": 123}'
        content_type = self.extractor._detect_content_type(content)
        self.assertEqual(content_type, "json")

    def test_detect_content_type_xml(self) -> None:
        """Тест определения типа XML"""
        content = "<root><item>test</item></root>"
        content_type = self.extractor._detect_content_type(content)
        self.assertEqual(content_type, "xml")

    def test_detect_content_type_hex(self) -> None:
        """Тест определения типа hex"""
        content = "48656c6c6f20576f726c64"
        content_type = self.extractor._detect_content_type(content)
        self.assertEqual(content_type, "hex")

    def test_detect_content_type_text(self) -> None:
        """Тест определения типа text"""
        content = "Розы красные цветы"
        content_type = self.extractor._detect_content_type(content)
        self.assertEqual(content_type, "text")

    def test_extract_flower_data(self) -> None:
        """Тест извлечения данных о цветах"""
        mock_blob = Mock()
        mock_blob.value = "Розы красные 50 штук по 174 рубля за штуку"

        flower_data = self.extractor.extract_flower_data(mock_blob)

        self.assertIn("extraction_result", flower_data)
        self.assertIn("flower_info", flower_data)
        self.assertIn("found_flowers", flower_data["flower_info"])
        self.assertIn("flower_colors", flower_data["flower_info"])
        self.assertIn("quantities", flower_data["flower_info"])
        self.assertIn("prices", flower_data["flower_info"])

        # Проверяем, что найдены цветы
        self.assertGreater(len(flower_data["flower_info"]["found_flowers"]), 0)
        self.assertGreater(len(flower_data["flower_info"]["flower_colors"]), 0)
        self.assertGreater(len(flower_data["flower_info"]["quantities"]), 0)
        self.assertGreater(len(flower_data["flower_info"]["prices"]), 0)

    def test_extract_temporal_data(self) -> None:
        """Тест извлечения временных данных"""
        mock_blob = Mock()
        mock_blob.value = "Дата поступления 15.01.2025 время 14:30"

        temporal_data = self.extractor.extract_temporal_data(mock_blob)

        self.assertIn("extraction_result", temporal_data)
        self.assertIn("temporal_info", temporal_data)
        self.assertIn("dates", temporal_data["temporal_info"])
        self.assertIn("times", temporal_data["temporal_info"])
        self.assertIn("events", temporal_data["temporal_info"])

        # Проверяем, что найдены даты и времена
        self.assertGreater(len(temporal_data["temporal_info"]["dates"]), 0)
        self.assertGreater(len(temporal_data["temporal_info"]["times"]), 0)

    def test_extract_financial_data(self) -> None:
        """Тест извлечения финансовых данных"""
        mock_blob = Mock()
        mock_blob.value = "Сумма 8700 рублей НДС 0 рублей"

        financial_data = self.extractor.extract_financial_data(mock_blob)

        self.assertIn("extraction_result", financial_data)
        self.assertIn("financial_info", financial_data)
        self.assertIn("amounts", financial_data["financial_info"])
        self.assertIn("currencies", financial_data["financial_info"])
        self.assertIn("taxes", financial_data["financial_info"])

        # Проверяем, что найдены суммы и валюты
        self.assertGreater(len(financial_data["financial_info"]["amounts"]), 0)
        self.assertGreater(len(financial_data["financial_info"]["currencies"]), 0)


class TestEnhancedSafeGetBlobContent(unittest.TestCase):
    """Тесты для функции enhanced_safe_get_blob_content"""

    def test_enhanced_safe_get_blob_content(self) -> None:
        """Тест основной функции"""
        mock_blob = Mock()
        mock_blob.value = "Тестовое содержимое"

        result = enhanced_safe_get_blob_content(mock_blob)

        self.assertIsInstance(result, BlobExtractionResult)
        self.assertEqual(result.content, "Тестовое содержимое")
        self.assertIn("onec_dtools", result.extraction_methods)


class TestSpecializedExtractionFunctions(unittest.TestCase):
    """Тесты для специализированных функций извлечения"""

    def test_extract_flower_data_function(self) -> None:
        """Тест функции extract_flower_data"""
        mock_blob = Mock()
        mock_blob.value = "Розы красные 50 штук"

        flower_data = extract_flower_data(mock_blob)

        self.assertIn("extraction_result", flower_data)
        self.assertIn("flower_info", flower_data)

    def test_extract_temporal_data_function(self) -> None:
        """Тест функции extract_temporal_data"""
        mock_blob = Mock()
        mock_blob.value = "Дата 15.01.2025"

        temporal_data = extract_temporal_data(mock_blob)

        self.assertIn("extraction_result", temporal_data)
        self.assertIn("temporal_info", temporal_data)

    def test_extract_financial_data_function(self) -> None:
        """Тест функции extract_financial_data"""
        mock_blob = Mock()
        mock_blob.value = "Сумма 8700 рублей"

        financial_data = extract_financial_data(mock_blob)

        self.assertIn("extraction_result", financial_data)
        self.assertIn("financial_info", financial_data)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def test_full_extraction_workflow(self) -> None:
        """Тест полного workflow извлечения"""
        # Создаем комплексный мок объект
        mock_blob = Mock()
        mock_blob.value = "Розы красные 50 штук по 174 рубля за штуку, дата 15.01.2025"
        mock_blob.__iter__ = Mock(return_value=iter(["Дополнительная информация"]))
        mock_blob.__bytes__ = Mock(return_value=b"Binary data")

        # Тестируем извлечение данных о цветах
        flower_data = extract_flower_data(mock_blob)

        self.assertIsNotNone(flower_data["extraction_result"].content)
        self.assertGreater(len(flower_data["flower_info"]["found_flowers"]), 0)

        # Тестируем извлечение временных данных
        temporal_data = extract_temporal_data(mock_blob)

        self.assertIsNotNone(temporal_data["extraction_result"].content)
        self.assertGreater(len(temporal_data["temporal_info"]["dates"]), 0)

        # Тестируем извлечение финансовых данных
        financial_data = extract_financial_data(mock_blob)

        self.assertIsNotNone(financial_data["extraction_result"].content)
        self.assertGreater(len(financial_data["financial_info"]["amounts"]), 0)


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)
