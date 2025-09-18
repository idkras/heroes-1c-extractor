#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Базовый класс для всех extractors
Устраняет дублирование кода и обеспечивает единую архитектуру
"""

import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_processor import BlobProcessor
from src.utils.document_analyzer import DocumentAnalyzer
from src.utils.keyword_searcher import KeywordSearcher


class BaseExtractor(ABC):
    """
    JTBD:
    Как система базового класса, я хочу предоставить общую функциональность для всех extractors,
    чтобы устранить дублирование кода и обеспечить единую архитектуру.
    """

    def __init__(self) -> None:
        self.blob_processor = BlobProcessor()
        self.keyword_searcher = KeywordSearcher()
        self.document_analyzer = DocumentAnalyzer()
        self.db: Optional[DatabaseReader] = None
        self.results: Dict[str, Any] = {}

    def open_database(self, db_path: str = "data/raw/1Cv8.1CD") -> bool:
        """
        JTBD:
        Как система открытия базы данных, я хочу безопасно открыть 1C базу данных,
        чтобы все extractors могли работать с данными без дублирования кода.

        Args:
            db_path: Путь к файлу базы данных

        Returns:
            bool: True если база открыта успешно
        """
        try:
            # Применяем патч для onec_dtools
            self._apply_patch()

            with open(db_path, "rb") as f:
                self.db = DatabaseReader(f)
                print(f"✅ База данных открыта успешно: {db_path}")
                return True

        except Exception as e:
            print(f"❌ Ошибка открытия базы данных: {e}")
            return False

    def _apply_patch(self) -> None:
        """
        Применяет патч для onec_dtools
        """
        try:
            patch_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "patches", "onec_dtools"
            )
            sys.path.insert(0, patch_path)
            from patches.onec_dtools.onec_dtools_patch import apply_patch

            apply_patch()
        except Exception as e:
            # Если патч не найден, продолжаем без него
            logger.debug(f"Патч не найден: {e}")

    def get_document_tables(self, max_tables: int = 50) -> List[tuple]:
        """
        JTBD:
        Как система поиска таблиц документов, я хочу найти все таблицы документов,
        чтобы extractors могли анализировать их без дублирования кода.

        Args:
            max_tables: Максимальное количество таблиц для анализа

        Returns:
            List[tuple]: Список (table_name, record_count) отсортированный по размеру
        """
        if not self.db:
            return []

        document_tables = []
        for table_name in self.db.tables.keys():
            if table_name.startswith("_DOCUMENT") and "_VT" not in table_name:
                table = self.db.tables[table_name]
                if len(table) > 0:
                    document_tables.append((table_name, len(table)))

        # Сортируем по размеру (большие таблицы первыми)
        document_tables.sort(key=lambda x: x[1], reverse=True)
        return document_tables[:max_tables]

    def get_reference_tables(self, max_tables: int = 30) -> List[tuple]:
        """
        JTBD:
        Как система поиска справочников, я хочу найти все справочники,
        чтобы extractors могли анализировать их без дублирования кода.

        Args:
            max_tables: Максимальное количество таблиц для анализа

        Returns:
            List[tuple]: Список (table_name, record_count) отсортированный по размеру
        """
        if not self.db:
            return []

        reference_tables = []
        for table_name in self.db.tables.keys():
            if table_name.startswith("_Reference"):
                table = self.db.tables[table_name]
                if len(table) > 0:
                    reference_tables.append((table_name, len(table)))

        # Сортируем по размеру
        reference_tables.sort(key=lambda x: x[1], reverse=True)
        return reference_tables[:max_tables]

    def analyze_table_records(
        self, table_name: str, max_records: int = 10
    ) -> List[Dict[str, Any]]:
        """
        JTBD:
        Как система анализа записей таблицы, я хочу безопасно прочитать записи из таблицы,
        чтобы extractors могли анализировать данные без дублирования кода.

        Args:
            table_name: Имя таблицы
            max_records: Максимальное количество записей для анализа

        Returns:
            List[Dict[str, Any]]: Список записей таблицы
        """
        if not self.db or table_name not in self.db.tables:
            return []

        try:
            table = self.db.tables[table_name]
            records = []

            for i in range(min(max_records, len(table))):
                try:
                    row = table[i]
                    if not row.is_empty:
                        row_data = row.as_dict()
                        records.append(row_data)
                except Exception as e:
                    print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                    continue

            return records

        except Exception as e:
            print(f"    ⚠️ Ошибка анализа таблицы {table_name}: {e}")
            return []

    def save_results(self, filename: str, results: Dict[str, Any]) -> bool:
        """
        JTBD:
        Как система сохранения результатов, я хочу безопасно сохранить результаты анализа,
        чтобы extractors могли сохранять данные без дублирования кода.

        Args:
            filename: Имя файла для сохранения
            results: Словарь с результатами

        Returns:
            bool: True если сохранение успешно
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ Результаты сохранены в {filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения результатов: {e}")
            return False

    def create_metadata(self, source_file: str = "data/raw/1Cv8.1CD") -> Dict[str, Any]:
        """
        JTBD:
        Как система создания метаданных, я хочу создать стандартные метаданные,
        чтобы все extractors имели единый формат результатов.

        Args:
            source_file: Путь к исходному файлу

        Returns:
            Dict[str, Any]: Словарь с метаданными
        """
        return {
            "extraction_date": datetime.now().isoformat(),
            "source_file": source_file,
            "extractor_class": self.__class__.__name__,
            "total_tables_analyzed": 0,
            "documents_analyzed": 0,
        }

    @abstractmethod
    def extract(self) -> Optional[Dict[str, Any]]:
        """
        JTBD:
        Как система извлечения данных, я хочу определить интерфейс для извлечения данных,
        чтобы каждый extractor реализовал свою логику извлечения.

        Returns:
            Optional[Dict[str, Any]]: Результаты извлечения или None при ошибке
        """
        pass

    def run(self, db_path: str = "data/raw/1Cv8.1CD") -> Optional[Dict[str, Any]]:
        """
        JTBD:
        Как система запуска extractor, я хочу запустить полный цикл извлечения данных,
        чтобы extractors могли работать единообразно.

        Args:
            db_path: Путь к файлу базы данных

        Returns:
            Optional[Dict[str, Any]]: Результаты извлечения или None при ошибке
        """
        print(f"🔍 Запуск {self.__class__.__name__}")
        print("=" * 60)

        # Открываем базу данных
        if not self.open_database(db_path):
            return None

        # Запускаем извлечение данных
        try:
            results = self.extract()
            if results:
                print(f"✅ {self.__class__.__name__} завершен успешно")
                return results
            else:
                print(f"❌ {self.__class__.__name__} завершен с ошибками")
                return None
        except Exception as e:
            print(f"❌ Ошибка в {self.__class__.__name__}: {e}")
            return None
