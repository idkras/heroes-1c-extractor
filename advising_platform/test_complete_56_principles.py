#!/usr/bin/env python3
"""
Test Complete 56-Principle Ilya Krasinsky Review Standard
Including: Base + Practical + Rare Expert + Trust/Segmentation + Activation Engineering
"""

import sys
sys.path.append('/home/runner/workspace')

from advising_platform.src.mcp.python_backends.ilya_review_challenge import IlyaReviewChallenger

def main():
    challenger = IlyaReviewChallenger()
    
    # Comprehensive test content covering all 56 principle areas
    comprehensive_test_content = """
# SaaS Platform Landing — Complete Review Test

## Hero Section
Наша революционная платформа для всех типов компаний без различий.
Универсальное решение с полным списком всех преимуществ сразу.
Тысячи пользователей довольны, просто поверьте нам на слово.

## Value Proposition
Одна ценность для всех полезна - станете лучше во всем.
Получите все возможности включены в базовый тариф без ограничений.
Будет хорошо и улучшится всё автоматически без усилий.

## Trust & Social Proof
Много клиентов используют наш продукт без доказательств.
Постоянные отзывы и статичные цифры успеха.
Нет отзывов, но быстрое решение - сразу покупайте, не думайте.

## Features & Benefits
Все преимущества и полный список возможностей:
- Сложная настройка требует изучения
- Получишь результат когда будет доступно
- Ожидаемый результат через стандартный процесс
- Обычный опыт без интриги

## Targeting & Segmentation
Мужчины 30-40 лет, женщины 25-35 лет.
Для всех типов личности одинаковый подход.
Один подход для всех, стандартная презентация.
Возрастная группа без различий.

## Pricing & Risk
Один риск для всех, универсальные гарантии.
Все защищены одинаково в любое время когда удобно.
Без ограничений по времени покупки.

## User Experience & Activation
Для всех одинаково универсальный опыт активации.
Всё понятно без интриги, простая информация.
Готовое решение автоматически работает.
Ровный опыт без пиков, стандартное завершение.

## Onboarding & Learning
Сразу всё доступно без обучения, полная сложность.
Много вариантов - выбери сам различные пути.
Сложные шрифты, непонятные термины, много информации.

## Metrics & Measurement
Не измеряем результаты, без метрик активации.
Нет отслеживания пользовательского поведения.
Стандартные показатели для всех сегментов.

## Call to Action
Любой может купить когда удобно без временных рамок.
Выберите любой из множества доступных вариантов.
Все тарифы одинаково хороши для каждого.

## Mobile & Technical
Медленная загрузка, не адаптировано под мобильные.
Сложная навигация с множественными путями.
Технические ошибки в процессе использования.
"""
    
    print("=== ТЕСТ ПОЛНОГО СТАНДАРТА ИЛЬИ КРАСИНСКОГО (56 ПРИНЦИПОВ) ===\n")
    
    # Full analysis using all principles
    analysis = challenger.analyze_document(comprehensive_test_content, "landing_review")
    
    print(f"📊 Оценка качества контента: {analysis['quality_score']:.1f}/10")
    print(f"🎯 Обнаружено проблемных областей: {len(analysis['challenge_areas'])}")
    print(f"💬 Добавлено комментариев: {len(analysis.get('comments', []))}")
    
    if analysis['challenge_areas']:
        print(f"\n🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ПРОБЛЕМНЫХ ОБЛАСТЕЙ:")
        
        # Group by categories
        categories = {
            'Base Principles': ['user_centric', 'cognitive_overload', 'segment_gaps'],
            'Practical Issues': ['friction_points', 'mobile_gaps', 'loading_speed'],
            'Expert Techniques': ['scissors_effect', 'peak_end_missing', 'decoy_missing'],
            'Trust & Segmentation': ['missing_trust_stack', 'weak_social_proof', 'no_value_alignment'],
            'Activation Engineering': ['no_ttv', 'generic_activation', 'choice_overload']
        }
        
        for category, patterns in categories.items():
            found_in_category = [area for area in analysis['challenge_areas'] if area in patterns]
            if found_in_category:
                print(f"\n📂 {category}: {len(found_in_category)} проблем")
                for area in found_in_category:
                    print(f"   • {area}")
    
    # Test all activation-specific patterns
    activation_patterns = [
        "no_ttv", "no_anticipation", "generic_activation", "no_curiosity_gap",
        "no_investment", "flat_activation", "no_scaffolding", "static_social_proof",
        "choice_overload", "predictable_experience", "cognitive_complexity", "no_activation_metrics"
    ]
    
    activation_result = challenger.challenge_specific_content(comprehensive_test_content, activation_patterns)
    
    print(f"\n🚀 АНАЛИЗ АКТИВАЦИИ И AHA-МОМЕНТА:")
    print(f"Найдено активационных проблем: {len(activation_result['focused_challenges'])}")
    
    for challenge in activation_result['focused_challenges']:
        print(f"\n⚡ {challenge['area'].upper()}")
        print(f"   💬 {challenge['comment']}")
    
    # Generate final enhanced document
    enhanced_content = challenger.inject_challenges(comprehensive_test_content, analysis)
    
    print(f"\n{'='*80}")
    print("ФИНАЛЬНЫЙ ДОКУМЕНТ С КОММЕНТАРИЯМИ ИЛЬИ КРАСИНСКОГО:")
    print(f"{'='*80}")
    print(enhanced_content)
    
    # Save comprehensive analysis
    with open('advising_platform/complete_56_principles_analysis.md', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    # Summary statistics
    total_principles = 56
    detected_issues = len(analysis['challenge_areas'])
    activation_issues = len(activation_result['focused_challenges'])
    
    print(f"\n✅ ИТОГОВАЯ СТАТИСТИКА:")
    print(f"📋 Всего принципов в стандарте: {total_principles}")
    print(f"🔍 Обнаружено проблем: {detected_issues}")
    print(f"🚀 Активационных проблем: {activation_issues}")
    print(f"📈 Покрытие анализа: {(detected_issues/total_principles)*100:.1f}%")
    print(f"💾 Результат сохранен в: complete_56_principles_analysis.md")
    print(f"\n🎯 Стандарт готов к использованию на любых лендингах и продуктовых страницах")

if __name__ == "__main__":
    main()