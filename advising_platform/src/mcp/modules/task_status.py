"""
MCP Module: Task Status
Получение статуса всех задач
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def mcp_task_status(todo_file: str = "[todo · incidents]/duck.todo.md") -> Dict[str, Any]:
    """
    MCP команда: task-status
    Возвращает статус всех задач в проекте
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-task-status",
        "timestamp": datetime.now().isoformat(),
        "task_summary": {},
        "tasks_by_priority": {},
        "success": False
    }
    
    try:
        # Читаем todo файл
        todo_path = Path(todo_file)
        if not todo_path.exists():
            result["error"] = f"Todo file not found: {todo_file}"
            return result
        
        content = todo_path.read_text(encoding='utf-8')
        
        # Анализируем статус задач
        summary = _analyze_task_status(content)
        result["task_summary"] = summary["summary"]
        result["tasks_by_priority"] = summary["by_priority"]
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _analyze_task_status(content: str) -> Dict[str, Any]:
    """Анализирует статус всех задач"""
    
    summary = {
        "total_tasks": 0,
        "completed": 0,
        "in_progress": 0,
        "pending": 0,
        "completion_rate": 0
    }
    
    by_priority = {
        "BLOCKER": [],
        "ALARM": [],
        "ASAP": []
    }
    
    lines = content.split('\n')
    
    for line in lines:
        if 'TASK_' in line:
            summary["total_tasks"] += 1
            
            # Определяем статус
            if "COMPLETED" in line:
                summary["completed"] += 1
            elif "IN_PROGRESS" in line:
                summary["in_progress"] += 1
            else:
                summary["pending"] += 1
            
            # Определяем приоритет
            priority = "ASAP"  # по умолчанию
            if "BLOCKER" in line:
                priority = "BLOCKER"
            elif "ALARM" in line:
                priority = "ALARM"
            
            task_info = {
                "line": line.strip(),
                "status": "COMPLETED" if "COMPLETED" in line else "IN_PROGRESS" if "IN_PROGRESS" in line else "PENDING"
            }
            
            by_priority[priority].append(task_info)
    
    # Вычисляем процент завершения
    if summary["total_tasks"] > 0:
        summary["completion_rate"] = round((summary["completed"] / summary["total_tasks"]) * 100, 1)
    
    return {
        "summary": summary,
        "by_priority": by_priority
    }