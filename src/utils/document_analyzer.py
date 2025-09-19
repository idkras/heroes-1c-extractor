#!/usr/bin/env python3

"""
DocumentAnalyzer - Единый интерфейс для анализа структуры документов
Централизует логику анализа и улучшает читаемость кода
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_processor import BlobProcessor
from src.utils.keyword_searcher import KeywordSearcher, KeywordSearchResult


@dataclass
class DocumentAnalysisResult:
    """Результат анализа документа"""

    table_name: str
    record_count: int
    fields: list[str]
    blob_fields: list[str]
    sample_data: dict[str, Any] = field(default_factory=dict)
    analysis_metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Инициализация после создания объекта"""
        if self.analysis_metadata is None:
            self.analysis_metadata = {}


@dataclass
class TableAnalysisResult:
    """Результат анализа таблицы"""

    table_name: str
    record_count: int
    document_analysis: list[DocumentAnalysisResult]
    keyword_search_results: list[KeywordSearchResult]
    analysis_metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Инициализация после создания объекта"""
        if self.analysis_metadata is None:
            self.analysis_metadata = {}


class DocumentAnalyzer:
    """
    JTBD:
    Как система анализа документов, я хочу предоставить единый интерфейс для анализа структуры документов,
    чтобы централизовать логику анализа и улучшить читаемость кода.
    """

    def __init__(self) -> None:
        """Инициализация анализатора документов"""
        self.blob_processor = BlobProcessor()
        self.keyword_searcher = KeywordSearcher()

    def analyze_document_structure(
        self,
        record_data: dict[str, Any],
        table_name: str,
        record_index: int,
    ) -> DocumentAnalysisResult:
        """
        JTBD:
        Как система анализа структуры, я хочу проанализировать структуру документа,
        чтобы понять его поля и содержимое.

        Args:
            record_data: Словарь с данными записи
            table_name: Имя таблицы
            record_index: Индекс записи

        Returns:
            DocumentAnalysisResult: Результат анализа
        """
        # Анализируем поля
        fields = list(record_data.keys())
        blob_fields = []
        sample_data: dict[str, Any] = {}

        for field_name, field_value in record_data.items():
            if self.blob_processor.is_blob_field(field_value):
                blob_fields.append(field_name)
            # Сохраняем образцы обычных полей
            elif len(sample_data) < 5:  # Ограничиваем количество образцов
                sample_data[field_name] = field_value

        # Создаем результат анализа
        result = DocumentAnalysisResult(
            table_name=table_name,
            record_count=(
                1 if record_data else 0
            ),  # Анализируем одну запись или 0 для пустых данных
            fields=fields,
            blob_fields=blob_fields,
            sample_data=sample_data,
        )

        result.analysis_metadata = {
            "analysis_timestamp": datetime.now().isoformat(),
            "record_index": record_index,
            "total_fields": len(fields),
            "blob_fields_count": len(blob_fields),
            "regular_fields_count": len(fields) - len(blob_fields),
        }

        return result

    def analyze_table_documents(
        self,
        db: DatabaseReader,
        table_name: str,
        max_records: int = 5,
    ) -> TableAnalysisResult:
        """
        JTBD:
        Как система анализа таблиц, я хочу проанализировать документы в таблице,
        чтобы понять структуру и содержимое данных.

        Args:
            db: Объект базы данных
            table_name: Имя таблицы
            max_records: Максимальное количество записей для анализа

        Returns:
            TableAnalysisResult: Результат анализа таблицы
        """
        table = db.tables[table_name]
        record_count = len(table)

        document_analysis = []
        keyword_search_results = []

        # Анализируем первые записи
        for i in range(min(max_records, record_count)):
            try:
                record = table[i]
                if not record.is_empty:
                    record_data = record.as_dict()

                    # Анализируем структуру документа
                    doc_analysis = self.analyze_document_structure(
                        record_data,
                        table_name,
                        i,
                    )
                    document_analysis.append(doc_analysis)

                    # Ищем ключевые слова
                    quality_search = self.keyword_searcher.search_quality_keywords(
                        record_data,
                    )
                    if quality_search.found_keywords:
                        keyword_search_results.append(quality_search)

            except Exception as e:
                # Логируем ошибку, но продолжаем анализ
                print(f"    ⚠️ Ошибка анализа записи {i} в таблице {table_name}: {e}")
                continue

        # Создаем результат анализа таблицы
        result = TableAnalysisResult(
            table_name=table_name,
            record_count=record_count,
            document_analysis=document_analysis,
            keyword_search_results=keyword_search_results,
        )

        result.analysis_metadata = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzed_records": len(document_analysis),
            "found_keywords_records": len(keyword_search_results),
            "max_records_analyzed": max_records,
        }

        return result

    def analyze_document_tables(
        self,
        db: DatabaseReader,
        max_tables: int = 20,
    ) -> list[TableAnalysisResult]:
        """
        JTBD:
        Как система анализа таблиц документов, я хочу проанализировать все таблицы документов,
        чтобы получить полную картину структуры данных.

        Args:
            db: Объект базы данных
            max_tables: Максимальное количество таблиц для анализа

        Returns:
            List[TableAnalysisResult]: Список результатов анализа таблиц
        """
        # Находим таблицы документов
        document_tables = {}
        for table_name in db.tables.keys():
            if table_name.startswith("_DOCUMENT") and "_VT" not in table_name:
                table = db.tables[table_name]
                if len(table) > 0:
                    document_tables[table_name] = len(table)

        # Сортируем по размеру
        sorted_tables = sorted(
            document_tables.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []
        for i, (table_name, record_count) in enumerate(sorted_tables[:max_tables]):
            print(f"\n📋 {i + 1:2d}. {table_name} ({record_count:,} записей)")

            try:
                table_analysis = self.analyze_table_documents(db, table_name)
                results.append(table_analysis)

                # Показываем результаты
                if table_analysis.keyword_search_results:
                    print(
                        f"    ✅ Найдено {len(table_analysis.keyword_search_results)} записей с ключевыми словами",
                    )
                else:
                    print("    ⚠️ Ключевые слова не найдены")

            except Exception as e:
                print(f"    ⚠️ Ошибка анализа таблицы {table_name}: {e}")
                continue

        return results

    def analyze_reference_tables(
        self,
        db: DatabaseReader,
        max_tables: int = 10,
    ) -> list[TableAnalysisResult]:
        """
        JTBD:
        Как система анализа справочников, я хочу проанализировать справочники,
        чтобы понять структуру справочных данных.

        Args:
            db: Объект базы данных
            max_tables: Максимальное количество таблиц для анализа

        Returns:
            List[TableAnalysisResult]: Список результатов анализа справочников
        """
        # Находим справочники
        reference_tables = {}
        for table_name in db.tables.keys():
            if table_name.startswith("_Reference"):
                table = db.tables[table_name]
                if len(table) > 0:
                    reference_tables[table_name] = len(table)

        # Сортируем по размеру
        sorted_tables = sorted(
            reference_tables.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []
        for i, (table_name, record_count) in enumerate(sorted_tables[:max_tables]):
            print(f"\n📋 {i + 1:2d}. {table_name} ({record_count:,} записей)")

            try:
                table_analysis = self.analyze_table_documents(
                    db,
                    table_name,
                    max_records=3,
                )
                results.append(table_analysis)

            except Exception as e:
                print(f"    ⚠️ Ошибка анализа справочника {table_name}: {e}")
                continue

        return results

    def analyze_accumulation_registers(
        self,
        db: DatabaseReader,
    ) -> list[TableAnalysisResult]:
        """
        JTBD:
        Как система анализа регистров накопления, я хочу проанализировать регистры накопления,
        чтобы понять структуру накопленных данных.

        Args:
            db: Объект базы данных

        Returns:
            List[TableAnalysisResult]: Список результатов анализа регистров
        """
        # Находим регистры накопления
        accumulation_tables = {}
        for table_name in db.tables.keys():
            if table_name.startswith("_AccumRGT"):
                table = db.tables[table_name]
                if len(table) > 0:
                    accumulation_tables[table_name] = len(table)

        # Сортируем по размеру
        sorted_tables = sorted(
            accumulation_tables.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []
        for i, (table_name, record_count) in enumerate(sorted_tables):
            print(f"\n📋 {i + 1:2d}. {table_name} ({record_count:,} записей)")

            try:
                table_analysis = self.analyze_table_documents(
                    db,
                    table_name,
                    max_records=2,
                )
                results.append(table_analysis)

            except Exception as e:
                print(f"    ⚠️ Ошибка анализа регистра {table_name}: {e}")
                continue

        return results

    def get_analysis_summary(
        self,
        results: list[TableAnalysisResult],
    ) -> dict[str, Any]:
        """
        JTBD:
        Как система создания сводки, я хочу создать сводку результатов анализа,
        чтобы предоставить общую картину структуры данных.

        Args:
            results: Список результатов анализа таблиц

        Returns:
            Dict[str, Any]: Сводка анализа
        """
        total_tables = len(results)
        total_records = sum(r.record_count for r in results)
        total_keywords_found = sum(len(r.keyword_search_results) for r in results)

        # Анализируем поля
        all_fields = set()
        all_blob_fields = set()
        for result in results:
            for doc_analysis in result.document_analysis:
                all_fields.update(doc_analysis.fields)
                all_blob_fields.update(doc_analysis.blob_fields)

        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_tables_analyzed": total_tables,
            "total_records": total_records,
            "total_keywords_found": total_keywords_found,
            "unique_fields": len(all_fields),
            "unique_blob_fields": len(all_blob_fields),
            "field_coverage": (
                len(all_blob_fields) / len(all_fields) if all_fields else 0
            ),
        }


# Глобальный экземпляр для обратной совместимости
document_analyzer = DocumentAnalyzer()


def analyze_document_structure(
    record_data: dict[str, Any],
    table_name: str,
    record_index: int,
) -> DocumentAnalysisResult:
    """
    JTBD:
    Как система обратной совместимости, я хочу предоставить старый интерфейс для анализа структуры,
    чтобы не сломать существующий код.

    Args:
        record_data: Словарь с данными записи
        table_name: Имя таблицы
        record_index: Индекс записи

    Returns:
        DocumentAnalysisResult: Результат анализа
    """
    return document_analyzer.analyze_document_structure(
        record_data,
        table_name,
        record_index,
    )
