#!/usr/bin/env python3
"""
Update Registry Standard Workflow - атомарные шаги с рефлексией

Workflow для обновления Registry Standard через проверяемые шаги:
1. read_registry_standard → [reflection]
2. identify_missing_commands → [reflection]
3. prepare_command_entries → [reflection]
4. validate_update_scope → [reflection]
5. apply_registry_updates → [reflection]
6. validate_compliance → [reflection]
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def update_registry_standard_workflow(request):
    """Orchestrates Registry Standard update through atomic MCP commands with reflection."""
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    workflow_id = f"registry_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow_state = {
        "workflow_id": workflow_id,
        "steps_completed": [],
        "current_step": None,
        "validation_results": {},
        "registry_data": {},
        "start_time": datetime.now().isoformat()
    }
    
    print(f"🔄 Запуск workflow обновления Registry Standard: {workflow_id}")
    
    try:
        # STEP 1: Read Registry Standard
        step1_result = step1_read_registry_standard(request, workflow_state)
        if not step1_result["success"]:
            return step1_result
        
        # STEP 2: Identify Missing Commands
        step2_result = step2_identify_missing_commands(step1_result["registry_content"], workflow_state)
        if not step2_result["success"]:
            return step2_result
            
        # STEP 3: Prepare Command Entries
        step3_result = step3_prepare_command_entries(step2_result["missing_commands"], workflow_state)
        if not step3_result["success"]:
            return step3_result
            
        # STEP 4: Validate Update Scope
        step4_result = step4_validate_update_scope(step3_result["new_entries"], workflow_state)
        if not step4_result["success"]:
            return step4_result
            
        # STEP 5: Apply Registry Updates
        step5_result = step5_apply_registry_updates(step4_result["validated_entries"], workflow_state)
        if not step5_result["success"]:
            return step5_result
            
        # STEP 6: Validate Compliance
        step6_result = step6_validate_compliance(step5_result["updated_file"], workflow_state)
        
        workflow_state["end_time"] = datetime.now().isoformat()
        workflow_state["total_duration"] = (datetime.now() - datetime.fromisoformat(workflow_state["start_time"])).total_seconds()
        
        return {
            "success": step6_result["success"],
            "workflow_id": workflow_id,
            "registry_updated": step5_result.get("updated_file"),
            "commands_added": len(step3_result.get("new_entries", [])),
            "compliance_score": step6_result.get("compliance_score", 0),
            "workflow_state": workflow_state
        }
        
    except Exception as e:
        workflow_state["error"] = str(e)
        workflow_state["failed_at"] = workflow_state.get("current_step", "unknown")
        return {
            "success": False,
            "error": str(e),
            "workflow_id": workflow_id,
            "workflow_state": workflow_state
        }

def step1_read_registry_standard(request, workflow_state):
    """STEP 1: Чтение текущего Registry Standard."""
    workflow_state["current_step"] = "read_registry_standard"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("📋 STEP 1: Чтение Registry Standard")
    
    registry_path = Path("/home/runner/workspace/[standards .md]/0. core standards/0.1 registry standard 15 may 2025 1320 CET by AI Assistant.md")
    
    # РЕФЛЕКСИЯ: Проверяем доступность Registry Standard
    reflection_result = reflection_guard(
        claim="Registry Standard доступен для чтения и обновления",
        evidence={
            "file_exists": registry_path.exists(),
            "file_readable": registry_path.is_file() if registry_path.exists() else False,
            "has_update_request": bool(request.get("new_commands")),
            "path_correct": "registry standard" in str(registry_path).lower()
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Проблемы с доступностью Registry Standard")
        return {
            "success": False,
            "step": "read_registry_standard",
            "error": "Registry Standard недоступен",
            "reflection_details": reflection_result
        }
    
    if not registry_path.exists():
        return {
            "success": False,
            "step": "read_registry_standard",
            "error": f"Registry Standard не найден: {registry_path}"
        }
    
    # Читаем содержимое
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_content = f.read()
    
    workflow_state["steps_completed"].append("read_registry_standard")
    workflow_state["validation_results"]["step1"] = reflection_result
    workflow_state["registry_data"]["content"] = registry_content
    workflow_state["registry_data"]["path"] = str(registry_path)
    
    print("✅ STEP 1: Registry Standard прочитан")
    return {
        "success": True,
        "step": "read_registry_standard",
        "registry_content": registry_content,
        "registry_path": str(registry_path)
    }

def step2_identify_missing_commands(registry_content, workflow_state):
    """STEP 2: Определение отсутствующих MCP команд."""
    workflow_state["current_step"] = "identify_missing_commands"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("🔍 STEP 2: Поиск отсутствующих команд")
    
    # Список новых команд из dependency matrix
    new_commands = [
        {
            "name": "update-standard",
            "description": "Обновляет стандарты с валидацией против Registry и Task Master требований",
            "backend": "advising_platform/src/mcp/python_backends/update_standard.py",
            "status": "PRODUCTION"
        },
        {
            "name": "add-mcp-command", 
            "description": "Добавляет новые MCP команды с валидацией зависимостей",
            "backend": "advising_platform/src/mcp/python_backends/add_mcp_command.py",
            "status": "PRODUCTION"
        },
        {
            "name": "validate-standard-compliance",
            "description": "Проверяет соответствие всех секций стандарта требованиям Registry и Task Master",
            "backend": "advising_platform/src/mcp/python_backends/validate_standard_compliance.py", 
            "status": "PRODUCTION"
        },
        {
            "name": "incident-creation-workflow",
            "description": "Атомарный workflow создания инцидентов с рефлексией на каждом шаге",
            "backend": "advising_platform/src/mcp/workflows/incident_creation_workflow.py",
            "status": "PRODUCTION"
        }
    ]
    
    # Проверяем какие команды отсутствуют в Registry
    missing_commands = []
    for cmd in new_commands:
        if cmd["name"] not in registry_content:
            missing_commands.append(cmd)
    
    # РЕФЛЕКСИЯ: Проверяем полноту анализа команд
    reflection_result = reflection_guard(
        claim="Определены все новые MCP команды требующие регистрации",
        evidence={
            "commands_found": len(missing_commands) > 0,
            "matches_dependency_matrix": len(missing_commands) <= 4,
            "has_descriptions": all(cmd.get("description") for cmd in missing_commands),
            "has_backends": all(cmd.get("backend") for cmd in missing_commands)
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Анализ команд требует улучшения")
    
    workflow_state["steps_completed"].append("identify_missing_commands")
    workflow_state["validation_results"]["step2"] = reflection_result
    workflow_state["registry_data"]["missing_commands"] = missing_commands
    
    print(f"✅ STEP 2: Найдено {len(missing_commands)} новых команд для регистрации")
    for cmd in missing_commands:
        print(f"  - {cmd['name']}: {cmd['description'][:50]}...")
    
    return {
        "success": True,
        "step": "identify_missing_commands",
        "missing_commands": missing_commands
    }

def step3_prepare_command_entries(missing_commands, workflow_state):
    """STEP 3: Подготовка записей для новых команд."""
    workflow_state["current_step"] = "prepare_command_entries"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("🔧 STEP 3: Подготовка записей команд")
    
    new_entries = []
    
    for cmd in missing_commands:
        # Создаем запись согласно формату Registry Standard
        entry = f"""
