#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BlobProcessor - Единый интерфейс для обработки BLOB данных
Устраняет дублирование кода между extractors
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BlobExtractionResult:
    """Результат извлечения BLOB данных"""

    content: Optional[str] = None
    extraction_methods: Optional[List[str]] = None
    content_length: int = 0
    quality_score: float = 0.0
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Инициализация после создания объекта"""
        if self.extraction_methods is None:
            self.extraction_methods = []
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


class BlobProcessor:
    """
    JTBD:
    Как система обработки BLOB данных, я хочу предоставить единый интерфейс для извлечения содержимого,
    чтобы устранить дублирование кода и обеспечить консистентность обработки.
    """

    def __init__(self) -> None:
        """Инициализация процессора BLOB данных"""
        self.methods = ["value", "iterator", "bytes", "str", "direct_data"]

    def extract_blob_content(
        self, blob_obj: Any, data_type: str = "general"
    ) -> BlobExtractionResult:
        """
        JTBD:
        Как система извлечения BLOB данных, я хочу извлечь содержимое BLOB объекта,
        чтобы получить читаемые данные для анализа.

        Args:
            blob_obj: BLOB объект для извлечения
            data_type: Тип данных ('flower', 'temporal', 'financial', 'general')

        Returns:
            BlobExtractionResult: Результат извлечения
        """
        result = BlobExtractionResult()
        if result.metadata is not None:
            result.metadata["data_type"] = data_type
            result.metadata["extraction_timestamp"] = datetime.now().isoformat()

        # Пробуем все методы извлечения
        for method in self.methods:
            try:
                if method == "value":
                    success = self._try_value_method(blob_obj, result)
                elif method == "iterator":
                    success = self._try_iterator_method(blob_obj, result)
                elif method == "bytes":
                    success = self._try_bytes_method(blob_obj, result)
                elif method == "str":
                    success = self._try_str_method(blob_obj, result)
                elif method == "direct_data":
                    success = self._try_direct_data_method(blob_obj, result)

                if success and result.content:
                    if result.extraction_methods is not None:
                        result.extraction_methods.append(method)
                    break

            except Exception as e:
                if result.errors is not None:
                    result.errors.append(f"{method}: {str(e)}")

        # Рассчитываем качество
        if result.content:
            result.content_length = len(result.content)
            result.quality_score = self._calculate_quality_score(result, data_type)

        return result

    def _try_value_method(self, blob_obj: Any, result: BlobExtractionResult) -> bool:
        """Попытка извлечения через value атрибут"""
        try:
            if hasattr(blob_obj, "value"):
                value = blob_obj.value
                # Проверяем что value не является Mock объектом
                if (
                    value is not None
                    and not str(value).startswith("<Mock")
                    and str(value).strip()
                ):
                    result.content = str(value)
                    return True
        except Exception as e:
            if result.errors is None:
                result.errors = []
            result.errors.append(f"value method error: {str(e)}")
        return False

    def _try_iterator_method(self, blob_obj: Any, result: BlobExtractionResult) -> bool:
        """Попытка извлечения через итератор"""
        try:
            if hasattr(blob_obj, "__iter__") and not hasattr(blob_obj, "value"):
                content_parts = []
                for item in blob_obj:
                    content_parts.append(str(item))
                if content_parts:
                    result.content = "\n".join(content_parts)
                    return True
        except StopIteration:
            # StopIteration - это нормальное завершение итератора, не ошибка
            pass
        except Exception as e:
            if result.errors is not None:
                result.errors.append(f"iterator method error: {str(e)}")
        return False

    def _try_bytes_method(self, blob_obj: Any, result: BlobExtractionResult) -> bool:
        """Попытка извлечения через bytes"""
        try:
            if hasattr(blob_obj, "__bytes__") and not hasattr(blob_obj, "value"):
                bytes_data = blob_obj.__bytes__()
                if bytes_data:
                    result.content = bytes_data.decode("utf-8", errors="ignore")
                    return True
        except Exception as e:
            if result.errors is not None:
                result.errors.append(f"bytes method error: {str(e)}")
        return False

    def _try_str_method(self, blob_obj: Any, result: BlobExtractionResult) -> bool:
        """Попытка извлечения через str"""
        try:
            if hasattr(blob_obj, "__str__") and not hasattr(blob_obj, "value"):
                content = str(blob_obj)
                if (
                    content
                    and content != str(type(blob_obj))
                    and not content.startswith("<Mock")
                ):
                    result.content = content
                    return True
        except Exception as e:
            if result.errors is not None:
                result.errors.append(f"str method error: {str(e)}")
        return False

    def _try_direct_data_method(
        self, blob_obj: Any, result: BlobExtractionResult
    ) -> bool:
        """Попытка извлечения через _data атрибут"""
        try:
            if hasattr(blob_obj, "_data") and not hasattr(blob_obj, "value"):
                data = blob_obj._data
                if data is not None and str(data).strip():
                    result.content = str(data)
                    return True
        except Exception as e:
            if result.errors is not None:
                result.errors.append(f"direct_data method error: {str(e)}")
        return False

    def _calculate_quality_score(
        self, result: BlobExtractionResult, data_type: str
    ) -> float:
        """Расчет оценки качества извлечения"""
        score = 0.0

        # Базовый счет за длину контента
        if result.content_length > 0:
            score += min(result.content_length / 100.0, 0.3)

        # Бонус за количество методов
        if result.extraction_methods is not None and len(result.extraction_methods) > 1:
            score += 0.2

        # Штраф за ошибки
        if result.errors:
            score -= min(len(result.errors) * 0.1, 0.3)

        # Специализированные бонусы
        if data_type == "flower" and result.content:
            score += self._calculate_flower_quality_bonus(result.content)
        elif data_type == "temporal" and result.content:
            score += self._calculate_temporal_quality_bonus(result.content)
        elif data_type == "financial" and result.content:
            score += self._calculate_financial_quality_bonus(result.content)

        return max(0.0, min(1.0, score))

    def _calculate_flower_quality_bonus(self, content: str) -> float:
        """Бонус качества для данных о цветах"""
        if not content:
            return 0.0

        bonus = 0.0
        flower_keywords = ["роз", "тюльпан", "гвоздик", "цвет", "букет"]
        for keyword in flower_keywords:
            if keyword in content.lower():
                bonus += 0.1

        return min(bonus, 0.3)

    def _calculate_temporal_quality_bonus(self, content: str) -> float:
        """Бонус качества для временных данных"""
        if not content:
            return 0.0

        bonus = 0.0
        temporal_keywords = ["дата", "время", "период", "год", "месяц", "день"]
        for keyword in temporal_keywords:
            if keyword in content.lower():
                bonus += 0.1

        return min(bonus, 0.3)

    def _calculate_financial_quality_bonus(self, content: str) -> float:
        """Бонус качества для финансовых данных"""
        if not content:
            return 0.0

        bonus = 0.0
        financial_keywords = ["сумма", "рубл", "доллар", "евро", "цена", "стоимость"]
        for keyword in financial_keywords:
            if keyword in content.lower():
                bonus += 0.1

        return min(bonus, 0.3)

    def is_blob_field(self, field_value: Any) -> bool:
        """
        JTBD:
        Как система определения типов полей, я хочу проверить является ли поле BLOB полем,
        чтобы правильно обработать его содержимое.

        Args:
            field_value: Значение поля

        Returns:
            bool: True если поле является BLOB полем
        """
        return str(field_value).startswith("<onec_dtools.database_reader.Blob")

    def safe_get_blob_content(self, value: Any) -> Optional[str]:
        """
        JTBD:
        Как система безопасного извлечения, я хочу извлечь содержимое BLOB поля без ошибок,
        чтобы получить данные для анализа.

        Args:
            value: BLOB объект из onec_dtools

        Returns:
            str: Содержимое BLOB поля или None если не удалось извлечь
        """
        result = self.extract_blob_content(value)
        return result.content if result.content else None


# Глобальный экземпляр для обратной совместимости
blob_processor = BlobProcessor()


def safe_get_blob_content(value: Any) -> Optional[str]:
    """
    JTBD:
    Как система обратной совместимости, я хочу предоставить старый интерфейс для извлечения BLOB данных,
    чтобы не сломать существующий код.

    Args:
        value: BLOB объект для извлечения

    Returns:
        str: Содержимое BLOB поля или None
    """
    return blob_processor.safe_get_blob_content(value)


def is_blob_field(field_value: Any) -> bool:
    """
    JTBD:
    Как система обратной совместимости, я хочу предоставить старый интерфейс для проверки BLOB полей,
    чтобы не сломать существующий код.

    Args:
        field_value: Значение поля

    Returns:
        bool: True если поле является BLOB полем
    """
    return blob_processor.is_blob_field(field_value)
