"""
Ядро системы Standa.

Содержит базовые компоненты для трассировки, обнаружения и валидации
соответствия реализаций стандартам.
"""

from advising_platform.standards.core.traceable import implements_standard
from advising_platform.standards.core.registry import (
    StandardImplementationRegistry,
    get_implementation,
    list_implementations,
    get_implementation_status
)
from advising_platform.standards.core.validation import (
    ValidationResult,
    validate_implementation
)

__all__ = [
    'implements_standard',
    'StandardImplementationRegistry',
    'get_implementation',
    'list_implementations',
    'get_implementation_status',
    'ValidationResult',
    'validate_implementation'
]