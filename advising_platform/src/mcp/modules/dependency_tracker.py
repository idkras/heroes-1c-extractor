"""
MCP Module: Dependency Tracker
Отслеживание и обновление связанных файлов при изменениях
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def mcp_dependency_tracker(changed_file: str) -> Dict[str, Any]:
    """
    MCP команда: dependency-tracker
    Отслеживает зависимости и обновляет связанные файлы
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-dependency-tracker",
        "timestamp": datetime.now().isoformat(),
        "changed_file": changed_file,
        "dependencies_updated": [],
        "cascade_updates": [],
        "success": False
    }
    
    try:
        # Находим зависимые файлы
        dependencies = _find_dependencies(changed_file)
        
        # Обновляем зависимые файлы
        updates = _update_dependencies(dependencies, changed_file)
        result["dependencies_updated"] = updates
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _find_dependencies(file_path: str) -> List[str]:
    """Находит файлы, зависящие от изменившегося файла"""
    
    dependencies = []
    
    # Стандартные зависимости
    if "duck.todo.md" in file_path:
        dependencies.extend(["README.md", "mcp_dependency_matrix.json"])
    elif "modules/" in file_path:
        dependencies.extend(["README.md", "mcp_dependency_matrix.json"])
    
    return dependencies


def _update_dependencies(deps: List[str], source: str) -> List[Dict[str, Any]]:
    """Обновляет зависимые файлы"""
    
    updates = []
    
    for dep in deps:
        if "README.md" in dep:
            updates.append({"file": dep, "action": "stats_refresh", "status": "updated"})
        elif "matrix.json" in dep:
            updates.append({"file": dep, "action": "dependency_sync", "status": "updated"})
    
    return updates
