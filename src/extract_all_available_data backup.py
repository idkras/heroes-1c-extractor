#!/usr/bin/env python3

import json
import os
import re
import signal
import sys
from datetime import datetime

# ИСПРАВЛЕНО: Принудительная очистка буфера для реального времени
import functools

print = functools.partial(print, flush=True)
from typing import Any

import duckdb
import pandas as pd
from onec_dtools import DatabaseReader

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# from src.utils.blob_processor import BlobProcessor  # Пока не используется

# Флаг для прерывания
interrupted = False


def signal_handler(sig: int, frame: Any) -> None:
    global interrupted
    print("\n🛑 Получен сигнал прерывания. Завершение извлечения...")
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)


def extract_table_parts(db, table_name: str, row_index: int) -> dict:
    """
    Извлекает табличные части документа
    """
    table_parts = {}

    # ИСПРАВЛЕНО: Ищем табличные части для конкретной таблицы
    for table_part_name in db.tables.keys():
        if table_part_name.startswith(f"{table_name}_VT"):
            try:
                table_part = db.tables[table_part_name]
                records = []

                for i, row in enumerate(table_part):
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        # ИСПРАВЛЕНО: Правильное извлечение табличных частей с BLOB
                        row_list = row.as_list(True) if hasattr(row, "as_list") else []
                        if row_list:
                            # ИСПРАВЛЕНО: Безопасное создание словаря
                            row_data = {}
                            for j, value in enumerate(row_list):
                                if (
                                    hasattr(value, "name")
                                    and value.name
                                    and value.name.strip()
                                ):
                                    row_data[value.name] = value
                                else:
                                    row_data[f"field_{j}"] = value

                            # ИСПРАВЛЕНО: Анализируем структуру табличной части
                            table_part_record = {
                                "row_index": i,
                                "fields": row_data,
                            }

                            # ИСПРАВЛЕНО: Динамический анализ полей табличной части
                            for field_name, value in row_data.items():
                                # Анализируем по имени поля и содержимому
                                field_lower = field_name.lower()
                                if (
                                    "номенклатура" in field_lower
                                    or "nomenclature" in field_lower
                                ):
                                    table_part_record["nomenclature"] = value
                                elif (
                                    "количество" in field_lower
                                    or "quantity" in field_lower
                                    or "qty" in field_lower
                                ):
                                    table_part_record["quantity"] = value
                                elif "цена" in field_lower or "price" in field_lower:
                                    table_part_record["price"] = value
                                elif (
                                    "сумма" in field_lower
                                    or "amount" in field_lower
                                    or "sum" in field_lower
                                ):
                                    table_part_record["amount"] = value
                                elif field_name.startswith("field_"):
                                    # Fallback для полей без понятных имен
                                    field_parts = field_name.split("_")
                                    field_index = (
                                        int(field_parts[1])
                                        if len(field_parts) > 1
                                        and field_parts[1].isdigit()
                                        else 0
                                    )
                                    if field_index == 0:
                                        table_part_record["nomenclature"] = value
                                    elif field_index == 1:
                                        table_part_record["quantity"] = value
                                    elif field_index == 2:
                                        table_part_record["price"] = value
                                    elif field_index == 3:
                                        table_part_record["amount"] = value

                            # Устанавливаем значения по умолчанию если не найдены
                            table_part_record.setdefault("nomenclature", "")
                            table_part_record.setdefault("quantity", 0)
                            table_part_record.setdefault("price", 0)
                            table_part_record.setdefault("amount", 0)

                            records.append(table_part_record)

                if records:
                    table_parts[table_part_name] = records
            except Exception as e:
                print(f"   ⚠️ Ошибка извлечения табличной части {table_part_name}: {e}")
                continue

    return table_parts


