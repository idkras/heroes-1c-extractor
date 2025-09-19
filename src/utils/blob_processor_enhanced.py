#!/usr/bin/env python3

"""
BlobProcessorEnhanced - улучшенный обработчик BLOB полей
Выделен из extract_all_available_data.py для упрощения основного кода
"""

from typing import Any


class BlobProcessorEnhanced:
    """
    JTBD:
    Как система обработки BLOB полей, я хочу предоставить улучшенную
    функциональность для обработки BLOB полей 1С, чтобы упростить
    extract_all_available_data.py и улучшить качество извлечения данных.
    """

    def __init__(self) -> None:
        self.processing_stats: dict[str, Any] = {
            "total_blobs_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extraction_methods_used": {},
        }

    def process_blob_fields(self, row_dict: dict[str, Any]) -> dict[str, Any]:
        """
        JTBD:
        Как система обработки BLOB полей, я хочу обработать все BLOB поля
        в записи с множественными методами извлечения, чтобы получить
        максимально полную информацию из BLOB данных.
        """
        blob_data = {}
        processed_blobs = set()

        for field_name, value in row_dict.items():
            if self._is_blob_field(value) and field_name not in processed_blobs:
                try:
                    blob_info = self._extract_blob_content(value, field_name)
                    if blob_info:
                        blob_data[field_name] = blob_info
                        processed_blobs.add(field_name)
                        total_processed: int = self.processing_stats.get(
                            "total_blobs_processed",
                            0,
                        )
                        self.processing_stats["total_blobs_processed"] = (
                            total_processed + 1
                        )

                        if blob_info.get("extraction_methods"):
                            successful: int = self.processing_stats.get(
                                "successful_extractions",
                                0,
                            )
                            self.processing_stats["successful_extractions"] = (
                                successful + 1
                            )
                        else:
                            failed: int = self.processing_stats.get(
                                "failed_extractions",
                                0,
                            )
                            self.processing_stats["failed_extractions"] = failed + 1

                except Exception as e:
                    print(f"   ⚠️ Ошибка обработки BLOB поля {field_name}: {e}")
                    failed_count: int = self.processing_stats.get(
                        "failed_extractions",
                        0,
                    )
                    self.processing_stats["failed_extractions"] = failed_count + 1
                    continue

        return blob_data

    def _is_blob_field(self, value: Any) -> bool:
        """
        JTBD:
        Как система определения BLOB поля, я хочу определить является ли
        поле BLOB полем, чтобы правильно обработать его содержимое.
        """
        if value is None:
            return False

        # Проверяем тип объекта
        if hasattr(value, "__class__") and "Blob" in str(type(value)):
            return True

        # Проверяем наличие value атрибута (характерно для BLOB полей)
        if hasattr(value, "value"):
            return True

        return False

    def _extract_blob_content(self, value: Any, field_name: str) -> dict[str, Any]:
        """
        JTBD:
        Как система извлечения содержимого BLOB, я хочу извлечь содержимое
        BLOB поля с множественными методами декодирования, чтобы получить
        максимально полную информацию.
        """
        blob_info: dict[str, Any] = {
            "field_type": "blob",
            "field_name": field_name,
            "size": len(value) if hasattr(value, "__len__") else 0,
            "extraction_methods": [],
            "content": {},
        }

        # Метод 1: value атрибут (самый надежный)
        if hasattr(value, "value"):
            try:
                content = value.value
                if content:
                    decoded_content = self._decode_blob_content(content)
                    if decoded_content:
                        blob_info["content"]["value"] = decoded_content
                        methods_list: list[str] = blob_info["extraction_methods"]
                        methods_list.append("value")
                        self._update_method_stats("value")
            except Exception as e:
                blob_info["value_error"] = str(e)

        # Метод 2: bytes обработка
        if isinstance(value, bytes):
            try:
                decoded_content = self._decode_bytes_content(value)
                if decoded_content:
                    blob_info["content"]["bytes"] = decoded_content
                    methods_bytes: list[str] = blob_info["extraction_methods"]
                    methods_bytes.append("bytes")
                    self._update_method_stats("bytes")
            except Exception as e:
                blob_info["bytes_error"] = str(e)

        # Метод 3: итератор (если доступен)
        if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            try:
                iterator_content = self._extract_from_iterator(value)
                if iterator_content:
                    blob_info["content"]["iterator"] = iterator_content
                    methods_iter: list[str] = blob_info["extraction_methods"]
                    methods_iter.append("iterator")
                    self._update_method_stats("iterator")
            except Exception as e:
                blob_info["iterator_error"] = str(e)

        return blob_info

    def _decode_blob_content(self, content: Any) -> dict[str, Any] | None:
        """
        JTBD:
        Как система декодирования BLOB содержимого, я хочу декодировать
        содержимое BLOB поля с множественными кодировками, чтобы получить
        читаемый текст.
        """
        if not content:
            return None

        if isinstance(content, bytes):
            # Пробуем разные кодировки
            encodings = ["utf-16", "utf-8", "cp1251", "latin1"]

            for encoding in encodings:
                try:
                    decoded_text = content.decode(encoding)
                    return {
                        "content": decoded_text,
                        "encoding": encoding,
                        "length": len(decoded_text),
                        "type": "text",
                    }
                except UnicodeDecodeError:
                    continue

            # Если не удалось декодировать, возвращаем hex
            return {
                "content": content.hex(),
                "encoding": "hex",
                "length": len(content),
                "type": "binary",
            }
        return {
            "content": str(content),
            "encoding": "string",
            "length": len(str(content)),
            "type": "string",
        }

    def _decode_bytes_content(self, content: bytes) -> dict[str, Any] | None:
        """
        JTBD:
        Как система декодирования bytes содержимого, я хочу декодировать
        bytes данные с множественными кодировками, чтобы получить
        читаемый текст.
        """
        if not content:
            return None

        # Пробуем разные кодировки
        encodings = ["utf-8", "cp1251", "latin1", "utf-16"]

        for encoding in encodings:
            try:
                decoded_text = content.decode(encoding)
                return {
                    "content": decoded_text,
                    "encoding": encoding,
                    "length": len(decoded_text),
                    "type": "text",
                }
            except UnicodeDecodeError:
                continue

        # Если не удалось декодировать, возвращаем hex
        return {
            "content": content.hex(),
            "encoding": "hex",
            "length": len(content),
            "type": "binary",
        }

    def _extract_from_iterator(self, value: Any) -> dict[str, Any] | None:
        """
        JTBD:
        Как система извлечения из итератора, я хочу извлечь содержимое
        из итератора BLOB поля, чтобы получить дополнительную информацию.
        """
        try:
            iterator_content = []
            for item in value:
                if hasattr(item, "value"):
                    iterator_content.append(str(item.value))
                else:
                    iterator_content.append(str(item))

            if iterator_content:
                return {
                    "content": "".join(iterator_content),
                    "type": "iterator",
                    "length": len("".join(iterator_content)),
                }
        except Exception:
            pass

        return None

    def _update_method_stats(self, method: str) -> None:
        """Обновить статистику методов извлечения"""
        methods_used: dict[str, int] = self.processing_stats["extraction_methods_used"]
        if method not in methods_used:
            methods_used[method] = 0
        methods_used[method] += 1

    def get_processing_stats(self) -> dict[str, Any]:
        """Получить статистику обработки"""
        return self.processing_stats.copy()

    def reset_stats(self) -> None:
        """Сбросить статистику обработки"""
        self.processing_stats = {
            "total_blobs_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extraction_methods_used": {},
        }
