#!/usr/bin/env python3
"""
Compliance Checker Backend

JTBD: Я (validator) хочу проверить соответствие контента стандартам,
чтобы обеспечить качество создаваемых материалов и выявить нарушения.

Интеграция с стандартами для автоматической валидации контента.

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any

# Добавляем путь к модулям advising_platform
current_dir = Path(__file__).parent.resolve()
advising_platform_dir = current_dir.parent.parent
sys.path.insert(0, str(advising_platform_dir))

# Динамический импорт для лучшей совместимости
try:
    from advising_platform.src.core.unified_key_resolver import get_resolver
    from advising_platform.src.cache.real_inmemory_cache import get_cache
except ImportError:
    # Direct import
    project_root = current_dir.parent.parent.parent
    sys.path.insert(0, str(project_root))
    try:
        from advising_platform.src.core.unified_key_resolver import get_resolver
        from advising_platform.src.cache.real_inmemory_cache import get_cache
    except ImportError:
        # Fallback for testing
        def get_resolver():
            return None
        def get_cache():
            return None

def main(args):
    """Main function for MCP integration"""
    try:
        checker = ComplianceChecker()
        content = args.get('content', '')
        standards = args.get('standards', [])
        
        if not content:
            return {
                "success": True,
                "result": "ComplianceChecker initialized successfully",
                "message": "No content provided for validation"
            }
        
        result = checker.validate_compliance(content, standards)
        return {
            "success": True,
            "result": result,
            "message": "Compliance check completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error in compliance check"
        }

class ComplianceChecker:
    """
    JTBD: Я (класс) хочу проверять соответствие контента стандартам,
    чтобы обеспечить качество создаваемых материалов и автоматически выявлять нарушения.
    """
    
    def __init__(self):
        self.resolver = get_resolver()
        self.cache = get_cache()
        
        # Инициализируем кеш если не загружен
        if len(self.cache.get_all_paths()) == 0:
            self.cache.initialize_from_disk()
            
        # Правила валидации по умолчанию
        self.default_rules = {
            "jtbd_format": {
                "description": "Проверка корректности JTBD формата",
                "patterns": [
                    r"когда.*роль.*хочет.*чтобы",
                    r"я \([^)]+\).*хочу.*чтобы",
                    r"when.*as.*want.*so that"
                ],
                "severity": "medium"
            },
            "tdd_structure": {
                "description": "Проверка структуры TDD документации",
                "required_elements": ["RED", "GREEN", "REFACTOR", "гипотеза"],
                "severity": "high"
            },
            "documentation_completeness": {
                "description": "Проверка полноты документации",
                "required_sections": ["цель", "описание", "автор", "дата"],
                "severity": "medium"
            },
            "standard_references": {
                "description": "Проверка корректности ссылок на стандарты",
                "patterns": [r"abstract://standard:[a-z_]+", r"стандарт.*v\d+\.\d+"],
                "severity": "low"
            }
        }
    
    def validate_compliance(self, content: str, standards_to_check: List[str] = None, strict_mode: bool = False) -> Dict[str, Any]:
        """
        JTBD: Я (метод) хочу проверить соответствие контента стандартам,
        чтобы вернуть детальный отчет о нарушениях и предложения по исправлению.
        """
        try:
            violations = []
            warnings = []
            suggestions = []
            
            # 1. Применяем базовые правила
            base_violations = self._check_basic_rules(content, strict_mode)
            violations.extend(base_violations)
            
            # 2. Проверяем против конкретных стандартов
            if standards_to_check:
                standard_violations = self._check_against_standards(content, standards_to_check, strict_mode)
                violations.extend(standard_violations)
            else:
                # Автоматически определяем релевантные стандарты
                auto_standards = self._auto_detect_relevant_standards(content)
                if auto_standards:
                    standard_violations = self._check_against_standards(content, auto_standards, strict_mode)
                    violations.extend(standard_violations)
            
            # 3. Генерируем предложения по улучшению
            suggestions = self._generate_suggestions(content, violations)
            
            # 4. Вычисляем общий score соответствия
            compliance_score = self._calculate_compliance_score(violations)
            
            return {
                "success": True,
                "compliance_score": compliance_score,
                "status": self._get_compliance_status(compliance_score),
                "violations": violations,
                "warnings": warnings,
                "suggestions": suggestions,
                "checked_standards": standards_to_check or auto_standards or [],
                "strict_mode": strict_mode,
                "summary": {
                    "total_violations": len(violations),
                    "critical_violations": len([v for v in violations if v["severity"] == "critical"]),
                    "high_violations": len([v for v in violations if v["severity"] == "high"]),
                    "medium_violations": len([v for v in violations if v["severity"] == "medium"]),
                    "low_violations": len([v for v in violations if v["severity"] == "low"])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Compliance check failed: {str(e)}",
                "content_length": len(content)
            }
    
    def _check_basic_rules(self, content: str, strict_mode: bool) -> List[Dict[str, Any]]:
        """Проверяет базовые правила качества контента."""
        violations = []
        content_lower = content.lower()
        
        for rule_name, rule_config in self.default_rules.items():
            rule_violations = []
            
            if rule_name == "jtbd_format":
                # Проверяем JTBD формат
                if "jtbd" in content_lower or "job-to-be-done" in content_lower:
                    has_valid_jtbd = False
                    for pattern in rule_config["patterns"]:
                        if re.search(pattern, content_lower, re.IGNORECASE):
                            has_valid_jtbd = True
                            break
                    
                    if not has_valid_jtbd:
                        rule_violations.append({
                            "rule": rule_name,
                            "description": rule_config["description"],
                            "message": "JTBD не соответствует стандартному формату",
                            "severity": rule_config["severity"],
                            "location": "document",
                            "suggestion": "Используйте формат: 'Когда [ситуация], Роль [кто], Хочет [что], Чтобы [результат]'"
                        })
            
            elif rule_name == "tdd_structure":
                # Проверяем TDD структуру
                if "tdd" in content_lower or "test" in content_lower:
                    missing_elements = []
                    for element in rule_config["required_elements"]:
                        if element.lower() not in content_lower:
                            missing_elements.append(element)
                    
                    if missing_elements:
                        rule_violations.append({
                            "rule": rule_name,
                            "description": rule_config["description"],
                            "message": f"Отсутствуют обязательные элементы TDD: {', '.join(missing_elements)}",
                            "severity": rule_config["severity"],
                            "location": "structure",
                            "suggestion": f"Добавьте секции: {', '.join(missing_elements)}"
                        })
            
            elif rule_name == "documentation_completeness":
                # Проверяем полноту документации
                missing_sections = []
                for section in rule_config["required_sections"]:
                    if section.lower() not in content_lower:
                        missing_sections.append(section)
                
                if missing_sections and (strict_mode or len(missing_sections) > 2):
                    rule_violations.append({
                        "rule": rule_name,
                        "description": rule_config["description"],
                        "message": f"Отсутствуют разделы документации: {', '.join(missing_sections)}",
                        "severity": rule_config["severity"],
                        "location": "metadata",
                        "suggestion": f"Добавьте разделы: {', '.join(missing_sections)}"
                    })
            
            elif rule_name == "standard_references":
                # Проверяем ссылки на стандарты
                invalid_refs = []
                for pattern in rule_config["patterns"]:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match.startswith("abstract://standard:"):
                            # Проверяем существование стандарта
                            canonical = self.resolver.resolve_to_canonical(match)
                            if canonical == match:  # Не найден
                                invalid_refs.append(match)
                
                if invalid_refs:
                    rule_violations.append({
                        "rule": rule_name,
                        "description": rule_config["description"],
                        "message": f"Найдены несуществующие ссылки на стандарты: {', '.join(invalid_refs)}",
                        "severity": rule_config["severity"],
                        "location": "references",
                        "suggestion": "Проверьте корректность адресов стандартов"
                    })
            
            violations.extend(rule_violations)
        
        return violations
    
    def _check_against_standards(self, content: str, standards: List[str], strict_mode: bool) -> List[Dict[str, Any]]:
        """Проверяет соответствие конкретным стандартам."""
        violations = []
        
        for standard_address in standards:
            # Получаем содержимое стандарта
            canonical_path = self.resolver.resolve_to_canonical(standard_address)
            cache_entry = self.cache.get_document(canonical_path)
            
            if not cache_entry:
                continue
            
            standard_content = cache_entry.content
            standard_violations = self._extract_violations_from_standard(content, standard_content, standard_address, strict_mode)
            violations.extend(standard_violations)
        
        return violations
    
    def _extract_violations_from_standard(self, content: str, standard_content: str, standard_address: str, strict_mode: bool) -> List[Dict[str, Any]]:
        """Извлекает правила валидации из стандарта и проверяет соответствие."""
        violations = []
        content_lower = content.lower()
        standard_lower = standard_content.lower()
        
        # Извлекаем требования из стандарта
        requirements = self._extract_requirements_from_standard(standard_content)
        
        for requirement in requirements:
            req_lower = requirement.lower()
            
            # Проверяем наличие обязательных элементов
            if any(word in req_lower for word in ["должен", "обязательно", "необходимо", "must", "required"]):
                # Извлекаем ключевые термины из требования
                key_terms = self._extract_key_terms(requirement)
                missing_terms = [term for term in key_terms if term.lower() not in content_lower]
                
                if missing_terms:
                    violations.append({
                        "rule": "standard_requirement",
                        "standard": standard_address,
                        "description": f"Требование стандарта не выполнено",
                        "message": f"Отсутствуют обязательные элементы: {', '.join(missing_terms)}",
                        "requirement": requirement,
                        "severity": "high" if strict_mode else "medium",
                        "location": "content",
                        "suggestion": f"Добавьте: {', '.join(missing_terms)}"
                    })
        
        # Проверяем структурные требования
        if "структура" in standard_lower or "structure" in standard_lower:
            structure_violations = self._check_structure_compliance(content, standard_content, standard_address)
            violations.extend(structure_violations)
        
        return violations
    
    def _extract_requirements_from_standard(self, standard_content: str) -> List[str]:
        """Извлекает требования из текста стандарта."""
        requirements = []
        lines = standard_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(marker in line.lower() for marker in [
                "требование", "должен", "обязательно", "необходимо",
                "requirement", "must", "shall", "required"
            ]):
                if len(line) > 20:  # Фильтруем слишком короткие
                    requirements.append(line)
        
        return requirements
    
    def _extract_key_terms(self, requirement: str) -> List[str]:
        """Извлекает ключевые термины из требования."""
        # Простое извлечение терминов в кавычках или заглавными буквами
        terms = []
        
        # Термины в кавычках
        quoted_terms = re.findall(r'"([^"]+)"', requirement)
        terms.extend(quoted_terms)
        
        # Термины в одинарных кавычках  
        single_quoted = re.findall(r"'([^']+)'", requirement)
        terms.extend(single_quoted)
        
        # Заглавные слова (возможные термины)
        caps_terms = re.findall(r'\b[A-ZА-Я]{2,}\b', requirement)
        terms.extend(caps_terms)
        
        return [term for term in terms if len(term) > 2]
    
    def _check_structure_compliance(self, content: str, standard_content: str, standard_address: str) -> List[Dict[str, Any]]:
        """Проверяет соответствие структурным требованиям."""
        violations = []
        
        # Проверяем наличие заголовков
        content_headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        if len(content_headers) < 2:
            violations.append({
                "rule": "structure_headers",
                "standard": standard_address,
                "description": "Недостаточная структуризация документа",
                "message": "Документ должен содержать больше заголовков для структуризации",
                "severity": "medium",
                "location": "structure",
                "suggestion": "Добавьте заголовки для разделения контента на логические секции"
            })
        
        return violations
    
    def _auto_detect_relevant_standards(self, content: str) -> List[str]:
        """Автоматически определяет релевантные стандарты для проверки."""
        content_lower = content.lower()
        relevant_standards = []
        
        # Сопоставляем ключевые слова с типами стандартов
        standard_keywords = {
            "abstract://standard:tdd": ["tdd", "test", "тест", "тестирование", "red", "green", "refactor"],
            "abstract://standard:jtbd": ["jtbd", "job-to-be-done", "роль", "хочет", "чтобы"],
            "abstract://standard:registry": ["стандарт", "standard", "методология", "процесс"],
            "abstract://standard:context": ["контекст", "context", "задача", "task"],
            "abstract://standard:naming": ["именование", "naming", "название", "имя"]
        }
        
        for standard_addr, keywords in standard_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                # Проверяем что стандарт существует
                canonical = self.resolver.resolve_to_canonical(standard_addr)
                if canonical != standard_addr:
                    relevant_standards.append(standard_addr)
        
        return relevant_standards[:5]  # Максимум 5 стандартов
    
    def _generate_suggestions(self, content: str, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Генерирует предложения по улучшению на основе нарушений."""
        suggestions = []
        
        # Группируем нарушения по типам
        violation_groups = {}
        for violation in violations:
            rule = violation["rule"]
            if rule not in violation_groups:
                violation_groups[rule] = []
            violation_groups[rule].append(violation)
        
        # Генерируем предложения для каждой группы
        for rule, rule_violations in violation_groups.items():
            if rule == "jtbd_format":
                suggestions.append({
                    "type": "improvement",
                    "priority": "high",
                    "description": "Улучшение JTBD формата",
                    "action": "Переформулируйте JTBD в стандартном формате",
                    "example": "Когда [ситуация], Роль [кто], Хочет [что], Чтобы [результат]"
                })
            elif rule == "tdd_structure":
                suggestions.append({
                    "type": "structure",
                    "priority": "high", 
                    "description": "Добавление TDD структуры",
                    "action": "Добавьте RED-GREEN-REFACTOR секции",
                    "example": "## RED: Failing Test\n## GREEN: Implementation\n## REFACTOR: Optimization"
                })
            elif rule == "documentation_completeness":
                suggestions.append({
                    "type": "documentation",
                    "priority": "medium",
                    "description": "Дополнение документации",
                    "action": "Добавьте недостающие метаданные",
                    "example": "Автор, дата создания, версия, цель документа"
                })
        
        return suggestions
    
    def _calculate_compliance_score(self, violations: List[Dict[str, Any]]) -> float:
        """Вычисляет общий score соответствия стандартам."""
        if not violations:
            return 1.0
        
        # Взвешиваем нарушения по серьезности
        severity_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        
        total_penalty = 0.0
        for violation in violations:
            severity = violation.get("severity", "medium")
            penalty = severity_weights.get(severity, 0.5)
            total_penalty += penalty
        
        # Нормализуем score от 0 до 1
        max_penalty = len(violations) * 1.0  # Если все critical
        normalized_penalty = min(total_penalty / max_penalty if max_penalty > 0 else 0, 1.0)
        
        return max(0.0, 1.0 - normalized_penalty)
    
    def _get_compliance_status(self, score: float) -> str:
        """Определяет статус соответствия на основе score."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "acceptable"
        elif score >= 0.3:
            return "poor"
        else:
            return "critical"


def main():
    """Основная функция для вызова из MCP сервера."""
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python compliance_checker.py <json_args>")
        
        args = json.loads(sys.argv[1])
        
        checker = ComplianceChecker()
        result = checker.validate_compliance(
            content=args.get("content"),
            standards_to_check=args.get("standardsToCheck"),
            strict_mode=args.get("strictMode", False)
        )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Script execution failed: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()