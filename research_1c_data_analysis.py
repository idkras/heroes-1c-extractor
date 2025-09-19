#!/usr/bin/env python3
"""
Research-First анализ реальных данных из 1С базы.

JTBD:
Как исследователь данных, я хочу проанализировать реальную структуру 1С базы,
чтобы понять паттерны извлечения данных и создать план рефакторинга на основе фактов.
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


def analyze_1c_database_structure():
    """
    JTBD:
    Как анализатор структуры базы данных, я хочу проанализировать реальную 1С базу,
    чтобы понять структуру таблиц, типы данных и паттерны извлечения.
    """
    print("🔍 RESEARCH-FIRST АНАЛИЗ 1С БАЗЫ ДАННЫХ")
    print("=" * 60)

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

            # Анализируем структуру базы
            analysis_results = {
                "database_info": {
                    "file_path": str(cdb_file_path),
                    "file_size_gb": cdb_file_path.stat().st_size / (1024 * 1024 * 1024),
                    "total_tables": len(db.tables),
                    "analysis_date": datetime.now().isoformat(),
                },
                "table_categories": {},
                "document_tables": {},
                "reference_tables": {},
                "register_tables": {},
                "sample_data": {},
                "extraction_patterns": {},
                "hypotheses": [],
            }

            # 1. АНАЛИЗ КАТЕГОРИЙ ТАБЛИЦ
            print("\n📊 АНАЛИЗ КАТЕГОРИЙ ТАБЛИЦ:")
            all_tables = list(db.tables.keys())

            document_tables = [t for t in all_tables if t.startswith("_DOCUMENT")]
            reference_tables = [t for t in all_tables if t.startswith("_Reference")]
            register_tables = [
                t
                for t in all_tables
                if t.startswith("_AccumRGT") or t.startswith("_InfoRGT")
            ]
            other_tables = [
                t
                for t in all_tables
                if not any(
                    t.startswith(prefix)
                    for prefix in ["_DOCUMENT", "_Reference", "_AccumRGT", "_InfoRGT"]
                )
            ]

            analysis_results["table_categories"] = {
                "document_tables": len(document_tables),
                "reference_tables": len(reference_tables),
                "register_tables": len(register_tables),
                "other_tables": len(other_tables),
                "total_tables": len(all_tables),
            }

            print(f"   📄 Документы: {len(document_tables)}")
            print(f"   📚 Справочники: {len(reference_tables)}")
            print(f"   📊 Регистры: {len(register_tables)}")
            print(f"   🔧 Другие: {len(other_tables)}")

            # 2. АНАЛИЗ ТАБЛИЦ ДОКУМЕНТОВ
            print("\n📄 АНАЛИЗ ТАБЛИЦ ДОКУМЕНТОВ:")
            document_analysis = {}

            # Берем первые 10 таблиц документов для анализа
            sample_document_tables = document_tables[:10]

            for table_name in sample_document_tables:
                try:
                    table = db.tables[table_name]
                    table_size = len(table)

                    print(f"   🎯 {table_name}: {table_size:,} записей")

                    # Анализируем структуру таблицы
                    if table_size > 0:
                        # Пробуем прочитать первые несколько записей
                        sample_records = []
                        for i in range(min(5, table_size)):
                            try:
                                row = table[i]
                                if not hasattr(row, "is_empty") or not row.is_empty:
                                    row_list = (
                                        row.as_list(True)
                                        if hasattr(row, "as_list")
                                        else []
                                    )
                                    if row_list:
                                        # Анализируем поля
                                        fields_analysis = {}
                                        for j, value in enumerate(row_list):
                                            field_name = getattr(
                                                value, "name", f"field_{j}"
                                            )
                                            field_type = type(value).__name__

                                            fields_analysis[field_name] = {
                                                "type": field_type,
                                                "is_blob": hasattr(value, "value")
                                                and "Blob" in str(type(value)),
                                                "is_numeric": isinstance(
                                                    value, (int, float)
                                                ),
                                                "is_string": isinstance(value, str),
                                                "is_date": isinstance(value, datetime),
                                                "sample_value": (
                                                    str(value)[:100] if value else None
                                                ),
                                            }

                                        sample_records.append(
                                            {"row_index": i, "fields": fields_analysis}
                                        )
                            except Exception as e:
                                print(f"      ⚠️ Ошибка при чтении записи {i}: {e}")
                                continue

                        document_analysis[table_name] = {
                            "size": table_size,
                            "sample_records": sample_records,
                            "field_types": list(
                                set(
                                    field["type"]
                                    for record in sample_records
                                    for field in record["fields"].values()
                                )
                            ),
                            "blob_fields": [
                                name
                                for record in sample_records
                                for name, field in record["fields"].items()
                                if field["is_blob"]
                            ],
                            "numeric_fields": [
                                name
                                for record in sample_records
                                for name, field in record["fields"].items()
                                if field["is_numeric"]
                            ],
                            "string_fields": [
                                name
                                for record in sample_records
                                for name, field in record["fields"].items()
                                if field["is_string"]
                            ],
                            "date_fields": [
                                name
                                for record in sample_records
                                for name, field in record["fields"].items()
                                if field["is_date"]
                            ],
                        }

                        print(
                            f"      📊 Поля: {len(document_analysis[table_name]['field_types'])} типов"
                        )
                        print(
                            f"      📦 BLOB поля: {len(document_analysis[table_name]['blob_fields'])}"
                        )
                        print(
                            f"      🔢 Числовые поля: {len(document_analysis[table_name]['numeric_fields'])}"
                        )
                        print(
                            f"      📝 Строковые поля: {len(document_analysis[table_name]['string_fields'])}"
                        )
                        print(
                            f"      📅 Дата поля: {len(document_analysis[table_name]['date_fields'])}"
                        )

                        # Показываем примеры полей
                        if sample_records:
                            first_record = sample_records[0]
                            print(f"      🔍 Пример полей:")
                            for field_name, field_info in list(
                                first_record["fields"].items()
                            )[:5]:
                                print(
                                    f"         {field_name}: {field_info['type']} = {field_info['sample_value']}"
                                )

                except Exception as e:
                    print(f"   ❌ Ошибка при анализе таблицы {table_name}: {e}")
                    continue

            analysis_results["document_tables"] = document_analysis

            # 3. АНАЛИЗ СПРАВОЧНИКОВ
            print("\n📚 АНАЛИЗ СПРАВОЧНИКОВ:")
            reference_analysis = {}

            sample_reference_tables = reference_tables[:5]

            for table_name in sample_reference_tables:
                try:
                    table = db.tables[table_name]
                    table_size = len(table)

                    print(f"   🎯 {table_name}: {table_size:,} записей")

                    if table_size > 0:
                        # Анализируем первые записи
                        sample_records = []
                        for i in range(min(3, table_size)):
                            try:
                                row = table[i]
                                if not hasattr(row, "is_empty") or not row.is_empty:
                                    row_list = (
                                        row.as_list(True)
                                        if hasattr(row, "as_list")
                                        else []
                                    )
                                    if row_list:
                                        fields_analysis = {}
                                        for j, value in enumerate(row_list):
                                            field_name = getattr(
                                                value, "name", f"field_{j}"
                                            )
                                            field_type = type(value).__name__

                                            fields_analysis[field_name] = {
                                                "type": field_type,
                                                "sample_value": (
                                                    str(value)[:100] if value else None
                                                ),
                                            }

                                        sample_records.append(
                                            {"row_index": i, "fields": fields_analysis}
                                        )
                            except Exception as e:
                                continue

                        reference_analysis[table_name] = {
                            "size": table_size,
                            "sample_records": sample_records,
                        }

                        print(
                            f"      📊 Поля: {len(sample_records[0]['fields']) if sample_records else 0}"
                        )

                except Exception as e:
                    print(f"   ❌ Ошибка при анализе справочника {table_name}: {e}")
                    continue

            analysis_results["reference_tables"] = reference_analysis

            # 4. ВЫЯВЛЕНИЕ ПАТТЕРНОВ ИЗВЛЕЧЕНИЯ
            print("\n🔍 ВЫЯВЛЕНИЕ ПАТТЕРНОВ ИЗВЛЕЧЕНИЯ:")

            extraction_patterns = {
                "common_field_types": {},
                "blob_processing_patterns": [],
                "data_quality_issues": [],
                "performance_considerations": [],
            }

            # Анализируем общие типы полей
            all_field_types = []
            all_blob_fields = []

            for table_name, table_data in document_analysis.items():
                for record in table_data.get("sample_records", []):
                    for field_name, field_info in record["fields"].items():
                        all_field_types.append(field_info["type"])
                        if field_info["is_blob"]:
                            all_blob_fields.append(field_name)

            # Подсчитываем частоту типов полей
            from collections import Counter

            field_type_counts = Counter(all_field_types)

            extraction_patterns["common_field_types"] = dict(field_type_counts)
            extraction_patterns["blob_processing_patterns"] = list(set(all_blob_fields))

            print(f"   📊 Общие типы полей: {dict(field_type_counts)}")
            print(f"   📦 BLOB поля: {list(set(all_blob_fields))}")

            analysis_results["extraction_patterns"] = extraction_patterns

            # 5. ФОРМИРОВАНИЕ ГИПОТЕЗ
            print("\n💡 ФОРМИРОВАНИЕ ГИПОТЕЗ:")

            hypotheses = []

            # Гипотеза 1: BLOB поля требуют специальной обработки
            if all_blob_fields:
                hypotheses.append(
                    {
                        "hypothesis": "BLOB поля требуют специальной обработки с декодированием",
                        "evidence": f"Найдено {len(set(all_blob_fields))} уникальных BLOB полей",
                        "implication": "Нужен специализированный BlobProcessor",
                    }
                )

            # Гипотеза 2: Разные типы таблиц требуют разных подходов
            if len(document_tables) > 0 and len(reference_tables) > 0:
                hypotheses.append(
                    {
                        "hypothesis": "Документы, справочники и регистры требуют разных экстракторов",
                        "evidence": f"Найдено {len(document_tables)} документов, {len(reference_tables)} справочников",
                        "implication": "Нужны отдельные DocumentExtractor, ReferenceExtractor, RegisterExtractor",
                    }
                )

            # Гипотеза 3: Производительность зависит от размера таблиц
            large_tables = [
                name for name, data in document_analysis.items() if data["size"] > 1000
            ]
            if large_tables:
                hypotheses.append(
                    {
                        "hypothesis": "Большие таблицы требуют оптимизации производительности",
                        "evidence": f"Найдено {len(large_tables)} таблиц с >1000 записей",
                        "implication": "Нужна пакетная обработка и прогресс-трекинг",
                    }
                )

            for i, hypothesis in enumerate(hypotheses, 1):
                print(f"   💡 Гипотеза {i}: {hypothesis['hypothesis']}")
                print(f"      📊 Доказательства: {hypothesis['evidence']}")
                print(f"      🎯 Импликация: {hypothesis['implication']}")

            analysis_results["hypotheses"] = hypotheses

            # Сохраняем результаты анализа
            output_file = "research_1c_analysis_results.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    analysis_results, f, ensure_ascii=False, indent=2, default=str
                )

            print(f"\n💾 Результаты анализа сохранены в: {output_file}")

            # 6. РЕКОМЕНДАЦИИ ДЛЯ РЕФАКТОРИНГА
            print("\n🎯 РЕКОМЕНДАЦИИ ДЛЯ РЕФАКТОРИНГА:")

            recommendations = []

            if all_blob_fields:
                recommendations.append(
                    "1. Создать BlobProcessor для обработки BLOB полей"
                )

            if len(document_tables) > 0:
                recommendations.append(
                    "2. Создать DocumentExtractor для извлечения документов"
                )

            if len(reference_tables) > 0:
                recommendations.append(
                    "3. Создать ReferenceExtractor для извлечения справочников"
                )

            if len(register_tables) > 0:
                recommendations.append(
                    "4. Создать RegisterExtractor для извлечения регистров"
                )

            if large_tables:
                recommendations.append("5. Добавить ProgressTracker для больших таблиц")

            recommendations.append("6. Создать ErrorHandler для обработки ошибок")
            recommendations.append(
                "7. Создать DataConverter для конвертации в Parquet/DuckDB"
            )

            for recommendation in recommendations:
                print(f"   ✅ {recommendation}")

            analysis_results["recommendations"] = recommendations

            # Обновляем результаты
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    analysis_results, f, ensure_ascii=False, indent=2, default=str
                )

            print(f"\n🎉 RESEARCH-FIRST АНАЛИЗ ЗАВЕРШЕН!")
            print(
                f"📊 Проанализировано таблиц: {len(document_analysis) + len(reference_analysis)}"
            )
            print(f"💡 Сформировано гипотез: {len(hypotheses)}")
            print(f"🎯 Рекомендаций: {len(recommendations)}")

            return analysis_results

    except Exception as e:
        print(f"❌ Ошибка при анализе базы данных: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = analyze_1c_database_structure()
    if results:
        print("\n✅ Анализ завершен успешно!")
    else:
        print("\n❌ Анализ завершен с ошибками!")
