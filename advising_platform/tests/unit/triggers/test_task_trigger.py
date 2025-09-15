#!/usr/bin/env python3
"""
Тест для проверки триггера при создании задачи.
"""

import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("task_trigger_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("task_trigger_test")

# Импортируем унифицированный интерфейс документов
from document_unified_interface import TaskDocument

def test_task_trigger():
    """Тестирует вывод триггера при создании задачи."""
    logger.info("=== Тест триггера создания задачи ===")
    
    task_doc = TaskDocument()
    task_id = task_doc.create(
        title="Комплексная проверка вывода триггеров для задачи",
        description="""
## Описание
Задача на проверку полного вывода триггеров при создании задачи.

## Критерии готовности
1. Триггер выводит заголовок задачи
2. Триггер выводит статус и приоритет задачи
3. Триггер выводит URL на веб-интерфейс
4. Триггер выводит статистику по задачам
        """,
        priority="Высокий",
        status="Не начато",
        type="Тестирование"
    )
    
    logger.info(f"Создана тестовая задача с ID: {task_id}")
    print(f"\n[✓] Создана задача: Комплексная проверка вывода триггеров для задачи (ID: {task_id})")
    print(f"[✓] Проверьте вывод триггера в чат и наличие статистики по задачам!")
    print(f"[✓] Ожидаемый URL: http://0.0.0.0:5000/tasks/Комплексная-проверка-вывода-триггеров-для-задачи")

if __name__ == "__main__":
    test_task_trigger()