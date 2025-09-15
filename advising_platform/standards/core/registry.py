"""
Модуль для регистрации и поиска реализаций стандартов.

Обеспечивает централизованный реестр всех программных реализаций стандартов
и возможность их поиска по различным критериям.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from advising_platform.standards.core.traceable import (
    StandardImplementationInfo,
    get_standard_implementations
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Типы для аннотаций
T = TypeVar('T')


class ImplementationStatus:
    """Статус реализации стандарта."""
    
    def __init__(
        self,
        is_implemented: bool,
        is_current: bool,
        current_version: Optional[str] = None,
        implementation_version: Optional[str] = None
    ):
        """
        Инициализирует статус реализации стандарта.
        
        Args:
            is_implemented: Флаг наличия реализации
            is_current: Флаг соответствия текущей версии стандарта
            current_version: Текущая версия стандарта
            implementation_version: Версия реализации
        """
        self.is_implemented = is_implemented
        self.is_current = is_current
        self.current_version = current_version
        self.implementation_version = implementation_version
    
    def __str__(self) -> str:
        if not self.is_implemented:
            return "Not implemented"
        
        if self.is_current:
            return f"Current (v{self.current_version})"
        
        return f"Outdated (implementation: v{self.implementation_version}, current: v{self.current_version})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует статус в словарь."""
        return {
            "is_implemented": self.is_implemented,
            "is_current": self.is_current,
            "current_version": self.current_version,
            "implementation_version": self.implementation_version
        }


class StandardImplementationRegistry:
    """Реестр реализаций стандартов."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для реестра реализаций стандартов."""
        if cls._instance is None:
            cls._instance = super(StandardImplementationRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует реестр реализаций стандартов."""
        if getattr(self, '_initialized', False):
            return
        
        self._implementations: Dict[str, Dict[str, Dict[str, StandardImplementationInfo]]] = {}
        self._current_versions: Dict[str, str] = {}
        self._initialized = True
        
        # Загружаем все известные реализации
        self._load_implementations()
        
        logger.info("Инициализирован реестр реализаций стандартов")
    
    def _load_implementations(self) -> None:
        """Загружает все известные реализации стандартов."""
        for info in get_standard_implementations():
            self.register_implementation_info(info)
    
    def register_implementation_info(self, info: StandardImplementationInfo) -> None:
        """
        Регистрирует информацию о реализации стандарта.
        
        Args:
            info: Информация о реализации
        """
        # Создаем структуру при необходимости
        if info.standard_id not in self._implementations:
            self._implementations[info.standard_id] = {}
        
        if info.version not in self._implementations[info.standard_id]:
            self._implementations[info.standard_id][info.version] = {}
        
        # Регистрируем реализацию
        self._implementations[info.standard_id][info.version][info.component] = info
        
        # Обновляем информацию о текущей версии стандарта
        if info.standard_id not in self._current_versions or self._compare_versions(info.version, self._current_versions[info.standard_id]) > 0:
            self._current_versions[info.standard_id] = info.version
        
        logger.info(f"Зарегистрирована реализация: {info}")
    
    def register_implementation(
        self,
        standard_id: str,
        version: str,
        component: str,
        obj: Union[Callable[..., Any], Type[Any]],
        description: Optional[str] = None
    ) -> None:
        """
        Регистрирует реализацию стандарта.
        
        Args:
            standard_id: Идентификатор стандарта
            version: Версия стандарта
            component: Компонент стандарта
            obj: Объект, реализующий стандарт
            description: Описание реализации
        """
        info = StandardImplementationInfo(standard_id, version, component, obj, description)
        self.register_implementation_info(info)
    
    def get_implementation(self, standard_id: str, version: str, component: str) -> Optional[Any]:
        """
        Возвращает реализацию стандарта.
        
        Args:
            standard_id: Идентификатор стандарта
            version: Версия стандарта
            component: Компонент стандарта
        
        Returns:
            Объект, реализующий стандарт, или None, если реализация не найдена
        """
        try:
            info = self._implementations[standard_id][version][component]
            return info.obj
        except KeyError:
            logger.warning(f"Реализация не найдена: {standard_id}:{version}:{component}")
            return None
    
    def get_latest_implementation(self, standard_id: str, component: str) -> Optional[Any]:
        """
        Возвращает последнюю версию реализации стандарта.
        
        Args:
            standard_id: Идентификатор стандарта
            component: Компонент стандарта
        
        Returns:
            Объект, реализующий последнюю версию стандарта, или None, если реализация не найдена
        """
        if standard_id not in self._current_versions:
            logger.warning(f"Стандарт не найден: {standard_id}")
            return None
        
        version = self._current_versions[standard_id]
        return self.get_implementation(standard_id, version, component)
    
    def list_implementations(self, standard_id: Optional[str] = None) -> List[StandardImplementationInfo]:
        """
        Возвращает список всех реализаций стандартов.
        
        Args:
            standard_id: Идентификатор стандарта для фильтрации (опционально)
        
        Returns:
            Список информации о реализациях стандартов
        """
        result = []
        
        if standard_id:
            # Фильтрация по стандарту
            if standard_id not in self._implementations:
                return []
            
            for version_dict in self._implementations[standard_id].values():
                for info in version_dict.values():
                    result.append(info)
        else:
            # Все реализации
            for standard_dict in self._implementations.values():
                for version_dict in standard_dict.values():
                    for info in version_dict.values():
                        result.append(info)
        
        return result
    
    def get_implementation_status(
        self,
        standard_id: str,
        component: str
    ) -> ImplementationStatus:
        """
        Возвращает статус реализации стандарта.
        
        Args:
            standard_id: Идентификатор стандарта
            component: Компонент стандарта
        
        Returns:
            Статус реализации
        """
        # Проверяем наличие стандарта
        if standard_id not in self._current_versions:
            return ImplementationStatus(False, False)
        
        current_version = self._current_versions[standard_id]
        
        # Проверяем наличие компонента в текущей версии
        if (
            standard_id in self._implementations and
            current_version in self._implementations[standard_id] and
            component in self._implementations[standard_id][current_version]
        ):
            # Компонент реализован в текущей версии
            return ImplementationStatus(True, True, current_version, current_version)
        
        # Проверяем наличие компонента в других версиях
        if standard_id in self._implementations:
            for version, components in self._implementations[standard_id].items():
                if component in components:
                    # Компонент реализован в другой версии
                    return ImplementationStatus(
                        True, False, current_version, version
                    )
        
        # Компонент не реализован
        return ImplementationStatus(False, False, current_version, None)
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Сравнивает версии стандартов.
        
        Args:
            version1: Первая версия
            version2: Вторая версия
        
        Returns:
            1, если version1 > version2
            0, если version1 == version2
            -1, если version1 < version2
        """
        # Простая реализация сравнения версий
        try:
            # Пытаемся преобразовать к числам
            v1_parts = [float(part) for part in version1.split('.')]
            v2_parts = [float(part) for part in version2.split('.')]
            
            # Дополняем более короткую версию нулями
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)
            
            # Сравниваем по порядку
            for i in range(len(v1_parts)):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            
            return 0
        except ValueError:
            # Если не удалось преобразовать к числам, сравниваем как строки
            if version1 > version2:
                return 1
            elif version1 < version2:
                return -1
            return 0


