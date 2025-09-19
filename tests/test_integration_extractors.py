#!/usr/bin/env python3

"""
Integration тесты для рефакторированных extractors
Проверяем совместимость и работу всех extractors
"""

import unittest
from unittest.mock import Mock, patch

from src.extractors.search_all_document_types import AllDocumentTypesExtractor
from src.extractors.search_all_missing_documents import AllMissingDocumentsExtractor
from src.extractors.search_document_names_in_blob import DocumentNamesBlobExtractor
from src.extractors.search_documents_by_criteria import DocumentsByCriteriaExtractor
from src.extractors.search_quality_documents import QualityDocumentsExtractor


class TestIntegrationExtractors(unittest.TestCase):
    """
    Integration тесты для всех рефакторированных extractors
    """

    def setUp(self):
        """Настройка тестов"""
        self.extractors = [
            DocumentNamesBlobExtractor(),
            DocumentsByCriteriaExtractor(),
            AllDocumentTypesExtractor(),
            AllMissingDocumentsExtractor(),
            QualityDocumentsExtractor(),
        ]

    def test_all_extractors_inherit_base(self):
        """Тест что все extractors наследуют BaseExtractor"""
        for extractor in self.extractors:
            self.assertTrue(hasattr(extractor, "extract"))
            self.assertTrue(hasattr(extractor, "run"))
            self.assertTrue(hasattr(extractor, "open_database"))
            self.assertTrue(hasattr(extractor, "get_document_tables"))

    def test_all_extractors_have_metadata(self):
        """Тест что все extractors имеют метаданные"""
        for extractor in self.extractors:
            self.assertIsNotNone(extractor.metadata)
            self.assertIn("extraction_date", extractor.metadata)
            self.assertIn("source_file", extractor.metadata)
            self.assertIn("extractor_class", extractor.metadata)

    def test_all_extractors_have_extract_method(self):
        """Тест что все extractors имеют метод extract"""
        for extractor in self.extractors:
            self.assertTrue(callable(extractor.extract))
            # Проверяем что метод возвращает словарь
            with patch.object(extractor, "db", None):
                result = extractor.extract()
                self.assertIsInstance(result, dict)

    def test_all_extractors_handle_no_database(self):
        """Тест что все extractors корректно обрабатывают отсутствие базы данных"""
        for extractor in self.extractors:
            extractor.db = None
            result = extractor.extract()
            self.assertIsInstance(result, dict)
            # Должен содержать ошибку или пустой результат
            self.assertTrue("error" in result or len(result) > 0)

    def test_all_extractors_use_common_methods(self):
        """Тест что все extractors используют общие методы BaseExtractor"""
        for extractor in self.extractors:
            # Проверяем наличие общих методов
            self.assertTrue(hasattr(extractor, "get_document_tables"))
            self.assertTrue(hasattr(extractor, "get_reference_tables"))
            self.assertTrue(hasattr(extractor, "get_register_tables"))
            self.assertTrue(hasattr(extractor, "extract_blob_content"))
            self.assertTrue(hasattr(extractor, "save_results"))

    def test_extractors_return_consistent_structure(self):
        """Тест что все extractors возвращают консистентную структуру"""
        for extractor in self.extractors:
            with patch.object(extractor, "db", Mock()) as mock_db:
                mock_db.tables = Mock()
                mock_db.tables.__len__ = Mock(return_value=0)
                with patch.object(extractor, "get_document_tables", return_value=[]):
                    with patch.object(
                        extractor,
                        "get_reference_tables",
                        return_value=[],
                    ):
                        with patch.object(
                            extractor,
                            "get_register_tables",
                            return_value=[],
                        ):
                            result = extractor.extract()
                            self.assertIsInstance(result, dict)
                            # Проверяем что результат не пустой
                            self.assertTrue(len(result) > 0)

    def test_all_extractors_have_jtbd_documentation(self):
        """Тест что все extractors имеют JTBD документацию"""
        for extractor in self.extractors:
            # Проверяем что класс имеет docstring
            self.assertIsNotNone(extractor.__class__.__doc__)
            # Проверяем что docstring содержит JTBD
            docstring = extractor.__class__.__doc__
            self.assertIn("JTBD", docstring)

    def test_extractors_are_independent(self):
        """Тест что extractors работают независимо"""
        for i, extractor1 in enumerate(self.extractors):
            for j, extractor2 in enumerate(self.extractors):
                if i != j:
                    # Проверяем что это разные объекты
                    self.assertIsNot(extractor1, extractor2)
                    # Проверяем что у них разные метаданные
                    self.assertNotEqual(extractor1.metadata, extractor2.metadata)

    def test_all_extractors_handle_errors_gracefully(self):
        """Тест что все extractors корректно обрабатывают ошибки"""
        for extractor in self.extractors:
            # Симулируем ошибку в методе extract
            with patch.object(
                extractor,
                "extract",
                side_effect=Exception("Test error"),
            ):
                result = extractor.run()
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)

    def test_extractors_use_common_blob_processing(self):
        """Тест что все extractors используют общую BLOB обработку"""
        for extractor in self.extractors:
            # Проверяем что есть метод для BLOB обработки
            self.assertTrue(hasattr(extractor, "extract_blob_content"))
            # Проверяем что метод работает
            result = extractor.extract_blob_content(None)
            self.assertTrue(result is None or isinstance(result, str))


if __name__ == "__main__":
    unittest.main()
