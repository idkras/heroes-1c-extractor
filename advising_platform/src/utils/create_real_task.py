#!/usr/bin/env python3
"""
JTBD:
Я (разработчик) хочу создать задачу, инцидент, гипотезу и стандарт,
чтобы проверить работу системы триггеров и убедиться, что все нужные данные
отображаются в чате.

Скрипт для создания тестовых документов и проверки работы триггеров.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import sys
import time
import logging
import argparse
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trigger_demo.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импортируем необходимые компоненты
try:
    from advising_platform.src.core.registry.trigger_handler import (
        get_handler, TriggerType, TriggerContext, TriggerResult
    )
except ImportError as e:
    logger.error(f"Ошибка импорта системы триггеров: {e}")
    sys.exit(1)

def create_task(title: str, description: str, priority: str = "MEDIUM") -> TriggerResult:
    """
    JTBD:
    Я (разработчик) хочу создать задачу и проверить запуск триггера,
    чтобы увидеть, что система корректно собирает и отображает всю нужную информацию.
    
    Создает новую задачу и запускает триггер.
    
    Args:
        title: Название задачи
        description: Описание задачи
        priority: Приоритет задачи (HIGH, MEDIUM, LOW)
        
    Returns:
        TriggerResult: Результат выполнения триггера
    """
    logger.info(f"Создание задачи: {title}")
    
    # Подготавливаем данные задачи
    task_data = {
        "title": title,
        "description": description,
        "status": "NEW",
        "priority": priority,
        "type": "feature",
        "created_at": time.time(),
        "updated_at": time.time(),
        "assignee": "system"
    }
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.TASK_CREATE,
        data=task_data,
        source="create_real_task.py"
    )
    
    # Получаем обработчик триггеров
    trigger_handler = get_handler()
    
    # Запускаем обработку триггера
    result = trigger_handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Задача '{title}' успешно создана и триггер обработан")
    else:
        logger.error(f"Ошибка при создании задачи '{title}': {result.message}")
    
    return result

def create_incident(title: str, description: str, severity: str = "HIGH", five_whys: Optional[list] = None) -> TriggerResult:
    """
    JTBD:
    Я (разработчик) хочу создать инцидент и проверить запуск триггера,
    чтобы увидеть, что система корректно отображает анализ "5 почему" и статус инцидента.
    
    Создает новый инцидент и запускает триггер.
    
    Args:
        title: Название инцидента
        description: Описание инцидента
        severity: Серьезность инцидента (CRITICAL, HIGH, MEDIUM, LOW)
        five_whys: Список "5 почему" или None для автогенерации
        
    Returns:
        TriggerResult: Результат выполнения триггера
    """
    logger.info(f"Создание инцидента: {title}")
    
    # Если "5 почему" не указаны, создаем шаблонные
    if five_whys is None:
        five_whys = [
            f"Почему возник инцидент '{title}'? - Возникли неполадки в системе.",
            "Почему возникли неполадки? - Не были учтены граничные условия.",
            "Почему не были учтены граничные условия? - Отсутствовали тесты для этих сценариев.",
            "Почему отсутствовали тесты? - Не была разработана полная стратегия тестирования.",
            "Почему не была разработана полная стратегия? - Недостаточно ресурсов выделено на тестирование."
        ]
    
    # Подготавливаем данные инцидента
    incident_data = {
        "title": title,
        "description": description,
        "status": "NEW",
        "severity": severity,
        "root_cause": "Требуется анализ",
        "five_whys": five_whys,
        "created_at": time.time(),
        "updated_at": time.time(),
        "assignee": "system"
    }
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.INCIDENT_CREATE,
        data=incident_data,
        source="create_real_task.py"
    )
    
    # Получаем обработчик триггеров
    trigger_handler = get_handler()
    
    # Запускаем обработку триггера
    result = trigger_handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Инцидент '{title}' успешно создан и триггер обработан")
    else:
        logger.error(f"Ошибка при создании инцидента '{title}': {result.message}")
    
    return result

def create_hypothesis(title: str, description: str, rat: Optional[Dict[str, str]] = None, 
                     falsifiability: Optional[str] = None) -> TriggerResult:
    """
    JTBD:
    Я (разработчик) хочу создать гипотезу и проверить запуск триггера,
    чтобы убедиться, что система правильно отображает RAT и критерий фальсифицируемости.
    
    Создает новую гипотезу и запускает триггер.
    
    Args:
        title: Название гипотезы
        description: Описание гипотезы
        rat: Словарь с RAT (Reach, Action, Target) или None для автогенерации
        falsifiability: Критерий фальсифицируемости или None для автогенерации
        
    Returns:
        TriggerResult: Результат выполнения триггера
    """
    logger.info(f"Создание гипотезы: {title}")
    
    # Если RAT не указан, создаем шаблонный
    if rat is None:
        rat = {
            "reach": f"Пользователи, которым требуется решение проблемы '{title}'",
            "action": "Внедрение новой функциональности с улучшенным алгоритмом",
            "target": "Увеличение эффективности обработки данных на 25%"
        }
    
    # Если критерий фальсифицируемости не указан, создаем шаблонный
    if falsifiability is None:
        falsifiability = f"Если внедрение решения '{title}' не приводит к увеличению эффективности хотя бы на 15%, гипотеза считается опровергнутой."
    
    # Подготавливаем данные гипотезы
    hypothesis_data = {
        "title": title,
        "description": description,
        "status": "NEW",
        "rat": rat,
        "falsifiability": falsifiability,
        "created_at": time.time(),
        "updated_at": time.time(),
        "owner": "system"
    }
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.HYPOTHESIS_CREATE,
        data=hypothesis_data,
        source="create_real_task.py"
    )
    
    # Получаем обработчик триггеров
    trigger_handler = get_handler()
    
    # Запускаем обработку триггера
    result = trigger_handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Гипотеза '{title}' успешно создана и триггер обработан")
    else:
        logger.error(f"Ошибка при создании гипотезы '{title}': {result.message}")
    
    return result

def create_standard(title: str, description: str, category: str = "code_quality",
                   tags: Optional[list] = None) -> TriggerResult:
    """
    JTBD:
    Я (разработчик) хочу создать стандарт и проверить запуск триггера,
    чтобы убедиться, что система правильно отображает категорию и теги стандарта.
    
    Создает новый стандарт и запускает триггер.
    
    Args:
        title: Название стандарта
        description: Описание стандарта
        category: Категория стандарта
        tags: Список тегов или None для автогенерации
        
    Returns:
        TriggerResult: Результат выполнения триггера
    """
    logger.info(f"Создание стандарта: {title}")
    
    # Если теги не указаны, создаем шаблонные
    if tags is None:
        tags = ["documentation", "jtbd", "quality", "best_practices"]
    
    # Подготавливаем данные стандарта
    standard_data = {
        "title": title,
        "description": description,
        "status": "ACTIVE",
        "category": category,
        "tags": tags,
        "created_at": time.time(),
        "updated_at": time.time(),
        "author": "system"
    }
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.STANDARD_CREATE,
        data=standard_data,
        source="create_real_task.py"
    )
    
    # Получаем обработчик триггеров
    trigger_handler = get_handler()
    
    # Запускаем обработку триггера
    result = trigger_handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Стандарт '{title}' успешно создан и триггер обработан")
    else:
        logger.error(f"Ошибка при создании стандарта '{title}': {result.message}")
    
    return result

def create_script_file(file_path: str, content: str, description: str) -> TriggerResult:
    """
    JTBD:
    Я (разработчик) хочу создать скрипт и проверить запуск триггера проверки дублирования,
    чтобы убедиться, что система правильно анализирует файл и проверяет наличие JTBD-документации.
    
    Создает новый скрипт и запускает триггер проверки дублирования.
    
    Args:
        file_path: Путь к файлу скрипта
        content: Содержимое файла
        description: Описание скрипта
        
    Returns:
        TriggerResult: Результат выполнения триггера
    """
    logger.info(f"Создание скрипта: {file_path}")
    
    # Создаем директорию, если она не существует
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Записываем содержимое в файл
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Файл {file_path} успешно создан")
    except Exception as e:
        logger.error(f"Ошибка при создании файла {file_path}: {e}")
        return TriggerResult(success=False, message=str(e))
    
    # Подготавливаем данные для триггера
    file_data = {
        "file_path": file_path,
        "file_content": content,
        "description": description
    }
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.FILE_DUPLICATION_CHECK,
        data=file_data,
        source="create_real_task.py"
    )
    
    # Получаем обработчик триггеров
    trigger_handler = get_handler()
    
    # Запускаем обработку триггера
    result = trigger_handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Скрипт '{file_path}' успешно создан и триггер обработан")
    else:
        logger.error(f"Ошибка при проверке скрипта '{file_path}': {result.message}")
    
    return result

def main():
    """
    JTBD:
    Я (разработчик) хочу запустить демонстрацию работы триггеров для разных типов документов,
    чтобы наглядно убедиться в корректности работы системы.
    
    Основная функция для демонстрации работы триггеров.
    """
    parser = argparse.ArgumentParser(description="Демонстрация работы триггеров")
    parser.add_argument('--type', choices=['task', 'incident', 'hypothesis', 'standard', 'script', 'all'],
                      default='all', help='Тип создаваемого документа')
    parser.add_argument('--title', help='Название документа')
    parser.add_argument('--description', help='Описание документа')
    
    args = parser.parse_args()
    
    document_type = args.type
    title = args.title
    description = args.description
    
    # Используем значения по умолчанию, если не указаны
    if title is None:
        title = f"Тестовый документ для демонстрации триггера ({time.strftime('%Y-%m-%d %H:%M:%S')})"
    
    if description is None:
        description = f"Описание документа для демонстрации работы триггера. Создано: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    logger.info("Запуск демонстрации работы триггеров")
    
    if document_type == 'task' or document_type == 'all':
        create_task(
            title=f"Задача: {title}",
            description=f"Описание задачи: {description}",
            priority="MEDIUM"
        )
        # Добавляем паузу для лучшего восприятия в чате
        time.sleep(2)
    
    if document_type == 'incident' or document_type == 'all':
        create_incident(
            title=f"Инцидент: {title}",
            description=f"Описание инцидента: {description}",
            severity="HIGH"
        )
        time.sleep(2)
    
    if document_type == 'hypothesis' or document_type == 'all':
        create_hypothesis(
            title=f"Гипотеза: {title}",
            description=f"Описание гипотезы: {description}"
        )
        time.sleep(2)
    
    if document_type == 'standard' or document_type == 'all':
        create_standard(
            title=f"Стандарт: {title}",
            description=f"Описание стандарта: {description}",
            category="documentation"
        )
        time.sleep(2)
    
    if document_type == 'script' or document_type == 'all':
        script_content = f'''#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации триггера.
Это пример скрипта без JTBD-документации.
"""

def main():
    """
    Основная функция скрипта.
    """
    print("Это тестовый скрипт для демонстрации работы триггера")
    print("Создан: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
'''
        script_path = f"test_scripts/demo_trigger_script_{int(time.time())}.py"
        create_script_file(
            file_path=script_path,
            content=script_content,
            description=f"Тестовый скрипт для демонстрации триггера: {description}"
        )
    
    logger.info("Демонстрация работы триггеров завершена")

if __name__ == "__main__":
    main()