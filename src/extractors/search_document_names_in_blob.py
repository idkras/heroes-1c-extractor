#!/usr/bin/env python3

import logging
from typing import Any

from src.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class DocumentNamesBlobExtractor(BaseExtractor):
    """
    Поиск названий документов в BLOB полях

    JTBD:
    Как система анализа документов, я хочу найти реальные названия документов в BLOB полях,
    чтобы понять назначение каждого типа документа.
    """

    def extract(self, table_name: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Поиск названий документов в BLOB полях
        ЦЕЛЬ: Найти реальные названия документов для понимания их назначения
        """
        print("🔍 ПОИСК НАЗВАНИЙ ДОКУМЕНТОВ В BLOB ПОЛЯХ")
        print("🎯 ЦЕЛЬ: Определить назначение каждого типа документа")
        print("=" * 60)

        results: dict[str, Any] = {
            "document_names": {},
            "blob_content_samples": {},
            "metadata": {
                "extraction_date": self.metadata["extraction_date"],
                "source_file": self.metadata["source_file"],
                "total_tables": (
                    len(self.db.tables) if hasattr(self, "db") and self.db else 0
                ),
            },
        }

        if not hasattr(self, "db") or self.db is None:
            print("❌ База данных не открыта")
            return [results]

        print(f"\n📊 Всего таблиц в базе: {len(self.db.tables):,}")

        # Поиск таблиц документов
        document_tables = self.get_document_tables()
        print(f"📄 Найдено таблиц документов: {len(document_tables)}")

        # Анализируем каждую таблицу документов
        for table_name in document_tables[:5]:  # Ограничиваем для тестирования
            print(f"\n🔍 Анализ таблицы: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 100 записей
            sample_size = min(100, len(table))
            blob_samples = []

            for i in range(sample_size):
                try:
                    row = table[i]
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                        # Ищем BLOB поля
                        for field_name, value in row_dict.items():
                            if hasattr(value, "value") and value.value is not None:
                                blob_content = self.extract_blob_content(value)
                                if blob_content and len(blob_content) > 10:
                                    blob_samples.append(
                                        {
                                            "table_name": table_name,
                                            "field_name": field_name,
                                            "content": (
                                                blob_content[:200] + "..."
                                                if len(blob_content) > 200
                                                else blob_content
                                            ),
                                            "length": len(blob_content),
                                        },
                                    )

                except Exception as e:
                    logger.warning(
                        f"Ошибка обработки записи {i} в таблице {table_name}: {e}",
                    )
                    continue

            if blob_samples:
                results["blob_content_samples"][table_name] = blob_samples[
                    :10
                ]  # Первые 10 образцов
                print(f"   ✅ Найдено {len(blob_samples)} BLOB образцов")

        return [results]


def search_document_names_in_blob() -> dict[str, Any]:
    """
    Функция-обертка для обратной совместимости
    """
    from ..processors.database_connector import DatabaseConnector

    db_connector = DatabaseConnector("data/raw/1Cv8.1CD")
    extractor = DocumentNamesBlobExtractor(db_connector=db_connector)
    return extractor.run()
