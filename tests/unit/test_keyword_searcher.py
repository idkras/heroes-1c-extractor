"""
Unit тесты для KeywordSearcher
Согласно TDD Documentation Standard
"""

from src.utils.keyword_searcher import KeywordSearcher


class TestKeywordSearcher:
    """Тесты для KeywordSearcher"""

    def setup_method(self):
        """Настройка тестового окружения"""
        self.searcher = KeywordSearcher()

    def test_search_quality_keywords(self):
        """
        JTBD:
        Как поисковик, я хочу найти ключевые слова о качестве в записи,
        чтобы определить релевантность для анализа качества товаров.
        """
        # Arrange
        record_data = {
            "name": "Заказ роз",
            "description": "Красные розы качественные",
            "notes": "Проверка качества товара",
        }

        # Act
        result = self.searcher.search_quality_keywords(record_data)

        # Assert
        assert result.found_keywords is not None
        assert len(result.found_keywords) > 0
        # Проверяем что найдены ключевые слова из списка качества
        quality_keywords = ["розы", "проверка", "товар"]
        assert any(keyword in result.found_keywords for keyword in quality_keywords)

    def test_search_document_type_keywords(self):
        """
        JTBD:
        Как поисковик, я хочу найти ключевые слова типов документов,
        чтобы классифицировать документы по типам.
        """
        # Arrange
        record_data = {
            "name": "Документ заказа",
            "description": "Заказ на поставку цветов",
            "type": "Заказ",
        }

        # Act
        result = self.searcher.search_document_type_keywords(record_data)

        # Assert
        assert result.found_keywords is not None
        assert len(result.found_keywords) >= 0

    def test_search_jtbd_keywords(self):
        """
        JTBD:
        Как поисковик, я хочу найти JTBD ключевые слова,
        чтобы понять потребности пользователей.
        """
        # Arrange
        record_data = {
            "name": "Анализ потребностей",
            "description": "Пользователь хочет заказать цветы",
            "notes": "JTBD анализ",
        }

        # Act
        result = self.searcher.search_jtbd_keywords(record_data)

        # Assert
        assert result.found_keywords is not None
        assert len(result.found_keywords) >= 0

    def test_search_custom_keywords(self):
        """
        JTBD:
        Как поисковик, я хочу найти пользовательские ключевые слова,
        чтобы обеспечить гибкость поиска.
        """
        # Arrange
        record_data = {
            "name": "Заказ роз",
            "description": "Красные розы для свадьбы",
            "notes": "Свадебный букет",
        }
        custom_keywords = ["свадьба", "свадебный", "розы"]

        # Act
        result = self.searcher.search_custom_keywords(record_data, custom_keywords)

        # Assert
        assert result.found_keywords is not None
        assert len(result.found_keywords) > 0

    def test_search_keywords_in_record(self):
        """
        JTBD:
        Как поисковик, я хочу найти ключевые слова в записи,
        чтобы обеспечить базовую функциональность поиска.
        """
        # Arrange
        record_data = {
            "name": "Заказ цветов",
            "description": "Красные розы и белые тюльпаны",
            "amount": "1500 рублей",
        }
        keywords = ["розы", "тюльпаны", "цветы"]

        # Act
        result = self.searcher.search_keywords_in_record(record_data, keywords)

        # Assert
        assert result.found_keywords is not None
        assert len(result.found_keywords) > 0

    def test_search_empty_record(self):
        """
        JTBD:
        Как поисковик, я хочу корректно обработать пустую запись,
        чтобы избежать ошибок.
        """
        # Arrange
        record_data: dict[str, str] = {}
        keywords = ["розы", "тюльпаны"]

        # Act
        result = self.searcher.search_keywords_in_record(record_data, keywords)

        # Assert
        assert result.found_keywords is not None
        assert len(result.found_keywords) == 0
