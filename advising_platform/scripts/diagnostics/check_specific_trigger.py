#!/usr/bin/env python3
"""
Скрипт для проверки конкретного типа триггера.
Упрощенная версия fix_trigger_system.py для тестирования отдельных компонентов.

Использование: python check_specific_trigger.py [тип_триггера]
Доступные типы триггеров: task, incident, hypothesis, standard

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import logging
import traceback
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("check_specific_trigger")

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

def test_task_trigger():
    """Тестирует триггер создания задачи."""
    logger.info("Тестирование триггера создания задачи")
    
    # Получаем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем дату-время для уникальности тестовых данных
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.TASK_CREATE,
        data={
            "title": f"Тестовая задача {timestamp}",
            "description": "Это тестовая задача для проверки работы системы триггеров",
            "file_path": f"test_task_{timestamp}.md",
            "properties": {"status": "Новая", "priority": "Высокий"}
        },
        source="diagnosis"
    )
    
    # Обрабатываем триггер
    result = handler.handle_trigger(context)
    
    # Выводим результат
    logger.info(f"Результат тестирования триггера task_create: {result.success}")
    if result.success:
        print(f"✅ Триггер task_create успешно отработал!")
    else:
        print(f"❌ Триггер task_create завершился с ошибкой: {result.message}")
    
    return result.success

def test_incident_trigger():
    """Тестирует триггер создания инцидента."""
    logger.info("Тестирование триггера создания инцидента")
    
    # Получаем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем дату-время для уникальности тестовых данных
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.INCIDENT_CREATE,
        data={
            "title": f"Тестовый инцидент {timestamp}",
            "description": """Тестовый инцидент для проверки 5-почему анализа.

### Почему #1: Почему система триггеров работает некорректно?
**Ответ:** Недостаточная интеграция между компонентами системы.

### Почему #2: Почему интеграция недостаточна?
**Ответ:** Отсутствует единый механизм передачи состояния между процессами.

### Почему #3: Почему отсутствует единый механизм?
**Ответ:** Система развивалась постепенно без централизованного проектирования.

### Почему #4: Почему не было централизованного проектирования?
**Ответ:** Разработка велась в условиях быстрого прототипирования.

### Почему #5: Почему использовалось быстрое прототипирование?
**Ответ:** Необходимо было быстро выпустить MVP продукта для тестирования гипотез.

### Корневая причина:
Приоритет скорости разработки над архитектурной целостностью на ранних этапах проекта.""",
            "file_path": f"test_incident_{timestamp}.md",
            "properties": {"status": "Новый", "severity": "Критический"}
        },
        source="diagnosis"
    )
    
    # Обрабатываем триггер
    result = handler.handle_trigger(context)
    
    # Выводим результат
    logger.info(f"Результат тестирования триггера incident_create: {result.success}")
    if result.success:
        print(f"✅ Триггер incident_create успешно отработал!")
    else:
        print(f"❌ Триггер incident_create завершился с ошибкой: {result.message}")
    
    return result.success

def test_hypothesis_trigger():
    """Тестирует триггер создания гипотезы."""
    logger.info("Тестирование триггера создания гипотезы")
    
    # Получаем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем дату-время для уникальности тестовых данных
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.HYPOTHESIS_CREATE,
        data={
            "title": f"Тестовая гипотеза {timestamp}",
            "description": """**Гипотеза**: Система триггеров может быть оптимизирована для повышения надежности и производительности.

## Рисуемая мишень (RAT)
**Реалистичность**: Система триггеров может быть улучшена в короткие сроки с текущими ресурсами.
**Амбициозность**: Улучшение обеспечит полную автоматизацию обработки всех типов документов.
**Тестируемость**: Каждый тип триггера имеет специфичные метрики успеха и может быть проверен.

## Критерий фальсифицируемости
Если после внедрения изменений хотя бы один тип триггера не работает или работает некорректно, гипотеза считается опровергнутой.

## Эксперимент
Для проверки гипотезы будет разработан скрипт, который последовательно проверяет работу всех типов триггеров и собирает статистику успешных и неуспешных вызовов.""",
            "file_path": f"test_hypothesis_{timestamp}.md",
            "properties": {"status": "Новая"},
            "rat": "Система триггеров может быть улучшена в короткие сроки с текущими ресурсами.",
            "falsifiability_criterion": "Если после внедрения изменений хотя бы один тип триггера не работает или работает некорректно, гипотеза считается опровергнутой."
        },
        source="diagnosis"
    )
    
    # Обрабатываем триггер
    result = handler.handle_trigger(context)
    
    # Выводим результат
    logger.info(f"Результат тестирования триггера hypothesis_create: {result.success}")
    if result.success:
        print(f"✅ Триггер hypothesis_create успешно отработал!")
    else:
        print(f"❌ Триггер hypothesis_create завершился с ошибкой: {result.message}")
    
    return result.success

def test_standard_trigger():
    """Тестирует триггер создания стандарта."""
    logger.info("Тестирование триггера создания стандарта")
    
    # Получаем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем дату-время для уникальности тестовых данных
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Создаем контекст триггера
    context = TriggerContext(
        trigger_type=TriggerType.STANDARD_CREATE,
        data={
            "title": f"Тестовый стандарт {timestamp}",
            "description": "Это тестовый стандарт для проверки работы системы триггеров",
            "file_path": f"test_standard_{timestamp}.md",
            "properties": {"status": "Active", "version": "1.0", "tags": ["test", "standard", "trigger"]}
        },
        source="diagnosis"
    )
    
    # Обрабатываем триггер
    result = handler.handle_trigger(context)
    
    # Выводим результат
    logger.info(f"Результат тестирования триггера standard_create: {result.success}")
    if result.success:
        print(f"✅ Триггер standard_create успешно отработал!")
    else:
        print(f"❌ Триггер standard_create завершился с ошибкой: {result.message}")
    
    return result.success

def main():
    """Основная функция скрипта."""
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        trigger_type = sys.argv[1].lower()
    else:
        trigger_type = "all"
    
    print(f"🧪 Тестирование триггера типа: {trigger_type}")
    
    try:
        if trigger_type == "task" or trigger_type == "all":
            test_task_trigger()
        
        if trigger_type == "incident" or trigger_type == "all":
            test_incident_trigger()
        
        if trigger_type == "hypothesis" or trigger_type == "all":
            test_hypothesis_trigger()
        
        if trigger_type == "standard" or trigger_type == "all":
            test_standard_trigger()
        
        print("🏁 Тестирование завершено!")
    except Exception as e:
        logger.error(f"Ошибка при тестировании триггера: {e}")
        traceback.print_exc()
        print(f"❌ Произошла ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()