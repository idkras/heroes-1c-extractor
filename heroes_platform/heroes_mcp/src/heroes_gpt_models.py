#!/usr/bin/env python3
"""
HeroesGPT Data Models - структуры данных для анализа лендингов

Основано на: HeroesGPT Standard v1.8 + Legacy system analysis
Стандарт: TDD-doc v2.0 + From-The-End Standard v2.4
Автор: AI Assistant
Дата: 15 Aug 2025
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class OfferAnalysis:
    """Структура анализа одного оффера"""

    offer_text: str
    offer_type: (
        str  # обещание/выгода/гарантия/соц_доказательство/позиционирование/функция
    )
    quantitative_data: str
    target_segment: str
    emotional_trigger: str
    value_tax_rating: str  # Выгода/Налог
    trust_level: str  # Высокая/Средняя/Низкая
    urgency_level: str  # Высокая/Средняя/Низкая


@dataclass
class JTBDScenario:
    """JTBD сценарий по стандарту v4.0"""

    big_jtbd: str
    when_trigger: str
    medium_jtbd: str
    small_jtbd: str
    implementing_files: str
    status: str
    relevance_score: int  # 1-10


@dataclass
class LandingAnalysis:
    """Результат анализа лендинга"""

    url: str
    business_type: str
    main_value_prop: str
    target_segments: list[str]
    analysis_time: float
    content_length: int
    price_category: str  # Low-tier/Mid-tier/High-tier
    primary_goal: str


@dataclass
class ReflectionCheckpoint:
    """Reflection checkpoint согласно Registry Standard v1.5"""

    stage: str
    questions: list[str]
    validation_criteria: list[str]
    timestamp: str
    passed: bool
    notes: Optional[str] = None


@dataclass
class HeroesGPTReport:
    """Полный отчет по стандарту heroesGPT v1.8"""

    id: str
    timestamp: str
    landing_analysis: LandingAnalysis
    offers_table: list[OfferAnalysis]
    jtbd_scenarios: list[JTBDScenario]
    segments: dict[str, Any]
    rating: int  # 1-5
    recommendations: list[str]
    reflections: list[ReflectionCheckpoint]
    narrative_coherence_score: int  # 1-10
    self_compliance_passed: bool
    analysis_metadata: dict[str, Any]


@dataclass
class AnalysisMetadata:
    """Метаданные анализа"""

    type: str = "heroes_gpt_analysis"
    analysis_id: str = None  # type: ignore
    created: str = None  # type: ignore
    analyzed_url: str = None  # type: ignore
    analysis_type: str = "landing_page"
    standard_version: str = "HeroesGPT Landing Analysis Standard v1.8"
    requestor: str = "User"
    status: str = "In Progress"
    quality_check: str = "PENDING"

    def __post_init__(self):
        if self.analysis_id is None:
            self.analysis_id = f"HGA{str(uuid4())[:8].upper()}"
        if self.created is None:
            self.created = datetime.now().strftime(
                "%d %b %Y, %H:%M CET by AI Assistant"
            )


@dataclass
class SegmentAnalysis:
    """Анализ целевого сегмента"""

    segment_name: str
    characteristics: str
    pain_points: list[str]
    motivation: str
    relevant_offers: list[str]
    artifact_relevance: str  # 🟢 Идеальная/🟡 Средняя/🔴 Низкая
    jtbd_scenarios: list[JTBDScenario]


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""

    analysis_time: float
    content_processed: int
    offers_found: int
    segments_identified: int
    memory_usage: float
    cpu_usage: float


def create_heroes_gpt_report(
    url: str,
    landing_analysis: LandingAnalysis,
    offers_table: list[OfferAnalysis],
    jtbd_scenarios: list[JTBDScenario],
    segments: dict[str, Any],
    rating: int,
    recommendations: list[str],
    reflections: list[ReflectionCheckpoint],
    narrative_coherence_score: int,
    self_compliance_passed: bool,
) -> HeroesGPTReport:
    """Создает полный отчет HeroesGPT"""

    metadata = AnalysisMetadata(analyzed_url=url)

    return HeroesGPTReport(
        id=metadata.analysis_id,
        timestamp=metadata.created,
        landing_analysis=landing_analysis,
        offers_table=offers_table,
        jtbd_scenarios=jtbd_scenarios,
        segments=segments,
        rating=rating,
        recommendations=recommendations,
        reflections=reflections,
        narrative_coherence_score=narrative_coherence_score,
        self_compliance_passed=self_compliance_passed,
        analysis_metadata=asdict(metadata),
    )


def validate_heroes_gpt_report(report: HeroesGPTReport) -> bool:
    """Валидирует отчет HeroesGPT"""

    # Проверка обязательных полей
    if not report.id or not report.timestamp:
        return False

    if not report.landing_analysis or not report.landing_analysis.url:
        return False

    if not report.offers_table:
        return False

    # Проверка рейтинга
    if not (1 <= report.rating <= 5):
        return False

    # Проверка narrative coherence score
    if not (1 <= report.narrative_coherence_score <= 10):
        return False

    return True


def format_heroes_gpt_report(report: HeroesGPTReport) -> str:
    """Форматирует отчет HeroesGPT в markdown"""

    if not validate_heroes_gpt_report(report):
        raise ValueError("Invalid HeroesGPT report")

    # Метаданные
    metadata = report.analysis_metadata
    md = f"""# 🔍 Heroes-GPT: {metadata["analyzed_url"]} Analysis