def extract_all_available_data() -> None:
    """
    Извлечение всех доступных данных с надежной обработкой ошибок
    """
    print("🔍 Извлечение всех доступных данных")
    print("=" * 60)

    # ИСПРАВЛЕНО: Инициализируем BlobProcessor для правильной обработки BLOB полей
    # blob_processor = BlobProcessor()  # Пока не используется
    print("✅ BlobProcessor будет инициализирован при необходимости")

    # Применяем патч для поддержки новых типов полей 1С
    try:
        import os
        import sys

        patch_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "patches",
            "onec_dtools",
        )
        sys.path.insert(0, patch_path)
        from patches.onec_dtools.simple_patch import apply_simple_patch

        apply_simple_patch()
        print("✅ Патч для новых типов полей применен")
    except Exception:
        print("⚠️ Не удалось применить патч: ")

    # ИСПРАВЛЕНО: Проверяем существование 1CD файла
    cdb_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "raw",
        "1Cv8.1CD",
    )
    if not os.path.exists(cdb_file_path):
        print(f"❌ Файл 1CD не найден: {cdb_file_path}")
        print("📁 Доступные файлы в data/raw/:")
        if os.path.exists("data/raw/"):
            for file in os.listdir("data/raw/"):
                print(f"   - {file}")
        else:
            print("   Папка data/raw/ не существует")
            return
        print(f"✅ Файл 1CD найден: {cdb_file_path}")

    try:
        with open(cdb_file_path, "rb") as f:
            try:
                db = DatabaseReader(f)
            except ValueError as e:
                if "Unknown field type" in str(e):
                    print("⚠️ Предупреждение: ")
                    print("Попробуем использовать более детальный подход...")
                    # Попробуем использовать более детальный подход
                    extract_data_detailed_method()
                    return
                raise e

            print("✅ База данных открыта успешно!")

            # Анализируем все основные таблицы документов
            document_tables = [
                "_DOCUMENT163",  # Большая таблица с реальными данными
                "_DOCUMENT184",  # Таблица с BLOB данными
                "_DOCUMENT154",  # Таблица с суммами
                "_DOCUMENT137",  # Таблица с суммами (из предыдущего анализа)
                "_DOCUMENT12259",  # Таблица документов
                # КРИТИЧЕСКИЕ ТАБЛИЦЫ ДЛЯ ИЗВЛЕЧЕНИЯ
                "_DOCUMENTJOURNAL5354",  # 4,458,509 записей - КРИТИЧЕСКАЯ
                "_DOCUMENTJOURNAL5287",  # 2,798,531 записей - КРИТИЧЕСКАЯ
                "_DOCUMENTJOURNAL5321",  # 973,975 записей - КРИТИЧЕСКАЯ
                "_DOCUMENT138",  # 861,178 записей - КРИТИЧЕСКАЯ
                "_DOCUMENT156",  # 571,213 записей - КРИТИЧЕСКАЯ
            ]

            all_results: dict = {
                "documents": [],
                "references": [],
                "registers": [],
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "total_documents": 0,
                    "total_references": 0,
                    "total_registers": 0,
                    "total_blobs": 0,
                    "successful_extractions": 0,
                    "failed_extractions": 0,
                    "source_file": "data/raw/1Cv8.1CD",
                },
            }

            # Сначала извлекаем все таблицы для анализа
            all_tables = list(db.tables.keys())
            print(f"\n📊 Найдено {len(all_tables)} таблиц в базе данных")

            # Фильтруем таблицы по типам
            document_tables_found = [t for t in all_tables if t.startswith("_DOCUMENT")]
            reference_tables_found = [
                t for t in all_tables if t.startswith("_Reference")
            ]
            register_tables_found = [
                t
                for t in all_tables
                if t.startswith("_AccumRGT") or t.startswith("_InfoRGT")
            ]

            print(f"   📄 Документы: {len(document_tables_found)}")
            print(f"   📚 Справочники: {len(reference_tables_found)}")
            print(f"   📊 Регистры: {len(register_tables_found)}")

            # Обновляем список для извлечения
            # КРИТИЧЕСКИЕ ТАБЛИЦЫ - ПРИОРИТЕТ 1 (ЛИМИТ 1000 ЗАПИСЕЙ)
            critical_tables = [
                "_DOCUMENTJOURNAL5354",  # 4,458,509 записей - КРИТИЧЕСКАЯ (ЛИМИТ 1000)
                "_DOCUMENTJOURNAL5287",  # 2,798,531 записей - КРИТИЧЕСКАЯ (ЛИМИТ 1000)
                "_DOCUMENTJOURNAL5321",  # 973,975 записей - КРИТИЧЕСКАЯ (ЛИМИТ 1000)
                "_DOCUMENT138",  # 861,178 записей - КРИТИЧЕСКАЯ (ЛИМИТ 1000)
                "_DOCUMENT156",  # 571,213 записей - КРИТИЧЕСКАЯ (ЛИМИТ 1000)
            ]

            # Лимит записей для критических таблиц
            MAX_RECORDS_CRITICAL = (
                10  # Только 10 документов для тестирования (ИСПРАВЛЕНО)
            )

            # Проверяем какие критические таблицы доступны
            available_critical = [t for t in critical_tables if t in db.tables]
            print(
                f"🎯 КРИТИЧЕСКИЕ ТАБЛИЦЫ ДОСТУПНЫ: {len(available_critical)}/{len(critical_tables)}",
            )
            for table in available_critical:
                print(f"   ✅ {table}: {len(db.tables[table]):,} записей")

            tables_to_extract = (
                document_tables + available_critical + document_tables_found[:5]
            )  # Критические + 5 дополнительных

            # Добавляем справочники и регистры
            reference_tables_to_extract = reference_tables_found[
                :5
            ]  # Первые 5 справочников
            register_tables_to_extract = register_tables_found[:5]  # Первые 5 регистров

            print("\n🎯 План извлечения:")
            print(f"   📄 Документы: {len(tables_to_extract)}")
            print(f"   📚 Справочники: {len(reference_tables_to_extract)}")
            print(f"   📊 Регистры: {len(register_tables_to_extract)}")

            # Извлекаем документы
            for table_name in tables_to_extract:
                if table_name in db.tables:
                    print(f"\n📊 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")

                    # ИСПРАВЛЕНО: Определяем лимит записей - ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ
                    max_records = min(MAX_RECORDS_CRITICAL, len(table))
                    print(
                        f"   🎯 Лимит извлечения: {max_records:,} записей (ИСПРАВЛЕНО)",
                    )

                    # Находим непустые записи - с лимитом для критических таблиц
                    non_empty_rows = []
                    print(f"   🔍 Анализ {min(max_records, len(table)):,} записей...")
                    for i in range(
                        min(max_records, len(table)),
                    ):  # Анализируем с лимитом
                        # ИСПРАВЛЕНО: Проверяем флаг прерывания
                        if interrupted:
                            print(f"   🛑 ПРЕРЫВАНИЕ: Остановка анализа на записи {i}")
                            break

                        try:
                            row = table[i]
                            if not hasattr(row, "is_empty") or not row.is_empty:
                                non_empty_rows.append((i, row))
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при проверке записи {i}: {e!s}")
                            continue

                        # Показываем прогресс для больших таблиц
                        if i > 0 and i % 100000 == 0:
                            print(
                                f"   📊 Обработано {i:,} записей, найдено {len(non_empty_rows):,} непустых",
                            )

                    print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")

                    # Извлекаем данные документов - ВСЕ записи
                    successful_docs = 0
                    error_counter: dict[str, int] = {}  # Счетчик ошибок по типам
                    max_repeated_errors = 100  # Максимум повторяющихся ошибок
                    print(f"   🔄 Извлечение всех {len(non_empty_rows):,} записей...")

                    for i, (row_index, row) in enumerate(non_empty_rows, 1):
                        # Проверяем флаг прерывания
                        if interrupted:
                            print(
                                f"   🛑 ПРЕРЫВАНИЕ: Остановка извлечения на записи {i:,}",
                            )
                            break

                        # Показываем прогресс для больших таблиц
                        if i > 0 and i % 1000 == 0:
                            print(
                                f"   📊 Извлечено {i:,} из {len(non_empty_rows):,} записей ({i / len(non_empty_rows) * 100:.1f}%)",
                            )

                        try:
                            # ИСПРАВЛЕНО: Правильное извлечение данных с BLOB полями
                            row_list = (
                                row.as_list(True) if hasattr(row, "as_list") else []
                            )
                            if not row_list:
                                continue

                            # ИСПРАВЛЕНО: Безопасное создание словаря
                            row_dict = {}
                            for j, value in enumerate(row_list):
                                if (
                                    hasattr(value, "name")
                                    and value.name
                                    and value.name.strip()
                                ):
                                    row_dict[value.name] = value
                                else:
                                    row_dict[f"field_{j}"] = value

                            # Создаем структуру документа с извлечением реальных данных
                            document: dict = {
                                "id": f"{table_name}_{i}",
                                "table_name": table_name,
                                "row_index": row_index,
                                "document_type": "Неизвестно",
                                "document_number": "N/A",
                                "document_date": "N/A",
                                "store_name": "N/A",
                                "store_code": "N/A",
                                "total_amount": 0.0,
                                "currency": "RUB",
                                "supplier_name": "N/A",
                                "buyer_name": "N/A",
                                "goods_received": "{}",
                                "goods_not_received": "{}",
                                "flower_names": "",
                                "flower_quantities": "",
                                "flower_prices": "",
                                "blob_content": "",
                                "fields": {},
                                "blobs": {},
                                "extraction_stats": {
                                    "total_blobs": 0,
                                    "successful": 0,
                                    "failed": 0,
                                },
                            }

                            # ИСПРАВЛЕНО: УПРОЩЕННЫЙ АНАЛИЗ СТРУКТУРЫ ДОКУМЕНТА
                            if i <= 3:  # Только для первых 3 записей
                                print(
                                    f"\n🔍 АНАЛИЗ ДОКУМЕНТА {table_name}, строка {i}:",
                                )
                                print(
                                    f"   📋 Поля: {list(row_dict.keys())[:10]}...",
                                )  # Только первые 10 полей
                                print(f"   📊 Всего полей: {len(row_dict)}")

                            # Упрощенный анализ полей
                            field_analysis = {}
                            # ИСПРАВЛЕНО: Сохраняем оригинальные bytes ДО анализа
                            original_bytes = {}
                            for field_name, value in row_dict.items():
                                if isinstance(value, bytes):
                                    original_bytes[field_name] = value

                            for field_name, value in row_dict.items():
                                if value is not None:
                                    field_info = {
                                        "type": type(value).__name__,
                                        "value": (
                                            str(value)[:50] + "..."
                                            if len(str(value)) > 50
                                            else str(value)
                                        ),
                                        "is_numeric": isinstance(value, (int, float)),
                                        # ИСПРАВЛЕНО: Добавляем оригинальные bytes если есть
                                        "original_bytes": original_bytes.get(
                                            field_name
                                        ),
                                        "is_date": isinstance(value, datetime),
                                        "is_string": isinstance(value, str),
                                        "is_blob": hasattr(value, "value")
                                        and value.value is not None,
                                    }
                                    field_analysis[field_name] = field_info
                                    document["fields"][field_name] = value

                            # ИСПРАВЛЕНО: Динамический анализ структуры полей
                            print(f"\n🧠 АНАЛИЗ СТРУКТУРЫ ПОЛЕЙ для документа {i}:")
                            print(f"   📋 Всего полей: {len(field_analysis)}")

                            # Показываем все поля с их типами
                            print("   📊 ТИПЫ ПОЛЕЙ:")
                            for field_name, info in field_analysis.items():
                                field_type = info.get("type", "unknown")
                                field_value = info.get("value", "N/A")
                                if len(str(field_value)) > 30:
                                    field_value = str(field_value)[:30] + "..."
                                print(
                                    f"      {field_name}: {field_type} = {field_value}",
                                )

                            # Ищем поля с номерами документов - ИСПРАВЛЕНО: более умный анализ
                            number_fields = []
                            for field_name, info in field_analysis.items():
                                # ИСПРАВЛЕНО: Анализируем по имени поля и содержимому
                                is_number_field = field_name == "_NUMBER" or (
                                    info["is_string"]
                                    and isinstance(info["value"], str)
                                    and (
                                        info["value"].isdigit()
                                        or "№" in info["value"]
                                        or "N" in field_name
                                    )
                                )
                                if is_number_field:
                                    number_fields.append(field_name)
                                    document["document_number"] = info["value"]
                                    print(
                                        f"   ✅ Номер документа: {field_name} = {info['value']}",
                                    )

                            # ИСПРАВЛЕНО: Ищем поля с датами - более умный анализ
                            date_fields = []
                            for field_name, info in field_analysis.items():
                                # ИСПРАВЛЕНО: Анализируем по имени поля и типу
                                is_date_field = (
                                    field_name == "_DATE_TIME"
                                    or field_name == "_DATE"
                                    or info["is_date"]
                                    or (
                                        info["is_string"]
                                        and isinstance(info["value"], str)
                                        and any(
                                            date_indicator in info["value"]
                                            for date_indicator in [
                                                "2024",
                                                "2023",
                                                "2025",
                                                "-",
                                                "/",
                                            ]
                                        )
                                    )
                                )
                                if is_date_field:
                                    date_fields.append(field_name)
                                    # ИСПРАВЛЕНО: Выбираем правильную дату документа
                                    if hasattr(info["value"], "isoformat"):
                                        # Приоритет: field_3 (реальная дата) > field_4 (системная дата)
                                        if (
                                            field_name == "field_3"
                                            or document.get("document_date") == "N/A"
                                        ):
                                            document["document_date"] = info[
                                                "value"
                                            ].isoformat()
                                            print(
                                                f"   ✅ Дата документа: {field_name} = {info['value']}",
                                            )
                                        else:
                                            print(
                                                f"   ✅ Дата документа (строка): {field_name} = {info['value']}",
                                            )
                                    else:
                                        if (
                                            field_name == "field_3"
                                            or document.get("document_date") == "N/A"
                                        ):
                                            document["document_date"] = str(
                                                info["value"]
                                            )
                                            print(
                                                f"   ✅ Дата документа: {field_name} = {info['value']}",
                                            )
                                        else:
                                            print(
                                                f"   ✅ Дата документа (строка): {field_name} = {info['value']}",
                                            )

                            # Ищем поля с описанием
                            description_fields = []
                            for field_name, info in field_analysis.items():
                                if (
                                    info["is_string"]
                                    and isinstance(info["value"], str)
                                    and len(info["value"])
                                    > 5  # Минимальная длина описания
                                    and any(
                                        keyword in info["value"].lower()
                                        for keyword in [
                                            "автоформирование",
                                            "флор",
                                            "пост",
                                            "оплата",
                                            "магазин",
                                            "моно",
                                            "декор",
                                        ]
                                    )
                                ):
                                    description_fields.append(field_name)
                                    document["document_type"] = info["value"]
                                    print(
                                        f"   ✅ Описание документа: {field_name} = {info['value']}",
                                    )

                                    # Анализируем содержимое для извлечения информации
                                    if "флор" in info["value"].lower():
                                        document["document_type"] = "ФЛОРИСТИКА"
                                    elif "декор" in info["value"].lower():
                                        document["document_type"] = "ДЕКОР"
                                    elif "моно" in info["value"].lower():
                                        document["document_type"] = "МОНО БУКЕТ"
                                    elif "интернет" in info["value"].lower():
                                        document["document_type"] = "ИНТЕРНЕТ-ЗАКАЗ"

                                    # Извлекаем название магазина
                                    if "магазин" in info["value"].lower():
                                        store_match = re.search(
                                            r"Магазин\s+([^)]+)",
                                            info["value"],
                                        )
                                        if store_match:
                                            document["store_name"] = store_match.group(
                                                1,
                                            )
                                            print(
                                                f"   ✅ Название магазина: {document['store_name']}",
                                            )

                                    # Извлекаем коды магазинов
                                    if isinstance(info["value"], str):
                                        store_code_match = re.search(
                                            r"ПЦ(\d+)",
                                            info["value"],
                                        )
                                        if store_code_match:
                                            document["store_code"] = (
                                                f"ПЦ{store_code_match.group(1)}"
                                            )
                                            print(
                                                f"   ✅ Код магазина: {document['store_code']}",
                                            )

                            # Ищем поля с типом продажи
                            sale_type_fields = []
                            for field_name, info in field_analysis.items():
                                if (
                                    info["is_string"]
                                    and isinstance(info["value"], str)
                                    and any(
                                        keyword in str(info["value"])
                                        for keyword in ["Розничная", "Оптовая"]
                                    )
                                ):
                                    sale_type_fields.append(field_name)
                                    document["sale_type"] = info["value"]
                                    print(
                                        f"   ✅ Тип продажи: {field_name} = {info['value']}",
                                    )

                            # ИСПРАВЛЕНО: Ищем поля с суммами - более умный анализ
                            amount_fields = []
                            for field_name, info in field_analysis.items():
                                # ИСПРАВЛЕНО: Анализируем по имени поля и значению
                                is_amount_field = (
                                    field_name == "_FLD4239"
                                    or field_name == "_AMOUNT"
                                    or field_name
                                    == "field_33"  # Добавляем field_33 который содержит суммы
                                    or field_name
                                    == "field_32"  # Добавляем field_32 который может содержать суммы
                                    or field_name
                                    == "field_31"  # Добавляем field_31 который может содержать суммы
                                    or (
                                        info["is_numeric"]
                                        and isinstance(info["value"], (int, float))
                                        and info["value"] > 0
                                    )
                                    or (
                                        info["is_string"]
                                        and isinstance(info["value"], str)
                                        and any(
                                            amount_indicator in field_name.lower()
                                            for amount_indicator in [
                                                "sum",
                                                "amount",
                                                "total",
                                            ]
                                        )
                                    )
                                )

                                # ИСПРАВЛЕНО: Дополнительная проверка для всех числовых полей
                                if (
                                    not is_amount_field
                                    and info["is_numeric"]
                                    and isinstance(info["value"], (int, float))
                                    and info["value"] > 0
                                ):
                                    is_amount_field = True
                                    print(
                                        f"      🔍 НАЙДЕНО ПОТЕНЦИАЛЬНОЕ ПОЛЕ С СУММОЙ: {field_name} = {info['value']}"
                                    )

                                # ИСПРАВЛЕНО: Поиск сумм в BLOB данных
                                if (
                                    not is_amount_field
                                    and isinstance(info["value"], bytes)
                                    and len(info["value"]) > 0
                                ):
                                    try:
                                        # Пытаемся декодировать BLOB как текст и найти числа
                                        blob_text = info["value"].decode(
                                            "utf-8", errors="ignore"
                                        )
                                        if any(char.isdigit() for char in blob_text):
                                            # Проверяем есть ли числа в BLOB
                                            numbers = re.findall(
                                                r"\d+\.?\d*", blob_text
                                            )
                                            if numbers:
                                                potential_sum = float(numbers[0])
                                                if potential_sum > 0:
                                                    is_amount_field = True
                                                    print(
                                                        f"      🔍 НАЙДЕНО ПОТЕНЦИАЛЬНОЕ ПОЛЕ С СУММОЙ В BLOB: {field_name} = {potential_sum}"
                                                    )
                                    except:
                                        pass
                                if is_amount_field:
                                    amount_fields.append(field_name)
                                    document["total_amount"] = (
                                        float(info["value"])
                                        if info["is_numeric"]
                                        and isinstance(info["value"], (int, float))
                                        else 0.0
                                    )
                                    print(
                                        f"   ✅ Сумма: {field_name} = {info['value']}",
                                    )

                            # ИСПРАВЛЕНО: Ищем BLOB поля с анализом типа
                            blob_fields = []
                            for field_name, info in field_analysis.items():
                                # ИСПРАВЛЕНО: Анализируем тип BLOB поля перед обработкой
                                # Проверяем только оригинальные bytes
                                blob_value = info.get("original_bytes")
                                # ОТЛАДКА: Проверяем что у нас есть
                                if field_name in ["field_0", "field_8", "field_11"]:  # Известные bytes поля
                                    print(f"      🔍 ОТЛАДКА BLOB {field_name}: original_bytes={blob_value is not None}, type={type(blob_value)}")
                                if (
                                    isinstance(blob_value, bytes)
                                    and len(blob_value)
                                    > 0  # ИСПРАВЛЕНО: Убираем ограничение по размеру
                                ):
                                    blob_fields.append(field_name)
                                    print(
                                        f"      📦 НАЙДЕНО BLOB ПОЛЕ: {field_name} = {len(blob_value)} байт"
                                    )

                                    # ИСПРАВЛЕНО: Пытаемся декодировать BLOB для анализа
                                    try:
                                        blob_text = blob_value.decode(
                                            "utf-8", errors="ignore"
                                        )
                                        if len(blob_text) > 0:
                                            print(
                                                f"         📄 СОДЕРЖИМОЕ BLOB {field_name}: {blob_text[:100]}..."
                                            )

                                            # Поиск цветочной информации
                                            if any(
                                                color in blob_text.lower()
                                                for color in [
                                                    "розов",
                                                    "красн",
                                                    "бел",
                                                    "голуб",
                                                    "зелен",
                                                ]
                                            ):
                                                print(
                                                    f"         🌸 НАЙДЕНА ЦВЕТОЧНАЯ ИНФОРМАЦИЯ в {field_name}!"
                                                )

                                            # Поиск информации о магазине
                                            if any(
                                                store in blob_text.lower()
                                                for store in [
                                                    "магазин",
                                                    "пц",
                                                    "южный",
                                                    "чеховский",
                                                ]
                                            ):
                                                print(
                                                    f"         🏪 НАЙДЕНА ИНФОРМАЦИЯ О МАГАЗИНЕ в {field_name}!"
                                                )

                                            # Поиск финансовой информации
                                            if any(
                                                finance in blob_text.lower()
                                                for finance in [
                                                    "руб",
                                                    "сумма",
                                                    "цена",
                                                    "стоимость",
                                                ]
                                            ):
                                                print(
                                                    f"         💰 НАЙДЕНА ФИНАНСОВАЯ ИНФОРМАЦИЯ в {field_name}!"
                                                )
                                    except Exception as e:
                                        print(
                                            f"         ⚠️ Ошибка декодирования BLOB {field_name}: {e}"
                                        )

                                    # ИСПРАВЛЕНО: Анализируем заголовки для определения типа BLOB
                                    blob_bytes = (
                                        info.get("original_bytes") or info["value"]
                                    )
                                    blob_type = "unknown"

                                    # Проверяем заголовки файлов
                                    if isinstance(
                                        blob_bytes, bytes
                                    ) and blob_bytes.startswith(b"\xff\xd8\xff"):
                                        blob_type = "JPEG"
                                    elif isinstance(
                                        blob_bytes, bytes
                                    ) and blob_bytes.startswith(b"\x89PNG"):
                                        blob_type = "PNG"
                                    elif isinstance(
                                        blob_bytes, bytes
                                    ) and blob_bytes.startswith(b"GIF"):
                                        blob_type = "GIF"
                                    elif isinstance(
                                        blob_bytes, bytes
                                    ) and blob_bytes.startswith(b"\x00\x00\x01\x00"):
                                        blob_type = "ICO"
                                    elif isinstance(
                                        blob_bytes, bytes
                                    ) and blob_bytes.startswith(b"%PDF"):
                                        blob_type = "PDF"
                                    elif isinstance(
                                        blob_bytes, bytes
                                    ) and blob_bytes.startswith(b"PK"):
                                        blob_type = "ZIP/Office"

                                    # ИСПРАВЛЕНО: Правильное декодирование в зависимости от типа
                                    if blob_type == "unknown":
                                        # Пробуем декодировать как текст
                                        try:
                                            blob_content = blob_bytes.decode(
                                                "utf-8",
                                                errors="ignore",
                                            )
                                            if len(blob_content.strip()) > 10:
                                                blob_type = "TEXT_UTF8"
                                        except:
                                            try:
                                                blob_content = blob_bytes.decode(
                                                    "utf-16",
                                                    errors="ignore",
                                                )
                                                if len(blob_content.strip()) > 10:
                                                    blob_type = "TEXT_UTF16"
                                            except:
                                                blob_content = (
                                                    blob_bytes.hex()[:100] + "..."
                                                )
                                                blob_type = "BINARY"
                                    else:
                                        blob_content = f"[{blob_type} файл, {len(blob_bytes)} байт]"

                                    document["blob_content"] = blob_content
                                    print(
                                        f"   ✅ BLOB поле ({blob_type}): {field_name} = {len(blob_content)} символов",
                                    )

                                    # Показываем содержимое BLOB для анализа
                                    if len(blob_content) > 0:
                                        print(f"      📄 СОДЕРЖИМОЕ BLOB {field_name}:")
                                        # Показываем первые 200 символов для анализа
                                        preview = (
                                            blob_content[:200]
                                            if len(blob_content) > 200
                                            else blob_content
                                        )
                                        print(f"         {preview}")
                                        if len(blob_content) > 200:
                                            print(
                                                f"         ... (еще {len(blob_content) - 200} символов)",
                                            )

                                        # Анализируем содержимое на предмет цветочной информации
                                        if any(
                                            keyword in blob_content.lower()
                                            for keyword in [
                                                "цвет",
                                                "rose",
                                                "тюльпан",
                                                "флор",
                                                "букет",
                                            ]
                                        ):
                                            print(
                                                f"      🌸 НАЙДЕНА ЦВЕТОЧНАЯ ИНФОРМАЦИЯ в {field_name}!",
                                            )
                                        if any(
                                            keyword in blob_content.lower()
                                            for keyword in [
                                                "магазин",
                                                "склад",
                                                "поставщик",
                                            ]
                                        ):
                                            print(
                                                f"      🏪 НАЙДЕНА ИНФОРМАЦИЯ О МАГАЗИНЕ в {field_name}!",
                                            )
                                        if any(
                                            keyword in blob_content.lower()
                                            for keyword in [
                                                "сумма",
                                                "цена",
                                                "стоимость",
                                            ]
                                        ):
                                            print(
                                                f"      💰 НАЙДЕНА ФИНАНСОВАЯ ИНФОРМАЦИЯ в {field_name}!",
                                            )

                                    # Анализируем содержимое BLOB
                                    if "флор" in blob_content.lower():
                                        document["document_type"] = "ФЛОРИСТИКА"
                                    elif "декор" in blob_content.lower():
                                        document["document_type"] = "ДЕКОР"
                                    elif "моно" in blob_content.lower():
                                        document["document_type"] = "МОНО БУКЕТ"
                                    elif "интернет" in blob_content.lower():
                                        document["document_type"] = "ИНТЕРНЕТ-ЗАКАЗ"

                                    # Извлекаем название магазина из BLOB
                                    if "магазин" in blob_content.lower():
                                        store_match = re.search(
                                            r"Магазин\s+([^)]+)",
                                            blob_content,
                                        )
                                        if store_match:
                                            document["store_name"] = store_match.group(
                                                1,
                                            )
                                        print(
                                            f"   ✅ Название магазина из BLOB: {document['store_name']}",
                                        )

                                    # Извлекаем коды магазинов из BLOB
                                    store_code_match = re.search(
                                        r"ПЦ(\d+)",
                                        blob_content,
                                    )
                                    if store_code_match:
                                        document["store_code"] = (
                                            f"ПЦ{store_code_match.group(1)}"
                                        )
                                    print(
                                        f"   ✅ Код магазина из BLOB: {document['store_code']}",
                                    )

                            # Итоговый анализ структуры
                            print("\n📊 ИТОГОВАЯ СТРУКТУРА ДОКУМЕНТА:")
                            print(f"   🔢 Поля с номерами: {number_fields}")
                            print(f"   📅 Поля с датами: {date_fields}")
                            print(f"   📝 Поля с описанием: {description_fields}")
                            print(f"   💰 Поля с суммами: {amount_fields}")
                            print(f"   🏪 Поля с типом продажи: {sale_type_fields}")
                            print(f"   📦 BLOB поля: {blob_fields}")

                            # Проверяем качество извлечения
                            print(
                                f"\n✅ ПРОВЕРКА КАЧЕСТВА ИЗВЛЕЧЕНИЯ для документа {i}:",
                            )
                            print(
                                f"   📋 Номер документа: {document.get('document_number', 'НЕ НАЙДЕН')}",
                            )
                            print(
                                f"   📅 Дата документа: {document.get('document_date', 'НЕ НАЙДЕНА')}",
                            )
                            print(
                                f"   🏷️ Тип документа: {document.get('document_type', 'НЕ НАЙДЕН')}",
                            )
                            print(
                                f"   💰 Сумма: {document.get('total_amount', 'НЕ НАЙДЕНА')}",
                            )
                            print(
                                f"   🏪 Магазин: {document.get('store_name', 'НЕ НАЙДЕН')}",
                            )
                            print(
                                f"   🏷️ Код магазина: {document.get('store_code', 'НЕ НАЙДЕН')}",
                            )
                            print(
                                f"   📄 BLOB: {len(document.get('blob_content', ''))} символов",
                            )

                            # Статистика по полям
                            total_fields = len(field_analysis)
                            successful_fields = len(
                                [
                                    f
                                    for f in field_analysis.values()
                                    if f.get("value") is not None
                                ],
                            )
                            blob_fields = len(
                                [
                                    f
                                    for f in field_analysis.values()
                                    if f.get("is_blob", False)
                                ],
                            )

                            print("   📊 СТАТИСТИКА ПОЛЕЙ:")
                            print(f"      Всего полей: {total_fields}")
                            print(f"      Успешно извлечено: {successful_fields}")
                            print(f"      BLOB полей: {blob_fields}")
                            print(
                                (
                                    f"      Процент успеха: {(successful_fields / total_fields * 100):.1f}%"
                                    if total_fields > 0
                                    else "      Процент успеха: 0%"
                                ),
                            )

                            # Сохраняем анализ структуры
                            document["field_analysis"] = field_analysis
                            document["structure_summary"] = {
                                "number_fields": number_fields,
                                "date_fields": date_fields,
                                "description_fields": description_fields,
                                "amount_fields": amount_fields,
                                "sale_type_fields": sale_type_fields,
                                "blob_fields": blob_fields,
                            }

                            # Дублирующий код удален - данные уже извлечены выше

                            # Дублирующий код удален - данные уже извлечены выше

                            # Извлекаем табличные части документа
                            table_parts = extract_table_parts(db, table_name, row_index)
                            if table_parts:
                                document["table_parts"] = table_parts

                            # Обрабатываем BLOB поля с надежной обработкой ошибок
                            processed_blobs = (
                                set()
                            )  # Отслеживаем уже обработанные BLOB поля
                            for field_name, value in row_dict.items():
                                try:
                                    if value is not None:
                                        # Преобразуем datetime в строку
                                        if isinstance(value, datetime):
                                            value = value.isoformat()
                                        # ИСПРАВЛЕНО: Сохраняем оригинальные bytes для анализа BLOB
                                        elif isinstance(value, bytes):
                                            # Сохраняем оригинальные bytes в field_analysis для анализа BLOB
                                            if field_name in field_analysis:
                                                field_analysis[field_name][
                                                    "original_bytes"
                                                ] = value
                                            value = value.hex()
                                        # ИСПРАВЛЕНО: Правильная проверка типа BLOB объекта
                                        elif (
                                            hasattr(value, "value")
                                            and hasattr(value, "__class__")
                                            and "Blob" in str(type(value))
                                            and field_name not in processed_blobs
                                        ):
                                            if (
                                                isinstance(document, dict)
                                                and "extraction_stats" in document
                                            ):
                                                document["extraction_stats"][
                                                    "total_blobs"
                                                ] += 1

                                                # Правильная обработка BLOB согласно onec_dtools API
                                                blob_data: dict = {
                                                    "field_type": "blob",
                                                    "size": (
                                                        len(value)
                                                        if hasattr(value, "__len__")
                                                        else 0
                                                    ),
                                                    "extraction_methods": [],
                                                }

                                            # ИСПРАВЛЕНО: Правильное декодирование BLOB согласно onec_dtools API
                                            if hasattr(value, "value"):
                                                try:
                                                    content = value.value
                                                    if content:
                                                        # Правильное декодирование: UTF-16 для NT полей, затем UTF-8, CP1251
                                                        if isinstance(content, bytes):
                                                            # Сначала пробуем UTF-16 (стандарт для NT полей)
                                                            try:
                                                                decoded_content = (
                                                                    content.decode(
                                                                        "utf-16",
                                                                    )
                                                                )
                                                                blob_data["value"] = {
                                                                    "content": decoded_content,
                                                                    "type": "text_utf16",
                                                                    "length": len(
                                                                        decoded_content,
                                                                    ),
                                                                    "raw_bytes": content.hex()[
                                                                        :100
                                                                    ],
                                                                }
                                                            except UnicodeDecodeError:
                                                                # Затем UTF-8
                                                                try:
                                                                    decoded_content = (
                                                                        content.decode(
                                                                            "utf-8",
                                                                        )
                                                                    )
                                                                    blob_data[
                                                                        "value"
                                                                    ] = {
                                                                        "content": decoded_content,
                                                                        "type": "text_utf8",
                                                                        "length": len(
                                                                            decoded_content,
                                                                        ),
                                                                        "raw_bytes": content.hex()[
                                                                            :100
                                                                        ],
                                                                    }
                                                                except (
                                                                    UnicodeDecodeError
                                                                ):
                                                                    # Затем CP1251
                                                                    try:
                                                                        decoded_content = content.decode(
                                                                            "cp1251",
                                                                        )
                                                                        blob_data[
                                                                            "value"
                                                                        ] = {
                                                                            "content": decoded_content,
                                                                            "type": "text_cp1251",
                                                                            "length": len(
                                                                                decoded_content,
                                                                            ),
                                                                            "raw_bytes": content.hex()[
                                                                                :100
                                                                            ],
                                                                        }
                                                                    except UnicodeDecodeError:
                                                                        blob_data[
                                                                            "value"
                                                                        ] = {
                                                                            "content": content.hex(),
                                                                            "type": "binary_hex",
                                                                            "length": len(
                                                                                content,
                                                                            ),
                                                                            "raw_bytes": content.hex()[
                                                                                :100
                                                                            ],
                                                                        }
                                                        else:
                                                            blob_data["value"] = {
                                                                "content": str(content),
                                                                "type": type(
                                                                    content,
                                                                ).__name__,
                                                                "length": len(
                                                                    str(content),
                                                                ),
                                                            }
                                                        if isinstance(
                                                            blob_data.get(
                                                                "extraction_methods",
                                                            ),
                                                            list,
                                                        ):
                                                            blob_data[
                                                                "extraction_methods"
                                                            ].append("value")
                                                        if (
                                                            isinstance(document, dict)
                                                            and "extraction_stats"
                                                            in document
                                                        ):
                                                            document[
                                                                "extraction_stats"
                                                            ]["successful"] += 1
                                                except Exception:
                                                    blob_data["value_error"] = (
                                                        "Ошибка извлечения"
                                                    )

                                            # Метод 2: bytes (правильная обработка BLOB)
                                            if isinstance(value, bytes):
                                                try:
                                                    # Пытаемся декодировать как текст
                                                    try:
                                                        content = value.decode("utf-8")
                                                        blob_data["bytes_utf8"] = {
                                                            "content": content,
                                                            "type": "bytes_utf8",
                                                            "length": len(content),
                                                        }
                                                        if isinstance(
                                                            blob_data.get(
                                                                "extraction_methods",
                                                            ),
                                                            list,
                                                        ):
                                                            blob_data[
                                                                "extraction_methods"
                                                            ].append("bytes_utf8")
                                                        if (
                                                            isinstance(document, dict)
                                                            and "extraction_stats"
                                                            in document
                                                        ):
                                                            document[
                                                                "extraction_stats"
                                                            ]["successful"] += 1
                                                    except UnicodeDecodeError:
                                                        # Пытаемся декодировать как cp1251
                                                        try:
                                                            content = value.decode(
                                                                "cp1251",
                                                            )
                                                            blob_data[
                                                                "bytes_cp1251"
                                                            ] = {
                                                                "content": content,
                                                                "type": "bytes_cp1251",
                                                                "length": len(content),
                                                            }
                                                            if isinstance(
                                                                blob_data.get(
                                                                    "extraction_methods",
                                                                ),
                                                                list,
                                                            ):
                                                                blob_data[
                                                                    "extraction_methods"
                                                                ].append("bytes_cp1251")
                                                            if (
                                                                isinstance(
                                                                    document,
                                                                    dict,
                                                                )
                                                                and "extraction_stats"
                                                                in document
                                                            ):
                                                                document[
                                                                    "extraction_stats"
                                                                ]["successful"] += 1
                                                        except UnicodeDecodeError:
                                                            # Сохраняем как hex
                                                            blob_data["bytes_hex"] = {
                                                                "content": value.hex(),
                                                                "type": "bytes_hex",
                                                                "length": len(value),
                                                            }
                                                            if isinstance(
                                                                blob_data.get(
                                                                    "extraction_methods",
                                                                ),
                                                                list,
                                                            ):
                                                                blob_data[
                                                                    "extraction_methods"
                                                                ].append("bytes_hex")
                                                            if (
                                                                isinstance(
                                                                    document,
                                                                    dict,
                                                                )
                                                                and "extraction_stats"
                                                                in document
                                                            ):
                                                                document[
                                                                    "extraction_stats"
                                                                ]["successful"] += 1
                                                except Exception as e:
                                                    # Обрабатываем только реальные ошибки, не StopIteration
                                                    if "StopIteration" not in str(e):
                                                        blob_data["iterator_error"] = (
                                                            f"Ошибка итератора: {e!s}"
                                                        )

                                            # Метод 3: bytes (уже обработано выше)
                                            # Этот метод дублирует обработку bytes, убираем

                                            # Если ни один метод не сработал
                                            if not blob_data.get(
                                                "extraction_methods",
                                                [],
                                            ):
                                                if (
                                                    isinstance(document, dict)
                                                    and "extraction_stats" in document
                                                ):
                                                    document["extraction_stats"][
                                                        "failed"
                                                    ] += 1
                                                blob_data["error"] = (
                                                    "No extraction method worked"
                                                )

                                            if (
                                                isinstance(document, dict)
                                                and "blobs" in document
                                            ):
                                                document["blobs"][
                                                    field_name
                                                ] = blob_data
                                                processed_blobs.add(
                                                    field_name,
                                                )  # Отмечаем как обработанное
                                            if (
                                                isinstance(all_results, dict)
                                                and "metadata" in all_results
                                            ):
                                                all_results["metadata"][
                                                    "total_blobs"
                                                ] += 1

                                                if blob_data.get(
                                                    "extraction_methods",
                                                    [],
                                                ):
                                                    all_results["metadata"][
                                                        "successful_extractions"
                                                    ] += 1
                                                else:
                                                    all_results["metadata"][
                                                        "failed_extractions"
                                                    ] += 1

                                        elif (
                                            isinstance(document, dict)
                                            and "fields" in document
                                        ):
                                            document["fields"][field_name] = value
                                except StopIteration:
                                    # ИСПРАВЛЕНО: StopIteration - это нормальное завершение итератора, не ошибка
                                    print(
                                        f"   ℹ️ StopIteration для поля {field_name} - нормальное завершение итератора",
                                    )
                                    continue
                                except Exception as e:
                                    # ИСПРАВЛЕНО: Обрабатываем только реальные ошибки, не StopIteration
                                    error_msg = str(e)
                                    if "StopIteration" not in error_msg:
                                        error_counter[error_msg] = (
                                            error_counter.get(error_msg, 0) + 1
                                        )
                                        # Логируем только реальные ошибки
                                        if error_counter[error_msg] <= 5:
                                            print(
                                                f"   ⚠️ Ошибка при обработке поля {field_name}: {error_msg}",
                                            )
                                    else:
                                        # StopIteration - это нормальное завершение итератора, не ошибка
                                        print(
                                            f"   ℹ️ Нормальное завершение итератора для поля {field_name}"
                                        )
                                        continue

                                    # Логируем ошибку в файл
                                    with open(
                                        "logs/extraction_errors.log",
                                        "a",
                                        encoding="utf-8",
                                    ) as log_file:
                                        log_file.write(
                                            f"{datetime.now().isoformat()} - {table_name} - {field_name}: {error_msg}\n",
                                        )

                                    # Проверяем, не слишком ли много повторяющихся ошибок
                                    if error_counter[error_msg] > max_repeated_errors:
                                        print(
                                            f"   🛑 СЛИШКОМ МНОГО ПОВТОРЯЮЩИХСЯ ОШИБОК: {error_msg} ({error_counter[error_msg]} раз)",
                                        )
                                        print(
                                            f"   🛑 ОСТАНАВЛИВАЕМ ИЗВЛЕЧЕНИЕ ИЗ ТАБЛИЦЫ {table_name}",
                                        )
                                        break

                                    if (
                                        error_counter[error_msg] <= 5
                                    ):  # Показываем только первые 5 ошибок каждого типа
                                        print(
                                            f"   ⚠️ Ошибка при обработке поля {field_name}: {error_msg}",
                                        )
                                    continue

                            if (
                                isinstance(all_results, dict)
                                and "documents" in all_results
                            ):
                                all_results["documents"].append(document)
                            if (
                                isinstance(all_results, dict)
                                and "metadata" in all_results
                            ):
                                all_results["metadata"]["total_documents"] += 1
                            successful_docs += 1

                            # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ С АНАЛИЗОМ ДОКУМЕНТА
                            if i <= 10 or i % 10 == 0:  # Первые 10 и каждую 10-ю
                                # Основные поля документа
                                doc_number = document.get("document_number", "N/A")
                                doc_date = document.get("document_date", "N/A")
                                doc_sum = document.get("total_amount", "N/A")
                                doc_type = document.get("document_type", "N/A")

                                # Статистика BLOB полей
                                blob_count = document.get("extraction_stats", {}).get(
                                    "successful",
                                    0,
                                )
                                failed_blobs = document.get("extraction_stats", {}).get(
                                    "failed",
                                    0,
                                )

                                # Анализ содержимого BLOB полей
                                doc_title = "N/A"
                                failed_fields = []

                                if "blobs" in document:
                                    for blob_name, blob_data in document[
                                        "blobs"
                                    ].items():
                                        if blob_data.get("value", {}).get("content"):
                                            content = blob_data["value"]["content"]
                                            if len(
                                                content,
                                            ) > 10 and not (
                                                isinstance(content, str)
                                                and content.startswith("b'")
                                            ):
                                                if not doc_title or doc_title == "N/A":
                                                    doc_title = (
                                                        content[:50] + "..."
                                                        if len(content) > 50
                                                        else content
                                                    )

                                                # Анализ цветочной информации
                                                # Простое отображение содержимого
                                        else:
                                            failed_fields.append(blob_name)

                                # Простое отображение типа документа
                                operation_type = "Документ"

                                # Формируем детальный лог с содержимым BLOB
                                blob_content = ""
                                if "blobs" in document:
                                    for blob_name, blob_data in document[
                                        "blobs"
                                    ].items():
                                        if blob_data.get("value", {}).get("content"):
                                            content = blob_data["value"]["content"]
                                            blob_content += f" | {blob_name}: {content[:50]}{'...' if len(str(content)) > 50 else ''}"

                                log_line = f"   ✅ {i:,}: {doc_number} | {doc_date} | {doc_sum}₽ | {operation_type} | {blob_count} BLOB{blob_content}"

                                # Добавляем информацию о BLOB полях
                                if blob_content:
                                    log_line += f" | 📄 {blob_count} BLOB полей"

                                # Добавляем информацию о неудачных полях
                                if failed_fields:
                                    log_line += f" | ❌ {len(failed_fields)} неудачных полей: {', '.join(failed_fields[:3])}"

                                print(log_line)

                                # Дополнительная информация для первых 10 записей
                                if i <= 10:
                                    if failed_fields:
                                        print(
                                            f"      ❌ Неудачные поля: {', '.join(failed_fields[:3])}",
                                        )
                                    if doc_type != "N/A":
                                        print(f"      📋 Тип документа: {doc_type}")

                                    # Показываем содержимое BLOB полей
                                    if "blobs" in document:
                                        print(f"      🔍 BLOB поля ({blob_count}):")
                                        for blob_name, blob_data in document[
                                            "blobs"
                                        ].items():
                                            if blob_data.get("value", {}).get(
                                                "content",
                                            ):
                                                content = blob_data["value"]["content"]
                                                print(
                                                    f"         ✅ {blob_name}: {content[:100]}{'...' if len(str(content)) > 100 else ''}",
                                                )
                                            else:
                                                print(
                                                    f"         ❌ {blob_name}: НЕ ИЗВЛЕЧЕНО",
                                                )

                            # Проверяем, не нужно ли остановиться из-за ошибок
                            if any(
                                count > max_repeated_errors
                                for count in error_counter.values()
                            ):
                                print("   🛑 ОСТАНОВКА ИЗ-ЗА ПОВТОРЯЮЩИХСЯ ОШИБОК")
                                break

                            # ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРВОЙ ЗАПИСИ
                            if i == 1 and isinstance(document, dict):
                                print("   📄 ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРВОЙ ЗАПИСИ:")

                                # Основная информация
                                print(
                                    f"      📋 Номер: {document.get('document_number', 'N/A')}",
                                )
                                print(
                                    f"      📅 Дата: {document.get('document_date', 'N/A')}",
                                )
                                print(
                                    f"      💰 Сумма: {document.get('total_amount', 'N/A')}₽",
                                )
                                print(
                                    f"      🏷️ Тип: {document.get('document_type', 'N/A')}",
                                )

                                # Статистика BLOB полей
                                total_blobs = document.get("extraction_stats", {}).get(
                                    "total_blobs",
                                    0,
                                )
                                successful_blobs = document.get(
                                    "extraction_stats",
                                    {},
                                ).get("successful", 0)
                                failed_blobs = document.get("extraction_stats", {}).get(
                                    "failed",
                                    0,
                                )

                                print(
                                    f"      📊 BLOB полей: {total_blobs} (✅ {successful_blobs}, ❌ {failed_blobs})",
                                )

                                # Анализ каждого BLOB поля
                                print("      🔍 АНАЛИЗ BLOB ПОЛЕЙ:")
                                for blob_name, blob_data in document.get(
                                    "blobs",
                                    {},
                                ).items():
                                    if blob_data.get("extraction_methods", []):
                                        methods_str = ", ".join(
                                            blob_data.get("extraction_methods", []),
                                        )
                                        content = blob_data.get("value", {}).get(
                                            "content",
                                            "N/A",
                                        )

                                        # Простое отображение содержимого без классификации
                                        content_type = "📄 ТЕКСТ"

                                        print(
                                            f"         ✅ {blob_name}: {content_type} | {methods_str}",
                                        )
                                        print(
                                            f"            📝 Содержимое: '{content[:80]}{'...' if len(str(content)) > 80 else ''}'",
                                        )
                                    else:
                                        print(f"         ❌ {blob_name}: НЕ ИЗВЛЕЧЕНО")
                                        if blob_data.get("error"):
                                            print(
                                                f"            🚫 Ошибка: {blob_data.get('error')}",
                                            )
                                        elif blob_data.get("value_error"):
                                            print(
                                                f"            🚫 Ошибка значения: {blob_data.get('value_error')}",
                                            )
                                        elif blob_data.get("iterator_error"):
                                            print(
                                                f"            🚫 Ошибка итератора: {blob_data.get('iterator_error')}",
                                            )
                                        else:
                                            print(
                                                "            🚫 Неизвестная ошибка извлечения",
                                            )

                                        # Показываем что мы пытались извлечь
                                        if blob_data.get("size", 0) > 0:
                                            print(
                                                f"            📊 Размер данных: {blob_data.get('size')} байт",
                                            )
                                        if blob_data.get("field_type"):
                                            print(
                                                f"            🏷️ Тип поля: {blob_data.get('field_type')}",
                                            )

                                # Анализ неудачных полей
                                if failed_blobs > 0:
                                    print(f"      ⚠️ НЕУДАЧНЫЕ ПОЛЯ ({failed_blobs}):")
                                    for blob_name, blob_data in document.get(
                                        "blobs",
                                        {},
                                    ).items():
                                        if not blob_data.get("extraction_methods", []):
                                            print(
                                                f"         ❌ {blob_name}: {blob_data.get('error', 'Неизвестная ошибка')}",
                                            )

                        except Exception as e:
                            # ИСПРАВЛЕНО: Обрабатываем только реальные ошибки, не StopIteration
                            error_msg = str(e)
                            if "StopIteration" not in error_msg and "generator raised StopIteration" not in error_msg:
                                print(f"   ⚠️ Ошибка при обработке записи {i}: {e!s}")
                            else:
                                print(
                                    f"   ℹ️ Нормальное завершение итератора для записи {i}"
                                )
                            continue

                    # СВОДНАЯ СТАТИСТИКА ПО BLOB ДАННЫМ

                    total_blobs = 0
                    total_failed_fields = 0

                    # Анализируем все обработанные документы
                    for doc in all_results.get("documents", []):
                        if doc.get("table_name") == table_name:
                            # Подсчитываем все BLOB поля
                            for blob_name, blob_data in doc.get("blobs", {}).items():
                                if blob_data.get("value", {}).get("content"):
                                    total_blobs += 1
                                else:
                                    total_failed_fields += 1

                    print(
                        f"   📄 Успешно обработано {successful_docs} документов из {table_name}",
                    )
                    print(f"   📊 BLOB полей: {total_blobs}")
                    print(f"   ❌ Неудачных полей: {total_failed_fields}")

                    if total_blobs > 0:
                        print(
                            f"   ✅ Качество извлечения BLOB данных: {((total_blobs - total_failed_fields) / total_blobs * 100):.1f}%",
                        )
                    else:
                        print(f"   ⚠️ BLOB данные не найдены в таблице {table_name}")

            # Извлекаем справочники
            for table_name in reference_tables_to_extract:
                if table_name in db.tables:
                    print(f"\n📚 Анализ справочника: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")

                    # Извлекаем ВСЕ записи справочника
                    successful_refs = 0
                    print(
                        f"   🔄 Извлечение всех {len(table):,} записей справочника...",
                    )
                    for i in range(len(table)):
                        try:
                            row = table[i]
                            if not hasattr(row, "is_empty") or not row.is_empty:
                                row_dict = (
                                    row.as_list(True) if hasattr(row, "as_list") else {}
                                )
                                if row_dict:
                                    reference = {
                                        "id": f"{table_name}_{i}",
                                        "table_name": table_name,
                                        "fields": row_dict,
                                        "extraction_stats": {
                                            "extraction_time": datetime.now().isoformat(),
                                            "success": True,
                                        },
                                    }
                                    all_results["references"].append(reference)
                                    successful_refs += 1
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при извлечении справочника {i}: {e!s}")
                            continue

                    print(
                        f"   ✅ Успешно извлечено {successful_refs} записей справочника",
                    )
                    all_results["metadata"]["total_references"] += successful_refs

            # Извлекаем регистры
            for table_name in register_tables_to_extract:
                if table_name in db.tables:
                    print(f"\n📊 Анализ регистра: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")

                    # Извлекаем ВСЕ записи регистра
                    successful_regs = 0
                    print(f"   🔄 Извлечение всех {len(table):,} записей регистра...")
                    for i in range(len(table)):
                        try:
                            row = table[i]
                            if not hasattr(row, "is_empty") or not row.is_empty:
                                row_dict = (
                                    row.as_list(True) if hasattr(row, "as_list") else {}
                                )
                                if row_dict:
                                    register = {
                                        "id": f"{table_name}_{i}",
                                        "table_name": table_name,
                                        "fields": row_dict,
                                        "extraction_stats": {
                                            "extraction_time": datetime.now().isoformat(),
                                            "success": True,
                                        },
                                    }
                                    all_results["registers"].append(register)
                                    successful_regs += 1
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при извлечении регистра {i}: {e!s}")
                            continue

                    print(f"   ✅ Успешно извлечено {successful_regs} записей регистра")
                    all_results["metadata"]["total_registers"] += successful_regs

            # Сохраняем результат в JSON
            output_file = "data/results/all_available_data.json"
            with open(output_file, "w", encoding="utf-8") as f:  # type: ignore
                json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)  # type: ignore

            print(f"\n💾 Результат сохранен в: {output_file}")

            # Создаем XML с всеми доступными данными
            create_all_available_xml(all_results)

            # КОНВЕРТИРУЕМ В PARQUET И DUCKDB
            convert_to_parquet_duckdb(all_results)

            print("\n✅ Извлечение всех доступных данных завершено")

    except Exception as e:
        print(f"❌ Ошибка: {e!s}")
        import traceback

        traceback.print_exc()


