#!/usr/bin/env python3
"""
DocumentExtractor - извлекатель документов из 1С базы данных
Создан для извлечения реальных документов в формате, соответствующем тест-кейсам
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

from ..processors.database_connector import DatabaseConnector
from .base_extractor import BaseExtractor


class DocumentExtractor(BaseExtractor):
    """
    JTBD:
    Как извлекатель документов, я хочу извлекать данные из документов 1С,
    чтобы предоставить структурированную информацию о цветочном бизнесе.
    Примеры документов:
    - ФЛОРИСТИКА, ДЕКОР, МОНО БУКЕТ, ИНТЕРНЕТ-ЗАКАЗ
    - Документы поступления, продажи, перемещения
    - Документы с данными о цветах, магазинах, финансах
    """

    def __init__(self, db_path: str):
        """
        Инициализация извлекателя документов.

        Args:
            db_path: Путь к файлу базы данных 1C
        """
        db_connector = DatabaseConnector(db_path)
        super().__init__(db_connector)

        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        self.documents_data: list[dict[str, Any]] = []
        self.extraction_stats: dict[str, Any] = {
            "total_documents": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extraction_errors": [],
        }

    def extract(self, table_name: str, limit: int = 100) -> list[dict]:
        """
        Реализация абстрактного метода extract из BaseExtractor.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество элементов для извлечения

        Returns:
            Список извлеченных документов
        """
        try:
            if (
                not hasattr(self.db_connector, "_file_handle")
                or self.db_connector._file_handle is None
            ):
                self.db_connector.connect()

            table = self.db_connector.get_table(table_name)
            if not table:
                return []

            extracted_data = []

            for i, row in enumerate(table):
                if i >= limit:
                    break

                processed_row = self.process_document_row(row, i, table_name)
                if processed_row:
                    extracted_data.append(processed_row)

            return extracted_data

        except Exception as e:
            self.log_extraction_error(e, {"table_name": table_name, "limit": limit})
            return []

    def extract_documents(self) -> dict[str, Any]:
        """
        Извлекает все документы из базы данных.

        Returns:
            Словарь с результатами извлечения документов
        """
        try:
            self.logger.info("🔍 Начинаю извлечение документов...")

            self.db_connector.connect()

            all_tables = self.db_connector.get_tables()
            self.logger.info(f"📊 Найдено таблиц: {len(all_tables)}")

            document_tables = self._filter_document_tables(all_tables)
            self.logger.info(f"📊 Найдено документов: {len(document_tables)}")

            for table_name, table_info in document_tables.items():
                self.logger.info(f"🔍 Извлекаю документы: {table_name}")
                try:
                    extracted_items = self._extract_single_document_table(table_name)

                    if extracted_items:
                        self.documents_data.extend(extracted_items)
                        self.extraction_stats["successful_extractions"] += 1
                    else:
                        self.extraction_stats["failed_extractions"] += 1
                        self.extraction_stats["extraction_errors"].append(
                            f"Не удалось извлечь {table_name}",
                        )
                except Exception as e:
                    self.logger.error(f"❌ Ошибка при извлечении {table_name}: {e}")
                    self.extraction_stats["failed_extractions"] += 1
                    self.extraction_stats["extraction_errors"].append(
                        f"Ошибка в {table_name}: {e!s}",
                    )

            self.extraction_stats["total_documents"] = len(document_tables)

            result = {
                "extraction_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_documents": self.extraction_stats["total_documents"],
                    "successful_extractions": self.extraction_stats[
                        "successful_extractions"
                    ],
                    "failed_extractions": self.extraction_stats["failed_extractions"],
                },
                "documents": self.documents_data,
                "extraction_stats": self.extraction_stats,
            }

            self.logger.info(
                f"✅ Извлечение завершено: {self.extraction_stats['successful_extractions']}/{self.extraction_stats['total_documents']} документов",
            )
            return result

        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка при извлечении документов: {e}")
            raise
        finally:
            self.db_connector.close()

    def _filter_document_tables(self, all_tables: dict[str, Any]) -> dict[str, Any]:
        """
        Фильтрует таблицы, оставляя только документы.

        Args:
            all_tables: Словарь всех таблиц

        Returns:
            Словарь документов
        """
        document_tables = {}

        for table_name, table_info in all_tables.items():
            if (
                any(
                    pattern in table_name.upper()
                    for pattern in ["_DOCUMENT", "DOCUMENT_"]
                )
                and "_VT" not in table_name.upper()
            ):
                document_tables[table_name] = table_info

        return document_tables

    def _extract_single_document_table(self, table_name: str) -> list[dict[str, Any]]:
        """
        Извлекает документы из одной таблицы.

        Args:
            table_name: Имя таблицы документов

        Returns:
            Список документов
        """
        try:
            if (
                not hasattr(self.db_connector, "_file_handle")
                or self.db_connector._file_handle is None
            ):
                self.db_connector.connect()

            table = self.db_connector.get_table(table_name)
            if not table:
                return []

            documents = []

            # Извлекаем первые 5 документов для анализа
            for i, record in enumerate(table):
                if i >= 5:
                    break

                try:
                    document = self._extract_single_document(record, i, table_name)
                    if document:
                        documents.append(document)
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка при извлечении документа {i}: {e}")
                    continue

            return documents

        except Exception as e:
            self.logger.error(f"❌ Ошибка при извлечении {table_name}: {e}")
            return []

    def _extract_single_document(
        self,
        record: Any,
        index: int,
        table_name: str,
    ) -> dict[str, Any] | None:
        """
        Извлекает один документ.

        Args:
            record: Запись из таблицы
            index: Индекс записи
            table_name: Имя таблицы

        Returns:
            Данные документа или None
        """
        try:
            if not hasattr(record, "as_list"):
                return None

            record_list = record.as_list(True)
            document = {
                "id": f"{table_name}_{index}",
                "table_name": table_name,
                "document_type": self._determine_document_type(table_name),
                "document_number": self._extract_field_value(record_list, "_NUMBER"),
                "document_date": self._extract_field_value(record_list, "_DATE"),
                "store_name": self._extract_field_value(record_list, "_STORE"),
                "store_code": self._extract_field_value(record_list, "_STORE_CODE"),
                "total_amount": self._extract_field_value(record_list, "_AMOUNT"),
                "currency": "RUB",
                "supplier_name": self._extract_field_value(record_list, "_SUPPLIER"),
                "buyer_name": self._extract_field_value(record_list, "_BUYER"),
                "goods_received": self._extract_goods_data(record_list, "received"),
                "goods_not_received": self._extract_goods_data(
                    record_list,
                    "not_received",
                ),
                "flower_names": self._extract_flower_names(record_list),
                "flower_quantities": self._extract_flower_quantities(record_list),
                "flower_prices": self._extract_flower_prices(record_list),
                "blob_content": self._extract_blob_content(record_list),
                "table_parts": self._extract_table_parts(table_name, index),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            return document

        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при извлечении документа: {e}")
            return None

    def _determine_document_type(self, table_name: str) -> str:
        """
        Определяет тип документа по имени таблицы.

        Args:
            table_name: Имя таблицы

        Returns:
            Тип документа
        """
        type_mapping = {
            "ФЛОРИСТИКА": ["флористика", "florist", "цветы"],
            "ДЕКОР": ["декор", "decor", "украшение"],
            "МОНО БУКЕТ": ["моно", "mono", "букет"],
            "ИНТЕРНЕТ-ЗАКАЗ": ["интернет", "internet", "заказ"],
        }

        table_lower = table_name.lower()
        for doc_type, keywords in type_mapping.items():
            if any(keyword in table_lower for keyword in keywords):
                return doc_type

        return "НЕИЗВЕСТНЫЙ ДОКУМЕНТ"

    def _extract_field_value(self, record_list: list, field_name: str) -> Any:
        """
        Извлекает значение поля из записи.

        Args:
            record_list: Список полей записи
            field_name: Имя поля

        Returns:
            Значение поля
        """
        try:
            for field in record_list:
                if hasattr(field, "name") and field.name == field_name:
                    if hasattr(field, "value"):
                        return field.value
                    return str(field)
            return None
        except:
            return None

    def _extract_goods_data(self, record_list: list, goods_type: str) -> dict[str, Any]:
        """
        Извлекает данные о товарах.

        Args:
            record_list: Список полей записи
            goods_type: Тип товаров (received/not_received)

        Returns:
            Данные о товарах
        """
        # Упрощенная реализация - в реальности нужно анализировать табличные части
        return {"flowers": [], "quantities": [], "prices": []}

    def _extract_flower_names(self, record_list: list) -> list[str]:
        """
        Извлекает названия цветов.

        Args:
            record_list: Список полей записи

        Returns:
            Список названий цветов
        """
        flower_names = []
        for field in record_list:
            if hasattr(field, "value") and field.value:
                field_str = str(field.value).lower()
                if any(
                    flower in field_str
                    for flower in [
                        "роза",
                        "rose",
                        "тюльпан",
                        "tulip",
                        "хризантема",
                        "chrysanthemum",
                    ]
                ):
                    flower_names.append(str(field.value))
        return flower_names

    def _extract_flower_quantities(self, record_list: list) -> list[float]:
        """
        Извлекает количества цветов.

        Args:
            record_list: Список полей записи

        Returns:
            Список количеств
        """
        quantities = []
        for field in record_list:
            if hasattr(field, "value") and field.value:
                try:
                    if isinstance(field.value, (int, float)):
                        quantities.append(float(field.value))
                except:
                    continue
        return quantities

    def _extract_flower_prices(self, record_list: list) -> list[float]:
        """
        Извлекает цены цветов.

        Args:
            record_list: Список полей записи

        Returns:
            Список цен
        """
        prices = []
        for field in record_list:
            if hasattr(field, "value") and field.value:
                try:
                    if isinstance(field.value, (int, float)):
                        prices.append(float(field.value))
                except:
                    continue
        return prices

    def _extract_blob_content(self, record_list: list) -> str:
        """
        Извлекает содержимое BLOB полей.

        Args:
            record_list: Список полей записи

        Returns:
            Содержимое BLOB полей
        """
        blob_content = []
        for field in record_list:
            if hasattr(field, "value") and isinstance(field.value, bytes):
                try:
                    decoded = field.value.decode("utf-8", errors="ignore")
                    blob_content.append(decoded)
                except:
                    blob_content.append(str(field.value))
        return " ".join(blob_content)

    def _extract_table_parts(
        self,
        table_name: str,
        document_index: int,
    ) -> dict[str, Any]:
        """
        Извлекает табличные части документа.

        Args:
            table_name: Имя таблицы
            document_index: Индекс документа

        Returns:
            Табличные части
        """
        # Упрощенная реализация - в реальности нужно извлекать из _VT таблиц
        return {"nomenclature": [], "quantities": [], "prices": []}

    def save_results(
        self,
        results: list[dict[str, Any]] | None = None,
        output_path: str = "data/results/documents_extraction.json",
    ) -> str:
        """
        Сохраняет результаты извлечения документов.

        Args:
            output_path: Путь для сохранения результатов

        Returns:
            Путь к сохраненному файлу
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Используем переданные результаты или внутренние данные
            data_to_save = results if results is not None else self.documents_data

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 Результаты сохранены: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении результатов: {e}")
            raise

    def save_to_parquet(
        self,
        output_path: str = "data/results/parquet/documents_extraction.parquet",
    ) -> str:
        """
        Сохраняет результаты в Parquet формат для совместимости с notebook.

        Args:
            output_path: Путь для сохранения Parquet файла

        Returns:
            Путь к сохраненному файлу
        """
        try:
            import pandas as pd
            import pyarrow as pa
            import pyarrow.parquet as pq

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            df = pd.DataFrame(self.documents_data)

            # ИСПРАВЛЕНО: Правильное сохранение BLOB данных как binary
            table_data = {}
            for col in df.columns:
                if df[col].dtype == "object":
                    # Проверяем, содержит ли колонка BLOB данные
                    blob_data = []
                    for val in df[col]:
                        if isinstance(val, bytes):
                            blob_data.append(val)
                        elif (
                            isinstance(val, str)
                            and val.startswith("b'")
                            and val.endswith("'")
                        ):
                            # Восстанавливаем bytes из строкового представления
                            try:
                                import ast

                                blob_data.append(ast.literal_eval(val))
                            except:
                                blob_data.append(b"")
                        else:
                            blob_data.append(b"")

                    # Сохраняем как binary колонку
                    table_data[col] = pa.array(blob_data, type=pa.binary())
                else:
                    # Обычные поля как строки
                    table_data[col] = pa.array(df[col].astype(str))

            # Создаем PyArrow Table
            table = pa.table(table_data)

            # Сохраняем с правильными типами
            pq.write_table(table, output_path)
            self.logger.info(f"💾 Parquet результаты сохранены: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении Parquet: {e}")
            raise

    def get_extraction_summary(self) -> dict[str, Any]:
        """
        Возвращает сводку по извлечению документов.

        Returns:
            Словарь со статистикой извлечения
        """
        return {
            "total_documents": self.extraction_stats["total_documents"],
            "successful_extractions": self.extraction_stats["successful_extractions"],
            "failed_extractions": self.extraction_stats["failed_extractions"],
            "success_rate": (
                self.extraction_stats["successful_extractions"]
                / max(int(self.extraction_stats["total_documents"]), 1)
                * 100
            ),
            "extraction_errors": self.extraction_stats["extraction_errors"],
        }
