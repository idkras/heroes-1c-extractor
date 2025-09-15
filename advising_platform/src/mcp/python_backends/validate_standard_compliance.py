#!/usr/bin/env python3
"""
MCP Backend: validate_standard_compliance

JTBD: Я хочу проверять соответствие всех секций стандарта требованиям Registry и Task Master,
чтобы гарантировать качество и полноту каждого стандарта после обновления.
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def validate_standard_compliance(request):
    """Проверяет все секции стандарта на соответствие Registry и Task Master требованиям."""
    
    try:
        from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation
    except ImportError:
        log_mcp_operation = lambda *args, **kwargs: None
    
    start_time = datetime.now()
    
    try:
        standard_path = request.get("standard_path", "")
        check_type = request.get("check_type", "full")  # full, registry_only, task_master_only
        
        if not standard_path:
            return {
                "success": False,
                "error": "Требуется standard_path",
                "command": "validate_standard_compliance"
            }
        
        # Читаем стандарт для проверки
        full_path = Path(f"/home/runner/workspace/{standard_path}")
        if not full_path.exists():
            return {
                "success": False,
                "error": f"Стандарт не найден: {standard_path}",
                "command": "validate_standard_compliance"
            }
        
        with open(full_path, 'r', encoding='utf-8') as f:
            standard_content = f.read()
        
        # Читаем требования Registry и Task Master стандартов
        registry_requirements = load_registry_requirements()
        task_master_requirements = load_task_master_requirements()
        
        # Выполняем проверку секций
        validation_results = {
            "standard_path": standard_path,
            "registry_compliance": {},
            "task_master_compliance": {},
            "overall_score": 0,
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if check_type in ["full", "registry_only"]:
            validation_results["registry_compliance"] = check_registry_compliance(
                standard_content, registry_requirements
            )
        
        if check_type in ["full", "task_master_only"]:
            validation_results["task_master_compliance"] = check_task_master_compliance(
                standard_content, task_master_requirements
            )
        
        # Вычисляем общий балл соответствия
        validation_results["overall_score"] = calculate_overall_score(validation_results)
        
        # Генерируем рекомендации по улучшению
        validation_results["recommendations"] = generate_recommendations(validation_results)
        
        # Определяем успешность проверки
        success = validation_results["overall_score"] >= 0.8  # 80% соответствие
        
        result = {
            "success": success,
            "compliance_score": validation_results["overall_score"],
            "validation_results": validation_results,
            "command": "validate_standard_compliance"
        }
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        log_mcp_operation("validate_standard_compliance", start_time, result, duration_ms)
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "command": "validate_standard_compliance",
            "timestamp": datetime.now().isoformat()
        }
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        log_mcp_operation("validate_standard_compliance", start_time, error_result, duration_ms)
        return error_result

def load_registry_requirements():
    """Загружает требования из Registry Standard."""
    registry_path = Path("/home/runner/workspace/[standards .md]/0. core standards/0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md")
    
    if not registry_path.exists():
        return {"sections": [], "format_rules": [], "metadata_rules": []}
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "sections": extract_required_sections_from_registry(content),
            "format_rules": extract_format_rules(content),
            "metadata_rules": extract_metadata_rules(content),
            "naming_conventions": extract_naming_conventions(content)
        }
    except Exception:
        return {"sections": [], "format_rules": [], "metadata_rules": []}

def load_task_master_requirements():
    """Загружает требования из Task Master Standard."""
    task_master_path = Path("/home/runner/workspace/[standards .md]/0. core standards/0.2 task master standard 15 may 2025 1430 CET by AI Assistant.md")
    
    if not task_master_path.exists():
        return {"protected_sections": [], "update_protocols": [], "quality_checks": []}
    
    try:
        with open(task_master_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "protected_sections": extract_protected_sections(content),
            "update_protocols": extract_update_protocols(content),
            "quality_checks": extract_quality_checklists(content),
            "version_requirements": extract_version_requirements(content)
        }
    except Exception:
        return {"protected_sections": [], "update_protocols": [], "quality_checks": []}

def extract_required_sections_from_registry(content):
    """Извлекает обязательные секции из Registry Standard."""
    sections = []
    
    # Ищем секции с ключевыми словами
    required_patterns = [
        r'обязательн\w+\s+секци\w+',
        r'required\s+section\w*',
        r'должн\w+\s+содержать',
        r'структура\s+стандарта'
    ]
    
    for pattern in required_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.UNICODE)
        sections.extend(matches)
    
    # Добавляем базовые обязательные секции
    sections.extend([
        "Заголовок стандарта", "Версия", "Дата создания",
        "JTBD (Jobs To Be Done)", "Описание", "Критерии соответствия"
    ])
    
    return list(set(sections))

def extract_format_rules(content):
    """Извлекает правила форматирования."""
    rules = []
    
    # Ищем правила форматирования
    format_patterns = [
        r'формат\s+заголовка[:\-]\s*(.+)',
        r'структура\s+файла[:\-]\s*(.+)',
        r'naming\s+convention[:\-]\s*(.+)'
    ]
    
    for pattern in format_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        rules.extend(matches)
    
    return rules

def extract_metadata_rules(content):
    """Извлекает правила метаданных."""
    metadata = []
    
    # Ищем требования к метаданным
    metadata_patterns = [
        r'версия[:\-]\s*(.+)',
        r'автор[:\-]\s*(.+)',
        r'дата[:\-]\s*(.+)',
        r'метаданные[:\-]\s*(.+)'
    ]
    
    for pattern in metadata_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        metadata.extend(matches)
    
    return metadata

def extract_naming_conventions(content):
    """Извлекает соглашения по именованию."""
    conventions = []
    
    # Ищем правила именования файлов
    naming_patterns = [
        r'именование\s+файлов[:\-]\s*(.+)',
        r'file\s+naming[:\-]\s*(.+)',
        r'название\s+стандарта[:\-]\s*(.+)'
    ]
    
    for pattern in naming_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        conventions.extend(matches)
    
    return conventions

def extract_protected_sections(content):
    """Извлекает защищенные секции из Task Master."""
    protected = []
    
    # Ищем PROTECTED SECTION
    protected_match = re.search(r'PROTECTED\s+SECTION(.*?)END\s+PROTECTED', content, re.DOTALL | re.IGNORECASE)
    if protected_match:
        protected.append("PROTECTED SECTION найдена")
    
    # Ищем другие защищенные элементы
    protected_patterns = [
        r'версия[:\-]\s*v\d+\.\d+',
        r'дата\s+создания',
        r'автор\s+стандарта',
        r'метаданные'
    ]
    
    for pattern in protected_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            protected.append(f"Найден защищенный элемент: {pattern}")
    
    return protected

def extract_update_protocols(content):
    """Извлекает протоколы обновления."""
    protocols = []
    
    # Ищем протокол бережности
    if re.search(r'бережн\w+\s+обновлен\w+', content, re.IGNORECASE):
        protocols.append("Протокол бережности обнаружен")
    
    if re.search(r'максимум\s+\d+%', content, re.IGNORECASE):
        protocols.append("Ограничение процента изменений обнаружено")
    
    return protocols

def extract_quality_checklists(content):
    """Извлекает чеклисты качества."""
    checklists = []
    
    # Ищем чеклисты
    checklist_patterns = [
        r'[-*]\s*\[[ x]\]\s*(.+)',
        r'\d+\.\s+(.+проверка.+)',
        r'\d+\.\s+(.+валидация.+)'
    ]
    
    for pattern in checklist_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        checklists.extend(matches[:5])  # Ограничиваем количество
    
    return checklists

def extract_version_requirements(content):
    """Извлекает требования к версионированию."""
    requirements = []
    
    if re.search(r'версия\s+v\d+\.\d+', content, re.IGNORECASE):
        requirements.append("Семантическое версионирование обнаружено")
    
    if re.search(r'changelog|история\s+изменений', content, re.IGNORECASE):
        requirements.append("История изменений обнаружена")
    
    return requirements

def check_registry_compliance(standard_content, registry_requirements):
    """Проверяет соответствие Registry Standard."""
    compliance = {
        "sections_score": 0,
        "format_score": 0,
        "metadata_score": 0,
        "naming_score": 0,
        "total_score": 0,
        "missing_sections": [],
        "format_issues": [],
        "metadata_issues": []
    }
    
    # Проверяем обязательные секции
    required_sections = registry_requirements.get("sections", [])
    present_sections = 0
    
    for section in required_sections:
        if section.lower() in standard_content.lower():
            present_sections += 1
        else:
            compliance["missing_sections"].append(section)
    
    if required_sections:
        compliance["sections_score"] = present_sections / len(required_sections)
    
    # Проверяем формат
    if re.search(r'^#[^#].*', standard_content, re.MULTILINE):
        compliance["format_score"] += 0.3
    if re.search(r'^##[^#].*', standard_content, re.MULTILINE):
        compliance["format_score"] += 0.4
    if re.search(r'^###[^#].*', standard_content, re.MULTILINE):
        compliance["format_score"] += 0.3
    
    # Проверяем метаданные
    if re.search(r'v\d+\.\d+|версия', standard_content, re.IGNORECASE):
        compliance["metadata_score"] += 0.4
    if re.search(r'\d{2}\s+\w+\s+\d{4}', standard_content):
        compliance["metadata_score"] += 0.3
    if re.search(r'by\s+\w+|автор', standard_content, re.IGNORECASE):
        compliance["metadata_score"] += 0.3
    
    # Проверяем именование
    if "standard" in standard_content.lower() or "стандарт" in standard_content.lower():
        compliance["naming_score"] = 1.0
    
    # Общий балл
    compliance["total_score"] = (
        compliance["sections_score"] * 0.4 +
        compliance["format_score"] * 0.3 +
        compliance["metadata_score"] * 0.2 +
        compliance["naming_score"] * 0.1
    )
    
    return compliance

def check_task_master_compliance(standard_content, task_master_requirements):
    """Проверяет соответствие Task Master Standard."""
    compliance = {
        "protected_sections_score": 0,
        "update_protocol_score": 0,
        "quality_checks_score": 0,
        "version_score": 0,
        "total_score": 0,
        "protocol_violations": [],
        "missing_quality_checks": []
    }
    
    # Проверяем защищенные секции
    protected_found = 0
    for protected in task_master_requirements.get("protected_sections", []):
        if "PROTECTED" in standard_content:
            protected_found += 1
            break
    
    if task_master_requirements.get("protected_sections"):
        compliance["protected_sections_score"] = min(1.0, protected_found / len(task_master_requirements["protected_sections"]))
    
    # Проверяем протоколы обновления
    if re.search(r'обновлен\w+|updated|изменен\w+', standard_content, re.IGNORECASE):
        compliance["update_protocol_score"] = 1.0
    
    # Проверяем качество
    quality_indicators = [
        r'проверка',
        r'валидация', 
        r'тест',
        r'критерии',
        r'соответств\w+'
    ]
    
    quality_found = sum(1 for pattern in quality_indicators if re.search(pattern, standard_content, re.IGNORECASE))
    compliance["quality_checks_score"] = min(1.0, quality_found / len(quality_indicators))
    
    # Проверяем версионирование
    if re.search(r'v\d+\.\d+', standard_content):
        compliance["version_score"] = 1.0
    
    # Общий балл
    compliance["total_score"] = (
        compliance["protected_sections_score"] * 0.2 +
        compliance["update_protocol_score"] * 0.3 +
        compliance["quality_checks_score"] * 0.3 +
        compliance["version_score"] * 0.2
    )
    
    return compliance

def calculate_overall_score(validation_results):
    """Вычисляет общий балл соответствия."""
    registry_score = validation_results.get("registry_compliance", {}).get("total_score", 0)
    task_master_score = validation_results.get("task_master_compliance", {}).get("total_score", 0)
    
    if registry_score and task_master_score:
        return (registry_score + task_master_score) / 2
    elif registry_score:
        return registry_score
    elif task_master_score:
        return task_master_score
    else:
        return 0

def generate_recommendations(validation_results):
    """Генерирует рекомендации по улучшению."""
    recommendations = []
    
    registry = validation_results.get("registry_compliance", {})
    task_master = validation_results.get("task_master_compliance", {})
    
    # Рекомендации по Registry
    if registry.get("sections_score", 0) < 0.8:
        recommendations.append("Добавить недостающие обязательные секции из Registry Standard")
    
    if registry.get("format_score", 0) < 0.7:
        recommendations.append("Улучшить структуру заголовков (H1, H2, H3)")
    
    if registry.get("metadata_score", 0) < 0.8:
        recommendations.append("Добавить версию, дату и автора стандарта")
    
    # Рекомендации по Task Master
    if task_master.get("protected_sections_score", 0) < 0.5:
        recommendations.append("Добавить PROTECTED SECTION для критических метаданных")
    
    if task_master.get("quality_checks_score", 0) < 0.6:
        recommendations.append("Добавить критерии проверки и валидации")
    
    if task_master.get("version_score", 0) < 1.0:
        recommendations.append("Добавить семантическую версию (v1.0, v1.1, etc.)")
    
    return recommendations

if __name__ == "__main__":
    # Тестирование команды
    test_request = {
        "standard_path": "[standards .md]/3. scenarium · jtbd · hipothises · offering · tone/2.2 hypothesis standard 14 may 2025 0740 cet by ai assistant.md",
        "check_type": "full"
    }
    
    result = validate_standard_compliance(test_request)
    print(json.dumps(result, indent=2, ensure_ascii=False))