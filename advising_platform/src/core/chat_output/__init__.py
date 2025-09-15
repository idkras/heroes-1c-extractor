"""
Пакет для вывода информации в чат при создании документов через систему триггеров.

Этот пакет обеспечивает:
1. Вывод статистики по задачам в чат
2. Вывод 5-почему анализа для инцидентов в чат
3. Вывод RAT и критерия фальсифицируемости для гипотез в чат
4. Вывод ссылок на веб-превью для всех типов документов
"""

import logging

from advising_platform.src.core.chat_output.trigger_reporter import (
    ChatReporter,
    TaskChatReporter,
    IncidentChatReporter,
    HypothesisChatReporter,
    StandardChatReporter,
    ChatReporterFactory,
    process_document_creation_trigger
)

from advising_platform.src.core.chat_output.chat_trigger_integration import (
    initialize_chat_trigger_system,
    register_chat_trigger_handlers
)

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Инициализируем систему вывода в чат при импорте пакета
try:
    success = initialize_chat_trigger_system()
    if success:
        logger.info("Система вывода в чат успешно инициализирована при импорте пакета")
    else:
        logger.warning("Не удалось инициализировать систему вывода в чат при импорте пакета")
except Exception as e:
    logger.error(f"Ошибка при инициализации системы вывода в чат: {str(e)}")

__all__ = [
    'ChatReporter',
    'TaskChatReporter',
    'IncidentChatReporter',
    'HypothesisChatReporter',
    'StandardChatReporter',
    'ChatReporterFactory',
    'process_document_creation_trigger',
    'initialize_chat_trigger_system',
    'register_chat_trigger_handlers'
]