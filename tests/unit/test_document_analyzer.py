#!/usr/bin/env python3
"""
Unit тесты для DocumentAnalyzer

JTBD:
Как тестировщик, я хочу протестировать DocumentAnalyzer с различными типами данных,
чтобы убедиться в корректности анализа документов и извлечения метаданных.
"""

from datetime import datetime

import pytest

from src.processors.document_analyzer import DocumentAnalyzer


class TestDocumentAnalyzer:
    """Тесты для DocumentAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Фикстура для DocumentAnalyzer"""
        return DocumentAnalyzer()

    @pytest.fixture
    def sample_row_dict(self):
        """Фикстура с примером данных документа"""
        return {
            "_NUMBER": "00000053131",
            "_DATE_TIME": datetime(2015, 8, 16, 10, 30, 0),
            "_FLD4239": 8700.0,
            "_FLD4229": "Флор на Магазин ПЦ022 (Чеховский) от 16.08.2015",
            "_FLD4240": 1,
            "_POSTED": True,
            "_MARKED": False,
            "field_33": 100.0,
            "field_34": "Розничная продажа",
        }

    def test_analyze_document_structure(self, analyzer, sample_row_dict):
        """Тест анализа структуры документа"""
        field_analysis, structure = analyzer.analyze_document_structure(sample_row_dict)

        # Проверяем, что все поля проанализированы
        assert len(field_analysis) == len(sample_row_dict)

        # Проверяем, что поля классифицированы
        assert "_NUMBER" in structure.number_fields
        assert "_DATE_TIME" in structure.date_fields
        assert "_FLD4239" in structure.amount_fields
        assert "_FLD4229" in structure.description_fields
        assert "field_34" in structure.sale_type_fields

    def test_analyze_field_numeric(self, analyzer):
        """Тест анализа числового поля"""
        field_info = analyzer._analyze_field("_FLD4239", 8700.0)

        assert field_info.name == "_FLD4239"
        assert field_info.value == 8700.0
        assert field_info.type == "float"
        assert field_info.is_numeric is True
        assert field_info.is_date is False
        assert field_info.is_string is False
        assert field_info.is_blob is False
        assert field_info.is_empty is False
        assert field_info.size == 0

    def test_analyze_field_string(self, analyzer):
        """Тест анализа строкового поля"""
        field_info = analyzer._analyze_field("_FLD4229", "Флор на Магазин ПЦ022")

        assert field_info.name == "_FLD4229"
        assert field_info.value == "Флор на Магазин ПЦ022"
        assert field_info.type == "str"
        assert field_info.is_numeric is False
        assert field_info.is_date is False
        assert field_info.is_string is True
        assert field_info.is_blob is False
        assert field_info.is_empty is False
        assert field_info.size == len("Флор на Магазин ПЦ022")

    def test_analyze_field_datetime(self, analyzer):
        """Тест анализа поля с датой"""
        dt = datetime(2015, 8, 16, 10, 30, 0)
        field_info = analyzer._analyze_field("_DATE_TIME", dt)

        assert field_info.name == "_DATE_TIME"
        assert field_info.value == dt
        assert field_info.type == "datetime"
        assert field_info.is_numeric is False
        assert field_info.is_date is True
        assert field_info.is_string is False
        assert field_info.is_blob is False
        assert field_info.is_empty is False

    def test_extract_document_metadata(self, analyzer, sample_row_dict):
        """Тест извлечения метаданных документа"""
        field_analysis, structure = analyzer.analyze_document_structure(sample_row_dict)
        metadata = analyzer.extract_document_metadata(field_analysis, structure)

        assert metadata.document_number == "00000053131"
        assert metadata.document_date == "2015-08-16T10:30:00"
        assert metadata.total_amount == 8700.0
        assert metadata.document_type == "ФЛОРИСТИКА"
        assert metadata.store_name == "ПЦ022 (Чеховский)"
        assert metadata.store_code == "ПЦ022"
        assert metadata.sale_type == "Розничная продажа"

    def test_analyze_blob_content_floristic(self, analyzer):
        """Тест анализа BLOB содержимого с цветочной информацией"""
        blob_content = "Флор на Магазин ПЦ022 с розовыми розами и белыми тюльпанами"
        analysis = analyzer.analyze_blob_content(blob_content)

        assert analysis["has_floristic_info"] is True
        assert analysis["has_store_info"] is True
        assert "розов" in analysis["colors_found"]
        assert "бел" in analysis["colors_found"]
        assert "пц" in analysis["stores_found"]

    def test_create_document_summary(self, analyzer, sample_row_dict):
        """Тест создания сводки документа"""
        field_analysis, structure = analyzer.analyze_document_structure(sample_row_dict)
        metadata = analyzer.extract_document_metadata(field_analysis, structure)
        summary = analyzer.create_document_summary(field_analysis, structure, metadata)

        # Проверяем метаданные
        assert summary["metadata"]["document_number"] == "00000053131"
        assert summary["metadata"]["document_type"] == "ФЛОРИСТИКА"
        assert summary["metadata"]["total_amount"] == 8700.0

        # Проверяем структуру
        assert "_NUMBER" in summary["structure"]["number_fields"]
        assert "_DATE_TIME" in summary["structure"]["date_fields"]
        assert "_FLD4239" in summary["structure"]["amount_fields"]

        # Проверяем статистику
        assert summary["statistics"]["total_fields"] == len(sample_row_dict)
        assert summary["statistics"]["numeric_fields"] > 0
        assert summary["statistics"]["string_fields"] > 0
        assert summary["statistics"]["date_fields"] > 0
