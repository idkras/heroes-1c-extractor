#!/usr/bin/env python3

"""
KeywordSearcher - Единый интерфейс для поиска ключевых слов
Устраняет дублирование логики поиска между extractors
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.utils.blob_processor import BlobProcessor


@dataclass
class KeywordSearchResult:
    """Результат поиска ключевых слов"""

    found_keywords: list[str] | None = None
    matches: list[dict[str, Any]] | None = None
    search_metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Инициализация после создания объекта"""
        if self.found_keywords is None:
            self.found_keywords = []
        if self.matches is None:
            self.matches = []
        if self.search_metadata is None:
            self.search_metadata = {}


class KeywordSearcher:
    """
    JTBD:
    Как система поиска ключевых слов, я хочу предоставить единый интерфейс для поиска в BLOB и обычных полях,
    чтобы устранить дублирование логики поиска и обеспечить консистентность результатов.
    """

    def __init__(self) -> None:
        """Инициализация поисковика ключевых слов"""
        self.blob_processor = BlobProcessor()

        # Предопределенные наборы ключевых слов
        self.quality_keywords = [
            "корректировка",
            "качество",
            "товар",
            "брак",
            "дефект",
            "проверка",
            "контроль",
            "отбраковка",
            "списание",
            "уценка",
            "некондиция",
            "реализация",
            "поступление",
            "склад",
            "цвет",
            "цветы",
            "розы",
            "тюльпаны",
            "флористика",
            "биржа",
            "7цветов",
            "цветочный",
            "рай",
        ]

        self.document_type_keywords = {
            "перемещение": [
                "перемещение",
                "перемещ",
                "склад отгрузки",
                "склад получатель",
            ],
            "реализация": ["реализация", "реализ", "продажа", "счет-фактура"],
            "перекомплектация": ["перекомплектация", "комплектация", "комплект"],
            "поступление": ["поступление", "поступл", "приход", "накладная"],
            "качество": ["качество", "брак", "дефект", "некондиция", "стандарт"],
            "поставка": ["поставка", "поставщ", "договор поставки"],
            "списание": ["списание", "списан", "расход", "брак"],
            "инвентаризация": ["инвентаризация", "пересчет", "остатки"],
            "возврат": ["возврат", "рекламация", "возвращ"],
            "корректировка": ["корректировка", "исправление", "коррект"],
        }

        self.jtbd_keywords = {
            "цвет": [
                "цвет",
                "розовый",
                "голубой",
                "красный",
                "белый",
                "желтый",
                "синий",
            ],
            "букет": ["букет", "флористический", "композиция", "моно", "яндекс букет"],
            "склад": ["склад", "братиславский", "045", "подразделение", "магазин"],
            "канал": [
                "яндекс маркет",
                "яндекс директ",
                "яндекс-еда",
                "интернет магазин",
            ],
            "качество": [
                "качество",
                "брак",
                "дефект",
                "некондиция",
                "стандарт",
                "премиум",
            ],
        }

    def search_keywords_in_record(
        self,
        record_data: dict[str, Any],
        keywords: list[str],
    ) -> KeywordSearchResult:
        """
        JTBD:
        Как система поиска в записи, я хочу найти ключевые слова в полях записи,
        чтобы определить релевантность данных для анализа.

        Args:
            record_data: Словарь с данными записи
            keywords: Список ключевых слов для поиска

        Returns:
            KeywordSearchResult: Результат поиска
        """
        result = KeywordSearchResult()
        result.search_metadata = {
            "search_timestamp": datetime.now().isoformat(),
            "total_fields": len(record_data),
            "keywords_searched": len(keywords),
        }

        found_keywords = set()
        matches: list[dict[str, Any]] = []

        for field_name, field_value in record_data.items():
            # Поиск в BLOB полях
            if self.blob_processor.is_blob_field(field_value):
                blob_result = self._search_in_blob_field(
                    field_name,
                    field_value,
                    keywords,
                )
                if blob_result.found_keywords:
                    found_keywords.update(blob_result.found_keywords)
                    if blob_result.matches is not None:
                        matches.extend(blob_result.matches)

            # Поиск в обычных полях
            else:
                field_result = self._search_in_regular_field(
                    field_name,
                    field_value,
                    keywords,
                )
                if field_result.found_keywords:
                    found_keywords.update(field_result.found_keywords)
                    if field_result.matches is not None:
                        matches.extend(field_result.matches)

        result.found_keywords = list(found_keywords)
        result.matches = matches
        result.search_metadata["found_keywords_count"] = len(found_keywords)
        result.search_metadata["matches_count"] = len(matches)

        return result

    def _search_in_blob_field(
        self,
        field_name: str,
        field_value: Any,
        keywords: list[str],
    ) -> KeywordSearchResult:
        """Поиск ключевых слов в BLOB поле"""
        result = KeywordSearchResult()

        try:
            # Извлекаем содержимое BLOB
            blob_content = self.blob_processor.safe_get_blob_content(field_value)
            if not blob_content or len(blob_content) < 10:
                return result

            # Ищем ключевые слова
            found_keywords = set()
            for keyword in keywords:
                if keyword.lower() in blob_content.lower():
                    found_keywords.add(keyword)
                    if result.matches is not None:
                        result.matches.append(
                            {
                                "field_name": field_name,
                                "keyword": keyword,
                                "content_sample": blob_content[:200],
                                "field_type": "blob",
                            },
                        )

            result.found_keywords = list(found_keywords)

        except Exception as e:
            if result.search_metadata is not None:
                result.search_metadata["blob_error"] = str(e)

        return result

    def _search_in_regular_field(
        self,
        field_name: str,
        field_value: Any,
        keywords: list[str],
    ) -> KeywordSearchResult:
        """Поиск ключевых слов в обычном поле"""
        result = KeywordSearchResult()

        try:
            field_str = str(field_value).lower()
            found_keywords = set()

            for keyword in keywords:
                if keyword.lower() in field_str:
                    found_keywords.add(keyword)
                    if result.matches is not None:
                        result.matches.append(
                            {
                                "field_name": field_name,
                                "keyword": keyword,
                                "content_sample": str(field_value),
                                "field_type": "regular",
                            },
                        )

            result.found_keywords = list(found_keywords)

        except Exception as e:
            if result.search_metadata is not None:
                result.search_metadata["regular_field_error"] = str(e)

        return result

    def search_quality_keywords(
        self,
        record_data: dict[str, Any],
    ) -> KeywordSearchResult:
        """
        JTBD:
        Как система поиска качества, я хочу найти ключевые слова связанные с качеством товаров,
        чтобы выявить документы о качестве и браке.

        Args:
            record_data: Словарь с данными записи

        Returns:
            KeywordSearchResult: Результат поиска
        """
        return self.search_keywords_in_record(record_data, self.quality_keywords)

    def search_document_type_keywords(
        self,
        record_data: dict[str, Any],
    ) -> KeywordSearchResult:
        """
        JTBD:
        Как система определения типов документов, я хочу найти ключевые слова типов документов,
        чтобы классифицировать документы по их назначению.

        Args:
            record_data: Словарь с данными записи

        Returns:
            KeywordSearchResult: Результат поиска
        """
        all_keywords = []
        for keyword_list in self.document_type_keywords.values():
            all_keywords.extend(keyword_list)

        return self.search_keywords_in_record(record_data, all_keywords)

    def search_jtbd_keywords(self, record_data: dict[str, Any]) -> KeywordSearchResult:
        """
        JTBD:
        Как система поиска JTBD данных, я хочу найти ключевые слова для JTBD сценариев,
        чтобы выявить данные о цветах, складах и каналах продаж.

        Args:
            record_data: Словарь с данными записи

        Returns:
            KeywordSearchResult: Результат поиска
        """
        all_keywords = []
        for keyword_list in self.jtbd_keywords.values():
            all_keywords.extend(keyword_list)

        return self.search_keywords_in_record(record_data, all_keywords)

    def search_custom_keywords(
        self,
        record_data: dict[str, Any],
        custom_keywords: list[str],
    ) -> KeywordSearchResult:
        """
        JTBD:
        Как система пользовательского поиска, я хочу найти пользовательские ключевые слова,
        чтобы обеспечить гибкость поиска для разных задач.

        Args:
            record_data: Словарь с данными записи
            custom_keywords: Пользовательские ключевые слова

        Returns:
            KeywordSearchResult: Результат поиска
        """
        return self.search_keywords_in_record(record_data, custom_keywords)

    def get_keyword_categories(self) -> dict[str, list[str]]:
        """
        JTBD:
        Как система категоризации, я хочу предоставить доступ к категориям ключевых слов,
        чтобы разработчики могли использовать предопределенные наборы.

        Returns:
            Dict[str, List[str]]: Словарь категорий ключевых слов
        """
        return {
            "quality": list(self.quality_keywords),
            "document_types": list(self.document_type_keywords),
            "jtbd": list(self.jtbd_keywords),
        }


# Глобальный экземпляр для обратной совместимости
keyword_searcher = KeywordSearcher()


def search_keywords_in_record(
    record_data: dict[str, Any],
    keywords: list[str],
) -> KeywordSearchResult:
    """
    JTBD:
    Как система обратной совместимости, я хочу предоставить старый интерфейс для поиска ключевых слов,
    чтобы не сломать существующий код.

    Args:
        record_data: Словарь с данными записи
        keywords: Список ключевых слов для поиска

    Returns:
        KeywordSearchResult: Результат поиска
    """
    return keyword_searcher.search_keywords_in_record(record_data, keywords)
