#!/usr/bin/env python3
"""
BaseExtractor - базовый класс для всех экстракторов данных из 1С.

JTBD:
Как базовый экстрактор, я хочу предоставить общую логику извлечения данных,
чтобы все специализированные экстракторы могли наследовать общую функциональность.
"""

import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

# Добавляем путь к процессорам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "processors"))

from blob_processor import BlobProcessor
from database_connector import DatabaseConnector
from table_analyzer import TableAnalyzer


class BaseExtractor(ABC):
    """
    JTBD:
    Как BaseExtractor, я хочу предоставить базовую функциональность для всех экстракторов,
    чтобы специализированные экстракторы могли наследовать общую логику.
    """

    def __init__(self, db_connector: DatabaseConnector):
        """
        JTBD:
        Как конструктор BaseExtractor, я хочу инициализировать базовые компоненты,
        чтобы все экстракторы имели доступ к общей функциональности.

        Args:
            db_connector: Подключение к базе данных 1С
        """
        self.db_connector = db_connector
        self.table_analyzer = TableAnalyzer()
        self.blob_processor = BlobProcessor()
        self.extraction_stats = {
            "total_items": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "blob_fields_found": 0,
            "blob_fields_processed": 0,
            "extraction_errors": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
        }

    @abstractmethod
    def extract(self, table_name: str, limit: int = 100) -> list[dict]:
        """
        JTBD:
        Как абстрактный метод извлечения, я хочу определить интерфейс для всех экстракторов,
        чтобы каждый экстрактор реализовывал свою логику извлечения.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество элементов для извлечения

        Returns:
            Список извлеченных элементов
        """

    def process_row(self, row, row_index: int, table_name: str) -> dict | None:
        """
        JTBD:
        Как метод обработки строки, я хочу обработать одну строку данных,
        чтобы извлечь структурированную информацию из строки таблицы.

        Args:
            row: Строка данных из таблицы
            row_index: Индекс строки
            table_name: Имя таблицы

        Returns:
            Словарь с данными строки или None при ошибке
        """
        try:
            # Получаем список полей
            if hasattr(row, "as_list"):
                try:
                    row_list = row.as_list(True)
                except StopIteration:
                    # Нормальное завершение итератора
                    return None
            else:
                return None

            # Создаем базовую структуру элемента
            item = {
                "table_name": table_name,
                "row_index": row_index,
                "fields": {},
                "blob_fields": {},
                "metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "field_count": len(row_list),
                    "has_blob_fields": False,
                },
            }

            # Обрабатываем каждое поле
            for j, value in enumerate(row_list):
                field_name = getattr(value, "name", f"field_{j}")

                # Анализируем тип поля
                field_metadata = self.table_analyzer.extract_field_metadata(
                    field_name,
                    value,
                )

                # Проверяем, является ли поле BLOB
                if field_metadata.get("is_blob", False):
                    self.extraction_stats["blob_fields_found"] += 1
                    item["metadata"]["has_blob_fields"] = True

                    # Обрабатываем BLOB поле
                    blob_data = self.blob_processor.process_blob_field(
                        field_name,
                        value,
                    )
                    if blob_data and not blob_data.get("error"):
                        item["blob_fields"][field_name] = blob_data
                        self.extraction_stats["blob_fields_processed"] += 1
                    else:
                        item["blob_fields"][field_name] = {
                            "error": blob_data.get("error", "Unknown error"),
                            "field_type": "blob",
                            "size": 0,
                        }
                else:
                    # Обычное поле
                    item["fields"][field_name] = {
                        "value": str(value) if value is not None else None,
                        "type": field_metadata.get("type", "unknown"),
                        "is_numeric": field_metadata.get("is_numeric", False),
                        "is_date": field_metadata.get("is_date", False),
                        "is_string": field_metadata.get("is_string", False),
                    }

            return item

        except Exception as e:
            error_msg = f"Ошибка обработки строки {row_index}: {e}"
            self.extraction_stats["extraction_errors"].append(error_msg)
            return None

    def validate_data(self, data: dict) -> bool:
        """
        JTBD:
        Как метод валидации данных, я хочу проверить корректность извлеченных данных,
        чтобы убедиться в качестве извлечения.

        Args:
            data: Словарь с данными для валидации

        Returns:
            True если данные корректны, False иначе
        """
        try:
            # Проверяем обязательные поля
            required_fields = ["table_name", "row_index", "fields"]
            for field in required_fields:
                if field not in data:
                    return False

            # Проверяем типы данных
            if not isinstance(data["table_name"], str):
                return False
            if not isinstance(data["row_index"], int):
                return False
            if not isinstance(data["fields"], dict):
                return False

            # Проверяем наличие хотя бы одного поля
            if len(data["fields"]) == 0:
                return False

            return True

        except Exception:
            return False

    def get_extraction_stats(self) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения статистики, я хочу вернуть статистику извлечения,
        чтобы проанализировать результаты работы экстрактора.

        Returns:
            Словарь со статистикой извлечения
        """
        # Обновляем время завершения
        self.extraction_stats["end_time"] = datetime.now().isoformat()

        # Вычисляем продолжительность
        if self.extraction_stats["start_time"] and self.extraction_stats["end_time"]:
            start = datetime.fromisoformat(self.extraction_stats["start_time"])
            end = datetime.fromisoformat(self.extraction_stats["end_time"])
            duration = (end - start).total_seconds()
            self.extraction_stats["duration_seconds"] = duration

        return self.extraction_stats.copy()

    def reset_stats(self) -> None:
        """
        JTBD:
        Как метод сброса статистики, я хочу сбросить статистику извлечения,
        чтобы начать новое извлечение с чистого листа.
        """
        self.extraction_stats = {
            "total_items": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "blob_fields_found": 0,
            "blob_fields_processed": 0,
            "extraction_errors": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
        }

    def log_extraction_error(self, error: Exception, context: dict) -> None:
        """
        JTBD:
        Как метод логирования ошибок, я хочу записать ошибку извлечения,
        чтобы отслеживать проблемы в процессе извлечения.

        Args:
            error: Исключение, которое произошло
            context: Контекст ошибки (таблица, строка и т.д.)
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        self.extraction_stats["extraction_errors"].append(error_info)

    def should_continue_extraction(
        self,
        error_count: int,
        max_errors: int = 100,
    ) -> bool:
        """
        JTBD:
        Как метод проверки продолжения, я хочу определить следует ли продолжать извлечение,
        чтобы избежать бесконечных циклов при множественных ошибках.

        Args:
            error_count: Количество ошибок
            max_errors: Максимальное количество ошибок

        Returns:
            True если следует продолжать, False иначе
        """
        return error_count < max_errors

    def analyze_extraction_quality(self, extracted_data: list[dict]) -> dict[str, Any]:
        """
        JTBD:
        Как метод анализа качества, я хочу проанализировать качество извлеченных данных,
        чтобы оценить успешность извлечения.

        Args:
            extracted_data: Список извлеченных данных

        Returns:
            Словарь с метриками качества
        """
        if not extracted_data:
            return {
                "total_items": 0,
                "quality_score": 0,
                "success_rate": 0,
                "blob_success_rate": 0,
                "field_completeness": 0,
            }

        total_items = len(extracted_data)
        successful_items = sum(1 for item in extracted_data if self.validate_data(item))
        items_with_blobs = sum(
            1
            for item in extracted_data
            if item.get("metadata", {}).get("has_blob_fields", False)
        )

        # Вычисляем метрики качества
        success_rate = (successful_items / total_items) * 100 if total_items > 0 else 0
        blob_success_rate = (
            (
                self.extraction_stats["blob_fields_processed"]
                / self.extraction_stats["blob_fields_found"]
            )
            * 100
            if self.extraction_stats["blob_fields_found"] > 0
            else 0
        )

        # Вычисляем полноту полей
        total_fields = sum(len(item.get("fields", {})) for item in extracted_data)
        filled_fields = sum(
            sum(
                1
                for field in item.get("fields", {}).values()
                if field.get("value") is not None
            )
            for item in extracted_data
        )
        field_completeness = (
            (filled_fields / total_fields) * 100 if total_fields > 0 else 0
        )

        # Вычисляем общий балл качества
        quality_score = 0
        if success_rate > 80:
            quality_score += 40
        elif success_rate > 60:
            quality_score += 20
        if blob_success_rate > 80:
            quality_score += 30
        elif blob_success_rate > 60:
            quality_score += 15
        if field_completeness > 80:
            quality_score += 30
        elif field_completeness > 60:
            quality_score += 15

        return {
            "total_items": total_items,
            "successful_items": successful_items,
            "items_with_blobs": items_with_blobs,
            "quality_score": quality_score,
            "success_rate": success_rate,
            "blob_success_rate": blob_success_rate,
            "field_completeness": field_completeness,
            "error_count": len(self.extraction_stats["extraction_errors"]),
        }

    def save_extraction_report(
        self,
        output_file: str,
        extracted_data: list[dict],
    ) -> bool:
        """
        JTBD:
        Как метод сохранения отчета, я хочу сохранить отчет об извлечении,
        чтобы документировать результаты работы экстрактора.

        Args:
            output_file: Путь к файлу для сохранения отчета
            extracted_data: Список извлеченных данных

        Returns:
            True если отчет сохранен успешно, False иначе
        """
        try:
            # Анализируем качество извлечения
            quality_metrics = self.analyze_extraction_quality(extracted_data)

            # Создаем отчет
            report = {
                "extraction_stats": self.get_extraction_stats(),
                "quality_metrics": quality_metrics,
                "extracted_data": extracted_data,
                "timestamp": datetime.now().isoformat(),
                "total_items": len(extracted_data),
            }

            import json

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            self.log_extraction_error(
                e,
                {"method": "save_extraction_report", "output_file": output_file},
            )
            return False

    def __str__(self) -> str:
        """Строковое представление для отладки."""
        return f"BaseExtractor(db_connector={self.db_connector}, stats={self.get_extraction_stats()})"
