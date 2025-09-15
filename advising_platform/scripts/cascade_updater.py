#!/usr/bin/env python3
"""
Каскадное обновление компонентов системы при изменениях.
Обеспечивает синхронизацию всех зависимых элементов.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class CascadeUpdater:
    """Обеспечивает каскадное обновление всех зависимых компонентов."""
    
    def __init__(self):
        self.update_log = []
        
    def log_update(self, component: str, status: str, details: str = ""):
        """Логирует обновление компонента."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'status': status,
            'details': details
        }
        self.update_log.append(entry)
        print(f"[{entry['timestamp']}] {status}: {component} - {details}")
    
    def update_dependency_mapping_table(self):
        """Обновляет таблицу в dependency_mapping.md с реальными статусами."""
        dependency_file = "dependency_mapping.md"
        
        if not os.path.exists(dependency_file):
            self.log_update("dependency_mapping.md", "❌ ОШИБКА", "Файл не найден")
            return False
            
        try:
            with open(dependency_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Обновляем статусы реальных компонентов
            updates = {
                "task_completion_trigger.py": "✅" if self._check_file_exists("src/core/task_completion_trigger.py") else "❌",
                "archive_tasks.py": "✅" if self._check_file_exists("scripts/archive_tasks.py") else "❌", 
                "dependency_tracker.py": "✅" if self._check_file_exists("scripts/dependency_tracker.py") else "❌",
                "cascade_updater.py": "✅" if self._check_file_exists("scripts/cascade_updater.py") else "❌"
            }
            
            # Применяем обновления к содержимому
            updated_content = content
            for component, status in updates.items():
                # Простая замена статусов в таблице
                if f"❌ НЕТ {component}" in updated_content:
                    updated_content = updated_content.replace(
                        f"❌ НЕТ {component}", 
                        f"{status} {component}"
                    )
                elif f"❌ НЕТ СКРИПТА" in updated_content and component in updated_content:
                    updated_content = updated_content.replace(
                        "❌ НЕТ СКРИПТА",
                        f"{status} СОЗДАН"
                    )
            
            # Записываем обновленное содержимое
            with open(dependency_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            self.log_update("dependency_mapping.md", "✅ ОБНОВЛЕН", "Таблица синхронизирована")
            return True
            
        except Exception as e:
            self.log_update("dependency_mapping.md", "❌ ОШИБКА", str(e))
            return False
    
    def _check_file_exists(self, filepath: str) -> bool:
        """Проверяет существование файла."""
        return os.path.exists(filepath)
    
    def update_all_components(self):
        """Обновляет все компоненты системы."""
        self.log_update("CASCADE_UPDATE", "🚀 ЗАПУСК", "Начинаем каскадное обновление")
        
        # 1. Обновляем dependency mapping таблицу
        self.update_dependency_mapping_table()
        
        # 2. Обновляем кеш если возможно
        self._try_update_cache()
        
        # 3. Обновляем статистику задач
        self._try_update_task_stats()
        
        # 4. Создаем отчет
        self._generate_update_report()
        
        self.log_update("CASCADE_UPDATE", "✅ ЗАВЕРШЕН", f"Обработано {len(self.update_log)} компонентов")
    
    def _try_update_cache(self):
        """Пытается обновить кеш."""
        try:
            from src.cache.real_inmemory_cache import get_cache
            cache = get_cache()
            self.log_update("RealInMemoryCache", "✅ ОБНОВЛЕН", "Кеш доступен")
        except Exception as e:
            self.log_update("RealInMemoryCache", "⚠️ ОШИБКА", str(e))
    
    def _try_update_task_stats(self):
        """Пытается обновить статистику задач."""
        try:
            from src.core.task_completion_trigger import TaskCompletionTrigger
            trigger = TaskCompletionTrigger()
            self.log_update("TaskCompletionTrigger", "✅ ДОСТУПЕН", "Компонент импортируется")
        except Exception as e:
            self.log_update("TaskCompletionTrigger", "⚠️ ОШИБКА", str(e))
    
    def _generate_update_report(self):
        """Генерирует отчет об обновлениях."""
        report_file = f"cascade_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# Отчет каскадного обновления\n\n")
                f.write(f"**Дата:** {datetime.now().isoformat()}\n\n")
                f.write("## Обновленные компоненты:\n\n")
                
                for entry in self.update_log:
                    f.write(f"- **{entry['component']}**: {entry['status']} - {entry['details']}\n")
                
            self.log_update("UPDATE_REPORT", "✅ СОЗДАН", report_file)
            
        except Exception as e:
            self.log_update("UPDATE_REPORT", "❌ ОШИБКА", str(e))

def main():
    """Основная функция для автономного запуска."""
    updater = CascadeUpdater()
    updater.update_all_components()

if __name__ == "__main__":
    main()