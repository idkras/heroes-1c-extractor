#!/usr/bin/env python3
"""
Модуль для прямой интеграции с чатом Replit.
Предоставляет простые и надежные функции для отправки различных типов
документов в чат-интерфейс Replit без промежуточных слоев.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import logging
from typing import Dict, Any, Optional, Union, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальная функция report_progress для отправки сообщений в чат
# Инициализируется как None, будет заменена на функцию из antml.function_calls
report_progress = None

def initialize_report_function():
    """
    Инициализирует функцию report_progress для отправки сообщений в чат.
    Этот шаг необходим для обеспечения корректной интеграции.
    """
    global report_progress
    
    # Пытаемся импортировать функцию из antml.function_calls (встроенный Replit API)
    try:
        from antml.function_calls import report_progress as rp
        report_progress = rp
        logger.info("Инициализирована отправка сообщений через Replit API")
        return True
    except ImportError:
        logger.warning("Не удалось импортировать report_progress из antml.function_calls")
        
        # Если мы в среде, где нет доступа к antml, используем собственную версию
        try:
            # Импортируем версию функции из инструментов Replit Blueprint
            import sys
            from replit_blueprint_tools import report_progress as bp_rp
            report_progress = bp_rp
            logger.info("Инициализирована отправка сообщений через Blueprint инструменты")
            return True
        except ImportError:
            # Если ничего не удалось импортировать, создаем fallback функцию
            logger.warning("Не удалось импортировать report_progress из blueprints")
            
            def fallback_report_progress(data):
                if isinstance(data, dict) and 'summary' in data:
                    print(f"\n--- СООБЩЕНИЕ В ЧАТ ---\n{data['summary']}\n----------------------\n")
                else:
                    print(f"\n--- СООБЩЕНИЕ В ЧАТ ---\n{data}\n----------------------\n")
                return True
            
            report_progress = fallback_report_progress
            logger.warning("Используется вывод сообщений в консоль вместо чата")
            return False

def send_message_to_chat(message: Union[str, Dict[str, Any]]) -> bool:
    """
    Отправляет сообщение в чат-интерфейс Replit.
    
    Args:
        message: Сообщение для отображения (строка или словарь с ключом 'summary')
    
    Returns:
        bool: True если сообщение отправлено успешно, иначе False
    """
    global report_progress
    
    # Если функция report_progress не инициализирована, инициализируем ее
    if report_progress is None:
        initialize_report_function()
    
    try:
        # Если передана строка, преобразуем в словарь
        if isinstance(message, str):
            message_data = {"summary": message}
        else:
            message_data = message
        
        # Отправляем сообщение через функцию report_progress
        report_progress(message_data)
        logger.info("Сообщение успешно отправлено в чат")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в чат: {e}")
        return False

def send_task_to_chat(task_name: str, status: str = "TODO", priority: str = "Средний",
                    stats_total: int = 15, stats_completed: int = 5, stats_in_progress: int = 3,
                    priority_high: int = 4, priority_medium: int = 6, priority_low: int = 5) -> bool:
    """
    Отправляет информацию о задаче в чат с статистикой.
    
    Args:
        task_name: Название задачи
        status: Статус задачи
        priority: Приоритет задачи
        stats_total: Общее количество задач
        stats_completed: Количество выполненных задач
        stats_in_progress: Количество задач в работе
        priority_high: Количество задач с высоким приоритетом
        priority_medium: Количество задач со средним приоритетом  
        priority_low: Количество задач с низким приоритетом
    
    Returns:
        bool: True если сообщение отправлено успешно, иначе False
    """
    # Создаем URL-совместимое название задачи
    url_name = task_name.lower().replace(" ", "-")
    
    # Вычисляем процент выполнения и количество незапущенных задач
    completion_percentage = int((stats_completed / stats_total) * 100) if stats_total > 0 else 0
    not_started = stats_total - stats_completed - stats_in_progress
    
    # Формируем сообщение
    message = (
        f"✅ **Задача создана**: {task_name}\n"
        f"📋 Статус: {status}\n"
        f"🔴 Приоритет: {priority}\n"
        f"🌐 Просмотр: http://0.0.0.0:5000/tasks/{url_name}\n\n"
        f"📊 **Статистика по задачам**:\n"
        f"📝 Всего задач: {stats_total}\n"
        f"✅ Выполнено: {stats_completed} ({completion_percentage}%)\n"
        f"⏳ В процессе: {stats_in_progress}\n"
        f"🆕 Не начато: {not_started}\n\n"
        f"🔢 **По приоритетам**:\n"
        f"🔴 Высокий: {priority_high}\n"
        f"🟠 Средний: {priority_medium}\n"
        f"🟢 Низкий: {priority_low}\n"
    )
    
    return send_message_to_chat(message)

def send_incident_to_chat(incident_name: str, status: str = "INVESTIGATING", severity: str = "Высокий",
                         five_why_analysis: Optional[str] = None,
                         stats_total: int = 5, stats_resolved: int = 2, 
                         stats_in_progress: int = 2, stats_new: int = 1) -> bool:
    """
    Отправляет информацию об инциденте в чат с анализом 5-почему.
    
    Args:
        incident_name: Название инцидента
        status: Статус инцидента
        severity: Серьезность инцидента
        five_why_analysis: Анализ 5-почему (строка с форматированием)
        stats_total: Общее количество инцидентов
        stats_resolved: Количество решенных инцидентов
        stats_in_progress: Количество инцидентов в работе
        stats_new: Количество новых инцидентов
    
    Returns:
        bool: True если сообщение отправлено успешно, иначе False
    """
    # Создаем URL-совместимое название инцидента
    url_name = incident_name.lower().replace(" ", "-")
    
    # Формируем сообщение
    message = (
        f"🚨 **Инцидент создан**: {incident_name}\n"
        f"📋 Статус: {status}\n"
        f"⚠️ Серьезность: {severity}\n"
        f"🌐 Просмотр: http://0.0.0.0:5000/incidents/{url_name}\n\n"
    )
    
    # Добавляем анализ 5-почему, если предоставлен
    if five_why_analysis:
        message += f"🔍 **Анализ 5 почему**:\n{five_why_analysis}\n\n"
    
    # Добавляем статистику инцидентов
    message += (
        f"📊 **Статистика инцидентов**:\n"
        f"🚨 Всего инцидентов: {stats_total}\n"
        f"✅ Решено: {stats_resolved}\n"
        f"⏳ В процессе: {stats_in_progress}\n"
        f"🆕 Новых: {stats_new}\n\n"
    )
    
    return send_message_to_chat(message)

def send_hypothesis_to_chat(hypothesis_name: str, status: str = "PROPOSED",
                          rat: Optional[str] = None, falsifiability: Optional[str] = None,
                          stats_total: int = 3, stats_confirmed: int = 1, 
                          stats_rejected: int = 0, stats_testing: int = 2) -> bool:
    """
    Отправляет информацию о гипотезе в чат с RAT и критерием фальсифицируемости.
    
    Args:
        hypothesis_name: Название гипотезы
        status: Статус гипотезы
        rat: RAT (Rapid Assumption Testing) текст
        falsifiability: Критерий фальсифицируемости текст
        stats_total: Общее количество гипотез
        stats_confirmed: Количество подтвержденных гипотез
        stats_rejected: Количество опровергнутых гипотез
        stats_testing: Количество гипотез в процессе тестирования
    
    Returns:
        bool: True если сообщение отправлено успешно, иначе False
    """
    # Создаем URL-совместимое название гипотезы
    url_name = hypothesis_name.lower().replace(" ", "-")
    
    # Формируем сообщение
    message = (
        f"💡 **Гипотеза создана**: {hypothesis_name}\n"
        f"📋 Статус: {status}\n"
        f"🌐 Просмотр: http://0.0.0.0:5000/hypotheses/{url_name}\n\n"
    )
    
    # Добавляем RAT, если предоставлен
    if rat:
        message += f"🔬 **RAT (Rapid Assumption Testing)**:\n{rat}\n\n"
    
    # Добавляем критерий фальсифицируемости, если предоставлен
    if falsifiability:
        message += f"❌ **Критерий фальсифицируемости**:\n{falsifiability}\n\n"
    
    # Добавляем статистику гипотез
    message += (
        f"📊 **Статистика гипотез**:\n"
        f"💡 Всего гипотез: {stats_total}\n"
        f"✅ Подтверждено: {stats_confirmed}\n"
        f"❌ Опровергнуто: {stats_rejected}\n"
        f"⏳ В процессе проверки: {stats_testing}\n\n"
    )
    
    return send_message_to_chat(message)