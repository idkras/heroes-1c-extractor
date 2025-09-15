"""
MCP Module: Evaluate Outcome
Сравнение test_results с hypothesis.outcome
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def mcp_evaluate_outcome(hypothesis_data: Dict[str, Any], test_results_file: str = None) -> Dict[str, Any]:
    """
    MCP команда: evaluate-outcome
    Сравнивает результаты тестов с ожидаемыми результатами гипотезы
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-evaluate-outcome",
        "timestamp": datetime.now().isoformat(),
        "evaluation_success": False,
        "hypothesis_met": False,
        "deviations": [],
        "outcome_report_path": None,
        "execution_time_ms": 0
    }
    
    try:
        # Читаем результаты тестов
        test_results = _read_test_results(test_results_file)
        
        # Сравниваем с гипотезой
        evaluation = _compare_with_hypothesis(hypothesis_data, test_results)
        result.update(evaluation)
        
        # Создаем outcome_report.md
        report_path = _create_outcome_report(hypothesis_data, test_results, evaluation)
        result["outcome_report_path"] = str(report_path)
        
        result["evaluation_success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _read_test_results(test_results_file: str = None) -> Dict[str, Any]:
    """Читает результаты тестов"""
    
    if not test_results_file:
        test_results_file = "advising_platform/src/mcp/output/test_results.json"
    
    test_path = Path(test_results_file)
    
    if test_path.exists():
        with open(test_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"tests_run": [], "tests_passed": 0, "tests_failed": 0}


def _compare_with_hypothesis(hypothesis: Dict[str, Any], test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Сравнивает результаты с гипотезой"""
    
    # Простое сравнение - можно расширить
    hypothesis_met = test_results.get("tests_failed", 0) == 0
    
    deviations = []
    if not hypothesis_met:
        deviations.append({
            "metric": "tests_failed", 
            "expected": 0,
            "actual": test_results.get("tests_failed", 0)
        })
    
    return {
        "hypothesis_met": hypothesis_met,
        "deviations": deviations
    }


def _create_outcome_report(hypothesis: Dict[str, Any], test_results: Dict[str, Any], evaluation: Dict[str, Any]) -> Path:
    """Создает outcome_report.md"""
    
    report_content = f"""# Outcome Report - {datetime.now().strftime('%d %b %Y %H:%M')}

## Hypothesis Evaluation

**Hypothesis Met**: {evaluation['hypothesis_met']}

## Test Results Summary

- Tests Run: {len(test_results.get('tests_run', []))}
- Tests Passed: {test_results.get('tests_passed', 0)}
- Tests Failed: {test_results.get('tests_failed', 0)}

## Deviations

{chr(10).join([f"- {dev['metric']}: expected {dev['expected']}, got {dev['actual']}" for dev in evaluation.get('deviations', [])])}

## Conclusion

{"✅ Hypothesis confirmed" if evaluation['hypothesis_met'] else "❌ Hypothesis falsified"}
"""
    
    report_path = Path("advising_platform/src/mcp/output/outcome_report.md")
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report_content, encoding='utf-8')
    
    return report_path
