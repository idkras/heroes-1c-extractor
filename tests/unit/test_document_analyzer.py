"""
Unit тесты для DocumentAnalyzer
Согласно TDD Documentation Standard
"""

import sys
from unittest.mock import MagicMock, Mock

# Mock onec_dtools для тестов
onec_dtools_mock = MagicMock()
onec_dtools_mock.database_reader.DatabaseReader = MagicMock()
sys.modules["onec_dtools"] = onec_dtools_mock
sys.modules["onec_dtools.database_reader"] = onec_dtools_mock.database_reader

# Импортируем после мокирования
from src.utils.document_analyzer import DocumentAnalyzer


class TestDocumentAnalyzer:
    """Тесты для DocumentAnalyzer"""

    def setup_method(self) -> None:
        """Настройка тестового окружения"""
        self.analyzer = DocumentAnalyzer()

    def test_analyze_document_structure_basic(self) -> None:
        """
        JTBD:
        Как анализатор документов, я хочу проанализировать структуру документа,
        чтобы извлечь поля, BLOB данные и найти ключевые слова.
        """
        # Arrange
        table_name = "TestTable"
        record_index = 0
        record_data = {
            "id": "123",
            "name": "Test Document",
            "description": "Test description",
        }

        # Act
        result = self.analyzer.analyze_document_structure(
            record_data, table_name, record_index
        )

        # Assert
        assert result.table_name == table_name
        assert result.record_count == 1
        assert "id" in result.fields
        assert "name" in result.fields
        assert "description" in result.fields
        assert result.blob_fields == []
        assert result.sample_data["id"] == "123"

    def test_analyze_document_structure_with_blobs(self) -> None:
        """
        JTBD:
        Как анализатор документов, я хочу обработать BLOB поля,
        чтобы извлечь их содержимое для анализа.
        """
        # Arrange
        table_name = "TestTable"
        record_index = 0
        record_data = {
            "id": "123",
            "content": Mock(),  # BLOB поле
            "description": "Test description",
        }

        # Act
        result = self.analyzer.analyze_document_structure(
            record_data, table_name, record_index
        )

        # Assert
        assert result.table_name == table_name
        assert result.record_count == 1
        assert "id" in result.fields
        assert "content" in result.fields
        assert "description" in result.fields

    def test_analyze_document_structure_empty_data(self):
        """
        JTBD:
        Как анализатор документов, я хочу корректно обработать пустые данные,
        чтобы избежать ошибок.
        """
        # Arrange
        table_name = "TestTable"
        record_index = 0
        record_data: dict[str, str] = {}

        # Act
        result = self.analyzer.analyze_document_structure(
            record_data, table_name, record_index
        )

        # Assert
        assert result.table_name == table_name
        assert result.record_count == 0  # Анализируется пустая запись
        assert result.fields == []
        assert result.blob_fields == []
        assert result.sample_data == {}

    def test_analyze_document_structure_metadata(self):
        """
        JTBD:
        Как анализатор документов, я хочу сохранить метаданные анализа,
        чтобы обеспечить трассируемость результатов.
        """
        # Arrange
        table_name = "TestTable"
        record_index = 0
        record_data = {"id": "123", "name": "Test Document"}

        # Act
        result = self.analyzer.analyze_document_structure(
            record_data, table_name, record_index
        )

        # Assert
        assert result.table_name == table_name
        assert result.record_count == 1
        assert "id" in result.fields
        assert "name" in result.fields
        assert result.analysis_metadata is not None
        assert "analysis_timestamp" in result.analysis_metadata
