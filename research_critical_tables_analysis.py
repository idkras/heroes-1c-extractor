#!/usr/bin/env python3
"""
Research-First анализ критических таблиц из extract_all_available_data.py

JTBD:
Как исследователь данных, я хочу проанализировать критические таблицы,
чтобы понять их структуру, содержимое и паттерны для рефакторинга.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

# Добавляем путь к src для импорта
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Применяем патч для поддержки новых типов полей 1С
try:
    import os
    import sys

    patch_path = os.path.join(
        os.path.dirname(__file__),
        "tests",
        "integration",
    )
    sys.path.insert(0, patch_path)
    from simple_patch import apply_simple_patch

    apply_simple_patch()
    print("✅ Патч для новых типов полей применен")
except Exception as e:
    print(f"⚠️ Не удалось применить патч: {e}")

from onec_dtools import DatabaseReader


def analyze_critical_tables():
    """
    JTBD:
    Как анализатор критических таблиц, я хочу проанализировать структуру и содержимое
    критических таблиц из extract_all_available_data.py для понимания паттернов данных.
    """
    print("🔍 RESEARCH-FIRST АНАЛИЗ КРИТИЧЕСКИХ ТАБЛИЦ")
    print("=" * 60)

    # Критические таблицы из extract_all_available_data.py
    critical_tables = [
        "_DOCUMENTJOURNAL5354",  # 4,458,509 записей - КРИТИЧЕСКАЯ
        "_DOCUMENTJOURNAL5287",  # 2,798,531 записей - КРИТИЧЕСКАЯ
        "_DOCUMENTJOURNAL5321",  # 973,975 записей - КРИТИЧЕСКАЯ
        "_DOCUMENT138",  # 861,178 записей - КРИТИЧЕСКАЯ
        "_DOCUMENT156",  # 571,213 записей - КРИТИЧЕСКАЯ
    ]

    # Дополнительные таблицы документов
    document_tables = [
        "_DOCUMENT163",  # Большая таблица с реальными данными
        "_DOCUMENT184",  # Таблица с BLOB данными
        "_DOCUMENT154",  # Таблица с суммами
        "_DOCUMENT137",  # Таблица с суммами
        "_DOCUMENT12259",  # Таблица документов
    ]

    # Подключение к базе
    cdb_file_path = Path(__file__).parent / "data" / "raw" / "1Cv8.1CD"

    if not cdb_file_path.exists():
        print(f"❌ Файл 1С базы данных не найден: {cdb_file_path}")
        return

    print(f"📁 Путь к файлу: {cdb_file_path}")
    print(f"📏 Размер файла: {cdb_file_path.stat().st_size / (1024*1024*1024):.2f} GB")

    try:
        with open(cdb_file_path, "rb") as f:
            db = DatabaseReader(f)
            print("✅ База данных открыта успешно!")

            # Анализ критических таблиц
            analysis_results = {
                "database_info": {
                    "file_path": str(cdb_file_path),
                    "file_size_gb": cdb_file_path.stat().st_size / (1024 * 1024 * 1024),
                    "analysis_date": datetime.now().isoformat(),
                },
                "critical_tables_analysis": {},
                "document_tables_analysis": {},
                "field_patterns": {},
                "blob_patterns": {},
                "data_quality_issues": [],
                "refactoring_recommendations": [],
            }

            # 1. АНАЛИЗ КРИТИЧЕСКИХ ТАБЛИЦ
            print("\n📊 АНАЛИЗ КРИТИЧЕСКИХ ТАБЛИЦ:")

            for table_name in critical_tables:
                if table_name in db.tables:
                    print(f"\n🎯 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    table_size = len(table)

                    print(f"   📈 Размер таблицы: {table_size:,} записей")

                    # Анализируем первые 5 записей
                    sample_records = []
                    field_analysis = {}
                    blob_fields = []
                    numeric_fields = []
                    string_fields = []
                    date_fields = []

                    for i in range(min(5, table_size)):
                        try:
                            row = table[i]
                            if not hasattr(row, "is_empty") or not row.is_empty:
                                row_list = (
                                    row.as_list(True) if hasattr(row, "as_list") else []
                                )
                                if row_list:
                                    record_fields = {}
                                    for j, value in enumerate(row_list):
                                        field_name = getattr(
                                            value, "name", f"field_{j}"
                                        )
                                        field_type = type(value).__name__

                                        # Анализируем тип поля
                                        is_blob = hasattr(
                                            value, "value"
                                        ) and "Blob" in str(type(value))
                                        is_numeric = isinstance(value, (int, float))
                                        is_string = isinstance(value, str)
                                        is_date = isinstance(value, datetime)

                                        field_info = {
                                            "type": field_type,
                                            "is_blob": is_blob,
                                            "is_numeric": is_numeric,
                                            "is_string": is_string,
                                            "is_date": is_date,
                                            "sample_value": (
                                                str(value)[:100] if value else None
                                            ),
                                        }

                                        record_fields[field_name] = field_info

                                        # Собираем статистику по типам полей
                                        if is_blob:
                                            blob_fields.append(field_name)
                                        if is_numeric:
                                            numeric_fields.append(field_name)
                                        if is_string:
                                            string_fields.append(field_name)
                                        if is_date:
                                            date_fields.append(field_name)

                                    sample_records.append(
                                        {"row_index": i, "fields": record_fields}
                                    )

                                    # Обновляем общий анализ полей
                                    for field_name, field_info in record_fields.items():
                                        if field_name not in field_analysis:
                                            field_analysis[field_name] = {
                                                "type": field_info["type"],
                                                "is_blob": field_info["is_blob"],
                                                "is_numeric": field_info["is_numeric"],
                                                "is_string": field_info["is_string"],
                                                "is_date": field_info["is_date"],
                                                "sample_values": [],
                                            }
                                        field_analysis[field_name][
                                            "sample_values"
                                        ].append(field_info["sample_value"])

                        except Exception as e:
                            print(f"      ⚠️ Ошибка при чтении записи {i}: {e}")
                            continue

                    # Сохраняем анализ таблицы
                    analysis_results["critical_tables_analysis"][table_name] = {
                        "size": table_size,
                        "sample_records": sample_records,
                        "field_analysis": field_analysis,
                        "field_counts": {
                            "total_fields": len(field_analysis),
                            "blob_fields": len(set(blob_fields)),
                            "numeric_fields": len(set(numeric_fields)),
                            "string_fields": len(set(string_fields)),
                            "date_fields": len(set(date_fields)),
                        },
                        "field_lists": {
                            "blob_fields": list(set(blob_fields)),
                            "numeric_fields": list(set(numeric_fields)),
                            "string_fields": list(set(string_fields)),
                            "date_fields": list(set(date_fields)),
                        },
                    }

                    print(f"   📊 Поля: {len(field_analysis)} уникальных")
                    print(f"   📦 BLOB поля: {len(set(blob_fields))}")
                    print(f"   🔢 Числовые поля: {len(set(numeric_fields))}")
                    print(f"   📝 Строковые поля: {len(set(string_fields))}")
                    print(f"   📅 Дата поля: {len(set(date_fields))}")

                    # Показываем примеры полей
                    if sample_records:
                        first_record = sample_records[0]
                        print(f"   🔍 Примеры полей:")
                        for field_name, field_info in list(
                            first_record["fields"].items()
                        )[:5]:
                            print(
                                f"      {field_name}: {field_info['type']} = {field_info['sample_value']}"
                            )

                else:
                    print(f"   ❌ Таблица {table_name} не найдена в базе")

            # 2. АНАЛИЗ ТАБЛИЦ ДОКУМЕНТОВ
            print("\n📄 АНАЛИЗ ТАБЛИЦ ДОКУМЕНТОВ:")

            for table_name in document_tables:
                if table_name in db.tables:
                    print(f"\n🎯 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    table_size = len(table)

                    print(f"   📈 Размер таблицы: {table_size:,} записей")

                    # Анализируем первые 3 записи
                    sample_records = []
                    field_analysis = {}

                    for i in range(min(3, table_size)):
                        try:
                            row = table[i]
                            if not hasattr(row, "is_empty") or not row.is_empty:
                                row_list = (
                                    row.as_list(True) if hasattr(row, "as_list") else []
                                )
                                if row_list:
                                    record_fields = {}
                                    for j, value in enumerate(row_list):
                                        field_name = getattr(
                                            value, "name", f"field_{j}"
                                        )
                                        field_type = type(value).__name__

                                        field_info = {
                                            "type": field_type,
                                            "sample_value": (
                                                str(value)[:100] if value else None
                                            ),
                                        }

                                        record_fields[field_name] = field_info

                                    sample_records.append(
                                        {"row_index": i, "fields": record_fields}
                                    )

                                    # Обновляем общий анализ полей
                                    for field_name, field_info in record_fields.items():
                                        if field_name not in field_analysis:
                                            field_analysis[field_name] = {
                                                "type": field_info["type"],
                                                "sample_values": [],
                                            }
                                        field_analysis[field_name][
                                            "sample_values"
                                        ].append(field_info["sample_value"])

                        except Exception as e:
                            continue

                    # Сохраняем анализ таблицы
                    analysis_results["document_tables_analysis"][table_name] = {
                        "size": table_size,
                        "sample_records": sample_records,
                        "field_analysis": field_analysis,
                        "field_count": len(field_analysis),
                    }

                    print(f"   📊 Поля: {len(field_analysis)} уникальных")

                    # Показываем примеры полей
                    if sample_records:
                        first_record = sample_records[0]
                        print(f"   🔍 Примеры полей:")
                        for field_name, field_info in list(
                            first_record["fields"].items()
                        )[:5]:
                            print(
                                f"      {field_name}: {field_info['type']} = {field_info['sample_value']}"
                            )

                else:
                    print(f"   ❌ Таблица {table_name} не найдена в базе")

            # 3. ВЫЯВЛЕНИЕ ПАТТЕРНОВ
            print("\n🔍 ВЫЯВЛЕНИЕ ПАТТЕРНОВ:")

            # Анализируем общие паттерны полей
            all_field_types = []
            all_blob_fields = []
            all_numeric_fields = []
            all_string_fields = []

            for table_name, table_data in analysis_results[
                "critical_tables_analysis"
            ].items():
                for field_name, field_info in table_data["field_analysis"].items():
                    all_field_types.append(field_info["type"])
                    if field_info["is_blob"]:
                        all_blob_fields.append(field_name)
                    if field_info["is_numeric"]:
                        all_numeric_fields.append(field_name)
                    if field_info["is_string"]:
                        all_string_fields.append(field_name)

            # Подсчитываем частоту типов полей
            from collections import Counter

            field_type_counts = Counter(all_field_types)

            analysis_results["field_patterns"] = {
                "common_field_types": dict(field_type_counts),
                "blob_fields": list(set(all_blob_fields)),
                "numeric_fields": list(set(all_numeric_fields)),
                "string_fields": list(set(all_string_fields)),
            }

            print(f"   📊 Общие типы полей: {dict(field_type_counts)}")
            print(f"   📦 BLOB поля: {list(set(all_blob_fields))}")
            print(f"   🔢 Числовые поля: {list(set(all_numeric_fields))}")
            print(f"   📝 Строковые поля: {list(set(all_string_fields))}")

            # 4. РЕКОМЕНДАЦИИ ДЛЯ РЕФАКТОРИНГА
            print("\n🎯 РЕКОМЕНДАЦИИ ДЛЯ РЕФАКТОРИНГА:")

            recommendations = []

            if all_blob_fields:
                recommendations.append(
                    "1. Создать BlobProcessor для обработки BLOB полей"
                )

            if len(analysis_results["critical_tables_analysis"]) > 0:
                recommendations.append(
                    "2. Создать CriticalTableExtractor для критических таблиц"
                )

            if len(analysis_results["document_tables_analysis"]) > 0:
                recommendations.append(
                    "3. Создать DocumentTableExtractor для таблиц документов"
                )

            if all_numeric_fields:
                recommendations.append(
                    "4. Создать NumericFieldAnalyzer для числовых полей"
                )

            if all_string_fields:
                recommendations.append(
                    "5. Создать StringFieldAnalyzer для строковых полей"
                )

            recommendations.append(
                "6. Создать TableStructureAnalyzer для анализа структуры таблиц"
            )
            recommendations.append(
                "7. Создать DataQualityAnalyzer для проверки качества данных"
            )

            for recommendation in recommendations:
                print(f"   ✅ {recommendation}")

            analysis_results["refactoring_recommendations"] = recommendations

            # Сохраняем результаты анализа
            output_file = "research_critical_tables_analysis.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    analysis_results, f, ensure_ascii=False, indent=2, default=str
                )

            print(f"\n💾 Результаты анализа сохранены в: {output_file}")

            # 5. ИТОГОВАЯ СТАТИСТИКА
            print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
            print(
                f"   📄 Критических таблиц проанализировано: {len(analysis_results['critical_tables_analysis'])}"
            )
            print(
                f"   📚 Таблиц документов проанализировано: {len(analysis_results['document_tables_analysis'])}"
            )
            print(f"   🔧 Рекомендаций: {len(recommendations)}")

            return analysis_results

    except Exception as e:
        print(f"❌ Ошибка при анализе критических таблиц: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = analyze_critical_tables()
    if results:
        print("\n✅ Анализ критических таблиц завершен успешно!")
    else:
        print("\n❌ Анализ завершен с ошибками!")
