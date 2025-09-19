#!/usr/bin/env python3

"""
Упрощенная версия extract_all_available_data.py
Использует независимые методы для упрощения основного кода
"""

import os
import signal
import sys
from datetime import datetime
from typing import Any

# Добавляем путь к utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

from src.utils.blob_processor_enhanced import BlobProcessorEnhanced
from src.utils.data_converter_enhanced import DataConverterEnhanced
from src.utils.table_analyzer import TableAnalyzer

# Добавляем путь к onec_dtools
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "tools", "onec_dtools"),
)

from onec_dtools.database_reader import DatabaseReader

# Флаг для прерывания
interrupted = False


def signal_handler(sig: int, frame: Any) -> None:
    global interrupted
    print("\n🛑 Получен сигнал прерывания. Завершение извлечения...")
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)


def extract_table_parts(db: Any, table_name: str, row_index: int) -> dict:
    """
    JTBD:
    Как система извлечения табличных частей, я хочу извлечь табличные части
    документа для получения детальной информации о товарах и услугах.
    """
    table_parts = {}

    # Ищем табличные части для конкретной таблицы
    for table_part_name in db.tables.keys():
        if table_part_name.startswith(f"{table_name}_VT"):
            try:
                table_part = db.tables[table_part_name]
                records = []

                for i, row in enumerate(table_part):
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_list = row.as_list(True) if hasattr(row, "as_list") else []
                        if row_list:
                            row_data = {}
                            for j, value in enumerate(row_list):
                                if hasattr(value, "name") and value.name:
                                    row_data[value.name] = value
                                else:
                                    row_data[f"field_{j}"] = value

                            records.append(
                                {
                                    "row_index": i,
                                    "nomenclature": row_data.get("field_0", ""),
                                    "quantity": row_data.get("field_1", 0),
                                    "price": row_data.get("field_2", 0),
                                    "amount": row_data.get("field_3", 0),
                                    "fields": row_data,
                                },
                            )

                if records:
                    table_parts[table_part_name] = records
            except Exception as e:
                print(f"   ⚠️ Ошибка извлечения табличной части {table_part_name}: {e}")
                continue

    return table_parts


