#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit тесты для BlobProcessor
Согласно TDD Documentation Standard
"""

from unittest.mock import Mock

from src.utils.blob_processor import BlobProcessor


class TestBlobProcessor:
    """Тесты для BlobProcessor"""

    def setup_method(self) -> None:
        """Настройка для каждого теста"""
        self.processor = BlobProcessor()

    def test_extract_blob_content_value_method(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение содержимого через value атрибут,
        чтобы убедиться в корректности работы основного метода.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = "test content"

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content == "test content"
        assert result.extraction_methods is not None
        assert "value" in result.extraction_methods
        assert result.content_length == len("test content")
        assert result.quality_score > 0

    def test_extract_blob_content_iterator_method(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение содержимого через итератор,
        чтобы убедиться в корректности работы альтернативного метода.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.__iter__ = Mock(return_value=iter(["part1", "part2"]))
        # Убираем value атрибут чтобы тестировать iterator метод
        del mock_blob.value

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content == "part1\npart2"
        assert result.extraction_methods is not None
        assert "iterator" in result.extraction_methods

    def test_extract_blob_content_bytes_method(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение содержимого через bytes,
        чтобы убедиться в корректности работы бинарного метода.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.__bytes__ = Mock(return_value=b"test bytes")
        # Убираем value атрибут чтобы тестировать bytes метод
        del mock_blob.value

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content == "test bytes"
        assert result.extraction_methods is not None
        assert "bytes" in result.extraction_methods

    def test_extract_blob_content_str_method(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение содержимого через str,
        чтобы убедиться в корректности работы строкового метода.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.configure_mock(__str__=Mock(return_value="string content"))
        # Убираем value атрибут чтобы тестировать str метод
        del mock_blob.value

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content == "string content"
        assert result.extraction_methods is not None
        assert "str" in result.extraction_methods

    def test_extract_blob_content_direct_data_method(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение содержимого через _data атрибут,
        чтобы убедиться в корректности работы прямого метода.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob._data = "direct data"
        # Убираем value атрибут чтобы тестировать direct_data метод
        del mock_blob.value

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content == "direct data"
        assert result.extraction_methods is not None
        assert "direct_data" in result.extraction_methods

    def test_extract_blob_content_flower_data_type(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение данных о цветах,
        чтобы убедиться в корректности специализированной обработки.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = "розы красные тюльпаны желтые"

        # Act
        result = self.processor.extract_blob_content(mock_blob, "flower")

        # Assert
        assert result.content == "розы красные тюльпаны желтые"
        assert result.quality_score > 0.3  # Должен быть бонус за цветы

    def test_extract_blob_content_temporal_data_type(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение временных данных,
        чтобы убедиться в корректности специализированной обработки.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = "дата создания 2024-01-01 время 12:00"

        # Act
        result = self.processor.extract_blob_content(mock_blob, "temporal")

        # Assert
        assert result.content == "дата создания 2024-01-01 время 12:00"
        assert result.quality_score > 0.3  # Должен быть бонус за временные данные

    def test_extract_blob_content_financial_data_type(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение финансовых данных,
        чтобы убедиться в корректности специализированной обработки.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = "сумма 1000 рублей цена товара"

        # Act
        result = self.processor.extract_blob_content(mock_blob, "financial")

        # Assert
        assert result.content == "сумма 1000 рублей цена товара"
        assert result.quality_score > 0.3  # Должен быть бонус за финансовые данные

    def test_extract_blob_content_no_content(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить обработку пустого содержимого,
        чтобы убедиться в корректности обработки ошибок.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = None

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content is None
        assert result.extraction_methods is not None
        assert len(result.extraction_methods) == 0
        assert result.quality_score == 0.0

    def test_extract_blob_content_error_handling(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить обработку ошибок,
        чтобы убедиться в корректности обработки исключений.
        """
        # Arrange
        mock_blob = Mock()
        # Создаем Mock который возвращает невалидные данные
        mock_blob.value = None

        # Act
        result = self.processor.extract_blob_content(mock_blob)

        # Assert
        assert result.content is None
        assert result.extraction_methods == []
        assert result.quality_score == 0.0

    def test_is_blob_field_true(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение BLOB полей,
        чтобы убедиться в корректности классификации полей.
        """
        # Arrange
        mock_field = Mock()
        mock_field.configure_mock(
            __str__=Mock(return_value="<onec_dtools.database_reader.Blob object>")
        )

        # Act
        result = self.processor.is_blob_field(mock_field)

        # Assert
        assert result is True

    def test_is_blob_field_false(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение обычных полей,
        чтобы убедиться в корректности классификации полей.
        """
        # Arrange
        mock_field = Mock()
        mock_field.configure_mock(__str__=Mock(return_value="regular string value"))

        # Act
        result = self.processor.is_blob_field(mock_field)

        # Assert
        assert result is False

    def test_safe_get_blob_content_success(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить безопасное извлечение содержимого,
        чтобы убедиться в корректности работы основного интерфейса.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = "safe content"

        # Act
        result = self.processor.safe_get_blob_content(mock_blob)

        # Assert
        assert result == "safe content"

    def test_safe_get_blob_content_failure(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить обработку ошибок при извлечении,
        чтобы убедиться в корректности обработки исключений.
        """
        # Arrange
        mock_blob = Mock()
        # Создаем Mock который выбрасывает исключение при обращении к value
        mock_blob.value = Mock(side_effect=Exception("Test error"))

        # Act
        result = self.processor.safe_get_blob_content(mock_blob)

        # Assert
        assert result is None
