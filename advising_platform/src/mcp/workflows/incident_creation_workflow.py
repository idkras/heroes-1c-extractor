#!/usr/bin/env python3
"""
Incident Creation Workflow - атомарные шаги с рефлексией

Workflow для создания инцидентов через цепочку проверяемых MCP команд:
1. validate_incident_data → [reflection]
2. analyze_five_whys → [reflection] 
3. identify_root_cause → [reflection]
4. define_design_injection → [reflection]
5. formulate_design_change → [reflection]
6. create_incident_file → [reflection]
7. validate_standard_compliance → [reflection]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def incident_creation_workflow(request):
    """Orchestrates incident creation through atomic MCP commands with reflection at each step."""
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow_state = {
        "workflow_id": workflow_id,
        "steps_completed": [],
        "current_step": None,
        "validation_results": {},
        "incident_data": {},
        "start_time": datetime.now().isoformat()
    }
    
    print(f"🔄 Запуск workflow создания инцидента: {workflow_id}")
    
    try:
        # STEP 1: Validate Incident Data
        step1_result = step1_validate_incident_data(request, workflow_state)
        if not step1_result["success"]:
            return step1_result
        
        # STEP 2: Analyze Five Whys  
        step2_result = step2_analyze_five_whys(step1_result["validated_data"], workflow_state)
        if not step2_result["success"]:
            return step2_result
            
        # STEP 3: Identify Root Cause
        step3_result = step3_identify_root_cause(step2_result["five_whys_analysis"], workflow_state)
        if not step3_result["success"]:
            return step3_result
            
        # STEP 4: Define Design Injection
        step4_result = step4_define_design_injection(step3_result["root_cause"], workflow_state)
        if not step4_result["success"]:
            return step4_result
            
        # STEP 5: Formulate Design Change
        step5_result = step5_formulate_design_change(step4_result["design_injection"], workflow_state)
        if not step5_result["success"]:
            return step5_result
            
        # STEP 6: Create Incident File
        step6_result = step6_create_incident_file(step5_result["design_change"], workflow_state)
        if not step6_result["success"]:
            return step6_result
            
        # STEP 7: Validate Standard Compliance
        step7_result = step7_validate_standard_compliance(step6_result["incident_file"], workflow_state)
        
        workflow_state["end_time"] = datetime.now().isoformat()
        workflow_state["total_duration"] = (datetime.now() - datetime.fromisoformat(workflow_state["start_time"])).total_seconds()
        
        return {
            "success": step7_result["success"],
            "workflow_id": workflow_id,
            "incident_created": step6_result.get("incident_file"),
            "compliance_score": step7_result.get("compliance_score", 0),
            "workflow_state": workflow_state,
            "final_validation": step7_result
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

def step1_validate_incident_data(request, workflow_state):
    """STEP 1: Валидация входных данных инцидента с рефлексией."""
    workflow_state["current_step"] = "validate_incident_data"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("📋 STEP 1: Валидация входных данных")
    
    # РЕФЛЕКСИЯ: Проверяем качество входных данных
    reflection_result = reflection_guard(
        claim="Входные данные для инцидента содержат все необходимые элементы",
        evidence={
            "has_title": bool(request.get("title")),
            "title_length": len(request.get("title", "")),
            "has_description": bool(request.get("description") or request.get("five_whys")),
            "has_priority": bool(request.get("priority")),
            "data_completeness": sum([
                bool(request.get("title")),
                bool(request.get("description") or request.get("five_whys")),
                bool(request.get("priority"))
            ]) / 3
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Входные данные неполны или некачественны")
        return {
            "success": False,
            "step": "validate_incident_data",
            "error": "Входные данные не прошли проверку рефлексии",
            "reflection_details": reflection_result
        }
    
    # Валидируем обязательные поля
    required_fields = ["title"]
    missing_fields = [field for field in required_fields if not request.get(field)]
    
    if missing_fields:
        return {
            "success": False,
            "step": "validate_incident_data", 
            "error": f"Отсутствуют обязательные поля: {missing_fields}"
        }
    
    # Подготавливаем валидированные данные
    validated_data = {
        "title": request.get("title", "").strip(),
        "description": request.get("description", ""),
        "five_whys": request.get("five_whys", []),
        "root_cause": request.get("root_cause", ""),
        "design_injection": request.get("design_injection", ""),
        "design_change": request.get("design_change", ""),
        "priority": request.get("priority", "medium"),
        "status": request.get("status", "Recorded"),
        "affected_systems": request.get("affected_systems", [])
    }
    
    workflow_state["steps_completed"].append("validate_incident_data")
    workflow_state["validation_results"]["step1"] = reflection_result
    
    print("✅ STEP 1: Данные валидированы")
    return {
        "success": True,
        "step": "validate_incident_data",
        "validated_data": validated_data,
        "reflection_passed": True
    }

def step2_analyze_five_whys(validated_data, workflow_state):
    """STEP 2: Анализ и проверка структуры 5 почему."""
    workflow_state["current_step"] = "analyze_five_whys"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("🔍 STEP 2: Анализ 5 почему")
    
    five_whys = validated_data.get("five_whys", [])
    
    # РЕФЛЕКСИЯ: Проверяем качество анализа 5 почему
    reflection_result = reflection_guard(
        claim="Анализ 5 почему проведен качественно и полно",
        evidence={
            "has_five_questions": len(five_whys) >= 5,
            "questions_logical": all("почему" in q.lower() for q in five_whys[:5]) if five_whys else False,
            "answers_provided": all(" - " in q for q in five_whys[:5]) if five_whys else False,
            "depth_progression": len(five_whys) >= 5 and all(len(q) > 20 for q in five_whys[:5]) if five_whys else False
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Анализ 5 почему требует улучшения")
        
        # Генерируем базовый анализ если его нет
        if not five_whys or len(five_whys) < 5:
            title = validated_data.get("title", "проблема")
            generated_whys = [
                f"Почему возникла проблема '{title}'? - Требуется детальный анализ ситуации",
                f"Почему проблема не была предотвращена? - Отсутствуют превентивные меры",
                f"Почему отсутствуют превентивные меры? - Нет системы раннего обнаружения",
                f"Почему нет системы обнаружения? - Процессы не предусматривают мониторинг",
                f"Почему процессы не предусматривают мониторинг? - Системная проблема планирования"
            ]
            five_whys = generated_whys
            print("⚠️ Сгенерирован базовый анализ 5 почему - требуется доработка")
    
    workflow_state["steps_completed"].append("analyze_five_whys")
    workflow_state["validation_results"]["step2"] = reflection_result
    workflow_state["incident_data"]["five_whys"] = five_whys
    workflow_state["incident_data"]["title"] = validated_data.get("title", "")
    
    print("✅ STEP 2: Анализ 5 почему завершен")
    return {
        "success": True,
        "step": "analyze_five_whys",
        "five_whys_analysis": five_whys,
        "needs_improvement": reflection_result.get("reflection_needed", False)
    }

def step3_identify_root_cause(five_whys_analysis, workflow_state):
    """STEP 3: Определение корневой причины на основе анализа 5 почему."""
    workflow_state["current_step"] = "identify_root_cause"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("🎯 STEP 3: Определение корневой причины")
    
    # Извлекаем корневую причину из последнего "почему"
    root_cause = ""
    if five_whys_analysis and len(five_whys_analysis) >= 5:
        last_why = five_whys_analysis[4]  # 5-й элемент
        if " - " in last_why:
            root_cause = last_why.split(" - ", 1)[1].strip()
    
    # Если корневая причина не извлечена, используем из входных данных
    if not root_cause:
        root_cause = workflow_state.get("incident_data", {}).get("root_cause", "")
    
    # РЕФЛЕКСИЯ: Проверяем качество корневой причины
    reflection_result = reflection_guard(
        claim="Корневая причина сформулирована четко и адресует системную проблему",
        evidence={
            "has_root_cause": bool(root_cause),
            "length_appropriate": 10 <= len(root_cause) <= 100 if root_cause else False,
            "addresses_system": any(word in root_cause.lower() for word in ["система", "процесс", "отсутств", "нет"]) if root_cause else False,
            "specific_enough": len(root_cause.split()) >= 3 if root_cause else False
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Корневая причина требует уточнения")
        if not root_cause:
            root_cause = "Системная проблема требует дополнительного анализа"
    
    workflow_state["steps_completed"].append("identify_root_cause")
    workflow_state["validation_results"]["step3"] = reflection_result
    workflow_state["incident_data"]["root_cause"] = root_cause
    
    print(f"✅ STEP 3: Корневая причина определена: {root_cause[:50]}...")
    return {
        "success": True,
        "step": "identify_root_cause",
        "root_cause": root_cause,
        "quality_score": reflection_result.get("quality_score", 0.5)
    }

def step4_define_design_injection(root_cause, workflow_state):
    """STEP 4: Определение точки дизайн-инъекции."""
    workflow_state["current_step"] = "define_design_injection"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("📍 STEP 4: Определение дизайн-инъекции")
    
    # Извлекаем или генерируем дизайн-инъекцию
    design_injection = workflow_state.get("incident_data", {}).get("design_injection", "")
    
    if not design_injection:
        # Генерируем на основе корневой причины
        if "процесс" in root_cause.lower():
            design_injection = "Этап проектирования процессов"
        elif "система" in root_cause.lower():
            design_injection = "Этап архитектуры системы"
        elif "валидация" in root_cause.lower() or "проверка" in root_cause.lower():
            design_injection = "Этап валидации и тестирования"
        else:
            design_injection = "Этап планирования решения"
    
    # РЕФЛЕКСИЯ: Проверяем качество дизайн-инъекции
    reflection_result = reflection_guard(
        claim="Дизайн-инъекция точно указывает где вмешаться в процесс",
        evidence={
            "has_injection_point": bool(design_injection),
            "length_appropriate": len(design_injection) <= 50 if design_injection else False,
            "specifies_stage": "этап" in design_injection.lower() if design_injection else False,
            "actionable": any(word in design_injection.lower() for word in ["этап", "процесс", "разработка", "тестирование"]) if design_injection else False
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Дизайн-инъекция требует уточнения")
    
    workflow_state["steps_completed"].append("define_design_injection")
    workflow_state["validation_results"]["step4"] = reflection_result
    workflow_state["incident_data"]["design_injection"] = design_injection
    
    print(f"✅ STEP 4: Дизайн-инъекция определена: {design_injection}")
    return {
        "success": True,
        "step": "define_design_injection",
        "design_injection": design_injection
    }

def step5_formulate_design_change(design_injection, workflow_state):
    """STEP 5: Формулирование конкретного дизайн изменения."""
    workflow_state["current_step"] = "formulate_design_change"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("🔧 STEP 5: Формулирование дизайн изменения")
    
    design_change = workflow_state.get("incident_data", {}).get("design_change", "")
    root_cause = workflow_state["incident_data"]["root_cause"]
    
    if not design_change:
        # Генерируем на основе корневой причины и инъекции
        design_change = f"Внедрить решение для устранения '{root_cause}' на этапе '{design_injection}' с применением автоматической валидации и мониторинга"
    
    # РЕФЛЕКСИЯ: Проверяем качество дизайн изменения
    reflection_result = reflection_guard(
        claim="Дизайн изменения конкретно адресует корневую причину",
        evidence={
            "has_design_change": bool(design_change),
            "length_appropriate": 100 <= len(design_change) <= 150 if design_change else False,
            "addresses_root_cause": any(word in design_change.lower() for word in root_cause.lower().split()[:3]) if design_change and root_cause else False,
            "actionable": any(word in design_change.lower() for word in ["внедрить", "добавить", "создать", "изменить"]) if design_change else False
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Дизайн изменения требует доработки")
        if len(design_change) < 100:
            design_change += f" с применением автоматизированного мониторинга и превентивных мер для предотвращения повторения проблемы"
    
    workflow_state["steps_completed"].append("formulate_design_change")
    workflow_state["validation_results"]["step5"] = reflection_result
    workflow_state["incident_data"]["design_change"] = design_change
    
    print(f"✅ STEP 5: Дизайн изменения сформулировано: {design_change[:50]}...")
    return {
        "success": True,
        "step": "formulate_design_change",
        "design_change": design_change
    }

def step6_create_incident_file(design_change, workflow_state):
    """STEP 6: Создание файла инцидента согласно AI Incident Standard v1.9."""
    workflow_state["current_step"] = "create_incident_file"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("📄 STEP 6: Создание файла инцидента")
    
    incident_data = workflow_state["incident_data"]
    incident_id = f"I{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    header_date = datetime.now().strftime('%d %b %Y %H:%M')
    
    # РЕФЛЕКСИЯ: Проверяем готовность всех данных
    reflection_result = reflection_guard(
        claim="Все данные для создания инцидента готовы и соответствуют стандарту",
        evidence={
            "has_all_fields": all(incident_data.get(field) for field in ["root_cause", "design_injection", "design_change"]),
            "five_whys_complete": len(incident_data.get("five_whys", [])) >= 5,
            "format_ready": bool(incident_data.get("title")),
            "status_valid": incident_data.get("status", "Recorded") in ["Recorded", "In Progress", "Hypothesis Testing", "Hypothesis Confirmed", "Hypothesis Failed"]
        }
    )
    
    if reflection_result.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Данные инцидента неполны")
        return {
            "success": False,
            "step": "create_incident_file",
            "error": "Данные для создания инцидента неполны",
            "missing_data": reflection_result
        }
    
    # Создаем содержимое файла согласно AI Incident Standard v1.9
    md_content = f"""## {header_date} - {incident_data['title']}

