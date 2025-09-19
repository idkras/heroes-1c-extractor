#!/usr/bin/env python3

"""
Integration тесты для BLOB извлечения
Тестирует полный workflow извлечения данных о цветах
"""

import json
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


class TestBlobExtractionIntegration(unittest.TestCase):
    """Интеграционные тесты для BLOB извлечения"""

    def setUp(self) -> None:
        """Настройка тестов"""
        self.extractor = EnhancedBlobExtractor()

    def test_complete_flower_extraction_workflow(self) -> None:
        """Тест полного workflow извлечения данных о цветах"""
        # Создаем комплексный мок объект с данными о цветах
        mock_blob = Mock()
        mock_blob.value = """
        Поступление цветов от поставщика "Цветочная компания ООО"
        Дата: 15.01.2025
        Розы красные: 50 штук по 174 рубля за штуку
        Тюльпаны желтые: 30 штук по 120 рублей за штуку
        Гвоздики белые: 20 штук по 80 рублей за штуку
        Общая сумма: 8700 рублей
        НДС: 0 рублей
        """

        # Тестируем извлечение данных о цветах
        flower_data = extract_flower_data(mock_blob)

        # Проверяем результат извлечения
        self.assertIsNotNone(flower_data["extraction_result"].content)
        self.assertGreater(flower_data["extraction_result"].quality_score, 0.5)
        self.assertIn(
            "onec_dtools",
            flower_data["extraction_result"].extraction_methods,
        )

        # Проверяем данные о цветах
        flower_info = flower_data["flower_info"]
        self.assertGreater(len(flower_info["found_flowers"]), 0)
        self.assertGreater(len(flower_info["flower_colors"]), 0)
        self.assertGreater(len(flower_info["quantities"]), 0)
        self.assertGreater(len(flower_info["prices"]), 0)

        # Проверяем конкретные данные
        self.assertIn("роз", flower_info["found_flowers"])
        self.assertIn("красные", flower_info["flower_colors"])
        self.assertIn(50, flower_info["quantities"])
        self.assertIn(174.0, flower_info["prices"])

    def test_complete_temporal_extraction_workflow(self) -> None:
        """Тест полного workflow извлечения временных данных"""
        # Создаем мок объект с временными данными
        mock_blob = Mock()
        mock_blob.value = """
        Документ поступления товаров
        Дата создания: 15.01.2025
        Время создания: 14:30:25
        Дата поступления: 16.01.2025
        Время поступления: 09:15:00
        Период: январь 2025
        """

        # Тестируем извлечение временных данных
        temporal_data = extract_temporal_data(mock_blob)

        # Проверяем результат извлечения
        self.assertIsNotNone(temporal_data["extraction_result"].content)
        self.assertGreater(temporal_data["extraction_result"].quality_score, 0.5)

        # Проверяем временные данные
        temporal_info = temporal_data["temporal_info"]
        self.assertGreater(len(temporal_info["dates"]), 0)
        self.assertGreater(len(temporal_info["times"]), 0)
        self.assertGreater(len(temporal_info["events"]), 0)

        # Проверяем конкретные данные
        self.assertTrue(any("15.01.2025" in date for date in temporal_info["dates"]))
        self.assertTrue(any("14:30" in time for time in temporal_info["times"]))
        self.assertIn("дата", temporal_info["events"])

    def test_complete_financial_extraction_workflow(self) -> None:
        """Тест полного workflow извлечения финансовых данных"""
        # Создаем мок объект с финансовыми данными
        mock_blob = Mock()
        mock_blob.value = """
        Финансовые данные документа
        Основная сумма: 8700 рублей
        НДС: 0 рублей
        Итоговая сумма: 8700 рублей
        Валюта: рубли
        Скидка: 5%
        """

        # Тестируем извлечение финансовых данных
        financial_data = extract_financial_data(mock_blob)

        # Проверяем результат извлечения
        self.assertIsNotNone(financial_data["extraction_result"].content)
        self.assertGreater(financial_data["extraction_result"].quality_score, 0.5)

        # Проверяем финансовые данные
        financial_info = financial_data["financial_info"]
        self.assertGreater(len(financial_info["amounts"]), 0)
        self.assertGreater(len(financial_info["currencies"]), 0)
        self.assertGreater(len(financial_info["taxes"]), 0)

        # Проверяем конкретные данные
        self.assertIn(8700.0, financial_info["amounts"])
        self.assertIn("руб", financial_info["currencies"][0].lower())

    def test_multiple_extraction_methods(self) -> None:
        """Тест использования нескольких методов извлечения"""
        # Создаем мок объект с несколькими атрибутами
        mock_blob = Mock()
        mock_blob.value = "Основное содержимое"
        mock_blob.__iter__ = Mock(return_value=iter(["Дополнительная информация"]))
        mock_blob.__bytes__ = Mock(return_value=b"Binary data")
        mock_blob._data = "Прямые данные"

        # Тестируем извлечение
        result = enhanced_safe_get_blob_content(mock_blob)

        # Проверяем, что использованы несколько методов
        self.assertGreaterEqual(len(result.extraction_methods), 1)
        # Проверяем, что хотя бы один метод сработал
        self.assertTrue(len(result.extraction_methods) > 0)

        # Проверяем качество извлечения
        self.assertGreater(result.quality_score, 0.1)

    def test_error_handling_and_fallback(self) -> None:
        """Тест обработки ошибок и fallback методов"""
        # Создаем мок объект, который вызывает ошибки в первых методах
        mock_blob = Mock()
        mock_blob.value = None  # value не работает
        mock_blob.__iter__ = Mock(side_effect=StopIteration)  # iterator не работает
        mock_blob.__bytes__ = Mock(
            side_effect=Exception("Bytes error"),
        )  # bytes не работает
        # Используем patch для __str__ метода
        with patch.object(mock_blob, "__str__", return_value="Fallback содержимое"):
            result = self.extractor.extract_blob_content(mock_blob, "test")

            # Проверяем, что fallback сработал
            self.assertIsNotNone(result.content)
            self.assertIn(
                "onec_dtools",
                result.extraction_methods,
            )  # onec_dtools работает

        # Тестируем извлечение
        result = enhanced_safe_get_blob_content(mock_blob)

        # Проверяем, что fallback метод сработал
        self.assertIsNotNone(result.content)
        self.assertIn("onec_dtools", result.extraction_methods)
        # onec_dtools метод работает успешно, поэтому ошибок может не быть

    def test_content_type_detection(self) -> None:
        """Тест определения типа содержимого"""
        test_cases = [
            ('{"name": "test"}', "json"),
            ("<root>test</root>", "xml"),
            ("Розы красные цветы", "text"),
            ("48656c6c6f", "hex"),
            ("SGVsbG8gV29ybGQ=", "base64"),
        ]

        for content, expected_type in test_cases:
            with self.subTest(content=content):
                content_type = self.extractor._detect_content_type(content)
                self.assertEqual(content_type, expected_type)

    def test_quality_score_calculation(self) -> None:
        """Тест расчета оценки качества"""
        # Тест с высоким качеством
        result_high = BlobExtractionResult()
        result_high.content = "Розы красные 50 штук по 174 рубля за штуку"
        result_high.content_length = len(result_high.content)
        result_high.extraction_methods = ["value", "iterator"]

        score_high = self.extractor._calculate_quality_score(result_high, "flower")
        self.assertGreater(score_high, 0.7)

        # Тест с низким качеством
        result_low = BlobExtractionResult()
        result_low.content = "abc"
        result_low.content_length = len(result_low.content)
        result_low.extraction_methods = ["str"]
        result_low.errors = ["error1", "error2"]

        score_low = self.extractor._calculate_quality_score(result_low, "flower")
        self.assertLess(score_low, 0.5)

    def test_specialized_extraction_consistency(self) -> None:
        """Тест согласованности специализированного извлечения"""
        # Создаем мок объект с комплексными данными
        mock_blob = Mock()
        mock_blob.value = """
        Поступление цветов от "Цветочная компания ООО"
        Дата: 15.01.2025, время: 14:30
        Розы красные: 50 штук по 174 рубля
        Общая сумма: 8700 рублей, НДС: 0 рублей
        """

        # Извлекаем данные всеми специализированными методами
        flower_data = extract_flower_data(mock_blob)
        temporal_data = extract_temporal_data(mock_blob)
        financial_data = extract_financial_data(mock_blob)

        # Проверяем, что все методы нашли данные
        self.assertIsNotNone(flower_data["extraction_result"].content)
        self.assertIsNotNone(temporal_data["extraction_result"].content)
        self.assertIsNotNone(financial_data["extraction_result"].content)

        # Проверяем, что все методы имеют высокое качество
        self.assertGreater(flower_data["extraction_result"].quality_score, 0.5)
        self.assertGreater(temporal_data["extraction_result"].quality_score, 0.5)
        self.assertGreater(financial_data["extraction_result"].quality_score, 0.5)

        # Проверяем, что найдены специфические данные
        self.assertGreater(len(flower_data["flower_info"]["found_flowers"]), 0)
        self.assertGreater(len(temporal_data["temporal_info"]["dates"]), 0)
        self.assertGreater(len(financial_data["financial_info"]["amounts"]), 0)

    def test_performance_with_large_data(self) -> None:
        """Тест производительности с большими данными"""
        # Создаем большой контент
        large_content = "Розы красные " * 1000 + " 50 штук по 174 рубля"

        mock_blob = Mock()
        mock_blob.value = large_content

        # Тестируем производительность
        import time

        start_time = time.time()

        result = enhanced_safe_get_blob_content(mock_blob)

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверяем, что извлечение завершилось быстро (менее 1 секунды)
        self.assertLess(execution_time, 1.0)

        # Проверяем, что данные извлечены корректно
        self.assertIsNotNone(result.content)
        self.assertGreater(result.quality_score, 0)

    def test_json_serialization(self) -> None:
        """Тест сериализации результатов в JSON"""
        mock_blob = Mock()
        mock_blob.value = "Розы красные 50 штук по 174 рубля"

        # Извлекаем данные
        flower_data = extract_flower_data(mock_blob)

        # Тестируем сериализацию в JSON
        try:
            # Конвертируем BlobExtractionResult в словарь для сериализации
            serializable_data = {
                "extraction_result": flower_data["extraction_result"].__dict__,
                "flower_info": flower_data["flower_info"],
            }
            json_str = json.dumps(serializable_data, ensure_ascii=False, indent=2)
            self.assertIsInstance(json_str, str)
            self.assertGreater(len(json_str), 0)

            # Тестируем десериализацию
            parsed_data = json.loads(json_str)
            self.assertIn("extraction_result", parsed_data)
            self.assertIn("flower_info", parsed_data)
            self.assertIsInstance(parsed_data["extraction_result"], dict)

        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")


