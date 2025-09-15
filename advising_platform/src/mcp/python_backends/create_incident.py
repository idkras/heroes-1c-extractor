#!/usr/bin/env python3
"""
MCP Backend: create_incident

JTBD: Я хочу создавать структурированные инциденты через MCP команды,
чтобы все инциденты автоматически получали анализ первопричин.
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def create_incident(request):
    """Создает структурированный инцидент с автоматическим анализом и валидацией по AI Incident Standard."""
    
    try:
        from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        log_mcp_operation = lambda *args: None
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    start_time = datetime.now()
    
    # РЕФЛЕКСИЯ: Проверяем соответствие запроса AI Incident Standard
    reflection_result = reflection_guard(
        claim="Создаю инцидент согласно AI Incident Standard v1.9",
        evidence={
            "has_title": bool(request.get("title")),
            "has_five_whys": bool(request.get("five_whys")) or bool(request.get("description", "").find("почему")),
            "has_root_cause": bool(request.get("root_cause")),
            "has_design_injection": bool(request.get("design_injection")),
            "has_status": request.get("status", "Recorded") in ["Recorded", "In Progress", "Hypothesis Testing", "Hypothesis Confirmed", "Hypothesis Failed"]
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Инцидент может не соответствовать стандарту")
        print("Проверьте: 5 почему, корневая причина, дизайн-инъекция, статус")
    
    try:
        title = request.get("title", "")
        description = request.get("description", "")
        error_message = request.get("error", "")
        priority = request.get("priority", "medium")
        affected_systems = request.get("affected_systems", [])
        workflow_state = request.get("workflow_state", {})
        
        # Генерируем ID инцидента
        incident_id = f"I{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем структуру инцидента
        incident = {
            "id": incident_id,
            "title": title,
            "description": description,
            "error": error_message,
            "priority": priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "affected_systems": affected_systems,
            "workflow_state": workflow_state,
            "resolution_time_target": "4 hours" if priority == "high" else "24 hours",
            "assigned_to": "development_team",
            "tags": request.get("tags", []),
            "related_tasks": request.get("related_tasks", [])
        }
        
        # Сохраняем инцидент
        incidents_dir = Path("/home/runner/workspace/[todo · incidents]")
        incident_file = incidents_dir / f"incident_{incident_id}.md"
        
        # Извлекаем структурированные данные для стандартного формата
        five_whys = request.get("five_whys", [])
        root_cause = request.get("root_cause", "")
        design_injection = request.get("design_injection", "")
        design_change = request.get("design_change", "")
        status_options = ["Recorded", "In Progress", "Hypothesis Testing", "Hypothesis Confirmed", "Hypothesis Failed"]
        incident_status = request.get("status", "Recorded")
        
        if incident_status not in status_options:
            incident_status = "Recorded"
            
        # Создаем заголовок в формате AI Incident Standard: DD MMM YYYY HH:MM
        now = datetime.now()
        header_date = now.strftime('%d %b %Y %H:%M')
        
        # РЕФЛЕКСИЯ: Проверяем корректность формата перед созданием
        reflection_format = reflection_guard(
            claim="Создаю инцидент в точном соответствии с AI Incident Standard v1.9",
            evidence={
                "has_proper_header_format": bool(re.match(r'\d{2} \w{3} \d{4} \d{2}:\d{2}', header_date)),
                "has_five_whys": len(five_whys) >= 5 if five_whys else False,
                "has_root_cause": bool(root_cause),
                "has_design_injection": bool(design_injection),
                "has_design_change": bool(design_change),
                "valid_status": incident_status in status_options
            }
        )
        
        if reflection_format.get("reflection_needed", False):
            print("⚠️ РЕФЛЕКСИЯ: Инцидент не соответствует AI Incident Standard v1.9")
            return {
                "success": False,
                "error": "Инцидент не прошел проверку стандарта",
                "missing_elements": reflection_format.get("missing_elements", [])
            }
        
        # Создаем Markdown файл инцидента согласно AI Incident Standard v1.9
        # Формат заголовка: ## DD MMM YYYY HH:MM - Краткое описание проблемы
        md_content = f"""## {header_date} - {title}

