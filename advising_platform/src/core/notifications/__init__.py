"""
Пакет для управления уведомлениями в системе.

Предоставляет механизмы для отправки уведомлений о создании, обновлении и
других событиях, связанных с рабочими элементами (задачами, инцидентами и т.д.).
"""

from advising_platform.src.core.notifications.notification_manager import (
    NotificationManager, NotificationChannel, NotificationType, NotificationPriority,
    get_notification_manager, send_notification
)

__all__ = [
    'NotificationManager',
    'NotificationChannel',
    'NotificationType',
    'NotificationPriority',
    'get_notification_manager',
    'send_notification'
]