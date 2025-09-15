#!/usr/bin/env python3
"""
Скрипт для отображения статистики задач в консоли и чате.
Может запускаться вручную или по расписанию.
"""

import os
import sys
import logging
import time
from typing import Dict, Any

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем текущую директорию в путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def display_statistics():
    """
    Отображает статистику задач в консоли и чате.
    Использует особый формат для повышения заметности.
    """
    try:
        # Импортируем функции для работы со статистикой
        from advising_platform.src.core.storage.task_storage import get_task_statistics
        
        # Получаем статистику
        stats = get_task_statistics()
        
        # Формируем сообщение с заметным форматированием
        header = "=" * 80
        message = f"""
{header}
                        СТАТИСТИКА ЗАДАЧ
{header}

📝 Всего задач: {stats.get('total', 0)}
✅ Выполнено: {stats.get('completed', 0)} ({stats.get('completion_rate', 0)}%)
⏳ В процессе: {stats.get('in_progress', 0)}
🆕 Не начато: {stats.get('not_started', 0)}

🔢 ПО ПРИОРИТЕТАМ:
🔴 Высокий: {stats.get('high_priority', 0)}
🟠 Средний: {stats.get('medium_priority', 0)}
🟢 Низкий: {stats.get('low_priority', 0)}

Последнее обновление: {stats.get('last_update', '')}
{header}
"""
        
        # Выводим сообщение в консоль с максимальной заметностью
        print(message)
        
        # Пытаемся также вывести через report_progress
        try:
            from advising_platform.src.tools.reporting.report_interface import report_progress
            report_progress({"summary": message}, force_output=True)
        except Exception as e:
            logger.warning(f"Не удалось вывести статистику через report_progress: {e}")
            
        return stats
    except Exception as e:
        logger.error(f"Ошибка при отображении статистики: {e}")
        return None

def main():
    """Основная функция скрипта."""
    logger.info("Запуск отображения статистики задач")
    
    # Отображаем статистику один раз
    stats = display_statistics()
    
    if stats:
        logger.info("Статистика задач успешно отображена")
    else:
        logger.error("Не удалось отобразить статистику задач")
    
if __name__ == "__main__":
    main()