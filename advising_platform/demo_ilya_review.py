#!/usr/bin/env python3
"""
Демонстрация Ilya Krasinsky Review Standard на реальном контенте
"""

import sys
sys.path.append('/home/runner/workspace')

from advising_platform.src.mcp.python_backends.ilya_review_challenge import IlyaReviewChallenger

def main():
    challenger = IlyaReviewChallenger()
    
    # Тестовый контент из seller24 review с типичными проблемами
    test_content = """
# Seller24 Platform — Landing Review

## 3. Анализ дизайна и конверсии

### Hero Section
- **Headline:** "Увеличиваем продажи на маркетплейсах"
- **Subheadline:** Четкое позиционирование как агентство полного цикла
- **CTA:** "Получить консультацию" - ясный первый шаг

Наша компания предлагает лучшие решения для маркетплейсов.
Мы являемся лидерами рынка с 15-летним опытом работы.

### Services Overview
- Понятное разделение услуг по типам
- Четкие пакеты: "Старт", "Рост", "Масштабирование"
- Описание процессов работы

## 5. Recommendations

### High Priority
1. Добавить калькулятор стоимости - позволить клиентам оценить бюджет
2. Создать демо-кейс - показать процесс работы
3. Упростить форму заявки - убрать лишние поля

Общие рекомендации по улучшению дизайна и контента.
"""
    
    print("=== ДЕМОНСТРАЦИЯ ILYA KRASINSKY REVIEW STANDARD ===\n")
    
    # Анализируем документ
    analysis = challenger.analyze_document(test_content, "landing_review")
    
    print(f"📊 Оценка качества: {analysis['quality_score']:.1f}/10")
    print(f"🎯 Найдено областей для челленджа: {len(analysis['challenge_areas'])}")
    
    if analysis['challenge_areas']:
        print("\n💭 КОММЕНТАРИИ-ЧЕЛЛЕНДЖИ ОТ ИЛЬИ КРАСИНСКОГО:")
        for i, challenge in enumerate(analysis['challenge_areas'], 1):
            print(f"\n{i}. Тип: {challenge['type']}")
            print(f"   Комментарий: {challenge['comment']}")
    
    # Добавляем комментарии в документ
    enhanced_content = challenger.inject_challenges(test_content, analysis)
    
    print("\n" + "="*60)
    print("ДОКУМЕНТ С КОММЕНТАРИЯМИ ИЛЬИ КРАСИНСКОГО:")
    print("="*60)
    print(enhanced_content)
    
    # Сохраняем результат
    with open('advising_platform/demo_review_with_ilya_comments.md', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"\n✅ Результат сохранен в: demo_review_with_ilya_comments.md")

if __name__ == "__main__":
    main()