#!/usr/bin/env python3
"""
FlatTableExtractor - извлекатель плоской таблицы с сущностями из 1С
Создан для создания плоской таблицы где каждая строка = одна сущность из документа
ИСПРАВЛЕН: Интегрирован маппинг полей и исправлена обработка BLOB данных
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "processors"))

from extractors.base_extractor import BaseExtractor
from processors.database_connector import DatabaseConnector

# Импортируем маппинг функций из extract_all_available_data.py
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from extract_all_available_data import (
    get_field_mapping,
    get_field_mapping_by_index,
)


class FlatTableExtractor(BaseExtractor):
    """
    JTBD:
    Как извлекатель плоской таблицы, я хочу создать таблицу где каждая строка = одна сущность,
    чтобы можно было анализировать цветочный бизнес на уровне отдельных объектов.

    Структура плоской таблицы:
    - Каждая строка = одна сущность (цветок, товар, операция)
    - Каждый документ = несколько строк (по количеству сущностей)
    - Все сущности в едином формате для анализа
    """

    def __init__(self, db_path: str):
        """
        Инициализация извлекателя плоской таблицы.

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

        self.flat_data = []
        self.extraction_stats = {
            "total_documents": 0,
            "total_entities": 0,
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
            Список извлеченных сущностей
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

            extracted_entities = []

            for i, row in enumerate(table):
                if i >= limit:
                    break

                entities = self.process_document_row(row, i, table_name)
                if entities:
                    extracted_entities.extend(entities)

            return extracted_entities

        except Exception as e:
            self.log_extraction_error(e, {"table_name": table_name, "limit": limit})
            return []

    def extract_flat_table(self) -> dict[str, Any]:
        """
        JTBD: Как извлекатель плоской таблицы, я хочу создать полную таблицу
        со ВСЕМИ сущностями и полями из документов, чтобы обеспечить максимальную
        информативность для анализа цветочного бизнеса.

        КРИТИЧЕСКИ ВАЖНО: Извлекаем ВСЕ поля из ВСЕХ документов, даже неизвестные,
        чтобы создать полную картину данных для последующего маппинга и анализа.

        Извлекает плоскую таблицу со всеми сущностями.

        Returns:
            Словарь с результатами извлечения плоской таблицы
        """
        try:
            self.logger.info("🔍 Начинаю извлечение плоской таблицы...")

            self.db_connector.connect()

            all_tables = self.db_connector.get_tables()
            self.logger.info(f"📊 Найдено таблиц: {len(all_tables)}")

            document_tables = self._filter_document_tables(all_tables)
            self.logger.info(f"📊 Найдено документов: {len(document_tables)}")

            for table_name, table_info in document_tables.items():
                self.logger.info(f"🔍 Извлекаю сущности: {table_name}")
                try:
                    entities = self._extract_entities_from_document(table_name)

                    if entities:
                        self.flat_data.extend(entities)
                        self.extraction_stats["successful_extractions"] += 1
                        self.extraction_stats["total_entities"] += len(entities)
                    else:
                        self.extraction_stats["failed_extractions"] += 1
                        self.extraction_stats["extraction_errors"].append(
                            f"Не удалось извлечь сущности из {table_name}",
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
                    "total_entities": self.extraction_stats["total_entities"],
                    "successful_extractions": self.extraction_stats[
                        "successful_extractions"
                    ],
                    "failed_extractions": self.extraction_stats["failed_extractions"],
                },
                "flat_data": self.flat_data,
                "extraction_stats": self.extraction_stats,
            }

            self.logger.info(
                f"✅ Извлечение завершено: {self.extraction_stats['total_entities']} сущностей из {self.extraction_stats['successful_extractions']} документов",
            )
            return result

        except Exception as e:
            self.logger.error(
                f"❌ Критическая ошибка при извлечении плоской таблицы: {e}",
            )
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

    def _extract_entities_from_document(self, table_name: str) -> list[dict[str, Any]]:
        """
        Извлекает сущности из одного документа.

        Args:
            table_name: Имя таблицы документов

        Returns:
            Список сущностей
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

            entities = []

            # Извлекаем первые 3 документа для анализа
            for i, record in enumerate(table):
                if i >= 3:
                    break

                try:
                    document_entities = self._extract_entities_from_record(
                        record,
                        i,
                        table_name,
                    )
                    if document_entities:
                        entities.extend(document_entities)
                except Exception as e:
                    self.logger.warning(
                        f"⚠️ Ошибка при извлечении сущностей из документа {i}: {e}",
                    )
                    continue

            return entities

        except Exception as e:
            self.logger.error(
                f"❌ Ошибка при извлечении сущностей из {table_name}: {e}",
            )
            return []

    def _extract_entities_from_record(
        self,
        record,
        index: int,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """
        Извлекает сущности из одной записи документа.

        Args:
            record: Запись из таблицы
            index: Индекс записи
            table_name: Имя таблицы

        Returns:
            Список сущностей
        """
        try:
            if not hasattr(record, "as_list"):
                return []

            record_list = record.as_list(True)
            entities = []

            # Создаем базовую сущность документа
            base_entity = self._create_base_entity(record_list, index, table_name)
            entities.append(base_entity)

            # Извлекаем сущности товаров/цветов
            flower_entities = self._extract_flower_entities(
                record_list,
                index,
                table_name,
            )
            entities.extend(flower_entities)

            # Извлекаем сущности операций
            operation_entities = self._extract_operation_entities(
                record_list,
                index,
                table_name,
            )
            entities.extend(operation_entities)

            return entities

        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при извлечении сущностей из записи: {e}")
            return []

    def _create_base_entity(
        self,
        record_list: list,
        index: int,
        table_name: str,
    ) -> dict[str, Any]:
        """
        JTBD: Как создатель базовой сущности, я хочу создать полную запись документа
        со ВСЕМИ полями, чтобы обеспечить максимальную информативность для анализа.

        КРИТИЧЕСКИ ВАЖНО: Включаем ВСЕ поля из документа, даже неизвестные,
        чтобы создать полную картину данных для последующего маппинга.

        Создает базовую сущность документа.
        ИСПРАВЛЕНИЕ: Использует _extract_all_fields_from_record() для извлечения всех полей.

        Args:
            record_list: Список полей записи
            index: Индекс записи
            table_name: Имя таблицы

        Returns:
            Базовая сущность документа
        """
        # ИСПРАВЛЕНИЕ: Извлекаем все поля из записи
        all_fields = self._extract_all_fields_from_record(record_list)

        # Вспомогательная функция для безопасного извлечения значений
        def safe_get_value(field_name, default=None):
            if field_name in all_fields:
                value = all_fields[field_name]
                # Обрабатываем bytes как BLOB поля
                if isinstance(value, bytes):
                    return self._decode_blob_field(value)
                return value
            return default

        # Создаем базовую сущность с извлеченными полями
        base_entity = {
            # Идентификаторы
            "entity_id": f"{table_name}_{index}_document",
            "document_id": f"{table_name}_{index}",
            "table_name": table_name,
            "record_index": index,
            # Тип сущности
            "entity_type": "document",
            "document_type": self._determine_document_type(table_name),
            # Временные данные
            "created_date": safe_get_value("_DATE_TIME"),
            "execution_date": safe_get_value("_DATE"),
            "document_date": safe_get_value("_DATE"),
            # Участники
            "who_created": safe_get_value("_CREATED_BY"),
            "who_executed": safe_get_value("_EXECUTED_BY"),
            "supplier": safe_get_value("_SUPPLIER"),
            "buyer": safe_get_value("_BUYER"),
            "store": safe_get_value("_STORE"),
            "store_code": safe_get_value("_STORE_CODE"),
            # Что сделал
            "action": self._determine_action(table_name),
            "operation_type": self._determine_operation_type(table_name),
            # Объекты (цветы и товары)
            "objects": self._extract_objects(record_list),
            "flower_names": self._extract_flower_names(record_list),
            "flower_quantities": self._extract_flower_quantities(record_list),
            "flower_prices": self._extract_flower_prices(record_list),
            # Финансы
            "total_amount": safe_get_value("_FLD4239"),
            "currency": "RUB",
            "vat_amount": safe_get_value("_FLD4240"),
            "discount_amount": safe_get_value("_FLD4241"),
            # Статусы
            "is_posted": safe_get_value("_POSTED"),
            "is_marked": safe_get_value("_MARKED"),
            "payment_status": safe_get_value("_FLD4242"),
            "delivery_status": safe_get_value("_FLD4244"),
            # Дополнительная информация
            "description": self._extract_blob_content(record_list),
            "notes": safe_get_value("_FLD4245"),
            "version": safe_get_value("_VERSION"),
            # Метаданные
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
        }

        # ИСПРАВЛЕНИЕ: Добавляем все извлеченные поля как дополнительные поля
        for field_name, field_value in all_fields.items():
            if field_name not in base_entity:
                # Обрабатываем bytes как BLOB поля
                if isinstance(field_value, bytes):
                    base_entity[f"field_{field_name}"] = self._decode_blob_field(
                        field_value,
                    )
                else:
                    base_entity[f"field_{field_name}"] = field_value

        return base_entity

    def _extract_flower_entities(
        self,
        record_list: list,
        index: int,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """
        Извлекает сущности цветов из записи.

        Args:
            record_list: Список полей записи
            index: Индекс записи
            table_name: Имя таблицы

        Returns:
            Список сущностей цветов
        """
        entities = []

        # Ищем поля с цветами
        flower_names = self._extract_flower_names(record_list)
        flower_quantities = self._extract_flower_quantities(record_list)
        flower_prices = self._extract_flower_prices(record_list)

        # Создаем сущность для каждого цветка
        for i, flower_name in enumerate(flower_names):
            if flower_name and flower_name.strip():
                entity = {
                    # Идентификаторы
                    "entity_id": f"{table_name}_{index}_flower_{i}",
                    "document_id": f"{table_name}_{index}",
                    "table_name": table_name,
                    "record_index": index,
                    # Тип сущности
                    "entity_type": "flower",
                    "document_type": self._determine_document_type(table_name),
                    # Временные данные
                    "created_date": self._extract_field_value(
                        record_list,
                        "_DATE_TIME",
                    ),
                    "execution_date": self._extract_field_value(record_list, "_DATE"),
                    "document_date": self._extract_field_value(record_list, "_DATE"),
                    # Участники
                    "who_created": self._extract_field_value(
                        record_list,
                        "_CREATED_BY",
                    ),
                    "who_executed": self._extract_field_value(
                        record_list,
                        "_EXECUTED_BY",
                    ),
                    "supplier": self._extract_field_value(record_list, "_SUPPLIER"),
                    "buyer": self._extract_field_value(record_list, "_BUYER"),
                    "store": self._extract_field_value(record_list, "_STORE"),
                    "store_code": self._extract_field_value(record_list, "_STORE_CODE"),
                    # Что сделал
                    "action": self._determine_action(table_name),
                    "operation_type": self._determine_operation_type(table_name),
                    # Объекты (цветы и товары)
                    "object_name": flower_name,
                    "object_type": "flower",
                    "object_category": self._categorize_flower(flower_name),
                    "object_color": self._extract_flower_color(flower_name),
                    "object_size": self._extract_flower_size(flower_name),
                    "quantity": (
                        flower_quantities[i] if i < len(flower_quantities) else 0
                    ),
                    "unit_price": flower_prices[i] if i < len(flower_prices) else 0,
                    "total_price": (
                        flower_quantities[i] if i < len(flower_quantities) else 0
                    )
                    * (flower_prices[i] if i < len(flower_prices) else 0),
                    # Финансы
                    "total_amount": (
                        flower_quantities[i] if i < len(flower_quantities) else 0
                    )
                    * (flower_prices[i] if i < len(flower_prices) else 0),
                    "currency": "RUB",
                    # Статусы
                    "is_posted": self._extract_field_value(record_list, "_POSTED"),
                    "is_marked": self._extract_field_value(record_list, "_MARKED"),
                    # Метаданные
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
                entities.append(entity)

        return entities

    def _extract_operation_entities(
        self,
        record_list: list,
        index: int,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """
        Извлекает сущности операций из записи.

        Args:
            record_list: Список полей записи
            index: Индекс записи
            table_name: Имя таблицы

        Returns:
            Список сущностей операций
        """
        entities = []

        # Создаем сущность операции
        entity = {
            # Идентификаторы
            "entity_id": f"{table_name}_{index}_operation",
            "document_id": f"{table_name}_{index}",
            "table_name": table_name,
            "record_index": index,
            # Тип сущности
            "entity_type": "operation",
            "document_type": self._determine_document_type(table_name),
            # Временные данные
            "created_date": self._extract_field_value(record_list, "_DATE_TIME"),
            "execution_date": self._extract_field_value(record_list, "_DATE"),
            "document_date": self._extract_field_value(record_list, "_DATE"),
            # Участники
            "who_created": self._extract_field_value(record_list, "_CREATED_BY"),
            "who_executed": self._extract_field_value(record_list, "_EXECUTED_BY"),
            "supplier": self._extract_field_value(record_list, "_SUPPLIER"),
            "buyer": self._extract_field_value(record_list, "_BUYER"),
            "store": self._extract_field_value(record_list, "_STORE"),
            "store_code": self._extract_field_value(record_list, "_STORE_CODE"),
            # Что сделал
            "action": self._determine_action(table_name),
            "operation_type": self._determine_operation_type(table_name),
            # Объекты (цветы и товары)
            "objects": self._extract_objects(record_list),
            "object_name": f"Операция {self._determine_action(table_name)}",
            "object_type": "operation",
            "object_category": "business_operation",
            # Финансы
            "total_amount": self._extract_field_value(record_list, "_AMOUNT"),
            "currency": "RUB",
            "vat_amount": self._extract_field_value(record_list, "_VAT"),
            "discount_amount": self._extract_field_value(record_list, "_DISCOUNT"),
            # Статусы
            "is_posted": self._extract_field_value(record_list, "_POSTED"),
            "is_marked": self._extract_field_value(record_list, "_MARKED"),
            "payment_status": self._extract_field_value(record_list, "_PAYMENT_STATUS"),
            "delivery_status": self._extract_field_value(
                record_list,
                "_DELIVERY_STATUS",
            ),
            # Метаданные
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
        }
        entities.append(entity)

        return entities

    def _determine_document_type(self, table_name: str) -> str:
        """
        Определяет тип документа по имени таблицы на основе 1c-structure-mapping-analysis.md.

        Args:
            table_name: Имя таблицы

        Returns:
            Тип документа
        """
        # ПОЛНЫЙ МАППИНГ ДОКУМЕНТОВ на основе анализа структуры 1С
        document_types = {
            # КРИТИЧЕСКИЕ ДОКУМЕНТЫ (основные бизнес-процессы)
            "_DOCUMENT138": "Поступление товаров",
            "_DOCUMENT137": "Розничные продажи",
            "_DOCUMENT184": "Счета-фактуры",
            "_DOCUMENT154": "Отгрузка со склада",
            "_DOCUMENT163": "Перекомплектация",
            "_DOCUMENT156": "Реализация товаров",
            "_DOCUMENT12259": "Основные документы (технические)",
            # ЖУРНАЛЫ ДОКУМЕНТОВ (технические)
            "_DOCUMENTJOURNAL5354": "Журнал документов 5354",
            "_DOCUMENTJOURNAL5287": "Журнал документов 5287",
            "_DOCUMENTJOURNAL5321": "Журнал документов 5321",
            # ДОПОЛНИТЕЛЬНЫЕ ДОКУМЕНТЫ (на основе анализа)
            "_DOCUMENT90": "Документ 90 (технический)",
            "_DOCUMENT93": "Документ 93 (технический)",
            "_DOCUMENT94": "Документ 94 (технический)",
            "_DOCUMENT95": "Документ 95 (технический)",
            "_DOCUMENT104": "Документ 104 (технический)",
            "_DOCUMENT105": "Документ 105 (технический)",
            "_DOCUMENT109": "Документ 109 (технический)",
            "_DOCUMENT110": "Документ 110 (технический)",
            "_DOCUMENT111": "Документ 111 (технический)",
            "_DOCUMENT112": "Документ 112 (технический)",
            "_DOCUMENT113": "Документ 113 (технический)",
            "_DOCUMENT114": "Документ 114 (технический)",
            "_DOCUMENT115": "Документ 115 (технический)",
            "_DOCUMENT116": "Документ 116 (технический)",
            "_DOCUMENT117": "Документ 117 (технический)",
            "_DOCUMENT118": "Документ 118 (технический)",
            "_DOCUMENT119": "Документ 119 (технический)",
            "_DOCUMENT120": "Документ 120 (технический)",
            "_DOCUMENT121": "Документ 121 (технический)",
            "_DOCUMENT122": "Документ 122 (технический)",
            "_DOCUMENT123": "Документ 123 (технический)",
            "_DOCUMENT126": "Документ 126 (технический)",
            "_DOCUMENT127": "Документ 127 (технический)",
            "_DOCUMENT128": "Документ 128 (технический)",
            "_DOCUMENT129": "Документ 129 (технический)",
            "_DOCUMENT131": "Документ 131 (технический)",
            "_DOCUMENT132": "Документ 132 (технический)",
            "_DOCUMENT133": "Документ 133 (технический)",
            "_DOCUMENT134": "Документ 134 (технический)",
            "_DOCUMENT135": "Документ 135 (технический)",
            "_DOCUMENT136": "Документ 136 (технический)",
            "_DOCUMENT139": "Документ 139 (технический)",
            "_DOCUMENT140": "Документ 140 (технический)",
            "_DOCUMENT141": "Документ 141 (технический)",
            "_DOCUMENT142": "Документ 142 (технический)",
            "_DOCUMENT143": "Документ 143 (технический)",
            "_DOCUMENT144": "Документ 144 (технический)",
            "_DOCUMENT145": "Документ 145 (технический)",
            "_DOCUMENT146": "Документ 146 (технический)",
            "_DOCUMENT148": "Документ 148 (технический)",
            "_DOCUMENT149": "Документ 149 (технический)",
            "_DOCUMENT150": "Документ 150 (технический)",
            "_DOCUMENT151": "Документ 151 (технический)",
            "_DOCUMENT152": "Документ 152 (технический)",
            "_DOCUMENT153": "Документ 153 (технический)",
            "_DOCUMENT155": "Документ 155 (технический)",
            "_DOCUMENT157": "Документ 157 (технический)",
            "_DOCUMENT159": "Документ 159 (технический)",
            "_DOCUMENT160": "Документ 160 (технический)",
            "_DOCUMENT162": "Документ 162 (технический)",
            "_DOCUMENT164": "Документ 164 (технический)",
            "_DOCUMENT165": "Документ 165 (технический)",
            "_DOCUMENT166": "Документ 166 (технический)",
            "_DOCUMENT167": "Документ 167 (технический)",
            "_DOCUMENT168": "Документ 168 (технический)",
            "_DOCUMENT169": "Документ 169 (технический)",
            "_DOCUMENT170": "Документ 170 (технический)",
            "_DOCUMENT171": "Документ 171 (технический)",
            "_DOCUMENT172": "Документ 172 (технический)",
            "_DOCUMENT173": "Документ 173 (технический)",
            "_DOCUMENT174": "Документ 174 (технический)",
            "_DOCUMENT176": "Документ 176 (технический)",
            "_DOCUMENT177": "Документ 177 (технический)",
            "_DOCUMENT178": "Документ 178 (технический)",
            "_DOCUMENT190": "Документ 190 (технический)",
            # ДОКУМЕНТЫ С ИЗМЕНЕНИЯМИ (CHNGR)
            "_DOCUMENTCHNGR2119": "Документ изменений 2119",
            "_DOCUMENTCHNGR2142": "Документ изменений 2142",
            "_DOCUMENTCHNGR2190": "Документ изменений 2190",
            "_DOCUMENTCHNGR2204": "Документ изменений 2204",
            "_DOCUMENTCHNGR2228": "Документ изменений 2228",
            "_DOCUMENTCHNGR2250": "Документ изменений 2250",
            "_DOCUMENTCHNGR2311": "Документ изменений 2311",
            "_DOCUMENTCHNGR2369": "Документ изменений 2369",
            "_DOCUMENTCHNGR2396": "Документ изменений 2396",
            "_DOCUMENTCHNGR2428": "Документ изменений 2428",
            "_DOCUMENTCHNGR2452": "Документ изменений 2452",
            "_DOCUMENTCHNGR2486": "Документ изменений 2486",
            "_DOCUMENTCHNGR2511": "Документ изменений 2511",
            "_DOCUMENTCHNGR2569": "Документ изменений 2569",
            "_DOCUMENTCHNGR2620": "Документ изменений 2620",
            "_DOCUMENTCHNGR2638": "Документ изменений 2638",
            "_DOCUMENTCHNGR2661": "Документ изменений 2661",
            "_DOCUMENTCHNGR2688": "Документ изменений 2688",
            "_DOCUMENTCHNGR2692": "Документ изменений 2692",
            "_DOCUMENTCHNGR2703": "Документ изменений 2703",
            "_DOCUMENTCHNGR2744": "Документ изменений 2744",
            "_DOCUMENTCHNGR2783": "Документ изменений 2783",
            "_DOCUMENTCHNGR2806": "Документ изменений 2806",
            "_DOCUMENTCHNGR2813": "Документ изменений 2813",
            "_DOCUMENTCHNGR2846": "Документ изменений 2846",
            "_DOCUMENTCHNGR2878": "Документ изменений 2878",
            "_DOCUMENTCHNGR2957": "Документ изменений 2957",
            "_DOCUMENTCHNGR3013": "Документ изменений 3013",
            "_DOCUMENTCHNGR3105": "Документ изменений 3105",
            "_DOCUMENTCHNGR3145": "Документ изменений 3145",
            "_DOCUMENTCHNGR3155": "Документ изменений 3155",
            "_DOCUMENTCHNGR3172": "Документ изменений 3172",
            "_DOCUMENTCHNGR3200": "Документ изменений 3200",
            "_DOCUMENTCHNGR3236": "Документ изменений 3236",
            "_DOCUMENTCHNGR3270": "Документ изменений 3270",
            "_DOCUMENTCHNGR3307": "Документ изменений 3307",
            "_DOCUMENTCHNGR3341": "Документ изменений 3341",
            "_DOCUMENTCHNGR3398": "Документ изменений 3398",
            "_DOCUMENTCHNGR3466": "Документ изменений 3466",
            "_DOCUMENTCHNGR3529": "Документ изменений 3529",
            "_DOCUMENTCHNGR3585": "Документ изменений 3585",
            "_DOCUMENTCHNGR3644": "Документ изменений 3644",
            "_DOCUMENTCHNGR3697": "Документ изменений 3697",
            "_DOCUMENTCHNGR3714": "Документ изменений 3714",
            "_DOCUMENTCHNGR3766": "Документ изменений 3766",
            "_DOCUMENTCHNGR3873": "Документ изменений 3873",
            "_DOCUMENTCHNGR3969": "Документ изменений 3969",
            "_DOCUMENTCHNGR4025": "Документ изменений 4025",
            "_DOCUMENTCHNGR4057": "Документ изменений 4057",
            "_DOCUMENTCHNGR4075": "Документ изменений 4075",
            "_DOCUMENTCHNGR4102": "Документ изменений 4102",
            "_DOCUMENTCHNGR4133": "Документ изменений 4133",
            "_DOCUMENTCHNGR4189": "Документ изменений 4189",
            "_DOCUMENTCHNGR4221": "Документ изменений 4221",
            "_DOCUMENTCHNGR4346": "Документ изменений 4346",
            "_DOCUMENTCHNGR4369": "Документ изменений 4369",
            "_DOCUMENTCHNGR4391": "Документ изменений 4391",
            "_DOCUMENTCHNGR4413": "Документ изменений 4413",
            "_DOCUMENTCHNGR4434": "Документ изменений 4434",
            "_DOCUMENTCHNGR4467": "Документ изменений 4467",
            "_DOCUMENTCHNGR4510": "Документ изменений 4510",
            "_DOCUMENTCHNGR4546": "Документ изменений 4546",
            "_DOCUMENTCHNGR4637": "Документ изменений 4637",
            "_DOCUMENTCHNGR4703": "Документ изменений 4703",
            "_DOCUMENTCHNGR4732": "Документ изменений 4732",
            "_DOCUMENTCHNGR4753": "Документ изменений 4753",
            "_DOCUMENTCHNGR4786": "Документ изменений 4786",
            "_DOCUMENTCHNGR4809": "Документ изменений 4809",
            "_DOCUMENTCHNGR4818": "Документ изменений 4818",
            "_DOCUMENTCHNGR4828": "Документ изменений 4828",
        }

        # Проверяем точное совпадение
        if table_name in document_types:
            return document_types[table_name]

        # Проверяем частичное совпадение для других документов
        if "_DOCUMENT" in table_name:
            # Извлекаем номер документа
            doc_number = table_name.replace("_DOCUMENT", "")
            return f"Документ {doc_number} (технический)"
        if "_REFERENCE" in table_name:
            return "Справочник"
        if "_REGISTER" in table_name:
            return "Регистр"
        return "Неизвестный тип"

    def _determine_action(self, table_name: str) -> str:
        """
        Определяет действие по имени таблицы.

        Args:
            table_name: Имя таблицы

        Returns:
            Действие
        """
        action_mapping = {
            "закупка": ["поступление", "receipt", "приход"],
            "продажа": ["реализация", "sale", "продажа"],
            "перемещение": ["перемещение", "transfer", "движение"],
            "создание": ["создание", "creation", "новый"],
        }

        table_lower = table_name.lower()
        for action, keywords in action_mapping.items():
            if any(keyword in table_lower for keyword in keywords):
                return action

        return "неизвестное действие"

    def _determine_operation_type(self, table_name: str) -> str:
        """
        Определяет тип операции по имени таблицы.

        Args:
            table_name: Имя таблицы

        Returns:
            Тип операции
        """
        operation_mapping = {
            "входящая": ["поступление", "receipt", "приход"],
            "исходящая": ["реализация", "sale", "продажа"],
            "внутренняя": ["перемещение", "transfer", "движение"],
        }

        table_lower = table_name.lower()
        for op_type, keywords in operation_mapping.items():
            if any(keyword in table_lower for keyword in keywords):
                return op_type

        return "неизвестная операция"

    def _extract_field_value(self, record_list: list, field_name: str) -> Any:
        """
        JTBD: Как извлекатель значений полей, я хочу получить значение любого поля
        из документа, чтобы обеспечить полное извлечение данных для анализа.

        КРИТИЧЕСКИ ВАЖНО: Извлекаем значения ВСЕХ полей, включая неизвестные,
        чтобы создать полную таблицу маппинга полей для последующего анализа.

        Извлекает значение поля из записи с использованием маппинга полей.

        Args:
            record_list: Список полей записи
            field_name: Имя поля

        Returns:
            Значение поля
        """
        try:
            # Получаем маппинг полей
            field_mapping = get_field_mapping()
            index_mapping = get_field_mapping_by_index()

            # ИСПРАВЛЕНИЕ: Правильное извлечение полей из onec_dtools
            # onec_dtools возвращает поля как объекты с атрибутами name и value

            # ИСПРАВЛЕНИЕ: Маппинг на основе РЕАЛЬНЫХ полей из 1С базы данных
            field_alternatives = {
                # Временные поля - используем реальные поля с данными
                "document_date": [
                    "field__POSTED",
                    "field__DATE_TIME",
                    "_DATE",
                    "_DATE_TIME",
                ],
                "execution_date": [
                    "field__POSTED",
                    "field__DATE_TIME",
                    "_DATE",
                    "_DATE_TIME",
                ],
                "created_date": [
                    "field__DATE_TIME",
                    "field__POSTED",
                    "_DATE_TIME",
                    "_DATE",
                ],
                # Участники - пока не найдены реальные поля
                "who_created": ["_CREATED_BY", "_AUTHOR", "_USER"],
                "who_executed": ["_EXECUTED_BY", "_PERFORMER", "_EXECUTOR"],
                "supplier": ["_SUPPLIER", "_CONTRACTOR", "_VENDOR"],
                "buyer": ["_BUYER", "_CUSTOMER", "_CLIENT"],
                # Склады - пока не найдены реальные поля
                "store": ["_STORE", "_WAREHOUSE", "_LOCATION"],
                "store_code": ["_STORE_CODE", "_WAREHOUSE_CODE", "_LOCATION_CODE"],
                # Финансовые - используем реальные поля с данными
                "total_amount": [
                    "field__FLD4227",
                    "field__FLD4236",
                    "field__FLD4237",
                    "_FLD4239",
                ],
                "vat_amount": [
                    "field__FLD4227",
                    "field__FLD4236",
                    "field__FLD4237",
                    "_VAT",
                ],
                "discount_amount": [
                    "field__FLD4227",
                    "field__FLD4236",
                    "field__FLD4237",
                    "_DISCOUNT",
                ],
                # Статусы - используем реальные поля с данными
                "payment_status": ["field__POSTED", "field__MARKED", "_PAYMENT_STATUS"],
                "delivery_status": [
                    "field__POSTED",
                    "field__MARKED",
                    "_DELIVERY_STATUS",
                ],
                "is_posted": ["field__POSTED", "_POSTED", "_FLD9999"],
                "is_marked": ["field__MARKED", "_MARKED", "_FLD9998"],
            }

            # Сначала ищем по точному имени
            for field in record_list:
                if hasattr(field, "name") and field.name == field_name:
                    if hasattr(field, "value"):
                        # ИСПРАВЛЕНИЕ: Правильная обработка BLOB полей с UTF-16
                        if field_name in [
                            "_FLD4229",
                            "_FLD4243",
                            "_FLD4254",
                            "_FLD3108",
                            "_FLD4255",
                            "_FLD4256",
                        ]:
                            # UTF-16 для NT полей (стандарт 1С)
                            try:
                                if isinstance(field.value, bytes):
                                    content = field.value.decode("utf-16")
                                    if content and len(content.strip()) > 0:
                                        return content
                                else:
                                    return str(field.value)
                            except UnicodeDecodeError:
                                # Fallback на UTF-8, CP1251
                                for encoding in ["utf-8", "cp1251"]:
                                    try:
                                        if isinstance(field.value, bytes):
                                            content = field.value.decode(encoding)
                                            if content and len(content.strip()) > 0:
                                                return content
                                    except UnicodeDecodeError:
                                        continue
                                # Если все кодировки не сработали, используем hex
                                return (
                                    field.value.hex()
                                    if isinstance(field.value, bytes)
                                    else str(field.value)
                                )
                        return field.value
                    return str(field)

            # Если поле не найдено, пытаемся найти по индексу
            if field_name.startswith("field_"):
                try:
                    field_index = int(field_name.split("_")[1])
                    if field_index in index_mapping:
                        real_field_name = index_mapping[field_index]
                        return self._extract_field_value(record_list, real_field_name)
                except (ValueError, IndexError):
                    pass

            # ИСПРАВЛЕНИЕ: Если поле не найдено, пытаемся найти по маппингу
            if field_name in field_mapping:
                mapped_field = field_mapping[field_name]
                return self._extract_field_value(record_list, mapped_field)

            # НОВОЕ: Поиск по альтернативным именам полей
            if field_name in field_alternatives:
                for alt_field_name in field_alternatives[field_name]:
                    for field in record_list:
                        if hasattr(field, "name") and field.name == alt_field_name:
                            if hasattr(field, "value"):
                                return field.value
                            return str(field)

            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при извлечении поля {field_name}: {e}")
            return None

    def _extract_all_fields_from_record(self, record_list):
        """
        JTBD: Как извлекатель всех полей, я хочу извлечь ВСЕ поля из документа любого типа,
        чтобы создать полную картину данных для последующего анализа и маппинга.

        КРИТИЧЕСКИ ВАЖНО: Извлекаем ВСЕ поля, даже неизвестные, для создания полной таблицы маппинга.
        Это позволит нам в будущем понять структуру данных и создать правильные маппинги.

        ИСПРАВЛЕНИЕ: Извлекает все поля из записи используя правильный подход onec_dtools.
        Копирует подход из extract_all_available_data.py который работает.

        Args:
            record_list: Список полей записи

        Returns:
            Словарь со всеми полями и их значениями
        """
        try:
            # ИСПРАВЛЕНИЕ: Используем тот же подход что и в extract_all_available_data.py
            all_fields = {}

            for j, value in enumerate(record_list):
                # Определяем имя поля как в оригинальном коде
                field_name = f"field_{j}"
                if hasattr(value, "name") and value.name:
                    field_name = value.name
                elif hasattr(value, "__class__") and hasattr(
                    value.__class__,
                    "__name__",
                ):
                    # Пытаемся получить имя из типа поля
                    if "FLD" in str(value.__class__):
                        field_name = (
                            str(value.__class__).split("'")[1]
                            if "'" in str(value.__class__)
                            else f"field_{j}"
                        )

                # Применяем маппинг по индексу для field_X полей
                if field_name.startswith("field_"):
                    try:
                        field_index = int(field_name.split("_")[1])
                        index_mapping = get_field_mapping_by_index()
                        if field_index in index_mapping:
                            field_name = index_mapping[field_index]
                    except (ValueError, IndexError):
                        pass

                # ИСПРАВЛЕНИЕ: Правильно извлекаем значение из объекта поля
                if hasattr(value, "value"):
                    field_value = value.value
                    # Обрабатываем BLOB поля
                    if isinstance(field_value, bytes):
                        decoded_value = self._decode_blob_field(field_value)
                        all_fields[field_name] = decoded_value
                    else:
                        all_fields[field_name] = field_value
                else:
                    # Если нет атрибута value, сохраняем объект как есть
                    all_fields[field_name] = value

            return all_fields
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка при извлечении всех полей: {e}")
            return {}

    def _extract_objects(self, record_list: list) -> list[str]:
        """
        Извлекает объекты из записи.

        Args:
            record_list: Список полей записи

        Returns:
            Список объектов
        """
        objects = []
        for field in record_list:
            if hasattr(field, "value") and field.value:
                field_str = str(field.value).lower()
                if any(
                    obj in field_str
                    for obj in [
                        "роза",
                        "rose",
                        "тюльпан",
                        "tulip",
                        "хризантема",
                        "chrysanthemum",
                        "лилия",
                        "lily",
                    ]
                ):
                    objects.append(str(field.value))
        return objects

    def _extract_flower_names(self, record_list: list) -> list[str]:
        """
        Извлекает названия цветов из BLOB полей и других источников.

        Args:
            record_list: Список полей записи

        Returns:
            Список названий цветов
        """
        flower_names = []

        # Ищем в BLOB полях
        blob_content = self._extract_blob_content(record_list)
        if blob_content:
            # Ищем упоминания цветов в BLOB содержимом
            flower_keywords = [
                "роза",
                "rose",
                "тюльпан",
                "tulip",
                "хризантема",
                "chrysanthemum",
                "лилия",
                "lily",
                "гвоздика",
                "carnation",
                "орхидея",
                "orchid",
                "пион",
                "peony",
                "ирис",
                "iris",
                "нарцисс",
                "daffodil",
            ]

            for keyword in flower_keywords:
                if keyword.lower() in blob_content.lower():
                    # Извлекаем контекст вокруг найденного цветка
                    start = blob_content.lower().find(keyword.lower())
                    if start != -1:
                        context = blob_content[max(0, start - 50) : start + 50]
                        flower_names.append(f"{keyword} ({context.strip()})")

        # Ищем в обычных полях
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
                        "лилия",
                        "lily",
                        "гвоздика",
                        "carnation",
                        "орхидея",
                        "orchid",
                    ]
                ):
                    flower_names.append(str(field.value))

        return flower_names

    def _extract_flower_quantities(self, record_list: list) -> list[float]:
        """
        Извлекает количества цветов из полей _FLD4238 и других числовых полей.

        Args:
            record_list: Список полей записи

        Returns:
            Список количеств
        """
        quantities = []

        # Ищем в поле количества товара
        quantity_field = self._extract_field_value(record_list, "_FLD4238")
        if quantity_field is not None:
            try:
                quantities.append(float(quantity_field))
            except (ValueError, TypeError):
                pass

        # Ищем в других числовых полях
        for field in record_list:
            if hasattr(field, "value") and field.value:
                try:
                    if isinstance(field.value, (int, float)) and float(field.value) > 0:
                        quantities.append(float(field.value))
                except (ValueError, TypeError):
                    continue

        return quantities

    def _extract_flower_prices(self, record_list: list) -> list[float]:
        """
        Извлекает цены цветов из полей _FLD4239 и других финансовых полей.

        Args:
            record_list: Список полей записи

        Returns:
            Список цен
        """
        prices = []

        # Ищем в поле суммы документа
        amount_field = self._extract_field_value(record_list, "_FLD4239")
        if amount_field is not None:
            try:
                prices.append(float(amount_field))
            except (ValueError, TypeError):
                pass

        # Ищем в дополнительной сумме
        additional_amount = self._extract_field_value(record_list, "_FLD9885")
        if additional_amount is not None:
            try:
                prices.append(float(additional_amount))
            except (ValueError, TypeError):
                pass

        # Ищем в других числовых полях
        for field in record_list:
            if hasattr(field, "value") and field.value:
                try:
                    if isinstance(field.value, (int, float)) and float(field.value) > 0:
                        prices.append(float(field.value))
                except (ValueError, TypeError):
                    continue

        return prices

    def _categorize_flower(self, flower_name: str) -> str:
        """
        Категоризирует цветок по названию.

        Args:
            flower_name: Название цветка

        Returns:
            Категория цветка
        """
        flower_lower = flower_name.lower()

        if any(flower in flower_lower for flower in ["роза", "rose"]):
            return "розы"
        if any(flower in flower_lower for flower in ["тюльпан", "tulip"]):
            return "тюльпаны"
        if any(flower in flower_lower for flower in ["хризантема", "chrysanthemum"]):
            return "хризантемы"
        if any(flower in flower_lower for flower in ["лилия", "lily"]):
            return "лилии"
        return "другие цветы"

    def _extract_flower_color(self, flower_name: str) -> str:
        """
        Извлекает цвет цветка из названия.

        Args:
            flower_name: Название цветка

        Returns:
            Цвет цветка
        """
        flower_lower = flower_name.lower()

        if any(color in flower_lower for color in ["красн", "red", "алый"]):
            return "красный"
        if any(color in flower_lower for color in ["бел", "white", "белый"]):
            return "белый"
        if any(color in flower_lower for color in ["розов", "pink", "розовый"]):
            return "розовый"
        if any(color in flower_lower for color in ["желт", "yellow", "желтый"]):
            return "желтый"
        return "неизвестный цвет"

    def _extract_flower_size(self, flower_name: str) -> str:
        """
        Извлекает размер цветка из названия.

        Args:
            flower_name: Название цветка

        Returns:
            Размер цветка
        """
        flower_lower = flower_name.lower()

        if any(size in flower_lower for size in ["больш", "large", "крупн"]):
            return "большой"
        if any(size in flower_lower for size in ["маленьк", "small", "мелк"]):
            return "маленький"
        if any(size in flower_lower for size in ["средн", "medium", "средний"]):
            return "средний"
        return "неизвестный размер"

    def _decode_blob_field(self, blob_value: Any) -> str:
        """
        JTBD: Как декодер BLOB полей, я хочу извлечь ВСЕ текстовое содержимое
        из BLOB полей, чтобы получить максимальную информацию о документах.

        КРИТИЧЕСКИ ВАЖНО: Декодируем ВСЕ BLOB поля с различными кодировками,
        чтобы не потерять важную информацию о цветах, товарах и операциях.

        Декодирует BLOB поле с правильной обработкой UTF-16 и других кодировок.

        Args:
            blob_value: Значение BLOB поля

        Returns:
            Декодированное содержимое
        """
        try:
            if isinstance(blob_value, bytes):
                # ИСПРАВЛЕНИЕ: Правильная обработка BLOB с UTF-16 (стандарт 1С)
                # Сначала пробуем UTF-16 (стандарт для NT полей в 1С)
                try:
                    content = blob_value.decode("utf-16")
                    if content and len(content.strip()) > 0:
                        return content
                except UnicodeDecodeError:
                    pass

                # Затем UTF-8
                try:
                    content = blob_value.decode("utf-8")
                    if content and len(content.strip()) > 0:
                        return content
                except UnicodeDecodeError:
                    pass

                # Затем CP1251 для русских текстов
                try:
                    content = blob_value.decode("cp1251")
                    if content and len(content.strip()) > 0:
                        return content
                except UnicodeDecodeError:
                    pass

                # Затем Latin1
                try:
                    content = blob_value.decode("latin1")
                    if content and len(content.strip()) > 0:
                        return content
                except UnicodeDecodeError:
                    pass

                # В крайнем случае hex
                return blob_value.hex()
            return str(blob_value)
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка декодирования BLOB: {e}")
            return str(blob_value)

    def _extract_blob_content(self, record_list: list) -> str:
        """
        Извлекает содержимое BLOB полей с правильным декодированием.

        Args:
            record_list: Список полей записи

        Returns:
            Содержимое BLOB полей
        """
        blob_content = []
        for field in record_list:
            if hasattr(field, "value") and isinstance(field.value, bytes):
                decoded = self._decode_blob_field(field.value)
                if decoded and decoded.strip():
                    blob_content.append(decoded)
        return " ".join(blob_content)

    def save_results(
        self,
        output_path: str = "data/results/flat_table_extraction.json",
    ) -> str:
        """
        Сохраняет результаты извлечения плоской таблицы.

        Args:
            output_path: Путь для сохранения результатов

        Returns:
            Путь к сохраненному файлу
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.flat_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 Результаты сохранены: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении результатов: {e}")
            raise

    def save_to_csv(
        self,
        output_path: str = "data/results/flat_table_extraction.csv",
    ) -> str:
        """
        Сохраняет результаты в CSV формат.

        Args:
            output_path: Путь для сохранения CSV файла

        Returns:
            Путь к сохраненному файлу
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            df = pd.DataFrame(self.flat_data)
            df.to_csv(output_path, index=False, encoding="utf-8")

            self.logger.info(f"💾 CSV результаты сохранены: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении CSV: {e}")
            raise

    def get_extraction_summary(self) -> dict[str, Any]:
        """
        Возвращает сводку по извлечению плоской таблицы.

        Returns:
            Словарь со статистикой извлечения
        """
        return {
            "total_documents": self.extraction_stats["total_documents"],
            "total_entities": self.extraction_stats["total_entities"],
            "successful_extractions": self.extraction_stats["successful_extractions"],
            "failed_extractions": self.extraction_stats["failed_extractions"],
            "success_rate": (
                self.extraction_stats["successful_extractions"]
                / max(self.extraction_stats["total_documents"], 1)
                * 100
            ),
            "extraction_errors": self.extraction_stats["extraction_errors"],
        }

    def print_flat_table_preview(self, limit: int = 10) -> None:
        """
        Выводит превью плоской таблицы в терминал в табличном формате.

        Args:
            limit: Количество строк для отображения
        """
        if not self.flat_data:
            print("❌ Нет данных для отображения")
            return

        print(f"\n📊 ПРЕВЬЮ ПЛОСКОЙ ТАБЛИЦЫ (первые {limit} строк):")
        print("=" * 120)

        # Определяем ключевые колонки для отображения
        key_columns = [
            "entity_id",
            "entity_type",
            "document_type",
            "table_name",
            "created_date",
            "execution_date",
            "action",
            "object_name",
            "total_amount",
            "currency",
            "is_posted",
        ]

        # Фильтруем только существующие колонки
        available_columns = [col for col in key_columns if col in self.flat_data[0]]

        # Создаем заголовок таблицы
        header = " | ".join([col[:15].ljust(15) for col in available_columns])
        print(header)
        print("-" * len(header))

        # Выводим данные
        for i, entity in enumerate(self.flat_data[:limit]):
            row_data = []
            for col in available_columns:
                value = entity.get(col, "N/A")
                if value is None:
                    value = "N/A"
                elif isinstance(value, str) and len(value) > 15:
                    value = value[:12] + "..."
                else:
                    value = str(value)[:15]
                row_data.append(value.ljust(15))

            row = " | ".join(row_data)
            print(f"{i + 1:2d}. {row}")

        print(f"\n📈 Всего сущностей: {len(self.flat_data)}")
        print(f"📊 Показано: {min(limit, len(self.flat_data))}")

    def print_flat_table_detailed(self, limit: int = 5) -> None:
        """
        Выводит детальную информацию о плоской таблице.

        Args:
            limit: Количество сущностей для детального отображения
        """
        if not self.flat_data:
            print("❌ Нет данных для отображения")
            return

        print("\n🔍 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПЛОСКОЙ ТАБЛИЦЕ:")
        print("=" * 80)

        # Статистика по типам сущностей
        entity_types = {}
        for entity in self.flat_data:
            entity_type = entity.get("entity_type", "unknown")
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        print("📈 СТАТИСТИКА ПО ТИПАМ СУЩНОСТЕЙ:")
        for entity_type, count in entity_types.items():
            percentage = (count / len(self.flat_data)) * 100
            print(f"  - {entity_type}: {count} ({percentage:.1f}%)")

        # Анализ N/A значений
        na_count = 0
        total_fields = 0
        for entity in self.flat_data:
            for key, value in entity.items():
                total_fields += 1
                if value is None or value == "N/A" or str(value).strip() == "":
                    na_count += 1

        na_percentage = (na_count / total_fields * 100) if total_fields > 0 else 0
        print(f"\n📊 N/A ЗНАЧЕНИЯ: {na_count}/{total_fields} ({na_percentage:.1f}%)")

        # Детальные примеры
        print(f"\n📄 ДЕТАЛЬНЫЕ ПРИМЕРЫ (первые {limit} сущностей):")
        for i, entity in enumerate(self.flat_data[:limit]):
            print(f"\n--- Сущность {i + 1} ---")
            for key, value in entity.items():
                if key not in ["description"]:  # Пропускаем большие BLOB поля
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    print(f"  {key}: {value}")
