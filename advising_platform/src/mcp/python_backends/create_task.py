#!/usr/bin/env python3
"""
MCP Backend: create_task

JTBD: Я хочу создавать структурированные задачи через MCP команды,
чтобы все задачи имели единый формат и автоматически логировались.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def create_task(request):
    """Создает структурированную задачу."""
    
    try:
        from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation
    except ImportError:
        log_mcp_operation = lambda *args: None
    
    start_time = datetime.now()
    
    try:
        title = request.get("title", "")
        description = request.get("description", "")
        priority = request.get("priority", "medium")
        assignee = request.get("assignee", "development_team")
        due_date = request.get("due_date", "")
        labels = request.get("labels", [])
        
        # Генерируем ID задачи
        task_id = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем структуру задачи
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "open",
            "assignee": assignee,
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "labels": labels,
            "estimated_hours": request.get("estimated_hours", 0),
            "actual_hours": 0,
            "completion_percentage": 0,
            "related_incidents": request.get("related_incidents", []),
            "acceptance_criteria": request.get("acceptance_criteria", [])
        }
        
        # Сохраняем задачу
        tasks_dir = Path("/home/runner/workspace/[todo · incidents]")
        task_file = tasks_dir / f"task_{task_id}.json"
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        # Логируем операцию
        duration = (datetime.now() - start_time).total_seconds() * 1000
        log_mcp_operation(
            'create-task',
            {"title": title, "priority": priority},
            {"success": True, "task_created": True, "task_id": task_id},
            duration
        )
        
        # Обновляем документацию для критических задач
        try:
            from advising_platform.src.mcp.modules.documentation_validator import update_documentation
            update_documentation("create_task", {"task_id": task_id, "title": title})
        except ImportError:
            pass  # Документация не критична для базовой функциональности
        
        return {
            "success": True,
            "task": task,
            "task_file": str(task_file),
            "message": f"Задача {task_id} создана успешно"
        }
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        log_mcp_operation(
            'create-task',
            request,
            {"success": False, "error": str(e)},
            duration
        )
        
        return {
            "success": False,
            "error": str(e),
            "message": "Ошибка при создании задачи"
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        request_data = json.loads(sys.argv[1])
        result = create_task(request_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("CreateTask MCP command - use with task JSON input")