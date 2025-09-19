import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_utils import is_blob_field, safe_get_blob_content


def search_documents_by_criteria() -> dict[str, Any] | None:
    """
    Поиск документов по критериям из [todo · incidents]/todo.md
    Особое внимание на документы "корректировка качества товара"
    """
    logger.info("🔍 Поиск документов по критериям из [todo · incidents]/todo.md")
    logger.info("🎯 ЦЕЛЬ: Найти документы 'корректировка качества товара'")
    logger.info("=" * 60)

    try:
        with Path("raw/1Cv8.1CD").open("rb") as f:
            db = DatabaseReader(f)

            logger.info("✅ База данных открыта успешно!")

            results: dict[str, Any] = {
                "quality_documents": [],
                "found_keywords": [],
                "metadata": {
                    "extraction_date": datetime.now(UTC).isoformat(),
                    "total_quality_documents": 0,
                    "source_file": "raw/1Cv8.1CD",
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
                "цветочный",
                "рай",
            ]

            logger.info("\n🔍 Этап 1: Поиск в таблицах документов")
            logger.info("-" * 60)

            # Ищем таблицы документов
            document_tables = {}
            for table_name in db.tables:
                if table_name.startswith("_DOCUMENT"):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables[table_name] = len(table)

            logger.info("📊 Найдено таблиц документов: %s", len(document_tables))

            # Анализируем топ-20 таблиц документов
            sorted_documents = sorted(
                document_tables.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for i, (table_name, record_count) in enumerate(sorted_documents[:20]):
                logger.info(
                    "\n📋 %2d. %s (%s записей)",
                    i + 1,
                    table_name,
                    f"{record_count:,}",
                )

                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 3 записи
                        found_keywords = set()

                        for j in range(min(3, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()

                                    # Ищем ключевые слова в BLOB полях
                                    for field_name, field_value in record_data.items():
                                        if is_blob_field(field_value):
                                            content = safe_get_blob_content(field_value)
                                            if content and len(content) > 10:
                                                # Ищем ключевые слова
                                                for keyword in quality_keywords:
                                                    if (
                                                        keyword.lower()
                                                        in content.lower()
                                                    ):
                                                        found_keywords.add(keyword)
                                                        results[
                                                            "quality_documents"
                                                        ].append(
                                                            {
                                                                "table_name": table_name,
                                                                "record_count": record_count,
                                                                "field_name": field_name,
                                                                "keyword": keyword,
                                                                "content_sample": content[
                                                                    :200
                                                                ],
                                                            },
                                                        )

                                    # Ищем в обычных полях
                                    for field_name, field_value in record_data.items():
                                        if not is_blob_field(field_value):
                                            field_str = str(field_value).lower()
                                            for keyword in quality_keywords:
                                                if keyword.lower() in field_str:
                                                    found_keywords.add(keyword)
                                                    results["quality_documents"].append(
                                                        {
                                                            "table_name": table_name,
                                                            "record_count": record_count,
                                                            "field_name": field_name,
                                                            "keyword": keyword,
                                                            "content_sample": str(
                                                                field_value,
                                                            ),
                                                        },
                                                    )

                            except Exception as e:
                                logger.warning(f"Ошибка при обработке BLOB: {e}")
                                continue

                        # Показываем найденные ключевые слова
                        if found_keywords:
                            logger.info(
                                "    🎯 Найдено ключевых слов: %s",
                                ", ".join(found_keywords),
                            )
                            results["found_keywords"].extend(list(found_keywords))

                except Exception as e:
                    logger.warning("    ⚠️ Ошибка анализа таблицы: %s", e)
                    continue

            # Обновляем метаданные
            results["metadata"]["total_quality_documents"] = len(
                results["quality_documents"],
            )

            # Сохраняем результаты
            with Path("quality_documents_search.json").open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(results, file, ensure_ascii=False, indent=2, default=str)

            logger.info("\n✅ Результаты сохранены в quality_documents_search.json")
            logger.info(
                "📊 Найдено документов с качеством: %s",
                results["metadata"]["total_quality_documents"],
            )

            return results

    except Exception as e:
        logger.exception("❌ Ошибка: %s", e)
        return None


if __name__ == "__main__":
    search_documents_by_criteria()
