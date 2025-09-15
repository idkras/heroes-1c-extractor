#!/usr/bin/env python3
"""
Обработчики триггеров для кеш-системы.

Цель: Выделить логику обработки триггеров из task_incident_triggers.py
для создания модульной архитектуры кеша.

Автор: AI Assistant
Дата: 22 May 2025
"""

import logging
from typing import Dict, Any, Callable, Optional
from .trigger_types import TriggerType, TriggerContext, validate_trigger_context

logger = logging.getLogger(__name__)


class TriggerHandler:
    """Обработчик триггеров кеш-системы."""
    
    def __init__(self):
        """Инициализация обработчика триггеров."""
        self._handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Настройка обработчиков по умолчанию."""
        self.register_handler(TriggerType.TASK_CREATE, self._handle_task_create)
        self.register_handler(TriggerType.TASK_UPDATE, self._handle_task_update)
        self.register_handler(TriggerType.INCIDENT_CREATE, self._handle_incident_create)
        self.register_handler(TriggerType.CACHE_SYNC, self._handle_cache_sync)
    
    def register_handler(self, trigger_type: str, handler: Callable):
        """
        Регистрирует обработчик для типа триггера.
        
        Args:
            trigger_type: Тип триггера
            handler: Функция-обработчик
        """
        self._handlers[trigger_type] = handler
        logger.info(f"Зарегистрирован обработчик для {trigger_type}")
    
    def process_trigger(self, context: TriggerContext) -> bool:
        """
        Обрабатывает триггер.
        
        Args:
            context: Контекст триггера
            
        Returns:
            True если обработка успешна
        """
        try:
            # Валидация контекста
            if not validate_trigger_context(context):
                logger.error(f"Невалидный контекст триггера: {context}")
                return False
            
            # Поиск обработчика
            handler = self._handlers.get(context.trigger_type)
            if not handler:
                logger.warning(f"Обработчик не найден для типа {context.trigger_type}")
                return False
            
            # Выполнение обработки
            result = handler(context)
            logger.info(f"Триггер {context.trigger_type} обработан успешно")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка обработки триггера {context.trigger_type}: {e}")
            return False
    
    def _handle_task_create(self, context: TriggerContext) -> bool:
        """Обработчик создания задачи."""
        try:
            task_name = context.data.get('task_name')
            task_context = context.data.get('context')
            
            logger.info(f"Создание задачи: {task_name}")
            
            # Здесь будет реальная логика создания задачи
            # Пока возвращаем успех для TDD
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return False
    
    def _handle_task_update(self, context: TriggerContext) -> bool:
        """Обработчик обновления задачи."""
        try:
            task_id = context.data.get('task_id')
            
            logger.info(f"Обновление задачи: {task_id}")
            
            # Здесь будет реальная логика обновления задачи
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления задачи: {e}")
            return False
    
    def _handle_incident_create(self, context: TriggerContext) -> bool:
        """Обработчик создания инцидента."""
        try:
            title = context.data.get('incident_title')
            description = context.data.get('description')
            
            logger.info(f"Создание инцидента: {title}")
            
            # Здесь будет реальная логика создания инцидента
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания инцидента: {e}")
            return False
    
    def _handle_cache_sync(self, context: TriggerContext) -> bool:
        """Обработчик синхронизации кеша."""
        try:
            logger.info("Выполнение синхронизации кеша")
            
            # Здесь будет реальная логика синхронизации
            return True
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации кеша: {e}")
            return False
    
    def get_registered_handlers(self) -> list:
        """Возвращает список зарегистрированных типов триггеров."""
        return list(self._handlers.keys())


# Глобальный экземпляр обработчика
_global_handler: Optional[TriggerHandler] = None


def get_trigger_handler() -> TriggerHandler:
    """Возвращает глобальный экземпляр обработчика триггеров."""
    global _global_handler
    if _global_handler is None:
        _global_handler = TriggerHandler()
    return _global_handler


def process_trigger(trigger_type: str, data: Dict[str, Any]) -> bool:
    """
    Упрощенный интерфейс для обработки триггера.
    
    Args:
        trigger_type: Тип триггера
        data: Данные триггера
        
    Returns:
        True если обработка успешна
    """
    context = TriggerContext(trigger_type=trigger_type, data=data)
    handler = get_trigger_handler()
    return handler.process_trigger(context)