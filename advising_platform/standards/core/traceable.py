"""
Модуль для трассировки связи между программной реализацией и стандартами.

Содержит декораторы и утилиты для явного указания связи между кодом
и соответствующими стандартами.
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

# Типы для аннотаций
F = TypeVar('F', bound=Callable[..., Any])
C = TypeVar('C', bound=Type[Any])


class StandardImplementationInfo:
    """Информация о реализации стандарта."""
    
    def __init__(
        self,
        standard_id: str,
        version: str,
        component: str,
        obj: Union[Callable[..., Any], Type[Any]],
        description: Optional[str] = None
    ):
        """
        Инициализирует информацию о реализации стандарта.
        
        Args:
            standard_id: Идентификатор стандарта
            version: Версия стандарта
            component: Компонент стандарта
            obj: Объект, реализующий стандарт
            description: Описание реализации
        """
        self.standard_id = standard_id
        self.version = version
        self.component = component
        self.obj = obj
        self.description = description or ""
        
        # Безопасное получение имени модуля
        module_obj = inspect.getmodule(obj)
        self.module = module_obj.__name__ if module_obj and hasattr(module_obj, "__name__") else ""
        
        # Определение типа объекта
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            self.obj_type = "function"
        elif inspect.isclass(obj):
            self.obj_type = "class"
        else:
            self.obj_type = "other"
    
    def __str__(self) -> str:
        obj_name = getattr(self.obj, "__name__", str(self.obj))
        return (f"{self.standard_id}:{self.version}:{self.component} - "
                f"{self.obj_type} {obj_name} from {self.module}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует информацию в словарь."""
        obj_name = getattr(self.obj, "__name__", str(self.obj))
        return {
            "standard_id": self.standard_id,
            "version": self.version,
            "component": self.component,
            "obj_name": obj_name,
            "obj_type": self.obj_type,
            "module": self.module,
            "description": self.description
        }


# Глобальный реестр реализаций стандартов
_standard_implementations: List[StandardImplementationInfo] = []


def get_standard_implementations() -> List[StandardImplementationInfo]:
    """
    Возвращает список всех зарегистрированных реализаций стандартов.
    
    Returns:
        Список информации о реализациях стандартов
    """
    return _standard_implementations


def implements_standard(
    standard_id: str,
    version: str,
    component: str,
    description: Optional[str] = None
) -> Callable[[F], F]:
    """
    Декоратор для маркировки функций и классов как реализаций стандартов.
    
    Args:
        standard_id: Идентификатор стандарта
        version: Версия стандарта
        component: Компонент стандарта
        description: Описание реализации
    
    Returns:
        Декоратор, регистрирующий функцию или класс как реализацию стандарта
    """
    def decorator(obj: F) -> F:
        info = StandardImplementationInfo(
            standard_id, version, component, obj, description
        )
        _standard_implementations.append(info)
        
        # Сохраняем информацию о стандарте в атрибутах объекта
        if not hasattr(obj, "__standard_implementations__"):
            setattr(obj, "__standard_implementations__", [])
        
        getattr(obj, "__standard_implementations__").append(info)
        
        return obj
    
    return decorator


def get_implemented_standards(obj: Union[Callable[..., Any], Type[Any]]) -> List[StandardImplementationInfo]:
    """
    Возвращает список стандартов, реализуемых объектом.
    
    Args:
        obj: Объект для проверки
    
    Returns:
        Список информации о реализуемых стандартах
    """
    return getattr(obj, "__standard_implementations__", [])