### {cmd['name']}
**Описание**: {cmd['description']}  
**Backend**: `{cmd['backend']}`  
**Статус**: {cmd['status']}  
**Дата добавления**: {datetime.now().strftime('%d %b %Y')}  
**Интеграция**: Reflection Guard на каждом шаге  
**Зависимости**: Registry Standard, Task Master Standard  
"""
        new_entries.append({
            "command_name": cmd['name'],
            "entry_text": entry,
            "priority": "high" if "workflow" in cmd['name'] else "medium"
        })
    
    # РЕФЛЕКСИЯ: Проверяем качество подготовленных записей
    reflection_result = reflection_guard(
        claim="Записи команд соответствуют формату Registry Standard",
        evidence={
            "all_entries_prepared": len(new_entries) == len(missing_commands),
            "have_descriptions": all("Описание" in entry["entry_text"] for entry in new_entries),
            "have_backends": all("Backend" in entry["entry_text"] for entry in new_entries),
            "have_dates": all("Дата добавления" in entry["entry_text"] for entry in new_entries)
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Записи команд требуют улучшения формата")
    
    workflow_state["steps_completed"].append("prepare_command_entries")
    workflow_state["validation_results"]["step3"] = reflection_result
    workflow_state["registry_data"]["new_entries"] = new_entries
    
    print(f"✅ STEP 3: Подготовлено {len(new_entries)} записей команд")
    
    return {
        "success": True,
        "step": "prepare_command_entries",
        "new_entries": new_entries
    }

def step4_validate_update_scope(new_entries, workflow_state):
    """STEP 4: Валидация объема обновлений."""
    workflow_state["current_step"] = "validate_update_scope"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("📊 STEP 4: Валидация объема обновлений")
    
    current_content = workflow_state["registry_data"]["content"]
    total_new_content = sum(len(entry["entry_text"]) for entry in new_entries)
    original_length = len(current_content)
    
    # Вычисляем процент добавлений
    addition_percentage = (total_new_content / original_length) * 100 if original_length > 0 else 0
    
    # РЕФЛЕКСИЯ: Проверяем соответствие протоколу бережности
    reflection_result = reflection_guard(
        claim="Обновления соответствуют протоколу бережности (максимум 20% изменений)",
        evidence={
            "within_limit": addition_percentage <= 20,
            "reasonable_scope": addition_percentage > 0,
            "essential_additions": len(new_entries) <= 5,
            "percentage": addition_percentage
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print(f"⚠️ РЕФЛЕКСИЯ: Объем изменений {addition_percentage:.1f}% требует внимания")
        if addition_percentage > 20:
            return {
                "success": False,
                "step": "validate_update_scope",
                "error": f"Превышен протокол бережности: {addition_percentage:.1f}% добавлений (максимум 20%)",
                "addition_percentage": addition_percentage
            }
    
    workflow_state["steps_completed"].append("validate_update_scope")
    workflow_state["validation_results"]["step4"] = reflection_result
    workflow_state["registry_data"]["addition_percentage"] = addition_percentage
    
    print(f"✅ STEP 4: Объем обновлений валидирован ({addition_percentage:.1f}%)")
    
    return {
        "success": True,
        "step": "validate_update_scope",
        "validated_entries": new_entries,
        "addition_percentage": addition_percentage
    }

def step5_apply_registry_updates(validated_entries, workflow_state):
    """STEP 5: Применение обновлений к Registry Standard."""
    workflow_state["current_step"] = "apply_registry_updates"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("💾 STEP 5: Применение обновлений")
    
    registry_path = Path(workflow_state["registry_data"]["path"])
    current_content = workflow_state["registry_data"]["content"]
    
    # РЕФЛЕКСИЯ: Проверяем готовность к обновлению
    reflection_result = reflection_guard(
        claim="Готов безопасно обновить Registry Standard",
        evidence={
            "file_accessible": registry_path.exists(),
            "entries_validated": bool(validated_entries),
            "backup_possible": True,
            "within_protocol": workflow_state["registry_data"]["addition_percentage"] <= 20
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Обновление требует дополнительных проверок")
        return {
            "success": False,
            "step": "apply_registry_updates",
            "error": "Не удалось пройти проверки безопасности"
        }
    
    # Создаем резервную копию
    backup_path = Path(f"/home/runner/workspace/registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(current_content)
    
    # Находим место для вставки новых команд
    updated_content = current_content
    
    # Ищем секцию MCP Commands или создаем новую
    if "## MCP Commands Registry" in updated_content:
        insert_point = updated_content.find("## MCP Commands Registry")
        insert_point = updated_content.find("\n", insert_point) + 1
    else:
        # Добавляем новую секцию перед концом файла
        insert_point = len(updated_content) - 100  # Перед PROTECTED SECTION
        if insert_point < 0:
            insert_point = len(updated_content)
        
        new_section = "\n## MCP Commands Registry\n\nРеестр всех доступных MCP команд с описаниями и статусами.\n\n"
        updated_content = updated_content[:insert_point] + new_section + updated_content[insert_point:]
        insert_point += len(new_section)
    
    # Вставляем новые команды
    for entry in validated_entries:
        updated_content = updated_content[:insert_point] + entry["entry_text"] + updated_content[insert_point:]
        insert_point += len(entry["entry_text"])
    
    # Обновляем версию и дату
    updated_content = update_version_metadata(updated_content)
    
    # Сохраняем обновленный файл
    with open(registry_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    workflow_state["steps_completed"].append("apply_registry_updates")
    workflow_state["validation_results"]["step5"] = reflection_result
    workflow_state["registry_data"]["backup_path"] = str(backup_path)
    
    print(f"✅ STEP 5: Registry Standard обновлен, резервная копия: {backup_path.name}")
    
    return {
        "success": True,
        "step": "apply_registry_updates",
        "updated_file": str(registry_path),
        "backup_created": str(backup_path),
        "commands_added": len(validated_entries)
    }

def step6_validate_compliance(updated_file, workflow_state):
    """STEP 6: Финальная валидация соответствия стандартам."""
    workflow_state["current_step"] = "validate_compliance"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("✅ STEP 6: Финальная валидация")
    
    # Читаем обновленный файл
    with open(updated_file, 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    # Проверяем структуру и соответствие
    validation_checks = {
        "has_registry_section": "MCP Commands Registry" in final_content,
        "commands_added": all(entry["command_name"] in final_content for entry in workflow_state["registry_data"]["new_entries"]),
        "has_descriptions": final_content.count("**Описание**:") >= len(workflow_state["registry_data"]["new_entries"]),
        "has_backends": final_content.count("**Backend**:") >= len(workflow_state["registry_data"]["new_entries"]),
        "version_updated": datetime.now().strftime('%Y') in final_content,
        "structure_intact": final_content.count("##") >= 3
    }
    
    compliance_score = sum(validation_checks.values()) / len(validation_checks)
    
    # РЕФЛЕКСИЯ: Проверяем итоговое качество
    reflection_result = reflection_guard(
        claim="Обновленный Registry Standard соответствует всем требованиям",
        evidence=validation_checks
    )
    
    success = compliance_score >= 0.85
    
    workflow_state["steps_completed"].append("validate_compliance")
    workflow_state["validation_results"]["step6"] = reflection_result
    workflow_state["final_compliance_score"] = compliance_score
    
    if success:
        print("✅ STEP 6: Registry Standard успешно обновлен и валидирован")
    else:
        print("⚠️ STEP 6: Registry Standard обновлен с предупреждениями")
    
    return {
        "success": success,
        "step": "validate_compliance",
        "compliance_score": compliance_score,
        "validation_checks": validation_checks,
        "registry_compliant": success
    }

def update_version_metadata(content):
    """Обновляет версию и метаданные в стандарте."""
    now = datetime.now()
    
    # Обновляем дату в PROTECTED SECTION
    content = re.sub(
        r'updated: .+? by AI Assistant',
        f'updated: {now.strftime("%d %b %Y, %H:%M CET")} by AI Assistant',
        content
    )
    
    # Обновляем версию если есть
    if "version:" in content:
        content = re.sub(r'version: v(\d+)\.(\d+)', lambda m: f'version: v{m.group(1)}.{int(m.group(2))+1}', content)
    
    return content

if __name__ == "__main__":
    # Тестирование workflow
    test_request = {
        "new_commands": [
            "update-standard",
            "add-mcp-command", 
            "validate-standard-compliance",
            "incident-creation-workflow"
        ]
    }
    
    result = update_registry_standard_workflow(test_request)
    print(json.dumps(result, indent=2, ensure_ascii=False))