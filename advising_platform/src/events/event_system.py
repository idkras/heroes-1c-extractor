#!/usr/bin/env python3
"""
🚀 Event-driven система для автоматизации workflow

JTBD: Как событийная система, я хочу обеспечить автоматический запуск триггеров при изменениях,
чтобы система работала event-driven и реагировала на изменения в real-time.

Основано на: dependency_mapping.md анализе
Стандарт: TDD-doc + RADAR принципы
Автор: AI Assistant
Дата: 25 May 2025
"""

import os
import time
import threading
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """
    JTBD: Как типизация событий, я хочу определить все возможные типы событий в системе,
    чтобы обеспечить type safety и clear contracts.
    """
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    CACHE_UPDATED = "cache_updated"
    TASK_COMPLETED = "task_completed"
    TRIGGER_EXECUTED = "trigger_executed"
    SYSTEM_HEALTH_CHECK = "system_health_check"


@dataclass
class Event:
    """
    JTBD: Как структура события, я хочу содержать всю необходимую информацию о событии,
    чтобы handlers могли принимать правильные решения.
    """
    event_type: EventType
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EventHandler(ABC):
    """
    JTBD: Как абстрактный event handler, я хочу определить контракт для обработки событий,
    чтобы все handlers имели единообразный interface.
    """
    
    @abstractmethod
    def can_handle(self, event: Event) -> bool:
        """Проверяет, может ли handler обработать событие"""
        pass
    
    @abstractmethod
    def handle(self, event: Event) -> bool:
        """Обрабатывает событие и возвращает результат"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Имя handler'а для логирования"""
        pass


class FileWatcherHandler(EventHandler):
    """
    JTBD: Как file watcher handler, я хочу обрабатывать события изменения файлов,
    чтобы запускать соответствующие триггеры и обновления.
    """
    
    def __init__(self, target_patterns: List[str]):
        self.target_patterns = target_patterns
    
    @property
    def name(self) -> str:
        return "FileWatcherHandler"
    
    def can_handle(self, event: Event) -> bool:
        if event.event_type not in [EventType.FILE_CREATED, EventType.FILE_MODIFIED, EventType.FILE_DELETED]:
            return False
        
        file_path = event.data.get('file_path', '')
        return any(self._matches_pattern(file_path, pattern) for pattern in self.target_patterns)
    
    def handle(self, event: Event) -> bool:
        try:
            file_path = event.data.get('file_path', '')
            logger.info(f"FileWatcherHandler: Processing {event.event_type.value} for {file_path}")
            
            if 'todo.md' in file_path:
                self._trigger_task_completion_update(file_path)
            elif '[standards .md]' in file_path or file_path.endswith('.md'):
                self._trigger_cache_update(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"FileWatcherHandler error: {e}")
            return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        import fnmatch
        return fnmatch.fnmatch(os.path.basename(file_path), pattern)
    
    def _trigger_task_completion_update(self, file_path: str):
        logger.info(f"Triggering task completion update for {file_path}")
        
    def _trigger_cache_update(self, file_path: str):
        logger.info(f"Triggering cache update for {file_path}")


class EventBus:
    """
    JTBD: Как event bus, я хочу обеспечить централизованную отправку и обработку событий,
    чтобы компоненты системы могли взаимодействовать через события.
    """
    
    def __init__(self):
        self.handlers: List[EventHandler] = []
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        self._lock = threading.RLock()
    
    def add_handler(self, handler: EventHandler):
        with self._lock:
            self.handlers.append(handler)
            logger.info(f"Added event handler: {handler.name}")
    
    def publish(self, event: Event) -> Dict[str, bool]:
        results = {}
        
        with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)
            
            logger.info(f"Publishing event: {event.event_type.value} from {event.source}")
            
            for handler in self.handlers:
                if handler.can_handle(event):
                    try:
                        result = handler.handle(event)
                        results[handler.name] = result
                        logger.info(f"Handler {handler.name}: {'Success' if result else 'Failed'}")
                    except Exception as e:
                        results[handler.name] = False
                        logger.error(f"Handler {handler.name} error: {e}")
        
        return results


class EventSystem:
    """
    JTBD: Как основная event system, я хочу предоставить high-level API для event-driven automation,
    чтобы система могла легко интегрироваться с событийной моделью.
    """
    
    def __init__(self):
        self.event_bus = EventBus()
        self.is_running = False
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        file_watcher = FileWatcherHandler(['todo.md', '*.md', 'ai.incidents.md'])
        self.event_bus.add_handler(file_watcher)
        logger.info("EventSystem: Default handlers configured")
    
    def start(self):
        self.is_running = True
        logger.info("EventSystem: Started")
        self._schedule_health_checks()
    
    def stop(self):
        self.is_running = False
        logger.info("EventSystem: Stopped")
    
    def emit_file_event(self, event_type: EventType, file_path: str, metadata: Optional[Dict] = None):
        event = Event(
            event_type=event_type,
            source="FileSystem",
            timestamp=datetime.now(),
            data={'file_path': file_path},
            metadata=metadata or {}
        )
        return self.event_bus.publish(event)
    
    def _schedule_health_checks(self):
        def health_check_worker():
            while self.is_running:
                try:
                    health_event = Event(
                        event_type=EventType.SYSTEM_HEALTH_CHECK,
                        source="EventSystem",
                        timestamp=datetime.now(),
                        data={}
                    )
                    self.event_bus.publish(health_event)
                    time.sleep(30)
                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    time.sleep(30)
        
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
        logger.info("EventSystem: Health check scheduler started")


# Глобальный экземпляр
_global_event_system: Optional[EventSystem] = None

def get_event_system() -> EventSystem:
    global _global_event_system
    if _global_event_system is None:
        _global_event_system = EventSystem()
    return _global_event_system

def start_event_system():
    event_system = get_event_system()
    event_system.start()
    return event_system