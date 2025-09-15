"""
Простой скрипт для создания задач, инцидентов и стандартов с минимальной проверкой кеша.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import logging
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("quick_task_creator")

# Функция для фиктивного report_progress
def mock_report_progress(data: Dict[str, str]) -> None:
    """Имитирует функцию report_progress."""
    print("\n🔔 Report Progress вызван с данными:")
    print(f"  {data['summary']}")
    return None

def create_task(title: str, description: str, author: str = "AI Assistant", assignee: Optional[str] = None):
    """
    Создает новую задачу.
    
    Args:
        title: Заголовок задачи
        description: Описание задачи
        author: Автор задачи
        assignee: Ответственный за задачу
    
    Returns:
        ID созданной задачи или None при ошибке
    """
    try:
        from advising_platform.src.core.registry.trigger_handler import create_task as create_task_trigger
        
        # Создаем директорию для файла
        task_dir = "projects/tasks"
        os.makedirs(task_dir, exist_ok=True)
        
        # Создаем безопасное имя файла из заголовка
        safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())
        file_path = f"{task_dir}/{safe_title}.md"
        
        # Создаем задачу
        result = create_task_trigger(
            title=title,
            description=description,
            author=author,
            assignee=assignee,
            file_path=file_path,
            report_progress_func=mock_report_progress
        )
        
        if result and result.success and result.item:
            print(f"✅ Задача успешно создана: {result.item.id}: {result.item.title}")
            if result.item.file_path and os.path.exists(result.item.file_path):
                print(f"📄 Файл создан: {result.item.file_path}")
            return result.item.id
        else:
            print("❌ Ошибка при создании задачи")
            if result and result.errors:
                for error in result.errors:
                    print(f"  - {error}")
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        return None

def create_incident(title: str, description: str, author: str = "AI Assistant", assignee: Optional[str] = None):
    """
    Создает новый инцидент.
    
    Args:
        title: Заголовок инцидента
        description: Описание инцидента
        author: Автор инцидента
        assignee: Ответственный за инцидент
    
    Returns:
        ID созданного инцидента или None при ошибке
    """
    try:
        from advising_platform.src.core.registry.trigger_handler import create_incident as create_incident_trigger
        
        # Создаем директорию для файла
        incident_dir = "incidents"
        os.makedirs(incident_dir, exist_ok=True)
        
        # Создаем безопасное имя файла из заголовка
        safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())
        file_path = f"{incident_dir}/{safe_title}.md"
        
        # Создаем инцидент
        result = create_incident_trigger(
            title=title,
            description=description,
            author=author,
            assignee=assignee,
            file_path=file_path,
            report_progress_func=mock_report_progress
        )
        
        if result and result.success and result.item:
            print(f"✅ Инцидент успешно создан: {result.item.id}: {result.item.title}")
            if result.item.file_path and os.path.exists(result.item.file_path):
                print(f"📄 Файл создан: {result.item.file_path}")
            return result.item.id
        else:
            print("❌ Ошибка при создании инцидента")
            if result and result.errors:
                for error in result.errors:
                    print(f"  - {error}")
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при создании инцидента: {e}")
        return None

def main():
    """Основная функция."""
    print("🚀 Запуск создания рабочих элементов...")
    
    # Создаем пример задачи
    task_id = create_task(
        title="Разработать интеграцию с CRM-системой",
        description=(
            "Разработать модуль для интеграции с CRM-системой для автоматического "
            "создания задач и инцидентов на основе клиентских запросов."
        ),
        assignee="Developer"
    )
    
    # Создаем пример инцидента
    incident_id = create_incident(
        title="Отказ синхронизации репозитория",
        description=(
            "Обнаружена проблема с синхронизацией репозитория. При запуске команды sync "
            "возникает ошибка доступа к файлам и потеря части данных в кеше."
        ),
        assignee="SysAdmin"
    )
    
    # Выводим результаты
    if task_id and incident_id:
        print("\n✅ Созданы рабочие элементы:")
        print(f"  📋 Задача: {task_id}")
        print(f"  🚨 Инцидент: {incident_id}")
    
    print("\n🏁 Работа завершена")

if __name__ == "__main__":
    main()