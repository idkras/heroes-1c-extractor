#!/usr/bin/env python3
"""
DocumentAnalyzer - Анализ документов и метаданных

JTBD:
Как аналитик документов, я хочу анализировать структуру документов 1С,
чтобы извлекать метаданные, поля и бизнес-информацию для дальнейшей обработки.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FieldInfo:
    """Информация о поле документа"""

    name: str
    value: Any
    type: str
    is_numeric: bool
    is_date: bool
    is_string: bool
    is_blob: bool
    is_empty: bool
    size: int = 0


@dataclass
class DocumentMetadata:
    """Метаданные документа"""

    document_number: str = "N/A"
    document_date: str = "N/A"
    document_type: str = "Неизвестно"
    store_name: str = "N/A"
    store_code: str = "N/A"
    total_amount: float = 0.0
    currency: str = "RUB"
    supplier_name: str = "N/A"
    buyer_name: str = "N/A"
    sale_type: str = "N/A"


@dataclass
class DocumentStructure:
    """Структура документа"""

    number_fields: List[str] = None
    date_fields: List[str] = None
    description_fields: List[str] = None
    amount_fields: List[str] = None
    sale_type_fields: List[str] = None
    blob_fields: List[str] = None

    def __post_init__(self):
        if self.number_fields is None:
            self.number_fields = []
        if self.date_fields is None:
            self.date_fields = []
        if self.description_fields is None:
            self.description_fields = []
        if self.amount_fields is None:
            self.amount_fields = []
        if self.sale_type_fields is None:
            self.sale_type_fields = []
        if self.blob_fields is None:
            self.blob_fields = []


class DocumentAnalyzer:
    """
    Анализатор документов 1С для извлечения метаданных и структуры

    JTBD:
    Как анализатор документов, я хочу анализировать структуру документов 1С,
    чтобы извлекать метаданные, поля и бизнес-информацию для дальнейшей обработки.
    """

    def __init__(self):
        """Инициализация анализатора документов"""
        self.field_patterns = {
            "number": [r"_NUMBER", r"field_\d+", r".*[Nn]umber.*", r".*[Nn]um.*"],
            "date": [r"_DATE_TIME", r"_DATE", r".*[Dd]ate.*", r".*[Tt]ime.*"],
            "amount": [
                r"_FLD4239",
                r"_AMOUNT",
                r"field_3[0-9]",
                r".*[Aa]mount.*",
                r".*[Ss]um.*",
                r".*[Tt]otal.*",
            ],
            "description": [
                r"_FLD4229",
                r"_FLD4936",
                r".*[Dd]escription.*",
                r".*[Cc]omment.*",
            ],
        }

        self.business_keywords = {
            "floristic": ["флор", "цвет", "букет", "роз", "тюльпан"],
            "decor": ["декор", "украшение", "оформление"],
            "mono": ["моно", "одиночный", "простой"],
            "internet": ["интернет", "онлайн", "заказ"],
            "store": ["магазин", "склад", "пц", "южный", "чеховский"],
            "finance": ["руб", "сумма", "цена", "стоимость", "оплата"],
        }

    def analyze_document_structure(
        self, row_dict: Dict[str, Any]
    ) -> Tuple[Dict[str, FieldInfo], DocumentStructure]:
        """
        Анализ структуры документа

        Args:
            row_dict: Словарь с полями документа

        Returns:
            Tuple[Dict[str, FieldInfo], DocumentStructure]: Анализ полей и структура документа
        """
        field_analysis = {}
        structure = DocumentStructure()

        # Сохраняем оригинальные bytes для анализа BLOB
        original_bytes = {}
        for field_name, value in row_dict.items():
            if isinstance(value, bytes):
                original_bytes[field_name] = value

        # Анализируем каждое поле
        for field_name, value in row_dict.items():
            if value is not None:
                field_info = self._analyze_field(
                    field_name, value, original_bytes.get(field_name)
                )
                field_analysis[field_name] = field_info

                # Классифицируем поля по типам
                self._classify_field(field_name, field_info, structure)

        return field_analysis, structure

    def _analyze_field(
        self, field_name: str, value: Any, original_bytes: Optional[bytes] = None
    ) -> FieldInfo:
        """
        Анализ отдельного поля

        Args:
            field_name: Имя поля
            value: Значение поля
            original_bytes: Оригинальные bytes для BLOB полей

        Returns:
            FieldInfo: Информация о поле
        """
        # Определяем размер поля
        size = 0
        if isinstance(value, (str, bytes)):
            size = len(value)
        elif hasattr(value, "__len__"):
            size = len(value)

        # Проверяем, является ли поле BLOB
        is_blob = (
            hasattr(value, "value")
            and hasattr(value, "__class__")
            and "Blob" in str(type(value))
            and value.value is not None
        )

        # Проверяем, является ли поле пустым
        is_empty = (
            value is None
            or (isinstance(value, str) and not value.strip())
            or (isinstance(value, (list, dict)) and len(value) == 0)
            or (isinstance(value, bytes) and len(value) == 0)
        )

        return FieldInfo(
            name=field_name,
            value=value,
            type=type(value).__name__,
            is_numeric=isinstance(value, (int, float)),
            is_date=isinstance(value, datetime),
            is_string=isinstance(value, str),
            is_blob=is_blob,
            is_empty=is_empty,
            size=size,
        )

    def _classify_field(
        self, field_name: str, field_info: FieldInfo, structure: DocumentStructure
    ):
        """
        Классификация поля по типу

        Args:
            field_name: Имя поля
            field_info: Информация о поле
            structure: Структура документа для обновления
        """
        # Поиск полей с номерами документов
        if self._is_number_field(field_name, field_info):
            structure.number_fields.append(field_name)

        # Поиск полей с датами
        if self._is_date_field(field_name, field_info):
            structure.date_fields.append(field_name)

        # Поиск полей с суммами
        if self._is_amount_field(field_name, field_info):
            structure.amount_fields.append(field_name)

        # Поиск полей с описанием
        if self._is_description_field(field_name, field_info):
            structure.description_fields.append(field_name)

        # Поиск полей с типом продажи
        if self._is_sale_type_field(field_name, field_info):
            structure.sale_type_fields.append(field_name)

        # Поиск BLOB полей
        if field_info.is_blob:
            structure.blob_fields.append(field_name)

    def _is_number_field(self, field_name: str, field_info: FieldInfo) -> bool:
        """Проверка, является ли поле номером документа"""
        # Проверка по имени поля
        for pattern in self.field_patterns["number"]:
            if re.match(pattern, field_name, re.IGNORECASE):
                return True

        # Проверка по содержимому
        if field_info.is_string and isinstance(field_info.value, str):
            return (
                field_info.value.isdigit()
                or "№" in field_info.value
                or "N" in field_name
            )

        return False

    def _is_date_field(self, field_name: str, field_info: FieldInfo) -> bool:
        """Проверка, является ли поле датой"""
        # Проверка по имени поля
        for pattern in self.field_patterns["date"]:
            if re.match(pattern, field_name, re.IGNORECASE):
                return True

        # Проверка по типу
        if field_info.is_date:
            return True

        # Проверка по содержимому строки
        if field_info.is_string and isinstance(field_info.value, str):
            return any(
                date_indicator in field_info.value
                for date_indicator in ["2024", "2023", "2025", "-", "/"]
            )

        return False

    def _is_amount_field(self, field_name: str, field_info: FieldInfo) -> bool:
        """Проверка, является ли поле суммой"""
        # Проверка по имени поля
        for pattern in self.field_patterns["amount"]:
            if re.match(pattern, field_name, re.IGNORECASE):
                return True

        # Проверка по значению
        if field_info.is_numeric and isinstance(field_info.value, (int, float)):
            return field_info.value > 0

        # Проверка по содержимому строки
        if field_info.is_string and isinstance(field_info.value, str):
            return any(
                amount_indicator in field_name.lower()
                for amount_indicator in ["sum", "amount", "total"]
            )

        return False

    def _is_description_field(self, field_name: str, field_info: FieldInfo) -> bool:
        """Проверка, является ли поле описанием"""
        # Проверка по имени поля
        for pattern in self.field_patterns["description"]:
            if re.match(pattern, field_name, re.IGNORECASE):
                return True

        # Проверка по содержимому
        if (
            field_info.is_string
            and isinstance(field_info.value, str)
            and len(field_info.value) > 5
        ):
            return any(
                keyword in field_info.value.lower()
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

        return False

    def _is_sale_type_field(self, field_name: str, field_info: FieldInfo) -> bool:
        """Проверка, является ли поле типом продажи"""
        if field_info.is_string and isinstance(field_info.value, str):
            return any(
                keyword in str(field_info.value) for keyword in ["Розничная", "Оптовая"]
            )

        return False

    def extract_document_metadata(
        self, field_analysis: Dict[str, FieldInfo], structure: DocumentStructure
    ) -> DocumentMetadata:
        """
        Извлечение метаданных документа

        Args:
            field_analysis: Анализ полей документа
            structure: Структура документа

        Returns:
            DocumentMetadata: Метаданные документа
        """
        metadata = DocumentMetadata()

        # Извлекаем номер документа
        for field_name in structure.number_fields:
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                if field_info.is_string and isinstance(field_info.value, str):
                    metadata.document_number = field_info.value
                    break

        # Извлекаем дату документа
        for field_name in structure.date_fields:
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                if field_info.is_date and hasattr(field_info.value, "isoformat"):
                    metadata.document_date = field_info.value.isoformat()
                    break
                elif field_info.is_string and isinstance(field_info.value, str):
                    metadata.document_date = field_info.value
                    break

        # Извлекаем сумму документа
        for field_name in structure.amount_fields:
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                if field_info.is_numeric and isinstance(field_info.value, (int, float)):
                    metadata.total_amount = float(field_info.value)
                    break

        # Извлекаем тип документа и информацию о магазине
        for field_name in structure.description_fields:
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                if field_info.is_string and isinstance(field_info.value, str):
                    content = field_info.value.lower()

                    # Определяем тип документа
                    if "флор" in content:
                        metadata.document_type = "ФЛОРИСТИКА"
                    elif "декор" in content:
                        metadata.document_type = "ДЕКОР"
                    elif "моно" in content:
                        metadata.document_type = "МОНО БУКЕТ"
                    elif "интернет" in content:
                        metadata.document_type = "ИНТЕРНЕТ-ЗАКАЗ"

                    # Извлекаем название магазина
                    if "магазин" in content:
                        store_match = re.search(r"Магазин\s+([^)]+)", field_info.value)
                        if store_match:
                            metadata.store_name = store_match.group(1).strip() + ")"

                    # Извлекаем код магазина
                    store_code_match = re.search(r"ПЦ(\d+)", field_info.value)
                    if store_code_match:
                        metadata.store_code = f"ПЦ{store_code_match.group(1)}"

        # Извлекаем тип продажи
        for field_name in structure.sale_type_fields:
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                if field_info.is_string and isinstance(field_info.value, str):
                    metadata.sale_type = field_info.value
                    break

        return metadata

    def analyze_blob_content(self, blob_content: str) -> Dict[str, Any]:
        """
        Анализ содержимого BLOB поля

        Args:
            blob_content: Содержимое BLOB поля

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        analysis = {
            "has_floristic_info": False,
            "has_store_info": False,
            "has_finance_info": False,
            "colors_found": [],
            "bouquet_types_found": [],
            "stores_found": [],
        }

        content_lower = blob_content.lower()

        # Поиск цветочной информации
        for keyword in self.business_keywords["floristic"]:
            if keyword in content_lower:
                analysis["has_floristic_info"] = True
                break

        # Поиск информации о магазинах
        for keyword in self.business_keywords["store"]:
            if keyword in content_lower:
                analysis["has_store_info"] = True
                analysis["stores_found"].append(keyword)

        # Поиск финансовой информации
        for keyword in self.business_keywords["finance"]:
            if keyword in content_lower:
                analysis["has_finance_info"] = True
                break

        # Поиск цветов
        colors = ["розов", "красн", "бел", "голуб", "зелен", "желт", "фиолет", "оранж"]
        for color in colors:
            if color in content_lower:
                analysis["colors_found"].append(color)

        # Поиск типов букетов
        bouquet_types = ["моно", "букет", "композиция"]
        for bouquet_type in bouquet_types:
            if bouquet_type in content_lower:
                analysis["bouquet_types_found"].append(bouquet_type)

        return analysis

    def create_document_summary(
        self,
        field_analysis: Dict[str, FieldInfo],
        structure: DocumentStructure,
        metadata: DocumentMetadata,
    ) -> Dict[str, Any]:
        """
        Создание сводки документа

        Args:
            field_analysis: Анализ полей документа
            structure: Структура документа
            metadata: Метаданные документа

        Returns:
            Dict[str, Any]: Сводка документа
        """
        return {
            "metadata": {
                "document_number": metadata.document_number,
                "document_date": metadata.document_date,
                "document_type": metadata.document_type,
                "store_name": metadata.store_name,
                "store_code": metadata.store_code,
                "total_amount": metadata.total_amount,
                "currency": metadata.currency,
                "sale_type": metadata.sale_type,
            },
            "structure": {
                "number_fields": structure.number_fields,
                "date_fields": structure.date_fields,
                "description_fields": structure.description_fields,
                "amount_fields": structure.amount_fields,
                "sale_type_fields": structure.sale_type_fields,
                "blob_fields": structure.blob_fields,
            },
            "statistics": {
                "total_fields": len(field_analysis),
                "numeric_fields": len(
                    [f for f in field_analysis.values() if f.is_numeric]
                ),
                "string_fields": len(
                    [f for f in field_analysis.values() if f.is_string]
                ),
                "date_fields": len([f for f in field_analysis.values() if f.is_date]),
                "blob_fields": len([f for f in field_analysis.values() if f.is_blob]),
                "empty_fields": len([f for f in field_analysis.values() if f.is_empty]),
            },
        }
