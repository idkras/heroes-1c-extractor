"""
Standa - Система программной реализации стандартов.

Этот пакет содержит централизованные реализации всех стандартов проекта,
обеспечивая единую точку истины и предотвращая рассинхронизацию между
стандартами и их программной реализацией.

Основные возможности:
- Трассировка связей между стандартами и их реализациями
- Автоматическое обнаружение несоответствий
- Централизованный репозиторий реализаций стандартов
- Версионирование реализаций в соответствии с версиями стандартов
"""

from advising_platform.standards.core.registry import (
    get_implementation,
    list_implementations,
    get_implementation_status
)

from advising_platform.standards.core.traceable import implements_standard

__all__ = [
    'implements_standard',
    'get_implementation',
    'list_implementations',
    'get_implementation_status'
]