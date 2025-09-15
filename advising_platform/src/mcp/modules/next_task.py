"""
MCP Module: Next Task
Получение следующей задачи из todo списка
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def mcp_next_task(todo_file: str = "[todo · incidents]/duck.todo.md") -> Dict[str, Any]:
    """
    MCP команда: next-task
    Получает следующую задачу с высшим приоритетом из todo списка
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-next-task",
        "timestamp": datetime.now().isoformat(),
        "next_task": {},
        "priority_queue": [],
        "success": False
    }
    
    try:
        # Читаем todo файл
        todo_path = Path(todo_file)
        if not todo_path.exists():
            result["error"] = f"Todo file not found: {todo_file}"
            return result
        
        content = todo_path.read_text(encoding='utf-8')
        
        # Парсим задачи по приоритетам
        tasks = _parse_tasks_by_priority(content)
        result["priority_queue"] = tasks
        
        # Выбираем следующую задачу
        if tasks:
            next_task = tasks[0]
            result["next_task"] = next_task
            result["success"] = True
        else:
            result["message"] = "No pending tasks found"
            result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _parse_tasks_by_priority(content: str) -> list:
    """Парсит задачи из содержимого todo файла по приоритетам"""
    
    tasks = []
    lines = content.split('\n')
    
    current_task = None
    
    for line in lines:
        line = line.strip()
        
        # Ищем задачи по маркерам
        if 'TASK_' in line and ('ALARM' in line or 'ASAP' in line or 'BLOCKER' in line):
            if current_task:
                tasks.append(current_task)
            
            current_task = {
                "id": line.split('_')[1] if '_' in line else "unknown",
                "title": line,
                "priority": "ALARM" if "ALARM" in line else "ASAP" if "ASAP" in line else "BLOCKER",
                "status": "IN_PROGRESS" if "IN_PROGRESS" in line else "PENDING",
                "description": "",
                "requirements": []
            }
        
        elif current_task and line.startswith('**Описание**:'):
            current_task["description"] = line.replace('**Описание**:', '').strip()
        
        elif current_task and line.startswith('-') and line.strip() != '-':
            current_task["requirements"].append(line.strip('- '))
    
    # Добавляем последнюю задачу
    if current_task:
        tasks.append(current_task)
    
    # Сортируем по приоритету: BLOCKER -> ALARM -> ASAP
    priority_order = {"BLOCKER": 0, "ALARM": 1, "ASAP": 2}
    tasks.sort(key=lambda x: priority_order.get(x["priority"], 99))
    
    return tasks