#!/usr/bin/env python3
"""
TableAnalyzer - анализ структуры таблиц 1С.

JTBD:
Как анализатор структуры таблиц, я хочу анализировать структуру и типы полей таблиц 1С,
чтобы экстракторы могли правильно обрабатывать данные.
"""

import re
from datetime import datetime
from typing import Any

# from typing import Optional, Tuple  # Неиспользуемые импорты


class TableAnalyzer:
    """
    JTBD:
    Как TableAnalyzer, я хочу анализировать структуру таблиц 1С,
    чтобы предоставить метаданные о полях для правильной обработки данных.
    """

    def __init__(self) -> None:
        """
        JTBD:
        Как конструктор TableAnalyzer, я хочу инициализировать анализатор,
        чтобы подготовить все необходимые ресурсы для анализа структуры таблиц.
        """
        self.field_patterns = {
            "number": [r"_NUMBER", r"number", r"№"],
            "date": [r"_DATE", r"_DATE_TIME", r"date", r"время"],
            "amount": [r"_AMOUNT", r"_FLD\d+", r"sum", r"amount", r"сумма"],
            "description": [r"description", r"описание", r"комментарий"],
            "store": [r"store", r"магазин", r"склад"],
            "nomenclature": [r"номенклатура", r"nomenclature", r"товар"],
            "quantity": [r"количество", r"quantity", r"qty"],
            "price": [r"цена", r"price", r"стоимость"],
        }

    def analyze_table_structure(self, table: Any) -> dict[str, Any]:
        """
        JTBD:
        Как метод анализа структуры таблицы, я хочу проанализировать структуру таблицы,
        чтобы предоставить метаданные о полях и их назначении.
        """
        if not table or len(table) == 0:
            return {
                "table_size": 0,
                "has_data": False,
                "field_analysis": {},
                "structure_summary": {},
            }

        # ИСПРАВЛЕНО: Анализируем ВСЕ записи для понимания структуры
        # Убираем лимит в 10 записей - анализируем все доступные данные
        field_analysis = {}
        field_types = {}
        field_names = set()

        print(f"📊 Анализ структуры таблицы: {len(table)} записей")

        # ИСПРАВЛЕНО: Анализируем все записи, но с ограничением для производительности
        max_analysis_records = (
            min(1000, len(table)) if hasattr(table, "__len__") else 1000
        )
        print(f"📊 Будет проанализировано: {max_analysis_records} записей")

        for i in range(max_analysis_records):
            try:
                row = table[i]
                if not hasattr(row, "is_empty") or not row.is_empty:
                    row_list = row.as_list(True) if hasattr(row, "as_list") else []
                    if row_list:
                        for j, value in enumerate(row_list):
                            field_name = getattr(value, "name", f"field_{j}")
                            field_names.add(field_name)

                            # Анализируем тип поля
                            field_type = self._analyze_field_type(value)
                            if field_name not in field_types:
                                field_types[field_name] = field_type

                            # Анализируем содержимое поля
                            if field_name not in field_analysis:
                                field_analysis[field_name] = {
                                    "type": field_type,
                                    "sample_values": [],
                                    "is_numeric": False,
                                    "is_date": False,
                                    "is_string": False,
                                    "is_blob": False,
                                    "field_purpose": "unknown",
                                }

                            # Добавляем образец значения
                            sample_values = field_analysis[field_name]["sample_values"]
                            if (
                                isinstance(sample_values, list)
                                and len(sample_values) < 3
                            ):
                                sample_values.append(
                                    str(value)[:100] if value else None,
                                )

                            # Обновляем характеристики поля
                            field_analysis[field_name].update(
                                {
                                    "is_numeric": isinstance(value, (int, float)),
                                    "is_date": isinstance(value, datetime),
                                    "is_string": isinstance(value, str),
                                    "is_blob": self._is_blob_field(value),
                                },
                            )
            except Exception:
                continue

        # Определяем назначение полей
        for field_name, analysis in field_analysis.items():
            analysis["field_purpose"] = self._determine_field_purpose(
                field_name,
                analysis,
            )

        return {
            "table_size": len(table),
            "has_data": len(table) > 0,
            "field_analysis": field_analysis,
            "field_names": list(field_names),
            "structure_summary": self._create_structure_summary(field_analysis),
        }

    def identify_field_types(self, row: Any) -> dict[str, Any]:
        """
        JTBD:
        Как метод идентификации типов полей, я хочу определить типы полей в строке,
        чтобы экстракторы могли правильно обрабатывать данные.
        """
        if not row:
            return {}

        field_types = {}
        row_list = row.as_list(True) if hasattr(row, "as_list") else []

        for j, value in enumerate(row_list):
            field_name = getattr(value, "name", f"field_{j}")
            field_types[field_name] = {
                "type": self._analyze_field_type(value),
                "value": value,
                "is_numeric": isinstance(value, (int, float)),
                "is_date": isinstance(value, datetime),
                "is_string": isinstance(value, str),
                "is_blob": self._is_blob_field(value),
            }

        return field_types

    def extract_field_metadata(self, field_name: str, value: Any) -> dict[str, Any]:
        """
        JTBD:
        Как метод извлечения метаданных поля, я хочу извлечь метаданные конкретного поля,
        чтобы экстракторы могли принимать решения о обработке поля.
        """
        return {
            "field_name": field_name,
            "type": self._analyze_field_type(value),
            "is_numeric": isinstance(value, (int, float)),
            "is_date": isinstance(value, datetime),
            "is_string": isinstance(value, str),
            "is_blob": self._is_blob_field(value),
            "value_preview": str(value)[:100] if value else None,
            "field_purpose": self._determine_field_purpose(
                field_name,
                {
                    "type": self._analyze_field_type(value),
                    "is_numeric": isinstance(value, (int, float)),
                    "is_date": isinstance(value, datetime),
                    "is_string": isinstance(value, str),
                    "is_blob": self._is_blob_field(value),
                },
            ),
        }

    def analyze_document_structure(
        self,
        field_analysis: dict[str, Any],
    ) -> dict[str, list[str]]:
        """
        JTBD:
        Как метод анализа структуры документа, я хочу проанализировать структуру документа,
        чтобы выделить поля по их назначению (номера, даты, суммы и т.д.).
        """
        number_fields = []
        date_fields = []
        amount_fields = []
        description_fields = []
        store_fields = []
        blob_fields = []

        for field_name, analysis in field_analysis.items():
            field_purpose = analysis.get("field_purpose", "unknown")

            if field_purpose == "number":
                number_fields.append(field_name)
            elif field_purpose == "date":
                date_fields.append(field_name)
            elif field_purpose == "amount":
                amount_fields.append(field_name)
            elif field_purpose == "description":
                description_fields.append(field_name)
            elif field_purpose == "store":
                store_fields.append(field_name)
            elif analysis.get("is_blob", False):
                blob_fields.append(field_name)

        return {
            "number_fields": number_fields,
            "date_fields": date_fields,
            "amount_fields": amount_fields,
            "description_fields": description_fields,
            "store_fields": store_fields,
            "blob_fields": blob_fields,
        }

    def _analyze_field_type(self, value: Any) -> str:
        """
        JTBD:
        Как метод анализа типа поля, я хочу определить тип поля по его значению,
        чтобы правильно классифицировать поля.
        """
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "string"
        if isinstance(value, datetime):
            return "datetime"
        if isinstance(value, bytes):
            return "bytes"
        if hasattr(value, "value") and hasattr(value, "__class__"):
            if "Blob" in str(type(value)):
                return "blob"
            return "object"
        return "unknown"

    def _is_blob_field(self, value: Any) -> bool:
        """
        JTBD:
        Как метод проверки BLOB поля, я хочу определить является ли поле BLOB,
        чтобы правильно обрабатывать бинарные данные.
        """
        if isinstance(value, bytes) and len(value) > 0:
            return True
        if hasattr(value, "value") and hasattr(value, "__class__"):
            return "Blob" in str(type(value))
        return False

    def _determine_field_purpose(
        self,
        field_name: str,
        analysis: dict[str, Any],
    ) -> str:
        """
        JTBD:
        Как метод определения назначения поля, я хочу определить назначение поля по имени и типу,
        чтобы правильно классифицировать поля для обработки.
        """
        field_name_lower = field_name.lower()

        # Проверяем по имени поля
        for purpose, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, field_name_lower, re.IGNORECASE):
                    return purpose

        # Проверяем по типу и содержимому
        if analysis.get("is_numeric", False) and analysis.get("type") in [
            "integer",
            "float",
        ]:
            # Проверяем размер числа для определения типа
            if "sample_values" in analysis:
                for sample in analysis["sample_values"]:
                    if sample and isinstance(sample, str):
                        try:
                            num_value = float(sample)
                            if num_value > 1000:  # Вероятно сумма
                                return "amount"
                            if num_value < 100:  # Вероятно количество
                                return "quantity"
                        except ValueError:
                            pass

        if analysis.get("is_date", False):
            return "date"

        if analysis.get("is_blob", False):
            return "blob"

        if analysis.get("is_string", False):
            # Анализируем содержимое строки
            if "sample_values" in analysis:
                for sample in analysis["sample_values"]:
                    if sample and isinstance(sample, str):
                        if any(
                            keyword in sample.lower()
                            for keyword in ["магазин", "склад"]
                        ):
                            return "store"
                        if any(
                            keyword in sample.lower()
                            for keyword in ["флор", "декор", "моно"]
                        ):
                            return "description"

        return "unknown"

    def _create_structure_summary(
        self,
        field_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        JTBD:
        Как метод создания сводки структуры, я хочу создать сводку структуры таблицы,
        чтобы предоставить общую информацию о таблице.
        """
        total_fields = len(field_analysis)
        numeric_fields = sum(
            1 for f in field_analysis.values() if f.get("is_numeric", False)
        )
        string_fields = sum(
            1 for f in field_analysis.values() if f.get("is_string", False)
        )
        blob_fields = sum(1 for f in field_analysis.values() if f.get("is_blob", False))
        date_fields = sum(1 for f in field_analysis.values() if f.get("is_date", False))

        return {
            "total_fields": total_fields,
            "numeric_fields": numeric_fields,
            "string_fields": string_fields,
            "blob_fields": blob_fields,
            "date_fields": date_fields,
            "field_distribution": {
                "numeric": (
                    f"{(numeric_fields / total_fields * 100):.1f}%"
                    if total_fields > 0
                    else "0%"
                ),
                "string": (
                    f"{(string_fields / total_fields * 100):.1f}%"
                    if total_fields > 0
                    else "0%"
                ),
                "blob": (
                    f"{(blob_fields / total_fields * 100):.1f}%"
                    if total_fields > 0
                    else "0%"
                ),
                "date": (
                    f"{(date_fields / total_fields * 100):.1f}%"
                    if total_fields > 0
                    else "0%"
                ),
            },
        }
