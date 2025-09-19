#!/usr/bin/env python3

import logging
from typing import Any

from src.utils.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class QualityDocumentsExtractor(BaseExtractor):
    """
    JTBD:
    Как система поиска документов качества, я хочу найти документы о качестве товаров,
    чтобы получить данные для анализа качества цветов и флористики.
    """

    def extract(self) -> dict[str, Any] | None:
        """
        JTBD:
        Как система извлечения документов качества, я хочу найти все документы о качестве товаров,
        чтобы получить данные для анализа качества цветов и флористики.

        Returns:
            Optional[Dict[str, Any]]: Результаты поиска документов качества
        """
        print("🔍 Поиск документов 'корректировка качества товара'")
        print("🎯 ЦЕЛЬ: Найти первичные данные по качеству товаров")
        print("=" * 60)

        results: dict[str, Any] = {
            "quality_documents": [],
            "found_keywords": [],
            "metadata": self.create_metadata(),
        }

        print("\n🔍 Этап 1: Анализ таблиц документов")
        print("-" * 60)

        # Используем DocumentAnalyzer для анализа таблиц документов
        document_analysis_results = self.document_analyzer.analyze_document_tables(
            self.db,
            max_tables=15,
        )

        for table_analysis in document_analysis_results:
            table_name = table_analysis.table_name
            record_count = table_analysis.record_count

            print(f"\n📋 Анализ таблицы: {table_name}")
            print(f"📊 Записей: {record_count:,}")

            # Ищем ключевые слова качества в результатах анализа
            quality_records = []
            for doc_analysis in table_analysis.document_analysis:
                # Используем KeywordSearcher для поиска ключевых слов качества
                keyword_result = self.keyword_searcher.search_quality_keywords(
                    doc_analysis.sample_data,
                )

                if keyword_result.found_keywords:
                    print(
                        f"    🎯 Найдены ключевые слова: {keyword_result.found_keywords}",
                    )

                    # Сохраняем найденную запись
                    record_index = 0
                    if doc_analysis.analysis_metadata:
                        record_index = doc_analysis.analysis_metadata.get(
                            "record_index",
                            0,
                        )

                    quality_record = {
                        "record_index": record_index,
                        "found_keywords": keyword_result.found_keywords,
                        "fields": doc_analysis.fields,
                        "blob_fields": doc_analysis.blob_fields,
                        "sample_data": doc_analysis.sample_data,
                    }
                    quality_records.append(quality_record)

                    # Добавляем найденные ключевые слова в общий список
                    for keyword in keyword_result.found_keywords:
                        if keyword not in results["found_keywords"]:
                            results["found_keywords"].append(keyword)

            if quality_records:
                print(
                    f"    ✅ Найдено {len(quality_records)} записей с ключевыми словами",
                )

                # Сохраняем результаты анализа таблицы
                table_analysis_result = {
                    "table_name": table_name,
                    "record_count": record_count,
                    "quality_records": quality_records,
                }
                results["quality_documents"].append(table_analysis_result)

                # Останавливаемся после анализа 5 таблиц с результатами
                if len(results["quality_documents"]) >= 5:
                    break

        print("\n🔍 Этап 2: Анализ справочников")
        print("-" * 60)

        # Используем DocumentAnalyzer для анализа справочников
        reference_analysis_results = self.document_analyzer.analyze_reference_tables(
            self.db,
            max_tables=10,
        )

        for table_analysis in reference_analysis_results:
            table_name = table_analysis.table_name
            record_count = table_analysis.record_count

            print(f"📋 {table_name} ({record_count:,} записей)")

            # Ищем ключевые слова качества в результатах анализа
            for doc_analysis in table_analysis.document_analysis:
                # Используем KeywordSearcher для поиска ключевых слов качества
                keyword_result = self.keyword_searcher.search_quality_keywords(
                    doc_analysis.sample_data,
                )

                if keyword_result.found_keywords:
                    print(
                        f"    🎯 Найдены ключевые слова: {keyword_result.found_keywords}",
                    )

                    # Добавляем найденные ключевые слова в общий список
                    for keyword in keyword_result.found_keywords:
                        if keyword not in results["found_keywords"]:
                            results["found_keywords"].append(keyword)

        print("\n🔍 Этап 3: Анализ журналов документов")
        print("-" * 60)

        # Ищем журналы документов (табличные части)
        if self.db:
            # Проверяем что база данных доступна
            if self.db is None:
                logger.warning("База данных не инициализирована")
                return None

            for table_name in self.db.tables.keys():
                table = self.db.tables[table_name]
                # Анализируем первые 20 записей
                quality_records = []
                for i in range(min(20, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            row_data = row.as_dict()

                            # Используем KeywordSearcher для поиска ключевых слов качества
                            keyword_result = (
                                self.keyword_searcher.search_quality_keywords(row_data)
                            )

                            if keyword_result.found_keywords:
                                print(
                                    f"    🎯 Запись {i + 1}: найдены ключевые слова: {keyword_result.found_keywords}",
                                )

                                # Сохраняем найденную запись
                                quality_record = {
                                    "record_index": i,
                                    "found_keywords": keyword_result.found_keywords,
                                    "row_data": row_data,
                                }
                                quality_records.append(quality_record)

                                # Добавляем найденные ключевые слова в общий список
                                for keyword in keyword_result.found_keywords:
                                    if keyword not in results["found_keywords"]:
                                        results["found_keywords"].append(keyword)

                                # Останавливаемся после первых 5 найденных записей
                                if len(quality_records) >= 5:
                                    break

                    except Exception:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: ")
                        continue

                if quality_records:
                    print(
                        f"    ✅ Найдено {len(quality_records)} записей с ключевыми словами",
                    )

                    # Сохраняем результаты анализа журнала
                    journal_analysis = {
                        "table_name": table_name,
                        "record_count": record_count,
                        "quality_records": quality_records,
                    }
                    results["quality_documents"].append(journal_analysis)

                    # Останавливаемся после анализа 3 журналов с результатами
                    if len(results["quality_documents"]) >= 8:
                        break
                else:
                    print("    ⚠️ Ключевые слова не найдены")

        # Обновляем общую статистику
        results["metadata"]["total_quality_documents"] = len(
            results["quality_documents"],
        )

        # Сохраняем результаты
        self.save_results("quality_documents_search.json", results)

        print(
            f"📊 Найдено документов с качеством: {results['metadata']['total_quality_documents']}",
        )
        print(f"🎯 Найдено ключевых слов: {len(results['found_keywords'])}")

        if results["found_keywords"]:
            print(f"🔍 Ключевые слова: {', '.join(results['found_keywords'])}")

        return results


def search_quality_documents() -> dict[str, Any] | None:
    """
    JTBD:
    Returns:
        Optional[Dict[str, Any]]: Результаты поиска документов качества
    """
    extractor = QualityDocumentsExtractor()
    return extractor.run()


if __name__ == "__main__":
    search_quality_documents()
