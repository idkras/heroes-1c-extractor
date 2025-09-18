#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Извлечение только бизнес-данных из 1С без технических полей
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Set

# Добавляем путь к onec_dtools
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "tools", "onec_dtools")
)

from onec_dtools.database_reader import DatabaseReader

# Бизнес-поля для извлечения
BUSINESS_FIELDS: Set[str] = {
    "_NUMBER",  # номер документа
    "_DATE_TIME",  # дата и время
    "_FLD4239",  # сумма (финансовые данные)
    "_FLD4238",  # количество
    "_FLD4240",  # единица измерения
    "_FLD4225",  # флаг операции 1
    "_FLD4226",  # флаг операции 2
    "_FLD4227",  # флаг операции 3
    "_POSTED",  # проведен ли документ
    "_MARKED",  # помечен ли на удаление
}

# Технические поля для исключения
TECHNICAL_FIELDS: Set[str] = {
    "_FLD10651",
    "_FLD10654",
    "_FLD12950",
    "_FLD12955",
    "_FLD13609",
    "_FLD14340",
    "_FLD8015",
    "_FLD8070",
    "_FLD8205",
    "_FLD9885",
    "_VERSION",
}

# Критические таблицы для извлечения
CRITICAL_TABLES: List[str] = [
    "_DOCUMENTJOURNAL5354",  # 4,458,509 записей
    "_DOCUMENTJOURNAL5287",  # 2,798,531 записей
    "_DOCUMENTJOURNAL5321",  # 973,975 записей
    "_DOCUMENT138",  # 861,178 записей
    "_DOCUMENT156",  # 571,213 записей
]

# Справочники для извлечения
REFERENCE_TABLES: List[str] = [
    "_REFERENCE10",  # Номенклатура
    "_REFERENCE10002",  # Склады
    "_REFERENCE10003",  # Подразделения
    "_REFERENCE10004",  # Контрагенты
    "_REFERENCE10005",  # Кассы
]


