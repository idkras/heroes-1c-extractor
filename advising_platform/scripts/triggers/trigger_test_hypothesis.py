#!/usr/bin/env python3
"""
Скрипт для создания тестовой гипотезы и проверки триггеров.
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

def create_test_hypothesis():
    """
    Создает тестовую гипотезу и активирует триггер.
    """
    # Создаем директорию для гипотезы, если она не существует
    hypothesis_dir = "projects/hypotheses"
    os.makedirs(hypothesis_dir, exist_ok=True)
    
    # Формируем имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"test_hypothesis_{timestamp}.md"
    file_path = os.path.join(hypothesis_dir, file_name)
    
    # Формируем содержимое гипотезы
    hypothesis_content = f"""# Тестовая гипотеза о влиянии триггеров на качество системы

## Статус: Активна

## Описание гипотезы
Реализация единого интерфейса для обработки триггеров и интеграция всех типов документов с этой системой позволит значительно повысить качество и надежность системы, а также сократить время обработки задач.

## Рисуемая мишень (RAT)
Унификация обработки триггеров приведет к сокращению времени обработки задач на 30% и снижению количества инцидентов, связанных с некорректной работой системы, на 50% в течение месяца после внедрения.

## Критерий фальсифицируемости
Гипотеза будет опровергнута, если:
1. После внедрения единого интерфейса время обработки задач не изменится или увеличится
2. Количество инцидентов, связанных с некорректной работой системы, не уменьшится в течение месяца

## План проверки
1. Разработать и внедрить единый интерфейс для обработки триггеров
2. Интегрировать все типы документов с этой системой
3. Измерить время обработки задач до и после внедрения
4. Отслеживать количество инцидентов, связанных с некорректной работой системы
5. Провести анализ результатов через месяц после внедрения

## Ответственный: AI Assistant

## Дата создания: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Теги
- гипотеза
- триггеры
- оптимизация
- качество
"""
    
    # Записываем содержимое в файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(hypothesis_content)
    
    logger.info(f"Создана тестовая гипотеза: {file_path}")
    
    # Вызываем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем контекст триггера с данными гипотезы
    context = TriggerContext(
        trigger_type=TriggerType.HYPOTHESIS_CREATE,
        data={
            "title": "Тестовая гипотеза о влиянии триггеров на качество системы",
            "description": "Реализация единого интерфейса для обработки триггеров и интеграция всех типов документов с этой системой позволит значительно повысить качество и надежность системы, а также сократить время обработки задач.",
            "file_path": file_path,
            "properties": {
                "status": "Активна",
                "responsible": "AI Assistant",
                "tags": ["гипотеза", "триггеры", "оптимизация", "качество"]
            },
            "rat": "Унификация обработки триггеров приведет к сокращению времени обработки задач на 30% и снижению количества инцидентов, связанных с некорректной работой системы, на 50% в течение месяца после внедрения.",
            "falsifiability_criterion": "Гипотеза будет опровергнута, если: 1. После внедрения единого интерфейса время обработки задач не изменится или увеличится, 2. Количество инцидентов, связанных с некорректной работой системы, не уменьшится в течение месяца"
        },
        source="test_script"
    )
    
    # Запускаем триггер
    result = handler.handle_trigger(context)
    
    if result.success:
        logger.info(f"Триггер гипотезы успешно обработан: {result.message}")
        return True, file_path
    else:
        logger.warning(f"Триггер гипотезы не был успешно обработан: {result.message}")
        return False, file_path

if __name__ == "__main__":
    success, file_path = create_test_hypothesis()
    
    if success:
        print(f"✅ Тестовая гипотеза успешно создана и обработана: {file_path}")
    else:
        print(f"❌ Ошибка при создании и обработке тестовой гипотезы")