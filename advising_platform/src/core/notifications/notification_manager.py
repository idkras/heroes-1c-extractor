"""
Модуль управления уведомлениями для системы отслеживания задач.

Предоставляет интерфейс для отправки уведомлений о различных событиях,
таких как создание, обновление и завершение задач, через различные каналы связи.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import logging
import os
import json
import time
import threading
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set, Callable

# Настройка логирования
logger = logging.getLogger("notification_manager")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class NotificationChannel(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса NotificationChannel, чтобы эффективно решать соответствующие задачи в системе.
    
    Поддерживаемые каналы для отправки уведомлений."""
    CONSOLE = "console"         # Вывод в консоль (для отладки)
    EMAIL = "email"             # Отправка по электронной почте
    SLACK = "slack"             # Отправка в Slack
    TELEGRAM = "telegram"       # Отправка в Telegram
    WEBHOOK = "webhook"         # Отправка через webhook
    SYSTEM_LOG = "system_log"   # Запись в системный лог


class NotificationPriority(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса NotificationPriority, чтобы эффективно решать соответствующие задачи в системе.
    
    Приоритеты уведомлений."""
    LOW = "low"                 # Низкий приоритет
    NORMAL = "normal"           # Обычный приоритет
    HIGH = "high"               # Высокий приоритет
    CRITICAL = "critical"       # Критический приоритет


class NotificationType(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса NotificationType, чтобы эффективно решать соответствующие задачи в системе.
    
    Типы событий для уведомлений."""
    ITEM_CREATED = "item_created"         # Создан новый элемент
    ITEM_UPDATED = "item_updated"         # Обновлен элемент
    ITEM_DELETED = "item_deleted"         # Удален элемент
    RELATION_ADDED = "relation_added"     # Добавлена связь
    RELATION_REMOVED = "relation_removed" # Удалена связь
    STATUS_CHANGED = "status_changed"     # Изменен статус
    DEADLINE_APPROACHING = "deadline_approaching"  # Приближается дедлайн
    DEADLINE_MISSED = "deadline_missed"   # Пропущен дедлайн
    SYSTEM_WARNING = "system_warning"     # Системное предупреждение
    SYSTEM_ERROR = "system_error"         # Системная ошибка


class NotificationManager:
    """
    Менеджер уведомлений для отправки сообщений через различные каналы.
    
    Обеспечивает централизованный интерфейс для отправки уведомлений
    о различных событиях, таких как создание, обновление и завершение задач,
    через различные каналы связи.
    """
    
    def __init__(
        self,
        config_path: str = "advising_platform/config/notifications.json",
        enabled_channels: Optional[List[NotificationChannel]] = None
    ):
        """
        Инициализация менеджера уведомлений.
        
        Args:
            config_path: Путь к файлу конфигурации
            enabled_channels: Список активированных каналов (если None, используются все каналы из конфигурации)
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Если не указаны активированные каналы, используем все из конфигурации
        if enabled_channels is None:
            enabled_channels = [
                NotificationChannel(channel) 
                for channel in self.config.get("enabled_channels", ["console"])
            ]
        
        self.enabled_channels = enabled_channels
        self.notification_queue = []
        self.is_running = False
        self.thread = None
        
        # Загружаем конфигурации для каждого канала
        self.channel_configs = {
            channel: self.config.get(channel.value, {})
            for channel in NotificationChannel
        }
        
        logger.info(f"Менеджер уведомлений инициализирован с каналами: {[ch.value for ch in self.enabled_channels]}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Загружает конфигурацию из файла.
        
        Returns:
            Словарь с конфигурацией
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Если файл не существует, создаем базовую конфигурацию
                default_config = {
                    "enabled_channels": ["console", "system_log"],
                    "console": {"enabled": True},
                    "email": {"enabled": False},
                    "slack": {"enabled": False},
                    "telegram": {"enabled": False},
                    "webhook": {"enabled": False},
                    "system_log": {"enabled": True, "log_file": "advising_platform/logs/notifications.log"}
                }
                
                # Создаем директорию, если не существует
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                
                # Сохраняем базовую конфигурацию
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                
                logger.info(f"Создана базовая конфигурация уведомлений в {self.config_path}")
                return default_config
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации уведомлений: {e}")
            return {
                "enabled_channels": ["console"],
                "console": {"enabled": True}
            }
    
    def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> bool:
        """
        Отправляет уведомление через указанные каналы.
        
        Args:
            notification_type: Тип уведомления
            title: Заголовок уведомления
            message: Текст уведомления
            data: Дополнительные данные для уведомления
            channels: Список каналов для отправки (если None, используются все активированные каналы)
            priority: Приоритет уведомления
            
        Returns:
            True, если уведомление отправлено успешно, иначе False
        """
        if channels is None:
            channels = self.enabled_channels
        
        if data is None:
            data = {}
        
        notification = {
            "type": notification_type.value,
            "title": title,
            "message": message,
            "data": data,
            "priority": priority.value,
            "timestamp": time.time()
        }
        
        success = True
        for channel in channels:
            if channel in self.enabled_channels:
                try:
                    if channel == NotificationChannel.CONSOLE:
                        self._send_console_notification(notification)
                    elif channel == NotificationChannel.EMAIL:
                        self._send_email_notification(notification)
                    elif channel == NotificationChannel.SLACK:
                        self._send_slack_notification(notification)
                    elif channel == NotificationChannel.TELEGRAM:
                        self._send_telegram_notification(notification)
                    elif channel == NotificationChannel.WEBHOOK:
                        self._send_webhook_notification(notification)
                    elif channel == NotificationChannel.SYSTEM_LOG:
                        self._send_system_log_notification(notification)
                    else:
                        logger.warning(f"Неизвестный канал уведомлений: {channel}")
                        success = False
                except Exception as e:
                    logger.error(f"Ошибка при отправке уведомления через канал {channel.value}: {e}")
                    success = False
        
        return success
    
    def _send_console_notification(self, notification: Dict[str, Any]) -> None:
        """
        Отправляет уведомление в консоль.
        
        Args:
            notification: Данные уведомления
        """
        priority_color = {
            "low": "\033[94m",      # Синий
            "normal": "\033[92m",    # Зеленый
            "high": "\033[93m",      # Желтый
            "critical": "\033[91m"   # Красный
        }
        
        reset_color = "\033[0m"
        
        color = priority_color.get(notification["priority"], "\033[0m")
        
        print(f"\n{color}======= УВЕДОМЛЕНИЕ =======")
        print(f"Тип: {notification['type']}")
        print(f"Приоритет: {notification['priority']}")
        print(f"Заголовок: {notification['title']}")
        print(f"Сообщение: {notification['message']}")
        print(f"Данные: {notification['data']}")
        print(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(notification['timestamp']))}")
        print(f"============================={reset_color}\n")
    
    def _send_email_notification(self, notification: Dict[str, Any]) -> None:
        """
        Отправляет уведомление по электронной почте.
        
        Args:
            notification: Данные уведомления
        """
        logger.info(f"Отправка уведомления по email: {notification['title']}")
        # Здесь будет реализация отправки по email
        # Для настоящей отправки можно использовать smtplib
    
    def _send_slack_notification(self, notification: Dict[str, Any]) -> None:
        """
        Отправляет уведомление в Slack.
        
        Args:
            notification: Данные уведомления
        """
        logger.info(f"Отправка уведомления в Slack: {notification['title']}")
        # Здесь будет реализация отправки в Slack
        # Для настоящей отправки можно использовать webhooks или Slack API
    
    def _send_telegram_notification(self, notification: Dict[str, Any]) -> None:
        """
        Отправляет уведомление в Telegram.
        
        Args:
            notification: Данные уведомления
        """
        logger.info(f"Отправка уведомления в Telegram: {notification['title']}")
        # Здесь будет реализация отправки в Telegram
        # Для настоящей отправки можно использовать Telegram Bot API
    
    def _send_webhook_notification(self, notification: Dict[str, Any]) -> None:
        """
        Отправляет уведомление через webhook.
        
        Args:
            notification: Данные уведомления
        """
        logger.info(f"Отправка уведомления через webhook: {notification['title']}")
        # Здесь будет реализация отправки через webhook
        # Для настоящей отправки можно использовать requests
    
    def _send_system_log_notification(self, notification: Dict[str, Any]) -> None:
        """
        Отправляет уведомление в системный лог.
        
        Args:
            notification: Данные уведомления
        """
        log_level = {
            "low": logging.DEBUG,
            "normal": logging.INFO,
            "high": logging.WARNING,
            "critical": logging.ERROR
        }.get(notification["priority"], logging.INFO)
        
        log_message = (
            f"[{notification['type']}] {notification['title']}: {notification['message']} "
            f"(Данные: {notification['data']})"
        )
        
        logger.log(log_level, log_message)
    
    def start_background_worker(self) -> None:
        """
        Запускает фоновый поток для обработки очереди уведомлений.
        """
        if self.is_running:
            logger.warning("Фоновый обработчик уведомлений уже запущен")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._background_worker, daemon=True)
        self.thread.start()
        logger.info("Запущен фоновый обработчик уведомлений")
    
    def stop_background_worker(self) -> None:
        """
        Останавливает фоновый поток для обработки очереди уведомлений.
        """
        if not self.is_running:
            logger.warning("Фоновый обработчик уведомлений не запущен")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        logger.info("Остановлен фоновый обработчик уведомлений")
    
    def _background_worker(self) -> None:
        """
        Фоновый поток для обработки очереди уведомлений.
        """
        logger.info("Фоновый обработчик уведомлений запущен")
        
        while self.is_running:
            try:
                # Проверяем очередь уведомлений
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    self.send_notification(**notification)
                else:
                    # Если очередь пуста, ждем немного
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Ошибка в фоновом обработчике уведомлений: {e}")
                time.sleep(1.0)  # Пауза перед следующей попыткой
        
        logger.info("Фоновый обработчик уведомлений остановлен")
    
    def add_to_queue(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> None:
        """
        Добавляет уведомление в очередь для обработки фоновым потоком.
        
        Args:
            notification_type: Тип уведомления
            title: Заголовок уведомления
            message: Текст уведомления
            data: Дополнительные данные для уведомления
            channels: Список каналов для отправки (если None, используются все активированные каналы)
            priority: Приоритет уведомления
        """
        notification = {
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "data": data,
            "channels": channels,
            "priority": priority
        }
        
        self.notification_queue.append(notification)
        logger.debug(f"Добавлено уведомление в очередь: {title}")
    
    def __del__(self):
        """Деструктор для остановки фонового потока."""
        self.stop_background_worker()


# Глобальный экземпляр менеджера уведомлений для удобного использования
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """
    Получает глобальный экземпляр менеджера уведомлений.
    
    Returns:
        Экземпляр менеджера уведомлений
    """
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    
    return _notification_manager


def send_notification(
    notification_type: NotificationType,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    channels: Optional[List[NotificationChannel]] = None,
    priority: NotificationPriority = NotificationPriority.NORMAL
) -> bool:
    """
    Отправляет уведомление через глобальный менеджер уведомлений.
    
    Args:
        notification_type: Тип уведомления
        title: Заголовок уведомления
        message: Текст уведомления
        data: Дополнительные данные для уведомления
        channels: Список каналов для отправки (если None, используются все активированные каналы)
        priority: Приоритет уведомления
        
    Returns:
        True, если уведомление отправлено успешно, иначе False
    """
    return get_notification_manager().send_notification(
        notification_type=notification_type,
        title=title,
        message=message,
        data=data,
        channels=channels,
        priority=priority
    )