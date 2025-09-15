"""
Модуль для валидации соответствия реализаций стандартам.

Содержит функции и классы для проверки соответствия программной реализации
требованиям стандартов и обнаружения несоответствий.
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Type, Union

from advising_platform.standards.core.traceable import (
    StandardImplementationInfo,
    get_implemented_standards
)

# Настройка логирования
logger = logging.getLogger(__name__)


class ValidationIssue:
    """Проблема, обнаруженная при валидации."""
    
    def __init__(self, code: str, message: str, severity: str = "error"):
        """
        Инициализирует проблему валидации.
        
        Args:
            code: Код проблемы
            message: Описание проблемы
            severity: Серьезность проблемы (error, warning, info)
        """
        self.code = code
        self.message = message
        self.severity = severity
    
    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.code}: {self.message}"
    
    def to_dict(self) -> Dict[str, str]:
        """Преобразует проблему в словарь."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity
        }


class ValidationResult:
    """Результат валидации реализации стандарта."""
    
    def __init__(
        self,
        standard_info: StandardImplementationInfo,
        issues: Optional[List[ValidationIssue]] = None
    ):
        """
        Инициализирует результат валидации.
        
        Args:
            standard_info: Информация о проверяемом стандарте
            issues: Список обнаруженных проблем
        """
        self.standard_info = standard_info
        self.issues = issues or []
    
    @property
    def is_valid(self) -> bool:
        """Проверяет, является ли реализация действительной."""
        return not any(issue.severity == "error" for issue in self.issues)
    
    def add_issue(self, code: str, message: str, severity: str = "error") -> None:
        """
        Добавляет проблему в результат валидации.
        
        Args:
            code: Код проблемы
            message: Описание проблемы
            severity: Серьезность проблемы (error, warning, info)
        """
        self.issues.append(ValidationIssue(code, message, severity))
    
    def __str__(self) -> str:
        if self.is_valid:
            return f"Валидная реализация: {self.standard_info}"
        
        return f"Невалидная реализация: {self.standard_info}\nПроблемы:\n" + "\n".join(
            f"- {issue}" for issue in self.issues
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует результат валидации в словарь."""
        return {
            "standard_info": self.standard_info.to_dict(),
            "is_valid": self.is_valid,
            "issues": [issue.to_dict() for issue in self.issues]
        }


def validate_implementation(obj: Union[Callable[..., Any], Type[Any]]) -> List[ValidationResult]:
    """
    Проверяет соответствие объекта реализуемым стандартам.
    
    Args:
        obj: Объект для проверки
    
    Returns:
        Список результатов валидации для каждого реализуемого стандарта
    """
    results = []
    
    # Получаем информацию о реализуемых стандартах
    standard_infos = get_implemented_standards(obj)
    
    if not standard_infos:
        logger.warning(f"Объект не реализует ни одного стандарта: {obj}")
        return []
    
    # Проверяем каждый стандарт
    for info in standard_infos:
        result = validate_standard_implementation(info)
        results.append(result)
    
    return results


def validate_standard_implementation(info: StandardImplementationInfo) -> ValidationResult:
    """
    Проверяет соответствие реализации стандарту.
    
    Args:
        info: Информация о реализуемом стандарте
    
    Returns:
        Результат валидации
    """
    result = ValidationResult(info)
    
    # Проверяем наличие документации
    if info.obj_type == "function" or info.obj_type == "method":
        validate_function_implementation(info, result)
    elif info.obj_type == "class":
        validate_class_implementation(info, result)
    else:
        result.add_issue(
            "UNSUPPORTED_TYPE",
            f"Неподдерживаемый тип объекта: {info.obj_type}",
            "error"
        )
    
    return result


def validate_function_implementation(info: StandardImplementationInfo, result: ValidationResult) -> None:
    """
    Проверяет соответствие функции стандарту.
    
    Args:
        info: Информация о реализуемом стандарте
        result: Результат валидации для обновления
    """
    # Проверяем наличие документации
    doc = info.obj.__doc__
    if not doc:
        result.add_issue(
            "MISSING_DOCUMENTATION",
            "Отсутствует документация для функции",
            "warning"
        )
    
    # Проверяем наличие аннотаций типов параметров и возвращаемого значения
    sig = inspect.signature(info.obj)
    for param_name, param in sig.parameters.items():
        if param.annotation == inspect.Parameter.empty:
            result.add_issue(
                "MISSING_TYPE_ANNOTATION",
                f"Отсутствует аннотация типа для параметра '{param_name}'",
                "warning"
            )
    
    if sig.return_annotation == inspect.Signature.empty:
        result.add_issue(
            "MISSING_RETURN_ANNOTATION",
            "Отсутствует аннотация типа возвращаемого значения",
            "warning"
        )


def validate_class_implementation(info: StandardImplementationInfo, result: ValidationResult) -> None:
    """
    Проверяет соответствие класса стандарту.
    
    Args:
        info: Информация о реализуемом стандарте
        result: Результат валидации для обновления
    """
    # Проверяем наличие документации
    doc = info.obj.__doc__
    if not doc:
        result.add_issue(
            "MISSING_DOCUMENTATION",
            "Отсутствует документация для класса",
            "warning"
        )
    
    # Проверяем наличие документации для методов
    for name, method in inspect.getmembers(info.obj, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        
        if not method.__doc__:
            result.add_issue(
                "MISSING_METHOD_DOCUMENTATION",
                f"Отсутствует документация для метода '{name}'",
                "warning"
            )