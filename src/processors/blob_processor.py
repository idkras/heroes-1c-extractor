#!/usr/bin/env python3
"""
BlobProcessor - обработка BLOB полей из 1С базы данных.

JTBD:
Как система обработки BLOB данных, я хочу декодировать и анализировать бинарные поля,
чтобы извлечь текстовую информацию из BLOB полей 1С.
"""

import ast
import re
from typing import Any

# from typing import List, Union  # Неиспользуемые импорты
# from datetime import datetime  # Неиспользуемые импорты


class BlobProcessor:
    """
    JTBD:
    Как процессор BLOB данных, я хочу обрабатывать бинарные поля из 1С,
    чтобы извлекать текстовую информацию с правильным декодированием.
    """

    def __init__(self) -> None:
        """Инициализация процессора BLOB данных."""
        self.processed_blobs: set[str] = set()  # Отслеживаем уже обработанные BLOB поля

    def process_blob_field(self, field_name: str, value: Any) -> dict[str, Any]:
        """
        JTBD:
        Как процессор BLOB поля, я хочу обработать бинарное поле,
        чтобы извлечь текстовую информацию с метаданными.

        ИСПРАВЛЕНО согласно стандарту 1С:
        - Правильная обработка onec_dtools BLOB объектов
        - UTF-16 для NT полей (стандарт 1С)
        - Защита от больших файлов

        Args:
            field_name: Имя поля
            value: Значение поля (может быть BLOB объектом или bytes)

        Returns:
            Словарь с результатами обработки BLOB поля
        """
        blob_data = {
            "field_type": "blob",
            "size": 0,
            "extraction_methods": [],
            "field_name": field_name,
        }

        try:
            # ИСПРАВЛЕНО: Проверяем размер BLOB (защита от больших файлов)
            if hasattr(value, "__len__"):
                blob_size = len(value)
                if blob_size == 0:
                    return {
                        **blob_data,
                        "content": "",
                        "type": "empty_blob",
                        "size": 0,
                        "extraction_methods": ["empty_check"],
                    }
                elif blob_size > 100 * 1024 * 1024:  # 100MB
                    return {
                        **blob_data,
                        "content": f"BLOB слишком большой: {blob_size} байт",
                        "type": "large_blob",
                        "size": blob_size,
                        "extraction_methods": ["size_check"],
                    }

            # Проверяем тип BLOB объекта
            if self._is_blob_object(value):
                blob_data["size"] = self._get_blob_size(value)

                # ИСПРАВЛЕНО: Правильная обработка BLOB согласно onec_dtools API
                if hasattr(value, "value"):
                    try:
                        blob_value = value.value

                        # ИСПРАВЛЕНО: Обрабатываем в зависимости от типа данных
                        if isinstance(blob_value, bytes):
                            # Для бинарных данных пробуем UTF-16 (стандарт для NT полей)
                            decoded_result = self._decode_blob_content(blob_value)
                            if decoded_result:
                                blob_data["value"] = decoded_result
                                if isinstance(blob_data["extraction_methods"], list):
                                    blob_data["extraction_methods"].append(
                                        "onec_dtools_utf16"
                                    )
                        elif isinstance(blob_value, str):
                            # Для строковых данных
                            if blob_value and len(blob_value.strip()) > 0:
                                blob_data["value"] = {
                                    "content": blob_value,
                                    "type": "string_value",
                                    "length": len(blob_value),
                                    "encoding": "string",
                                }
                                if isinstance(blob_data["extraction_methods"], list):
                                    blob_data["extraction_methods"].append(
                                        "string_value"
                                    )
                        else:
                            # Для других типов конвертируем в строку
                            content = str(blob_value)
                            if content and len(content.strip()) > 0:
                                blob_data["value"] = {
                                    "content": content,
                                    "type": "converted_string",
                                    "length": len(content),
                                    "encoding": "converted",
                                }
                                if isinstance(blob_data["extraction_methods"], list):
                                    blob_data["extraction_methods"].append(
                                        "converted_string"
                                    )

                    except Exception as e:
                        blob_data["value_error"] = f"Ошибка извлечения: {e}"

                # Метод 2: bytes (если value это bytes)
                if isinstance(value, bytes):
                    decoded_result = self._decode_bytes(value)
                    if decoded_result:
                        blob_data["bytes"] = decoded_result
                        if isinstance(blob_data["extraction_methods"], list):
                            blob_data["extraction_methods"].append("bytes")

            # Если ни один метод не сработал
            if not blob_data.get("extraction_methods"):
                blob_data["error"] = "No extraction method worked"

        except Exception as e:
            blob_data["error"] = f"Ошибка обработки BLOB: {e}"

        return blob_data

    def _is_blob_object(self, value: Any) -> bool:
        """
        JTBD:
        Как анализатор типов, я хочу определить является ли объект BLOB полем,
        чтобы правильно обработать бинарные данные.
        """
        return (
            hasattr(value, "value")
            and hasattr(value, "__class__")
            and ("Blob" in str(type(value)) or "Blob" in str(value.__class__))
        ) or isinstance(value, bytes)

    def _get_blob_size(self, value: Any) -> int:
        """Получить размер BLOB данных."""
        if hasattr(value, "__len__"):
            return len(value)
        if hasattr(value, "value") and hasattr(value.value, "__len__"):
            return len(value.value)
        if hasattr(value, "value"):
            return len(str(value.value))
        return 0

    def _normalize_bytes(self, x: Any) -> Any:
        """
        Нормализация bytes из строковых представлений

        Args:
            x: Входные данные для нормализации

        Returns:
            Нормализованные bytes или исходные данные
        """
        if isinstance(x, (bytes, bytearray)):
            return bytes(x)
        if isinstance(x, str) and x.startswith("b'") and x.endswith("'"):
            try:
                y = ast.literal_eval(x)  # вернёт bytes
                if isinstance(y, (bytes, bytearray)):
                    return bytes(y)
            except Exception:
                pass
        return x

    def _guess_1c_blob_kind(self, b: bytes) -> str | None:
        """
        Распознает тип BLOB поля по сигнатурам 1С

        Args:
            b: Байты для анализа

        Returns:
            Тип BLOB или None
        """
        # Проверяем тип входных данных
        if isinstance(b, (bytes, bytearray)):
            # Конвертируем в bytes для анализа
            blob_bytes = bytes(b)

            # Частая «магия» 1С: 0x80 0xFD и «PV» в заголовке
            if (
                len(blob_bytes) >= 5
                and blob_bytes[0:2] == b"\x80\xfd"
                and blob_bytes[3:5] == b"PV"
            ):
                return "1c_presentation_value"

        return None

    def _decode_blob_content(self, content: Any) -> dict[str, Any] | None:
        """
        JTBD:
        Как декодер BLOB контента, я хочу декодировать бинарные данные в текст,
        чтобы извлечь читаемую информацию из BLOB полей.

        ИСПРАВЛЕНО согласно стандарту 1С:
        - Нормализация входных данных (str(bytes) -> bytes)
        - Детекция сигнатур 1С (\x80\xfd\x00PV)
        - UTF-16 для NT полей (стандарт 1С)
        - Правильная обработка onec_dtools BLOB объектов
        """
        # ИСПРАВЛЕНО: Нормализация входных данных
        x = self._normalize_bytes(content)

        if not isinstance(x, bytes):
            return {
                "content": str(x),
                "type": type(x).__name__,
                "length": len(str(x)),
            }

        # ИСПРАВЛЕНО: Сначала проверяем сигнатуры 1С
        kind = self._guess_1c_blob_kind(x)
        if kind == "1c_presentation_value":
            import base64

            return {
                "content": base64.b64encode(x).decode("ascii"),
                "type": "1c_binary",
                "encoding": "base64",
                "length": len(x),
                "note": "Внутренний контейнер 1С, требуется десериализация onec_dtools",
            }

        # ИСПРАВЛЕНО: UTF-16 для NT полей (стандарт 1С), затем UTF-8, CP1251
        # Согласно стандарту 1С: UTF-16 для NT полей, затем fallback
        try:
            # Сначала UTF-16 (стандарт для NT полей в 1С)
            decoded_content = x.decode("utf-16")
            if decoded_content and len(decoded_content.strip()) > 0:
                return {
                    "content": decoded_content,
                    "type": "text_utf16_nt_field",
                    "length": len(decoded_content),
                    "raw_bytes": x.hex()[:100],
                    "encoding": "utf-16",
                    "is_nt_field": True,
                }
        except UnicodeDecodeError:
            pass

        # Fallback на другие кодировки
        for encoding in ["utf-8", "cp1251", "latin1"]:
            try:
                decoded_content = x.decode(encoding)
                if decoded_content and len(decoded_content.strip()) > 0:
                    return {
                        "content": decoded_content,
                        "type": f"text_{encoding.replace('-', '')}",
                        "length": len(decoded_content),
                        "raw_bytes": x.hex()[:100],
                        "encoding": encoding,
                        "is_nt_field": False,
                    }
            except UnicodeDecodeError:
                continue

        # Если не удалось декодировать как текст, возвращаем hex
        return {
            "content": x.hex(),
            "type": "binary_hex",
            "length": len(x),
            "raw_bytes": x.hex()[:100],
            "encoding": "hex",
            "is_nt_field": False,
        }

    def _decode_bytes(self, blob_bytes: bytes) -> dict[str, Any] | None:
        """
        JTBD:
        Как декодер bytes, я хочу декодировать бинарные данные в текст,
        чтобы извлечь текстовую информацию из bytes объектов.
        """
        for encoding in ["utf-8", "cp1251", "utf-16"]:
            try:
                content = blob_bytes.decode(encoding)
                if len(content.strip()) > 0:
                    return {
                        "content": content,
                        "type": f"bytes_{encoding.replace('-', '')}",
                        "length": len(content),
                    }
            except UnicodeDecodeError:
                continue

        # Если не удалось декодировать, возвращаем hex
        return {
            "content": blob_bytes.hex(),
            "type": "bytes_hex",
            "length": len(blob_bytes),
        }

    def analyze_blob_type(self, blob_bytes: bytes) -> str:
        """
        JTBD:
        Как анализатор типов файлов, я хочу определить тип BLOB данных по заголовкам,
        чтобы правильно обработать различные форматы файлов.
        """
        if blob_bytes.startswith(b"\xff\xd8\xff"):
            return "JPEG"
        if blob_bytes.startswith(b"\x89PNG"):
            return "PNG"
        if blob_bytes.startswith(b"GIF"):
            return "GIF"
        if blob_bytes.startswith(b"\x00\x00\x01\x00"):
            return "ICO"
        if blob_bytes.startswith(b"%PDF"):
            return "PDF"
        if blob_bytes.startswith(b"PK"):
            return "ZIP/Office"
        return "unknown"

    def extract_flower_information(self, content: str) -> dict[str, bool]:
        """
        JTBD:
        Как анализатор цветочной информации, я хочу найти ключевые слова о цветах,
        чтобы идентифицировать цветочную информацию в BLOB данных.
        """
        content_lower = content.lower()

        return {
            "has_flower_info": any(
                keyword in content_lower
                for keyword in ["цвет", "rose", "тюльпан", "флор", "букет"]
            ),
            "has_store_info": any(
                keyword in content_lower
                for keyword in ["магазин", "склад", "поставщик"]
            ),
            "has_financial_info": any(
                keyword in content_lower for keyword in ["сумма", "цена", "стоимость"]
            ),
        }

    def extract_store_information(self, content: str) -> dict[str, str | None]:
        """
        JTBD:
        Как извлекатель информации о магазине, я хочу найти название и код магазина,
        чтобы извлечь информацию о торговой точке из BLOB данных.
        """
        result: dict[str, str | None] = {"store_name": None, "store_code": None}

        # Извлекаем название магазина
        store_match = re.search(r"Магазин\s+([^ПЦ]+?)(?:\s+ПЦ|$)", content)
        if store_match:
            result["store_name"] = store_match.group(1).strip()
        else:
            # Fallback: ищем просто "Магазин" + следующее слово
            store_match = re.search(r"Магазин\s+(\w+)", content)
            if store_match:
                result["store_name"] = store_match.group(1)

        # Извлекаем коды магазинов
        store_code_match = re.search(r"ПЦ(\d+)", content)
        if store_code_match:
            result["store_code"] = f"ПЦ{store_code_match.group(1)}"

        return result

    def determine_document_type(self, content: str) -> str:
        """
        JTBD:
        Как классификатор документов, я хочу определить тип документа по содержимому,
        чтобы правильно категоризировать документы.
        """
        content_lower = content.lower()

        if "флор" in content_lower:
            return "ФЛОРИСТИКА"
        if "декор" in content_lower:
            return "ДЕКОР"
        if "моно" in content_lower:
            return "МОНО БУКЕТ"
        if "интернет" in content_lower:
            return "ИНТЕРНЕТ-ЗАКАЗ"
        return "Неизвестно"

    def enhanced_safe_get_blob_content(self, blob_obj: Any) -> str:
        """
        ИСПРАВЛЕННАЯ функция извлечения BLOB данных согласно стандарту 1С.

        JTBD:
        Как извлекатель BLOB данных, я хочу правильно извлекать содержимое BLOB полей,
        чтобы получить читаемую информацию с правильной кодировкой UTF-16 для NT полей.

        ИСПРАВЛЕНО согласно стандарту 1С:
        - UTF-16 для NT полей (стандарт 1С)
        - Защита от больших файлов
        - Правильная обработка onec_dtools BLOB объектов
        """
        try:
            # ИСПРАВЛЕНО: Проверяем размер BLOB (защита от больших файлов)
            if hasattr(blob_obj, "__len__"):
                blob_size = len(blob_obj)
                if blob_size == 0:
                    return ""  # Пустой BLOB
                elif blob_size > 100 * 1024 * 1024:  # 100MB
                    return f"BLOB слишком большой: {blob_size} байт"

            # ИСПРАВЛЕНО: Получаем значение BLOB согласно onec_dtools API
            if hasattr(blob_obj, "value"):
                blob_value = blob_obj.value

                # ИСПРАВЛЕНО: Обрабатываем в зависимости от типа данных
                if isinstance(blob_value, bytes):
                    # Для бинарных данных пробуем UTF-16 (стандарт для NT полей)
                    try:
                        content = blob_value.decode("utf-16")
                        if content and len(content.strip()) > 0:
                            return content
                    except UnicodeDecodeError:
                        pass

                    # Если UTF-16 не сработал, пробуем другие кодировки
                    for encoding in ["utf-8", "cp1251", "latin1"]:
                        try:
                            content = blob_value.decode(encoding)
                            if content and len(content.strip()) > 0:
                                return content
                        except UnicodeDecodeError:
                            continue

                    # Если все кодировки не сработали, используем hex
                    return blob_value.hex()

                elif isinstance(blob_value, str):
                    # Для строковых данных
                    if blob_value and len(blob_value.strip()) > 0:
                        return blob_value

                else:
                    # Для других типов конвертируем в строку
                    content = str(blob_value)
                    if content and len(content.strip()) > 0:
                        return content

        except Exception as e:
            return f"Ошибка чтения BLOB: {e}"

        return "Не удалось извлечь содержимое BLOB"
