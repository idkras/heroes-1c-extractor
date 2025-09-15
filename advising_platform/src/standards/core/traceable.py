"""
Модуль для обеспечения отслеживаемости реализации стандартов.
"""

import functools
import inspect
from typing import Dict, Any, Optional, Callable, Type, Union, List, Set, Tuple

class StandardImplementation:
    """
    Информация о реализации стандарта в коде.
    """
    
    def __init__(self, 
                standard_id: str, 
                version: str, 
                section: Optional[str] = None,
                implementation_notes: Optional[str] = None):
        """
        Инициализирует информацию о реализации стандарта.
        
        Args:
            standard_id: Идентификатор стандарта
            version: Версия стандарта
            section: Раздел стандарта (опционально)
            implementation_notes: Заметки по реализации (опционально)
        """
        self.standard_id = standard_id
        self.version = version
        self.section = section
        self.implementation_notes = implementation_notes

def implements_standard(standard_id: str, 
                       version: str, 
                       section: Optional[str] = None,
                       implementation_notes: Optional[str] = None) -> Callable:
    """
    Декоратор для обозначения реализации стандарта.
    
    Args:
        standard_id: Идентификатор стандарта
        version: Версия стандарта
        section: Раздел стандарта (опционально)
        implementation_notes: Заметки по реализации (опционально)
        
    Returns:
        Декоратор для функции или класса
    """
    def decorator(obj: Any) -> Any:
        # Создаем информацию о реализации стандарта
        implementation = StandardImplementation(
            standard_id=standard_id,
            version=version,
            section=section,
            implementation_notes=implementation_notes
        )
        
        # Сохраняем информацию о реализации стандарта
        if not hasattr(obj, '_standard_implementations'):
            obj._standard_implementations = []
        
        obj._standard_implementations.append(implementation)
        
        return obj
    
    return decorator

def get_standard_implementations(obj: Any) -> List[StandardImplementation]:
    """
    Возвращает информацию о реализациях стандартов для объекта.
    
    Args:
        obj: Объект для проверки
        
    Returns:
        Список реализаций стандартов
    """
    if hasattr(obj, '_standard_implementations'):
        return obj._standard_implementations
    
    return []

def find_implementations(standard_id: str, version: Optional[str] = None) -> Dict[str, List[StandardImplementation]]:
    """
    Ищет реализации стандарта в загруженных модулях.
    
    Args:
        standard_id: Идентификатор стандарта
        version: Версия стандарта (опционально)
        
    Returns:
        Словарь {имя_объекта: список_реализаций}
    """
    import sys
    
    result = {}
    
    # Перебираем все загруженные модули
    for module_name, module in sys.modules.items():
        if not module_name.startswith('advising_platform'):
            continue
        
        # Получаем все объекты модуля
        for name, obj in inspect.getmembers(module):
            implementations = get_standard_implementations(obj)
            
            if not implementations:
                continue
            
            # Фильтруем по стандарту и версии
            filtered_implementations = [
                impl for impl in implementations
                if impl.standard_id == standard_id and (version is None or impl.version == version)
            ]
            
            if filtered_implementations:
                result[f"{module_name}.{name}"] = filtered_implementations
    
    return result