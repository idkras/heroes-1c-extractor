"""
🚀 Events package для event-driven автоматизации

JTBD: Как events package, я хочу предоставить компоненты для событийной архитектуры,
чтобы система могла работать в event-driven режиме.
"""

from .event_system import EventSystem, EventType, Event, get_event_system, start_event_system
from .event_bus import EventBusAdvanced, EventSubscriber, Priority, get_event_bus

__all__ = [
    'EventSystem', 'EventType', 'Event', 'get_event_system', 'start_event_system',
    'EventBusAdvanced', 'EventSubscriber', 'Priority', 'get_event_bus'
]