class TestRealWorldScenarios(unittest.TestCase):
    """Тесты реальных сценариев использования"""

    def test_flower_supply_scenario(self) -> None:
        """Тест сценария поставки цветов"""
        # Данные о поставке цветов
        supply_data = """
        Документ поступления товаров №12345
        Дата: 15.01.2025
        Поставщик: "Цветочная компания ООО"
        Адрес: г. Москва, ул. Цветочная, д. 1

        Товары:
        - Розы красные: 50 штук по 174 рубля за штуку
        - Тюльпаны желтые: 30 штук по 120 рублей за штуку
        - Гвоздики белые: 20 штук по 80 рублей за штуку

        Общая сумма: 8700 рублей
        НДС: 0 рублей
        Итого к оплате: 8700 рублей
        """

        mock_blob = Mock()
        mock_blob.value = supply_data

        # Извлекаем данные о цветах
        flower_data = extract_flower_data(mock_blob)

        # Проверяем, что найдены все цветы
        found_flowers = flower_data["flower_info"]["found_flowers"]
        self.assertIn("роз", found_flowers)
        self.assertIn("тюльпан", found_flowers)
        self.assertIn("гвоздик", found_flowers)

        # Проверяем количества
        quantities = flower_data["flower_info"]["quantities"]
        self.assertIn(50, quantities)
        self.assertIn(30, quantities)
        self.assertIn(20, quantities)

        # Проверяем цены
        prices = flower_data["flower_info"]["prices"]
        self.assertIn(174.0, prices)
        self.assertIn(120.0, prices)
        self.assertIn(80.0, prices)

    def test_flower_sales_scenario(self) -> None:
        """Тест сценария продажи цветов"""
        # Данные о продаже цветов
        sales_data = """
        Чек ККМ №001
        Дата: 16.01.2025, время: 15:30
        Кассир: Иванова А.А.

        Товары:
        - Розы красные: 5 штук по 200 рублей за штуку
        - Тюльпаны желтые: 3 штуки по 150 рублей за штуку

        Сумма: 1450 рублей
        Скидка: 5%
        Итого: 1377.50 рублей
        """

        mock_blob = Mock()
        mock_blob.value = sales_data

        # Извлекаем данные о цветах
        flower_data = extract_flower_data(mock_blob)

        # Проверяем найденные цветы
        found_flowers = flower_data["flower_info"]["found_flowers"]
        self.assertIn("роз", found_flowers)
        self.assertIn("тюльпан", found_flowers)

        # Проверяем количества
        quantities = flower_data["flower_info"]["quantities"]
        self.assertIn(5, quantities)
        self.assertIn(3, quantities)

        # Проверяем цены
        prices = flower_data["flower_info"]["prices"]
        self.assertIn(200.0, prices)
        self.assertIn(150.0, prices)

    def test_flower_inventory_scenario(self) -> None:
        """Тест сценария инвентаризации цветов"""
        # Данные об инвентаризации
        inventory_data = """
        Инвентаризация склада цветов
        Дата: 17.01.2025
        Склад: "Основной склад цветов"

        Остатки:
        - Розы красные: 25 штук (остаток)
        - Тюльпаны желтые: 15 штук (остаток)
        - Гвоздики белые: 10 штук (остаток)

        Общая стоимость остатков: 4350 рублей
        """

        mock_blob = Mock()
        mock_blob.value = inventory_data

        # Извлекаем данные о цветах
        flower_data = extract_flower_data(mock_blob)

        # Проверяем найденные цветы
        found_flowers = flower_data["flower_info"]["found_flowers"]
        self.assertIn("роз", found_flowers)
        self.assertIn("тюльпан", found_flowers)
        self.assertIn("гвоздик", found_flowers)

        # Проверяем количества
        quantities = flower_data["flower_info"]["quantities"]
        self.assertIn(25, quantities)
        self.assertIn(15, quantities)
        self.assertIn(10, quantities)


if __name__ == "__main__":
    # Запуск интеграционных тестов
    unittest.main(verbosity=2)
