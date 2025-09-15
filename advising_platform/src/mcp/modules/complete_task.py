"""
MCP Module: Complete Task
Отметка задачи как завершенной
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def mcp_complete_task(task_id: str, todo_file: str = "[todo · incidents]/duck.todo.md") -> Dict[str, Any]:
    """
    MCP команда: complete-task
    Отмечает задачу как завершенную в todo файле
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-complete-task",
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "task_completed": False,
        "success": False
    }
    
    try:
        # Читаем todo файл
        todo_path = Path(todo_file)
        if not todo_path.exists():
            result["error"] = f"Todo file not found: {todo_file}"
            return result
        
        content = todo_path.read_text(encoding='utf-8')
        
        # Обновляем статус задачи
        updated_content = _mark_task_completed(content, task_id)
        
        if updated_content != content:
            todo_path.write_text(updated_content, encoding='utf-8')
            result["task_completed"] = True
            result["success"] = True
        else:
            result["message"] = f"Task {task_id} not found or already completed"
            result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _mark_task_completed(content: str, task_id: str) -> str:
    """Отмечает задачу как завершенную в содержимом"""
    
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if f"TASK_{task_id}" in line:
            # Заменяем статус на COMPLETED
            if "IN_PROGRESS" in line:
                line = line.replace("IN_PROGRESS", "COMPLETED")
            elif "PENDING" in line:
                line = line.replace("PENDING", "COMPLETED")
            else:
                # Добавляем статус если его нет
                line = line + " - COMPLETED"
            
            # Добавляем дату завершения
            completion_date = datetime.now().strftime('%d %b %Y')
            if "COMPLETED" in line and completion_date not in line:
                line = line + f" ({completion_date})"
        
        updated_lines.append(line)
    
    return '\n'.join(updated_lines)