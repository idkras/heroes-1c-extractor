#!/usr/bin/env python3
"""
Определения типов триггеров для кеш-системы.

Цель: Выделить типы триггеров из большого модуля task_incident_triggers.py
для улучшения структуры и тестируемости.

Автор: AI Assistant
Дата: 22 May 2025
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class TriggerType:
    """Типы триггеров в системе кеша."""
    
    # Триггеры для задач
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    
    # Триггеры для инцидентов
    INCIDENT_CREATE = "incident_create"
    INCIDENT_UPDATE = "incident_update"
    INCIDENT_RESOLVE = "incident_resolve"
    
    # Триггеры для гипотез
    HYPOTHESIS_CREATE = "hypothesis_create"
    HYPOTHESIS_UPDATE = "hypothesis_update"
    
    # Триггеры для стандартов
    STANDARD_CREATE = "standard_create"
    STANDARD_UPDATE = "standard_update"
    
    # Триггеры кеша
    CACHE_SYNC = "cache_sync"
    CACHE_CLEAR = "cache_clear"
    
    # Системные триггеры
    PERIODIC_CHECK = "periodic_check"
    SYSTEM_STARTUP = "system_startup"


@dataclass
class TriggerContext:
    """Контекст выполнения триггера."""
    
    trigger_type: str
    data: Dict[str, Any]
    source_module: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        """Инициализация после создания."""
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class TriggerPriority:
    """Приоритеты выполнения триггеров."""
    
    CRITICAL = 0    # Критические системные операции
    HIGH = 1        # Операции с задачами и инцидентами
    NORMAL = 2      # Обычные операции с документами
    LOW = 3         # Операции кеша и оптимизации


def get_trigger_priority(trigger_type: str) -> int:
    """
    Определяет приоритет триггера по его типу.
    
    Args:
        trigger_type: Тип триггера
        
    Returns:
        Приоритет триггера (0 - критический, 3 - низкий)
    """
    critical_triggers = {
        TriggerType.SYSTEM_STARTUP,
        TriggerType.INCIDENT_CREATE,
        TriggerType.INCIDENT_RESOLVE
    }
    
    high_triggers = {
        TriggerType.TASK_CREATE,
        TriggerType.TASK_COMPLETE,
        TriggerType.STANDARD_CREATE
    }
    
    normal_triggers = {
        TriggerType.TASK_UPDATE,
        TriggerType.INCIDENT_UPDATE,
        TriggerType.STANDARD_UPDATE,
        TriggerType.HYPOTHESIS_CREATE,
        TriggerType.HYPOTHESIS_UPDATE
    }
    
    if trigger_type in critical_triggers:
        return TriggerPriority.CRITICAL
    elif trigger_type in high_triggers:
        return TriggerPriority.HIGH
    elif trigger_type in normal_triggers:
        return TriggerPriority.NORMAL
    else:
        return TriggerPriority.LOW


def validate_trigger_context(context: TriggerContext) -> bool:
    """
    Проверяет корректность контекста триггера.
    
    Args:
        context: Контекст триггера
        
    Returns:
        True, если контекст корректен
    """
    if not context.trigger_type:
        return False
        
    if not isinstance(context.data, dict):
        return False
    
    # Проверяем наличие обязательных полей для разных типов триггеров
    required_fields = get_required_fields(context.trigger_type)
    
    for field in required_fields:
        if field not in context.data:
            return False
    
    return True


def get_required_fields(trigger_type: str) -> list:
    """
    Возвращает список обязательных полей для типа триггера.
    
    Args:
        trigger_type: Тип триггера
        
    Returns:
        Список обязательных полей
    """
    field_mapping = {
        TriggerType.TASK_CREATE: ['task_name', 'context'],
        TriggerType.TASK_UPDATE: ['task_id'],
        TriggerType.TASK_COMPLETE: ['task_id'],
        TriggerType.INCIDENT_CREATE: ['incident_title', 'description'],
        TriggerType.INCIDENT_UPDATE: ['incident_id'],
        TriggerType.STANDARD_CREATE: ['standard_name', 'content'],
        TriggerType.STANDARD_UPDATE: ['standard_id'],
        TriggerType.HYPOTHESIS_CREATE: ['hypothesis_text'],
        TriggerType.CACHE_SYNC: [],
        TriggerType.PERIODIC_CHECK: []
    }
    
    return field_mapping.get(trigger_type, [])