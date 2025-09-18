#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Адаптивный извлекатель для разных типов таблиц 1С
"""

import logging
import os
import sys
import time
from datetime import datetime

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "tools", "onec_dtools")
)

import json
from typing import Any, Dict, List, Optional

from onec_dtools.database_reader import DatabaseReader

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("extraction_progress.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Импорты для Parquet и DuckDB
try:
    import duckdb
    import pandas as pd
    import pyarrow as pa  # noqa: F401
    import pyarrow.parquet as pq  # noqa: F401

    PARQUET_DUCKDB_AVAILABLE = True
except ImportError:
    PARQUET_DUCKDB_AVAILABLE = False
    logger.warning(
        "⚠️ Parquet/DuckDB не установлены. Установите: pip install pandas pyarrow duckdb"
    )


class AdaptiveExtractor:
    """Адаптивный извлекатель для разных типов таблиц"""

    def __init__(self) -> None:
        self.business_fields = {"_NUMBER", "_DATE_TIME", "_POSTED", "_MARKED"}

        # Статистика извлечения
        self.extraction_stats = {
            "total_records_processed": 0,
            "successful_records": 0,
            "failed_records": 0,
            "blob_errors": 0,
            "start_time": time.time(),
            "last_checkpoint": 0,
        }

        # Маппинг полей для разных типов таблиц
        self.field_mapping = {
            "_DOCUMENTJOURNAL5354": {
                "amount_fields": [],  # Нет полей с суммами
                "quantity_fields": [],
                "blob_fields": ["_FLD5363"],
            },
            "_DOCUMENTJOURNAL5287": {
                "amount_fields": [],
                "quantity_fields": [],
                "blob_fields": ["_FLD5299"],
            },
            "_DOCUMENTJOURNAL5321": {
                "amount_fields": ["_FLD5326"],
                "quantity_fields": ["_FLD5330", "_FLD5333", "_FLD5334"],
                "blob_fields": ["_FLD5336"],
            },
            "_DOCUMENT138": {
                "amount_fields": [],
                "quantity_fields": ["_FLD3111", "_FLD3112", "_FLD3113"],
                "blob_fields": ["_FLD3108"],
            },
            "_DOCUMENT156": {
                "amount_fields": ["_FLD3978"],
                "quantity_fields": ["_FLD3983", "_FLD3984", "_FLD3988"],
                "blob_fields": ["_FLD3980", "_FLD3981", "_FLD3982", "_FLD3986"],
            },
        }

    def analyze_table_structure(
        self, table_name: str, row_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализирует структуру таблицы и определяет бизнес-поля"""
        analysis: Dict[str, Any] = {
            "table_name": table_name,
            "total_fields": len(row_dict),
            "business_fields": {},
            "amount_fields": [],
            "quantity_fields": [],
            "blob_fields": [],
            "date_fields": [],
        }

        # Анализируем каждое поле
        for key, value in row_dict.items():
            # Базовые бизнес-поля
            if key in self.business_fields:
                analysis["business_fields"][key] = value

            # Поля с суммами (числовые значения > 100)
            elif isinstance(value, (int, float)) and value > 100:
                analysis["amount_fields"].append({"field": key, "value": value})

            # Поля с количествами (числовые значения <= 100)
            elif isinstance(value, (int, float)) and value <= 100:
                analysis["quantity_fields"].append({"field": key, "value": value})

            # BLOB поля
            elif hasattr(value, "__class__") and "Blob" in str(type(value)):
                analysis["blob_fields"].append(key)

            # Поля с датами
            elif "DATE" in key or "TIME" in key:
                analysis["date_fields"].append({"field": key, "value": value})

        return analysis

    def log_progress(
        self,
        table_name: str,
        current_record: int,
        total_records: int,
        error_count: int = 0,
    ) -> None:
        """Логирует прогресс извлечения с детальной информацией"""
        elapsed_time = time.time() - self.extraction_stats["start_time"]
        records_per_second = current_record / elapsed_time if elapsed_time > 0 else 0
        estimated_remaining = (
            (total_records - current_record) / records_per_second
            if records_per_second > 0
            else 0
        )

        progress_percent = (
            (current_record / total_records) * 100 if total_records > 0 else 0
        )

        logger.info(
            f"📊 {table_name}: {current_record:,}/{total_records:,} ({progress_percent:.1f}%) | "
            f"Скорость: {records_per_second:.1f} зап/сек | "
            f"Осталось: {estimated_remaining/60:.1f} мин | "
            f"Ошибки: {error_count}"
        )

        # Обновляем статистику
        self.extraction_stats["total_records_processed"] = current_record
        self.extraction_stats["last_checkpoint"] = current_record

    def log_error(
        self, table_name: str, record_index: int, error_type: str, error_message: str
    ) -> None:
        """Логирует ошибки с детальной информацией"""
        self.extraction_stats["failed_records"] += 1
        if "blob" in error_type.lower():
            self.extraction_stats["blob_errors"] += 1

        logger.error(f"❌ {table_name}[{record_index}]: {error_type} - {error_message}")

    def save_checkpoint(self, table_name: str, records: List[Dict[str, Any]]) -> None:
        """Сохраняет checkpoint для восстановления"""
        checkpoint_file = f"checkpoint_{table_name}_{len(records)}.json"
        try:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "table_name": table_name,
                        "records": records,
                        "timestamp": datetime.now().isoformat(),
                        "stats": self.extraction_stats,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            logger.info(f"💾 Checkpoint сохранен: {checkpoint_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения checkpoint: {str(e)}")

    def extract_blob_content(self, blob_obj: Any) -> Dict[str, Any]:
        """Извлекает содержимое BLOB поля"""
        blob_data: Dict[str, Any] = {
            "field_type": str(type(blob_obj)),
            "size": 0,
            "extraction_methods": [],
            "value": {"content": "", "type": "unknown", "length": 0},
        }

        try:
            # Безопасное извлечение через value атрибут
            if hasattr(blob_obj, "value"):
                try:
                    blob_value = blob_obj.value
                    if isinstance(blob_value, bytes):
                        # Пробуем разные кодировки
                        for encoding in ["utf-8", "cp1251", "latin1"]:
                            try:
                                content = blob_value.decode(encoding)
                                blob_data["value"] = {
                                    "content": content,
                                    "type": f"str_{encoding}",
                                    "length": len(content),
                                }
                                blob_data["extraction_methods"].append(
                                    f"value_{encoding}"
                                )
                                blob_data["size"] = len(blob_value)
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            # Если все кодировки не сработали, используем hex
                            blob_data["value"] = {
                                "content": blob_value.hex(),
                                "type": "hex",
                                "length": len(blob_value),
                            }
                            blob_data["extraction_methods"].append("value_hex")
                            blob_data["size"] = len(blob_value)
                    else:
                        # Если value не bytes, конвертируем в строку
                        blob_data["value"] = {
                            "content": str(blob_value),
                            "type": "str_direct",
                            "length": len(str(blob_value)),
                        }
                        blob_data["extraction_methods"].append("value_direct")
                        blob_data["size"] = len(str(blob_value))
                except StopIteration:
                    # StopIteration - это нормальное завершение итератора
                    blob_data["value"] = {
                        "content": "BLOB data (StopIteration)",
                        "type": "blob_stopiteration",
                        "length": 0,
                    }
                    blob_data["extraction_methods"].append("stopiteration")
                    blob_data["size"] = 0
                except Exception as e:
                    # Другие ошибки при доступе к value
                    blob_data["value"] = {
                        "content": f"BLOB access error: {str(e)}",
                        "type": "blob_error",
                        "length": 0,
                    }
                    blob_data["extraction_methods"].append("value_error")
                    blob_data["size"] = 0
            else:
                # Если нет value атрибута, пробуем другие методы
                blob_data["value"] = {
                    "content": str(blob_obj),
                    "type": "str_object",
                    "length": len(str(blob_obj)),
                }
                blob_data["extraction_methods"].append("object_str")
                blob_data["size"] = len(str(blob_obj))

        except Exception as e:
            blob_data["error"] = f"Ошибка извлечения: {str(e)}"
            blob_data["value"] = {
                "content": f"ERROR: {str(e)}",
                "type": "error",
                "length": 0,
            }

        return blob_data

    def extract_table_data(
        self, table_name: str, table: Any, max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Извлекает данные из таблицы с адаптивной логикой"""
        print(f"   🔄 Извлечение {table_name}...")
        print(f"      📊 Всего записей: {len(table):,}")

        records = []
        successful_records = 0

        # Определяем лимит записей
        if max_records is None:
            max_records = len(table)
        else:
            max_records = min(max_records, len(table))

        print(f"      🎯 Извлекаем {max_records:,} записей...")
        logger.info(f"🚀 Начинаем извлечение {table_name}: {max_records:,} записей")

        error_count = 0

        for i in range(max_records):
            try:
                row = table[i]

                # Пропускаем пустые записи
                if hasattr(row, "is_empty") and row.is_empty:
                    continue

                # Извлекаем данные
                row_dict = row.as_dict() if hasattr(row, "as_dict") else {}
                if not row_dict:
                    continue

                # Анализируем структуру (только для первых записей)
                if i < 3:
                    analysis = self.analyze_table_structure(table_name, row_dict)
                    logger.info(
                        f"🔍 Анализ записи {i}: {analysis['total_fields']} полей, "
                        f"{len(analysis['amount_fields'])} сумм, "
                        f"{len(analysis['quantity_fields'])} количеств, "
                        f"{len(analysis['blob_fields'])} BLOB"
                    )

                # Создаем запись
                record: Dict[str, Any] = {
                    "id": f"{table_name}_{i+1}",
                    "table_name": table_name,
                    "row_index": i + 1,
                    "fields": {},
                    "blobs": {},
                    "extraction_stats": {
                        "total_blobs": 0,
                        "successful": 0,
                        "failed": 0,
                    },
                }

                # Извлекаем бизнес-поля
                for key, value in row_dict.items():
                    if key in self.business_fields:
                        record["fields"][key] = value

                # Извлекаем поля с суммами
                for key, value in row_dict.items():
                    if isinstance(value, (int, float)) and value > 100:
                        record["fields"][f"amount_{key}"] = value

                # Извлекаем поля с количествами
                for key, value in row_dict.items():
                    if isinstance(value, (int, float)) and value <= 100:
                        record["fields"][f"quantity_{key}"] = value

                # Извлекаем BLOB поля с детальным логированием
                for key, value in row_dict.items():
                    if hasattr(value, "__class__") and "Blob" in str(type(value)):
                        try:
                            blob_data = self.extract_blob_content(value)
                            record["blobs"][key] = blob_data
                            record["extraction_stats"]["total_blobs"] += 1
                            if blob_data.get("extraction_methods"):
                                record["extraction_stats"]["successful"] += 1
                            else:
                                record["extraction_stats"]["failed"] += 1
                        except StopIteration:
                            # StopIteration - это нормальное завершение итератора
                            blob_data = {
                                "field_type": str(type(value)),
                                "size": 0,
                                "extraction_methods": ["stopiteration"],
                                "value": {
                                    "content": "BLOB data (StopIteration)",
                                    "type": "blob_stopiteration",
                                    "length": 0,
                                },
                            }
                            record["blobs"][key] = blob_data
                            record["extraction_stats"]["total_blobs"] += 1
                            record["extraction_stats"]["successful"] += 1
                            logger.debug(f"✅ BLOB {key} обработан (StopIteration)")
                        except Exception as e:
                            # Другие ошибки при извлечении BLOB
                            error_count += 1
                            self.log_error(table_name, i, "BLOB_ERROR", str(e))
                            blob_data = {
                                "field_type": str(type(value)),
                                "size": 0,
                                "extraction_methods": [],
                                "value": {
                                    "content": f"BLOB extraction error: {str(e)}",
                                    "type": "blob_error",
                                    "length": 0,
                                },
                                "error": f"Ошибка извлечения: {str(e)}",
                            }
                            record["blobs"][key] = blob_data
                            record["extraction_stats"]["total_blobs"] += 1
                            record["extraction_stats"]["failed"] += 1

                records.append(record)
                successful_records += 1
                self.extraction_stats["successful_records"] += 1

                # Мониторинг прогресса каждые 1000 записей
                if i > 0 and i % 1000 == 0:
                    self.log_progress(table_name, i, max_records, error_count)

                # Сохраняем checkpoint каждые 10000 записей
                if i > 0 and i % 10000 == 0:
                    self.save_checkpoint(table_name, records)

            except Exception as e:
                error_count += 1
                self.log_error(table_name, i, "RECORD_ERROR", str(e))
                self.extraction_stats["failed_records"] += 1
                continue

        # Финальная статистика
        elapsed_time = time.time() - self.extraction_stats["start_time"]
        logger.info(
            f"✅ {table_name} завершена: {successful_records:,} записей за {elapsed_time/60:.1f} мин"
        )
        logger.info(
            f"📊 Статистика: {successful_records:,} успешных, {error_count} ошибок"
        )

        print(f"      ✅ Извлечено {successful_records:,} записей из {table_name}")
        return records

    def extract_critical_tables(
        self, db: DatabaseReader
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Извлекает критические таблицы"""
        critical_tables = [
            "_DOCUMENTJOURNAL5354",  # 4,458,509 записей
            "_DOCUMENTJOURNAL5287",  # 2,798,531 записей
            "_DOCUMENTJOURNAL5321",  # 973,975 записей
            "_DOCUMENT138",  # 861,178 записей
            "_DOCUMENT156",  # 571,213 записей
        ]

        results = {}

        for table_name in critical_tables:
            if table_name in db.tables:
                table = db.tables[table_name]

                # Извлекаем ВСЕ записи (полное извлечение)
                max_records = len(table)  # ВСЕ записи из таблицы

                records = self.extract_table_data(table_name, table, max_records)
                results[table_name] = records
            else:
                print(f"   ❌ Таблица {table_name} не найдена")

        return results

    def save_to_parquet(self, results: Dict[str, List[Dict[str, Any]]]) -> None:
        """Сохраняет результаты в Parquet формат"""
        if not PARQUET_DUCKDB_AVAILABLE:
            logger.error("❌ Parquet/DuckDB не доступны")
            return

        try:
            logger.info("💾 Сохранение в Parquet формат...")

            # Создаем DataFrame для каждой таблицы
            parquet_files = {}

            for table_name, records in results.items():
                if not records:
                    continue

                # Преобразуем записи в DataFrame
                df_data = []
                for record in records:
                    row_data = {
                        "id": record.get("id"),
                        "table_name": record.get("table_name"),
                        "row_index": record.get("row_index"),
                    }

                    # Добавляем поля
                    for key, value in record.get("fields", {}).items():
                        row_data[f"field_{key}"] = value

                    # Добавляем BLOB поля (только метаданные)
                    for key, blob_data in record.get("blobs", {}).items():
                        row_data[f"blob_{key}_size"] = blob_data.get("size", 0)
                        row_data[f"blob_{key}_type"] = blob_data.get("value", {}).get(
                            "type", "unknown"
                        )

                    # Добавляем статистику извлечения
                    stats = record.get("extraction_stats", {})
                    row_data["total_blobs"] = stats.get("total_blobs", 0)
                    row_data["successful_blobs"] = stats.get("successful", 0)
                    row_data["failed_blobs"] = stats.get("failed", 0)

                    df_data.append(row_data)

                if df_data:
                    df = pd.DataFrame(df_data)
                    parquet_file = f"complete_1c_database_{table_name}.parquet"
                    df.to_parquet(parquet_file, engine="pyarrow")
                    parquet_files[table_name] = parquet_file
                    logger.info(
                        f"✅ {table_name}: {len(df):,} записей → {parquet_file}"
                    )

            # Создаем основной Parquet файл
            if parquet_files:
                main_parquet = "complete_1c_database.parquet"
                logger.info(f"📊 Создание основного Parquet файла: {main_parquet}")
                # Здесь можно объединить все таблицы в один файл

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в Parquet: {str(e)}")

    def save_to_duckdb(self, results: Dict[str, List[Dict[str, Any]]]) -> None:
        """Сохраняет результаты в DuckDB"""
        if not PARQUET_DUCKDB_AVAILABLE:
            logger.error("❌ Parquet/DuckDB не доступны")
            return

        try:
            logger.info("💾 Создание DuckDB базы данных...")

            # Создаем DuckDB соединение
            conn = duckdb.connect("complete_1c_database.duckdb")

            for table_name, records in results.items():
                if not records:
                    continue

                logger.info(f"📊 Создание таблицы {table_name} в DuckDB...")

                # Преобразуем записи в DataFrame
                df_data = []
                for record in records:
                    row_data = {
                        "id": record.get("id"),
                        "table_name": record.get("table_name"),
                        "row_index": record.get("row_index"),
                    }

                    # Добавляем поля
                    for key, value in record.get("fields", {}).items():
                        row_data[f"field_{key}"] = value

                    # Добавляем BLOB поля (только метаданные)
                    for key, blob_data in record.get("blobs", {}).items():
                        row_data[f"blob_{key}_size"] = blob_data.get("size", 0)
                        row_data[f"blob_{key}_type"] = blob_data.get("value", {}).get(
                            "type", "unknown"
                        )

                    # Добавляем статистику извлечения
                    stats = record.get("extraction_stats", {})
                    row_data["total_blobs"] = stats.get("total_blobs", 0)
                    row_data["successful_blobs"] = stats.get("successful", 0)
                    row_data["failed_blobs"] = stats.get("failed", 0)

                    df_data.append(row_data)

                if df_data:
                    df = pd.DataFrame(df_data)
                    # Создаем таблицу в DuckDB
                    conn.register(f"df_{table_name}", df)
                    conn.execute(
                        f"CREATE TABLE {table_name} AS SELECT * FROM df_{table_name}"
                    )
                    logger.info(f"✅ {table_name}: {len(df):,} записей → DuckDB")

            # Создаем индексы для быстрого поиска
            logger.info("🔍 Создание индексов...")
            for table_name in results.keys():
                try:
                    conn.execute(
                        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_id ON {table_name}(id)"
                    )
                    conn.execute(
                        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_table ON {table_name}(table_name)"
                    )
                except Exception as e:
                    logger.warning(
                        f"⚠️ Не удалось создать индекс для {table_name}: {str(e)}"
                    )

            conn.close()
            logger.info("✅ DuckDB база данных создана: complete_1c_database.duckdb")

        except Exception as e:
            logger.error(f"❌ Ошибка создания DuckDB: {str(e)}")


def main() -> None:
    """Основная функция адаптивного извлечения"""
    print("🔍 Адаптивное извлечение критических таблиц")
    print("=" * 60)

    try:
        db_file = open("data/raw/1Cv8.1CD", "rb")
        db = DatabaseReader(db_file)

        print("✅ База данных открыта успешно!")

        # Создаем адаптивный извлекатель
        extractor = AdaptiveExtractor()

        # Извлекаем критические таблицы
        print("\n🎯 Извлечение критических таблиц...")
        results = extractor.extract_critical_tables(db)

        # Сохраняем результаты в JSON
        output_file = "adaptive_extraction_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n✅ Результаты сохранены в {output_file}")

        # Сохраняем в Parquet и DuckDB
        print("\n💾 Сохранение в оптимизированные форматы...")
        extractor.save_to_parquet(results)
        extractor.save_to_duckdb(results)

        # Статистика
        total_records = sum(len(records) for records in results.values())
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   📄 Извлечено {total_records:,} записей из {len(results)} таблиц")

        for table_name, records in results.items():
            print(f"   📄 {table_name}: {len(records):,} записей")

        print("\n✅ Извлечение завершено успешно")
        print("📁 Созданные файлы:")
        print("   📄 adaptive_extraction_results.json - полные данные")
        print("   📊 complete_1c_database_*.parquet - оптимизированные таблицы")
        print("   🗄️ complete_1c_database.duckdb - индексированная база данных")

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
