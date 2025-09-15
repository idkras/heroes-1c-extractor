#!/usr/bin/env python3
"""
Demo HeroesGPT v1.5 Real Landing Analysis
Демонстрация анализа реального контента с сохранением отчета
"""

import asyncio
import sys
import json
from datetime import datetime

sys.path.append('.')
from advising_platform.src.mcp.heroes.heroes_workflow_orchestrator import analyze_landing

async def demo_real_landing_analysis():
    """Демонстрация анализа реального лендинга"""
    
    # Контент типичного образовательного лендинга
    real_landing_content = """
    Станьте востребованным Data Scientist за 6 месяцев
    
    Гарантируем трудоустройство в IT-компанию или возвращаем 100% стоимости
    
    Что вас ждет:
    ✓ Обучение с нуля до уровня Middle специалиста
    ✓ Реальные проекты в портфолио
    ✓ Помощь в трудоустройстве от HR-партнеров
    ✓ Менторская поддержка 24/7
    ✓ Доступ к закрытому комьюнити выпускников
    
    Наши выпускники работают в:
    • Яндекс • Сбер • ВТБ • Альфа-банк • Авито
    
    За 3 года выпустили 2,847 специалистов
    Средняя зарплата выпускника: 180,000 рублей
    
    Программа обучения:
    
    Модуль 1: Python и основы программирования (4 недели)
    - Синтаксис Python
    - Работа с данными (Pandas, NumPy)
    - Визуализация (Matplotlib, Seaborn)
    
    Модуль 2: Машинное обучение (8 недель)
    - Scikit-learn
    - Классификация и регрессия
    - Кластеризация
    - Нейронные сети
    
    Модуль 3: Глубокое обучение (6 недель)
    - TensorFlow и PyTorch
    - Computer Vision
    - NLP
    
    Модуль 4: Проектная работа (6 недель)
    - 3 проекта в портфолио
    - Презентация работодателям
    
    Стоимость: 
    Полная стоимость: 198,000 рублей
    При оплате сегодня: 89,000 рублей (скидка 55%)
    
    Рассрочка: от 7,400 рублей в месяц
    
    Бонусы при записи сегодня:
    + Бесплатный курс "Английский для IT" (стоимость 29,000₽)
    + Год доступа к платформе с задачами
    + Персональная консультация с карьерным консультантом
    
    Отзывы выпускников:
    
    "Прошел курс полгода назад, сейчас работаю в Сбере на зарплате 220к. 
    Очень доволен качеством обучения и поддержкой." - Алексей К.
    
    "Без технического образования за 8 месяцев стала ML-инженером. 
    Курс дал все необходимые знания." - Мария С.
    
    "Получил оффер в Яндексе через 2 месяца после окончания курса. 
    Рекомендую всем!" - Дмитрий П.
    
    Гарантии:
    ✓ Возврат 100% средств, если не найдете работу в течение 6 месяцев
    ✓ Бесплатное продление курса, если не усвоили материал
    ✓ Помощь в составлении резюме и подготовке к собеседованиям
    
    FAQ:
    В: Подойдет ли курс без технического образования?
    О: Да, 70% наших студентов приходят без опыта в программировании
    
    В: Сколько времени нужно заниматься?
    О: 15-20 часов в неделю для комфортного освоения материала
    
    В: Какие навыки нужны для трудоустройства?
    О: Все необходимые навыки даются в рамках курса
    
    Запишитесь на бесплатный вебинар и получите:
    • Карту развития Data Scientist
    • Чек-лист подготовки к собеседованию
    • Доступ к первому уроку курса
    
    Количество мест ограничено - осталось 12 из 30
    До конца акции: 2 дня 14 часов 23 минуты
    
    ЗАПИСАТЬСЯ СО СКИДКОЙ 55%
    """
    
    print("🚀 Запуск анализа реального образовательного лендинга")
    print("=" * 70)
    print(f"📝 Длина контента: {len(real_landing_content)} символов")
    print("🎯 Применяем HeroesGPT Standard v1.5")
    print()
    
    try:
        # Запуск полного анализа
        report = await analyze_landing(content=real_landing_content)
        
        print("✅ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО")
        print("=" * 50)
        print(f"📊 ID отчета: {report.id}")
        print(f"⭐ Общая оценка: {report.rating}/5")
        print(f"📝 Narrative coherence: {report.narrative_coherence_score}/10")
        print(f"🔍 Self-compliance: {'PASSED' if report.self_compliance_passed else 'FAILED'}")
        print()
        
        # Детальная статистика
        print("📈 СТАТИСТИКА АНАЛИЗА:")
        print("-" * 30)
        print(f"• Найдено оферов: {len(report.offers_table)}")
        print(f"• JTBD сценариев: {len(report.jtbd_scenarios)}")
        print(f"• Пользовательских сегментов: {len(report.segments)}")
        print(f"• Рекомендаций: {len(report.recommendations)}")
        print(f"• Reflections checkpoints: {len(report.reflections)}")
        print()
        
        # Анализ оферов по типам
        offer_types = {}
        value_benefits = 0
        tax_offers = 0
        
        for offer in report.offers_table:
            offer_type = offer.offer_type
            if offer_type not in offer_types:
                offer_types[offer_type] = 0
            offer_types[offer_type] += 1
            
            if hasattr(offer, 'value_tax_rating'):
                if "выгода" in offer.value_tax_rating.lower():
                    value_benefits += 1
                elif "налог" in offer.value_tax_rating.lower():
                    tax_offers += 1
        
        print("🎯 АНАЛИЗ ОФЕРОВ:")
        print("-" * 20)
        for offer_type, count in offer_types.items():
            print(f"• {offer_type}: {count}")
        print()
        print(f"⚖️ ВЫГОДА/НАЛОГ:")
        print(f"• Выгоды: {value_benefits}")
        print(f"• Налоги: {tax_offers}")
        print()
        
        # Топ-5 оферов
        print("🔝 ТОП-5 ОФЕРОВ:")
        print("-" * 20)
        for i, offer in enumerate(report.offers_table[:5], 1):
            rating = getattr(offer, 'value_tax_rating', 'не определено')
            print(f"{i}. \"{offer.offer_text[:60]}...\"")
            print(f"   Тип: {offer.offer_type} | Оценка: {rating}")
            print()
        
        # JTBD анализ
        print("🎯 JTBD СЦЕНАРИИ:")
        print("-" * 20)
        for i, jtbd in enumerate(report.jtbd_scenarios[:5], 1):
            print(f"{i}. {jtbd.big_jtbd}")
            print(f"   When: {jtbd.when_trigger}")
            print(f"   Status: {jtbd.status}")
            print()
        
        # Reflections status
        print("🔍 REFLECTIONS CHECKPOINTS:")
        print("-" * 30)
        passed = sum(1 for r in report.reflections if r.passed)
        total = len(report.reflections)
        print(f"Пройдено: {passed}/{total}")
        
        for reflection in report.reflections:
            status = "✅" if reflection.passed else "❌"
            print(f"{status} {reflection.stage}")
        print()
        
        # Рекомендации
        print("💡 РЕКОМЕНДАЦИИ:")
        print("-" * 20)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
        print()
        
        # Сохранение детального JSON отчета
        report_data = {
            "id": report.id,
            "timestamp": report.timestamp,
            "rating": report.rating,
            "narrative_coherence": report.narrative_coherence_score,
            "self_compliance": report.self_compliance_passed,
            "statistics": {
                "offers_count": len(report.offers_table),
                "jtbd_count": len(report.jtbd_scenarios),
                "segments_count": len(report.segments),
                "recommendations_count": len(report.recommendations),
                "reflections_passed": passed,
                "reflections_total": total,
                "value_benefits": value_benefits,
                "tax_offers": tax_offers
            },
            "offer_types": offer_types,
            "top_offers": [
                {
                    "text": offer.offer_text[:100],
                    "type": offer.offer_type,
                    "rating": getattr(offer, 'value_tax_rating', 'не определено')
                }
                for offer in report.offers_table[:10]
            ]
        }
        
        filename = f"heroes_v15_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Детальный отчет сохранен: {filename}")
        print()
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("HeroesGPT v1.5 workflow работает корректно!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(demo_real_landing_analysis())
    sys.exit(0 if success else 1)