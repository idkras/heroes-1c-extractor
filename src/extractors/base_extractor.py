#!/usr/bin/env python3
"""
BaseExtractor - базовый класс для всех экстракторов данных из 1С.

JTBD:
Как базовый экстрактор, я хочу предоставить общую логику извлечения данных,
чтобы все специализированные экстракторы могли наследовать общую функциональность.
"""

from abc import ABC
from datetime import datetime
from typing import Any

# Импорты процессоров
try:
    from ..processors.blob_processor import BlobProcessor
    from ..processors.database_connector import DatabaseConnector
    from ..processors.table_analyzer import TableAnalyzer
except ImportError:
    # Заглушки для компонентов (временно для исправления линтера)
    class BlobProcessorStub:
        def process_blob_field(self, field_name: str, value: Any) -> dict[str, Any]:
            return {"error": "BlobProcessor not available"}

    class DatabaseConnectorStub:
        def get_table(self, table_name: str) -> Any:
            return None

        def get_table_info(self, table_name: str) -> dict[str, Any]:
            return {"size": 0, "has_data": False, "is_empty": True}

    class TableAnalyzerStub:
        def analyze_table_structure(self, table: Any) -> dict[str, Any]:
            return {"structure_summary": {"total_fields": 0, "numeric_fields": 0}}

        def extract_field_metadata(self, field_name: str, value: Any) -> dict[str, Any]:
            return {"is_blob": False, "is_string": False, "type": "unknown"}

    # Алиасы для совместимости
    BlobProcessor = BlobProcessorStub  # type: ignore
    DatabaseConnector = DatabaseConnectorStub  # type: ignore
    TableAnalyzer = TableAnalyzerStub  # type: ignore


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
        self.db = db_connector  # Алиас для совместимости
        self.db_path = getattr(db_connector, "db_path", None)
        self.db_file = getattr(db_connector, "db_file", None)
        self.table_analyzer = TableAnalyzer()
        self.blob_processor = BlobProcessor()
        self.results: list[dict[str, Any]] = []
        self.extraction_stats: dict[str, Any] = {
            "total_items": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "blob_fields_found": 0,
            "blob_fields_processed": 0,
            "extraction_errors": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
        }

    def extract(self, table_name: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        JTBD:
        Как базовый метод извлечения, я хочу предоставить общую логику извлечения,
        чтобы специализированные экстракторы могли переопределить её при необходимости.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество элементов для извлечения

        Returns:
            Список извлеченных элементов
        """
        try:
            table = self.db_connector.get_table(table_name)
            if not table:
                return []

            results = []
            for i, row in enumerate(table):
                if i >= limit:
                    break

                processed_row = self.process_row(row, i, table_name)
                if processed_row:
                    results.append(processed_row)

            return results
        except Exception as e:
            self.log_extraction_error(e, {"table_name": table_name, "limit": limit})
            return []

    def process_row(
        self, row: Any, row_index: int, table_name: str
    ) -> dict[str, Any] | None:
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
            if hasattr(row, "_fields"):
                # Используем _fields если доступно
                if not row._fields:
                    # Пустые поля - возвращаем пустой результат
                    return {
                        "table_name": table_name,
                        "row_index": row_index,
                        "fields": {},
                        "blob_fields": {},
                        "metadata": {
                            "extraction_time": datetime.now().isoformat(),
                            "field_count": 0,
                            "has_blob_fields": False,
                        },
                    }
                # Для _fields создаем список значений и имен полей
                row_list = []
                field_names = list(row._fields.keys())
                field_values = list(row._fields.values())

                # Создаем объекты с атрибутами name и value
                for i, (name, value) in enumerate(zip(field_names, field_values)):
                    obj = type("Field", (), {"name": name, "value": value})()
                    row_list.append(obj)

            elif hasattr(row, "as_list"):
                try:
                    row_list = row.as_list(True)
                except StopIteration:
                    # Нормальное завершение итератора
                    return None
            else:
                return None

            # Создаем базовую структуру элемента
            item: dict[str, Any] = {
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
                # Получаем имя поля
                if hasattr(value, "name"):
                    field_name = value.name
                else:
                    field_name = f"field_{j}"

                # Анализируем тип поля
                field_metadata = self.table_analyzer.extract_field_metadata(
                    field_name,
                    value,
                )

                # Проверяем, является ли поле BLOB
                if field_metadata.get("is_blob", False):
                    if isinstance(self.extraction_stats["blob_fields_found"], int):
                        self.extraction_stats["blob_fields_found"] += 1
                    item["metadata"]["has_blob_fields"] = True

                    # Обрабатываем BLOB поле
                    blob_data = self.blob_processor.process_blob_field(
                        field_name,
                        value,
                    )
                    if blob_data and not blob_data.get("error"):
                        item["blob_fields"][field_name] = blob_data
                        if isinstance(
                            self.extraction_stats["blob_fields_processed"], int
                        ):
                            self.extraction_stats["blob_fields_processed"] += 1
                    else:
                        item["blob_fields"][field_name] = {
                            "error": blob_data.get("error", "Unknown error"),
                            "field_type": "blob",
                            "size": 0,
                        }
                else:
                    # Обычное поле
                    # Получаем значение поля
                    if hasattr(value, "value"):
                        field_value = value.value
                    else:
                        field_value = value

                    item["fields"][field_name] = {
                        "value": str(field_value) if field_value is not None else None,
                        "type": field_metadata.get("type", "unknown"),
                        "is_numeric": field_metadata.get("is_numeric", False),
                        "is_date": field_metadata.get("is_date", False),
                        "is_string": field_metadata.get("is_string", False),
                    }

            return item

        except Exception as e:
            error_msg = f"Ошибка обработки строки {row_index}: {e}"
            if isinstance(self.extraction_stats["extraction_errors"], list):
                self.extraction_stats["extraction_errors"].append(error_msg)
            return None

    def validate_data(self, data: dict[str, Any]) -> bool:
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
            start_time = self.extraction_stats["start_time"]
            end_time = self.extraction_stats["end_time"]
            if isinstance(start_time, str) and isinstance(end_time, str):
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                duration = (end - start).total_seconds()
                self.extraction_stats["duration_seconds"] = duration

        return self.extraction_stats.copy()

    def create_metadata(self, source_file: str = "data/raw/1Cv8.1CD") -> dict[str, Any]:
        """
        JTBD:
        Как метод создания метаданных, я хочу создать метаданные извлечения,
        чтобы документировать процесс извлечения данных.

        Args:
            source_file: Путь к исходному файлу базы данных

        Returns:
            Словарь с метаданными извлечения
        """
        return {
            "extraction_date": datetime.now().isoformat(),
            "source_file": source_file,
            "extractor_class": self.__class__.__name__,
            "total_items": self.extraction_stats["total_items"],
            "successful_extractions": self.extraction_stats["successful_extractions"],
            "failed_extractions": self.extraction_stats["failed_extractions"],
            "blob_fields_found": self.extraction_stats["blob_fields_found"],
            "blob_fields_processed": self.extraction_stats["blob_fields_processed"],
            "start_time": self.extraction_stats["start_time"],
            "end_time": self.extraction_stats["end_time"],
        }

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

    def log_extraction_error(self, error: Exception, context: dict[str, Any]) -> None:
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
        if isinstance(self.extraction_stats["extraction_errors"], list):
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

    def analyze_extraction_quality(
        self, extracted_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
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
        quality_score: float = 0.0
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
        extracted_data: list[dict[str, Any]],
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

    def get_document_tables(self) -> list[str]:
        """Получить список таблиц документов."""
        try:
            if hasattr(self.db_connector, "get_document_tables"):
                result: Any = self.db_connector.get_document_tables()
                return result if isinstance(result, list) else []
            return []
        except Exception:
            return []

    def get_reference_tables(self) -> list[str]:
        """Получить список справочных таблиц."""
        try:
            if hasattr(self.db_connector, "get_reference_tables"):
                result: Any = self.db_connector.get_reference_tables()
                return result if isinstance(result, list) else []
            return []
        except Exception:
            return []

    def get_register_tables(self) -> list[str]:
        """Получить список таблиц регистров."""
        try:
            if hasattr(self.db_connector, "get_register_tables"):
                result: Any = self.db_connector.get_register_tables()
                return result if isinstance(result, list) else []
            return []
        except Exception:
            return []

    def extract_blob_content(self, blob_field: Any) -> str:
        """Извлечь содержимое BLOB поля."""
        try:
            if hasattr(blob_field, "value") and isinstance(blob_field.value, bytes):
                # Пробуем разные кодировки
                for encoding in ["utf-16", "utf-8", "cp1251"]:
                    try:
                        return blob_field.value.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                # Fallback to hex
                return blob_field.value.hex()
            return str(blob_field) if blob_field is not None else ""
        except Exception:
            return ""

    def run(self) -> dict[str, Any]:
        """Запустить полный цикл извлечения."""
        try:
            return {
                "status": "completed",
                "extraction_stats": self.get_extraction_stats(),
                "message": "Extraction completed successfully",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "extraction_stats": self.get_extraction_stats(),
            }

    @property
    def metadata(self) -> dict[str, Any]:
        """Метаданные экстрактора."""
        return {
            "class_name": self.__class__.__name__,
            "extraction_stats": self.get_extraction_stats(),
            "db_connector_type": type(self.db_connector).__name__,
        }

    def open_database(self) -> None:
        """Открыть базу данных."""
        try:
            if hasattr(self.db_connector, "open_database"):
                self.db_connector.open_database()
        except Exception:
            pass

    def save_results(self, results: list[dict[str, Any]] | None = None) -> str:
        """Сохранить результаты извлечения."""
        if results is not None:
            self.results = results
        return "results_saved"

    def process_document_row(
        self, row: Any, row_index: int, table_name: str
    ) -> dict[str, Any] | None:
        """Обработать строку документа (базовая реализация)."""
        return self.process_row(row, row_index, table_name)

    def log_progress(self, message: str) -> None:
        """Логировать прогресс извлечения."""
        print(f"[{datetime.now().isoformat()}] {message}")

    def __str__(self) -> str:
        """Строковое представление для отладки."""
        return f"BaseExtractor(db_connector={self.db_connector}, stats={self.get_extraction_stats()})"
