#!/usr/bin/env python3
"""
BlobProcessor - обработка BLOB полей из 1С базы данных.

JTBD:
Как система обработки BLOB данных, я хочу декодировать и анализировать бинарные поля,
чтобы извлечь текстовую информацию из BLOB полей 1С.
"""

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

    def __init__(self):
        """Инициализация процессора BLOB данных."""
        self.processed_blobs = set()  # Отслеживаем уже обработанные BLOB поля

    def process_blob_field(self, field_name: str, value: Any) -> dict[str, Any]:
        """
        JTBD:
        Как процессор BLOB поля, я хочу обработать бинарное поле,
        чтобы извлечь текстовую информацию с метаданными.

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
            # Проверяем тип BLOB объекта
            if self._is_blob_object(value):
                blob_data["size"] = self._get_blob_size(value)

                # Метод 1: value (правильная обработка BLOB согласно onec_dtools API)
                if hasattr(value, "value"):
                    try:
                        content = value.value
                        if content:
                            decoded_result = self._decode_blob_content(content)
                            if decoded_result:
                                blob_data["value"] = decoded_result
                                blob_data["extraction_methods"].append("value")
                    except Exception as e:
                        blob_data["value_error"] = f"Ошибка извлечения: {e}"

                # Метод 2: bytes (если value это bytes)
                if isinstance(value, bytes):
                    decoded_result = self._decode_bytes(value)
                    if decoded_result:
                        blob_data["bytes"] = decoded_result
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

    def _decode_blob_content(self, content: bytes) -> dict[str, Any] | None:
        """
        JTBD:
        Как декодер BLOB контента, я хочу декодировать бинарные данные в текст,
        чтобы извлечь читаемую информацию из BLOB полей.
        """
        if not isinstance(content, bytes):
            return {
                "content": str(content),
                "type": type(content).__name__,
                "length": len(str(content)),
            }

        # Правильное декодирование: UTF-16 для NT полей, затем UTF-8, CP1251
        for encoding in ["utf-16", "utf-8", "cp1251"]:
            try:
                decoded_content = content.decode(encoding)
                if len(decoded_content.strip()) > 0:
                    return {
                        "content": decoded_content,
                        "type": f"text_{encoding.replace('-', '')}",
                        "length": len(decoded_content),
                        "raw_bytes": content.hex()[:100],
                    }
            except UnicodeDecodeError:
                continue

        # Если не удалось декодировать как текст, возвращаем hex
        return {
            "content": content.hex(),
            "type": "binary_hex",
            "length": len(content),
            "raw_bytes": content.hex()[:100],
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
        result = {"store_name": None, "store_code": None}

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
