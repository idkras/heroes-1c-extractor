#!/usr/bin/env python3
"""
Тесты для HeroesGPT Offers Extractor
HeroesGPT Landing Analysis Standard v1.8 Compliance Testing
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from heroes_gpt_offers_extractor import OffersExtractor


class TestOffersExtractor:
    """Тесты для OffersExtractor"""

    @pytest.fixture
    async def extractor(self):
        """Фикстура для создания экстрактора"""
        async with OffersExtractor() as extractor:
            yield extractor

    def test_validate_url(self, extractor):
        """Тест валидации URL"""
        # Валидные URL
        assert extractor._validate_url("https://example.com") == True
        assert extractor._validate_url("http://test.ru/page") == True

        # Невалидные URL
        assert extractor._validate_url("not-a-url") == False
        assert extractor._validate_url("") == False
        assert extractor._validate_url("ftp://example.com") == False

    def test_extract_text_elements(self, extractor):
        """Тест извлечения текстовых элементов"""
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <h1>Main Title</h1>
                <h2>Subtitle</h2>
                <p>This is a paragraph with some content.</p>
                <button>Click me</button>
                <a href="#">Link text</a>
            </body>
        </html>
        """

        elements = extractor._extract_text_elements(html_content)

        # Проверяем что элементы извлечены
        assert len(elements) > 0

        # Проверяем заголовки
        headers = [e for e in elements if e["type"] == "header"]
        assert len(headers) >= 2  # h1 и h2

        # Проверяем контент
        content = [e for e in elements if e["type"] == "content"]
        assert len(content) >= 1  # параграф

        # Проверяем CTAs
        ctas = [e for e in elements if e["type"] == "cta"]
        assert len(ctas) >= 2  # button и link

    def test_determine_offer_type(self, extractor):
        """Тест определения типа офера"""
        # Quantitative promises
        assert (
            extractor._determine_offer_type("Увеличим продажи на 50%")
            == "quantitative_promises"
        )
        assert (
            extractor._determine_offer_type("Экономия 30 часов в неделю")
            == "quantitative_promises"
        )

        # Social proof
        assert (
            extractor._determine_offer_type("Более 1000 довольных клиентов")
            == "social_proof"
        )
        assert (
            extractor._determine_offer_type("Отзывы наших пользователей")
            == "social_proof"
        )

        # Risk reducers
        assert (
            extractor._determine_offer_type("100% гарантия возврата") == "risk_reducers"
        )
        assert (
            extractor._determine_offer_type("Круглосуточная поддержка")
            == "risk_reducers"
        )

        # Urgency/scarcity
        assert (
            extractor._determine_offer_type("Ограниченное предложение")
            == "urgency_scarcity"
        )
        assert extractor._determine_offer_type("Только сегодня") == "urgency_scarcity"

        # Process clarity
        assert extractor._determine_offer_type("Как это работает") == "process_clarity"
        assert extractor._determine_offer_type("Пошаговый процесс") == "process_clarity"

        # Authority signals
        assert (
            extractor._determine_offer_type("Эксперты с 10-летним опытом")
            == "authority_signals"
        )
        assert (
            extractor._determine_offer_type("Сертифицированные специалисты")
            == "authority_signals"
        )

        # Qualitative benefits (по умолчанию)
        assert (
            extractor._determine_offer_type("Улучшите свои навыки")
            == "qualitative_benefits"
        )

    def test_extract_quantitative_data(self, extractor):
        """Тест извлечения количественных данных"""
        # Проценты
        data = extractor._extract_quantitative_data("Увеличим продажи на 50%")
        assert "percentages" in data
        assert 50 in data["percentages"]

        # Числа
        data = extractor._extract_quantitative_data("Более 1000 клиентов")
        assert "numbers" in data
        assert 1000 in data["numbers"]

        # Время
        data = extractor._extract_quantitative_data("Экономия 30 часов в неделю")
        assert "time_periods" in data
        assert ("30", "часов") in data["time_periods"]

    def test_identify_emotional_trigger(self, extractor):
        """Тест идентификации эмоционального триггера"""
        assert (
            extractor._identify_emotional_trigger("Страх потерять клиентов") == "fear"
        )
        assert (
            extractor._identify_emotional_trigger("Достигните успеха") == "achievement"
        )
        assert extractor._identify_emotional_trigger("Сэкономьте деньги") == "savings"
        assert extractor._identify_emotional_trigger("Быстрое решение") == "speed"
        assert extractor._identify_emotional_trigger("Простое использование") == "ease"
        assert extractor._identify_emotional_trigger("Обычный текст") == "neutral"

    def test_identify_segment_appeal(self, extractor):
        """Тест идентификации привлекательности для сегментов"""
        # Business owners
        segments = extractor._identify_segment_appeal("Для бизнеса и предпринимателей")
        assert "business_owners" in segments

        # Beginners
        segments = extractor._identify_segment_appeal("Для начинающих")
        assert "beginners" in segments

        # Professionals
        segments = extractor._identify_segment_appeal("Для опытных профессионалов")
        assert "professionals" in segments

        # Budget conscious
        segments = extractor._identify_segment_appeal("Экономичное решение")
        assert "budget_conscious" in segments

        # Quality focused
        segments = extractor._identify_segment_appeal("Премиум качество")
        assert "quality_focused" in segments

    def test_validate_offers_compliance(self, extractor):
        """Тест валидации соответствия стандарту"""
        # Создаем тестовые оферы
        offers = []
        for i in range(70):  # Больше минимума в 60
            offers.append(
                {
                    "text": f"Test offer {i}",
                    "type": "qualitative_benefits",
                    "quantitative_data": {"numbers": [i]} if i % 10 == 0 else {},
                    "emotional_trigger": "achievement" if i % 5 == 0 else "neutral",
                }
            )

        validation = extractor._validate_offers_compliance(offers)

        # Проверяем требования
        assert validation["total_offers"] >= 60
        assert validation["meets_minimum"] == True
        assert validation["quantitative_data_present"] == True
        assert validation["emotional_triggers_present"] == True
        assert validation["compliance_score"] >= 0.8

    @pytest.mark.asyncio
    async def test_extract_offers_from_url_success(self, extractor):
        """Тест успешного извлечения оферов"""
        # Мокаем HTTP запрос
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Увеличим продажи на 50%</h1>
                <p>Более 1000 довольных клиентов</p>
                <button>Получить консультацию</button>
            </body>
        </html>
        """
        )

        with patch.object(extractor.session, "get", return_value=mock_response):
            result = await extractor.extract_offers_from_url("https://example.com")

            assert result["status"] == "success"
            assert result["offers_count"] > 0
            assert result["standard_version"] == "v1.8"
            assert "analysis_id" in result

    @pytest.mark.asyncio
    async def test_extract_offers_from_url_invalid_url(self, extractor):
        """Тест обработки невалидного URL"""
        result = await extractor.extract_offers_from_url("not-a-url")

        assert result["status"] == "error"
        assert "Invalid URL format" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_offers_from_url_fetch_error(self, extractor):
        """Тест обработки ошибки загрузки"""
        mock_response = Mock()
        mock_response.status = 404

        with patch.object(extractor.session, "get", return_value=mock_response):
            result = await extractor.extract_offers_from_url("https://example.com")

            assert result["status"] == "error"
            assert "Failed to fetch content" in result["error"]


class TestHeroesGPTStandardCompliance:
    """Тесты соответствия HeroesGPT Standard v1.8"""

    def test_minimum_offers_requirement(self):
        """Тест требования минимум 60+ оферов"""
        extractor = OffersExtractor()

        # Создаем 70 оферов (больше минимума)
        offers = [
            {"text": f"Offer {i}", "type": "qualitative_benefits"} for i in range(70)
        ]
        validation = extractor._validate_offers_compliance(offers)

        assert validation["total_offers"] >= 60
        assert validation["meets_minimum"] == True

    def test_offer_types_coverage(self):
        """Тест покрытия всех 7 типов оферов"""
        extractor = OffersExtractor()

        # Создаем оферы всех типов
        offer_types = [
            "quantitative_promises",
            "qualitative_benefits",
            "social_proof",
            "risk_reducers",
            "urgency_scarcity",
            "process_clarity",
            "authority_signals",
        ]

        offers = []
        for offer_type in offer_types:
            offers.append({"text": f"Test {offer_type}", "type": offer_type})

        validation = extractor._validate_offers_compliance(offers)

        assert len(validation["offer_types"]) >= 5  # Минимум 5 типов
        assert validation["compliance_score"] >= 0.7

    def test_quantitative_data_extraction(self):
        """Тест извлечения количественных данных"""
        extractor = OffersExtractor()

        text = "Увеличим продажи на 50% и сэкономим 30 часов в неделю"
        data = extractor._extract_quantitative_data(text)

        assert "percentages" in data
        assert 50 in data["percentages"]
        assert "numbers" in data
        assert 30 in data["numbers"]

    def test_emotional_triggers_identification(self):
        """Тест идентификации эмоциональных триггеров"""
        extractor = OffersExtractor()

        triggers = [
            ("Страх потерять клиентов", "fear"),
            ("Достигните успеха", "achievement"),
            ("Сэкономьте деньги", "savings"),
            ("Быстрое решение", "speed"),
            ("Простое использование", "ease"),
        ]

        for text, expected_trigger in triggers:
            trigger = extractor._identify_emotional_trigger(text)
            assert trigger == expected_trigger


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
