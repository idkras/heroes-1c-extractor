"""
Модуль для работы с состоянием синхронизации.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

class SyncState:
    """
    Состояние синхронизации документа.
    
    Хранит информацию о текущем состоянии синхронизации между 
    кэшем и файловой системой для конкретного документа.
    """
    
    def __init__(self, 
                logical_path: str, 
                physical_path: str,
                last_sync_time: Optional[float] = None,
                cache_hash: Optional[str] = None,
                file_hash: Optional[str] = None,
                conflict_detected: bool = False,
                last_modified_by: Optional[str] = None):
        """
        Инициализирует состояние синхронизации.
        
        Args:
            logical_path: Логический путь документа
            physical_path: Физический путь документа
            last_sync_time: Время последней синхронизации (timestamp)
            cache_hash: Хеш содержимого в кэше
            file_hash: Хеш содержимого в файле
            conflict_detected: Флаг обнаруженного конфликта
            last_modified_by: Кто последний модифицировал документ
        """
        self.logical_path = logical_path
        self.physical_path = physical_path
        self.last_sync_time = last_sync_time or time.time()
        self.cache_hash = cache_hash
        self.file_hash = file_hash
        self.conflict_detected = conflict_detected
        self.last_modified_by = last_modified_by
        
        # Дополнительные метаданные
        self.metadata: Dict[str, Any] = {}
        
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def _calculate_hash(content: str) -> str:
        """
        Вычисляет хеш содержимого.
        
        Args:
            content: Содержимое для хеширования
            
        Returns:
            Хеш содержимого
        """
        if not content:
            return ""
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def update_cache_state(self, cache_content: str) -> None:
        """
        Обновляет информацию о состоянии в кэше.
        
        Args:
            cache_content: Содержимое в кэше
        """
        self.cache_hash = self._calculate_hash(cache_content)
        self.metadata['cache_updated_at'] = time.time()
    
    def update_file_state(self, file_content: str) -> None:
        """
        Обновляет информацию о состоянии в файле.
        
        Args:
            file_content: Содержимое в файле
        """
        self.file_hash = self._calculate_hash(file_content)
        self.metadata['file_updated_at'] = time.time()
    
    def mark_synced(self, modified_by: Optional[str] = None) -> None:
        """
        Отмечает документ как синхронизированный.
        
        Args:
            modified_by: Кто модифицировал документ
        """
        self.last_sync_time = time.time()
        self.conflict_detected = False
        
        if modified_by:
            self.last_modified_by = modified_by
        
        self.metadata['last_sync'] = {
            'time': self.last_sync_time,
            'modified_by': self.last_modified_by
        }
    
    def mark_conflict(self) -> None:
        """
        Отмечает документ как конфликтный.
        """
        self.conflict_detected = True
        self.metadata['conflict_detected_at'] = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертирует состояние в словарь для сериализации.
        
        Returns:
            Словарь с данными состояния
        """
        return {
            'logical_path': self.logical_path,
            'physical_path': self.physical_path,
            'last_sync_time': self.last_sync_time,
            'cache_hash': self.cache_hash,
            'file_hash': self.file_hash,
            'conflict_detected': self.conflict_detected,
            'last_modified_by': self.last_modified_by,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncState':
        """
        Создает состояние из словаря.
        
        Args:
            data: Словарь с данными состояния
            
        Returns:
            Созданное состояние
        """
        state = cls(
            logical_path=data['logical_path'],
            physical_path=data['physical_path'],
            last_sync_time=data.get('last_sync_time'),
            cache_hash=data.get('cache_hash'),
            file_hash=data.get('file_hash'),
            conflict_detected=data.get('conflict_detected', False),
            last_modified_by=data.get('last_modified_by')
        )
        
        state.metadata = data.get('metadata', {})
        
        return state
    
    def is_synced(self) -> bool:
        """
        Проверяет, синхронизированы ли кэш и файл.
        
        Returns:
            True, если синхронизированы, иначе False
        """
        # Если хеши равны, то синхронизированы
        if self.cache_hash == self.file_hash:
            return True
        
        # Если есть конфликт, то не синхронизированы
        if self.conflict_detected:
            return False
        
        return False


class SyncStateRepository:
    """
    Хранилище состояний синхронизации.
    
    Управляет хранением и загрузкой состояний синхронизации для всех документов.
    """
    
    def __init__(self, state_file: str = 'sync_state.json'):
        """
        Инициализирует хранилище состояний.
        
        Args:
            state_file: Путь к файлу для хранения состояний
        """
        self.state_file = state_file
        self.states: Dict[str, SyncState] = {}
        self.logger = logging.getLogger(__name__)
        
        # Создаем директорию для файла состояний, если не существует
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        # Загружаем состояния, если файл существует
        self._load_states()
    
    def _load_states(self) -> None:
        """
        Загружает состояния из файла.
        """
        if not os.path.exists(self.state_file):
            self.logger.info(f"Файл состояний не найден: {self.state_file}")
            return
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for state_data in data.get('states', []):
                state = SyncState.from_dict(state_data)
                self.states[state.logical_path] = state
            
            self.logger.info(f"Загружено {len(self.states)} состояний из {self.state_file}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки состояний: {e}")
    
    def _save_states(self) -> None:
        """
        Сохраняет состояния в файл.
        """
        data = {
            'version': '1.0',
            'updated_at': time.time(),
            'states': [state.to_dict() for state in self.states.values()]
        }
        
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.debug(f"Сохранено {len(self.states)} состояний в {self.state_file}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения состояний: {e}")
    
    def get_document_state(self, logical_path: str) -> Optional[SyncState]:
        """
        Возвращает состояние синхронизации для документа.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            Состояние синхронизации или None, если не найдено
        """
        return self.states.get(logical_path)
    
    def create_document_state(self, 
                             logical_path: str, 
                             physical_path: str, 
                             cache_content: Optional[str] = None,
                             file_content: Optional[str] = None) -> SyncState:
        """
        Создает новое состояние синхронизации для документа.
        
        Args:
            logical_path: Логический путь документа
            physical_path: Физический путь документа
            cache_content: Содержимое в кэше (опционально)
            file_content: Содержимое в файле (опционально)
            
        Returns:
            Созданное состояние
        """
        state = SyncState(
            logical_path=logical_path,
            physical_path=physical_path
        )
        
        if cache_content is not None:
            state.update_cache_state(cache_content)
        
        if file_content is not None:
            state.update_file_state(file_content)
        
        self.states[logical_path] = state
        self._save_states()
        
        return state
    
    def update_document_state(self, state: SyncState) -> None:
        """
        Обновляет состояние синхронизации для документа.
        
        Args:
            state: Состояние синхронизации
        """
        self.states[state.logical_path] = state
        self._save_states()
    
    def remove_document_state(self, logical_path: str) -> bool:
        """
        Удаляет состояние синхронизации для документа.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            True, если состояние было удалено, иначе False
        """
        if logical_path in self.states:
            del self.states[logical_path]
            self._save_states()
            return True
        
        return False
    
    def get_all_states(self) -> Dict[str, SyncState]:
        """
        Возвращает все состояния синхронизации.
        
        Returns:
            Словарь состояний {logical_path: state}
        """
        return self.states.copy()
    
    def clear(self) -> None:
        """
        Очищает все состояния.
        """
        self.states = {}
        self._save_states()
    
    def backup(self, backup_file: str) -> bool:
        """
        Создает резервную копию состояний.
        
        Args:
            backup_file: Путь к файлу резервной копии
            
        Returns:
            True, если резервная копия успешно создана, иначе False
        """
        try:
            data = {
                'version': '1.0',
                'created_at': time.time(),
                'states': [state.to_dict() for state in self.states.values()]
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Создана резервная копия {len(self.states)} состояний в {backup_file}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            return False
    
    def restore(self, backup_file: str) -> bool:
        """
        Восстанавливает состояния из резервной копии.
        
        Args:
            backup_file: Путь к файлу резервной копии
            
        Returns:
            True, если восстановление успешно, иначе False
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            states = {}
            for state_data in data.get('states', []):
                state = SyncState.from_dict(state_data)
                states[state.logical_path] = state
            
            # Заменяем текущие состояния
            self.states = states
            self._save_states()
            
            self.logger.info(f"Восстановлено {len(self.states)} состояний из {backup_file}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка восстановления из резервной копии: {e}")
            return False