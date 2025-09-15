"""
Маршруты API для информации о реорганизации проекта.
"""

from flask import Blueprint, jsonify
import os
from datetime import datetime

reorganization_blueprint = Blueprint('reorganization', __name__)

@reorganization_blueprint.route('/reorganization/status', methods=['GET'])
def get_reorganization_status():
    """
    Получение статуса реорганизации файловой структуры.
    
    Возвращает информацию о реорганизации файлов и директорий в проекте.
    """
    # Список завершенных задач
    completed_tasks = [
        {
            "name": "process_incidents.py", 
            "old_path": "/process_incidents.py",
            "new_path": "advising_platform/scripts/incidents/process_incidents.py",
            "status": "completed"
        },
        {
            "name": "test_bidirectional_sync.py", 
            "old_path": "/test_bidirectional_sync.py",
            "new_path": "advising_platform/scripts/tests/test_bidirectional_sync.py",
            "status": "completed"
        },
        {
            "name": "bidirectional_sync_test_results.json", 
            "old_path": "/bidirectional_sync_test_results.json",
            "new_path": "advising_platform/data/test_results/bidirectional_sync_test_results.json",
            "status": "completed"
        },
        {
            "name": "cache_validation_report.json", 
            "old_path": "/cache_validation_report.json",
            "new_path": "advising_platform/data/test_results/cache_validation_report.json",
            "status": "completed"
        },
        {
            "name": "Логи", 
            "description": "Перенос лог-файлов в структурированную директорию",
            "old_path": "/*.log",
            "new_path": "advising_platform/data/logs/",
            "status": "completed"
        },
        {
            "name": "API Routes", 
            "description": "Реорганизация маршрутов API",
            "old_path": "advising_platform/src/api/*.py",
            "new_path": "advising_platform/src/api/routes/",
            "status": "in_progress",
            "progress": 25
        }
    ]
    
    # Статистика реорганизации
    completion_percentage = sum([100 if task["status"] == "completed" else task.get("progress", 0) for task in completed_tasks]) / len(completed_tasks)
    
    return jsonify({
        "status": "in_progress" if completion_percentage < 100 else "completed",
        "completion_percentage": round(completion_percentage, 2),
        "started_at": "2025-05-15T21:00:00Z",
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tasks": completed_tasks,
        "files_relocated": len([task for task in completed_tasks if task["status"] == "completed"]),
        "readme_files_created": 5,
        "maintainer": "AI Assistant"
    })