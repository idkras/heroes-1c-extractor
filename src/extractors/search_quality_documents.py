#!/usr/bin/env python3

import logging
from typing import Any

from src.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class QualityDocumentsExtractor(BaseExtractor):
    """
    Поиск документов качества

    JTBD:
    Как система поиска документов качества, я хочу найти документы о качестве товаров,
    чтобы получить данные для анализа качества цветов и флористики.
    """

    def extract(self, table_name: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Поиск документов качества
        """
        print("🔍 Поиск документов 'корректировка качества товара'")
        print("🎯 ЦЕЛЬ: Найти первичные данные по качеству товаров")
        print("=" * 60)

        if not hasattr(self, "db") or self.db is None:
            print("❌ База данных не открыта")
            return []

        results: dict[str, Any] = {
            "quality_documents": [],
            "found_keywords": [],
            "metadata": self.metadata,
        }

        # Ключевые слова для поиска документов качества
        quality_keywords = [
            "корректировка качества",
            "качество товара",
            "брак",
            "дефект",
            "некондиция",
            "стандарт",
            "премиум",
            "качество",
            "цвет",
            "букет",
            "флористический",
        ]

        # Получаем таблицы документов
        document_tables = self.get_document_tables()
        print(f"📄 Найдено таблиц документов: {len(document_tables)}")

        # Анализируем каждую таблицу документов
        for table_name in document_tables[:3]:  # Ограничиваем для тестирования
            print(f"\n🔍 Анализ таблицы: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 30 записей
            sample_size = min(30, len(table))
            quality_docs = []

            for i in range(sample_size):
                try:
                    row = table[i]
                    if not hasattr(row, "is_empty") or not row.is_empty:
                        row_dict = row.as_dict() if hasattr(row, "as_dict") else {}

                        # Ищем ключевые слова в полях
                        for field_name, value in row_dict.items():
                            if isinstance(value, str):
                                for keyword in quality_keywords:
                                    if keyword.lower() in value.lower():
                                        quality_docs.append(
                                            {
                                                "table_name": table_name,
                                                "field_name": field_name,
                                                "keyword": keyword,
                                                "content": (
                                                    value[:200] + "..."
                                                    if len(value) > 200
                                                    else value
                                                ),
                                                "row_index": i,
                                            },
                                        )
                                        results["found_keywords"].append(keyword)

                except Exception as e:
                    logger.warning(
                        f"Ошибка обработки записи {i} в таблице {table_name}: {e}",
                    )
                    continue

            if quality_docs:
                results["quality_documents"].extend(
                    quality_docs[:5],
                )  # Первые 5 документов
                print(f"   ✅ Найдено {len(quality_docs)} документов качества")

        results["metadata"]["total_quality_documents"] = len(
            results["quality_documents"],
        )
        return [results]  # Возвращаем список словарей


def search_quality_documents() -> dict[str, Any]:
    """
    Функция-обертка для обратной совместимости
    """
    from ..processors.database_connector import DatabaseConnector

    db_connector = DatabaseConnector("data/raw/1Cv8.1CD")
    extractor = QualityDocumentsExtractor(db_connector=db_connector)
    return extractor.run()
