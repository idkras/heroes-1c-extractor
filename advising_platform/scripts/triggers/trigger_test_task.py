#!/usr/bin/env python3
"""
Скрипт для создания тестовой задачи и проверки триггеров.
"""

import os
import sys
import logging
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем необходимые модули
try:
    from advising_platform.src.core.registry.trigger_handler import (
        TriggerHandler, TriggerType, TriggerContext, get_handler
    )
    from advising_platform.src.tools.reporting.report_interface import report_progress
    
    logger.info("Модули триггеров успешно импортированы")
except ImportError as e:
    logger.error(f"Не удалось импортировать модули триггеров: {e}")
    sys.exit(1)

def create_test_task():
    """
    Создает тестовую задачу и активирует триггер.
    """
    # Создаем директорию для задачи, если она не существует
    task_dir = "projects/tasks"
    os.makedirs(task_dir, exist_ok=True)
    
    # Формируем имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"test_task_{timestamp}.md"
    file_path = os.path.join(task_dir, file_name)
    
    # Формируем содержимое задачи
    task_content = f"""# Тестовая задача для проверки триггеров {timestamp}

## Описание
Это тестовая задача, созданная для проверки работы системы триггеров.
Задача должна быть автоматически обработана и добавлена в список задач.

## Шаги
1. Создание файла
2. Запуск триггера
3. Проверка результатов

## Ожидаемые результаты
1. Задача должна быть добавлена в todo.md
2. Должна обновиться статистика задач
3. Должна быть выполнена проверка на дубликаты

## Статус: В работе

## Приоритет: Средний

## Категория: Тестирование

## Теги
- тест
- триггеры
- автоматизация

## Дата создания: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Автор: AI Assistant
"""
    
    # Записываем содержимое в файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(task_content)
    
    logger.info(f"Создана тестовая задача: {file_path}")
    
    # Вызываем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.TASK_CREATE,
        data={
            "title": f"Тестовая задача для проверки триггеров {timestamp}",
            "description": "Это тестовая задача, созданная для проверки работы системы триггеров.",
            "file_path": file_path,
            "properties": {
                "priority": "Средний",
                "category": "Тестирование",
                "tags": ["тест", "триггеры", "автоматизация"],
                "status": "В работе"
            }
        },
        source="test_script"
    )
    
    # Запускаем триггер
    result = handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Триггер задачи успешно обработан: {result.message}")
        return True, file_path
    else:
        logger.warning(f"Триггер задачи не был успешно обработан: {result.message}")
        return False, file_path

if __name__ == "__main__":
    success, file_path = create_test_task()
    
    if success:
        print(f"✅ Тестовая задача успешно создана и обработана: {file_path}")
    else:
        print(f"❌ Ошибка при создании и обработке тестовой задачи")