#!/usr/bin/env python3
"""
Модуль для разрешения конфликтов синхронизации между кэшем и файловой системой.
"""

import os
import sys
import time
import logging
import hashlib
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("conflict_resolver")

class ConflictResolutionStrategy(Enum):
    """Стратегии разрешения конфликтов."""
    PREFER_FILESYSTEM = 'filesystem'  # Предпочитать версию файловой системы
    PREFER_CACHE = 'cache'           # Предпочитать версию из кэша
    NEWEST = 'newest'                # Предпочитать более новую версию
    OLDEST = 'oldest'                # Предпочитать более старую версию
    MANUAL = 'manual'                # Требовать ручного разрешения
    CREATE_BACKUP = 'backup'         # Создать резервную копию и использовать версию файловой системы

class ConflictResolutionResult(Enum):
    """Результаты разрешения конфликтов."""
    RESOLVED_FILESYSTEM = 'resolved_filesystem'  # Конфликт разрешен в пользу файловой системы
    RESOLVED_CACHE = 'resolved_cache'           # Конфликт разрешен в пользу кэша
    BACKUP_CREATED = 'backup_created'           # Создана резервная копия
    REQUIRES_MANUAL = 'requires_manual'         # Требуется ручное разрешение
    NO_CONFLICT = 'no_conflict'                 # Конфликта нет
    ERROR = 'error'                            # Ошибка при разрешении конфликта

