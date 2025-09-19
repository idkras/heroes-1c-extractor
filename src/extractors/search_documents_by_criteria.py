import logging
from datetime import UTC, datetime
from typing import Any

from src.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class DocumentsByCriteriaExtractor(BaseExtractor):
    """
    Поиск документов по критериям

    JTBD:
    Как система поиска документов, я хочу найти документы по заданным критериям,
    чтобы анализировать качество товаров и корректировки.
    """

    def extract(self) -> dict[str, Any]:
        """
        Поиск документов по критериям из [todo · incidents]/todo.md
        Особое внимание на документы "корректировка качества товара"
        """
        logger.info("🔍 Поиск документов по критериям из [todo · incidents]/todo.md")
        logger.info("🎯 ЦЕЛЬ: Найти документы 'корректировка качества товара'")
        logger.info("=" * 60)

        if self.db is None:
            print("❌ База данных не открыта")
            return {"error": "База данных не открыта"}

        results: dict[str, Any] = {
            "quality_documents": [],
            "found_keywords": [],
            "metadata": {
                "extraction_date": datetime.now(UTC).isoformat(),
                "total_quality_documents": 0,
                "source_file": self.metadata["source_file"],
            },
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
            "7цветов",
        ]

        # Получаем таблицы документов
        document_tables = self.get_document_tables()
        print(f"📄 Найдено таблиц документов: {len(document_tables)}")

        # Анализируем каждую таблицу документов
        for table_name in document_tables[:3]:  # Ограничиваем для тестирования
            print(f"\n🔍 Анализ таблицы: {table_name}")
            table = self.db.tables[table_name]
            print(f"   📈 Всего записей: {len(table):,}")

            # Анализируем первые 50 записей
            sample_size = min(50, len(table))
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
                    quality_docs[:10],
                )  # Первые 10 документов
                print(f"   ✅ Найдено {len(quality_docs)} документов качества")

        results["metadata"]["total_quality_documents"] = len(
            results["quality_documents"],
        )
        return results


def search_documents_by_criteria() -> dict[str, Any]:
    """
    Функция-обертка для обратной совместимости
    """
    extractor = DocumentsByCriteriaExtractor()
    return extractor.run()
