#!/usr/bin/env python3
"""
TDD Development Workflow с рефлексией и XP принципами

JTBD: Как разработчик, я хочу использовать структурированный TDD workflow с атомарными функциями,
чтобы создавать качественный, тестируемый код следуя принципам XP.

Архитектура: 7 атомарных шагов с reflection checkpoints
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, '/home/runner/workspace')

def analyze_problem(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Шаг 1: Анализ проблемы через 5W+H framework
    
    JTBD: Как разработчик, я хочу структурированно проанализировать проблему,
    чтобы понять корневые причины и сформулировать четкие требования.
    """
    result = {
        "step": "analyze_problem",
        "success": False,
        "analysis": {},
        "reflection": {}
    }
    
    try:
        problem_text = input_data.get("problem_description", "")
        context = input_data.get("context", {})
        
        # 5W+H анализ
        analysis = {
            "what": extract_what_problem(problem_text),
            "who": extract_who_affected(problem_text, context),
            "when": extract_when_occurs(problem_text),
            "where": extract_where_happens(problem_text, context),
            "why": extract_why_important(problem_text),
            "how": extract_how_current_state(problem_text)
        }
        
        # Reflection checkpoint
        reflection = {
            "is_problem_clear": len(analysis["what"]) > 10,
            "has_user_context": bool(analysis["who"]) and analysis["who"] != "unknown",
            "measurable_impact": any(word in problem_text.lower() for word in ["время", "ошибк", "производительность", "метрик"]),
            "actionable": any(word in problem_text.lower() for word in ["улучшить", "исправить", "создать", "автоматизировать", "оптимизировать", "анализировать", "извлекать", "сократить", "повысить"])
        }
        
        result["analysis"] = analysis
        result["reflection"] = reflection
        result["success"] = all(reflection.values())
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def extract_what_problem(text: str) -> str:
    """Извлекает суть проблемы"""
    return text.split('.')[0] if text else ""

def extract_who_affected(text: str, context: Dict) -> str:
    """Определяет кого затрагивает проблема"""
    users = ["пользователь", "разработчик", "система", "команда"]
    for user in users:
        if user in text.lower():
            return user
    return context.get("target_user", "unknown")

def extract_when_occurs(text: str) -> str:
    """Определяет когда происходит проблема"""
    triggers = ["когда", "при", "во время", "после"]
    for trigger in triggers:
        if trigger in text.lower():
            parts = text.lower().split(trigger)
            if len(parts) > 1:
                return parts[1].split('.')[0].strip()
    return "неопределено"

def extract_where_happens(text: str, context: Dict) -> str:
    """Определяет где происходит проблема"""
    locations = ["интерфейс", "код", "система", "база данных", "API"]
    for location in locations:
        if location in text.lower():
            return location
    return context.get("component", "unknown")

def extract_why_important(text: str) -> str:
    """Определяет почему проблема важна"""
    if "чтобы" in text.lower():
        return text.lower().split("чтобы")[1].strip()
    # Ищем другие индикаторы важности
    impact_words = ["ошибкам", "снижению", "потерям", "проблемам"]
    for word in impact_words:
        if word in text.lower():
            return f"предотвратить {word}"
    return text.split(',')[-1].strip() if ',' in text else "повысить эффективность"

def extract_how_current_state(text: str) -> str:
    """Описывает текущее состояние"""
    if "сейчас" in text.lower() or "текущ" in text.lower():
        return "определено"
    # Ищем описание текущего состояния
    if "вручную" in text.lower():
        return "ручной процесс"
    if "много времени" in text.lower():
        return "неэффективный процесс"
    return "автоматизация требуется"

