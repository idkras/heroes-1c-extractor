#!/usr/bin/env python3
"""
Ilya Krasinsky Review Challenge - MCP Backend
Adds challenge comments from Ilya Krasinsky to documents based on standards compliance
"""

import re
import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.append('/home/runner/workspace')

class IlyaReviewChallenger:
    def __init__(self):
        self.challenge_patterns = {
            "user_centric": {
                "pattern": r"(наш[а-я]*\s+продукт|мы\s+предлагаем|компания\s+является|наши\s+услуги)",
                "comment": "Илья К.: Здесь я вижу фокус на продукте вместо пользователя. По нашему стандарту, каждое сообщение должно отвечать на вопрос 'Что я получу?' с точки зрения пользователя. Переформулируй через призму выгод."
            },
            "cognitive_load": {
                "pattern": r"(технические\s+характеристики|сложные\s+термины|без\s+объяснения\s+выгод)",
                "comment": "Илья К.: Когнитивный налог! Этот блок забирает внимание, но не возвращает радость, смысл или пользу. По стандарту Ильяхова 'ясно-понятно' - либо убираем, либо превращаем в очевидную выгоду."
            },
            "segment_gaps": {
                "pattern": r"(один\s+размер\s+для\s+всех|универсальное\s+решение|общие\s+рекомендации)",
                "comment": "Илья К.: Не вижу учета конкретных сегментов. Где ответы на их специфические страхи? Детали создают доверие - добавь конкретику, которая резонирует именно с этой аудиторией."
            },
            "missing_vision": {
                "pattern": r"(без\s+четкого\s+плана|нет\s+пошаговых\s+действий|неясен\s+результат)",
                "comment": "Илья К.: Где пошаговый план получения выгоды? Пользователь должен видеть конкретный путь: делаю А → получаю Б → показываю другим В. Артефакт должен быть готов к использованию."
            },
            "no_tasks": {
                "pattern": r"(рекомендации\s+без\s+задач|общие\s+советы|нет\s+конкретных\s+действий)",
                "comment": "Илья К.: Отличный анализ, но где задачи? Нужен список с ролями, контекстом, ссылками и метриками успеха. Двойной контроль качества обязателен."
            },
            "missing_insights": {
                "pattern": r"(очевидная\s+информация|банальные\s+выводы|без\s+удивления)",
                "comment": "Илья К.: Где удивление по Шеннону? Лендинг должен давать активирующее знание, которое запускает пользователя в JTBD-сценарий. Сейчас это просто информация."
            },
            "trust_issues": {
                "pattern": r"(обещания\s+без\s+подтверждений|противоречивые\s+данные|сомнительные\s+утверждения)",
                "comment": "Илья К.: Здесь снижается доверие. Обещали одно, показываете другое. По нашему стандарту доверия - каждый элемент должен подтверждать предыдущие обещания."
            },
            "scissors_effect": {
                "pattern": r"(проблем[а-я]*\s+онбординг|сложн[а-я]*\s+регистрац|много\s+полей|долг[а-я]*\s+загрузк)",
                "comment": "Илья К.: Видишь эффект ножниц? Плохой онбординг → ↓конверсия → ↑CAC → ↓ROI → меньше трафика. Где твоя позитивная спираль?"
            },
            "peak_end_missing": {
                "pattern": r"(средн[а-я]*\s+опыт|обычн[а-я]*\s+процесс|стандартн[а-я]*\s+путь)",
                "comment": "Илья К.: Где пик удовольствия и как завершается опыт? Disney делает очереди веселыми, а выход - через магазин подарков."
            },
            "no_zeigarnik": {
                "pattern": r"(завершенн[а-я]*\s+процесс|полн[а-я]*\s+информац|все\s+сразу)",
                "comment": "Илья К.: Что оставляешь незавершенным? LinkedIn показывает '87% профиля заполнено'. Создавай напряжение незавершенности."
            },
            "no_decoy": {
                "pattern": r"(два\s+тарифа|простой\s+выбор|только\s+один\s+вариант)",
                "comment": "Илья К.: Где твой 'приманочный' тариф? Economist продавал подписку: digital $59, print $125, digital+print $125. Кто выберет только print?"
            },
            "no_isolation": {
                "pattern": r"(все\s+одинаков|похож[а-я]*\s+элемент|нет\s+выделения)",
                "comment": "Илья К.: Что выделяется изоляцией? Apple делает iPhone другого цвета в рекламе. Один элемент должен кричать."
            },
            "no_effort_investment": {
                "pattern": r"(готов[а-я]*\s+решение|без\s+усилий|автоматическ)",
                "comment": "Илья К.: Где пользователь вкладывает усилия? Nike By You дает кастомизацию кроссовок. Труд создает привязанность."
            },
            "info_overload": {
                "pattern": r"(вся\s+информация|полн[а-я]*\s+описание|все\s+детали\s+сразу)",
                "comment": "Илья К.: Не вываливаешь все сразу? TurboTax задает по одному вопросу. Сложность убивает, простота продает."
            },
            "no_ownership": {
                "pattern": r"(наш[а-я]*\s+продукт|общ[а-я]*\s+решение|стандартн[а-я]*\s+предложение)",
                "comment": "Илья К.: Как делаешь продукт 'моим'? Amazon пишет 'Ваши рекомендации'. Spotify создает 'Мой микс'. Обладание до покупки."
            },
            "no_loss_aversion": {
                "pattern": r"(получ[а-я]*\s+выгод|приобрет[а-я]*\s+бонус|плюс[а-я]*\s+продукт)",
                "comment": "Илья К.: Что теряет пользователь, НЕ купив? Booking.com: 'Осталось 2 номера, 5 человек смотрят'. Потеря > приобретение."
            },
            "no_temporal_anchor": {
                "pattern": r"(в\s+любое\s+время|когда\s+удобно|без\s+ограничений)",
                "comment": "Илья К.: Почему покупать именно сегодня? Duolingo напоминает о дне рождения стрика. Создавай значимые моменты."
            },
            "missing_trust_stack": {
                "pattern": r"(нет\s+отзывов|без\s+доказательств|просто\s+поверьте)",
                "comment": "Илья К.: Какой слой доверия сейчас строишь? Amazon начинает с компетентности (отзывы), потом надежность (доставка), эмпатия (возвраты), предсказуемость (Prime)."
            },
            "generic_personas": {
                "pattern": r"(для\s+всех|универсальное|одинаков[а-я]*\s+подход)",
                "comment": "Илья К.: Для аналитика нужны данные, для визуала - схемы, для кинестетика - пробные действия. Где персонализация доверия под психотип?"
            },
            "no_temporal_trust": {
                "pattern": r"(быстрое\s+решение|сразу\s+покупай|не\s+думай)",
                "comment": "Илья К.: Импульсивный покупает за 3 минуты, аналитик изучает неделю. Netflix дает сразу смотреть, Tesla - тест-драйв на выходные."
            },
            "weak_social_proof": {
                "pattern": r"(много\s+клиентов|тысячи\s+пользователей|все\s+довольны)",
                "comment": "Илья К.: 'Много клиентов' не работает. 'IT-директор из Сбера сэкономил 40% на инфраструктуре' - работает для IT-директоров."
            },
            "no_value_alignment": {
                "pattern": r"(одна\s+ценность|универсальн[а-я]*\s+выгод|для\s+всех\s+полезно)",
                "comment": "Илья К.: Для CFO говори про ROI, для CTO - про техничность, для CEO - про конкурентные преимущества. Одно решение, разные углы ценности."
            },
            "missing_bias_segmentation": {
                "pattern": r"(один\s+подход|все\s+одинаково|стандартн[а-я]*\s+презентация)",
                "comment": "Илья К.: Новички любят Authority (эксперты советуют), профи - Evidence (данные говорят). Какое искажение используешь для каждого сегмента?"
            },
            "no_risk_adaptation": {
                "pattern": r"(один\s+риск|универсальн[а-я]*\s+гарантии|все\s+защищены)",
                "comment": "Илья К.: Консерватору покажи 'используют 500 компаний', инноватору - 'первыми получат преимущество'. Где адаптация под риск-профиль?"
            },
            "weak_future_vision": {
                "pattern": r"(станете\s+лучше|будет\s+хорошо|улучшится\s+все)",
                "comment": "Илья К.: Startup-founder мечтает о масштабе, корпоративный менеджер - о стабильности. Salesforce показывает разные 'успешные компании' разным сегментам."
            },
            "demographic_targeting": {
                "pattern": r"(мужчины\s+30-40|женщины\s+25-35|возраст[а-я]*\s+группа)",
                "comment": "Илья К.: Не 'мужчины 30-40', а 'кто принимает решения быстро vs кто изучает детально'. Spotify знает музыкальное поведение, не возраст."
            },
            "flat_emotional_journey": {
                "pattern": r"(просто\s+купите|одно\s+решение|без\s+эмоций)",
                "comment": "Илья К.: Сомнение → любопытство → интерес → желание → уверенность → действие. На каком этапе твой пользователь? Apple Store ведет от touch к wow к want к buy."
            },
            "no_identity_alignment": {
                "pattern": r"(любой\s+может|для\s+всех\s+типов|без\s+различий)",
                "comment": "Илья К.: 'Я эко-осознанный' → Tesla. 'Я статусный' → BMW. 'Я практичный' → Toyota. Как твое решение укрепляет их self-image?"
            },
            "value_dump": {
                "pattern": r"(все\s+преимущества|полный\s+список|всё\s+включено)",
                "comment": "Илья К.: Не вываливай всю ценность сразу. Netflix: сначала 'смотри сериалы', потом 'без рекламы', потом 'эксклюзивы', потом 'скачай офлайн'."
            },
            "no_ttv": {
                "pattern": r"(сложная\s+настройка|долгая\s+установка|изучение\s+требует)",
                "comment": "Илья К.: Где ага-момент в первые 30 секунд? TikTok показывает видео сразу, Canva дает редактировать template мгновенно. 78% never return если активация >2 минут."
            },
            "no_anticipation": {
                "pattern": r"(получишь\s+результат|будет\s+доступно|ожидай)",
                "comment": "Илья К.: Как создаешь предвкушение результата? Spotify показывает 'Discover Weekly готов', GitHub - 'Your code is building'. Expectation > experience."
            },
            "generic_activation": {
                "pattern": r"(для\s+всех\s+одинаково|универсальный\s+опыт|стандартная\s+активация)",
                "comment": "Илья К.: B2C нужно развлечение за 10 сек, B2B - решение проблемы за 60 сек, Social - связь с людьми, Achievement - прогресс. Какой тип у твоего сегмента?"
            },
            "no_curiosity_gap": {
                "pattern": r"(всё\s+понятно|без\s+интриги|простая\s+информация)",
                "comment": "Илья К.: Где curiosity gap? LinkedIn показывает 'Кто смотрел профиль', Duolingo - 'Streak: 45 дней'. Создавай интригу для следующего действия."
            },
            "no_investment": {
                "pattern": r"(без\s+усилий|автоматически|готовое\s+решение)",
                "comment": "Илья К.: Как пользователь инвестирует в продукт? IKEA заставляет собирать, Instagram - настраивать профиль. Вложенность = привязанность."
            },
            "flat_activation": {
                "pattern": r"(ровный\s+опыт|без\s+пиков|стандартное\s+завершение)",
                "comment": "Илья К.: Где эмоциональный пик и как завершается первая сессия? Apple Store: touch iPhone → wow → купить. Disney: очередь → excitement → magical experience."
            },
            "no_scaffolding": {
                "pattern": r"(сразу\s+всё|без\s+обучения|полная\s+сложность)",
                "comment": "Илья К.: Как убираешь training wheels? Duolingo: подсказки → самостоятельность, Photoshop: guided → expert mode. Scaffolding исчезает с ростом skill."
            },
            "static_social_proof": {
                "pattern": r"(постоянные\s+отзывы|статичные\s+цифры|старые\s+кейсы)",
                "comment": "Илья К.: Где live social proof? 'Sarah from London just created project', '5 пользователей сейчас онлайн'. Booking.com: 'In high demand!' прямо сейчас."
            },
            "choice_overload": {
                "pattern": r"(много\s+вариантов|выбери\s+сам|различные\s+пути)",
                "comment": "Илья К.: Сколько решений требуешь сразу? Netflix автовыбирает что смотреть, Amazon - one-click купить. Выбор = paralysis, направление = action."
            },
            "predictable_experience": {
                "pattern": r"(ожидаемый\s+результат|стандартный\s+процесс|обычный\s+опыт)",
                "comment": "Илья К.: Где overdelivery vs expectations? Zappos отправляет за ночь вместо недели, Mailchimp показывает monkey animations. Surprised = remembered."
            },
            "cognitive_complexity": {
                "pattern": r"(сложные\s+шрифты|непонятные\s+термины|много\s+информации)",
                "comment": "Илья К.: Насколько легко обработать первое впечатление? Простые шрифты, знакомые паттерны, очевидные действия. Easy = valuable, hard = skip."
            },
            "no_activation_metrics": {
                "pattern": r"(не\s+измеряем|без\s+метрик|нет\s+отслеживания)",
                "comment": "Илья К.: Какие метрики отслеживаешь? Time to First Value <2 min, Session Depth >5 actions, Day 1 Retention >30%. Measure what matters for activation."
            }
        }
        
        self.document_type_specific = {
            "landing_review": {
                "required_sections": ["JTBD", "Value Proposition", "Social Proof", "Actionable Tasks"],
                "challenge_focus": ["user_centric", "segment_gaps", "missing_vision", "no_tasks"]
            },
            "analysis": {
                "required_sections": ["Data Analysis", "Insights", "Recommendations"],
                "challenge_focus": ["missing_insights", "no_tasks", "trust_issues"]
            },
            "recommendation": {
                "required_sections": ["Problem Statement", "Solution", "Implementation Plan"],
                "challenge_focus": ["no_tasks", "missing_vision", "trust_issues"]
            }
        }

    def analyze_document(self, content: str, doc_type: str = "landing_review") -> Dict[str, Any]:
        """
        Анализирует документ и определяет области для челленджа
        """
        result = {
            "document_type": doc_type,
            "total_words": len(content.split()),
            "challenge_areas": [],
            "quality_score": 10.0,
            "missing_elements": [],
            "suggestions": []
        }
        
        # Проверяем паттерны для челленджа
        for challenge_type, config in self.challenge_patterns.items():
            if doc_type in self.document_type_specific:
                if challenge_type in self.document_type_specific[doc_type]["challenge_focus"]:
                    if re.search(config["pattern"], content, re.IGNORECASE):
                        result["challenge_areas"].append({
                            "type": challenge_type,
                            "severity": "high",
                            "comment": config["comment"]
                        })
                        result["quality_score"] -= 1.5
        
        # Проверяем обязательные секции
        if doc_type in self.document_type_specific:
            required = self.document_type_specific[doc_type]["required_sections"]
            for section in required:
                if section.lower() not in content.lower():
                    result["missing_elements"].append(section)
                    result["quality_score"] -= 1.0
        
        return result

    def inject_challenges(self, content: str, analysis: Dict[str, Any]) -> str:
        """
        Вставляет комментарии-челленджи в документ
        """
        enhanced_content = content
        challenge_count = 0
        
        # Добавляем комментарии для каждой области челленджа
        for challenge in analysis["challenge_areas"]:
            challenge_count += 1
            challenge_marker = f"\n\n> **💭 {challenge['comment']}**\n"
            
            # Ищем подходящее место для вставки комментария
            sections = enhanced_content.split('\n## ')
            if len(sections) > challenge_count:
                sections[challenge_count] += challenge_marker
                enhanced_content = '\n## '.join(sections)
        
        # Добавляем общий блок с рекомендациями по улучшению
        if analysis["missing_elements"]:
            improvement_section = self._generate_improvement_section(analysis)
            enhanced_content += f"\n\n{improvement_section}"
        
        return enhanced_content

    def _generate_improvement_section(self, analysis: Dict[str, Any]) -> str:
        """
        Генерирует секцию с рекомендациями по улучшению
        """
        section = "---\n\n## 🎯 Илья К.: Рекомендации по улучшению\n\n"
        
        if analysis["missing_elements"]:
            section += "### Отсутствующие элементы:\n"
            for element in analysis["missing_elements"]:
                section += f"- **{element}**: Добавить обязательную секцию\n"
        
        section += f"\n### Текущая оценка качества: {analysis['quality_score']:.1f}/10\n"
        
        if analysis['quality_score'] < 8.0:
            section += "\n> **Илья К.: Документ требует доработки перед использованием. Учти все комментарии выше.**\n"
        elif analysis['quality_score'] < 9.0:
            section += "\n> **Илья К.: Хорошая работа, но есть точки роста. Внеси правки и будет отлично.**\n"
        else:
            section += "\n> **Илья К.: Отличный материал! Соответствует нашим стандартам качества.**\n"
        
        return section

    def challenge_specific_content(self, content: str, focus_areas: List[str]) -> Dict[str, Any]:
        """
        Применяет специфические челленджи к выбранным областям
        """
        challenges = []
        
        for area in focus_areas:
            if area in self.challenge_patterns:
                pattern_config = self.challenge_patterns[area]
                if re.search(pattern_config["pattern"], content, re.IGNORECASE):
                    challenges.append({
                        "area": area,
                        "comment": pattern_config["comment"],
                        "priority": "high"
                    })
        
        return {
            "focused_challenges": challenges,
            "recommendation": "Обрати внимание на выделенные области и внеси соответствующие правки."
        }