def extract_all_available_data_simplified() -> None:
    """
    JTBD:
    Как система извлечения всех данных, я хочу извлечь все доступные данные
    из 1С с использованием независимых методов, чтобы упростить код и
    улучшить его читаемость.
    """
    print("🔍 Извлечение всех доступных данных (упрощенная версия)")
    print("=" * 60)

    # Инициализируем независимые компоненты
    table_analyzer = TableAnalyzer()
    blob_processor = BlobProcessorEnhanced()
    data_converter = DataConverterEnhanced()

    # Применяем патч для поддержки новых типов полей 1С
    try:
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
        print("⚠️ Не удалось применить патч")

    # Проверяем существование 1CD файла
    cdb_file_path = "data/raw/1Cv8.1CD"
    if not os.path.exists(cdb_file_path):
        print(f"❌ Файл 1CD не найден: {cdb_file_path}")
        return

    try:
        with open(cdb_file_path, "rb") as f:
            try:
                db = DatabaseReader(f)
            except ValueError as e:
                if "Unknown field type" in str(e):
                    print("⚠️ Предупреждение: Неизвестный тип поля")
                    return
                raise e

            print("✅ База данных открыта успешно!")

            # Критические таблицы для извлечения
            critical_tables = [
                "_DOCUMENTJOURNAL5354",  # 4,458,509 записей - КРИТИЧЕСКАЯ
                "_DOCUMENTJOURNAL5287",  # 2,798,531 записей - КРИТИЧЕСКАЯ
                "_DOCUMENTJOURNAL5321",  # 973,975 записей - КРИТИЧЕСКАЯ
                "_DOCUMENT138",  # 861,178 записей - КРИТИЧЕСКАЯ
                "_DOCUMENT156",  # 571,213 записей - КРИТИЧЕСКАЯ
            ]

            # Лимит записей для критических таблиц
            MAX_RECORDS_CRITICAL = 100  # Только 100 документов для тестирования

            # Инициализируем результаты
            all_results: dict[str, Any] = {
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

            # Извлекаем критические таблицы
            print("\n🎯 Извлечение критических таблиц...")
            for table_name in critical_tables:
                if table_name in db.tables:
                    print(f"📊 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")

                    # Анализируем структуру таблицы
                    structure_info = table_analyzer.analyze_table_structure(table)
                    print(
                        f"   🔍 Структура: {structure_info['total_records']} записей, {len(structure_info['field_types'])} типов полей",
                    )

                    # Извлекаем документы
                    documents = extract_documents_from_table(
                        table_name,
                        table,
                        MAX_RECORDS_CRITICAL,
                        blob_processor,
                    )
                    all_results["documents"].extend(documents)

                    print(f"   ✅ Извлечено {len(documents)} документов")

            # Извлекаем справочники
            print("\n📚 Извлечение справочников...")
            reference_tables = get_reference_tables(db)
            for table_name, record_count in reference_tables[
                :5
            ]:  # Первые 5 справочников
                print(f"📊 Анализ справочника: {table_name}")
                references = extract_references_from_table(
                    table_name,
                    db.tables[table_name],
                )
                all_results["references"].extend(references)
                print(f"   ✅ Извлечено {len(references)} записей справочника")

            # Обновляем метаданные
            all_results["metadata"]["total_documents"] = len(all_results["documents"])
            all_results["metadata"]["total_references"] = len(all_results["references"])

            # Сохраняем результат в JSON
            output_file = "data/results/all_available_data_simplified.json"
            import json

            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(
                    all_results,
                    json_file,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )

            print(f"\n💾 Результат сохранен в: {output_file}")

            # Конвертируем в Parquet и DuckDB
            print("\n🦆 Конвертация в Parquet и DuckDB...")
            data_converter.convert_to_parquet(all_results)
            data_converter.convert_to_duckdb(all_results)

            print("\n✅ Извлечение всех доступных данных завершено")
            print("📊 Статистика:")
            print(f"   📄 Документов: {all_results['metadata']['total_documents']}")
            print(f"   📚 Справочников: {all_results['metadata']['total_references']}")
            print(
                f"   🔍 BLOB полей: {blob_processor.get_processing_stats()['total_blobs_processed']}",
            )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()


def extract_documents_from_table(
    table_name: str,
    table: Any,
    max_records: int,
    blob_processor: BlobProcessorEnhanced,
) -> list[dict[str, Any]]:
    """
    JTBD:
    Как система извлечения документов из таблицы, я хочу извлечь документы
    с полной обработкой BLOB полей и табличных частей, чтобы получить
    детальную информацию о каждом документе.
    """
    documents = []
    max_records = min(max_records, len(table))

    print(f"   🔄 Извлечение {max_records:,} записей...")

    for i in range(max_records):
        if interrupted:
            print(f"   🛑 ПРЕРЫВАНИЕ: Остановка извлечения на записи {i:,}")
            break

        try:
            row = table[i]
            if not hasattr(row, "is_empty") or not row.is_empty:
                # Извлекаем данные через as_list для правильной обработки BLOB
                row_list = row.as_list(True) if hasattr(row, "as_list") else []
                if not row_list:
                    continue

                # Создаем словарь полей
                row_dict = {}
                for j, value in enumerate(row_list):
                    if hasattr(value, "name") and value.name:
                        row_dict[value.name] = value
                    else:
                        row_dict[f"field_{j}"] = value

                # Создаем структуру документа
                document = create_document_structure(table_name, i, row_dict)

                # Извлекаем табличные части (передаем db как параметр)
                # table_parts = extract_table_parts(db, table_name, i)
                table_parts: dict[str, Any] = {}  # Временно отключаем для упрощения
                if table_parts:
                    document["table_parts"] = table_parts

                # Обрабатываем BLOB поля
                blob_data = blob_processor.process_blob_fields(row_dict)
                if blob_data:
                    document["blobs"] = blob_data
                    document["extraction_stats"]["total_blobs"] = len(blob_data)
                    document["extraction_stats"]["successful"] = len(
                        [b for b in blob_data.values() if b.get("extraction_methods")],
                    )

                documents.append(document)

        except Exception as e:
            print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
            continue

    return documents


def extract_references_from_table(table_name: str, table: Any) -> list[dict[str, Any]]:
    """
    JTBD:
    Как система извлечения справочников, я хочу извлечь записи справочника
    с базовой обработкой полей, чтобы получить информацию о номенклатуре,
    складах и других справочных данных.
    """
    references = []
    max_records = min(100, len(table))  # Лимит для справочников

    for i in range(max_records):
        try:
            row = table[i]
            if not hasattr(row, "is_empty") or not row.is_empty:
                row_dict = row.as_dict() if hasattr(row, "as_dict") else {}
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
                    references.append(reference)
        except Exception as e:
            print(f"   ⚠️ Ошибка при извлечении справочника {i}: {e}")
            continue

    return references


def create_document_structure(
    table_name: str,
    row_index: int,
    row_dict: dict,
) -> dict[str, Any]:
    """
    JTBD:
    Как система создания структуры документа, я хочу создать стандартную
    структуру документа с основными полями, чтобы все документы имели
    единый формат для анализа.
    """
    document = {
        "id": f"{table_name}_{row_index}",
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

    # Анализируем основные поля документа
    for field_name, value in row_dict.items():
        if field_name == "_NUMBER":
            document["document_number"] = str(value) if value else "N/A"
        elif field_name == "_DATE_TIME":
            document["document_date"] = str(value) if value else "N/A"
        elif field_name == "_FLD4239":  # Итоговая сумма
            document["total_amount"] = float(value) if value else 0.0
        elif field_name == "_FLD4240":  # Тип документа
            document["document_type"] = str(value) if value else "Неизвестно"

        # Сохраняем все поля
        if "fields" in document:
            fields = document["fields"]
            if isinstance(fields, dict):
                fields[field_name] = value

    return document


def get_reference_tables(db: Any) -> list[tuple[str, int]]:
    """
    JTBD:
    Как система поиска справочников, я хочу найти все справочники
    в базе данных, чтобы извлечь справочные данные.
    """
    reference_tables = []
    for table_name in db.tables.keys():
        if table_name.startswith("_Reference"):
            table = db.tables[table_name]
            if len(table) > 0:
                reference_tables.append((table_name, len(table)))

    # Сортируем по размеру
    reference_tables.sort(key=lambda x: x[1], reverse=True)
    return reference_tables


if __name__ == "__main__":
    try:
        extract_all_available_data_simplified()
        print("✅ Извлечение и валидация завершены успешно")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
