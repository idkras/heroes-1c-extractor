#!/usr/bin/env python3

"""
BlobProcessor - централизованная обработка BLOB полей в 1С
Использует onec_dtools для правильного извлечения BLOB данных
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class BlobExtractionResult:
    """
    Результат извлечения BLOB данных
    """

    def __init__(self, data: Dict[str, Any]):
        self.field_name = data.get("field_name", "")
        self.context = data.get("context", "")
        self.content = data.get("content", None)
        self.content_type = data.get("content_type", "unknown")
        self.content_length = data.get("content_length", 0)
        self.quality_score = data.get("quality_score", 0.0)
        self.errors = data.get("errors", [])
        self.metadata = data.get("metadata", {})
        self.extraction_methods = data.get("extraction_methods", [])

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "field_name": self.field_name,
            "context": self.context,
            "content": self.content,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "quality_score": self.quality_score,
            "errors": self.errors,
            "metadata": self.metadata,
            "extraction_methods": self.extraction_methods,
        }


class BlobProcessor:
    """
    Централизованный процессор BLOB данных для 1С

    JTBD:
    Как система обработки BLOB данных, я хочу централизовать извлечение
    всех BLOB полей с использованием onec_dtools, чтобы устранить дублирование
    и обеспечить единую архитектуру обработки.
    """

    def __init__(self) -> None:
        """
        Инициализация BlobProcessor
        """
        self.extraction_methods = [
            "onec_dtools_utf16",
            "onec_dtools_utf8",
            "onec_dtools_cp1251",
            "fallback_hex",
        ]

        self.stats: Dict[str, Any] = {
            "total_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "method_usage": {},
            "encoding_stats": {},
        }

    def extract_blob_content(
        self, blob_obj: Any, context: str = "", field_name: str = ""
    ) -> BlobExtractionResult:
        """
        Извлечение BLOB содержимого с множественными методами

        Args:
            blob_obj: BLOB объект из onec_dtools
            context: Контекст извлечения (например, "document", "reference")
            field_name: Имя поля для диагностики

        Returns:
            Словарь с результатами извлечения
        """
        self.stats["total_processed"] += 1

        result: Dict[str, Any] = {
            "field_name": field_name,
            "context": context,
            "extraction_methods": [],
            "content": None,
            "content_type": "unknown",
            "content_length": 0,
            "quality_score": 0.0,
            "errors": [],
            "metadata": {
                "extraction_time": datetime.now().isoformat(),
                "blob_type": type(blob_obj).__name__,
                "blob_size": 0,
            },
        }

        try:
            # Проверяем размер BLOB
            if hasattr(blob_obj, "__len__"):
                blob_size = len(blob_obj)
                result["metadata"]["blob_size"] = blob_size

                if blob_size == 0:
                    result["content"] = ""
                    result["content_type"] = "empty"
                    result["quality_score"] = 0.0
                    result["extraction_methods"].append("empty_blob")
                    return BlobExtractionResult(result)
                elif blob_size > 100 * 1024 * 1024:  # 100MB
                    result["errors"].append(f"BLOB слишком большой: {blob_size} байт")
                    result["content"] = f"BLOB слишком большой: {blob_size} байт"
                    result["content_type"] = "oversized"
                    return BlobExtractionResult(result)

            # Получаем значение BLOB
            if hasattr(blob_obj, "value"):
                blob_value = blob_obj.value

                # Обрабатываем в зависимости от типа данных
                if isinstance(blob_value, bytes):
                    # Для бинарных данных пробуем UTF-16 (стандарт для NT полей)
                    try:
                        content = blob_value.decode("utf-16")
                        if content and len(content.strip()) > 0:
                            result["content"] = content
                            result["content_type"] = "text_utf16"
                            result["content_length"] = len(content)
                            result["quality_score"] = 0.9
                            result["extraction_methods"].append("onec_dtools_utf16")
                            self.stats["successful_extractions"] += 1
                            self.stats["method_usage"]["onec_dtools_utf16"] = (
                                self.stats["method_usage"].get("onec_dtools_utf16", 0)
                                + 1
                            )
                            self.stats["encoding_stats"]["utf16"] = (
                                self.stats["encoding_stats"].get("utf16", 0) + 1
                            )
                            return BlobExtractionResult(result)
                    except UnicodeDecodeError:
                        pass

                    # Если UTF-16 не сработал, пробуем другие кодировки
                    for encoding in ["utf-8", "cp1251", "latin1"]:
                        try:
                            content = blob_value.decode(encoding)
                            if content and len(content.strip()) > 0:
                                result["content"] = content
                                result["content_type"] = f"text_{encoding}"
                                result["content_length"] = len(content)
                                result["quality_score"] = 0.8
                                result["extraction_methods"].append(
                                    f"onec_dtools_{encoding}"
                                )
                                self.stats["successful_extractions"] += 1
                                self.stats["method_usage"][
                                    f"onec_dtools_{encoding}"
                                ] = (
                                    self.stats["method_usage"].get(
                                        f"onec_dtools_{encoding}", 0
                                    )
                                    + 1
                                )
                                self.stats["encoding_stats"][encoding] = (
                                    self.stats["encoding_stats"].get(encoding, 0) + 1
                                )
                                return BlobExtractionResult(result)
                        except UnicodeDecodeError:
                            continue

                    # Если все кодировки не сработали, используем hex
                    result["content"] = blob_value.hex()
                    result["content_type"] = "binary_hex"
                    result["content_length"] = len(blob_value)
                    result["quality_score"] = 0.3
                    result["extraction_methods"].append("fallback_hex")
                    self.stats["successful_extractions"] += 1
                    self.stats["method_usage"]["fallback_hex"] = (
                        self.stats["method_usage"].get("fallback_hex", 0) + 1
                    )
                    return BlobExtractionResult(result)

                elif isinstance(blob_value, str):
                    # Для строковых данных
                    if blob_value and len(blob_value.strip()) > 0:
                        result["content"] = blob_value
                        result["content_type"] = "text_string"
                        result["content_length"] = len(blob_value)
                        result["quality_score"] = 0.95
                        result["extraction_methods"].append("string_direct")
                        self.stats["successful_extractions"] += 1
                        self.stats["method_usage"]["string_direct"] = (
                            self.stats["method_usage"].get("string_direct", 0) + 1
                        )
                        return BlobExtractionResult(result)

                else:
                    # Для других типов конвертируем в строку
                    content = str(blob_value)
                    if content and len(content.strip()) > 0:
                        result["content"] = content
                        result["content_type"] = "text_converted"
                        result["content_length"] = len(content)
                        result["quality_score"] = 0.6
                        result["extraction_methods"].append("str_conversion")
                        self.stats["successful_extractions"] += 1
                        self.stats["method_usage"]["str_conversion"] = (
                            self.stats["method_usage"].get("str_conversion", 0) + 1
                        )
                        return BlobExtractionResult(result)

            # Если ни один метод не сработал
            result["errors"].append("No extraction method worked")
            result["content"] = "Не удалось извлечь содержимое"
            result["content_type"] = "failed"
            result["quality_score"] = 0.0
            self.stats["failed_extractions"] += 1

        except Exception as e:
            error_msg = f"Ошибка чтения BLOB: {e}"
            result["errors"].append(error_msg)
            result["content"] = error_msg
            result["content_type"] = "error"
            result["quality_score"] = 0.0
            self.stats["failed_extractions"] += 1
            logger.error(f"BlobProcessor error for {field_name}: {e}")

        return BlobExtractionResult(result)

    def is_blob_field(self, field_value: Any) -> bool:
        """
        Проверяет, является ли поле BLOB полем

        Args:
            field_value: Значение поля для проверки

        Returns:
            True если поле является BLOB полем
        """
        try:
            # Проверяем типы, которые могут быть BLOB
            if isinstance(field_value, bytes):
                return True
            elif hasattr(field_value, "value") and isinstance(field_value.value, bytes):
                return True
            elif hasattr(field_value, "__iter__") and not isinstance(
                field_value, (str, int, float, bool)
            ):
                return True
            else:
                return False
        except Exception:
            return False

    def safe_get_blob_content(
        self, blob_obj: Any, context: str = "", field_name: str = ""
    ) -> BlobExtractionResult:
        """
        Безопасное извлечение BLOB содержимого с обработкой ошибок

        Args:
            blob_obj: BLOB объект
            context: Контекст извлечения
            field_name: Имя поля

        Returns:
            Результат извлечения BLOB
        """
        try:
            return self.extract_blob_content(blob_obj, context, field_name)
        except Exception as e:
            logger.error(f"Ошибка извлечения BLOB {field_name}: {e}")
            error_data = {
                "field_name": field_name,
                "context": context,
                "content": None,
                "content_type": "error",
                "quality_score": 0.0,
                "errors": [str(e)],
                "metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "blob_type": type(blob_obj).__name__,
                    "blob_size": 0,
                },
            }
            return BlobExtractionResult(error_data)

    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики обработки

        Returns:
            Словарь со статистикой
        """
        if self.stats["total_processed"] > 0:
            success_rate = (
                self.stats["successful_extractions"] / self.stats["total_processed"]
            ) * 100
        else:
            success_rate = 0.0

        return {
            **self.stats,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
        }

    def reset_stats(self) -> None:
        """
        Сброс статистики
        """
        self.stats = {
            "total_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "method_usage": {},
            "encoding_stats": {},
        }

    def process_multiple_blobs(
        self, blob_objects: List[Any], context: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Обработка множественных BLOB объектов

        Args:
            blob_objects: Список BLOB объектов
            context: Контекст обработки

        Returns:
            Список результатов обработки
        """
        results = []

        for i, blob_obj in enumerate(blob_objects):
            field_name = f"blob_{i}"
            result = self.extract_blob_content(blob_obj, context, field_name)
            results.append(result)

        return results

    def analyze_blob_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализ качества извлечения BLOB данных

        Args:
            results: Список результатов обработки

        Returns:
            Анализ качества
        """
        total_results = len(results)
        successful_results = sum(1 for r in results if r["quality_score"] > 0)

        quality_analysis: Dict[str, Any] = {
            "total_blobs": total_results,
            "successful_blobs": successful_results,
            "success_rate": (
                (successful_results / total_results * 100) if total_results > 0 else 0
            ),
            "average_quality_score": (
                sum(r["quality_score"] for r in results) / total_results
                if total_results > 0
                else 0
            ),
            "content_types": {},
            "extraction_methods": {},
            "errors": [],
        }

        # Анализ типов содержимого
        for result in results:
            content_type = result["content_type"]
            quality_analysis["content_types"][content_type] = (
                quality_analysis["content_types"].get(content_type, 0) + 1
            )

            for method in result["extraction_methods"]:
                quality_analysis["extraction_methods"][method] = (
                    quality_analysis["extraction_methods"].get(method, 0) + 1
                )

            if result["errors"]:
                quality_analysis["errors"].extend(result["errors"])

        return quality_analysis


# Глобальный экземпляр для использования в других модулях
blob_processor = BlobProcessor()
