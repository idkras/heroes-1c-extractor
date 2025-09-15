#!/usr/bin/env python3
"""
TDD Testing Pyramid Validator

JTBD: Я (валидатор) хочу проверить соблюдение Testing Pyramid в TDD,
чтобы предотвратить "Unit Tunnel Vision" anti-pattern.

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any

# Добавляем пути к модулям
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

def analyze_testing_pyramid(project_path: str) -> Dict[str, Any]:
    """
    JTBD: Я (анализатор) хочу проанализировать Testing Pyramid проекта,
    чтобы выявить недостающие типы тестов.
    """
    results = {
        "pyramid_compliance": False,
        "missing_test_types": [],
        "recommendations": [],
        "test_distribution": {},
        "anti_patterns_detected": []
    }
    
    project_root = Path(str(project_path))
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        results["missing_test_types"] = ["unit", "integration", "e2e", "contract", "acceptance"]
        results["anti_patterns_detected"].append("No tests directory found")
        return results
    
    # Анализируем существующие типы тестов
    test_types_found = {
        "unit": False,
        "integration": False,
        "e2e": False,
        "contract": False,
        "acceptance": False
    }
    
    test_counts = {
        "unit": 0,
        "integration": 0,
        "e2e": 0,
        "contract": 0,
        "acceptance": 0
    }
    
    # Сканируем директории тестов
    for test_type in test_types_found.keys():
        type_dir = tests_dir / test_type
        if type_dir.exists():
            test_types_found[test_type] = True
            # Подсчитываем файлы тестов
            test_files = list(type_dir.glob("test_*.py")) + list(type_dir.glob("*_test.py"))
            test_counts[test_type] = len(test_files)
    
    # Проверяем на Unit Tunnel Vision
    if test_types_found["unit"] and not any([
        test_types_found["integration"],
        test_types_found["e2e"]
    ]):
        results["anti_patterns_detected"].append("Unit Tunnel Vision: только unit тесты без integration/e2e")
    
    # Проверяем на Green Tests, Broken System
    if test_counts["unit"] > 0 and test_counts["integration"] == 0:
        results["anti_patterns_detected"].append("Green Tests, Broken System: unit тесты без integration тестов")
    
    # Определяем недостающие типы
    for test_type, found in test_types_found.items():
        if not found:
            results["missing_test_types"].append(test_type)
    
    # Формируем рекомендации
    if "integration" in results["missing_test_types"]:
        results["recommendations"].append(
            "КРИТИЧНО: Создать integration тесты для проверки взаимодействия компонентов"
        )
    
    if "e2e" in results["missing_test_types"]:
        results["recommendations"].append(
            "ВАЖНО: Создать e2e тесты для проверки полного пользовательского workflow"
        )
    
    if test_counts["unit"] > test_counts["integration"] * 3:
        results["recommendations"].append(
            "ВНИМАНИЕ: Слишком много unit тестов относительно integration тестов"
        )
    
    # Проверяем соблюдение пирамиды
    required_types = ["unit", "integration"]
    results["pyramid_compliance"] = all(test_types_found[t] for t in required_types)
    
    results["test_distribution"] = test_counts
    
    return results

def generate_tdd_compliance_report(analysis: Dict[str, Any]) -> str:
    """
    JTBD: Я (генератор) хочу создать отчет о соблюдении TDD Testing Pyramid,
    чтобы дать четкие рекомендации разработчику.
    """
    report = []
    
    # Заголовок
    report.append("🔍 TDD Testing Pyramid Analysis Report")
    report.append("=" * 45)
    
    # Статус соблюдения
    if analysis["pyramid_compliance"]:
        report.append("✅ Testing Pyramid: СОБЛЮДАЕТСЯ")
    else:
        report.append("❌ Testing Pyramid: НАРУШАЕТСЯ")
    
    report.append("")
    
    # Распределение тестов
    report.append("📊 Test Distribution:")
    for test_type, count in analysis["test_distribution"].items():
        status = "✅" if count > 0 else "❌"
        report.append(f"  {status} {test_type.capitalize()}: {count} тестов")
    
    report.append("")
    
    # Anti-patterns
    if analysis["anti_patterns_detected"]:
        report.append("⚠️  DETECTED ANTI-PATTERNS:")
        for pattern in analysis["anti_patterns_detected"]:
            report.append(f"  🚨 {pattern}")
        report.append("")
    
    # Недостающие типы тестов
    if analysis["missing_test_types"]:
        report.append("❌ MISSING TEST TYPES:")
        for missing_type in analysis["missing_test_types"]:
            report.append(f"  📝 {missing_type.capitalize()} tests")
        report.append("")
    
    # Рекомендации
    if analysis["recommendations"]:
        report.append("💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            report.append(f"  {i}. {rec}")
        report.append("")
    
    # Итоговая оценка
    if analysis["pyramid_compliance"] and not analysis["anti_patterns_detected"]:
        report.append("🎯 RESULT: TDD Testing Pyramid соблюдается корректно!")
    else:
        report.append("🔥 RESULT: Требуется доработка Testing Pyramid!")
    
    return "\n".join(report)

def main():
    """Основная функция валидатора Testing Pyramid."""
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python tdd_pyramid_validator.py <json_args>")
        
        args = json.loads(sys.argv[1])
        project_path = args.get("project_path", ".")
        
        # Выполняем анализ
        analysis = analyze_testing_pyramid(project_path)
        
        # Генерируем отчет
        report = generate_tdd_compliance_report(analysis)
        
        # Формируем результат
        result = {
            "success": True,
            "pyramid_compliance": analysis["pyramid_compliance"],
            "analysis": analysis,
            "report": report,
            "action_required": len(analysis["missing_test_types"]) > 0 or len(analysis["anti_patterns_detected"]) > 0
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"TDD Pyramid validation failed: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()