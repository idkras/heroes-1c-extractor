#!/usr/bin/env python3
"""
Updated Hypothesis Verification Workflow
Обновленный воркфлоу проверки гипотез согласно улучшенному процессу
"""

import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class WorkflowStep(Enum):
    IDENTIFY_PROBLEM = "identify_problem"
    BUILD_JTBD_SCENARIO = "build_jtbd_scenario" 
    FIND_DESIGN_INJECTION_POINT = "find_design_injection_point"
    FORM_HYPOTHESIS = "form_hypothesis"
    CHALLENGE_HYPOTHESIS = "challenge_hypothesis"
    RISK_ASSUMPTION_TESTS = "risk_assumption_tests"
    RED_PHASE_TESTS = "red_phase_tests"
    IMPLEMENT_SOLUTION = "implement_solution"
    RUN_TESTS = "run_tests"
    EVALUATE_OUTCOME = "evaluate_outcome"
    FALSIFY_OR_CONFIRM = "falsify_or_confirm"

@dataclass
class HypothesisWorkflowResult:
    step: WorkflowStep
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: float
    success: bool
    errors: List[str] = None

class UpdatedHypothesisWorkflow:
    """Обновленный воркфлоу работы с гипотезами"""
    
    def __init__(self):
        self.results = []
        
    def identify_problem(self, user_idea: str, context: str = "") -> HypothesisWorkflowResult:
        """
        Шаг 1: Выявление проблемы из идеи/заметки/задачи
        
        JTBD: Когда у меня есть идея или задача,
        я хочу четко сформулировать проблему которую решаю,
        чтобы фокусироваться на реальной пользовательской боли
        """
        start_time = time.time()
        
        # Анализируем идею и извлекаем проблему
        problem_analysis = {
            "source_idea": user_idea,
            "identified_problems": [],
            "root_cause_analysis": "",
            "user_pain_points": [],
            "business_impact": ""
        }
        
        # Простой анализ ключевых слов для выявления проблем
        problem_indicators = ["медленно", "сложно", "не работает", "ошибка", "проблема", "трудно"]
        pain_points = [indicator for indicator in problem_indicators if indicator in user_idea.lower()]
        
        if pain_points:
            problem_analysis["identified_problems"] = [
                f"Обнаружена проблема связанная с: {', '.join(pain_points)}"
            ]
            problem_analysis["user_pain_points"] = pain_points
        else:
            # Если явных проблем не найдено, формулируем предположения
            problem_analysis["identified_problems"] = [
                "Требуется анализ для выявления скрытых проблем пользователей"
            ]
            
        duration = (time.time() - start_time) * 1000
        
        return HypothesisWorkflowResult(
            step=WorkflowStep.IDENTIFY_PROBLEM,
            input_data={"user_idea": user_idea, "context": context},
            output_data=problem_analysis,
            duration_ms=duration,
            success=True
        )
    
    def build_jtbd_scenario(self, problem_data: Dict[str, Any]) -> HypothesisWorkflowResult:
        """
        Шаг 2: Создание JTBD-сценария с триггером
        
        Формат: Когда [ситуация-триггер] у [роли] происходит [проблема],
        он видит [что видит], понимает [что понимает], хочет [что хочет], делает [что делает]
        """
        start_time = time.time()
        
        jtbd_scenario = {
            "trigger_situation": "Когда пользователь сталкивается с проблемой",
            "user_role": "Пользователь системы", 
            "problem_context": problem_data.get("identified_problems", ["Неопределенная проблема"])[0],
            "what_user_sees": "Препятствия в достижении цели",
            "what_user_understands": "Текущий процесс неэффективен",
            "what_user_wants": "Быстрое и простое решение",
            "what_user_does": "Ищет альтернативы или обходные пути",
            "nine_component_structure": {
                "when": "Когда возникает проблема",
                "role": "Пользователь",
                "wants": "Решить проблему",
                "need": "Эффективность",
                "we_show": "Решение",
                "understands": "Ценность решения", 
                "does": "Принимает решение",
                "we_want": "Удовлетворенность пользователя",
                "we_do": "Предоставляем поддержку"
            }
        }
        
        duration = (time.time() - start_time) * 1000
        
        return HypothesisWorkflowResult(
            step=WorkflowStep.BUILD_JTBD_SCENARIO,
            input_data=problem_data,
            output_data=jtbd_scenario,
            duration_ms=duration,
            success=True
        )
        
    def find_design_injection_point(self, jtbd_data: Dict[str, Any]) -> HypothesisWorkflowResult:
        """
        Шаг 3: Определение точки дизайн-инъекции в Customer Journey Map
        
        Где именно в пользовательском пути мы будем вмешиваться
        """
        start_time = time.time()
        
        # Анализируем JTBD для определения точки вмешательства
        injection_analysis = {
            "cjm_stage": "consideration",  # awareness, consideration, decision, usage, advocacy
            "intervention_point": "В момент когда пользователь понимает проблему",
            "intervention_type": "process_improvement",  # ui_change, process_improvement, new_feature
            "impact_level": "medium",  # low, medium, high
            "touchpoints_affected": ["user_interface", "workflow"],
            "intervention_rationale": "Оптимальная точка для вмешательства с максимальным эффектом"
        }
        
        duration = (time.time() - start_time) * 1000
        
        return HypothesisWorkflowResult(
            step=WorkflowStep.FIND_DESIGN_INJECTION_POINT,
            input_data=jtbd_data,
            output_data=injection_analysis,
            duration_ms=duration,
            success=True
        )
    
    def form_hypothesis_updated_format(self, jtbd_data: Dict[str, Any], injection_data: Dict[str, Any]) -> HypothesisWorkflowResult:
        """
        Шаг 4: Формирование гипотезы в обновленном формате
        
        Формат: Когда [ситуация-триггер] происходит [проблема],
        если мы изменим [CJM сценарий в точке дизайн-инъекции],
        то пользователь увидит [output] и мы получим [outcome с метриками]
        """
        start_time = time.time()
        
        hypothesis = {
            "trigger_situation": jtbd_data.get("trigger_situation", ""),
            "problem_occurs": jtbd_data.get("problem_context", ""),
            "cjm_change": f"изменим {injection_data.get('intervention_point', '')}",
            "user_will_see": "улучшенный пользовательский опыт",
            "business_outcome": {
                "qualitative_metrics": [
                    "Улучшение пользовательского опыта",
                    "Снижение фрустрации пользователей"
                ],
                "quantitative_metrics": [
                    "Время выполнения задачи: -30%",
                    "Удовлетворенность пользователей: +25%"
                ]
            },
            "full_hypothesis": self._format_hypothesis(jtbd_data, injection_data),
            "hypothesis_type": "improvement",  # new_feature, improvement, optimization
            "confidence_level": "medium"  # low, medium, high
        }
        
        duration = (time.time() - start_time) * 1000
        
        return HypothesisWorkflowResult(
            step=WorkflowStep.FORM_HYPOTHESIS,
            input_data={"jtbd": jtbd_data, "injection": injection_data},
            output_data=hypothesis,
            duration_ms=duration,
            success=True
        )
    
    def _format_hypothesis(self, jtbd_data: Dict[str, Any], injection_data: Dict[str, Any]) -> str:
        """Форматирует гипотезу в стандартном виде"""
        return f"""
Когда: {jtbd_data.get('trigger_situation', '')}
Происходит проблема: {jtbd_data.get('problem_context', '')}

Если мы изменим CJM сценарий в точке: {injection_data.get('intervention_point', '')}

То пользователь увидит: улучшенный опыт взаимодействия
И мы получим outcome: повышение ключевых метрик пользовательского опыта
        """.strip()
    
    def challenge_hypothesis(self, hypothesis_data: Dict[str, Any]) -> HypothesisWorkflowResult:
        """
        Шаг 5: Челлендж гипотезы на когнитивные искажения
        
        Проверяем гипотезу на предвзятости и слабые места
        """
        start_time = time.time()
        
        challenge_analysis = {
            "cognitive_biases_check": {
                "confirmation_bias": "Ищем ли мы только подтверждающие доказательства?",
                "overconfidence_bias": "Не переоцениваем ли вероятность успеха?",
                "planning_fallacy": "Учли ли сложность реализации?",
                "survivorship_bias": "Рассмотрели ли неуспешные примеры?"
            },
            "assumption_challenges": [
                "Что если пользователи не заметят изменение?",
                "Что если решение создаст новые проблемы?",
                "Что если конкуренты уже решили эту проблему?"
            ],
            "alternative_explanations": [
                "Возможно проблема не в том, что мы думаем",
                "Возможно есть более простое решение"
            ],
            "risk_factors": [
                "Технические ограничения",
                "Пользовательское сопротивление изменениям",
                "Ресурсные ограничения"
            ]
        }
        
        duration = (time.time() - start_time) * 1000
        
        return HypothesisWorkflowResult(
            step=WorkflowStep.CHALLENGE_HYPOTHESIS,
            input_data=hypothesis_data,
            output_data=challenge_analysis,
            duration_ms=duration,
            success=True
        )
    
    def risk_assumption_tests(self, hypothesis_data: Dict[str, Any], challenge_data: Dict[str, Any]) -> HypothesisWorkflowResult:
        """
        Шаг 6: Risk Assumption Tests (RAT)
        
        Создает тесты для проверки рискованных допущений
        """
        start_time = time.time()
        
        rat_tests = {
            "critical_assumptions": [
                "Пользователи хотят решить эту проблему",
                "Предложенное решение технически реализуемо",
                "Изменение не нарушит существующий workflow"
            ],
            "risk_tests": [
                {
                    "assumption": "Пользователи поймут новый интерфейс",
                    "test_method": "Прототипирование и пользовательские тесты",
                    "success_criteria": "80% пользователей успешно выполняют задачу",
                    "timeline": "1-2 недели"
                },
                {
                    "assumption": "Техническое решение работает стабильно", 
                    "test_method": "MVP с ограниченной функциональностью",
                    "success_criteria": "Uptime > 99%",
                    "timeline": "2-3 недели"
                }
            ],
            "validation_sequence": [
                "1. Проверить пользовательское понимание",
                "2. Протестировать техническую реализуемость", 
                "3. Измерить влияние на ключевые метрики"
            ]
        }
        
        duration = (time.time() - start_time) * 1000
        
        return HypothesisWorkflowResult(
            step=WorkflowStep.RISK_ASSUMPTION_TESTS,
            input_data={"hypothesis": hypothesis_data, "challenge": challenge_data},
            output_data=rat_tests,
            duration_ms=duration,
            success=True
        )
    
    def run_full_workflow(self, user_idea: str, context: str = "") -> List[HypothesisWorkflowResult]:
        """Запускает полный обновленный воркфлоу проверки гипотез"""
        
        # Шаг 1: Проблема
        problem_result = self.identify_problem(user_idea, context)
        self.results.append(problem_result)
        
        # Шаг 2: JTBD сценарий
        jtbd_result = self.build_jtbd_scenario(problem_result.output_data)
        self.results.append(jtbd_result)
        
        # Шаг 3: Точка дизайн-инъекции
        injection_result = self.find_design_injection_point(jtbd_result.output_data)
        self.results.append(injection_result)
        
        # Шаг 4: Гипотеза
        hypothesis_result = self.form_hypothesis_updated_format(
            jtbd_result.output_data, 
            injection_result.output_data
        )
        self.results.append(hypothesis_result)
        
        # Шаг 5: Челлендж
        challenge_result = self.challenge_hypothesis(hypothesis_result.output_data)
        self.results.append(challenge_result)
        
        # Шаг 6: RAT тесты
        rat_result = self.risk_assumption_tests(
            hypothesis_result.output_data,
            challenge_result.output_data
        )
        self.results.append(rat_result)
        
        return self.results

def main():
    """Демонстрация обновленного воркфлоу"""
    
    workflow = UpdatedHypothesisWorkflow()
    
    # Тестовая идея
    test_idea = "Система кеширования стандартов работает медленно и загружает неправильные файлы"
    
    print("🧪 ОБНОВЛЕННЫЙ WORKFLOW ПРОВЕРКИ ГИПОТЕЗ")
    print("=" * 50)
    
    results = workflow.run_full_workflow(test_idea)
    
    for i, result in enumerate(results, 1):
        print(f"\n📋 Шаг {i}: {result.step.value.replace('_', ' ').title()}")
        print(f"⏱️  Время: {result.duration_ms:.1f}ms")
        print(f"✅ Успех: {result.success}")
        
        if result.step == WorkflowStep.FORM_HYPOTHESIS:
            print(f"📝 Гипотеза: {result.output_data.get('full_hypothesis', '')}")
            
        if result.step == WorkflowStep.RISK_ASSUMPTION_TESTS:
            print("🧪 RAT тесты:")
            for test in result.output_data.get('risk_tests', []):
                print(f"  - {test.get('assumption', '')}")

if __name__ == "__main__":
    main()