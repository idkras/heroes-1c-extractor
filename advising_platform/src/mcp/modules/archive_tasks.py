"""
MCP Module: Archive Tasks
Архивация завершенных задач в archive/*.md файлы
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def mcp_archive_tasks(task_source: str = "[todo · incidents]/duck.todo.md") -> Dict[str, Any]:
    """
    MCP команда: archive-tasks
    Архивирует завершенные задачи в archive/ директорию
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-archive-tasks",
        "timestamp": datetime.now().isoformat(),
        "tasks_archived": [],
        "archive_files_created": [],
        "success": False
    }
    
    try:
        # Находим завершенные задачи
        completed_tasks = _find_completed_tasks(task_source)
        
        # Архивируем задачи
        if completed_tasks:
            archived = _archive_completed_tasks(completed_tasks)
            result["tasks_archived"] = archived["tasks"]
            result["archive_files_created"] = archived["files"]
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _find_completed_tasks(source_file: str) -> List[Dict[str, Any]]:
    """Находит завершенные задачи в файле"""
    
    source = Path(source_file)
    if not source.exists():
        return []
    
    content = source.read_text(encoding='utf-8')
    completed_tasks = []
    
    # Ищем задачи с маркерами завершения
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '✅' in line or 'COMPLETED' in line or 'DONE' in line:
            completed_tasks.append({
                "line_number": i + 1,
                "content": line.strip(),
                "context": _get_task_context(lines, i)
            })
    
    return completed_tasks


def _get_task_context(lines: List[str], task_line: int) -> Dict[str, Any]:
    """Получает контекст задачи (заголовок секции, описание)"""
    
    context = {"section": "", "description": ""}
    
    # Ищем заголовок секции выше
    for i in range(task_line - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith('#'):
            context["section"] = line
            break
    
    # Получаем описание из следующих строк
    description_lines = []
    for i in range(task_line + 1, min(task_line + 4, len(lines))):
        line = lines[i].strip()
        if line and not line.startswith('#') and not line.startswith('-'):
            description_lines.append(line)
    
    context["description"] = ' '.join(description_lines)
    return context


def _archive_completed_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Архивирует завершенные задачи"""
    
    # Создаем директорию archive если не существует
    archive_dir = Path("[todo · incidents]/archive")
    archive_dir.mkdir(exist_ok=True)
    
    # Группируем задачи по дате
    today = datetime.now().strftime('%Y-%m-%d')
    archive_file = archive_dir / f"completed_tasks_{today}.md"
    
    # Создаем содержимое архива
    archive_content = f"""# Завершенные задачи - {today}

## Архивировано: {datetime.now().strftime('%d %b %Y %H:%M')}

"""
    
    archived_tasks = []
    for task in tasks:
        task_entry = f"""### {task['context']['section']}
- {task['content']}
- Описание: {task['context']['description']}
- Строка: {task['line_number']}

"""
        archive_content += task_entry
        archived_tasks.append({
            "content": task['content'],
            "section": task['context']['section']
        })
    
    # Сохраняем архив
    archive_file.write_text(archive_content, encoding='utf-8')
    
    return {
        "tasks": archived_tasks,
        "files": [str(archive_file)]
    }