<!-- 🔒 МЕТАДАННЫЕ АНАЛИЗА: BEGIN -->
type: {metadata["type"]}
analysis_id: {metadata["analysis_id"]}
created: {metadata["created"]}
analyzed_url: {metadata["analyzed_url"]}
analysis_type: {metadata["analysis_type"]}
standard_version: {metadata["standard_version"]}
requestor: {metadata["requestor"]}
status: {metadata["status"]}
quality_check: {metadata["quality_check"]}
<!-- 🔒 МЕТАДАННЫЕ АНАЛИЗА: END -->

---

<details open>
<summary>## 📊 Общий обзор</summary>

{report.landing_analysis.main_value_prop}

**Тип бизнеса:** {report.landing_analysis.business_type}
**Основная цель артефакта:** {report.landing_analysis.primary_goal}
**Ценовая категория:** {report.landing_analysis.price_category}
**Общее впечатление:** {", ".join(report.landing_analysis.target_segments[:3])}

</details>

---

<details open><summary>## 📋 ПОЛНЫЙ АНАЛИЗ ОФЕРОВ И СООБЩЕНИЙ</summary>

**КРИТИЧЕСКИ ВАЖНЫЙ ЭТАП**: Выписываем ВСЕ офферы, сообщения и обещания с лендинга в структурированную таблицу.

### Таблица анализа оферов:

| № | Текст оффера/сообщения | Тип | Количественные данные | Сегмент аудитории | Эмоциональный триггер | Доверие | Срочность |
|---|------------------------|-----|---------------------|-------------------|---------------------|---------|-----------|
"""

    # Добавляем офферы
    for i, offer in enumerate(report.offers_table, 1):
        md += f'| {i} | "{offer.offer_text}" | {offer.offer_type} | {offer.quantitative_data} | {offer.target_segment} | {offer.emotional_trigger} | {offer.trust_level} | {offer.urgency_level} |\n'

    md += """

### 📊 Анализ по категориям оферов:

"""

    # Группируем офферы по типам
    offer_types: dict[str, list[Any]] = {}
    for offer in report.offers_table:
        if offer.offer_type not in offer_types:
            offer_types[offer.offer_type] = []
        offer_types[offer.offer_type].append(offer)

    for offer_type, offers in offer_types.items():
        md += f"#### {offer_type.title()} ({len(offers)} офферов):\n"
        for offer in offers:
            md += f"- **{offer.offer_text}** - {offer.emotional_trigger}\n"
        md += "\n"

    md += "---\n\n"

    # Добавляем сегментацию
    md += """<details open>
<summary>## 👥 Расширенная сегментация целевой аудитории</summary>

"""

    for segment_name, segment_data in report.segments.items():
        if isinstance(segment_data, dict):
            md += f"""### {segment_name}
- **Характеристики**: {segment_data.get("characteristics", "N/A")}
- **Боли**: {", ".join(segment_data.get("pain_points", []))}
- **Мотивация**: {segment_data.get("motivation", "N/A")}
- **Релевантные офферы**: {", ".join(segment_data.get("relevant_offers", []))}
- **Релевантность артефакта**: {segment_data.get("relevance", "N/A")}

"""

    md += "</details>\n\n---\n\n"

    # Добавляем рекомендации
    if report.recommendations:
        md += """<details open>
<summary>## 💡 Рекомендации</summary>

"""
        for i, rec in enumerate(report.recommendations, 1):
            md += f"{i}. {rec}\n"
        md += "\n</details>\n\n"

    # Добавляем метрики
    md += f"""## 📈 Метрики анализа

- **Рейтинг лендинга**: {report.rating}/5
- **Narrative Coherence Score**: {report.narrative_coherence_score}/10
- **Self Compliance**: {"✅ PASSED" if report.self_compliance_passed else "❌ FAILED"}
- **Время анализа**: {report.landing_analysis.analysis_time:.2f} сек
- **Обработано контента**: {report.landing_analysis.content_length} символов
- **Найдено офферов**: {len(report.offers_table)}
- **Определено сегментов**: {len(report.segments)}

"""

    return md
