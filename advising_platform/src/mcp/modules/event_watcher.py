"""
MCP Module: Event Watcher
Мониторинг изменений todo.md для автозапуска триггеров
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import hashlib


def mcp_event_watcher(target_file: str = "[todo · incidents]/duck.todo.md") -> Dict[str, Any]:
    """
    MCP команда: event-watcher
    Мониторинг изменений файлов для автозапуска триггеров
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-event-watcher",
        "timestamp": datetime.now().isoformat(),
        "target_file": target_file,
        "changes_detected": [],
        "triggers_fired": [],
        "success": False
    }
    
    try:
        # Проверяем изменения
        changes = _detect_file_changes(target_file)
        result["changes_detected"] = changes
        
        # Запускаем триггеры
        if changes:
            triggers = _fire_triggers(changes)
            result["triggers_fired"] = triggers
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _detect_file_changes(file_path: str) -> list[dict[str, Any]]:
    """Обнаруживает изменения в файле"""
    
    target = Path(file_path)
    if not target.exists():
        return []
    
    current_hash = hashlib.md5(target.read_bytes()).hexdigest()
    
    # Проверяем с последним известным хешем
    hash_file = Path(f"{file_path}.hash")
    
    if hash_file.exists():
        last_hash = hash_file.read_text().strip()
        if current_hash != last_hash:
            hash_file.write_text(current_hash)
            return [{"type": "file_modified", "file": file_path, "hash": current_hash}]
    else:
        hash_file.write_text(current_hash)
        return [{"type": "file_created", "file": file_path, "hash": current_hash}]
    
    return []


def _fire_triggers(changes: list[dict[str, Any]]) -> list[str]:
    """Запускает триггеры на основе изменений"""
    
    triggers = []
    
    for change in changes:
        if change["type"] in ["file_modified", "file_created"]:
            triggers.append("task_completion_check")
            triggers.append("status_update")
    
    return triggers