#!/usr/bin/env python3
"""
HeroesGPT Landing Analyzer - основной анализатор лендингов

Основано на: HeroesGPT Standard v1.8 + Legacy system analysis
Стандарт: TDD-doc v2.0 + From-The-End Standard v2.4
Автор: AI Assistant
Дата: 15 Aug 2025
"""

import logging
import time
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from .heroes_gpt_models import (
    HeroesGPTReport,
    JTBDScenario,
    LandingAnalysis,
    OfferAnalysis,
    create_heroes_gpt_report,
)


class HeroesGPTAnalyzer:
    """Основной анализатор лендингов HeroesGPT"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def analyze_landing_page(self, url: str) -> HeroesGPTReport:
        """Анализирует лендинг и возвращает полный отчет"""

        start_time = time.time()

        try:
            # Извлекаем контент
            content = self._extract_content(url)

            # Анализируем лендинг
            landing_analysis = self._analyze_landing_basic(url, content, start_time)

            # Анализируем офферы
            offers_table = self._analyze_offers(content)

            # Анализируем JTBD сценарии
            jtbd_scenarios = self._analyze_jtbd_scenarios(content)

            # Анализируем сегменты
            segments = self._analyze_segments(content, offers_table)

            # Рассчитываем рейтинг
            rating = self._calculate_rating(offers_table, segments)

            # Генерируем рекомендации
            recommendations = self._generate_recommendations(offers_table, segments)

            # Создаем reflection checkpoints
            reflections = self._create_reflections()

            # Рассчитываем narrative coherence
            narrative_coherence = self._calculate_narrative_coherence(
                offers_table, segments
            )

            # Проверяем self compliance
            self_compliance = self._check_self_compliance(offers_table, segments)

            # Создаем отчет
            report = create_heroes_gpt_report(
                url=url,
                landing_analysis=landing_analysis,
                offers_table=offers_table,
                jtbd_scenarios=jtbd_scenarios,
                segments=segments,
                rating=rating,
                recommendations=recommendations,
                reflections=reflections,
                narrative_coherence_score=narrative_coherence,
                self_compliance_passed=self_compliance,
            )

            return report

        except Exception as e:
            self.logger.error(f"Error analyzing landing page {url}: {e}")
            raise

    def _extract_content(self, url: str) -> str:
        """Извлекает контент с лендинга"""

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Удаляем скрипты и стили
            for script in soup(["script", "style"]):
                script.decompose()

            # Извлекаем текст
            text = soup.get_text()

            # Очищаем текст
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            raise

    def _analyze_landing_basic(
        self, url: str, content: str, start_time: float
    ) -> LandingAnalysis:
        """Базовый анализ лендинга"""

        analysis_time = time.time() - start_time
        content_length = len(content)

        # Определяем тип бизнеса
        business_type = self._determine_business_type(content)

        # Определяем основную ценность
        main_value_prop = self._extract_main_value_prop(content)

        # Определяем целевые сегменты
        target_segments = self._extract_target_segments(content)

        # Определяем ценовую категорию
        price_category = self._determine_price_category(content)

        # Определяем основную цель
        primary_goal = self._determine_primary_goal(content)

        return LandingAnalysis(
            url=url,
            business_type=business_type,
            main_value_prop=main_value_prop,
            target_segments=target_segments,
            analysis_time=analysis_time,
            content_length=content_length,
            price_category=price_category,
            primary_goal=primary_goal,
        )

    def _determine_business_type(self, content: str) -> str:
        """Определяет тип бизнеса"""

        content_lower = content.lower()

        # SaaS / Software
        if any(
            word in content_lower
            for word in ["software", "platform", "saas", "app", "tool"]
        ):
            return "B2B SaaS / Software Platform"

        # E-commerce
        if any(
            word in content_lower
            for word in ["shop", "store", "buy", "purchase", "cart"]
        ):
            return "E-commerce / Online Store"

        # Service
        if any(
            word in content_lower
            for word in ["service", "consulting", "agency", "help"]
        ):
            return "Service / Consulting"

        # Product
        if any(word in content_lower for word in ["product", "solution", "system"]):
            return "Product / Solution"

        return "General Business"

    def _extract_main_value_prop(self, content: str) -> str:
        """Извлекает основную ценность"""

        # Ищем заголовки и ключевые фразы
        lines = content.split("\n")

        for line in lines[:20]:  # Первые 20 строк
            line = line.strip()
            if len(line) > 20 and len(line) < 200:
                if any(
                    word in line.lower()
                    for word in ["help", "solve", "provide", "offer", "enable"]
                ):
                    return line

        # Fallback
        return "Основная ценность не определена"

    def _extract_target_segments(self, content: str) -> list[str]:
        """Извлекает целевые сегменты"""

        segments = []
        content_lower = content.lower()

        # Определяем сегменты по ключевым словам
        segment_keywords = {
            "business": ["business", "company", "enterprise", "corporate"],
            "individuals": ["individual", "person", "user", "customer"],
            "professionals": ["professional", "expert", "specialist"],
            "startups": ["startup", "small business", "entrepreneur"],
            "enterprises": ["enterprise", "large company", "corporation"],
        }

        for segment, keywords in segment_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                segments.append(segment.title())

        return segments if segments else ["General Audience"]

    def _determine_price_category(self, content: str) -> str:
        """Определяет ценовую категорию"""

        content_lower = content.lower()

        # Высокая цена
        if any(
            word in content_lower
            for word in ["premium", "enterprise", "professional", "advanced"]
        ):
            return "High-tier"

        # Средняя цена
        if any(word in content_lower for word in ["standard", "business", "pro"]):
            return "Mid-tier"

        # Низкая цена
        if any(word in content_lower for word in ["basic", "starter", "free", "cheap"]):
            return "Low-tier"

        return "Mid-tier"

    def _determine_primary_goal(self, content: str) -> str:
        """Определяет основную цель"""

        content_lower = content.lower()

        if any(
            word in content_lower
            for word in ["sign up", "register", "join", "subscribe"]
        ):
            return "Привлечение подписчиков"

        if any(word in content_lower for word in ["buy", "purchase", "order"]):
            return "Продажа продукта/услуги"

        if any(word in content_lower for word in ["contact", "call", "email"]):
            return "Привлечение лидов"

        if any(word in content_lower for word in ["learn", "read", "download"]):
            return "Образование и контент"

        return "Привлечение внимания"

    def _analyze_offers(self, content: str) -> list[OfferAnalysis]:
        """Анализирует офферы в контенте"""

        offers = []
        lines = content.split("\n")

        # Ищем потенциальные офферы
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 500:
                if self._is_potential_offer(line):
                    offer = self._create_offer_analysis(line)
                    if offer:
                        offers.append(offer)

        return offers[:20]  # Ограничиваем 20 офферами

    def _is_potential_offer(self, text: str) -> bool:
        """Проверяет, является ли текст потенциальным оффером"""

        text_lower = text.lower()

        # Ключевые слова офферов
        offer_keywords = [
            "help",
            "solve",
            "provide",
            "offer",
            "enable",
            "give",
            "make",
            "save",
            "increase",
            "improve",
            "reduce",
            "eliminate",
            "create",
            "build",
            "develop",
            "design",
            "manage",
            "organize",
            "automate",
        ]

        return any(keyword in text_lower for keyword in offer_keywords)

    def _create_offer_analysis(self, text: str) -> Optional[OfferAnalysis]:
        """Создает анализ оффера"""

        try:
            # Определяем тип оффера
            offer_type = self._determine_offer_type(text)

            # Извлекаем количественные данные
            quantitative_data = self._extract_quantitative_data(text)

            # Определяем целевой сегмент
            target_segment = self._determine_offer_target_segment(text)

            # Определяем эмоциональный триггер
            emotional_trigger = self._determine_emotional_trigger(text)

            # Определяем value/tax rating
            value_tax_rating = self._determine_value_tax_rating(text)

            # Определяем уровень доверия
            trust_level = self._determine_trust_level(text)

            # Определяем уровень срочности
            urgency_level = self._determine_urgency_level(text)

            return OfferAnalysis(
                offer_text=text[:100] + "..." if len(text) > 100 else text,
                offer_type=offer_type,
                quantitative_data=quantitative_data,
                target_segment=target_segment,
                emotional_trigger=emotional_trigger,
                value_tax_rating=value_tax_rating,
                trust_level=trust_level,
                urgency_level=urgency_level,
            )

        except Exception as e:
            self.logger.warning(f"Error creating offer analysis: {e}")
            return None

    def _determine_offer_type(self, text: str) -> str:
        """Определяет тип оффера"""

        text_lower = text.lower()

        if any(word in text_lower for word in ["promise", "guarantee", "assure"]):
            return "гарантия"

        if any(word in text_lower for word in ["benefit", "advantage", "profit"]):
            return "выгода"

        if any(word in text_lower for word in ["testimonial", "review", "customer"]):
            return "соц_доказательство"

        if any(word in text_lower for word in ["position", "brand", "identity"]):
            return "позиционирование"

        if any(word in text_lower for word in ["function", "feature", "capability"]):
            return "функция"

        return "обещание"

    def _extract_quantitative_data(self, text: str) -> str:
        """Извлекает количественные данные"""

        import re

        # Ищем числа
        numbers = re.findall(r"\d+", text)
        if numbers:
            return f"{numbers[0]} units"

        # Ищем проценты
        percentages = re.findall(r"\d+%", text)
        if percentages:
            return percentages[0]

        return "-"

    def _determine_offer_target_segment(self, text: str) -> str:
        """Определяет целевой сегмент оффера"""

        text_lower = text.lower()

        if any(word in text_lower for word in ["business", "company", "enterprise"]):
            return "Бизнес"

        if any(word in text_lower for word in ["individual", "person", "user"]):
            return "Индивидуальные пользователи"

        if any(word in text_lower for word in ["professional", "expert"]):
            return "Профессионалы"

        return "Общая аудитория"

    def _determine_emotional_trigger(self, text: str) -> str:
        """Определяет эмоциональный триггер"""

        text_lower = text.lower()

        if any(word in text_lower for word in ["fear", "worry", "problem", "issue"]):
            return "Страх/Беспокойство"

        if any(word in text_lower for word in ["desire", "want", "need", "wish"]):
            return "Желание/Потребность"

        if any(word in text_lower for word in ["success", "achieve", "win"]):
            return "Успех/Достижение"

        if any(word in text_lower for word in ["save", "money", "time", "effort"]):
            return "Экономия/Эффективность"

        return "Общий интерес"

    def _determine_value_tax_rating(self, text: str) -> str:
        """Определяет value/tax rating"""

        text_lower = text.lower()

        if any(word in text_lower for word in ["free", "save", "gain", "benefit"]):
            return "Выгода"

        if any(word in text_lower for word in ["cost", "price", "pay", "fee"]):
            return "Налог"

        return "Нейтральный"

    def _determine_trust_level(self, text: str) -> str:
        """Определяет уровень доверия"""

        text_lower = text.lower()

        if any(
            word in text_lower for word in ["guarantee", "proven", "tested", "trusted"]
        ):
            return "Высокая"

        if any(word in text_lower for word in ["maybe", "might", "could", "possibly"]):
            return "Низкая"

        return "Средняя"

    def _determine_urgency_level(self, text: str) -> str:
        """Определяет уровень срочности"""

        text_lower = text.lower()

        if any(word in text_lower for word in ["now", "today", "immediate", "urgent"]):
            return "Высокая"

        if any(word in text_lower for word in ["soon", "quick", "fast"]):
            return "Средняя"

        return "Низкая"

    def _analyze_jtbd_scenarios(self, content: str) -> list[JTBDScenario]:
        """Анализирует JTBD сценарии"""

        # Базовая реализация - можно расширить
        scenarios = []

        # Пример JTBD сценария
        scenarios.append(
            JTBDScenario(
                big_jtbd="Улучшить бизнес-процессы",
                when_trigger="Когда нужно оптимизировать работу",
                medium_jtbd="Автоматизировать рутинные задачи",
                small_jtbd="Использовать инструменты автоматизации",
                implementing_files="landing_page_analysis",
                status="identified",
                relevance_score=7,
            )
        )

        return scenarios

    def _analyze_segments(
        self, content: str, offers: list[OfferAnalysis]
    ) -> dict[str, Any]:
        """Анализирует целевые сегменты"""

        segments = {}

        # Базовые сегменты
        segments["General Business"] = {
            "characteristics": "Общий бизнес-сегмент",
            "pain_points": ["Неэффективность", "Потеря времени"],
            "motivation": "Улучшение процессов",
            "relevant_offers": [offer.offer_text for offer in offers[:3]],
            "relevance": "🟡 Средняя",
        }

        return segments

    def _calculate_rating(
        self, offers: list[OfferAnalysis], segments: dict[str, Any]
    ) -> int:
        """Рассчитывает рейтинг лендинга"""

        # Базовая логика расчета рейтинга
        base_score: float = 3.0

        # Бонусы за количество офферов
        if len(offers) >= 10:
            base_score += 1
        elif len(offers) >= 5:
            base_score += 0.5

        # Бонусы за разнообразие типов офферов
        offer_types = {offer.offer_type for offer in offers}
        if len(offer_types) >= 4:
            base_score += 0.5

        # Бонусы за сегменты
        if len(segments) >= 2:
            base_score += 0.5

        return min(5, max(1, int(base_score)))

    def _generate_recommendations(
        self, offers: list[OfferAnalysis], segments: dict[str, Any]
    ) -> list[str]:
        """Генерирует рекомендации"""

        recommendations = []

        # Рекомендации на основе анализа
        if len(offers) < 5:
            recommendations.append("Добавить больше офферов и обещаний")

        offer_types = {offer.offer_type for offer in offers}
        if len(offer_types) < 3:
            recommendations.append("Разнообразить типы офферов")

        if len(segments) < 2:
            recommendations.append("Расширить сегментацию аудитории")

        return recommendations

    def _create_reflections(self) -> list[Any]:
        """Создает reflection checkpoints"""

        # Базовая реализация
        return []

    def _calculate_narrative_coherence(
        self, offers: list[OfferAnalysis], segments: dict[str, Any]
    ) -> int:
        """Рассчитывает narrative coherence score"""

        # Базовая логика
        base_score = 5

        if len(offers) >= 5:
            base_score += 2

        if len(segments) >= 2:
            base_score += 1

        return min(10, max(1, base_score))

    def _check_self_compliance(
        self, offers: list[OfferAnalysis], segments: dict[str, Any]
    ) -> bool:
        """Проверяет self compliance"""

        # Базовая проверка
        return len(offers) > 0 and len(segments) > 0
