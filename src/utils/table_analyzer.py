#!/usr/bin/env python3

"""
TableAnalyzer - независимый компонент для анализа таблиц
Выделен из extract_all_available_data.py для упрощения основного кода
"""

from typing import Any


class TableAnalyzer:
    """
    JTBD:
    Как система анализа таблиц, я хочу предоставить независимую функциональность
    для анализа таблиц 1С, чтобы упростить extract_all_available_data.py и
    устранить дублирование кода.
    """

    def __init__(self) -> None:
        self.analysis_stats = {
            "tables_analyzed": 0,
            "records_processed": 0,
            "errors_count": 0,
        }

    def analyze_table_structure(self, table: Any) -> dict[str, Any]:
        """
        JTBD:
        Как система анализа структуры таблицы, я хочу проанализировать
        структуру таблицы и вернуть метаданные, чтобы понимать содержимое
        таблицы без дублирования кода.
        """
        if not table:
            return {}

        structure_info: dict[str, Any] = {
            "total_records": len(table),
            "has_empty_records": False,
            "field_types": {},
            "sample_records": [],
        }

        # Анализируем первые несколько записей для понимания структуры
        sample_size = min(5, len(table))
        for i in range(sample_size):
            try:
                row = table[i]
                if hasattr(row, "is_empty") and row.is_empty:
                    structure_info["has_empty_records"] = True
                # Анализируем поля записи
                elif hasattr(row, "as_dict"):
                    row_dict = row.as_dict()
                    for field_name, value in row_dict.items():
                        field_type = type(value).__name__
                        field_types: dict[str, str] = structure_info["field_types"]
                        if field_name not in field_types:
                            field_types[field_name] = field_type

                    # Сохраняем образец записи
                    sample_records: list[dict[str, Any]] = structure_info[
                        "sample_records"
                    ]
                    if len(sample_records) < 3:
                        sample_records.append(
                            {
                                "row_index": i,
                                "fields": row_dict,
                            },
                        )
            except Exception:
                self.analysis_stats["errors_count"] += 1
                continue

        return structure_info

    def get_table_priority(self, table_name: str, record_count: int) -> str:
        """
        JTBD:
        Как система определения приоритета таблицы, я хочу определить
        приоритет таблицы на основе её имени и размера, чтобы правильно
        планировать извлечение данных.
        """
        # Критические таблицы с большим количеством записей
        if record_count > 1000000:
            return "CRITICAL"
        if record_count > 100000:
            return "HIGH"
        if record_count > 10000:
            return "MEDIUM"
        return "LOW"

    def estimate_extraction_time(
        self,
        record_count: int,
        complexity: str = "MEDIUM",
    ) -> int:
        """
        JTBD:
        Как система оценки времени извлечения, я хочу оценить время
        извлечения данных из таблицы, чтобы планировать ресурсы
        и время выполнения.
        """
        # Базовое время на запись (в миллисекундах)
        base_time_per_record = {
            "LOW": 1,  # Простые поля
            "MEDIUM": 5,  # С BLOB полями
            "HIGH": 20,  # Сложная обработка
        }

        time_per_record = base_time_per_record.get(complexity, 5)
        estimated_time = record_count * time_per_record

        return estimated_time

    def get_analysis_stats(self) -> dict[str, Any]:
        """Получить статистику анализа"""
        return self.analysis_stats.copy()

    def reset_stats(self) -> None:
        """Сбросить статистику анализа"""
        self.analysis_stats = {
            "tables_analyzed": 0,
            "records_processed": 0,
            "errors_count": 0,
        }
