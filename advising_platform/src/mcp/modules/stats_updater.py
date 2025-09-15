"""
MCP Module: Stats Updater
Обновление статистики в header todo.md
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def mcp_stats_updater(target_file: str = "[todo · incidents]/duck.todo.md") -> Dict[str, Any]:
    """
    MCP команда: stats-updater
    Обновляет статистику в заголовке todo.md файла
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-stats-updater",
        "timestamp": datetime.now().isoformat(),
        "stats_updated": {},
        "file_updated": target_file,
        "success": False
    }
    
    try:
        # Собираем статистику
        stats = _collect_project_stats()
        result["stats_updated"] = stats
        
        # Обновляем файл
        _update_file_header(target_file, stats)
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _collect_project_stats() -> Dict[str, Any]:
    """Собирает статистику проекта"""
    
    stats = {
        "total_modules": 0,
        "mcp_commands": 0,
        "completed_tasks": 0,
        "active_incidents": 0,
        "last_updated": datetime.now().strftime('%d %b %Y')
    }
    
    # Подсчет MCP модулей
    modules_path = Path("advising_platform/src/mcp/modules")
    if modules_path.exists():
        modules = list(modules_path.glob("*.py"))
        stats["total_modules"] = len([m for m in modules if not m.name.startswith("__")])
    
    # Подсчет MCP команд
    stats["mcp_commands"] = 20  # из README изображения
    
    # Подсчет завершенных задач
    duck_todo = Path("[todo · incidents]/duck.todo.md")
    if duck_todo.exists():
        content = duck_todo.read_text(encoding='utf-8')
        stats["completed_tasks"] = content.count("✅")
    
    # Подсчет активных инцидентов
    incidents_file = Path("[todo · incidents]/ai.incidents.md")
    if incidents_file.exists():
        content = incidents_file.read_text(encoding='utf-8')
        stats["active_incidents"] = content.count("**Статус:** ACTIVE")
    
    return stats


def _update_file_header(file_path: str, stats: Dict[str, Any]) -> None:
    """Обновляет заголовок файла статистикой"""
    
    target = Path(file_path)
    if not target.exists():
        return
    
    content = target.read_text(encoding='utf-8')
    
    # Обновляем дату обновления
    content = content.replace(
        "**Обновлено**: 27 мая 2025",
        f"**Обновлено**: {stats['last_updated']}"
    )
    
    # Добавляем статистику в заголовок если её нет
    stats_section = f"""
**📊 Статистика проекта:**
- Модулей: {stats['total_modules']}
- MCP команд: {stats['mcp_commands']}
- Завершенных задач: {stats['completed_tasks']}
- Активных инцидентов: {stats['active_incidents']}

"""
    
    if "**📊 Статистика проекта:**" not in content:
        # Вставляем после заголовка версии
        version_line = "**Версия**: "
        if version_line in content:
            version_end = content.find('\n', content.find(version_line)) + 1
            content = content[:version_end] + stats_section + content[version_end:]
    
    target.write_text(content, encoding='utf-8')