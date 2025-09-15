#!/usr/bin/env python3
"""
Test Enhanced Ilya Krasinsky Review Standard with Advanced Conversion Principles
"""

import sys
sys.path.append('/home/runner/workspace')

from advising_platform.src.mcp.python_backends.ilya_review_challenge import IlyaReviewChallenger

def main():
    challenger = IlyaReviewChallenger()
    
    # Test content with multiple conversion issues
    advanced_test_content = """
# Новый SaaS продукт — Landing Review

## Hero Section
Наша компания предлагает революционное решение для всех типов бизнеса.
Мы являемся лидерами рынка с инновационными технологиями.

## Pricing
У нас есть два простых тарифа:
- Базовый: $99/месяц
- Премиум: $299/месяц

Выберите любой когда удобно, без ограничений по времени.

## Features
Вся информация о продукте доступна на одной странице:
- Полное описание всех возможностей
- Технические характеристики системы  
- Все детали сразу для вашего удобства

## Onboarding
Готовое решение без усилий - автоматическая настройка за вас.
Стандартный процесс для всех клиентов.

## Benefits
Получите выгоды от нашего продукта:
- Приобретете бонусные функции
- Плюсы продукта очевидны

## Process
Средний опыт пользователей показывает обычный процесс покупки.
Завершенный процесс регистрации с полной информацией.

## Recommendations
- Улучшить дизайн
- Добавить больше контента
- Общие советы по оптимизации
"""
    
    print("=== ТЕСТ РАСШИРЕННОГО ILYA KRASINSKY REVIEW STANDARD ===\n")
    
    # Анализируем с фокусом на продвинутые принципы
    focus_areas = [
        "user_centric", "no_decoy", "info_overload", "no_effort_investment", 
        "no_loss_aversion", "no_temporal_anchor", "peak_end_missing",
        "segment_gaps", "no_tasks"
    ]
    
    analysis = challenger.analyze_document(advanced_test_content, "landing_review")
    
    print(f"📊 Оценка качества: {analysis['quality_score']:.1f}/10")
    print(f"🎯 Найдено областей для челленджа: {len(analysis['challenge_areas'])}")
    
    if analysis['challenge_areas']:
        print("\n💭 КОММЕНТАРИИ-ЧЕЛЛЕНДЖИ ОТ ИЛЬИ КРАСИНСКОГО:")
        for i, challenge in enumerate(analysis['challenge_areas'], 1):
            print(f"\n{i}. [{challenge['type']}]")
            print(f"   {challenge['comment']}")
    
    # Тестируем специфические челленджи
    specific_result = challenger.challenge_specific_content(advanced_test_content, focus_areas)
    
    if specific_result['focused_challenges']:
        print(f"\n🔍 ЦЕЛЕВЫЕ ЧЕЛЛЕНДЖИ ({len(specific_result['focused_challenges'])} найдено):")
        for challenge in specific_result['focused_challenges']:
            print(f"- {challenge['area']}: {challenge['comment'][:80]}...")
    
    # Добавляем комментарии в документ
    enhanced_content = challenger.inject_challenges(advanced_test_content, analysis)
    
    print("\n" + "="*80)
    print("ИТОГОВЫЙ ДОКУМЕНТ С КОММЕНТАРИЯМИ ИЛЬИ КРАСИНСКОГО:")
    print("="*80)
    print(enhanced_content)
    
    # Сохраняем результат
    with open('advising_platform/enhanced_review_with_advanced_challenges.md', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"\n✅ Результат сохранен в: enhanced_review_with_advanced_challenges.md")
    print(f"📈 Покрытие принципов: {len(analysis['challenge_areas'])}/32 возможных")

if __name__ == "__main__":
    main()