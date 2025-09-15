"""
Простой скрипт для создания задач и инцидентов через триггер-хендлер.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_task_creator")

# Функция для фиктивного report_progress
def mock_report_progress(data: Dict[str, str]) -> None:
    """Имитирует функцию report_progress."""
    print("\n🔔 Report Progress вызван с данными:")
    print(f"  {data['summary']}")
    return None

def create_test_task():
    """Создает тестовую задачу через триггер-хендлер."""
    try:
        # Импортируем функцию для создания задачи
        from advising_platform.src.core.registry.trigger_handler import create_task
        
        # Создаем директорию для файла, если она не существует
        task_dir = "projects/tests"
        os.makedirs(task_dir, exist_ok=True)
        
        # Создаем задачу
        result = create_task(
            title="Тестовая задача для проверки системы",
            description="Это тестовая задача, созданная для проверки работы системы управления задачами.",
            author="AI Assistant",
            assignee="Developer",
            file_path=f"{task_dir}/test-task.md",
            report_progress_func=mock_report_progress
        )
        
        # Выводим результат
        if result and result.success:
            print(f"✅ Задача успешно создана: {result.item.id}: {result.item.title}")
            if result.item.file_path and os.path.exists(result.item.file_path):
                print(f"📄 Файл создан: {result.item.file_path}")
            
            return result.item.id if result.item else None
        else:
            print("❌ Ошибка при создании задачи")
            if result and result.errors:
                for error in result.errors:
                    print(f"  - {error}")
            
            return None
    
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return None

def create_test_incident():
    """Создает тестовый инцидент через триггер-хендлер."""
    try:
        # Импортируем функцию для создания инцидента
        from advising_platform.src.core.registry.trigger_handler import create_incident
        
        # Создаем директорию для файла, если она не существует
        incident_dir = "incidents"
        os.makedirs(incident_dir, exist_ok=True)
        
        # Создаем инцидент
        result = create_incident(
            title="Тестовый инцидент для проверки системы",
            description="Это тестовый инцидент, созданный для проверки работы системы управления инцидентами.",
            author="AI Assistant",
            assignee="SysAdmin",
            file_path=f"{incident_dir}/test-incident.md",
            report_progress_func=mock_report_progress
        )
        
        # Выводим результат
        if result and result.success:
            print(f"✅ Инцидент успешно создан: {result.item.id}: {result.item.title}")
            if result.item.file_path and os.path.exists(result.item.file_path):
                print(f"📄 Файл создан: {result.item.file_path}")
            
            return result.item.id if result.item else None
        else:
            print("❌ Ошибка при создании инцидента")
            if result and result.errors:
                for error in result.errors:
                    print(f"  - {error}")
            
            return None
    
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return None

def main():
    """Основная функция."""
    print("🚀 Запуск создания тестовых элементов...")
    
    # Создаем задачу
    task_id = create_test_task()
    
    # Создаем инцидент
    incident_id = create_test_incident()
    
    # Выводим результаты
    if task_id and incident_id:
        print(f"\n✅ Оба элемента успешно созданы:")
        print(f"  - Задача: {task_id}")
        print(f"  - Инцидент: {incident_id}")
        
        # Проверяем созданные файлы
        total_files = 0
        
        if os.path.exists("projects/tests/test-task.md"):
            print(f"  - Файл задачи создан")
            total_files += 1
        
        if os.path.exists("incidents/test-incident.md"):
            print(f"  - Файл инцидента создан")
            total_files += 1
        
        print(f"\nВсего создано файлов: {total_files}")
    else:
        print("\n❌ Не удалось создать все элементы")

if __name__ == "__main__":
    main()