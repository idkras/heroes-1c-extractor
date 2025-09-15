#!/usr/bin/env python3
"""
🚀 Event Bus для межкомпонентного взаимодействия

JTBD: Как event bus, я хочу обеспечить decoupled communication между компонентами,
чтобы система была более модульной и расширяемой.

Автор: AI Assistant
Дата: 25 May 2025
"""

import threading
import logging
import time
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class EventMessage:
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.NORMAL

class EventSubscriber:
    def __init__(self, callback: Callable[[EventMessage], bool], topics: List[str], name: str):
        self.callback = callback
        self.topics = set(topics)
        self.name = name
        self.processed_count = 0
    
    def can_process(self, message: EventMessage) -> bool:
        return message.topic in self.topics or '*' in self.topics
    
    def process(self, message: EventMessage) -> bool:
        try:
            result = self.callback(message)
            if result:
                self.processed_count += 1
            return result
        except Exception as e:
            logger.error(f"Subscriber {self.name} error: {e}")
            return False

class EventBusAdvanced:
    def __init__(self):
        self.subscribers: List[EventSubscriber] = []
        self._lock = threading.RLock()
    
    def subscribe(self, subscriber: EventSubscriber):
        with self._lock:
            self.subscribers.append(subscriber)
            logger.info(f"Subscribed: {subscriber.name}")
    
    def publish(self, topic: str, payload: Dict[str, Any], priority: Priority = Priority.NORMAL) -> str:
        message = EventMessage(topic=topic, payload=payload, priority=priority)
        
        for subscriber in self.subscribers:
            if subscriber.can_process(message):
                subscriber.process(message)
        
        return f"msg_{datetime.now().timestamp()}"

# Глобальный экземпляр
_global_event_bus: Optional[EventBusAdvanced] = None

def get_event_bus() -> EventBusAdvanced:
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBusAdvanced()
    return _global_event_bus