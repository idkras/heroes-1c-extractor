#!/usr/bin/env python3

import logging
from datetime import datetime
from typing import Any

from src.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class AllMissingDocumentsExtractor(BaseExtractor):
    """
    Поиск всех недостающих документов для JTBD сценариев

    JTBD:
    Как система анализа недостающих данных, я хочу найти справочники, регистры, документы с цветами и типами букетов,
    чтобы обеспечить полноту данных для JTBD сценариев.
    """

    def extract(self) -> dict[str, Any]:
        """
        Поиск всех недостающих документов для JTBD сценариев
        ЦЕЛЬ: Найти справочники, регистры, документы с цветами и типами букетов
        """
        print("🔍 ПОИСК ВСЕХ НЕДОСТАЮЩИХ ДОКУМЕНТОВ")
        print("🎯 ЦЕЛЬ: JTBD сценарии - цвета, типы букетов, склады, подразделения")
        print("=" * 60)

        if self.db is None:
            print("❌ База данных не открыта")
            return {"error": "База данных не открыта"}

        results: dict[str, Any] = {
            "missing_documents": {},
            "found_references": {},
            "found_registers": {},
            "jtbd_scenarios": {},
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "source_file": self.metadata["source_file"],
                "total_tables": len(self.db.tables),
            },
        }

        # JTBD ключевые слова для поиска
        jtbd_keywords = {
            "цвета": ["цвет", "красный", "белый", "розовый", "желтый", "синий"],
            "букеты": [
                "букет",
                "композиция",
                "аранжировка",
                "свадебный",
                "праздничный",
            ],
            "склады": ["склад", "хранилище", "холодильник", "температура"],
            "подразделения": ["отдел", "подразделение", "магазин", "филиал"],
            "поставщики": ["поставщик", "производитель", "ферма", "выращивание"],
        }

        # Получаем все типы таблиц
        document_tables = self.get_document_tables()
        reference_tables = self.get_reference_tables()
        register_tables = self.get_register_tables()

        print(f"📄 Документы: {len(document_tables)}")
        print(f"📚 Справочники: {len(reference_tables)}")
        print(f"📊 Регистры: {len(register_tables)}")

        # Анализируем справочники на предмет JTBD данных
        for table_name in reference_tables[:5]:  # Ограничиваем для тестирования
            print(f"\n📚 Анализ справочника: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 20 записей
            sample_size = min(20, len(table))
            jtbd_matches = []

            for i in range(sample_size):
                try:
                    row = table[i]
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                        # Ищем JTBD ключевые слова
                        for field_name, value in row_dict.items():
                            if isinstance(value, str):
                                for category, keywords in jtbd_keywords.items():
                                    for keyword in keywords:
                                        if keyword.lower() in value.lower():
                                            jtbd_matches.append(
                                                {
                                                    "table_name": table_name,
                                                    "field_name": field_name,
                                                    "category": category,
                                                    "keyword": keyword,
                                                    "content": (
                                                        value[:200] + "..."
                                                        if len(value) > 200
                                                        else value
                                                    ),
                                                    "row_index": i,
                                                },
                                            )

                except Exception as e:
                    logger.warning(
                        f"Ошибка обработки записи {i} в таблице {table_name}: {e}",
                    )
                    continue

            if jtbd_matches:
                results["found_references"][table_name] = {
                    "total_records": len(table),
                    "jtbd_matches": jtbd_matches[:10],  # Первые 10 совпадений
                    "categories": list(
                        set(match["category"] for match in jtbd_matches),
                    ),
                }
                print(f"   ✅ Найдено {len(jtbd_matches)} JTBD совпадений")

        # Анализируем регистры на предмет JTBD данных
        for table_name in register_tables[:3]:  # Ограничиваем для тестирования
            print(f"\n📊 Анализ регистра: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 10 записей
            sample_size = min(10, len(table))
            register_matches = []

            for i in range(sample_size):
                try:
                    row = table[i]
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                        # Ищем JTBD ключевые слова в регистрах
                        for field_name, value in row_dict.items():
                            if isinstance(value, str):
                                for category, keywords in jtbd_keywords.items():
                                    for keyword in keywords:
                                        if keyword.lower() in value.lower():
                                            register_matches.append(
                                                {
                                                    "table_name": table_name,
                                                    "field_name": field_name,
                                                    "category": category,
                                                    "keyword": keyword,
                                                    "content": (
                                                        value[:200] + "..."
                                                        if len(value) > 200
                                                        else value
                                                    ),
                                                    "row_index": i,
                                                },
                                            )

                except Exception as e:
                    logger.warning(
                        f"Ошибка обработки записи {i} в таблице {table_name}: {e}",
                    )
                    continue

            if register_matches:
                results["found_registers"][table_name] = {
                    "total_records": len(table),
                    "jtbd_matches": register_matches[:5],  # Первые 5 совпадений
                    "categories": list(
                        set(match["category"] for match in register_matches),
                    ),
                }
                print(f"   ✅ Найдено {len(register_matches)} JTBD совпадений")

        # Создаем сводку JTBD сценариев
        all_categories = set()
        for ref_data in results["found_references"].values():
            all_categories.update(ref_data.get("categories", []))
        for reg_data in results["found_registers"].values():
            all_categories.update(reg_data.get("categories", []))

        results["jtbd_scenarios"] = {
            "found_categories": list(all_categories),
            "total_references": len(results["found_references"]),
            "total_registers": len(results["found_registers"]),
            "coverage_analysis": {
                "цвета": "найдено" if "цвета" in all_categories else "не найдено",
                "букеты": "найдено" if "букеты" in all_categories else "не найдено",
                "склады": "найдено" if "склады" in all_categories else "не найдено",
                "подразделения": (
                    "найдено" if "подразделения" in all_categories else "не найдено"
                ),
                "поставщики": (
                    "найдено" if "поставщики" in all_categories else "не найдено"
                ),
            },
        }

        return results


def search_all_missing_documents() -> dict[str, Any]:
    """
    Функция-обертка для обратной совместимости
    """
    extractor = AllMissingDocumentsExtractor()
    return extractor.run()
