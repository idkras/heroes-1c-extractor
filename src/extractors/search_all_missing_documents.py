#!/usr/bin/env python3

import json
import logging
from datetime import datetime
from typing import Any

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_utils import is_blob_field, safe_get_blob_content

logger = logging.getLogger(__name__)


def search_all_missing_documents() -> dict[str, Any] | None:
    """
    Поиск всех недостающих документов для JTBD сценариев
    ЦЕЛЬ: Найти справочники, регистры, документы с цветами и типами букетов
    """
    print("🔍 ПОИСК ВСЕХ НЕДОСТАЮЩИХ ДОКУМЕНТОВ")
    print("🎯 ЦЕЛЬ: JTBD сценарии - цвета, типы букетов, склады, подразделения")
    print("=" * 60)

    try:
        with open("raw/1Cv8.1CD", "rb") as f:
            db = DatabaseReader(f)

            print("✅ База данных открыта успешно!")

            results: dict[str, Any] = {
                "references": {},
                "accumulation_registers": {},
                "document_journals": {},
                "keyword_search": {},
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "source_file": "raw/1Cv8.1CD",
                    "total_tables": len(db.tables),
                },
            }

            print("\n📊 Всего таблиц в базе: {len(db.tables):,}")

            # 1. ПОИСК СПРАВОЧНИКОВ
            print("\n🔍 ЭТАП 1: Поиск справочников")
            print("-" * 60)

            reference_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith("_Reference"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        reference_tables[table_name] = len(table)

            print("📊 Найдено таблиц справочников: {len(reference_tables)}")

            # Анализируем все справочники
            sorted_references = sorted(
                reference_tables.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for i, (table_name, record_count) in enumerate(sorted_references):
                print("\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 3 записи
                        sample_records = []
                        blob_samples = []

                        for j in range(min(3, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()

                                    # Ищем BLOB поля
                                    for field_name, field_value in record_data.items():
                                        if is_blob_field(field_value):
                                            content = safe_get_blob_content(field_value)
                                            if content and len(content) > 10:
                                                blob_samples.append(
                                                    {
                                                        "field": field_name,
                                                        "content": content[:200],
                                                    },
                                                )

                                    # Сохраняем образец записи
                                    sample_records.append(
                                        {
                                            "record_index": j,
                                            "data": {
                                                k: v
                                                for k, v in record_data.items()
                                                if not is_blob_field(v)
                                            },
                                        },
                                    )

                            except Exception as e:
                                logger.warning(f"Ошибка при обработке BLOB: {e}")
                                continue

                        # Показываем образцы BLOB содержимого
                        if blob_samples:
                            print("    🔍 BLOB поля ({len(blob_samples)}):")
                            for sample in blob_samples[:2]:
                                print(
                                    f"        📋 {sample['field']}: {sample['content']}...",
                                )

                        # Сохраняем информацию о справочнике
                        ref_info = {
                            "table_name": table_name,
                            "record_count": record_count,
                            "sample_records": sample_records,
                            "blob_samples": blob_samples[:5],
                        }
                        results["references"][table_name] = ref_info

                except Exception:
                    print("    ⚠️ Ошибка анализа справочника: {e}")
                    continue

            # 2. ПОИСК РЕГИСТРОВ НАКОПЛЕНИЯ
            print("\n🔍 ЭТАП 2: Поиск регистров накопления")
            print("-" * 60)

            accumulation_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith("_AccumRGT"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        accumulation_tables[table_name] = len(table)

            print("📊 Найдено таблиц регистров накопления: {len(accumulation_tables)}")

            # Анализируем все регистры накопления
            sorted_accumulation = sorted(
                accumulation_tables.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for i, (table_name, record_count) in enumerate(sorted_accumulation):
                print("\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 2 записи
                        sample_records = []

                        for j in range(min(2, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()

                                    # Сохраняем образец записи
                                    sample_records.append(
                                        {
                                            "record_index": j,
                                            "data": {
                                                k: v
                                                for k, v in record_data.items()
                                                if not is_blob_field(v)
                                            },
                                        },
                                    )

                            except Exception as e:
                                logger.warning(f"Ошибка при обработке BLOB: {e}")
                                continue

                        # Сохраняем информацию о регистре
                        acc_info = {
                            "table_name": table_name,
                            "record_count": record_count,
                            "sample_records": sample_records,
                        }
                        results["accumulation_registers"][table_name] = acc_info

                except Exception:
                    print("    ⚠️ Ошибка анализа регистра: {e}")
                    continue

            # 3. ПОИСК ДОКУМЕНТОВ ПО КЛЮЧЕВЫМ СЛОВАМ JTBD
            print("\n🔍 ЭТАП 3: Поиск документов по ключевым словам JTBD")
            print("-" * 60)

            # Ключевые слова для JTBD сценариев
            jtbd_keywords = {
                "цвет": [
                    "цвет",
                    "розовый",
                    "голубой",
                    "красный",
                    "белый",
                    "желтый",
                    "синий",
                ],
                "букет": [
                    "букет",
                    "флористический",
                    "композиция",
                    "моно",
                    "яндекс букет",
                ],
                "склад": ["склад", "братиславский", "045", "подразделение", "магазин"],
                "канал": [
                    "яндекс маркет",
                    "яндекс директ",
                    "яндекс-еда",
                    "интернет магазин",
                ],
                "качество": [
                    "качество",
                    "брак",
                    "дефект",
                    "некондиция",
                    "стандарт",
                    "премиум",
                ],
            }

            # Поиск по всем таблицам документов
            document_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith("_DOCUMENT"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables[table_name] = len(table)

            print("📊 Анализируем {len(document_tables)} таблиц документов...")

            keyword_results: dict[str, list[dict[str, Any]]] = {
                keyword: [] for keyword in jtbd_keywords
            }

            # Анализируем топ-50 таблиц документов
            sorted_documents = sorted(
                document_tables.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for i, (table_name, record_count) in enumerate(sorted_documents[:50]):
                if i % 10 == 0:
                    print(
                        f"    📊 Обработано таблиц: {i}/{min(50, len(sorted_documents))}",
                    )

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 3 записи
                        found_keywords = set()

                        for j in range(min(3, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()

                                    # Ищем ключевые слова в BLOB полях
                                    for field_name, field_value in record_data.items():
                                        if is_blob_field(field_value):
                                            content = safe_get_blob_content(field_value)
                                            if content and len(content) > 10:
                                                # Ищем ключевые слова
                                                for (
                                                    keyword,
                                                    variations,
                                                ) in jtbd_keywords.items():
                                                    for variation in variations:
                                                        if (
                                                            variation.lower()
                                                            in content.lower()
                                                        ):
                                                            found_keywords.add(keyword)
                                                            keyword_results[
                                                                keyword
                                                            ].append(
                                                                {
                                                                    "table_name": table_name,
                                                                    "record_count": record_count,
                                                                    "field_name": field_name,
                                                                    "content_sample": content[
                                                                        :200
                                                                    ],
                                                                },
                                                            )

                                    # Ищем в обычных полях
                                    for field_name, field_value in record_data.items():
                                        if not is_blob_field(field_value):
                                            field_str = str(field_value).lower()
                                            for (
                                                keyword,
                                                variations,
                                            ) in jtbd_keywords.items():
                                                for variation in variations:
                                                    if variation.lower() in field_str:
                                                        found_keywords.add(keyword)
                                                        keyword_results[keyword].append(
                                                            {
                                                                "table_name": table_name,
                                                                "record_count": record_count,
                                                                "field_name": field_name,
                                                                "content_sample": str(
                                                                    field_value,
                                                                ),
                                                            },
                                                        )

                            except Exception as e:
                                logger.warning(f"Ошибка при обработке BLOB: {e}")
                                continue

                        # Показываем найденные ключевые слова
                        if found_keywords:
                            print("    🎯 {table_name}: {', '.join(found_keywords)}")

                except Exception as e:
                    logger.warning(f"Ошибка при обработке таблицы: {e}")
                    continue

            # Показываем результаты поиска по ключевым словам
            print("\n📊 РЕЗУЛЬТАТЫ ПОИСКА ПО КЛЮЧЕВЫМ СЛОВАМ:")
            print("-" * 60)

            for keyword, matches in keyword_results.items():
                if matches:
                    print("\n🎯 {keyword.upper()}: найдено {len(matches)} совпадений")
                    for match in matches[:3]:  # Показываем первые 3
                        print(
                            f"    📋 {match['table_name']} ({match['record_count']:,} записей)",
                        )
                        print("        📋 Поле: {match['field_name']}")
                        print("        📋 Образец: {match['content_sample']}...")
                else:
                    print("\n❌ {keyword.upper()}: не найдено")

            # Сохраняем результаты поиска по ключевым словам
            results["keyword_search"] = keyword_results

            # Сохраняем все результаты
            with open(
                "all_missing_documents_search.json",
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(results, file, ensure_ascii=False, indent=2, default=str)

            print("\n✅ Результаты сохранены в all_missing_documents_search.json")

            # Итоговая статистика
            print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
            print("    📋 Справочники: {len(results['references'])} типов")
            print(
                f"    📋 Регистры накопления: {len(results['accumulation_registers'])} типов",
            )
            print(
                f"    🔍 Ключевые слова найдены: {sum(1 for v in keyword_results.values() if v)} из {len(jtbd_keywords)}",
            )

            return results

    except Exception:
        print("❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    search_all_missing_documents()
