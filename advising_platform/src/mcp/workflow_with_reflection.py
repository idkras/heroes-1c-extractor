#!/usr/bin/env python3
"""
Hypothesis Workflow with Reflection Guard on Every Step
Воркфлоу с обязательной рефлексией на каждом этапе
"""

import json
import time
from typing import Dict, Any, List
from pathlib import Path
import subprocess

class ReflectionWorkflow:
    """Воркфлоу с принудительной рефлексией на каждом шаге"""
    
    def __init__(self):
        self.reflection_guard_path = "src/mcp/reflection_guard.py"
        
    def reflection_checkpoint(self, step_name: str, output_claim: str, step_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обязательная рефлексия на каждом шаге: а не брак ли я делаю?
        """
        print(f"\n🛑 REFLECTION CHECKPOINT: {step_name}")
        print("=" * 50)
        
        # Запускаем reflection_guard для проверки утверждения
        try:
            result = subprocess.run([
                "python", self.reflection_guard_path, output_claim
            ], capture_output=True, text=True, cwd=".")
            
            if result.returncode == 1:  # Требуется проверка
                reflection_data = json.loads(result.stdout)
                print(f"⚠️  ВНИМАНИЕ: {reflection_data.get('warning', '')}")
                print("\n🤔 ОБЯЗАТЕЛЬНЫЕ ВОПРОСЫ ДЛЯ РЕФЛЕКСИИ:")
                for i, question in enumerate(reflection_data.get('reflection_questions', []), 1):
                    print(f"   {i}. {question}")
                
                print(f"\n📋 ОБЯЗАТЕЛЬНЫЕ ПРОВЕРКИ:")
                for i, check in enumerate(reflection_data.get('mandatory_checks', []), 1):
                    print(f"   {i}. {check}")
                
                return {
                    "reflection_required": True,
                    "warning": reflection_data.get('warning'),
                    "checks": reflection_data.get('mandatory_checks', []),
                    "step_approved": False
                }
            else:
                print("✅ Рефлексия: утверждение не требует дополнительной проверки")
                return {
                    "reflection_required": False,
                    "step_approved": True
                }
                
        except Exception as e:
            print(f"❌ Ошибка рефлексии: {e}")
            return {
                "reflection_required": True,
                "error": str(e),
                "step_approved": False
            }
    
    def step_with_reflection(self, step_name: str, step_function, *args, **kwargs):
        """Выполняет шаг с обязательной рефлексией"""
        
        # Выполняем шаг
        result = step_function(*args, **kwargs)
        
        # Формируем утверждение о результате шага
        claim = f"{step_name} выполнен успешно: {self._extract_claim(result)}"
        
        # Обязательная рефлексия
        reflection = self.reflection_checkpoint(step_name, claim, result)
        
        # Добавляем рефлексию к результату
        result["reflection"] = reflection
        
        if not reflection["step_approved"]:
            print(f"🚫 Шаг {step_name} не прошел рефлексию - требуется переделать")
            result["requires_rework"] = True
        
        return result
    
    def _extract_claim(self, result: Dict[str, Any]) -> str:
        """Извлекает ключевое утверждение из результата шага"""
        if "success" in result:
            return f"результат достигнут с success={result['success']}"
        if "count" in result:
            return f"найдено {result['count']} элементов"
        if "output_data" in result:
            return "данные сгенерированы корректно"
        return "шаг завершен"

def complete_workflow_with_reflection():
    """Полный воркфлоу с рефлексией на каждом шаге"""
    
    workflow = ReflectionWorkflow()
    
    print("🧪 HYPOTHESIS VERIFICATION WORKFLOW С РЕФЛЕКСИЕЙ")
    print("=" * 60)
    
    # Пример прохождения воркфлоу с рефлексией
    steps = [
        ("problem identification", "Выявлена проблема системы кеширования"),
        ("jtbd scenario", "Создан JTBD сценарий с 9 компонентами"), 
        ("design injection point", "Определена точка вмешательства в CJM"),
        ("hypothesis formation", "Сформулирована гипотеза с outcome метриками"),
        ("challenge hypothesis", "Проведена проверка когнитивных искажений"),
        ("risk assumption tests", "Созданы RAT тесты для критических допущений"),
        ("red phase tests", "Написаны провальные тесты"),
        ("implement feature", "Реализовано решение"),
        ("run tests", "Выполнены тесты с результатом 95% успеха"),
        ("evaluate outcome", "Гипотеза подтверждена на 153%"),
        ("falsify or confirm", "Принято решение подтвердить гипотезу")
    ]
    
    results = []
    
    for step_name, claim in steps:
        print(f"\n📋 Шаг: {step_name}")
        
        # Имитируем выполнение шага
        step_result = {
            "step": step_name,
            "claim": claim,
            "success": True,
            "timestamp": time.time()
        }
        
        # Рефлексия на каждом шаге
        reflection = workflow.reflection_checkpoint(step_name, claim, step_result)
        step_result["reflection"] = reflection
        
        results.append(step_result)
        
        # Если рефлексия не прошла - останавливаемся
        if not reflection.get("step_approved", False):
            print(f"🛑 ВОРКФЛОУ ОСТАНОВЛЕН на шаге {step_name}")
            print("Требуется исправить проблемы перед продолжением")
            break
    
    print(f"\n📊 ИТОГИ ВОРКФЛОУ:")
    approved_steps = sum(1 for r in results if r["reflection"].get("step_approved", False))
    print(f"Одобрено шагов: {approved_steps}/{len(results)}")
    
    return results

if __name__ == "__main__":
    complete_workflow_with_reflection()