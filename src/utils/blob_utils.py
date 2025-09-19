#!/usr/bin/env python3

"""
Общие утилиты для работы с BLOB данными в 1С
Устраняет дублирование кода между extractors
Интегрирован с новым BlobProcessor для обратной совместимости
"""

from typing import Any

from src.utils import blob_processor


def safe_get_blob_content(value: Any) -> str | None:
    """
    JTBD:
    Как система обратной совместимости, я хочу предоставить старый интерфейс для извлечения BLOB данных,
    чтобы не сломать существующий код.

    Args:
        value: BLOB объект из onec_dtools

    Returns:
        str: Содержимое BLOB поля или None если не удалось извлечь
    """
    result = blob_processor.safe_get_blob_content(value)
    return result if result is not None else None


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


def extract_blob_content_safe(record_data: dict, field_name: str) -> str | None:
    """
    Безопасно извлекает содержимое BLOB поля из записи

    Args:
        record_data: Словарь с данными записи
        field_name: Имя поля

    Returns:
        str: Содержимое BLOB поля или None
    """
    if field_name not in record_data:
        return None

    field_value = record_data[field_name]

    if not is_blob_field(field_value):
        return None

    return safe_get_blob_content(field_value)


def get_blob_fields_from_record(record_data: dict) -> list:
    """
    Возвращает список BLOB полей из записи

    Args:
        record_data: Словарь с данными записи

    Returns:
        list: Список имен BLOB полей
    """
    blob_fields = []
    for field_name, field_value in record_data.items():
        if is_blob_field(field_value):
            blob_fields.append(field_name)
    return blob_fields