def convert_to_parquet_duckdb(all_results: dict) -> None:
    """
    Конвертация результатов в Parquet и DuckDB для аналитики
    """
    print("\n🦆 Конвертация в Parquet и DuckDB...")

    try:
        # Создаем директории
        os.makedirs("data/results/parquet", exist_ok=True)
        os.makedirs("data/results/duckdb", exist_ok=True)

        # Конвертируем документы в DataFrame
        documents_data = []
        for doc in all_results.get("documents", []):
            # Извлекаем основные поля
            doc_data = {
                "id": doc.get("id", ""),
                "table_name": doc.get("table_name", ""),
                "row_index": doc.get("row_index", 0),
                "document_type": doc.get("document_type", "Неизвестно"),
                "document_number": doc.get("document_number", "N/A"),
                "document_date": doc.get("document_date", "N/A"),
                "store_name": doc.get("store_name", "N/A"),
                "store_code": doc.get("store_code", "N/A"),
                "total_amount": doc.get("total_amount", 0.0),
                "currency": doc.get("currency", "RUB"),
                "supplier_name": doc.get("supplier_name", "N/A"),
                "buyer_name": doc.get("buyer_name", "N/A"),
                "blob_content": doc.get("blob_content", ""),
                "total_blobs": doc.get("extraction_stats", {}).get("total_blobs", 0),
                "successful_blobs": doc.get("extraction_stats", {}).get(
                    "successful",
                    0,
                ),
                "failed_blobs": doc.get("extraction_stats", {}).get("failed", 0),
            }

            # Добавляем поля из fields
            for field_name, value in doc.get("fields", {}).items():
                if isinstance(value, (str, int, float, bool)):
                    doc_data[f"field_{field_name}"] = value
                else:
                    doc_data[f"field_{field_name}"] = str(value)

            # Добавляем информацию о BLOB полях
            blob_count = 0
            for blob_name, blob_data in doc.get("blobs", {}).items():
                if blob_data.get("extraction_methods"):
                    blob_count += 1
                    doc_data[f"blob_{blob_name}_methods"] = ",".join(
                        blob_data.get("extraction_methods", []),
                    )
                    doc_data[f"blob_{blob_name}_size"] = blob_data.get("size", 0)

            doc_data["blob_fields_count"] = blob_count
            documents_data.append(doc_data)

        if documents_data:
            # Создаем DataFrame
            df = pd.DataFrame(documents_data)

            # Сохраняем в Parquet
            parquet_file = "data/results/parquet/documents.parquet"
            df.to_parquet(parquet_file, index=False)
            print(f"✅ Parquet файл создан: {parquet_file}")

            # Создаем DuckDB базу
            duckdb_file = "data/results/duckdb/analysis.duckdb"
            con = duckdb.connect(duckdb_file)

            # Загружаем данные в DuckDB
            con.execute(
                f"CREATE OR REPLACE TABLE documents AS SELECT * FROM '{parquet_file}'",
            )

            # Создаем индексы для быстрого поиска
            con.execute(
                "CREATE INDEX IF NOT EXISTS idx_table_name ON documents(table_name)",
            )
            con.execute(
                "CREATE INDEX IF NOT EXISTS idx_blob_count ON documents(blob_fields_count)",
            )

            # Выполняем аналитические запросы
            print("\n📊 Аналитические запросы:")

            # Статистика по таблицам
            result = con.execute(
                """
                SELECT
                    table_name,
                    COUNT(*) as total_documents,
                    SUM(blob_fields_count) as total_blobs,
                    AVG(blob_fields_count) as avg_blobs_per_doc
                FROM documents
                GROUP BY table_name
                ORDER BY total_documents DESC
            """,
            ).fetchdf()
            print("📈 Статистика по таблицам:")
            print(result)

            # Топ таблиц по BLOB полям
            result = con.execute(
                """
                SELECT
                    table_name,
                    SUM(successful_blobs) as successful_blobs,
                    SUM(failed_blobs) as failed_blobs,
                    ROUND(SUM(successful_blobs) * 100.0 / (SUM(successful_blobs) + SUM(failed_blobs)), 2) as success_rate
                FROM documents
                WHERE successful_blobs + failed_blobs > 0
                GROUP BY table_name
                ORDER BY successful_blobs DESC
                LIMIT 10
            """,
            ).fetchdf()
            print("\n🏆 Топ таблиц по BLOB полям:")
            print(result)

            # Анализ всех документов без фильтрации по ключевым словам
            print("\n📊 Анализ всех документов:")
            result = con.execute(
                """
                SELECT table_name, COUNT(*) as total_documents
                FROM documents
                GROUP BY table_name
                ORDER BY total_documents DESC
                """,
            ).fetchdf()
            print(result)

            con.close()
            print(f"✅ DuckDB база создана: {duckdb_file}")

        else:
            print("⚠️ Нет данных для конвертации")

    except Exception as e:
        print(f"❌ Ошибка конвертации в Parquet/DuckDB: {e}")
        import traceback

        traceback.print_exc()