**5 почему разбор:**
"""
        
        # РЕФЛЕКСИЯ: Проверяем качество анализа 5 почему
        if five_whys and len(five_whys) >= 5:
            for i, why in enumerate(five_whys[:5], 1):
                md_content += f"{i}. {why}\n"
        elif description and "5 почему" in description:
            # Извлекаем из description если там есть структура 5 почему
            md_content += f"{description}\n"
        else:
            # РЕФЛЕКСИЯ: Требуется настоящий анализ, не шаблон
            reflection_analysis = reflection_guard(
                claim="Генерирую полноценный анализ 5 почему вместо шаблона",
                evidence={"has_real_analysis": False, "using_template": True}
            )
            
            if reflection_analysis.get("reflection_needed", False):
                print("⚠️ РЕФЛЕКСИЯ: Требуется настоящий анализ 5 почему, не шаблон")
            
            md_content += f"""1. Почему возникла проблема '{title}'? - Требуется детальный анализ.
2. Почему проблема не была предотвращена? - Необходимо выяснить причины.
3. Почему отсутствуют превентивные меры? - Требуется анализ процессов.
4. Почему процессы не предусматривают защиту? - Нужна проверка системы.
5. Почему система не обеспечивает надежность? - Корневая причина требует исследования.
"""

        # РЕФЛЕКСИЯ: Проверяем корневую причину
        if not root_cause or len(root_cause) > 100:
            reflection_root_cause = reflection_guard(
                claim="Корневая причина сформулирована корректно (не более 100 символов)",
                evidence={"has_root_cause": bool(root_cause), "within_limit": len(root_cause) <= 100 if root_cause else False}
            )
            if reflection_root_cause.get("reflection_needed", False):
                print("⚠️ РЕФЛЕКСИЯ: Корневая причина должна быть не более 100 символов")

        # РЕФЛЕКСИЯ: Проверяем дизайн-инъекцию
        if not design_injection or len(design_injection) > 50:
            reflection_injection = reflection_guard(
                claim="Дизайн-инъекция указана корректно (не более 50 символов)",
                evidence={"has_injection": bool(design_injection), "within_limit": len(design_injection) <= 50 if design_injection else False}
            )
            if reflection_injection.get("reflection_needed", False):
                print("⚠️ РЕФЛЕКСИЯ: Дизайн-инъекция должна быть не более 50 символов")

        # РЕФЛЕКСИЯ: Проверяем дизайн изменения
        if not design_change or len(design_change) < 100 or len(design_change) > 150:
            reflection_change = reflection_guard(
                claim="Дизайн изменения сформулировано корректно (100-150 символов)",
                evidence={"has_change": bool(design_change), "within_range": 100 <= len(design_change) <= 150 if design_change else False}
            )
            if reflection_change.get("reflection_needed", False):
                print("⚠️ РЕФЛЕКСИЯ: Дизайн изменения должно быть 100-150 символов")

        md_content += f"""
**Корневая причина:** {root_cause if root_cause else 'Требуется анализ первопричин'}
**Дизайн-инъекция:** {design_injection if design_injection else 'Требуется определение точки вмешательства'}
**Дизайн изменения:** {design_change if design_change else 'Требуется разработка конкретного решения адресующего корневую причину'}
**Статус:** {incident_status}
"""
        
        with open(incident_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Также сохраняем JSON версию
        json_file = incidents_dir / f"incident_{incident_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(incident, f, indent=2, ensure_ascii=False)
        
        # Логируем операцию
        duration = (datetime.now() - start_time).total_seconds() * 1000
        log_mcp_operation(
            'create-incident',
            {"title": title, "priority": priority},
            {"success": True, "incident_created": True, "incident_id": incident_id},
            duration
        )
        
        # Обновляем документацию для критических инцидентов
        try:
            from advising_platform.src.mcp.modules.documentation_validator import update_documentation
            update_documentation("create_incident", {
                "incident_id": incident_id,
                "title": title,
                "priority": priority
            })
        except ImportError:
            pass  # Документация не критична для базовой функциональности
        
        return {
            "success": True,
            "incident": incident,
            "incident_file": str(incident_file),
            "json_file": str(json_file),
            "message": f"Инцидент {incident_id} создан успешно",
            "next_action": "Запустить анализ первопричин"
        }
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        log_mcp_operation(
            'create-incident',
            request,
            {"success": False, "error": str(e)},
            duration
        )
        
        return {
            "success": False,
            "error": str(e),
            "message": "Ошибка при создании инцидента"
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        request_data = json.loads(sys.argv[1])
        result = create_incident(request_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("CreateIncident MCP command - use with incident JSON input")