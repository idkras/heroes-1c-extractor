#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Добавляем путь к патчам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Применяем патч для onec_dtools
from patches.onec_dtools.onec_dtools_patch import apply_patch

apply_patch()

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_utils import safe_get_blob_content


def search_document_names_in_blob() -> Optional[Dict[str, Any]]:
    """
    Поиск названий документов в BLOB полях
    ЦЕЛЬ: Найти реальные названия документов для понимания их назначения
    """
    print("🔍 ПОИСК НАЗВАНИЙ ДОКУМЕНТОВ В BLOB ПОЛЯХ")
    print("🎯 ЦЕЛЬ: Определить назначение каждого типа документа")
    print("=" * 60)

    try:
        with open("data/raw/1Cv8.1CD", "rb") as f:
            db = DatabaseReader(f)

            print("✅ База данных открыта успешно!")

            results: Dict[str, Any] = {
                "document_names": {},
                "blob_content_samples": {},
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "source_file": "data/raw/1Cv8.1CD",
                    "total_tables": len(db.tables),
                },
            }

            print(f"\n📊 Всего таблиц в базе: {len(db.tables):,}")

            # Поиск таблиц документов
            document_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith("_DOCUMENT"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables[table_name] = len(table)

            print(f"📊 Найдено таблиц документов: {len(document_tables)}")

            # Ключевые слова для поиска в BLOB полях
            keywords = {
                "перемещение": [
                    "перемещение",
                    "перемещ",
                    "склад отгрузки",
                    "склад получатель",
                ],
                "реализация": ["реализация", "реализ", "продажа", "счет-фактура"],
                "перекомплектация": ["перекомплектация", "комплектация", "комплект"],
                "поступление": ["поступление", "поступл", "приход", "накладная"],
                "качество": ["качество", "брак", "дефект", "некондиция", "стандарт"],
                "поставка": ["поставка", "поставщ", "договор поставки"],
                "списание": ["списание", "списан", "расход", "брак"],
                "инвентаризация": ["инвентаризация", "пересчет", "остатки"],
                "возврат": ["возврат", "рекламация", "возвращ"],
                "корректировка": ["корректировка", "исправление", "коррект"],
            }

            # Анализируем топ-30 таблиц документов
            sorted_documents = sorted(
                document_tables.items(), key=lambda x: x[1], reverse=True
            )

            print("\n🔍 Анализируем топ-30 таблиц документов...")

            for i, (table_name, record_count) in enumerate(sorted_documents[:30]):
                print(f"\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 5 записей для поиска названий
                        found_names = set()
                        blob_samples = []

                        for j in range(min(5, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()

                                    # Ищем BLOB поля
                                    for field_name, field_value in record_data.items():
                                        if str(field_value).startswith(
                                            "<onec_dtools.database_reader.Blob"
                                        ):
                                            content = safe_get_blob_content(field_value)
                                            if content and len(content) > 10:
                                                # Ищем ключевые слова
                                                for (
                                                    keyword,
                                                    variations,
                                                ) in keywords.items():
                                                    for variation in variations:
                                                        if (
                                                            variation.lower()
                                                            in content.lower()
                                                        ):
                                                            found_names.add(
                                                                f"{keyword}: {variation}"
                                                            )

                                                # Сохраняем образец BLOB содержимого
                                                blob_samples.append(
                                                    {
                                                        "field": field_name,
                                                        "content": content[:200],
                                                    }
                                                )

                                    # Ищем в обычных полях
                                    for field_name, field_value in record_data.items():
                                        if not str(field_value).startswith(
                                            "<onec_dtools.database_reader.Blob"
                                        ):
                                            field_str = str(field_value).lower()
                                            for keyword, variations in keywords.items():
                                                for variation in variations:
                                                    if variation.lower() in field_str:
                                                        found_names.add(
                                                            f"{keyword}: {variation}"
                                                        )

                            except Exception as e:
                                logger.warning(f"Ошибка при обработке BLOB: {e}")
                                continue

                        # Показываем найденные названия
                        if found_names:
                            print("    🎯 Найдены ключевые слова:")
                            for name in sorted(found_names):
                                print(f"        ✅ {name}")

                        # Показываем образцы BLOB содержимого
                        if blob_samples:
                            print("    🔍 Образцы BLOB содержимого:")
                            for sample in blob_samples[:3]:
                                print(
                                    f"        📋 {sample['field']}: {sample['content']}..."
                                )

                        # Сохраняем информацию о таблице
                        table_info = {
                            "table_name": table_name,
                            "record_count": record_count,
                            "found_keywords": list(found_names),
                            "blob_samples": blob_samples[:5],
                        }
                        results["document_names"][table_name] = table_info

                        # Если нашли ключевые слова, показываем подробнее
                        if found_names:
                            print("    📊 Статус: ✅ НАЙДЕНЫ КЛЮЧЕВЫЕ СЛОВА")
                        else:
                            print("    📊 Статус: ❌ Ключевые слова не найдены")

                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа таблицы: {e}")
                    continue

            # Поиск по конкретным ключевым словам
            print("\n🔍 ДЕТАЛЬНЫЙ ПОИСК ПО КЛЮЧЕВЫМ СЛОВАМ")
            print("-" * 60)

            keyword_results = {}

            for keyword, variations in keywords.items():
                print(f"\n🔍 Поиск: {keyword}")
                print(f"    Вариации: {', '.join(variations)}")

                matching_tables = []

                for table_name, table_info in results["document_names"].items():
                    if table_info["found_keywords"]:
                        for found_keyword in table_info["found_keywords"]:
                            if keyword in found_keyword:
                                matching_tables.append(
                                    {
                                        "table_name": table_name,
                                        "record_count": table_info["record_count"],
                                        "found_keywords": table_info["found_keywords"],
                                    }
                                )
                                break

                if matching_tables:
                    print(f"    ✅ Найдено таблиц: {len(matching_tables)}")
                    for match in matching_tables:
                        print(
                            f"        📋 {match['table_name']} ({match['record_count']:,} записей)"
                        )
                        print(f"            🎯 {', '.join(match['found_keywords'])}")
                    keyword_results[keyword] = matching_tables
                else:
                    print("    ❌ Таблицы не найдены")
                    keyword_results[keyword] = []

            # Сохраняем результаты поиска по ключевым словам
            results["keyword_search_results"] = keyword_results

            # Сохраняем все результаты
            with open("document_names_blob_search.json", "w", encoding="utf-8") as file:
                json.dump(results, file, ensure_ascii=False, indent=2, default=str)

            print("\n✅ Результаты сохранены в document_names_blob_search.json")

            # Итоговая статистика
            print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
            print(f"    📋 Проанализировано таблиц: {len(results['document_names'])}")
            print(
                f"    🔍 Найдено таблиц с ключевыми словами: {sum(1 for info in results['document_names'].values() if info['found_keywords'])}"
            )

            # Показываем найденные ключевые слова
            all_found_keywords = set()
            for table_info in results["document_names"].values():
                all_found_keywords.update(table_info["found_keywords"])

            if all_found_keywords:
                print("    🎯 Найденные ключевые слова:")
                for keyword in sorted(all_found_keywords):
                    print(f"        ✅ {keyword}")
            else:
                print("    ❌ Ключевые слова не найдены")

            return results

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    search_document_names_in_blob()