def filter_business_fields(record_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Фильтрует только бизнес-поля из записи"""
    filtered = {}

    for field, value in record_dict.items():
        # Извлекаем только бизнес-поля
        if field in BUSINESS_FIELDS:
            filtered[field] = value
        # Исключаем технические поля
        elif field in TECHNICAL_FIELDS:
            continue
        # Оставляем BLOB поля для анализа
        elif hasattr(value, "__class__") and "Blob" in str(type(value)):
            filtered[field] = value

    return filtered


def extract_blob_content(blob_obj: Any) -> Dict[str, Any]:
    """Извлекает содержимое BLOB поля"""
    blob_data: Dict[str, Any] = {
        "field_type": str(type(blob_obj)),
        "size": 0,
        "extraction_methods": [],
        "value": {"content": "", "type": "unknown", "length": 0},
    }

    try:
        # Метод 1: прямое значение
        if hasattr(blob_obj, "value"):
            blob_value = blob_obj.value
            if isinstance(blob_value, bytes):
                try:
                    content = blob_value.decode("utf-8")
                    blob_data["value"] = {
                        "content": content,
                        "type": "str",
                        "length": len(content),
                    }
                    blob_data["extraction_methods"].append("value")
                    blob_data["size"] = len(blob_value)
                except UnicodeDecodeError:
                    try:
                        content = blob_value.decode("cp1251")
                        blob_data["value"] = {
                            "content": content,
                            "type": "str_cp1251",
                            "length": len(content),
                        }
                        blob_data["extraction_methods"].append("value_cp1251")
                        blob_data["size"] = len(blob_value)
                    except UnicodeDecodeError:
                        blob_data["value"] = {
                            "content": blob_value.hex(),
                            "type": "hex",
                            "length": len(blob_value),
                        }
                        blob_data["extraction_methods"].append("value_hex")
                        blob_data["size"] = len(blob_value)
    except Exception as e:
        blob_data["error"] = f"Ошибка извлечения: {str(e)}"

    return blob_data


def extract_critical_tables(db: DatabaseReader) -> Dict[str, List[Dict]]:
    """Извлекает критические таблицы"""
    results = {}

    for table_name in CRITICAL_TABLES:
        if table_name not in db.tables:
            print(f"   ❌ Таблица {table_name} не найдена")
            continue

        print(f"   🔄 Извлечение {table_name}...")
        table = db.tables[table_name]

        # Получаем количество записей без вызова len()
        try:
            table_length = 0
            for _ in table:
                table_length += 1
            print(f"      📊 Всего записей: {table_length:,}")
        except Exception as e:
            print(f"      ⚠️ Не удалось определить размер таблицы: {e}")
            continue

        table_records = []
        successful_records = 0

        # Обрабатываем все записи
        for i, row in enumerate(table):
            try:
                # НЕ пропускаем пустые записи - обрабатываем все
                # if hasattr(row, 'is_empty') and row.is_empty:
                #     continue

                # Извлекаем данные
                row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                # Проверяем, есть ли данные в записи
                if not row_dict:
                    continue

                # Отладочная информация для первых записей
                if i < 3:
                    print(f"      🔍 Запись {i}: {list(row_dict.keys())[:5]}...")

                # Фильтруем бизнес-поля
                business_fields = filter_business_fields(row_dict)

                # Отладочная информация для первых записей
                if i < 3:
                    print(f"      🔍 Бизнес-поля: {list(business_fields.keys())}")

                # Пропускаем записи без бизнес-полей
                if not business_fields:
                    continue

                # Обрабатываем BLOB поля
                blobs = {}
                for field_name, value in row_dict.items():
                    if hasattr(value, "__class__") and "Blob" in str(type(value)):
                        blobs[field_name] = extract_blob_content(value)

                # Создаем запись
                record = {
                    "id": f"{table_name}_{i+1}",
                    "table_name": table_name,
                    "row_index": i + 1,
                    "fields": business_fields,
                    "blobs": blobs,
                    "extraction_stats": {
                        "total_blobs": len(blobs),
                        "successful": len(
                            [b for b in blobs.values() if b.get("extraction_methods")]
                        ),
                        "failed": len([b for b in blobs.values() if b.get("error")]),
                    },
                }

                table_records.append(record)
                successful_records += 1

                # Показываем прогресс
                if i > 0 and i % 10000 == 0:
                    print(f"      📊 Обработано {i:,} записей")

            except Exception as e:
                print(f"      ⚠️ Ошибка в записи {i}: {str(e)}")
                continue

        results[table_name] = table_records
        print(f"      ✅ Извлечено {successful_records:,} записей из {table_name}")

    return results


def extract_reference_tables(db: DatabaseReader) -> Dict[str, List[Dict]]:
    """Извлекает справочники"""
    results = {}

    for table_name in REFERENCE_TABLES:
        if table_name not in db.tables:
            print(f"   ❌ Справочник {table_name} не найден")
            continue

        print(f"   🔄 Извлечение справочника {table_name}...")
        table = db.tables[table_name]
        # Получаем количество записей без вызова len()
        try:
            table_length = 0
            for _ in table:
                table_length += 1
            print(f"      📊 Всего записей: {table_length:,}")
        except Exception as e:
            print(f"      ⚠️ Не удалось определить размер таблицы: {e}")
            continue

        table_records = []
        successful_records = 0

        # Обрабатываем все записи
        for i, row in enumerate(table):
            try:
                # НЕ пропускаем пустые записи - обрабатываем все
                # if hasattr(row, 'is_empty') and row.is_empty:
                #     continue

                # Извлекаем данные
                row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                # Проверяем, есть ли данные в записи
                if not row_dict:
                    continue

                # Фильтруем бизнес-поля
                business_fields = filter_business_fields(row_dict)

                # Пропускаем записи без бизнес-полей
                if not business_fields:
                    continue

                # Создаем запись справочника
                record = {
                    "id": f"{table_name}_{i+1}",
                    "table_name": table_name,
                    "row_index": i + 1,
                    "fields": business_fields,
                    "type": "reference",
                }

                table_records.append(record)
                successful_records += 1

                # Показываем прогресс
                if i > 0 and i % 1000 == 0:
                    print(f"      📊 Обработано {i:,} записей")

            except Exception as e:
                print(f"      ⚠️ Ошибка в записи {i}: {str(e)}")
                continue

        results[table_name] = table_records
        print(f"      ✅ Извлечено {successful_records:,} записей из {table_name}")

    return results


def main() -> None:
    """Основная функция извлечения бизнес-данных"""
    print("🔍 Извлечение бизнес-данных из 1С")
    print("=" * 50)

    try:
        # Открываем базу данных
        print("📂 Открытие базы данных...")
        db_file = open("data/raw/1Cv8.1CD", "rb")
        db = DatabaseReader(db_file)

        print("✅ База данных открыта успешно!")
        print(f"📊 Найдено {len(db.tables)} таблиц")

        # Инициализируем результаты
        all_results: Dict[str, Any] = {
            "critical_tables": {},
            "reference_tables": {},
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_tables": 0,
                "total_records": 0,
                "business_fields": list(BUSINESS_FIELDS),
                "technical_fields": list(TECHNICAL_FIELDS),
                "source_file": "data/raw/1Cv8.1CD",
            },
        }

        # Извлекаем критические таблицы
        print("\n🎯 Извлечение критических таблиц...")
        critical_results = extract_critical_tables(db)
        all_results["critical_tables"] = critical_results

        # Извлекаем справочники
        print("\n📚 Извлечение справочников...")
        reference_results = extract_reference_tables(db)
        all_results["reference_tables"] = reference_results

        # Подсчитываем статистику
        total_records = sum(len(records) for records in critical_results.values())
        total_records += sum(len(records) for records in reference_results.values())

        all_results["metadata"]["total_tables"] = len(critical_results) + len(
            reference_results
        )
        all_results["metadata"]["total_records"] = total_records

        # Сохраняем результаты
        print("\n💾 Сохранение результатов...")

        # JSON файл
        json_file = "business_data_extraction.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ Результаты сохранены в {json_file}")
        print(
            f"📊 Извлечено {total_records:,} записей из {all_results['metadata']['total_tables']} таблиц"
        )

        # Выводим статистику
        print("\n📈 СТАТИСТИКА ИЗВЛЕЧЕНИЯ:")
        for table_name, records in critical_results.items():
            print(f"   📄 {table_name}: {len(records):,} записей")

        for table_name, records in reference_results.items():
            print(f"   📚 {table_name}: {len(records):,} записей")

        print("\n✅ Извлечение бизнес-данных завершено!")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # Закрываем файл
        if "db_file" in locals():
            db_file.close()


if __name__ == "__main__":
    main()