class SyncConflict:
    """
    Класс, представляющий конфликт синхронизации между кэшем и файловой системой.
    """
    
    def __init__(self, 
                path: str, 
                filesystem_data: Optional[Dict[str, Any]] = None, 
                cache_data: Optional[Dict[str, Any]] = None):
        """
        Инициализирует объект конфликта.
        
        Args:
            path: Путь к файлу, вызвавшему конфликт
            filesystem_data: Данные из файловой системы
            cache_data: Данные из кэша
        """
        self.path = path
        self.filesystem_data = filesystem_data or {}
        self.cache_data = cache_data or {}
        
        # Метаданные конфликта
        self.detected_time = time.time()
        self.resolved = False
        self.resolution_strategy: Optional[ConflictResolutionStrategy] = None
        self.resolution_result: Optional[ConflictResolutionResult] = None
        self.backup_path: Optional[str] = None
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление конфликта.
        
        Returns:
            Строковое представление
        """
        resolved_str = "разрешен" if self.resolved else "не разрешен"
        
        filesystem_size = self.filesystem_data.get('size', 'Н/Д')
        filesystem_mtime = self.filesystem_data.get('mtime_str', 'Н/Д')
        
        cache_size = self.cache_data.get('content_length', 'Н/Д')
        cache_last_accessed = self.cache_data.get('last_accessed_str', 'Н/Д')
        
        return (f"Конфликт для {self.path} ({resolved_str}):\n"
                f"  Файловая система: размер={filesystem_size}, изменен={filesystem_mtime}\n"
                f"  Кэш: размер={cache_size}, последний доступ={cache_last_accessed}")

class ConflictResolver:
    """
    Компонент для разрешения конфликтов между кэшем и файловой системой.
    """
    
    def __init__(self, default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.NEWEST):
        """
        Инициализирует разрешитель конфликтов.
        
        Args:
            default_strategy: Стратегия разрешения конфликтов по умолчанию
        """
        self.default_strategy = default_strategy
        self.conflicts_history: List[SyncConflict] = []
        self.backup_dir = os.path.join(os.getcwd(), '.sync_backups')
        
        # Создаем директорию для резервных копий, если она не существует
        if not os.path.exists(self.backup_dir):
            try:
                os.makedirs(self.backup_dir)
                logger.info(f"Создана директория для резервных копий: {self.backup_dir}")
            except OSError as e:
                logger.warning(f"Не удалось создать директорию для резервных копий: {e}")
    
    def detect_conflict(self, 
                       path: str, 
                       filesystem_data: Dict[str, Any], 
                       cache_data: Dict[str, Any]) -> Optional[SyncConflict]:
        """
        Определяет, есть ли конфликт между данными из файловой системы и кэша.
        
        Args:
            path: Путь к файлу
            filesystem_data: Данные из файловой системы
            cache_data: Данные из кэша
            
        Returns:
            Объект конфликта или None, если конфликта нет
        """
        # Проверяем наличие конфликта по размеру
        filesystem_size = filesystem_data.get('size')
        cache_size = cache_data.get('content_length')
        
        if filesystem_size is not None and cache_size is not None and filesystem_size != cache_size:
            conflict = SyncConflict(path, filesystem_data, cache_data)
            self.conflicts_history.append(conflict)
            logger.info(f"Обнаружен конфликт для {path}: размер в ФС={filesystem_size}, размер в кэше={cache_size}")
            return conflict
        
        return None
    
    def resolve_conflict(self, 
                        conflict: SyncConflict, 
                        strategy: Optional[ConflictResolutionStrategy] = None,
                        filesystem_content: Optional[str] = None,
                        cache_content: Optional[str] = None) -> Tuple[ConflictResolutionResult, Optional[str]]:
        """
        Разрешает конфликт в соответствии с указанной стратегией.
        
        Args:
            conflict: Объект конфликта
            strategy: Стратегия разрешения конфликта
            filesystem_content: Содержимое файла из файловой системы
            cache_content: Содержимое файла из кэша
            
        Returns:
            Кортеж (результат разрешения, путь к выбранной версии или резервной копии)
        """
        # Если стратегия не указана, используем стратегию по умолчанию
        if strategy is None:
            strategy = self.default_strategy
        
        # Сохраняем стратегию в объекте конфликта
        conflict.resolution_strategy = strategy
        
        try:
            # Разрешаем конфликт в соответствии со стратегией
            if strategy == ConflictResolutionStrategy.PREFER_FILESYSTEM:
                # Предпочитаем версию из файловой системы
                conflict.resolved = True
                conflict.resolution_result = ConflictResolutionResult.RESOLVED_FILESYSTEM
                return ConflictResolutionResult.RESOLVED_FILESYSTEM, conflict.path
                
            elif strategy == ConflictResolutionStrategy.PREFER_CACHE:
                # Предпочитаем версию из кэша
                conflict.resolved = True
                conflict.resolution_result = ConflictResolutionResult.RESOLVED_CACHE
                return ConflictResolutionResult.RESOLVED_CACHE, conflict.path
                
            elif strategy == ConflictResolutionStrategy.NEWEST:
                # Предпочитаем более новую версию
                filesystem_mtime = conflict.filesystem_data.get('mtime', 0)
                cache_last_accessed = conflict.cache_data.get('last_accessed', 0)
                
                if filesystem_mtime > cache_last_accessed:
                    conflict.resolved = True
                    conflict.resolution_result = ConflictResolutionResult.RESOLVED_FILESYSTEM
                    return ConflictResolutionResult.RESOLVED_FILESYSTEM, conflict.path
                else:
                    conflict.resolved = True
                    conflict.resolution_result = ConflictResolutionResult.RESOLVED_CACHE
                    return ConflictResolutionResult.RESOLVED_CACHE, conflict.path
                
            elif strategy == ConflictResolutionStrategy.OLDEST:
                # Предпочитаем более старую версию
                filesystem_mtime = conflict.filesystem_data.get('mtime', float('inf'))
                cache_last_accessed = conflict.cache_data.get('last_accessed', float('inf'))
                
                if filesystem_mtime < cache_last_accessed:
                    conflict.resolved = True
                    conflict.resolution_result = ConflictResolutionResult.RESOLVED_FILESYSTEM
                    return ConflictResolutionResult.RESOLVED_FILESYSTEM, conflict.path
                else:
                    conflict.resolved = True
                    conflict.resolution_result = ConflictResolutionResult.RESOLVED_CACHE
                    return ConflictResolutionResult.RESOLVED_CACHE, conflict.path
                
            elif strategy == ConflictResolutionStrategy.CREATE_BACKUP:
                # Создаем резервную копию и используем версию файловой системы
                if cache_content is not None:
                    backup_path = self._create_backup(conflict.path, cache_content)
                    if backup_path:
                        conflict.backup_path = backup_path
                        conflict.resolved = True
                        conflict.resolution_result = ConflictResolutionResult.BACKUP_CREATED
                        return ConflictResolutionResult.BACKUP_CREATED, backup_path
                
                # Если не удалось создать резервную копию, используем версию файловой системы
                conflict.resolved = True
                conflict.resolution_result = ConflictResolutionResult.RESOLVED_FILESYSTEM
                return ConflictResolutionResult.RESOLVED_FILESYSTEM, conflict.path
                
            elif strategy == ConflictResolutionStrategy.MANUAL:
                # Требуется ручное разрешение
                conflict.resolution_result = ConflictResolutionResult.REQUIRES_MANUAL
                return ConflictResolutionResult.REQUIRES_MANUAL, None
                
            else:
                logger.warning(f"Неизвестная стратегия разрешения конфликта: {strategy}")
                return ConflictResolutionResult.ERROR, None
                
        except Exception as e:
            logger.error(f"Ошибка при разрешении конфликта для {conflict.path}: {e}")
            conflict.resolution_result = ConflictResolutionResult.ERROR
            return ConflictResolutionResult.ERROR, None
    
    def _create_backup(self, path: str, content: str) -> Optional[str]:
        """
        Создает резервную копию файла.
        
        Args:
            path: Путь к файлу
            content: Содержимое файла
            
        Returns:
            Путь к резервной копии или None, если не удалось создать
        """
        try:
            # Создаем уникальное имя для резервной копии
            filename = os.path.basename(path)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_filename = f"{filename}.{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Создаем резервную копию
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Создана резервная копия для {path}: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии для {path}: {e}")
            return None
    
    def get_conflicts_history(self) -> List[SyncConflict]:
        """
        Возвращает историю конфликтов.
        
        Returns:
            Список объектов конфликтов
        """
        return self.conflicts_history.copy()
    
    def get_unresolved_conflicts(self) -> List[SyncConflict]:
        """
        Возвращает список неразрешенных конфликтов.
        
        Returns:
            Список неразрешенных конфликтов
        """
        return [c for c in self.conflicts_history if not c.resolved]