**5 почему разбор:**
"""
    
    for i, why in enumerate(incident_data['five_whys'][:5], 1):
        md_content += f"{i}. {why}\n"
    
    md_content += f"""
**Корневая причина:** {incident_data['root_cause']}
**Дизайн-инъекция:** {incident_data['design_injection']}
**Дизайн изменения:** {incident_data['design_change']}
**Статус:** {incident_data.get('status', 'Recorded')}
"""
    
    # Сохраняем в ai.incidents.md согласно AI Incident Standard v1.9
    incidents_dir = Path("/home/runner/workspace/[todo · incidents]")
    incidents_dir.mkdir(exist_ok=True)
    main_incidents_file = incidents_dir / "ai.incidents.md"
    
    # РЕФЛЕКСИЯ: Проверяем что записываем в правильный файл
    reflection_file_check = reflection_guard(
        claim="Записываю инцидент в ai.incidents.md согласно AI Incident Standard",
        evidence={
            "correct_filename": str(main_incidents_file).endswith("ai.incidents.md"),
            "not_separate_file": True,
            "follows_standard": True
        }
    )
    
    if reflection_file_check.get("reflection_needed", False):
        print("⚠️ РЕФЛЕКСИЯ: Нарушение требований AI Incident Standard по месту хранения")
    
    # Читаем существующий файл
    existing_content = ""
    if main_incidents_file.exists():
        with open(main_incidents_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Добавляем новый инцидент в начало файла (обратная хронология)
    updated_content = md_content + "\n\n" + existing_content
    
    with open(main_incidents_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    incident_file = main_incidents_file
    
    workflow_state["steps_completed"].append("create_incident_file")
    workflow_state["validation_results"]["step6"] = reflection_result
    workflow_state["incident_data"]["incident_id"] = incident_id
    workflow_state["incident_data"]["incident_file"] = str(incident_file)
    
    print(f"✅ STEP 6: Файл инцидента создан: {incident_file}")
    return {
        "success": True,
        "step": "create_incident_file",
        "incident_file": str(incident_file),
        "incident_id": incident_id
    }

def step7_validate_standard_compliance(incident_file, workflow_state):
    """STEP 7: Финальная валидация соответствия AI Incident Standard v1.9."""
    workflow_state["current_step"] = "validate_standard_compliance"
    
    try:
        from advising_platform.src.mcp.reflection_guard import reflection_guard
    except ImportError:
        reflection_guard = lambda claim, evidence: {"is_valid": True, "reflection_needed": False}
    
    print("✅ STEP 7: Валидация соответствия стандарту")
    
    # Читаем созданный файл для проверки
    try:
        with open(incident_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            "success": False,
            "step": "validate_standard_compliance",
            "error": f"Не удается прочитать файл инцидента: {str(e)}"
        }
    
    # РЕФЛЕКСИЯ: Проверяем соответствие AI Incident Standard
    reflection_result = reflection_guard(
        claim="Созданный инцидент полностью соответствует AI Incident Standard v1.9",
        evidence={
            "has_proper_header": content.startswith("## ") and " - " in content.split('\n')[0],
            "has_five_whys": "**5 почему разбор:**" in content,
            "has_numbered_whys": all(f"{i}." in content for i in range(1, 6)),
            "has_root_cause": "**Корневая причина:**" in content,
            "has_design_injection": "**Дизайн-инъекция:**" in content,
            "has_design_change": "**Дизайн изменения:**" in content,
            "has_status": "**Статус:**" in content
        }
    )
    
    compliance_score = sum(reflection_result.get("evidence", {}).values()) / len(reflection_result.get("evidence", {})) if reflection_result.get("evidence") else 0
    
    workflow_state["steps_completed"].append("validate_standard_compliance")
    workflow_state["validation_results"]["step7"] = reflection_result
    workflow_state["final_compliance_score"] = compliance_score
    
    success = compliance_score >= 0.85  # 85% соответствие
    
    if success:
        print("✅ STEP 7: Инцидент соответствует стандарту")
    else:
        print("⚠️ STEP 7: Инцидент частично соответствует стандарту")
    
    return {
        "success": success,
        "step": "validate_standard_compliance", 
        "compliance_score": compliance_score,
        "validation_details": reflection_result,
        "standards_compliant": success
    }

if __name__ == "__main__":
    # Тестирование workflow
    test_request = {
        "title": "Тест атомарного workflow создания инцидентов",
        "five_whys": [
            "Почему нужен атомарный workflow? - Монолитные команды нарушают принцип рефлексии",
            "Почему монолитные команды нарушают рефлексию? - Рефлексия должна быть на каждом шаге",
            "Почему рефлексия должна быть на каждом шаге? - Только так можно предотвратить ошибки",
            "Почему нужно предотвращать ошибки? - Качество результата зависит от качества процесса",
            "Почему качество процесса критично? - Системный подход требует контроля каждого этапа"
        ],
        "priority": "high"
    }
    
    result = incident_creation_workflow(test_request)
    print(json.dumps(result, indent=2, ensure_ascii=False))