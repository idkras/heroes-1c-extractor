#!/usr/bin/env python3
"""
MCP Reflection Guard - Система принудительного сомнения
Обязательная проверка перед любыми заявлениями о результатах
"""

import json
import sys
from typing import Dict, List, Any
from pathlib import Path

class ReflectionGuard:
    """Система принудительной рефлексии для предотвращения ложных заявлений"""
    
    def __init__(self):
        self.critical_triggers = [
            "153%", "превышает", "результат", "успешно", "работает",
            "выполнено", "готово", "исправлено", "загружено"
        ]
        
        # Триггеры нарушения MCP процессов
        self.process_violation_triggers = [
            "создал новый файл", "создание файла", "str_replace_based_edit_tool",
            "новый стандарт", "новый инцидент", "напрямую создал"
        ]
        
    def mandatory_reflection(self, claim: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обязательная рефлексия перед заявлением о результатах
        
        JTBD: Когда AI Assistant хочет заявить о результате,
        система должна принудительно проверить реальность утверждения
        """
        
        reflection_questions = [
            "Проверил ли я данные из первоисточника?",
            "Сравнил ли реальность с моими утверждениями?", 
            "Учел ли качество данных, а не только количество?",
            "Нашел ли проблемы в логах?",
            "Что я могу НЕ УЧИТЫВАТЬ в этом утверждении?"
        ]
        
        # Проверяем на подозрительные триггеры
        triggers_found = [t for t in self.critical_triggers if t.lower() in claim.lower()]
        
        # Проверяем на нарушения MCP процессов
        process_violations = [t for t in self.process_violation_triggers if t.lower() in claim.lower()]
        
        response = {
            "claim": claim,
            "triggers_found": triggers_found,
            "process_violations": process_violations,
            "requires_verification": len(triggers_found) > 0 or len(process_violations) > 0,
            "reflection_questions": reflection_questions,
            "verification_required": True if (triggers_found or process_violations) else False
        }
        
        if triggers_found or process_violations:
            warning_msg = ""
            if triggers_found:
                warning_msg += f"СТОП! Обнаружены триггеры: {triggers_found}. Обязательная проверка данных."
            if process_violations:
                warning_msg += f" НАРУШЕНИЕ ПРОЦЕССА: {process_violations}. Используйте MCP команды."
            
            response["warning"] = warning_msg
            response["mandatory_checks"] = self._generate_verification_steps(claim, context)
            
            if process_violations:
                response["mcp_process_check"] = [
                    "Проверить доступные MCP команды для этой задачи",
                    "Использовать create_incident вместо прямого создания файлов",
                    "Использовать update_standard вместо создания новых файлов",
                    "Применить reflection_guard к выбору инструментов"
                ]
            
        return response
    
    def _generate_verification_steps(self, claim: str, context: Dict[str, Any]) -> List[str]:
        """Генерирует обязательные шаги проверки для конкретного утверждения"""
        
        steps = [
            "Проверить первоисточник данных (не логи/кеш)",
            "Сравнить заявленные vs реальные цифры", 
            "Проанализировать качество данных",
            "Найти counter-evidence (что опровергает утверждение)",
            "Проверить все WARNING и ERROR в логах"
        ]
        
        # Специфичные проверки для определенных утверждений
        if "%" in claim:
            steps.append("Проверить математические вычисления")
            steps.append("Убедиться что знаменатель и числитель из одного источника")
            
        if "загружено" in claim.lower():
            steps.append("Проверить содержимое загруженных данных")
            steps.append("Убедиться что загружены правильные файлы")
            
        if "работает" in claim.lower():
            steps.append("Протестировать функциональность с реальными данными")
            steps.append("Проверить на edge cases")
            
        return steps
    
    def verify_claim_against_reality(self, claim: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Сверяет утверждение с реальными данными"""
        
        verification = {
            "claim": claim,
            "evidence_provided": bool(evidence),
            "verification_status": "pending"
        }
        
        if not evidence:
            verification["verification_status"] = "failed"
            verification["reason"] = "Нет доказательств для проверки утверждения"
            return verification
            
        # Проверяем численные утверждения
        if "%" in claim or any(char.isdigit() for char in claim):
            verification["math_check"] = self._verify_numbers(claim, evidence)
            
        # Проверяем утверждения о функциональности
        if any(word in claim.lower() for word in ["работает", "исправлено", "готово"]):
            verification["functionality_check"] = self._verify_functionality(claim, evidence)
            
        return verification
    
    def _verify_numbers(self, claim: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка численных утверждений"""
        return {
            "status": "requires_manual_verification",
            "note": "Численные утверждения требуют проверки первоисточников"
        }
    
    def _verify_functionality(self, claim: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка утверждений о функциональности"""
        return {
            "status": "requires_testing", 
            "note": "Утверждения о работоспособности требуют тестирования"
        }

def main():
    """CLI интерфейс для проверки утверждений"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python reflection_guard.py '<claim_to_verify>'"
        }))
        return 1
        
    claim = sys.argv[1]
    guard = ReflectionGuard()
    
    # Обязательная рефлексия
    reflection = guard.mandatory_reflection(claim)
    
    print(json.dumps(reflection, indent=2, ensure_ascii=False))
    
    # Если требуется проверка - возвращаем код ошибки
    return 1 if reflection["verification_required"] else 0

if __name__ == "__main__":
    sys.exit(main())