# Создаем глобальный экземпляр реестра
_registry = StandardImplementationRegistry()


def get_implementation(standard_id: str, version: str, component: str) -> Optional[Any]:
    """
    Возвращает реализацию стандарта.
    
    Args:
        standard_id: Идентификатор стандарта
        version: Версия стандарта
        component: Компонент стандарта
    
    Returns:
        Объект, реализующий стандарт, или None, если реализация не найдена
    """
    return _registry.get_implementation(standard_id, version, component)


def get_latest_implementation(standard_id: str, component: str) -> Optional[Any]:
    """
    Возвращает последнюю версию реализации стандарта.
    
    Args:
        standard_id: Идентификатор стандарта
        component: Компонент стандарта
    
    Returns:
        Объект, реализующий последнюю версию стандарта, или None, если реализация не найдена
    """
    return _registry.get_latest_implementation(standard_id, component)


def list_implementations(standard_id: Optional[str] = None) -> List[StandardImplementationInfo]:
    """
    Возвращает список всех реализаций стандартов.
    
    Args:
        standard_id: Идентификатор стандарта для фильтрации (опционально)
    
    Returns:
        Список информации о реализациях стандартов
    """
    return _registry.list_implementations(standard_id)


def get_implementation_status(standard_id: str, component: str) -> ImplementationStatus:
    """
    Возвращает статус реализации стандарта.
    
    Args:
        standard_id: Идентификатор стандарта
        component: Компонент стандарта
    
    Returns:
        Статус реализации
    """
    return _registry.get_implementation_status(standard_id, component)