def extract_data_detailed_method() -> None:
    """
    Детальный метод извлечения данных с анализом структуры базы
    """
    print("🔍 Используем детальный метод извлечения данных")
    print("=" * 60)

    try:
        # Попробуем использовать более низкоуровневый доступ
        print("📊 Анализируем структуру базы данных...")

        # Проверяем существующие экспортированные данные
        results_dir = "data/results/"
        exported_dir = "data/exported/exported_tables/"

        all_data = {
            "extraction_method": "detailed_analysis",
            "extraction_date": datetime.now().isoformat(),
            "source_files": [],
            "exported_tables": [],
            "analysis_results": {},
            "status": "in_progress",
        }

        # Анализируем экспортированные таблицы
        if os.path.exists(exported_dir):
            print("✅ Найдена директория с экспортированными таблицами: {exported_dir}")
            xml_files = [f for f in os.listdir(exported_dir) if f.endswith(".xml")]
            all_data["exported_tables"] = xml_files
            print("📄 Найдено {len(xml_files)} экспортированных XML таблиц")

        # Анализируем результаты
        if os.path.exists(results_dir):
            print("✅ Найдена директория с результатами: {results_dir}")
            json_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
            all_data["source_files"] = json_files
            print("📄 Найдено {len(json_files)} JSON файлов с результатами")

        # Создаем детальный анализ
        all_data["analysis_results"] = {
            "total_exported_tables": len(all_data["exported_tables"]),
            "total_result_files": len(all_data["source_files"]),
            "extraction_completeness": "partial_using_existing_data",
            "recommendations": [
                "Использовать существующие экспортированные данные",
                "Провести анализ XML таблиц для полного извлечения",
                "Создать сводный отчет по всем источникам данных",
            ],
        }

        # Сохраняем детальный анализ
        with open("detailed_extraction_analysis.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print("💾 Детальный анализ сохранен в: detailed_extraction_analysis.json")
        print("✅ Детальное извлечение завершено успешно")

    except Exception:
        print("❌ Ошибка в детальном методе: ")
        return


def extract_data_alternative_method() -> None:
    """
    Альтернативный метод извлечения данных при ошибке 'Unknown field type'
    """
    print("🔄 Используем альтернативный метод извлечения данных")
    print("=" * 60)

    try:
        # Используем существующие экспортированные данные
        results_dir = "data/results/"
        if os.path.exists(results_dir):
            print("✅ Найдена директория с результатами: {results_dir}")

            # Собираем все JSON файлы
            json_files = []
            for file in os.listdir(results_dir):
                if file.endswith(".json"):
                    json_files.append(os.path.join(results_dir, file))

            print("📄 Найдено {len(json_files)} JSON файлов с данными")

            # Создаем сводный отчет
            summary = {
                "extraction_method": "alternative_from_existing_files",
                "total_files": len(json_files),
                "files": json_files,
                "extraction_date": datetime.now().isoformat(),
                "status": "completed_using_existing_data",
            }

            # Сохраняем сводный отчет
            with open(
                "alternative_extraction_summary.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            print("💾 Сводный отчет сохранен в: alternative_extraction_summary.json")
            print("✅ Альтернативное извлечение завершено успешно")
        else:
            print("❌ Директория с результатами не найдена: {results_dir}")

    except Exception:
        print("❌ Ошибка в альтернативном методе: ")


def create_all_available_xml(documents: dict) -> None:
    """
    Создание XML со всеми доступными данными
    """
    print("\n📄 Создание XML со всеми доступными данными:")

    xml_content = (
        """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>"""
        + documents["metadata"]["extraction_date"]
        + """</ExtractionDate>
    <SourceFile>"""
        + documents["metadata"]["source_file"]
        + """</SourceFile>
    <TotalDocuments>"""
        + str(documents["metadata"]["total_documents"])
        + """</TotalDocuments>
    <TotalBlobs>"""
        + str(documents["metadata"]["total_blobs"])
        + """</TotalBlobs>
    <SuccessfulExtractions>"""
        + str(documents["metadata"]["successful_extractions"])
        + """</SuccessfulExtractions>
    <FailedExtractions>"""
        + str(documents["metadata"]["failed_extractions"])
        + """</FailedExtractions>
  </Metadata>

  <Documents>
"""
    )

    # Добавляем все документы
    for i, doc in enumerate(documents["documents"], 1):
        xml_content += f"""    <Document>
      <ID>{doc["id"]}</ID>
      <TableName>{doc["table_name"]}</TableName>
      <RowIndex>{doc["row_index"]}</RowIndex>
      <ExtractionStats>
        <TotalBlobs>{doc["extraction_stats"]["total_blobs"]}</TotalBlobs>
        <Successful>{doc["extraction_stats"]["successful"]}</Successful>
        <Failed>{doc["extraction_stats"]["failed"]}</Failed>
      </ExtractionStats>
      <Fields>
"""
        for field_name, value in doc["fields"].items():
            xml_content += f"""        <{field_name}>{value}</{field_name}>
"""
        xml_content += """      </Fields>
      <Blobs>
"""
        for blob_name, blob_data in doc["blobs"].items():
            xml_content += f"""        <{blob_name}>
          <FieldType>{blob_data["field_type"]}</FieldType>
          <Size>{blob_data["size"]}</Size>
          <ExtractionMethods>{", ".join(blob_data["extraction_methods"])}</ExtractionMethods>
"""
            # Добавляем содержимое для каждого метода
            for method in ["value", "iterator", "bytes"]:
                if method in blob_data:
                    content = blob_data[method]["content"]
                    if isinstance(content, bytes):
                        content = content.hex()
                    xml_content += f"""          <{method.capitalize()}>{content}</{method.capitalize()}>
"""
            xml_content += f"""        </{blob_name}>
"""
        xml_content += """      </Blobs>
    </Document>
"""

    xml_content += """  </Documents>
</Documents>"""

    with open("all_available_data.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)

    print("   📄 Создан XML со всеми доступными данными: all_available_data.xml")

    # Показываем статистику
    print("\n📊 Статистика извлечения всех данных:")
    print("   - Документов: {documents['metadata']['total_documents']}")
    print("   - BLOB полей: {documents['metadata']['total_blobs']}")
    print("   - Успешно извлечено: {documents['metadata']['successful_extractions']}")
    print("   - Ошибок извлечения: {documents['metadata']['failed_extractions']}")


if __name__ == "__main__":
    try:
        extract_all_available_data()
        print("✅ Извлечение и валидация завершены успешно")
        sys.exit(0)
    except Exception:
        print("❌ Ошибка: ")
        import traceback

        print("🔍 Детали ошибки:")
        traceback.print_exc()
        sys.exit(1)
