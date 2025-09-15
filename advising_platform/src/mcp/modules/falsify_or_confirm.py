"""
MCP Module: Falsify or Confirm Hypothesis
Ядро фальсификации гипотез для MCP Hypothesis Cycle v1.0

Принимает результаты тестов и сравнивает с исходной гипотезой,
принимая решение о фальсификации или подтверждении.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Импорт существующих систем
try:
    from advising_platform.src.standards_system import UnifiedStandardsSystem
except ImportError:
    UnifiedStandardsSystem = None


class HypothesisFalsificationEngine:
    """
    Движок фальсификации гипотез на основе результатов тестирования
    
    Реализует принципы фальсифицируемости из PRD:
    - Сравнение фактических метрик с ожидаемыми
    - Принятие решения о подтверждении/фальсификации
    - Генерация отчета с обоснованием
    """
    
    def __init__(self):
        """Инициализация движка фальсификации"""
        self.standards_system = None
        if UnifiedStandardsSystem:
            try:
                self.standards_system = UnifiedStandardsSystem()
            except Exception as e:
                print(f"⚠️ Стандарты недоступны: {e}")
        
        self.decision_threshold = 0.7  # Порог для подтверждения гипотезы
        self.operation_start_time = time.time()
    
    def evaluate_hypothesis(self, hypothesis_path: str, test_results_path: str) -> Dict[str, Any]:
        """
        Основная функция оценки гипотезы против результатов тестов
        
        Args:
            hypothesis_path: Путь к файлу hypothesis.json
            test_results_path: Путь к файлу test_results.json
            
        Returns:
            Словарь с результатом оценки и решением
        """
        try:
            # Загружаем гипотезу
            hypothesis = self._load_hypothesis(hypothesis_path)
            if not hypothesis:
                return self._create_error_result("Не удалось загрузить гипотезу")
            
            # Загружаем результаты тестов
            test_results = self._load_test_results(test_results_path)
            if not test_results:
                return self._create_error_result("Не удалось загрузить результаты тестов")
            
            # Сравниваем метрики
            comparison = self._compare_metrics(hypothesis, test_results)
            
            # Принимаем решение
            decision = self._make_decision(comparison)
            
            # Генерируем финальный отчет
            report = self._generate_evaluation_report(hypothesis, test_results, comparison, decision)
            
            return report
            
        except Exception as e:
            return self._create_error_result(f"Ошибка оценки гипотезы: {e}")
    
    def _load_hypothesis(self, path: str) -> Optional[Dict[str, Any]]:
        """Загружает гипотезу из JSON файла"""
        try:
            hypothesis_file = Path(path)
            if not hypothesis_file.exists():
                print(f"⚠️ Файл гипотезы не найден: {path}")
                return None
            
            with open(hypothesis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки гипотезы: {e}")
            return None
    
    def _load_test_results(self, path: str) -> Optional[Dict[str, Any]]:
        """Загружает результаты тестов из JSON файла"""
        try:
            results_file = Path(path)
            if not results_file.exists():
                print(f"⚠️ Файл результатов не найден: {path}")
                return None
            
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки результатов: {e}")
            return None
    
    def _compare_metrics(self, hypothesis: Dict[str, Any], test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Сравнивает ожидаемые метрики гипотезы с фактическими результатами
        """
        comparison = {
            "metrics_comparison": {},
            "overall_score": 0.0,
            "met_expectations": 0,
            "total_expectations": 0
        }
        
        # Получаем ожидаемые метрики из гипотезы
        expected_metrics = hypothesis.get("metrics", {})
        actual_metrics = test_results.get("metrics", {})
        
        total_score = 0
        metric_count = 0
        
        for metric_name, expected_value in expected_metrics.items():
            actual_value = actual_metrics.get(metric_name)
            
            if actual_value is not None:
                # Вычисляем соответствие метрики
                metric_result = self._evaluate_single_metric(
                    metric_name, expected_value, actual_value
                )
                
                comparison["metrics_comparison"][metric_name] = metric_result
                total_score += metric_result["score"]
                metric_count += 1
                
                if metric_result["meets_expectation"]:
                    comparison["met_expectations"] += 1
                
                comparison["total_expectations"] += 1
        
        # Вычисляем общий балл
        if metric_count > 0:
            comparison["overall_score"] = total_score / metric_count
        
        return comparison
    
    def _evaluate_single_metric(self, name: str, expected: Any, actual: Any) -> Dict[str, Any]:
        """Оценивает одну метрику"""
        try:
            # Для численных метрик
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                # Вычисляем отклонение
                if expected == 0:
                    score = 1.0 if actual == 0 else 0.0
                else:
                    deviation = abs(actual - expected) / abs(expected)
                    score = max(0, 1 - deviation)
                
                meets_expectation = score >= self.decision_threshold
                
                return {
                    "expected": expected,
                    "actual": actual,
                    "score": score,
                    "deviation_percent": deviation * 100 if expected != 0 else 0,
                    "meets_expectation": meets_expectation,
                    "type": "numeric"
                }
            
            # Для строковых/boolean метрик
            else:
                matches = expected == actual
                return {
                    "expected": expected,
                    "actual": actual,
                    "score": 1.0 if matches else 0.0,
                    "meets_expectation": matches,
                    "type": "categorical"
                }
                
        except Exception as e:
            return {
                "expected": expected,
                "actual": actual,
                "score": 0.0,
                "meets_expectation": False,
                "error": str(e),
                "type": "error"
            }
    
    def _make_decision(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Принимает финальное решение о гипотезе"""
        overall_score = comparison["overall_score"]
        met_expectations = comparison["met_expectations"]
        total_expectations = comparison["total_expectations"]
        
        # Логика принятия решения
        if overall_score >= self.decision_threshold:
            if total_expectations > 0 and (met_expectations / total_expectations) >= 0.5:
                decision = "CONFIRMED"
                confidence = overall_score
            else:
                decision = "PARTIALLY_CONFIRMED"
                confidence = overall_score * 0.8
        else:
            decision = "FALSIFIED"
            confidence = 1 - overall_score
        
        return {
            "decision": decision,
            "confidence": confidence,
            "overall_score": overall_score,
            "success_rate": met_expectations / total_expectations if total_expectations > 0 else 0,
            "reasoning": self._generate_decision_reasoning(decision, overall_score, met_expectations, total_expectations)
        }
    
    def _generate_decision_reasoning(self, decision: str, score: float, met: int, total: int) -> str:
        """Генерирует обоснование решения"""
        if decision == "CONFIRMED":
            return f"Гипотеза подтверждена: общий балл {score:.1%}, выполнено {met}/{total} ожиданий"
        elif decision == "PARTIALLY_CONFIRMED":
            return f"Гипотеза частично подтверждена: балл {score:.1%}, но не все ожидания выполнены ({met}/{total})"
        else:
            return f"Гипотеза фальсифицирована: балл {score:.1%} ниже порога {self.decision_threshold:.1%}"
    
    def _generate_evaluation_report(self, hypothesis: Dict[str, Any], test_results: Dict[str, Any], 
                                   comparison: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует полный отчет об оценке"""
        evaluation_time = time.time() - self.operation_start_time
        
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "evaluation_duration_ms": round(evaluation_time * 1000, 2),
            "hypothesis": {
                "title": hypothesis.get("title", "Untitled Hypothesis"),
                "description": hypothesis.get("description", ""),
                "expected_outcome": hypothesis.get("outcome", ""),
                "metrics": hypothesis.get("metrics", {})
            },
            "test_results_summary": {
                "total_tests": test_results.get("total_tests", 0),
                "passed_tests": test_results.get("passed_tests", 0),
                "failed_tests": test_results.get("failed_tests", 0),
                "execution_time": test_results.get("execution_time", 0)
            },
            "metrics_analysis": comparison["metrics_comparison"],
            "overall_evaluation": {
                "score": comparison["overall_score"],
                "met_expectations": comparison["met_expectations"],
                "total_expectations": comparison["total_expectations"],
                "success_rate": comparison["met_expectations"] / comparison["total_expectations"] if comparison["total_expectations"] > 0 else 0
            },
            "final_decision": decision,
            "next_steps": self._suggest_next_steps(decision["decision"])
        }
    
    def _suggest_next_steps(self, decision: str) -> List[str]:
        """Предлагает следующие шаги на основе решения"""
        if decision == "CONFIRMED":
            return [
                "Зафиксировать успешную гипотезу в документации",
                "Применить найденный подход к похожим задачам",
                "Создать новую более амбициозную гипотезу"
            ]
        elif decision == "PARTIALLY_CONFIRMED":
            return [
                "Проанализировать несоответствующие метрики",
                "Уточнить гипотезу с учетом полученных данных",
                "Повторить тесты с скорректированными ожиданиями"
            ]
        else:  # FALSIFIED
            return [
                "Провести root cause analysis (5 почему)",
                "Сформулировать новую гипотезу на основе полученных данных",
                "Документировать причины провала для избежания повторения"
            ]
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Создает результат с ошибкой"""
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "status": "ERROR",
            "error": error_message,
            "final_decision": {
                "decision": "ERROR",
                "confidence": 0.0,
                "reasoning": f"Не удалось выполнить оценку: {error_message}"
            }
        }


def mcp_falsify_or_confirm(hypothesis_file: str, test_results_file: str) -> Dict[str, Any]:
    """
    MCP команда для фальсификации или подтверждения гипотезы
    
    Args:
        hypothesis_file: Путь к файлу с гипотезой
        test_results_file: Путь к файлу с результатами тестов
        
    Returns:
        Результат оценки гипотезы
    """
    engine = HypothesisFalsificationEngine()
    return engine.evaluate_hypothesis(hypothesis_file, test_results_file)


if __name__ == "__main__":
    # Тестовый запуск с демонстрационными данными
    print("🧪 Демонстрация фальсификации гипотезы")
    
    # Создаем тестовую гипотезу
    test_hypothesis = {
        "title": "MCP сервер улучшит воспроизводимость AI-процессов",
        "description": "Если реализовать MCP-сервер, то missed_steps_count снизится",
        "outcome": "Повышение воспроизводимости в 3+ командах",
        "metrics": {
            "missed_steps_count": 2,  # Ожидаем не более 2 пропусков
            "workflow_completion_rate": 0.9,  # Ожидаем 90% завершений
            "incident_resolution_time": 30  # Ожидаем 30 минут
        }
    }
    
    # Симулируем результаты тестов
    test_results = {
        "total_tests": 10,
        "passed_tests": 7,
        "failed_tests": 3,
        "execution_time": 45,
        "metrics": {
            "missed_steps_count": 5,  # Фактически больше ожидаемого
            "workflow_completion_rate": 0.7,  # Ниже ожиданий
            "incident_resolution_time": 45  # Выше ожиданий
        }
    }
    
    # Сохраняем для тестирования
    Path("test_hypothesis.json").write_text(json.dumps(test_hypothesis, indent=2, ensure_ascii=False))
    Path("test_results.json").write_text(json.dumps(test_results, indent=2, ensure_ascii=False))
    
    # Выполняем фальсификацию
    result = mcp_falsify_or_confirm("test_hypothesis.json", "test_results.json")
    
    print(f"\n🎯 Результат: {result['final_decision']['decision']}")
    print(f"📊 Балл: {result['overall_evaluation']['score']:.1%}")
    print(f"💭 Обоснование: {result['final_decision']['reasoning']}")
    print(f"\n📋 Следующие шаги:")
    for step in result['next_steps']:
        print(f"  • {step}")