async def handle_ilya_review_challenge(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP handler для команды ilya-review-challenge
    """
    try:
        challenger = IlyaReviewChallenger()
        
        content = args.get("document_content", "")
        doc_type = args.get("document_type", "landing_review")
        focus_areas = args.get("focus_areas", [])
        
        if not content:
            return {
                "success": False,
                "error": "Требуется содержимое документа для анализа"
            }
        
        # Анализируем документ
        analysis = challenger.analyze_document(content, doc_type)
        
        # Применяем специфические челленджи если указаны
        if focus_areas:
            focused_result = challenger.challenge_specific_content(content, focus_areas)
            analysis["focused_challenges"] = focused_result["focused_challenges"]
        
        # Вставляем комментарии в документ
        enhanced_content = challenger.inject_challenges(content, analysis)
        
        return {
            "success": True,
            "original_content": content,
            "enhanced_content": enhanced_content,
            "analysis": analysis,
            "ilya_signature": f"Reviewed by Ilya Krasinsky on {datetime.now().strftime('%d %b %Y, %H:%M CET')}",
            "content": [{
                "type": "text",
                "text": f"# Документ с комментариями Ильи Красинского\n\n{enhanced_content}\n\n---\n*Качество: {analysis['quality_score']:.1f}/10*"
            }]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка при обработке челленджа: {str(e)}",
            "content": [{
                "type": "text", 
                "text": f"Ошибка: {str(e)}"
            }]
        }

if __name__ == "__main__":
    # Тестирование
    test_content = """
    # Анализ лендинга
    
    Наша компания предлагает лучшие решения для бизнеса.
    Мы являемся лидерами рынка с 10-летним опытом.
    
    ## Рекомендации
    Улучшить дизайн и добавить больше контента.
    """
    
    challenger = IlyaReviewChallenger()
    analysis = challenger.analyze_document(test_content, "landing_review")
    enhanced = challenger.inject_challenges(test_content, analysis)
    
    print("=== ORIGINAL ===")
    print(test_content)
    print("\n=== ENHANCED ===")
    print(enhanced)
    print(f"\nQuality Score: {analysis['quality_score']:.1f}/10")