def generate_jtbd_scenarios(problem_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Шаг 2: Генерация JTBD сценариев с триггерами
    
    JTBD: Как архитектор, я хочу преобразовать анализ проблемы в JTBD сценарии,
    чтобы определить точные пользовательские потребности.
    """
    result = {
        "step": "generate_jtbd_scenarios",
        "success": False,
        "scenarios": [],
        "reflection": {}
    }
    
    try:
        analysis = problem_analysis.get("analysis", {})
        
        # Генерируем основной JTBD
        main_jtbd = {
            "type": "primary",
            "when": analysis.get("when", "неопределенная ситуация"),
            "i_want": extract_desired_action(analysis),
            "so_that": analysis.get("why", "достичь цели"),
            "trigger": analysis.get("what", "проблема"),
            "user": analysis.get("who", "пользователь")
        }
        
        # Генерируем вспомогательные JTBD
        supporting_jtbd = generate_supporting_scenarios(analysis)
        
        scenarios = [main_jtbd] + supporting_jtbd
        
        # Reflection checkpoint
        reflection = {
            "has_clear_trigger": bool(main_jtbd["when"]),
            "actionable_want": len(main_jtbd["i_want"]) > 5,
            "measurable_outcome": bool(main_jtbd["so_that"]),
            "multiple_scenarios": len(scenarios) > 1
        }
        
        result["scenarios"] = scenarios
        result["reflection"] = reflection
        result["success"] = all(reflection.values())
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def extract_desired_action(analysis: Dict) -> str:
    """Извлекает желаемое действие из анализа"""
    what = analysis.get("what", "")
    actions = ["создать", "улучшить", "исправить", "автоматизировать", "оптимизировать"]
    
    for action in actions:
        if action in what.lower():
            return f"{action} {what.split(action)[1].strip() if action in what.lower() else what}"
    
    return what

def generate_supporting_scenarios(analysis: Dict) -> List[Dict]:
    """Генерирует поддерживающие JTBD сценарии"""
    scenarios = []
    
    # Сценарий для разработчика
    scenarios.append({
        "type": "developer",
        "when": "разрабатываю решение",
        "i_want": "следовать TDD принципам",
        "so_that": "создать качественный код",
        "trigger": "начало разработки",
        "user": "разработчик"
    })
    
    # Сценарий для тестирования
    scenarios.append({
        "type": "testing",
        "when": "проверяю решение",
        "i_want": "убедиться в корректности",
        "so_that": "предотвратить ошибки",
        "trigger": "завершение разработки",
        "user": "тестировщик"
    })
    
    return scenarios

def formulate_hypothesis(jtbd_scenarios: List[Dict]) -> Dict[str, Any]:
    """
    Шаг 3: Формулирование гипотезы с измеримыми критериями
    
    JTBD: Как продакт-менеджер, я хочу сформулировать проверяемую гипотезу,
    чтобы определить критерии успеха решения.
    """
    result = {
        "step": "formulate_hypothesis",
        "success": False,
        "hypothesis": {},
        "reflection": {}
    }
    
    try:
        primary_scenario = next((s for s in jtbd_scenarios if s.get("type") == "primary"), {})
        
        hypothesis = {
            "statement": f"Если мы {primary_scenario.get('i_want', 'решим проблему')}, то {primary_scenario.get('user', 'пользователь')} {primary_scenario.get('so_that', 'получит результат')}",
            "measurable_criteria": generate_success_criteria(primary_scenario),
            "falsification_criteria": generate_failure_criteria(primary_scenario),
            "target_metrics": extract_target_metrics(primary_scenario),
            "time_frame": "2 недели разработки + 1 неделя тестирования"
        }
        
        # Reflection checkpoint
        reflection = {
            "has_measurable_criteria": len(hypothesis["measurable_criteria"]) >= 3,
            "has_falsification": len(hypothesis["falsification_criteria"]) >= 2,
            "specific_metrics": len(hypothesis["target_metrics"]) > 0,
            "testable_statement": "если" in hypothesis["statement"].lower() and "то" in hypothesis["statement"].lower()
        }
        
        result["hypothesis"] = hypothesis
        result["reflection"] = reflection
        result["success"] = all(reflection.values())
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def generate_success_criteria(scenario: Dict) -> List[str]:
    """Генерирует критерии успеха"""
    return [
        "Все тесты проходят успешно",
        "Код соответствует стандартам качества",
        "Функциональность работает согласно JTBD",
        "Производительность соответствует требованиям"
    ]

def generate_failure_criteria(scenario: Dict) -> List[str]:
    """Генерирует критерии провала"""
    return [
        "Тесты не проходят более 24 часов",
        "Код не соответствует принципам XP",
        "Функциональность не решает исходную проблему"
    ]

def extract_target_metrics(scenario: Dict) -> Dict[str, str]:
    """Извлекает целевые метрики"""
    return {
        "test_coverage": ">80%",
        "code_quality": "A grade",
        "performance": "<2s response time",
        "user_satisfaction": ">90%"
    }

def tdd_development_workflow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Основной TDD workflow с рефлексией
    
    JTBD: Как команда разработки, мы хотим использовать структурированный TDD подход,
    чтобы создавать качественное ПО с минимальными дефектами.
    """
    workflow_id = f"tdd_workflow_{int(time.time())}"
    start_time = time.time()
    
    result = {
        "workflow_id": workflow_id,
        "success": False,
        "steps_completed": [],
        "final_reflection": {},
        "execution_time": 0
    }
    
    try:
        print(f"🔄 Запуск TDD Development Workflow: {workflow_id}")
        
        # Шаг 1: Анализ проблемы
        print("📋 STEP 1: Анализ проблемы")
        step1_result = analyze_problem(input_data)
        result["steps_completed"].append(step1_result)
        
        if not step1_result["success"]:
            result["error"] = "Шаг 1 failed: недостаточно данных для анализа проблемы"
            return result
        
        print("✅ STEP 1: Проблема проанализирована")
        
        # Шаг 2: Генерация JTBD
        print("🎯 STEP 2: Генерация JTBD сценариев")
        step2_result = generate_jtbd_scenarios(step1_result)
        result["steps_completed"].append(step2_result)
        
        if not step2_result["success"]:
            result["error"] = "Шаг 2 failed: не удалось сгенерировать качественные JTBD"
            return result
            
        print("✅ STEP 2: JTBD сценарии созданы")
        
        # Шаг 3: Формулирование гипотезы
        print("🧪 STEP 3: Формулирование гипотезы")
        step3_result = formulate_hypothesis(step2_result["scenarios"])
        result["steps_completed"].append(step3_result)
        
        if not step3_result["success"]:
            result["error"] = "Шаг 3 failed: гипотеза не соответствует критериям качества"
            return result
            
        print("✅ STEP 3: Гипотеза сформулирована")
        
        # Финальная рефлексия workflow
        final_reflection = {
            "all_steps_successful": all(step["success"] for step in result["steps_completed"]),
            "reflection_checkpoints_passed": sum(len(step.get("reflection", {})) for step in result["steps_completed"]),
            "ready_for_implementation": step3_result["success"],
            "quality_score": calculate_quality_score(result["steps_completed"])
        }
        
        result["final_reflection"] = final_reflection
        result["success"] = final_reflection["all_steps_successful"]
        result["execution_time"] = round((time.time() - start_time) * 1000, 2)
        
        print(f"🏁 TDD Workflow завершен. Качество: {final_reflection['quality_score']:.2f}")
        
    except Exception as e:
        result["error"] = f"Workflow error: {str(e)}"
        result["execution_time"] = round((time.time() - start_time) * 1000, 2)
    
    return result

def calculate_quality_score(steps: List[Dict]) -> float:
    """Вычисляет общий балл качества workflow"""
    if not steps:
        return 0.0
    
    scores = []
    for step in steps:
        reflection = step.get("reflection", {})
        if reflection:
            passed = sum(1 for check in reflection.values() if check)
            total = len(reflection)
            scores.append(passed / total if total > 0 else 0)
    
    return sum(scores) / len(scores) if scores else 0.0

if __name__ == "__main__":
    # Тестовый запуск
    test_input = {
        "problem_description": "Пользователи тратят много времени на валидацию данных вручную, что приводит к ошибкам и снижению производительности команды",
        "context": {
            "target_user": "разработчик",
            "component": "система валидации",
            "current_metrics": {"error_rate": "15%", "time_spent": "2 часа/день"}
        }
    }
    
    result = tdd_development_workflow(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))