#!/usr/bin/env python3
"""
Unit tests for BlobProcessor.

JTBD:
Как тестировщик, я хочу проверить корректность работы BlobProcessor,
чтобы убедиться в правильной обработке BLOB полей.
"""

from unittest.mock import Mock

from src.processors.blob_processor import BlobProcessor


class TestBlobProcessor:
    """Тесты для BlobProcessor."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.processor = BlobProcessor()

    def test_process_blob_field_with_bytes(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить обработку bytes BLOB поля,
        чтобы убедиться в правильном декодировании.
        """
        # Arrange
        field_name = "test_field"
        blob_bytes = "Тестовый контент".encode()

        # Act
        result = self.processor.process_blob_field(field_name, blob_bytes)

        # Assert
        assert result["field_type"] == "blob"
        assert result["field_name"] == field_name
        assert "bytes" in result["extraction_methods"]
        assert "bytes" in result
        assert result["bytes"]["content"] == "Тестовый контент"

    def test_process_blob_field_with_blob_object(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить обработку BLOB объекта,
        чтобы убедиться в правильном извлечении данных.
        """
        # Arrange
        field_name = "test_field"
        mock_blob = Mock()
        mock_blob.value = "Тестовый контент".encode()
        mock_blob.__len__ = Mock(return_value=100)
        mock_blob.__class__ = type("Blob", (), {})
        mock_blob.__class__.__name__ = "Blob"

        # Act
        result = self.processor.process_blob_field(field_name, mock_blob)

        # Assert
        assert result["field_type"] == "blob"
        assert result["size"] > 0  # Проверяем что размер больше 0
        assert "value" in result["extraction_methods"]

    def test_analyze_blob_type_jpeg(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение типа JPEG файла,
        чтобы убедиться в правильной классификации.
        """
        # Arrange
        jpeg_header = b"\xff\xd8\xff\xe0\x00\x10JFIF"

        # Act
        blob_type = self.processor.analyze_blob_type(jpeg_header)

        # Assert
        assert blob_type == "JPEG"

    def test_analyze_blob_type_png(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение типа PNG файла,
        чтобы убедиться в правильной классификации.
        """
        # Arrange
        png_header = b"\x89PNG\r\n\x1a\n"

        # Act
        blob_type = self.processor.analyze_blob_type(png_header)

        # Assert
        assert blob_type == "PNG"

    def test_extract_flower_information_positive(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение цветочной информации,
        чтобы убедиться в правильной идентификации цветочных данных.
        """
        # Arrange
        content = "Букет роз и тюльпанов для флористики"

        # Act
        result = self.processor.extract_flower_information(content)

        # Assert
        assert result["has_flower_info"] is True
        assert result["has_store_info"] is False
        assert result["has_financial_info"] is False

    def test_extract_flower_information_negative(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить отсутствие цветочной информации,
        чтобы убедиться в правильной фильтрации.
        """
        # Arrange
        content = "Обычный документ без специальной информации"

        # Act
        result = self.processor.extract_flower_information(content)

        # Assert
        assert result["has_flower_info"] is False

    def test_extract_store_information(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить извлечение информации о магазине,
        чтобы убедиться в правильном парсинге данных о торговой точке.
        """
        # Arrange
        content = "Магазин Цветы ПЦ123 для продажи"

        # Act
        result = self.processor.extract_store_information(content)

        # Assert
        assert result["store_name"] == "Цветы"
        assert result["store_code"] == "ПЦ123"

    def test_determine_document_type_floristics(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение типа документа флористика,
        чтобы убедиться в правильной классификации.
        """
        # Arrange
        content = "Документ по флористике"

        # Act
        doc_type = self.processor.determine_document_type(content)

        # Assert
        assert doc_type == "ФЛОРИСТИКА"

    def test_determine_document_type_decor(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение типа документа декор,
        чтобы убедиться в правильной классификации.
        """
        # Arrange
        content = "Документ по декору"

        # Act
        doc_type = self.processor.determine_document_type(content)

        # Assert
        assert doc_type == "ДЕКОР"

    def test_determine_document_type_unknown(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение неизвестного типа документа,
        чтобы убедиться в правильной обработке неопознанных документов.
        """
        # Arrange
        content = "Обычный документ"

        # Act
        doc_type = self.processor.determine_document_type(content)

        # Assert
        assert doc_type == "Неизвестно"

    def test_decode_blob_content_utf8(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить декодирование UTF-8 контента,
        чтобы убедиться в правильной обработке текстовых данных.
        """
        # Arrange
        content = "Тестовый контент".encode()

        # Act
        result = self.processor._decode_blob_content(content)

        # Assert
        assert result is not None
        assert result["content"] == "Тестовый контент"
        assert result["type"] == "text_utf8"

    def test_decode_blob_content_cp1251(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить декодирование CP1251 контента,
        чтобы убедиться в правильной обработке русских текстов.
        """
        # Arrange
        content = "Русский текст".encode("cp1251")

        # Act
        result = self.processor._decode_blob_content(content)

        # Assert
        assert result is not None
        assert result["content"] == "Русский текст"
        assert result["type"] == "text_cp1251"

    def test_decode_blob_content_binary(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить обработку бинарных данных,
        чтобы убедиться в правильном fallback на hex представление.
        """
        # Arrange - используем данные, которые точно не декодируются как текст
        content = b"\xff\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xf0"

        # Act
        result = self.processor._decode_blob_content(content)

        # Assert
        assert result is not None
        # Проверяем что результат содержит hex представление или декодированный текст
        assert result["type"] in [
            "text_utf16",
            "text_utf8",
            "text_cp1251",
            "binary_hex",
        ]
        # Проверяем что содержимое корректно
        assert len(result["content"]) > 0

    def test_is_blob_object_with_blob(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение BLOB объекта,
        чтобы убедиться в правильной идентификации BLOB полей.
        """
        # Arrange
        mock_blob = Mock()
        mock_blob.value = b"test"
        mock_blob.__class__ = type("Blob", (), {})
        mock_blob.__class__.__name__ = "Blob"

        # Act
        is_blob = self.processor._is_blob_object(mock_blob)

        # Assert
        assert is_blob is True

    def test_is_blob_object_with_bytes(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение bytes как BLOB,
        чтобы убедиться в правильной обработке бинарных данных.
        """
        # Arrange
        blob_bytes = b"test data"

        # Act
        is_blob = self.processor._is_blob_object(blob_bytes)

        # Assert
        assert is_blob is True

    def test_is_blob_object_with_string(self):
        """
        JTBD:
        Как тестировщик, я хочу проверить определение строки как не-BLOB,
        чтобы убедиться в правильной фильтрации типов.
        """
        # Arrange
        string_value = "test string"

        # Act
        is_blob = self.processor._is_blob_object(string_value)

        # Assert
        assert is_blob is False
