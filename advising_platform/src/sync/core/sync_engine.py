"""
Модуль ядра синхронизации кэша и файловой системы.
"""

import os
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Set, Tuple, Union

from advising_platform.src.sync.core.path_mapper import PathMapper
from advising_platform.src.sync.core.sync_state import SyncState, SyncStateRepository
from advising_platform.src.sync.core.conflict_resolver import ConflictResolver, ConflictResolution, SyncAction
from advising_platform.src.sync.core.file_watcher import FileSystemWatcher
from advising_platform.src.utils.rwlock import RWLock

class SyncEngine:
    """
    Ядро синхронизации кэша и файловой системы.
    
    Координирует работу всех компонентов синхронизации:
    - PathMapper для преобразования путей
    - SyncStateRepository для управления состояниями синхронизации
    - ConflictResolver для разрешения конфликтов
    - FileSystemWatcher для отслеживания изменений файлов
    
    Обеспечивает двунаправленную синхронизацию между кэшем и файловой системой.
    """
    
    def __init__(self, 
                cache_interface,
                path_mapper: PathMapper,
                state_repository: SyncStateRepository,
                conflict_resolver: ConflictResolver,
                file_watcher: Optional[FileSystemWatcher] = None,
                sync_interval: float = 60.0,
                auto_sync: bool = True,
                max_backups: int = 10):
        """
        Инициализирует ядро синхронизации.
        
        Args:
            cache_interface: Интерфейс для работы с кэшем
            path_mapper: Преобразователь путей
            state_repository: Хранилище состояний синхронизации
            conflict_resolver: Разрешитель конфликтов
            file_watcher: Наблюдатель за файловой системой (опционально)
            sync_interval: Интервал автоматической синхронизации в секундах
            auto_sync: Флаг автоматической синхронизации
            max_backups: Максимальное количество резервных копий
        """
        self.cache = cache_interface
        self.path_mapper = path_mapper
        self.state_repository = state_repository
        self.conflict_resolver = conflict_resolver
        self.file_watcher = file_watcher
        
        self.sync_interval = sync_interval
        self.auto_sync = auto_sync
        self.max_backups = max_backups
        
        # Блокировка для синхронизации
        self.sync_lock = RWLock()
        
        # Множество отслеживаемых директорий
        self.tracked_directories: Set[str] = set()
        
        # Флаг работы синхронизации
        self.running = False
        
        # Поток для автоматической синхронизации
        self.sync_thread = threading.Thread(target=self._auto_sync_worker, daemon=True)
        
        # Очередь файлов для синхронизации
        self.sync_queue: Set[str] = set()
        self.queue_lock = threading.Lock()
        
        # Логгер
        self.logger = logging.getLogger(__name__)
        
        # Если указан наблюдатель, настраиваем его
        if self.file_watcher:
            self._setup_file_watcher()
        
        self.logger.info("SyncEngine инициализирован")
    
    def _setup_file_watcher(self) -> None:
        """Настраивает наблюдатель файловой системы."""
        # Устанавливаем обработчик событий
        self.file_watcher.change_callback = self._on_file_change
    
    def _on_file_change(self, logical_path: str, event_type: str) -> None:
        """
        Обработчик событий изменения файлов.
        
        Args:
            logical_path: Логический путь измененного файла
            event_type: Тип события (created, modified, deleted, moved)
        """
        self.logger.debug(f"Получено событие {event_type} для {logical_path}")
        
        # Добавляем файл в очередь синхронизации
        with self.queue_lock:
            self.sync_queue.add(logical_path)
        
        # Если это не автоматическая синхронизация, синхронизируем сразу
        if not self.auto_sync:
            self.synchronize_document(logical_path)
    
    def start(self) -> None:
        """Запускает ядро синхронизации."""
        if self.running:
            return
        
        self.running = True
        
        # Запускаем наблюдатель, если указан
        if self.file_watcher:
            # Получаем физические пути директорий
            physical_dirs = [
                self.path_mapper.to_physical(logical_dir)
                for logical_dir in self.tracked_directories
            ]
            
            # Запускаем отслеживание директорий
            self.file_watcher.start_watching(physical_dirs)
        
        # Запускаем поток автоматической синхронизации
        if self.auto_sync:
            self.sync_thread = threading.Thread(target=self._auto_sync_worker, daemon=True)
            self.sync_thread.start()
        
        self.logger.info("SyncEngine запущен")
    
    def stop(self) -> None:
        """Останавливает ядро синхронизации."""
        if not self.running:
            return
        
        self.running = False
        
        # Останавливаем наблюдатель, если указан
        if self.file_watcher:
            self.file_watcher.stop_watching()
        
        # Ожидаем завершения потока автоматической синхронизации
        if self.auto_sync and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=2.0)
        
        self.logger.info("SyncEngine остановлен")
    
    def track_directory(self, logical_dir: str) -> None:
        """
        Добавляет директорию для отслеживания.
        
        Args:
            logical_dir: Логический путь директории
        """
        # Проверяем, существует ли физическая директория
        physical_dir = self.path_mapper.to_physical(logical_dir)
        
        if not os.path.exists(physical_dir):
            self.logger.warning(f"Физическая директория не существует: {physical_dir}")
            
            # Создаем директорию
            try:
                os.makedirs(physical_dir, exist_ok=True)
                self.logger.info(f"Создана директория: {physical_dir}")
            except Exception as e:
                self.logger.error(f"Ошибка создания директории {physical_dir}: {e}")
                return
        
        # Добавляем директорию в список отслеживаемых
        self.tracked_directories.add(logical_dir)
        
        # Если работает наблюдатель, добавляем директорию для отслеживания
        if self.running and self.file_watcher:
            self.file_watcher.start_watching([physical_dir])
        
        self.logger.info(f"Директория добавлена для отслеживания: {logical_dir}")
    
    def untrack_directory(self, logical_dir: str) -> None:
        """
        Удаляет директорию из отслеживаемых.
        
        Args:
            logical_dir: Логический путь директории
        """
        if logical_dir in self.tracked_directories:
            self.tracked_directories.remove(logical_dir)
            
            self.logger.info(f"Директория удалена из отслеживаемых: {logical_dir}")
    
    def synchronize_document(self, logical_path: str) -> Dict[str, Any]:
        """
        Синхронизирует указанный документ.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            Результат синхронизации
        """
        start_time = time.time()
        physical_path = self.path_mapper.to_physical(logical_path)
        
        self.logger.debug(f"Синхронизация документа: {logical_path} -> {physical_path}")
        
        result = {
            'logical_path': logical_path,
            'physical_path': physical_path,
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'success': False,
            'action': None,
            'error': None
        }
        
        try:
            # Получаем состояние синхронизации
            sync_state = self.state_repository.get_document_state(logical_path)
            
            # Проверяем наличие документа в кэше и файловой системе
            cache_exists = self.cache.exists(logical_path)
            file_exists = os.path.exists(physical_path)
            
            # Получаем содержимое и время модификации
            cache_content = None
            cache_modified_time = None
            
            if cache_exists:
                cache_content = self.cache.get_content(logical_path)
                cache_modified_time = self.cache.get_modified_time(logical_path)
            
            file_content = None
            file_modified_time = None
            
            if file_exists:
                try:
                    with open(physical_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    file_modified_time = os.path.getmtime(physical_path)
                except Exception as e:
                    self.logger.error(f"Ошибка чтения файла {physical_path}: {e}")
                    result['error'] = f"Ошибка чтения файла: {e}"
                    return result
            
            # Если состояния нет, создаем его
            if not sync_state:
                sync_state = self.state_repository.create_document_state(
                    logical_path=logical_path,
                    physical_path=physical_path,
                    cache_content=cache_content,
                    file_content=file_content
                )
            
            # Определяем действие для синхронизации
            resolution = self.conflict_resolver.resolve(
                logical_path=logical_path,
                physical_path=physical_path,
                sync_state=sync_state,
                cache_exists=cache_exists,
                cache_modified_time=cache_modified_time,
                cache_content=cache_content,
                file_exists=file_exists,
                file_modified_time=file_modified_time,
                file_content=file_content
            )
            
            # Применяем действие
            self._apply_sync_action(
                logical_path=logical_path,
                physical_path=physical_path,
                sync_state=sync_state,
                resolution=resolution,
                cache_content=cache_content,
                file_content=file_content
            )
            
            # Обновляем результат
            result['success'] = True
            result['action'] = resolution.action.name
            result['description'] = resolution.description
            
            if resolution.backup_path:
                result['backup_path'] = resolution.backup_path
            
            # Удаляем документ из очереди синхронизации
            with self.queue_lock:
                if logical_path in self.sync_queue:
                    self.sync_queue.remove(logical_path)
        
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации документа {logical_path}: {e}")
            result['error'] = str(e)
            result['success'] = False
        
        # Завершаем результат
        end_time = time.time()
        result['end_time'] = end_time
        result['duration'] = end_time - start_time
        
        return result
    
    def _apply_sync_action(self, 
                          logical_path: str,
                          physical_path: str,
                          sync_state: SyncState,
                          resolution: ConflictResolution,
                          cache_content: Optional[str],
                          file_content: Optional[str]) -> bool:
        """
        Применяет действие синхронизации.
        
        Args:
            logical_path: Логический путь документа
            physical_path: Физический путь документа
            sync_state: Состояние синхронизации
            resolution: Результат разрешения конфликта
            cache_content: Содержимое в кэше
            file_content: Содержимое файла
            
        Returns:
            True, если действие успешно применено, иначе False
        """
        action = resolution.action
        self.logger.debug(f"Применение действия {action.name} для {logical_path}")
        
        # В зависимости от действия
        if action == SyncAction.NO_ACTION_REQUIRED:
            # Ничего не делаем
            return True
        
        elif action == SyncAction.UPDATE_FILE_FROM_CACHE:
            # Обновляем файл из кэша
            if cache_content is None:
                self.logger.error(f"Отсутствует содержимое в кэше для {logical_path}")
                return False
            
            # Создаем директорию, если не существует
            os.makedirs(os.path.dirname(physical_path), exist_ok=True)
            
            # Обновляем файл
            with open(physical_path, 'w', encoding='utf-8') as f:
                f.write(cache_content)
            
            # Обновляем состояние
            sync_state.update_file_state(cache_content)
            sync_state.mark_synced(modified_by="cache")
            self.state_repository.update_document_state(sync_state)
            
            return True
        
        elif action == SyncAction.UPDATE_CACHE_FROM_FILE:
            # Обновляем кэш из файла
            if file_content is None:
                self.logger.error(f"Отсутствует содержимое файла для {logical_path}")
                return False
            
            # Обновляем кэш
            self.cache.update_content(logical_path, file_content)
            
            # Обновляем состояние
            sync_state.update_cache_state(file_content)
            sync_state.mark_synced(modified_by="file")
            self.state_repository.update_document_state(sync_state)
            
            return True
        
        elif action == SyncAction.CREATE_FILE_FROM_CACHE:
            # Создаем файл из кэша
            if cache_content is None:
                self.logger.error(f"Отсутствует содержимое в кэше для {logical_path}")
                return False
            
            # Создаем директорию, если не существует
            os.makedirs(os.path.dirname(physical_path), exist_ok=True)
            
            # Создаем файл
            with open(physical_path, 'w', encoding='utf-8') as f:
                f.write(cache_content)
            
            # Обновляем состояние
            sync_state.update_file_state(cache_content)
            sync_state.mark_synced(modified_by="cache")
            self.state_repository.update_document_state(sync_state)
            
            return True
        
        elif action == SyncAction.CREATE_CACHE_FROM_FILE:
            # Создаем кэш из файла
            if file_content is None:
                self.logger.error(f"Отсутствует содержимое файла для {logical_path}")
                return False
            
            # Создаем кэш
            self.cache.create_document(logical_path, file_content)
            
            # Обновляем состояние
            sync_state.update_cache_state(file_content)
            sync_state.mark_synced(modified_by="file")
            self.state_repository.update_document_state(sync_state)
            
            return True
        
        elif action == SyncAction.DELETE_CACHE:
            # Удаляем документ из кэша
            self.cache.delete_document(logical_path)
            
            # Удаляем состояние
            self.state_repository.remove_document_state(logical_path)
            
            return True
        
        elif action == SyncAction.DELETE_FILE:
            # Удаляем файл
            if os.path.exists(physical_path):
                os.remove(physical_path)
            
            # Удаляем состояние
            self.state_repository.remove_document_state(logical_path)
            
            return True
        
        elif action == SyncAction.BACKUP_AND_UPDATE_FILE:
            # Обновляем файл из кэша с созданием резервной копии
            if cache_content is None:
                self.logger.error(f"Отсутствует содержимое в кэше для {logical_path}")
                return False
            
            # Обновляем файл
            with open(physical_path, 'w', encoding='utf-8') as f:
                f.write(cache_content)
            
            # Обновляем состояние
            sync_state.update_file_state(cache_content)
            sync_state.mark_synced(modified_by="cache")
            self.state_repository.update_document_state(sync_state)
            
            return True
        
        elif action == SyncAction.BACKUP_AND_UPDATE_CACHE:
            # Обновляем кэш из файла с созданием резервной копии
            if file_content is None:
                self.logger.error(f"Отсутствует содержимое файла для {logical_path}")
                return False
            
            # Обновляем кэш
            self.cache.update_content(logical_path, file_content)
            
            # Обновляем состояние
            sync_state.update_cache_state(file_content)
            sync_state.mark_synced(modified_by="file")
            self.state_repository.update_document_state(sync_state)
            
            return True
        
        elif action == SyncAction.MANUAL_RESOLUTION_REQUIRED:
            # Отмечаем конфликт в состоянии
            sync_state.mark_conflict()
            self.state_repository.update_document_state(sync_state)
            
            self.logger.warning(f"Требуется ручное разрешение конфликта для {logical_path}")
            
            return False
        
        # Неизвестное действие
        self.logger.error(f"Неизвестное действие синхронизации: {action.name}")
        return False
    
    def synchronize_directory(self, logical_dir: str) -> Dict[str, Any]:
        """
        Синхронизирует указанную директорию.
        
        Args:
            logical_dir: Логический путь директории
            
        Returns:
            Результат синхронизации
        """
        start_time = time.time()
        physical_dir = self.path_mapper.to_physical(logical_dir)
        
        self.logger.info(f"Синхронизация директории: {logical_dir} -> {physical_dir}")
        
        result = {
            'logical_dir': logical_dir,
            'physical_dir': physical_dir,
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'success': True,
            'documents_processed': 0,
            'documents_synced': 0,
            'errors': [],
            'details': []
        }
        
        try:
            # Получаем список документов в кэше
            documents = self.cache.get_documents_in_directory(logical_dir)
            logical_paths = [doc.path for doc in documents]
            
            # Получаем список файлов в директории
            physical_paths = self._scan_directory(physical_dir)
            
            # Преобразуем физические пути в логические
            for physical_path in physical_paths:
                logical_path = self.path_mapper.to_logical(physical_path)
                if logical_path not in logical_paths:
                    logical_paths.append(logical_path)
            
            # Синхронизируем каждый документ
            for logical_path in logical_paths:
                result['documents_processed'] += 1
                
                document_result = self.synchronize_document(logical_path)
                result['details'].append(document_result)
                
                if document_result['success']:
                    result['documents_synced'] += 1
                else:
                    result['errors'].append({
                        'logical_path': logical_path,
                        'error': document_result.get('error')
                    })
                    result['success'] = False
        
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации директории {logical_dir}: {e}")
            result['error'] = str(e)
            result['success'] = False
        
        # Завершаем результат
        end_time = time.time()
        result['end_time'] = end_time
        result['duration'] = end_time - start_time
        
        return result
    
    def _scan_directory(self, physical_dir: str) -> List[str]:
        """
        Сканирует директорию и возвращает список файлов.
        
        Args:
            physical_dir: Физический путь к директории
            
        Returns:
            Список путей к файлам
        """
        files = []
        
        if not os.path.exists(physical_dir):
            return files
        
        for root, dirs, filenames in os.walk(physical_dir):
            for filename in filenames:
                # Пропускаем временные файлы и другие, которые не должны отслеживаться
                if filename.startswith('.') or self._should_ignore(filename):
                    continue
                
                file_path = os.path.join(root, filename)
                files.append(file_path)
        
        return files
    
    def _should_ignore(self, filename: str) -> bool:
        """
        Проверяет, следует ли игнорировать файл.
        
        Args:
            filename: Имя файла
            
        Returns:
            True, если файл следует игнорировать, иначе False
        """
        # Игнорируем типичные временные файлы и файлы редакторов
        ignore_patterns = [
            '~$', '.tmp', '.temp', '.swp', '.swo',
            '.pyc', '.pyo', '.pyd', '__pycache__',
            '.DS_Store', 'Thumbs.db', '.gitignore',
            '.sync_state.json', '.sync_backups'
        ]
        
        for pattern in ignore_patterns:
            if filename.endswith(pattern) or pattern in filename:
                return True
        
        return False
    
    def synchronize_all(self) -> Dict[str, Any]:
        """
        Синхронизирует все отслеживаемые директории.
        
        Returns:
            Результат синхронизации
        """
        start_time = time.time()
        
        self.logger.info(f"Синхронизация всех отслеживаемых директорий")
        
        result = {
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'success': True,
            'directories_processed': 0,
            'directories_synced': 0,
            'documents_processed': 0,
            'documents_synced': 0,
            'errors': [],
            'details': []
        }
        
        try:
            # Синхронизируем каждую директорию
            for logical_dir in self.tracked_directories:
                result['directories_processed'] += 1
                
                dir_result = self.synchronize_directory(logical_dir)
                result['details'].append(dir_result)
                
                if dir_result['success']:
                    result['directories_synced'] += 1
                    result['documents_processed'] += dir_result['documents_processed']
                    result['documents_synced'] += dir_result['documents_synced']
                else:
                    result['errors'].append({
                        'logical_dir': logical_dir,
                        'error': dir_result.get('error')
                    })
                    result['success'] = False
        
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации всех директорий: {e}")
            result['error'] = str(e)
            result['success'] = False
        
        # Завершаем результат
        end_time = time.time()
        result['end_time'] = end_time
        result['duration'] = end_time - start_time
        
        return result
    
    def _auto_sync_worker(self) -> None:
        """Поток для автоматической синхронизации."""
        self.logger.info("Запущен поток автоматической синхронизации")
        
        while self.running:
            # Спим указанное время
            time.sleep(self.sync_interval)
            
            if not self.running:
                break
            
            # Если есть файлы в очереди, синхронизируем их
            if self.sync_queue:
                with self.queue_lock:
                    files_to_sync = list(self.sync_queue)
                
                self.logger.debug(f"Автоматическая синхронизация {len(files_to_sync)} файлов")
                
                for logical_path in files_to_sync:
                    try:
                        self.synchronize_document(logical_path)
                    except Exception as e:
                        self.logger.error(f"Ошибка автоматической синхронизации {logical_path}: {e}")
        
        self.logger.info("Остановлен поток автоматической синхронизации")
    
    def get_sync_status(self, logical_path: str) -> Dict[str, Any]:
        """
        Возвращает статус синхронизации документа.
        
        Args:
            logical_path: Логический путь документа
            
        Returns:
            Статус синхронизации
        """
        physical_path = self.path_mapper.to_physical(logical_path)
        sync_state = self.state_repository.get_document_state(logical_path)
        
        status = {
            'logical_path': logical_path,
            'physical_path': physical_path,
            'exists_in_cache': self.cache.exists(logical_path),
            'exists_in_filesystem': os.path.exists(physical_path),
            'has_sync_state': sync_state is not None,
            'is_synced': False,
            'last_sync_time': None,
            'conflict_detected': False,
            'last_modified_by': None,
            'in_sync_queue': logical_path in self.sync_queue
        }
        
        if sync_state:
            # Проверяем, синхронизированы ли хеши
            status['is_synced'] = (sync_state.cache_hash == sync_state.file_hash and 
                                 not sync_state.conflict_detected)
            status['last_sync_time'] = sync_state.last_sync_time
            status['conflict_detected'] = sync_state.conflict_detected
            status['last_modified_by'] = sync_state.last_modified_by
        
        return status
    
    def get_directory_sync_status(self, logical_dir: str) -> Dict[str, Any]:
        """
        Возвращает статус синхронизации директории.
        
        Args:
            logical_dir: Логический путь директории
            
        Returns:
            Статус синхронизации
        """
        physical_dir = self.path_mapper.to_physical(logical_dir)
        
        status = {
            'logical_dir': logical_dir,
            'physical_dir': physical_dir,
            'exists_in_filesystem': os.path.exists(physical_dir),
            'is_tracked': logical_dir in self.tracked_directories,
            'documents': [],
            'total_documents': 0,
            'synced_documents': 0,
            'documents_with_conflicts': 0
        }
        
        try:
            # Получаем список документов в кэше
            documents = self.cache.get_documents_in_directory(logical_dir)
            logical_paths = [doc.path for doc in documents]
            
            # Получаем список файлов в директории
            physical_paths = self._scan_directory(physical_dir)
            
            # Преобразуем физические пути в логические
            for physical_path in physical_paths:
                logical_path = self.path_mapper.to_logical(physical_path)
                if logical_path not in logical_paths:
                    logical_paths.append(logical_path)
            
            # Получаем статус для каждого документа
            for logical_path in logical_paths:
                doc_status = self.get_sync_status(logical_path)
                status['documents'].append(doc_status)
                
                status['total_documents'] += 1
                
                if doc_status['is_synced']:
                    status['synced_documents'] += 1
                
                if doc_status['conflict_detected']:
                    status['documents_with_conflicts'] += 1
        
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса синхронизации директории {logical_dir}: {e}")
            status['error'] = str(e)
        
        return status