"""
TDD тесты для HeroesGPT MCP Workflow
Проверка соответствия всем критериям гипотезы
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path

from advising_platform.src.mcp.heroes.heroes_workflow_orchestrator import (
    HeroesWorkflowOrchestrator,
    analyze_landing
)

class TestHeroesWorkflowTDD:
    """TDD тесты для проверки гипотезы heroesGPT workflow"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.orchestrator = HeroesWorkflowOrchestrator()
        
    # === RED PHASE TESTS (критерии фальсификации) ===
    
    @pytest.mark.asyncio
    async def test_analysis_time_under_5_minutes(self):
        """КРИТЕРИЙ ФАЛЬСИФИКАЦИИ: время анализа >10 минут"""
        start_time = datetime.now()
        
        report = await analyze_landing(
            url="https://example.com/test-landing"
        )
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        # КРИТИЧНО: должно быть <5 минут (300 секунд)
        assert analysis_time < 300, f"Анализ занял {analysis_time:.1f}с > 5 минут"
        
        # ЖЕЛАТЕЛЬНО: <2 минут для быстрого feedback
        if analysis_time < 120:
            print(f"🚀 Отличная скорость: {analysis_time:.1f}с")
        
    @pytest.mark.asyncio
    async def test_offers_extraction_over_90_percent(self):
        """КРИТЕРИЙ ФАЛЬСИФИКАЦИИ: пропущено >10% оферов"""
        report = await analyze_landing(
            content="Тестовый лендинг с множеством оферов..."
        )
        
        offers = report.offers_table
        
        # Минимум 20 оферов для детального лендинга
        assert len(offers) >= 20, f"Найдено только {len(offers)} оферов < 20"
        
        # Проверка качества извлечения
        valid_offers = [o for o in offers if o.offer_text and o.offer_type]
        quality_ratio = len(valid_offers) / len(offers)
        
        assert quality_ratio >= 0.9, f"Качество извлечения {quality_ratio:.1%} < 90%"
        
        # Проверка разнообразия типов
        offer_types = set(o.offer_type for o in offers)
        assert len(offer_types) >= 3, f"Мало типов оферов: {offer_types}"
        
    @pytest.mark.asyncio 
    async def test_auto_save_100_percent(self):
        """КРИТЕРИЙ ФАЛЬСИФИКАЦИИ: отсутствует автосохранение"""
        report = await analyze_landing(
            url="https://example.com/autosave-test"
        )
        
        # Проверяем что файлы созданы
        output_dir = Path("[projects]/[heroes-gpt-bot]/review-results/")
        
        # Основной отчет
        report_files = list(output_dir.glob(f"analysis_landing_*_{report.id}.md"))
        assert len(report_files) == 1, "Отчет не сохранен в markdown"
        
        # JSON данные
        data_files = list(output_dir.glob(f"data_*_{report.id}.json"))
        assert len(data_files) == 1, "Данные не сохранены в JSON"
        
        # Индекс обновлен
        index_file = output_dir / "analysis_index.json"
        assert index_file.exists(), "Индекс анализов не создан"
        
    @pytest.mark.asyncio
    async def test_heroesgpt_standard_compliance(self):
        """КРИТЕРИЙ ФАЛЬСИФИКАЦИИ: нарушение >20% требований стандарта"""
        report = await analyze_landing(
            url="https://example.com/standard-test"
        )
        
        # Проверка всех обязательных секций героесGPT стандарта
        required_sections = [
            'landing_analysis',  # Общий обзор
            'offers_table',      # Полный анализ оферов  
            'jtbd_scenarios',    # Задачи пользователя (JTBD)
            'segments',          # Сегментация
            'rating',            # Рейтинговая оценка
            'recommendations'    # Рекомендации
        ]
        
        missing_sections = []
        for section in required_sections:
            if not hasattr(report, section) or getattr(report, section) is None:
                missing_sections.append(section)
        
        compliance_ratio = (len(required_sections) - len(missing_sections)) / len(required_sections)
        assert compliance_ratio >= 0.8, f"Соответствие стандарту {compliance_ratio:.1%} < 80%"
        
        # Проверка структуры таблицы оферов
        if report.offers_table:
            offer = report.offers_table[0]
            required_offer_fields = [
                'offer_text', 'offer_type', 'quantitative_data',
                'target_segment', 'emotional_trigger', 'value_tax_rating'
            ]
            
            for field in required_offer_fields:
                assert hasattr(offer, field), f"Отсутствует поле {field} в анализе оферов"
    
    @pytest.mark.asyncio
    async def test_jtbd_table_creation(self):
        """КРИТЕРИЙ ФАЛЬСИФИКАЦИИ: не создается JTBD таблица по стандарту v4.0"""
        report = await analyze_landing(
            url="https://example.com/jtbd-test"
        )
        
        jtbd_scenarios = report.jtbd_scenarios
        
        # Минимум 8-12 Big JTBD по стандарту
        assert len(jtbd_scenarios) >= 8, f"JTBD сценариев {len(jtbd_scenarios)} < 8"
        assert len(jtbd_scenarios) <= 15, f"Слишком много JTBD: {len(jtbd_scenarios)} > 15"
        
        # Проверка структуры каждого сценария
        required_jtbd_fields = [
            'big_jtbd', 'when_trigger', 'medium_jtbd', 
            'small_jtbd', 'implementing_files', 'status'
        ]
        
        for scenario in jtbd_scenarios:
            for field in required_jtbd_fields:
                assert hasattr(scenario, field), f"JTBD сценарий без поля {field}"
                assert getattr(scenario, field), f"Пустое поле {field} в JTBD"
        
        # Проверка качества триггеров
        triggers = [s.when_trigger for s in jtbd_scenarios]
        unique_triggers = set(triggers)
        assert len(unique_triggers) >= len(triggers) * 0.8, "Слишком много дублирующихся триггеров"
    
    # === ДОПОЛНИТЕЛЬНЫЕ КАЧЕСТВЕННЫЕ ТЕСТЫ ===
    
    @pytest.mark.asyncio
    async def test_value_tax_analysis_quality(self):
        """Тест качества анализа Выгода/Налог по Tone-Style Standard"""
        report = await analyze_landing(
            content="Инновационные решения для оптимизации ваших процессов с гарантией 100%"
        )
        
        offers = report.offers_table
        
        # Должны быть и выгоды, и налоги
        benefits = [o for o in offers if o.value_tax_rating == "Выгода"]
        taxes = [o for o in offers if o.value_tax_rating == "Налог"]
        
        assert len(benefits) > 0, "Не найдено ни одной выгоды"
        
        # Проверка конкретности в выгодах
        quantitative_benefits = [o for o in benefits if o.quantitative_data]
        if benefits:
            concrete_ratio = len(quantitative_benefits) / len(benefits)
            assert concrete_ratio >= 0.3, f"Мало конкретных выгод: {concrete_ratio:.1%}"
    
    @pytest.mark.asyncio
    async def test_segment_grouping_logic(self):
        """Тест логики группировки пользователей по триггерам"""
        report = await analyze_landing(
            url="https://example.com/segments-test"
        )
        
        segments = report.segments
        
        # Минимум 3 сегмента
        assert len(segments) >= 3, f"Сегментов {len(segments)} < 3"
        
        # Каждый сегмент должен иметь описание и триггеры
        for segment_name, segment_data in segments.items():
            assert 'description' in segment_data, f"Сегмент {segment_name} без описания"
            assert 'triggers' in segment_data, f"Сегмент {segment_name} без триггеров"
            assert 'motivations' in segment_data, f"Сегмент {segment_name} без мотиваций"
    
    @pytest.mark.asyncio
    async def test_rating_calculation_logic(self):
        """Тест логики расчета рейтинга 1-5"""
        report = await analyze_landing(
            url="https://example.com/rating-test"
        )
        
        rating = report.rating
        
        # Рейтинг должен быть в диапазоне 1-5
        assert 1 <= rating <= 5, f"Рейтинг {rating} вне диапазона 1-5"
        assert isinstance(rating, int), f"Рейтинг должен быть целым числом, получен {type(rating)}"
    
    @pytest.mark.asyncio
    async def test_recommendations_relevance(self):
        """Тест релевантности рекомендаций"""
        report = await analyze_landing(
            url="https://example.com/recommendations-test"
        )
        
        recommendations = report.recommendations
        
        # Минимум 5 рекомендаций
        assert len(recommendations) >= 5, f"Рекомендаций {len(recommendations)} < 5"
        
        # Максимум 10 (чтобы не перегружать)
        assert len(recommendations) <= 10, f"Слишком много рекомендаций: {len(recommendations)}"
        
        # Рекомендации должны быть содержательными
        meaningful_recs = [r for r in recommendations if len(r) > 20]
        assert len(meaningful_recs) >= len(recommendations) * 0.8, "Много поверхностных рекомендаций"
    
    # === ИНТЕГРАЦИОННЫЕ ТЕСТЫ ===
    
    @pytest.mark.asyncio
    async def test_different_input_types(self):
        """Тест работы с разными типами входных данных"""
        
        # Тест с URL
        report_url = await analyze_landing(url="https://example.com")
        assert report_url.landing_analysis.url == "https://example.com"
        
        # Тест с контентом
        test_content = "Тестовый лендинг с оферами"
        report_content = await analyze_landing(content=test_content)
        assert report_content.landing_analysis.content_length > 0
        
        # Тест со скриншотом
        report_screenshot = await analyze_landing(screenshot="/path/to/screenshot.png")
        assert report_screenshot.landing_analysis.url == "/path/to/screenshot.png"
    
    @pytest.mark.asyncio 
    async def test_error_handling(self):
        """Тест обработки ошибок"""
        
        # Тест с пустыми данными
        with pytest.raises(Exception):
            await analyze_landing()  # Все параметры None
        
        # Тест с некорректным URL (должен обрабатываться gracefully)
        try:
            report = await analyze_landing(url="invalid-url")
            # Если не упало - проверяем что создан минимальный отчет
            assert report is not None
            assert hasattr(report, 'rating')
        except Exception as e:
            # Ошибка должна быть информативной
            assert len(str(e)) > 10
    
    # === PERFORMANCE ТЕСТЫ ===
    
    @pytest.mark.asyncio
    async def test_batch_processing_capability(self):
        """Тест возможности batch обработки"""
        
        urls = [
            "https://example1.com",
            "https://example2.com", 
            "https://example3.com"
        ]
        
        start_time = datetime.now()
        
        # Параллельная обработка
        tasks = [analyze_landing(url=url) for url in urls]
        reports = await asyncio.gather(*tasks)
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Batch должен быть быстрее чем 3 последовательных анализа
        assert total_time < 600, f"Batch обработка заняла {total_time:.1f}с > 10 минут"
        assert len(reports) == 3, "Не все отчеты созданы"
        
        # Все отчеты должны быть валидными
        for report in reports:
            assert report.rating >= 1
            assert len(report.offers_table) > 0

def run_all_tests():
    """Запуск всех TDD тестов"""
    print("🧪 ЗАПУСК TDD ТЕСТОВ HEROЕSGPT WORKFLOW")
    print("="*60)
    
    # Запуск через pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ - ГИПОТЕЗА ПОДТВЕРЖДЕНА")
        print("🎉 HeroesGPT MCP Workflow готов к продакшну!")
    else:
        print("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ - ГИПОТЕЗА ОПРОВЕРГНУТА")
        print("🔧 Требуется доработка workflow")
    
    return exit_code == 0

if __name__ == "__main__":
    run_all_tests()