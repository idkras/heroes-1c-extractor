#!/usr/bin/env python3

import logging
from datetime import datetime
from typing import Any

from src.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class AllDocumentTypesExtractor(BaseExtractor):
    """
    Поиск всех типов документов

    JTBD:
    Как система анализа документов, я хочу найти все типы документов,
    чтобы отследить полный путь от сырья до цветочков в магазине.
    """

    def extract(self, table_name: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Поиск всех типов документов согласно уточненному плану
        ЦЕЛЬ: Отследить весь путь от сырья до цветочков в магазине
        """
        print("🔍 ПОИСК ВСЕХ ТИПОВ ДОКУМЕНТОВ")
        print("🎯 ЦЕЛЬ: Полный путь цветов от сырья до магазина")
        print("=" * 60)

        if not hasattr(self, "db") or self.db is None:
            print("❌ База данных не открыта")
            return []

        results: dict[str, Any] = {
            "document_types": {},
            "references": {},
            "accumulation_registers": {},
            "information_registers": {},
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "source_file": self.metadata["source_file"],
                "total_tables": len(self.db.tables),
            },
        }

        # Получаем все типы таблиц
        document_tables = self.get_document_tables()
        reference_tables = self.get_reference_tables()
        register_tables = self.get_register_tables()

        print(f"📄 Документы: {len(document_tables)}")
        print(f"📚 Справочники: {len(reference_tables)}")
        print(f"📊 Регистры: {len(register_tables)}")

        # Анализируем документы
        for table_name in document_tables[:5]:  # Ограничиваем для тестирования
            print(f"\n🔍 Анализ документа: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 20 записей
            sample_size = min(20, len(table))
            doc_samples = []

            for i in range(sample_size):
                try:
                    row = table[i]
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                        # Извлекаем основные поля
                        doc_info: dict[str, Any] = {
                            "table_name": table_name,
                            "row_index": i,
                            "fields": {},
                            "field_count": len(row_dict),
                        }

                        # Анализируем поля
                        for field_name, value in row_dict.items():
                            if isinstance(value, (str, int, float, bool)):
                                doc_info["fields"][field_name] = str(value)[
                                    :100
                                ]  # Ограничиваем длину

                        doc_samples.append(doc_info)

                except Exception as e:
                    logger.warning(
                        f"Ошибка обработки записи {i} в таблице {table_name}: {e}",
                    )
                    continue

            if doc_samples:
                results["document_types"][table_name] = {
                    "total_records": len(table),
                    "sample_records": doc_samples[:5],  # Первые 5 записей
                    "field_names": (
                        list(doc_samples[0]["fields"].keys())
                        if doc_samples and doc_samples[0].get("fields")
                        else []
                    ),
                }
                print(f"   ✅ Найдено {len(doc_samples)} образцов документов")

        # Анализируем справочники
        for table_name in reference_tables[:3]:  # Ограничиваем для тестирования
            print(f"\n📚 Анализ справочника: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 10 записей
            sample_size = min(10, len(table))
            ref_samples = []

            for i in range(sample_size):
                try:
                    row = table[i]
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                        ref_info = {
                            "table_name": table_name,
                            "row_index": i,
                            "fields": {},
                        }

                        for field_name, value in row_dict.items():
                            if isinstance(value, (str, int, float, bool)):
                                if "fields" in ref_info and isinstance(
                                    ref_info["fields"],
                                    dict,
                                ):
                                    ref_info["fields"][field_name] = str(value)[:100]

                        ref_samples.append(ref_info)

                except Exception as e:
                    logger.warning(
                        f"Ошибка обработки записи {i} в таблице {table_name}: {e}",
                    )
                    continue

            if ref_samples:
                results["references"][table_name] = {
                    "total_records": len(table),
                    "sample_records": ref_samples[:3],  # Первые 3 записи
                    "field_names": (
                        list(ref_samples[0]["fields"].keys())
                        if ref_samples
                        and ref_samples[0]
                        and "fields" in ref_samples[0]
                        and isinstance(ref_samples[0]["fields"], dict)
                        else []
                    ),
                }
                print(f"   ✅ Найдено {len(ref_samples)} образцов справочников")

        return [results]


def search_all_document_types() -> dict[str, Any]:
    """
    Функция-обертка для обратной совместимости
    """
    from ..processors.database_connector import DatabaseConnector

    db_connector = DatabaseConnector("data/raw/1Cv8.1CD")
    extractor = AllDocumentTypesExtractor(db_connector=db_connector)
    return extractor.run()
