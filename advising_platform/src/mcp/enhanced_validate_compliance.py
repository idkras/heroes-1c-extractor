#!/usr/bin/env python3
"""
Enhanced Validate Compliance с Protocol Completion
Автономная реализация для задачи T034
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def enhanced_validate_compliance(request):
    """Валидация соответствия стандартам с Protocol Completion."""
    
    start_time = datetime.now()
    
    try:
        standard = request.get("standard", "")
        content = request.get("content", "")
        context = request.get("context", "")
        
        print(f"🔌 MCP ОПЕРАЦИЯ НАЧАТА: validate-compliance")
        print(f"📥 Параметры: standard={standard}, content_length={len(content)}")
        
        # Базовая валидация
        if not standard or not content:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                "success": False,
                "error": "Требуются параметры standard и content",
                "compliance_score": 0
            }
            
            print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
            print(f"⏰ Время выполнения: {duration:.1f}мс")
            print(f"📤 Результат: Недостаточно параметров")
            
            return result
        
        # Выполняем валидацию соответствия
        compliance_checks = perform_compliance_checks(standard, content)
        compliance_score = calculate_compliance_score(compliance_checks)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": True,
            "standard": standard,
            "compliance_score": compliance_score,
            "checks_passed": len([c for c in compliance_checks if c["passed"]]),
            "total_checks": len(compliance_checks),
            "compliance_checks": compliance_checks,
            "processing_time_ms": duration
        }
        
        # Protocol Completion: отчет об успехе
        print(f"✅ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"📊 Соответствие стандарту: {compliance_score:.1f}%")
        print(f"✅ Пройдено проверок: {result['checks_passed']}/{result['total_checks']}")
        print(f"🎯 Валидация стандарта '{standard}' завершена")
        
        # Предлагаем следующие шаги
        suggest_compliance_actions(compliance_score, standard)
        
        return result
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": False,
            "error": str(e),
            "compliance_score": 0,
            "message": "Ошибка при валидации соответствия"
        }
        
        print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"🚨 Ошибка: {str(e)}")
        
        return result

def perform_compliance_checks(standard: str, content: str) -> list:
    """Выполняет проверки соответствия стандарту."""
    
    checks = []
    
    # Базовые проверки
    checks.append({
        "name": "Минимальная длина контента",
        "description": "Контент должен содержать достаточно информации",
        "passed": len(content) >= 100,
        "details": f"Длина контента: {len(content)} символов"
    })
    
    checks.append({
        "name": "Структурированность",
        "description": "Контент должен содержать заголовки или разделы",
        "passed": any(marker in content for marker in ['#', '**', '##', '###']),
        "details": "Найдены элементы структуры" if any(marker in content for marker in ['#', '**', '##', '###']) else "Структура не найдена"
    })
    
    # Специфические проверки для разных стандартов
    if "task" in standard.lower():
        checks.append({
            "name": "Задача содержит цель",
            "description": "В задаче должна быть указана цель или результат",
            "passed": any(word in content.lower() for word in ['цель', 'результат', 'outcome', 'output']),
            "details": "Найдены маркеры цели"
        })
        
    elif "process" in standard.lower():
        checks.append({
            "name": "Процесс содержит шаги",
            "description": "Процесс должен содержать последовательность действий",
            "passed": any(marker in content for marker in ['1.', '2.', '- [', 'шаг']),
            "details": "Найдены элементы процесса"
        })
    
    return checks

def calculate_compliance_score(checks: list) -> float:
    """Вычисляет общий балл соответствия."""
    if not checks:
        return 0.0
    
    passed_checks = len([check for check in checks if check["passed"]])
    return (passed_checks / len(checks)) * 100

def suggest_compliance_actions(score: float, standard: str):
    """Предлагает действия на основе результатов валидации."""
    
    print(f"\n🎯 РЕКОМЕНДАЦИИ ПО СООТВЕТСТВИЮ:")
    
    if score >= 80:
        print("✅ Высокий уровень соответствия!")
        print("• Можно переходить к реализации")
        print("• Рассмотреть дополнительную оптимизацию")
    elif score >= 60:
        print("⚠️ Средний уровень соответствия")
        print("• Устранить выявленные несоответствия")
        print("• Добавить недостающие элементы структуры")
    else:
        print("🚨 Низкий уровень соответствия")
        print("• Требуется значительная доработка")
        print("• Изучить стандарт более детально")
        print("• Создать инцидент для анализа проблем")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        request_data = json.loads(sys.argv[1])
        result = enhanced_validate_compliance(request_data)
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ ВАЛИДАЦИИ:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Enhanced Validate Compliance с Protocol Completion")
        print("Использование: python enhanced_validate_compliance.py '{\"standard\": \"task_master\", \"content\": \"содержимое для проверки\"}'")