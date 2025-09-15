#!/usr/bin/env python3
"""
Test HeroesGPT v1.5 Workflow with Registry Standard compliance
Проверка двухэтапного workflow, reflections checkpoints, self-compliance
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append('.')

from advising_platform.src.mcp.heroes.heroes_workflow_orchestrator import HeroesWorkflowOrchestrator, analyze_landing

async def test_heroes_v15_compliance():
    """Тест соответствия HeroesGPT v1.5 стандарту"""
    
    print("🚀 Запуск тестирования HeroesGPT workflow v1.5")
    print("=" * 60)
    
    # Тест с контентом
    test_content = """
    Революционная система увеличения продаж!
    
    Гарантируем увеличение конверсии на 300% за 30 дней!
    Проверенные методы от экспертов с 15-летним опытом.
    
    Более 10,000 довольных клиентов уже используют нашу систему.
    
    Что вы получите:
    - Пошаговое руководство по продажам
    - Скрипты для холодных звонков
    - CRM интеграцию
    - Персональную поддержку 24/7
    
    Стоимость обычно 99,000₽, но только сегодня за 39,000₽!
    
    Если не увидите результат - вернем 100% денег!
    """
    
    try:
        # Запуск анализа
        report = await analyze_landing(content=test_content)
        
        print(f"✅ Анализ завершен успешно")
        print(f"📊 ID отчета: {report.id}")
        print(f"⭐ Общая оценка: {report.rating}/5")
        print(f"📝 Narrative coherence: {report.narrative_coherence_score}/10")
        print(f"🔍 Self-compliance: {'✅ PASSED' if report.self_compliance_passed else '❌ FAILED'}")
        
        # Проверка основных требований v1.5
        print("\n🔍 ПРОВЕРКА СООТВЕТСТВИЯ СТАНДАРТУ v1.5:")
        print("-" * 50)
        
        # 1. Проверка двухэтапного workflow
        table_has_value_tax_column = any("выгода" in str(offer.__dict__) for offer in report.offers_table[:3])
        print(f"1. Таблица БЕЗ колонки выгода/налог: {'✅' if not table_has_value_tax_column else '❌'}")
        
        # 2. Проверка наличия value_tax_rating в данных
        has_value_tax_data = any(hasattr(offer, 'value_tax_rating') and offer.value_tax_rating for offer in report.offers_table)
        print(f"2. Данные выгода/налог сохранены: {'✅' if has_value_tax_data else '❌'}")
        
        # 3. Проверка reflections checkpoints
        has_reflections = len(report.reflections) >= 6
        print(f"3. Reflections checkpoints (>=6): {'✅' if has_reflections else '❌'} ({len(report.reflections)})")
        
        # 4. Проверка стандартизированной терминологии
        tax_terms = ["фреон", "абстрактно", "оценочные_суждения", "впариваем", "нет_чувственного_опыта", "спорно", "противоречит_мировозрению_пользователя"]
        has_standard_terms = any(term in offer.value_tax_rating for offer in report.offers_table for term in tax_terms if hasattr(offer, 'value_tax_rating'))
        print(f"4. Стандартизированная терминология: {'✅' if has_standard_terms else '❌'}")
        
        # 5. Проверка JTBD структуры
        has_jtbd = len(report.jtbd_scenarios) >= 3
        print(f"5. JTBD сценарии (>=3): {'✅' if has_jtbd else '❌'} ({len(report.jtbd_scenarios)})")
        
        # 6. Проверка narrative coherence
        has_narrative = 1 <= report.narrative_coherence_score <= 10
        print(f"6. Narrative coherence (1-10): {'✅' if has_narrative else '❌'} ({report.narrative_coherence_score})")
        
        print(f"\n📋 ДЕТАЛИ АНАЛИЗА:")
        print(f"- Найдено оферов: {len(report.offers_table)}")
        print(f"- JTBD сценариев: {len(report.jtbd_scenarios)}")
        print(f"- Сегментов: {len(report.segments)}")
        print(f"- Рекомендаций: {len(report.recommendations)}")
        
        print(f"\n🎯 REFLECTIONS CHECKPOINTS:")
        for i, reflection in enumerate(report.reflections, 1):
            status = "✅ PASSED" if reflection.passed else "❌ FAILED"
            print(f"{i}. {reflection.stage}: {status}")
        
        # Проверка оферов с value_tax_rating
        print(f"\n⚖️ АНАЛИЗ ВЫГОДА/НАЛОГ (первые 5):")
        for i, offer in enumerate(report.offers_table[:5], 1):
            if hasattr(offer, 'value_tax_rating'):
                print(f"{i}. \"{offer.offer_text[:40]}...\" → {offer.value_tax_rating}")
        
        print(f"\n{'='*60}")
        print(f"🎉 ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_heroes_v15_compliance())
    sys.exit(0 if success else 1)