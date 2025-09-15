"""
Скрипт для проверки рабочего процесса создания задач и инцидентов.
Выполняет следующие проверки:

1. Проверка кеша и файловой системы на соответствие
2. Архивация задач и обновление статистики
3. Проверка предотвращения создания дублей
4. Проверка целостности между кешем и файловой системой

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import time
import logging
import json
from datetime import datetime
from typing import Dict, Any

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("verify_task_workflow")

# Импортируем функции для работы с задачами и инцидентами
try:
    from advising_platform.src.core.registry.trigger_handler import (
        create_task,
        create_incident,
        report_progress
    )
    from advising_platform.critical_instructions_cache import CriticalInstructionsCache
except ImportError:
    logger.error("Не удалось импортировать необходимые модули. Убедитесь, что вы находитесь в корневой директории проекта.")
    exit(1)

def verify_cache_filesystem_sync():
    """
    Проверяет соответствие между кешем и файловой системой.
    
    Returns:
        bool: True, если кеш и файловая система синхронизированы, иначе False
    """
    logger.info("Проверка соответствия кеша и файловой системы...")
    
    # Получаем информацию о состоянии кеша
    from advising_platform.src.core.sync_optimized import verify_cache_filesystem_sync
    
    # Запускаем проверку
    try:
        is_in_sync, details = verify_cache_filesystem_sync()
        
        if is_in_sync:
            logger.info("✅ Кеш и файловая система синхронизированы")
        else:
            logger.warning(f"❌ Обнаружены несоответствия между кешем и файловой системой: {details}")
        
        return is_in_sync
    except Exception as e:
        logger.error(f"Ошибка при проверке синхронизации: {e}")
        return False

def initialize_in_memory_cache():
    """
    Инициализирует in-memory кеш критических инструкций.
    
    Returns:
        CriticalInstructionsCache: Экземпляр кеша критических инструкций
    """
    logger.info("Инициализация in-memory кеша...")
    
    try:
        # Инициализируем кеш критических инструкций
        cache = CriticalInstructionsCache.get_instance()
        
        # Обновляем кеш из файла todo.md
        success = cache.update_cache_from_todo()
        
        if success:
            logger.info(f"✅ In-memory кеш успешно инициализирован, загружено {len(cache.get_critical_instructions())} инструкций")
        else:
            logger.warning("❌ Ошибка при инициализации in-memory кеша")
        
        return cache
    except Exception as e:
        logger.error(f"Ошибка при инициализации in-memory кеша: {e}")
        return None

def create_test_task():
    """
    Создает тестовую задачу для проверки рабочего процесса.
    
    Returns:
        dict: Результат создания задачи
    """
    logger.info("Создание тестовой задачи...")
    
    # Уникальный идентификатор для предотвращения дублей
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Создаем задачу через стандартный механизм
    task_result = create_task(
        title=f"Проверка рабочего процесса задач {timestamp}",
        description="Тестовая задача для проверки workflow создания задач и синхронизации кеша",
        author="AI Assistant",
        assignee="SysAdmin",
        file_path=f"projects/tasks/проверка_workflow_{timestamp}.md",
        report_progress_func=mock_report_progress
    )
    
    if task_result.success:
        logger.info(f"✅ Задача успешно создана: {task_result.item.id}")
    else:
        logger.error(f"❌ Ошибка при создании задачи: {task_result.errors}")
    
    return task_result

def check_duplicate_prevention():
    """
    Проверяет механизм предотвращения создания дублей.
    
    Returns:
        bool: True, если механизм работает корректно, иначе False
    """
    logger.info("Проверка механизма предотвращения дублей...")
    
    # Создаем первую задачу
    first_task = create_task(
        title="Тест предотвращения дублей",
        description="Эта задача должна быть создана только один раз",
        author="AI Assistant",
        assignee="SysAdmin",
        file_path="projects/tasks/test_duplicate_prevention.md",
        report_progress_func=mock_report_progress
    )
    
    if not first_task.success:
        logger.error(f"❌ Не удалось создать первую задачу: {first_task.errors}")
        return False
    
    # Создаем вторую задачу с тем же содержимым
    second_task = create_task(
        title="Тест предотвращения дублей",
        description="Эта задача должна быть создана только один раз",
        author="AI Assistant",
        assignee="SysAdmin",
        file_path="projects/tasks/test_duplicate_prevention_2.md",
        report_progress_func=mock_report_progress
    )
    
    # Проверяем, что вторая задача не была создана
    if not second_task.success and "дубликат" in str(second_task.errors).lower():
        logger.info("✅ Механизм предотвращения дублей работает корректно")
        return True
    else:
        logger.warning("❌ Механизм предотвращения дублей не сработал")
        return False

def mock_report_progress(data: Dict[str, str]) -> None:
    """
    Имитирует функцию report_progress.
    
    Args:
        data: Данные для отчета о прогрессе
    """
    logger.info(f"Отчет о прогрессе: {data}")

def verify_archive_and_stats_update():
    """
    Проверяет механизм архивации задач и обновления статистики.
    
    Returns:
        bool: True, если механизм работает корректно, иначе False
    """
    logger.info("Проверка механизма архивации и обновления статистики...")
    
    # Создаем задачу со статусом "выполнено"
    task = create_task(
        title="Задача для архивации",
        description="Эта задача должна быть архивирована",
        status="done",
        author="AI Assistant",
        assignee="SysAdmin",
        file_path="projects/tasks/task_for_archive.md",
        report_progress_func=mock_report_progress
    )
    
    if not task.success:
        logger.error(f"❌ Не удалось создать задачу для архивации: {task.errors}")
        return False
    
    # Запускаем процесс обработки задач и инцидентов
    from cache_init import process_tasks_and_incidents
    tasks_processed, incidents_processed = process_tasks_and_incidents()
    
    # Проверяем, что задача была архивирована
    if tasks_processed > 0:
        logger.info(f"✅ Обработано задач: {tasks_processed}, инцидентов: {incidents_processed}")
        return True
    else:
        logger.warning("❌ Механизм архивации и обновления статистики не сработал")
        return False

def main():
    """
    Основная функция скрипта.
    """
    logger.info("=== Начало проверки рабочего процесса создания задач и инцидентов ===")
    
    # 1. Проверка соответствия кеша и файловой системы
    verify_cache_filesystem_sync()
    
    # 2. Инициализация in-memory кеша
    cache = initialize_in_memory_cache()
    if not cache:
        logger.error("Не удалось инициализировать in-memory кеш. Прерывание проверки.")
        return
    
    # 3. Создание тестовой задачи
    task_result = create_test_task()
    
    # 4. Проверка предотвращения дублей
    check_duplicate_prevention()
    
    # 5. Проверка архивации и обновления статистики
    verify_archive_and_stats_update()
    
    # 6. Повторная проверка соответствия кеша и файловой системы
    verify_cache_filesystem_sync()
    
    logger.info("=== Проверка рабочего процесса завершена ===")

if __name__ == "__main__":
    main()