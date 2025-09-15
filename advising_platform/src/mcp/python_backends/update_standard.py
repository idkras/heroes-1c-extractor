#!/usr/bin/env python3
"""
MCP Backend: update_standard

JTBD: Я хочу обновлять стандарты с автоматической валидацией против Registry и Task Master стандартов,
чтобы все изменения соответствовали протоколу бережности и чеклистам качества.
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def update_standard(request):
    """Обновляет стандарт с автоматической валидацией против Registry и Task Master стандартов."""
    
    try:
        from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        log_mcp_operation = lambda *args: None
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    start_time = datetime.now()
    
    try:
        standard_path = request.get("standard_path", "")
        updates = request.get("updates", {})
        update_reason = request.get("update_reason", "")
        
        if not standard_path or not updates:
            return {
                "success": False,
                "error": "Требуются standard_path и updates",
                "command": "update_standard"
            }
        
        # РЕФЛЕКСИЯ: Проверяем обоснованность обновления
        reflection_result = reflection_guard(
            claim=f"Обновление стандарта '{standard_path}' необходимо и обосновано",
            evidence={
                "has_update_reason": bool(update_reason),
                "has_specific_updates": bool(updates and isinstance(updates, dict)),
                "standard_exists": Path(f"/home/runner/workspace/{standard_path}").exists()
            }
        )
        
        if reflection_result.get("reflection_needed", False):
            print("⚠️ РЕФЛЕКСИЯ: Обновление стандарта требует дополнительного обоснования")
            return {
                "success": False,
                "error": "Обновление не прошло проверку reflection_guard",
                "reflection_needed": True
            }
        
        # Читаем Registry Standard для проверки структуры
        registry_standard_path = "[standards .md]/0. core standards/0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md"
        task_master_path = "[standards .md]/0. core standards/0.2 task master standard 15 may 2025 1430 CET by AI Assistant.md"
        
        registry_requirements = read_standard_requirements(registry_standard_path)
        task_master_requirements = read_standard_requirements(task_master_path)
        
        # Читаем текущий стандарт
        full_path = Path(f"/home/runner/workspace/{standard_path}")
        if not full_path.exists():
            return {
                "success": False,
                "error": f"Стандарт не найден: {standard_path}",
                "command": "update_standard"
            }
        
        with open(full_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Применяем протокол бережности (максимум 10-20% изменений)
        original_length = len(current_content)
        
        # Создаем обновленную версию
        updated_content = apply_updates(current_content, updates, update_reason)
        
        # Проверяем процент изменений
        changes_percentage = calculate_changes_percentage(current_content, updated_content)
        
        if changes_percentage > 20:
            return {
                "success": False,
                "error": f"Превышен протокол бережности: {changes_percentage}% изменений (максимум 20%)",
                "changes_percentage": changes_percentage
            }
        
        # Валидируем обновленный стандарт
        validation_result = validate_standard_compliance(
            updated_content, 
            registry_requirements, 
            task_master_requirements
        )
        
        if not validation_result["is_compliant"]:
            return {
                "success": False,
                "error": "Обновленный стандарт не соответствует требованиям",
                "validation_errors": validation_result["errors"],
                "command": "update_standard"
            }
        
        # Обновляем версию и метаданные
        final_content = update_version_and_metadata(updated_content, update_reason)
        
        # Создаем резервную копию
        backup_path = create_backup(full_path, current_content)
        
        # Сохраняем обновленный стандарт
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        # Финальная проверка после сохранения
        final_validation = validate_updated_standard_all_sections(full_path)
        
        result = {
            "success": True,
            "standard_path": standard_path,
            "changes_percentage": changes_percentage,
            "backup_created": str(backup_path),
            "validation_passed": validation_result["is_compliant"],
            "final_validation": final_validation,
            "update_reason": update_reason,
            "timestamp": datetime.now().isoformat()
        }
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        log_mcp_operation("update_standard", start_time, result, duration_ms)
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "command": "update_standard",
            "timestamp": datetime.now().isoformat()
        }
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        log_mcp_operation("update_standard", start_time, error_result, duration_ms)
        return error_result

def read_standard_requirements(standard_path):
    """Читает требования из Registry или Task Master стандарта."""
    try:
        full_path = Path(f"/home/runner/workspace/{standard_path}")
        if not full_path.exists():
            return {"sections": [], "checklists": []}
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлекаем чеклисты и обязательные секции
        requirements = {
            "sections": extract_required_sections(content),
            "checklists": extract_checklists(content),
            "protected_elements": extract_protected_elements(content)
        }
        
        return requirements
    except Exception:
        return {"sections": [], "checklists": [], "protected_elements": []}

def extract_required_sections(content):
    """Извлекает обязательные секции из стандарта."""
    sections = []
    # Ищем заголовки секций
    section_matches = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    for match in section_matches:
        if any(keyword in match.lower() for keyword in ['обязательн', 'required', 'must', 'section']):
            sections.append(match.strip())
    return sections

def extract_checklists(content):
    """Извлекает чеклисты из стандарта."""
    checklists = []
    # Ищем чеклисты
    checklist_pattern = r'[-*]\s*\[[ x]\]\s*(.+)'
    checklist_matches = re.findall(checklist_pattern, content, re.MULTILINE)
    checklists.extend(checklist_matches)
    
    # Ищем пронумерованные списки требований
    numbered_pattern = r'^\d+\.\s+(.+)$'
    numbered_matches = re.findall(numbered_pattern, content, re.MULTILINE)
    checklists.extend(numbered_matches)
    
    return checklists

def extract_protected_elements(content):
    """Извлекает защищенные элементы (версии, метаданные)."""
    protected = []
    
    # PROTECTED SECTION в Task Master
    protected_match = re.search(r'PROTECTED SECTION.*?END PROTECTED', content, re.DOTALL)
    if protected_match:
        protected.append("PROTECTED SECTION")
    
    # Версии и даты
    version_matches = re.findall(r'v\d+\.\d+|\d{2}\s+\w+\s+\d{4}', content)
    protected.extend(version_matches)
    
    return protected

def apply_updates(content, updates, reason):
    """Применяет обновления к контенту стандарта."""
    updated_content = content
    
    for section, new_content in updates.items():
        if section == "add_section":
            # Добавляем новую секцию
            updated_content += f"\n\n## {new_content['title']}\n\n{new_content['content']}"
        elif section == "update_section":
            # Обновляем существующую секцию
            section_pattern = f"(## {new_content['title']}.*?)(?=##|$)"
            replacement = f"## {new_content['title']}\n\n{new_content['content']}\n\n"
            updated_content = re.sub(section_pattern, replacement, updated_content, flags=re.DOTALL)
        elif section == "add_note":
            # Добавляем примечание об обновлении
            note = f"\n**Обновление {datetime.now().strftime('%d %b %Y')}**: {reason}\n"
            updated_content += note
    
    return updated_content

def calculate_changes_percentage(original, updated):
    """Вычисляет процент изменений между версиями."""
    original_lines = original.splitlines()
    updated_lines = updated.splitlines()
    
    # Простое сравнение по строкам
    total_lines = max(len(original_lines), len(updated_lines))
    if total_lines == 0:
        return 0
    
    different_lines = 0
    for i in range(max(len(original_lines), len(updated_lines))):
        orig_line = original_lines[i] if i < len(original_lines) else ""
        upd_line = updated_lines[i] if i < len(updated_lines) else ""
        if orig_line != upd_line:
            different_lines += 1
    
    return round((different_lines / total_lines) * 100, 1)

def validate_standard_compliance(content, registry_req, task_master_req):
    """Валидирует соответствие стандарта Registry и Task Master требованиям."""
    errors = []
    
    # Проверяем обязательные секции из Registry
    for section in registry_req.get("sections", []):
        if section.lower() not in content.lower():
            errors.append(f"Отсутствует обязательная секция: {section}")
    
    # Проверяем чеклисты из Task Master
    for checklist_item in task_master_req.get("checklists", []):
        if checklist_item.lower() not in content.lower() and len(checklist_item) > 10:
            errors.append(f"Отсутствует элемент чеклиста: {checklist_item[:50]}...")
    
    # Проверяем защищенные элементы
    if "version" not in content.lower() and "версия" not in content.lower():
        errors.append("Отсутствует информация о версии")
    
    return {
        "is_compliant": len(errors) == 0,
        "errors": errors
    }

def update_version_and_metadata(content, reason):
    """Обновляет версию и метаданные в стандарте."""
    now = datetime.now()
    
    # Ищем существующую версию
    version_match = re.search(r'v(\d+)\.(\d+)', content)
    if version_match:
        major, minor = int(version_match.group(1)), int(version_match.group(2))
        new_version = f"v{major}.{minor + 1}"
        content = re.sub(r'v\d+\.\d+', new_version, content, count=1)
    else:
        # Добавляем версию если её нет
        content = f"**Версия**: v1.1\n\n{content}"
    
    # Добавляем запись об обновлении
    update_note = f"\n**Последнее обновление**: {now.strftime('%d %b %Y %H:%M')} - {reason}\n"
    
    # Вставляем в конец или перед защищенной секцией
    if "PROTECTED SECTION" in content:
        content = content.replace("PROTECTED SECTION", f"{update_note}\nPROTECTED SECTION")
    else:
        content += update_note
    
    return content

def create_backup(file_path, content):
    """Создает резервную копию стандарта."""
    backup_dir = Path("/home/runner/workspace/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{file_path.stem}_backup_{timestamp}.md"
    backup_path = backup_dir / backup_name
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return backup_path

def validate_updated_standard_all_sections(standard_path):
    """Финальная валидация всех секций обновленного стандарта."""
    try:
        with open(standard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            "has_title": bool(re.search(r'^#[^#]', content, re.MULTILINE)),
            "has_version": bool(re.search(r'v\d+\.\d+|версия', content, re.IGNORECASE)),
            "has_sections": len(re.findall(r'^##', content, re.MULTILINE)) >= 2,
            "has_update_metadata": any(keyword in content.lower() for keyword in ['обновлен', 'updated', 'изменен']),
            "proper_structure": bool(re.search(r'#{1,3}\s+.+', content))
        }
        
        all_passed = all(validation_results.values())
        
        return {
            "all_sections_valid": all_passed,
            "detailed_checks": validation_results,
            "compliance_level": sum(validation_results.values()) / len(validation_results)
        }
        
    except Exception as e:
        return {
            "all_sections_valid": False,
            "error": str(e),
            "compliance_level": 0
        }

if __name__ == "__main__":
    # Тестирование команды
    test_request = {
        "standard_path": "[standards .md]/3. scenarium · jtbd · hipothises · offering · tone/2.2 hypothesis standard 14 may 2025 0740 cet by ai assistant.md",
        "updates": {
            "add_note": "Добавлена интеграция с reflection_guard для проверки каждого шага workflow"
        },
        "update_reason": "Интеграция системы рефлексии в workflow стандарта гипотез"
    }
    
    result = update_standard(test_request)
    print(json.dumps(result, indent=2, ensure_ascii=False))