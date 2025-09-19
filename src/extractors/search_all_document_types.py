#!/usr/bin/env python3

import json
from datetime import datetime
from typing import Any

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_utils import is_blob_field


def search_all_document_types() -> dict[str, Any] | None:
    """
    Поиск всех типов документов согласно уточненному плану
    ЦЕЛЬ: Отследить весь путь от сырья до цветочков в магазине
    """
    print("🔍 ПОИСК ВСЕХ ТИПОВ ДОКУМЕНТОВ")
    print("🎯 ЦЕЛЬ: Полный путь цветов от сырья до магазина")
    print("=" * 60)

    try:
        with open("raw/1Cv8.1CD", "rb") as f:
            db = DatabaseReader(f)

            print("✅ База данных открыта успешно!")

            results: dict[str, Any] = {
                "document_types": {},
                "references": {},
                "accumulation_registers": {},
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "source_file": "raw/1Cv8.1CD",
                    "total_tables": len(db.tables),
                },
            }

            print("\n📊 Всего таблиц в базе: {len(db.tables):,}")

            # 1. ПОИСК ВСЕХ ТИПОВ ДОКУМЕНТОВ
            print("\n🔍 ЭТАП 1: Поиск всех типов документов")
            print("-" * 60)

            document_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith("_DOCUMENT"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables[table_name] = len(table)

            print("📊 Найдено таблиц документов: {len(document_tables)}")

            # Сортируем по количеству записей
            sorted_documents = sorted(
                document_tables.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            # Анализируем топ-20 таблиц документов
            for i, (table_name, record_count) in enumerate(sorted_documents[:20]):
                print("\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первую запись для понимания структуры
                        first_record = table[0]
                        if not first_record.is_empty:
                            record_data = first_record.as_dict()

                            # Показываем основные поля
                            print("    📄 Основные поля:")
                            for field_name, field_value in list(record_data.items())[
                                :10
                            ]:
                                if not is_blob_field(field_value):
                                    print("        📋 {field_name}: {field_value}")

                            # Ищем BLOB поля
                            blob_fields = []
                            for field_name, field_value in record_data.items():
                                if is_blob_field(field_value):
                                    blob_fields.append(field_name)

                            if blob_fields:
                                print(
                                    f"    🔍 BLOB поля ({len(blob_fields)}): {blob_fields[:5]}",
                                )

                                # Анализируем содержимое первого BLOB поля
                                if blob_fields:
                                    try:
                                        blob_value = record_data[blob_fields[0]]
                                        if hasattr(blob_value, "value"):
                                            content = blob_value.value
                                            if content and len(str(content)) > 0:
                                                print(
                                                    f"        📋 {blob_fields[0]}: {str(content)[:100]}...",
                                                )
                                    except Exception:
                                        print("        ⚠️ Ошибка чтения BLOB: {e}")

                            # Сохраняем информацию о таблице
                            table_info = {
                                "table_name": table_name,
                                "record_count": record_count,
                                "fields": list(record_data.keys()),
                                "blob_fields": blob_fields,
                                "sample_data": {
                                    k: v
                                    for k, v in list(record_data.items())[:5]
                                    if not str(v).startswith(
                                        "<onec_dtools.database_reader.Blob",
                                    )
                                },
                            }
                            results["document_types"][table_name] = table_info

                except Exception:
                    print("    ⚠️ Ошибка анализа таблицы: {e}")
                    continue

            # 2. ПОИСК СПРАВОЧНИКОВ
            print("\n🔍 ЭТАП 2: Поиск справочников")
            print("-" * 60)

            reference_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith("_Reference"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        reference_tables[table_name] = len(table)

            print("📊 Найдено таблиц справочников: {len(reference_tables)}")

            # Анализируем топ-10 справочников
            sorted_references = sorted(
                reference_tables.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for i, (table_name, record_count) in enumerate(sorted_references[:10]):
                print("\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первую запись
                        first_record = table[0]
                        if not first_record.is_empty:
                            record_data = first_record.as_dict()

                            # Показываем основные поля
                            print("    📄 Основные поля:")
                            for field_name, field_value in list(record_data.items())[
                                :8
                            ]:
                                if not is_blob_field(field_value):
                                    print("        📋 {field_name}: {field_value}")

                            # Ищем BLOB поля
                            blob_fields = []
                            for field_name, field_value in record_data.items():
                                if is_blob_field(field_value):
                                    blob_fields.append(field_name)

                            if blob_fields:
                                print(
                                    f"    🔍 BLOB поля ({len(blob_fields)}): {blob_fields[:3]}",
                                )

                            # Сохраняем информацию о справочнике
                            ref_info = {
                                "table_name": table_name,
                                "record_count": record_count,
                                "fields": list(record_data.keys()),
                                "blob_fields": blob_fields,
                                "sample_data": {
                                    k: v
                                    for k, v in list(record_data.items())[:5]
                                    if not str(v).startswith(
                                        "<onec_dtools.database_reader.Blob",
                                    )
                                },
                            }
                            results["references"][table_name] = ref_info

                except Exception:
                    print("    ⚠️ Ошибка анализа справочника: {e}")
                    continue

            # 3. ПОИСК РЕГИСТРОВ НАКОПЛЕНИЯ
            print("\n🔍 ЭТАП 3: Поиск регистров накопления")
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
                        # Анализируем первую запись
                        first_record = table[0]
                        if not first_record.is_empty:
                            record_data = first_record.as_dict()

                            # Показываем основные поля
                            print("    📄 Основные поля:")
                            for field_name, field_value in list(record_data.items())[
                                :8
                            ]:
                                if not is_blob_field(field_value):
                                    print("        📋 {field_name}: {field_value}")

                            # Сохраняем информацию о регистре
                            acc_info = {
                                "table_name": table_name,
                                "record_count": record_count,
                                "fields": list(record_data.keys()),
                                "sample_data": {
                                    k: v
                                    for k, v in list(record_data.items())[:5]
                                    if not str(v).startswith(
                                        "<onec_dtools.database_reader.Blob",
                                    )
                                },
                            }
                            results["accumulation_registers"][table_name] = acc_info

                except Exception:
                    print("    ⚠️ Ошибка анализа регистра: {e}")
                    continue

            # 4. ПОИСК ДОКУМЕНТОВ ПО КЛЮЧЕВЫМ СЛОВАМ
            print("\n🔍 ЭТАП 4: Поиск документов по ключевым словам")
            print("-" * 60)

            # Ключевые слова для поиска
            keywords = {
                "перемещение": "Перемещение товаров и услуг",
                "реализация": "Реализация товаров и услуг",
                "перекомплектация": "Перекомплектация номенклатуры",
                "поступление": "Поступление товаров и услуг",
                "комплектация": "Комплектация товаров",
                "качество": "Документы качества товаров",
                "брак": "Документы брака и дефектов",
                "поставка": "Документы поставок",
                "списание": "Документы списания",
                "инвентаризация": "Документы инвентаризации",
                "возврат": "Документы возвратов",
                "корректировка": "Документы корректировки",
            }

            found_keywords = {}

            for keyword, description in keywords.items():
                print("\n🔍 Поиск: {keyword} - {description}")

                matching_tables = []
                for table_name in document_tables:
                    if keyword.lower() in table_name.lower():
                        matching_tables.append(
                            (table_name, document_tables[table_name]),
                        )

                if matching_tables:
                    print("    ✅ Найдено таблиц: {len(matching_tables)}")
                    for table_name, record_count in matching_tables:
                        print("        📋 {table_name} ({record_count:,} записей)")
                    found_keywords[keyword] = matching_tables
                else:
                    print("    ❌ Таблицы не найдены")
                    found_keywords[keyword] = []

            # Сохраняем результаты поиска по ключевым словам
            results["keyword_search"] = found_keywords

            # Сохраняем все результаты
            with open(
                "all_document_types_analysis.json",
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(results, file, ensure_ascii=False, indent=2, default=str)

            print("\n✅ Результаты сохранены в all_document_types_analysis.json")

            # Итоговая статистика
            print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
            print("    📋 Документы: {len(results['document_types'])} типов")
            print("    📋 Справочники: {len(results['references'])} типов")
            print(
                f"    📋 Регистры накопления: {len(results['accumulation_registers'])} типов",
            )
            print(
                f"    🔍 Ключевые слова найдены: {sum(1 for v in found_keywords.values() if v)} из {len(keywords)}",
            )

            return results

    except Exception:
        print("❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    search_all_document_types()
