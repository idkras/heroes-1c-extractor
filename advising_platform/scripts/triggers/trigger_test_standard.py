#!/usr/bin/env python3
"""
Скрипт для создания тестового стандарта и проверки триггеров.
"""

import os
import sys
import logging
import traceback
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

def create_test_standard():
    """
    Создает тестовый стандарт и активирует триггер.
    """
    # Создаем директорию для стандарта, если она не существует
    standard_dir = "standards"
    os.makedirs(standard_dir, exist_ok=True)
    
    # Формируем имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"test_standard_{timestamp}.md"
    file_path = os.path.join(standard_dir, file_name)
    
    # Формируем содержимое стандарта
    standard_content = f"""# Стандарт обработки триггеров в системе задач и инцидентов

## Версия: 1.0

## Дата создания: {datetime.now().strftime("%Y-%m-%d")}

## Автор: AI Assistant

## Описание
Данный стандарт определяет правила и процессы обработки триггеров в системе управления задачами и инцидентами.

## Цель
Обеспечить единый подход к обработке событий в системе, повысить надежность и предсказуемость работы системы.

## Основные требования
1. Все триггеры должны обрабатываться через единый интерфейс TriggerHandler
2. Каждый тип триггера должен иметь отдельный метод обработки
3. Все методы обработки должны возвращать объект TriggerResult
4. Обработка триггера должна быть идемпотентной
5. Обработка должна быть атомарной - либо успешна полностью, либо не выполнена

## Процесс обработки триггеров
1. Регистрация триггера в системе
2. Передача контекста триггера в соответствующий обработчик
3. Обработка триггера с учетом его типа и контекста
4. Возврат результата обработки
5. Логирование результатов

## Исключения
В случае ошибки при обработке триггера, система должна логировать ошибку и возвращать результат с флагом success=False.

## Ссылки на связанные стандарты
- Стандарт оформления задач
- Стандарт обработки инцидентов
- Стандарт логирования

## Ключевые теги
- триггеры
- обработка событий
- надежность
- стандарты
"""
    
    # Записываем содержимое в файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(standard_content)
    
    logger.info(f"Создан тестовый стандарт: {file_path}")
    
    # Вызываем обработчик триггеров
    handler = get_handler(report_progress_func=report_progress)
    
    # Создаем контекст триггера с данными стандарта
    context = TriggerContext(
        trigger_type=TriggerType.STANDARD_CREATE,
        data={
            "title": "Стандарт обработки триггеров в системе задач и инцидентов",
            "description": "Данный стандарт определяет правила и процессы обработки триггеров в системе управления задачами и инцидентами.",
            "file_path": file_path,
            "properties": {
                "version": "1.0",
                "author": "AI Assistant",
                "tags": ["триггеры", "обработка событий", "надежность", "стандарты"]
            },
            "requirements": [
                "Все триггеры должны обрабатываться через единый интерфейс TriggerHandler",
                "Каждый тип триггера должен иметь отдельный метод обработки",
                "Все методы обработки должны возвращать объект TriggerResult",
                "Обработка триггера должна быть идемпотентной",
                "Обработка должна быть атомарной - либо успешна полностью, либо не выполнена"
            ]
        },
        source="test_script"
    )
    
    # Запускаем триггер
    try:
        result = handler.handle_trigger(context)
        
        if result.success:
            logger.info(f"Триггер стандарта успешно обработан: {result.message}")
            return True, file_path
        else:
            logger.warning(f"Триггер стандарта не был успешно обработан: {result.message}")
            return False, file_path
    except Exception as e:
        logger.error(f"Ошибка при обработке триггера стандарта: {e}")
        traceback.print_exc()
        return False, file_path

if __name__ == "__main__":
    success, file_path = create_test_standard()
    
    if success:
        print(f"✅ Тестовый стандарт успешно создан и обработан: {file_path}")
    else:
        print(f"❌ Ошибка при создании и обработке тестового стандарта")