"""
Модуль для преобразования логических путей в физические и обратно.
"""

import os
import re
import logging
from typing import Dict, Optional, List, Tuple

class PathMapper:
    """
    Компонент для преобразования логических путей в физические и обратно.
    
    Логические пути - это пути, используемые в кэше документов, например:
    "[standards .md]/1.1 incident standard.md"
    
    Физические пути - это пути в файловой системе, например:
    "./[standards .md]/1.1 incident standard.md"
    """
    
    def __init__(self):
        """
        Инициализирует преобразователь путей.
        """
        # Маппинг логических директорий на физические
        self.path_mappings: Dict[str, str] = {}
        
        # Кэш для быстрого преобразования путей
        self._logical_to_physical_cache: Dict[str, str] = {}
        self._physical_to_logical_cache: Dict[str, str] = {}
        
        self.logger = logging.getLogger(__name__)
    
    def register_mapping(self, logical_dir: str, physical_dir: str) -> None:
        """
        Регистрирует маппинг между логической и физической директориями.
        
        Args:
            logical_dir: Логическая директория
            physical_dir: Физическая директория
        """
        self.logger.debug(f"Регистрация маппинга: {logical_dir} -> {physical_dir}")
        
        # Нормализуем пути
        logical_dir = logical_dir.rstrip('/')
        physical_dir = physical_dir.rstrip('/')
        
        # Регистрируем маппинг
        self.path_mappings[logical_dir] = physical_dir
        
        # Очищаем кэш
        self._logical_to_physical_cache = {}
        self._physical_to_logical_cache = {}
    
    def to_physical(self, logical_path: str) -> str:
        """
        Преобразует логический путь в физический.
        
        Args:
            logical_path: Логический путь
            
        Returns:
            Физический путь
        """
        # Проверяем кэш
        if logical_path in self._logical_to_physical_cache:
            return self._logical_to_physical_cache[logical_path]
        
        # Путь уже абсолютный?
        if logical_path.startswith('/'):
            return logical_path
        
        # Ищем подходящую логическую директорию
        logical_dir, remaining = self._split_path(logical_path)
        
        if logical_dir in self.path_mappings:
            physical_dir = self.path_mappings[logical_dir]
            physical_path = os.path.join(physical_dir, remaining) if remaining else physical_dir
            
            # Кэшируем результат
            self._logical_to_physical_cache[logical_path] = physical_path
            
            return physical_path
        
        # Если не найдено соответствие, возвращаем исходный путь
        return logical_path
    
    def to_logical(self, physical_path: str) -> str:
        """
        Преобразует физический путь в логический.
        
        Args:
            physical_path: Физический путь
            
        Returns:
            Логический путь
        """
        # Проверяем кэш
        if physical_path in self._physical_to_logical_cache:
            return self._physical_to_logical_cache[physical_path]
        
        # Перебираем все маппинги
        for logical_dir, physical_dir in self.path_mappings.items():
            if physical_path.startswith(physical_dir):
                remaining = physical_path[len(physical_dir):].lstrip('/')
                logical_path = os.path.join(logical_dir, remaining) if remaining else logical_dir
                
                # Унифицируем разделители путей
                logical_path = logical_path.replace('\\', '/')
                
                # Кэшируем результат
                self._physical_to_logical_cache[physical_path] = logical_path
                
                return logical_path
        
        # Если не найдено соответствие, возвращаем исходный путь
        return physical_path
    
    def _split_path(self, path: str) -> Tuple[str, str]:
        """
        Разделяет путь на директорию и оставшуюся часть.
        
        Args:
            path: Путь для разделения
            
        Returns:
            Кортеж (директория, оставшаяся часть)
        """
        # Специальная обработка для путей с квадратными скобками
        if '[' in path:
            match = re.match(r'(\[[^\]]+\])(.*)', path)
            if match:
                dir_part = match.group(1)
                remaining = match.group(2).lstrip('/')
                return dir_part, remaining
        
        # Обычное разделение пути
        if '/' in path:
            dir_part, remaining = path.split('/', 1)
            return dir_part, remaining
        
        return path, ""
    
    def get_registered_mappings(self) -> Dict[str, str]:
        """
        Возвращает все зарегистрированные маппинги.
        
        Returns:
            Словарь маппингов {логическая_директория: физическая_директория}
        """
        return self.path_mappings.copy()
    
    def clear_mappings(self) -> None:
        """
        Очищает все зарегистрированные маппинги.
        """
        self.path_mappings = {}
        self._logical_to_physical_cache = {}
        self._physical_to_logical_cache = {}