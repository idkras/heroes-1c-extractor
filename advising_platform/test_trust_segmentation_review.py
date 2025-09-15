#!/usr/bin/env python3
"""
Test Trust & Behavioral Segmentation Principles in Ilya Krasinsky Review Standard
"""

import sys
sys.path.append('/home/runner/workspace')

from advising_platform.src.mcp.python_backends.ilya_review_challenge import IlyaReviewChallenger

def main():
    challenger = IlyaReviewChallenger()
    
    # Content with trust and segmentation issues
    trust_test_content = """
# B2B Enterprise Software — Landing Review

## Hero Section
Наша платформа для всех типов компаний. 
Универсальное решение для любого бизнеса без различий.
Тысячи пользователей уже довольны нашим продуктом.

## Trust Section
Просто поверьте нам на слово - мы лучшие.
Без доказательств, но много клиентов используют.
Быстрое решение - сразу покупайте, не думайте.

## Value Proposition  
Одна ценность для всех полезна:
- Станете лучше
- Будет хорошо
- Улучшится всё

## Targeting
Мужчины 30-40 лет, женщины 25-35 лет.
Возрастная группа предпринимателей.
Для всех типов личности одинаковый подход.

## Features
Все преимущества сразу:
- Полный список возможностей
- Всё включено в базовый пакет
- Одна ценность универсальная
- Просто купите без эмоций

## Risk Management
Один риск для всех, универсальные гарантии.
Все защищены одинаково, стандартная презентация.

## Call to Action
Любой может купить в любое время когда удобно, без ограничений.
"""
    
    print("=== ТЕСТ ПРИНЦИПОВ ДОВЕРИЯ И ПОВЕДЕНЧЕСКОЙ СЕГМЕНТАЦИИ ===\n")
    
    # Focus on trust and segmentation patterns
    trust_focus_areas = [
        "missing_trust_stack", "generic_personas", "no_temporal_trust", 
        "weak_social_proof", "no_value_alignment", "missing_bias_segmentation",
        "no_risk_adaptation", "weak_future_vision", "demographic_targeting",
        "flat_emotional_journey", "no_identity_alignment", "value_dump"
    ]
    
    analysis = challenger.analyze_document(trust_test_content, "landing_review")
    
    print(f"📊 Базовая оценка качества: {analysis['quality_score']:.1f}/10")
    print(f"🎯 Обнаружено проблем: {len(analysis['challenge_areas'])}")
    
    # Test specific trust and segmentation challenges
    specific_result = challenger.challenge_specific_content(trust_test_content, trust_focus_areas)
    
    print(f"\n🔍 ЦЕЛЕВЫЕ ПРИНЦИПЫ ДОВЕРИЯ И СЕГМЕНТАЦИИ:")
    print(f"Найдено проблем: {len(specific_result['focused_challenges'])}")
    
    for i, challenge in enumerate(specific_result['focused_challenges'], 1):
        print(f"\n{i}. 🎯 {challenge['area'].upper()}")
        print(f"   💬 {challenge['comment']}")
    
    # Generate enhanced content with trust and segmentation insights
    enhanced_content = challenger.inject_challenges(trust_test_content, analysis)
    
    print(f"\n{'='*80}")
    print("ДОКУМЕНТ С ПРИНЦИПАМИ ДОВЕРИЯ И СЕГМЕНТАЦИИ:")
    print(f"{'='*80}")
    print(enhanced_content)
    
    # Save comprehensive result
    with open('advising_platform/trust_segmentation_review_enhanced.md', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"\n✅ Расширенный анализ сохранен в: trust_segmentation_review_enhanced.md")
    print(f"📈 Покрытие принципов доверия: {len(specific_result['focused_challenges'])}/12")
    print(f"🧠 Общий охват стандарта: {len(analysis['challenge_areas'])}/44 принципов")

if __name__ == "__main__":
    main()