"""
MCP Module: Read Critical Instructions
Автоматически читает и применяет критические инструкции из todo.md и incidents.md

Интегрируется во все MCP команды для соблюдения критических требований.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def mcp_read_critical_instructions() -> Dict[str, Any]:
    """
    MCP команда: read-critical-instructions
    Читает критические инструкции из todo.md и incidents.md
    
    Returns:
        Все критические инструкции для соблюдения в MCP командах
    """
    
    critical_instructions = {
        "todo_instructions": [],
        "incidents_instructions": [],
        "combined_rules": [],
        "auto_triggers": [],
        "file_sources": []
    }
    
    # Читаем критические инструкции из todo.md
    todo_file = Path("[todo · incidents]/duck.todo.md")
    if todo_file.exists():
        todo_content = todo_file.read_text(encoding='utf-8')
        todo_critical = _extract_critical_sections(todo_content, "todo")
        critical_instructions["todo_instructions"] = todo_critical
        critical_instructions["file_sources"].append(str(todo_file))
    
    # Читаем критические инструкции из incidents.md
    incidents_file = Path("[todo · incidents]/ai.incidents.md")
    if incidents_file.exists():
        incidents_content = incidents_file.read_text(encoding='utf-8')
        incidents_critical = _extract_critical_sections(incidents_content, "incidents")
        critical_instructions["incidents_instructions"] = incidents_critical
        critical_instructions["file_sources"].append(str(incidents_file))
    
    # Объединяем все критические правила
    all_rules = []
    all_rules.extend(critical_instructions["todo_instructions"])
    all_rules.extend(critical_instructions["incidents_instructions"])
    critical_instructions["combined_rules"] = all_rules
    
    # Извлекаем авто-триггеры
    auto_triggers = _extract_auto_triggers(all_rules)
    critical_instructions["auto_triggers"] = auto_triggers
    
    return {
        "command": "mcp-read-critical-instructions",
        "timestamp": datetime.now().isoformat(),
        "critical_instructions": critical_instructions,
        "rules_count": len(all_rules),
        "auto_triggers_count": len(auto_triggers),
        "sources_read": critical_instructions["file_sources"],
        "compliance_required": True
    }


def _extract_critical_sections(content: str, source_type: str) -> List[Dict[str, Any]]:
    """Извлекает критические секции из контента файла"""
    
    critical_sections = []
    
    # Ищем секции с критическими инструкциями
    critical_patterns = [
        r"⚠️.*?КРИТИЧЕСКИЕ.*?ИНСТРУКЦИИ.*?:(.*?)(?=##|---|\n\n[A-Z])",
        r"🚨.*?ОБЯЗАТЕЛЬНО.*?:(.*?)(?=##|---|\n\n[A-Z])",
        r"ВАЖНО.*?:(.*?)(?=##|---|\n\n[A-Z])",
        r"\*\*ПРИОРИТЕТ.*?\*\*.*?:(.*?)(?=##|---|\n\n[A-Z])"
    ]
    
    for pattern in critical_patterns:
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            instruction_text = match.group(1).strip()
            
            # Извлекаем отдельные правила из текста
            rules = _parse_instruction_rules(instruction_text)
            
            for rule in rules:
                critical_sections.append({
                    "source": source_type,
                    "type": "critical_instruction",
                    "rule": rule,
                    "extracted_from": pattern,
                    "requires_compliance": True
                })
    
    return critical_sections


def _parse_instruction_rules(instruction_text: str) -> List[str]:
    """Парсит текст инструкций на отдельные правила"""
    
    rules = []
    
    # Ищем пронумерованные пункты
    numbered_rules = re.findall(r'\d+\.\s*\*\*(.*?)\*\*', instruction_text)
    rules.extend(numbered_rules)
    
    # Ищем пункты с дефисами
    dash_rules = re.findall(r'-\s*`(.*?)`', instruction_text)
    rules.extend(dash_rules)
    
    # Ищем общие правила
    general_rules = re.findall(r'>\s*(.*?)(?=\n|$)', instruction_text)
    rules.extend([rule.strip() for rule in general_rules if rule.strip()])
    
    return rules


def _extract_auto_triggers(rules: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Извлекает автоматические триггеры из правил"""
    
    auto_triggers = []
    
    for rule_data in rules:
        rule = rule_data.get("rule", "")
        
        # Ищем паттерны автоматических действий
        trigger_patterns = [
            (r"автоматически.*?создавай.*?инцидент", "auto_create_incident"),
            (r"сразу.*?под.*?критической.*?секции", "place_after_critical"),
            (r"обязательно.*?синхронизируй.*?кеш", "auto_sync_cache"),
            (r"используй.*?MCP.*?команды", "use_mcp_commands"),
            (r"читай.*?критические.*?секции", "read_critical_sections")
        ]
        
        for pattern, trigger_type in trigger_patterns:
            if re.search(pattern, rule, re.IGNORECASE):
                auto_triggers.append({
                    "trigger_type": trigger_type,
                    "rule": rule,
                    "source": rule_data.get("source", "unknown"),
                    "auto_execute": True
                })
    
    return auto_triggers


