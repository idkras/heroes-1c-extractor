#!/usr/bin/env python3
"""
SimpleDocumentExtractor - простой извлекатель документов из 1С.

JTBD:
Как простой извлекатель документов, я хочу извлекать реальные документы из 1С базы,
чтобы подтвердить возможность извлечения данных и проанализировать их структуру.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Добавляем путь к процессорам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "processors"))

from database_connector import DatabaseConnector
from table_analyzer import TableAnalyzer
from blob_processor import BlobProcessor


class SimpleDocumentExtractor:
    """
    JTBD:
    Как SimpleDocumentExtractor, я хочу извлекать реальные документы из 1С,
    чтобы подтвердить возможность извлечения данных и проанализировать их структуру.
    """

    def __init__(self, db_connector: DatabaseConnector):
        """
        JTBD:
        Как конструктор SimpleDocumentExtractor, я хочу инициализировать извлекатель,
        чтобы подготовить все необходимые компоненты для извлечения документов.
        """
        self.db_connector = db_connector
        self.table_analyzer = TableAnalyzer()
        self.blob_processor = BlobProcessor()
        self.extracted_documents = []
        self.extraction_stats = {
            "total_documents": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "blob_fields_found": 0,
            "blob_fields_processed": 0,
            "extraction_errors": [],
        }

    def extract_documents(self, table_name: str, limit: int = 100) -> List[Dict]:
        """
        JTBD:
        Как метод извлечения документов, я хочу извлечь реальные документы из таблицы,
        чтобы проанализировать их структуру и содержимое.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество документов для извлечения

        Returns:
            Список извлеченных документов
        """
        print(f"🔍 Извлечение документов из таблицы: {table_name}")
        print(f"📊 Лимит: {limit} документов")

        try:
            # Получаем таблицу
            table = self.db_connector.get_table(table_name)
            table_info = self.db_connector.get_table_info(table_name)

            print(f"📋 Информация о таблице:")
            print(f"   Размер: {table_info['size']} записей")
            print(f"   Есть данные: {table_info['has_data']}")
            print(f"   Пустая: {table_info['is_empty']}")

            if table_info["is_empty"]:
                print("⚠️ Таблица пуста, нет данных для извлечения")
                return []

            # Анализируем структуру таблицы
            structure_analysis = self.table_analyzer.analyze_table_structure(table)
            print(f"📊 Анализ структуры:")
            print(
                f"   Всего полей: {structure_analysis['structure_summary']['total_fields']}"
            )
            print(
                f"   BLOB полей: {structure_analysis['structure_summary']['blob_fields']}"
            )
            print(
                f"   Числовых полей: {structure_analysis['structure_summary']['numeric_fields']}"
            )

            # Извлекаем документы
            documents = []
            actual_limit = min(limit, table_info["size"])

            # Используем итератор вместо индексации
            try:
                table_iterator = iter(table)
                for i in range(actual_limit):
                    try:
                        row = next(table_iterator)
                        if hasattr(row, "is_empty") and row.is_empty:
                            continue

                        document = self._extract_single_document(row, i, table_name)
                        if document:
                            documents.append(document)
                            self.extraction_stats["successful_extractions"] += 1
                        else:
                            self.extraction_stats["failed_extractions"] += 1

                    except StopIteration:
                        # Нормальное завершение итератора
                        print(f"ℹ️ Итератор завершен на позиции {i}")
                        break
                    except Exception as e:
                        error_msg = f"Ошибка извлечения документа {i}: {e}"
                        print(f"❌ {error_msg}")
                        self.extraction_stats["extraction_errors"].append(error_msg)
                        self.extraction_stats["failed_extractions"] += 1
                        continue

            except Exception as e:
                error_msg = f"Ошибка создания итератора: {e}"
                print(f"❌ {error_msg}")
                self.extraction_stats["extraction_errors"].append(error_msg)

            self.extracted_documents = documents
            self.extraction_stats["total_documents"] = len(documents)

            print(f"✅ Извлечение завершено:")
            print(f"   Успешно: {self.extraction_stats['successful_extractions']}")
            print(f"   Ошибок: {self.extraction_stats['failed_extractions']}")
            print(
                f"   BLOB полей найдено: {self.extraction_stats['blob_fields_found']}"
            )
            print(
                f"   BLOB полей обработано: {self.extraction_stats['blob_fields_processed']}"
            )

            return documents

        except Exception as e:
            error_msg = f"Критическая ошибка извлечения из таблицы {table_name}: {e}"
            print(f"❌ {error_msg}")
            self.extraction_stats["extraction_errors"].append(error_msg)
            return []

    def _extract_single_document(
        self, row, row_index: int, table_name: str
    ) -> Optional[Dict]:
        """
        JTBD:
        Как метод извлечения одного документа, я хочу извлечь данные из строки,
        чтобы создать структурированный документ с метаданными.

        Args:
            row: Строка данных из таблицы
            row_index: Индекс строки
            table_name: Имя таблицы

        Returns:
            Словарь с данными документа или None при ошибке
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

            document = {
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
                    field_name, value
                )

                # Проверяем, является ли поле BLOB
                if field_metadata.get("is_blob", False):
                    self.extraction_stats["blob_fields_found"] += 1
                    document["metadata"]["has_blob_fields"] = True

                    # Обрабатываем BLOB поле
                    blob_data = self.blob_processor.process_blob_field(
                        field_name, value
                    )
                    if blob_data and not blob_data.get("error"):
                        document["blob_fields"][field_name] = blob_data
                        self.extraction_stats["blob_fields_processed"] += 1
                    else:
                        document["blob_fields"][field_name] = {
                            "error": blob_data.get("error", "Unknown error"),
                            "field_type": "blob",
                            "size": 0,
                        }
                else:
                    # Обычное поле
                    document["fields"][field_name] = {
                        "value": str(value) if value is not None else None,
                        "type": field_metadata.get("type", "unknown"),
                        "is_numeric": field_metadata.get("is_numeric", False),
                        "is_date": field_metadata.get("is_date", False),
                        "is_string": field_metadata.get("is_string", False),
                    }

            return document

        except Exception as e:
            print(f"❌ Ошибка извлечения документа {row_index}: {e}")
            return None

    def analyze_document_structure(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        JTBD:
        Как метод анализа структуры документов, я хочу проанализировать структуру извлеченных документов,
        чтобы понять их назначение и связи.

        Args:
            documents: Список извлеченных документов

        Returns:
            Словарь с анализом структуры документов
        """
        if not documents:
            return {"error": "Нет документов для анализа"}

        print(f"🔍 Анализ структуры {len(documents)} документов")

        # Анализируем поля
        field_analysis = {}
        blob_analysis = {}

        for doc in documents:
            # Анализируем обычные поля
            for field_name, field_data in doc.get("fields", {}).items():
                if field_name not in field_analysis:
                    field_analysis[field_name] = {
                        "count": 0,
                        "types": set(),
                        "has_values": 0,
                        "sample_values": [],
                    }

                field_analysis[field_name]["count"] += 1
                field_analysis[field_name]["types"].add(
                    field_data.get("type", "unknown")
                )

                if field_data.get("value") is not None:
                    field_analysis[field_name]["has_values"] += 1
                    if len(field_analysis[field_name]["sample_values"]) < 3:
                        field_analysis[field_name]["sample_values"].append(
                            field_data["value"]
                        )

            # Анализируем BLOB поля
            for field_name, blob_data in doc.get("blob_fields", {}).items():
                if field_name not in blob_analysis:
                    blob_analysis[field_name] = {
                        "count": 0,
                        "successful_extractions": 0,
                        "failed_extractions": 0,
                        "sample_contents": [],
                    }

                blob_analysis[field_name]["count"] += 1

                if blob_data.get("error"):
                    blob_analysis[field_name]["failed_extractions"] += 1
                else:
                    blob_analysis[field_name]["successful_extractions"] += 1
                    if len(blob_analysis[field_name]["sample_contents"]) < 3:
                        content = blob_data.get("value", {}).get("content", "")
                        if content:
                            blob_analysis[field_name]["sample_contents"].append(
                                content[:100]
                            )

        # Создаем сводку анализа
        structure_analysis = {
            "total_documents": len(documents),
            "field_analysis": {},
            "blob_analysis": {},
            "summary": {
                "total_fields": len(field_analysis),
                "total_blob_fields": len(blob_analysis),
                "documents_with_blobs": sum(
                    1
                    for doc in documents
                    if doc.get("metadata", {}).get("has_blob_fields", False)
                ),
            },
        }

        # Обрабатываем анализ полей
        for field_name, analysis in field_analysis.items():
            structure_analysis["field_analysis"][field_name] = {
                "count": analysis["count"],
                "types": list(analysis["types"]),
                "fill_rate": (analysis["has_values"] / analysis["count"]) * 100,
                "sample_values": analysis["sample_values"],
            }

        # Обрабатываем анализ BLOB полей
        for field_name, analysis in blob_analysis.items():
            success_rate = 0
            if analysis["count"] > 0:
                success_rate = (
                    analysis["successful_extractions"] / analysis["count"]
                ) * 100

            structure_analysis["blob_analysis"][field_name] = {
                "count": analysis["count"],
                "success_rate": success_rate,
                "successful_extractions": analysis["successful_extractions"],
                "failed_extractions": analysis["failed_extractions"],
                "sample_contents": analysis["sample_contents"],
            }

        print(f"📊 Результаты анализа структуры:")
        print(f"   Всего документов: {structure_analysis['total_documents']}")
        print(f"   Всего полей: {structure_analysis['summary']['total_fields']}")
        print(f"   BLOB полей: {structure_analysis['summary']['total_blob_fields']}")
        print(
            f"   Документов с BLOB: {structure_analysis['summary']['documents_with_blobs']}"
        )

        return structure_analysis

    def validate_extraction_quality(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        JTBD:
        Как метод валидации качества извлечения, я хочу проверить качество извлеченных документов,
        чтобы убедиться в корректности извлечения данных.

        Args:
            documents: Список извлеченных документов

        Returns:
            Словарь с результатами валидации качества
        """
        if not documents:
            return {"error": "Нет документов для валидации"}

        print(f"🔍 Валидация качества извлечения {len(documents)} документов")

        quality_metrics = {
            "total_documents": len(documents),
            "documents_with_data": 0,
            "documents_with_blobs": 0,
            "blob_success_rate": 0,
            "field_completeness": 0,
            "extraction_errors": len(self.extraction_stats["extraction_errors"]),
            "quality_score": 0,
        }

        total_blob_fields = 0
        successful_blob_fields = 0
        total_fields = 0
        filled_fields = 0

        for doc in documents:
            # Проверяем наличие данных
            if doc.get("fields") or doc.get("blob_fields"):
                quality_metrics["documents_with_data"] += 1

            # Проверяем BLOB поля
            if doc.get("blob_fields"):
                quality_metrics["documents_with_blobs"] += 1
                for field_name, blob_data in doc["blob_fields"].items():
                    total_blob_fields += 1
                    if not blob_data.get("error"):
                        successful_blob_fields += 1

            # Проверяем обычные поля
            for field_name, field_data in doc.get("fields", {}).items():
                total_fields += 1
                if field_data.get("value") is not None:
                    filled_fields += 1

        # Вычисляем метрики качества
        if total_blob_fields > 0:
            quality_metrics["blob_success_rate"] = (
                successful_blob_fields / total_blob_fields
            ) * 100

        if total_fields > 0:
            quality_metrics["field_completeness"] = (filled_fields / total_fields) * 100

        # Вычисляем общий балл качества
        quality_score = 0
        if quality_metrics["documents_with_data"] > 0:
            quality_score += 30  # За наличие данных
        if quality_metrics["blob_success_rate"] > 50:
            quality_score += 30  # За успешное извлечение BLOB
        if quality_metrics["field_completeness"] > 70:
            quality_score += 20  # За полноту полей
        if quality_metrics["extraction_errors"] == 0:
            quality_score += 20  # За отсутствие ошибок

        quality_metrics["quality_score"] = quality_score

        print(f"📊 Результаты валидации качества:")
        print(f"   Документов с данными: {quality_metrics['documents_with_data']}")
        print(f"   Документов с BLOB: {quality_metrics['documents_with_blobs']}")
        print(f"   Успешность BLOB: {quality_metrics['blob_success_rate']:.1f}%")
        print(f"   Полнота полей: {quality_metrics['field_completeness']:.1f}%")
        print(f"   Ошибок извлечения: {quality_metrics['extraction_errors']}")
        print(f"   Общий балл качества: {quality_score}/100")

        return quality_metrics

    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        JTBD:
        Как метод получения статистики извлечения, я хочу вернуть статистику извлечения,
        чтобы проанализировать результаты работы извлекателя.

        Returns:
            Словарь со статистикой извлечения
        """
        return self.extraction_stats.copy()

    def save_extraction_report(self, output_file: str) -> bool:
        """
        JTBD:
        Как метод сохранения отчета об извлечении, я хочу сохранить отчет об извлечении,
        чтобы документировать результаты работы извлекателя.

        Args:
            output_file: Путь к файлу для сохранения отчета

        Returns:
            True если отчет сохранен успешно, False иначе
        """
        try:
            report = {
                "extraction_stats": self.extraction_stats,
                "extracted_documents": self.extracted_documents,
                "timestamp": datetime.now().isoformat(),
                "total_documents": len(self.extracted_documents),
            }

            import json

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"✅ Отчет об извлечении сохранен: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")
            return False
