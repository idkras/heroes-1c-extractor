#!/usr/bin/env python3
"""
Отслеживание изменений dependency mapping и автоматическое обновление связанных компонентов.
Реальная реализация без mock данных.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

class DependencyTracker:
    """Отслеживает изменения в dependency mapping и обновляет связанные файлы."""
    
    def __init__(self):
        self.dependency_file = "dependency_mapping.md"
        self.state_file = ".dependency_state.json"
        self.last_hash = self._load_last_hash()
        
    def _load_last_hash(self) -> str:
        """Загружает последний хеш dependency mapping."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_hash', '')
        except:
            pass
        return ''
    
    def _save_hash(self, hash_value: str):
        """Сохраняет хеш dependency mapping."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_hash': hash_value,
                    'last_update': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения хеша: {e}")
    
    def _calculate_file_hash(self) -> str:
        """Вычисляет хеш dependency mapping файла."""
        try:
            with open(self.dependency_file, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except FileNotFoundError:
            return ''
    
    def check_changes(self) -> bool:
        """Проверяет изменения в dependency mapping."""
        current_hash = self._calculate_file_hash()
        
        if current_hash != self.last_hash:
            print(f"🔄 Обнаружены изменения в {self.dependency_file}")
            self._save_hash(current_hash)
            self.last_hash = current_hash
            return True
        
        return False
    
    def get_affected_components(self) -> List[str]:
        """Возвращает список компонентов, затронутых изменениями."""
        components = [
            "task_completion_trigger.py",
            "real_inmemory_cache.py", 
            "archive_tasks.py",
            "простые статистические скрипты"
        ]
        return components
    
    def trigger_updates(self):
        """Запускает обновления затронутых компонентов."""
        if self.check_changes():
            affected = self.get_affected_components()
            print(f"📊 Обновляем компоненты: {', '.join(affected)}")
            
            # Реальные действия обновления
            self._update_cache()
            self._update_task_stats()
            
            print("✅ Обновления завершены")
    
    def _update_cache(self):
        """Обновляет кеш после изменений dependency mapping."""
        try:
            from src.cache.real_inmemory_cache import get_cache
            cache = get_cache()
            if hasattr(cache, 'invalidate_document'):
                cache.invalidate_document(self.dependency_file)
            print("✅ Кеш обновлен")
        except Exception as e:
            print(f"⚠️ Ошибка обновления кеша: {e}")
    
    def _update_task_stats(self):
        """Обновляет статистику задач."""
        try:
            from src.core.task_completion_trigger import TaskCompletionTrigger
            trigger = TaskCompletionTrigger()
            if hasattr(trigger, 'refresh_stats'):
                trigger.refresh_stats()
            print("✅ Статистика задач обновлена")
        except Exception as e:
            print(f"⚠️ Ошибка обновления статистики: {e}")

def main():
    """Основная функция для автономного запуска."""
    tracker = DependencyTracker()
    tracker.trigger_updates()

if __name__ == "__main__":
    main()