def apply_critical_instructions_to_mcp_command(command_name: str, command_params: Dict[str, Any]) -> Dict[str, Any]:
    """Применяет критические инструкции к MCP команде перед выполнением"""
    
    # Читаем критические инструкции
    instructions_result = mcp_read_critical_instructions()
    critical_rules = instructions_result["critical_instructions"]["combined_rules"]
    auto_triggers = instructions_result["critical_instructions"]["auto_triggers"]
    
    applied_modifications = []
    
    # Применяем правила специфичные для команды
    if command_name in ["mcp_root_cause_analysis", "mcp_create_incident"]:
        # Проверяем правила для инцидентов
        for rule_data in critical_rules:
            rule = rule_data.get("rule", "")
            
            if "инцидент" in rule.lower() and "сразу под" in rule.lower():
                command_params["place_after_critical_section"] = True
                applied_modifications.append("place_after_critical_section")
            
            if "MCP команды" in rule and "вместо прямого" in rule:
                command_params["use_mcp_functions"] = True
                applied_modifications.append("use_mcp_functions")
            
            if "синхронизируй кеш" in rule.lower():
                command_params["auto_sync_cache"] = True
                applied_modifications.append("auto_sync_cache")
    
    # Применяем автоматические триггеры
    for trigger in auto_triggers:
        if trigger["auto_execute"]:
            trigger_type = trigger["trigger_type"]
            
            if trigger_type == "read_critical_sections":
                command_params["critical_instructions_read"] = True
                applied_modifications.append("critical_instructions_loaded")
            
            if trigger_type == "auto_create_incident" and command_name == "mcp_root_cause_analysis":
                command_params["auto_create_incident"] = True
                applied_modifications.append("auto_incident_creation")
    
    return {
        "modified_params": command_params,
        "applied_modifications": applied_modifications,
        "critical_rules_applied": len([r for r in critical_rules if any(mod in r.get("rule", "") for mod in applied_modifications)]),
        "compliance_status": "ENFORCED"
    }


def execute_critical_instructions_demo():
    """Демонстрация чтения критических инструкций"""
    
    print("📋 MCP Read Critical Instructions")
    print("=" * 40)
    
    # Читаем критические инструкции
    result = mcp_read_critical_instructions()
    
    critical = result['critical_instructions']
    print(f"📁 Источники: {len(result['sources_read'])}")
    print(f"📋 Правил извлечено: {result['rules_count']}")
    print(f"🤖 Авто-триггеров: {result['auto_triggers_count']}")
    
    print(f"\n🔥 Критические правила:")
    for i, rule_data in enumerate(critical['combined_rules'][:3], 1):
        print(f"  {i}. [{rule_data['source']}] {rule_data['rule'][:60]}...")
    
    print(f"\n⚡ Авто-триггеры:")
    for trigger in critical['auto_triggers'][:3]:
        print(f"  • {trigger['trigger_type']}: {trigger['rule'][:50]}...")
    
    # Демонстрация применения к команде
    print(f"\n🔧 Применение к mcp_root_cause_analysis:")
    demo_params = {"analysis_depth": "5_whys"}
    applied = apply_critical_instructions_to_mcp_command("mcp_root_cause_analysis", demo_params)
    
    print(f"✅ Модификаций применено: {len(applied['applied_modifications'])}")
    for mod in applied['applied_modifications']:
        print(f"  • {mod}")
    
    return result


if __name__ == "__main__":
    # Запуск демонстрации
    result = execute_critical_instructions_demo()
    
    # Сохраняем результат
    output_path = Path("critical_instructions_extracted.json")
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n💾 Критические инструкции сохранены в: {output_path}")