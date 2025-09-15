#!/usr/bin/env python3
"""
Модуль интеграции системы вывода в чат с системой триггеров.

Этот модуль обеспечивает автоматическую регистрацию обработчиков триггеров
для вывода информации в чат при создании различных типов документов.

Автор: AI Assistant
Дата: 22 мая 2025
"""

import logging
from typing import Dict, Any, Optional

from advising_platform.src.core.registry.trigger_handler import TriggerHandler, TriggerContext, TriggerResult, TriggerType
from advising_platform.src.core.chat_output.trigger_reporter import process_document_creation_trigger, TaskChatReporter, IncidentChatReporter, HypothesisChatReporter, StandardChatReporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chat_triggers.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chat_triggers")


def register_chat_trigger_handlers() -> bool:
    """JTBD:
Я (разработчик) хочу использовать функцию register_chat_trigger_handlers, чтобы эффективно зарегистрировать обработчики для вывода информации в чат при создании документов.
    
    Регистрирует обработчики триггеров для вывода информации в чат.
    
    Returns:
        bool: True, если регистрация прошла успешно, иначе False
    """
    try:
        # Получаем экземпляр обработчика триггеров
        trigger_handler = TriggerHandler._instance
        
        # Проверяем, что он инициализирован
        if not trigger_handler:
            logger.warning("Система триггеров не инициализирована, создаем новый экземпляр")
            trigger_handler = TriggerHandler()
            
        # Регистрируем обработчики для различных типов документов
        trigger_handler.register_handler(TriggerType.TASK_CREATE, handle_task_create)
        trigger_handler.register_handler(TriggerType.INCIDENT_CREATE, handle_incident_create)
        trigger_handler.register_handler(TriggerType.HYPOTHESIS_CREATE, handle_hypothesis_create)
        trigger_handler.register_handler(TriggerType.STANDARD_CREATE, handle_standard_create)
        
        logger.info("Обработчики триггеров для вывода в чат успешно зарегистрированы")
        return True
    except Exception as e:
        logger.error(f"Ошибка при регистрации обработчиков триггеров для вывода в чат: {str(e)}")
        return False


def initialize_chat_trigger_system() -> bool:
    """JTBD:
Я (разработчик) хочу использовать функцию initialize_chat_trigger_system, чтобы эффективно инициализировать и запустить систему вывода информации в чат.
    
    Инициализирует систему триггеров для вывода информации в чат.
    
    Returns:
        bool: True, если инициализация прошла успешно, иначе False
    """
    try:
        # Регистрируем обработчики триггеров
        success = register_chat_trigger_handlers()
        
        if success:
            logger.info("Система вывода информации в чат успешно инициализирована")
        else:
            logger.error("Не удалось инициализировать систему вывода информации в чат")
            
        return success
    except Exception as e:
        logger.error(f"Ошибка при инициализации системы вывода информации в чат: {str(e)}")
        return False


def handle_task_create(context: TriggerContext) -> TriggerResult:
    """
    Обрабатывает триггер создания задачи и выводит информацию в чат.
    
    Args:
        context: Контекст триггера
        
    Returns:
        TriggerResult: Результат обработки триггера
    """
    try:
        # Извлекаем данные из контекста
        document_data = context.data
        
        # Создаем репортер для задач и выводим информацию в чат
        reporter = TaskChatReporter()
        reporter.report_creation(document_data)
        
        # Выводим статистику по задачам
        reporter.report_statistics()
        
        # Продолжаем обработку триггера (не прерываем цепочку)
        return TriggerResult(success=True, message="Информация о задаче выведена в чат")
    except Exception as e:
        logger.error(f"Ошибка при обработке триггера создания задачи для вывода в чат: {str(e)}")
        # Продолжаем обработку триггера, даже если произошла ошибка
        return TriggerResult(success=True, message=f"Ошибка при выводе информации о задаче в чат: {str(e)}")


def handle_incident_create(context: TriggerContext) -> TriggerResult:
    """
    Обрабатывает триггер создания инцидента и выводит информацию в чат.
    
    Args:
        context: Контекст триггера
        
    Returns:
        TriggerResult: Результат обработки триггера
    """
    try:
        # Извлекаем данные из контекста
        document_data = context.data
        
        # Создаем репортер для инцидентов и выводим информацию в чат
        reporter = IncidentChatReporter()
        reporter.report_creation(document_data)
        
        # Выводим 5-почему анализ для инцидента, если он есть
        if 'five_why_analysis' in document_data:
            reporter.report_five_why_analysis(document_data)
        
        # Продолжаем обработку триггера (не прерываем цепочку)
        return TriggerResult(success=True, message="Информация об инциденте выведена в чат")
    except Exception as e:
        logger.error(f"Ошибка при обработке триггера создания инцидента для вывода в чат: {str(e)}")
        # Продолжаем обработку триггера, даже если произошла ошибка
        return TriggerResult(success=True, message=f"Ошибка при выводе информации об инциденте в чат: {str(e)}")


def handle_hypothesis_create(context: TriggerContext) -> TriggerResult:
    """
    Обрабатывает триггер создания гипотезы и выводит информацию в чат.
    
    Args:
        context: Контекст триггера
        
    Returns:
        TriggerResult: Результат обработки триггера
    """
    try:
        # Извлекаем данные из контекста
        document_data = context.data
        
        # Создаем репортер для гипотез и выводим информацию в чат
        reporter = HypothesisChatReporter()
        reporter.report_creation(document_data)
        
        # Продолжаем обработку триггера (не прерываем цепочку)
        return TriggerResult(success=True, message="Информация о гипотезе выведена в чат")
    except Exception as e:
        logger.error(f"Ошибка при обработке триггера создания гипотезы для вывода в чат: {str(e)}")
        # Продолжаем обработку триггера, даже если произошла ошибка
        return TriggerResult(success=True, message=f"Ошибка при выводе информации о гипотезе в чат: {str(e)}")


def handle_standard_create(context: TriggerContext) -> TriggerResult:
    """
    Обрабатывает триггер создания стандарта и выводит информацию в чат.
    
    Args:
        context: Контекст триггера
        
    Returns:
        TriggerResult: Результат обработки триггера
    """
    try:
        # Извлекаем данные из контекста
        document_data = context.data
        
        # Создаем репортер для стандартов и выводим информацию в чат
        reporter = StandardChatReporter()
        reporter.report_creation(document_data)
        
        # Продолжаем обработку триггера (не прерываем цепочку)
        return TriggerResult(success=True, message="Информация о стандарте выведена в чат")
    except Exception as e:
        logger.error(f"Ошибка при обработке триггера создания стандарта для вывода в чат: {str(e)}")
        # Продолжаем обработку триггера, даже если произошла ошибка
        return TriggerResult(success=True, message=f"Ошибка при выводе информации о стандарте в чат: {str(e)}")