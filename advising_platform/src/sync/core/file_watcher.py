"""
Модуль для отслеживания изменений файлов в файловой системе.
"""

import os
import time
import threading
import logging
from typing import Dict, List, Callable, Optional, Set, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

class BufferedEventHandler(FileSystemEventHandler):
    """
    Обработчик событий файловой системы с буферизацией.
    
    Буферизует события в течение указанного времени,
    чтобы избежать множественных оповещений для одного файла.
    """
    
    def __init__(self, 
                callback: Callable[[str, str], None], 
                path_mapper: Any,
                buffer_time: float = 0.5):
        """
        Инициализирует обработчик событий.
        
        Args:
            callback: Функция обратного вызова (path, event_type)
            path_mapper: Преобразователь путей
            buffer_time: Время буферизации в секундах
        """
        self.callback = callback
        self.path_mapper = path_mapper
        self.buffer_time = buffer_time
        
        # Буфер событий {path: (last_event_time, event_type)}
        self.event_buffer: Dict[str, tuple] = {}
        
        # Блокировка для буфера
        self.buffer_lock = threading.Lock()
        
        # Поток для обработки буфера
        self.buffer_thread = threading.Thread(target=self._process_buffer, daemon=True)
        self.buffer_running = False
        
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Запускает обработку буфера."""
        self.buffer_running = True
        self.buffer_thread.start()
        self.logger.debug("Запущена обработка буфера событий")
    
    def stop(self):
        """Останавливает обработку буфера."""
        self.buffer_running = False
        if self.buffer_thread.is_alive():
            self.buffer_thread.join(timeout=2.0)
        self.logger.debug("Остановлена обработка буфера событий")
    
    def on_any_event(self, event: FileSystemEvent):
        """
        Обрабатывает любое событие файловой системы.
        
        Args:
            event: Событие файловой системы
        """
        # Игнорируем директории
        if event.is_directory:
            return
        
        # Игнорируем скрытые файлы и файлы синхронизации
        if self._should_ignore(str(event.src_path)):
            return
        
        # Определяем тип события
        event_type = self._get_event_type(event)
        
        # Специальная обработка для событий создания файла
        # (открытие файла часто идет перед событием created на некоторых ОС)
        if event_type == 'modified' and not os.path.getsize(event.src_path):
            # Если файл был только создан и пустой, считаем это событием created
            event_type = 'created'
            self.logger.debug(f"Событие modified для пустого файла переквалифицировано как created: {event.src_path}")
        
        # Преобразуем путь
        logical_path = self.path_mapper.to_logical(event.src_path)
        
        # Добавляем событие в буфер с учетом приоритета
        # (created имеет высший приоритет)
        with self.buffer_lock:
            # Если для этого пути уже есть событие в буфере
            if logical_path in self.event_buffer:
                current_time, current_type = self.event_buffer[logical_path]
                
                # Если текущее событие 'created', оно имеет приоритет
                if event_type == 'created':
                    self.event_buffer[logical_path] = (time.time(), event_type)
                    self.logger.debug(f"Событие {current_type} заменено на {event_type} для {logical_path}")
                # Если текущее событие не 'created', обновляем его только если это не 'created'
                elif current_type != 'created':
                    self.event_buffer[logical_path] = (time.time(), event_type)
            else:
                # Для нового пути просто добавляем событие
                self.event_buffer[logical_path] = (time.time(), event_type)
    
    def _get_event_type(self, event: FileSystemEvent) -> str:
        """
        Определяет тип события.
        
        Args:
            event: Событие файловой системы
            
        Returns:
            Тип события (created, modified, deleted, moved)
        """
        event_type = event.event_type
        
        # Нормализуем тип события
        if event_type == 'created':
            return 'created'
        elif event_type == 'modified':
            return 'modified'
        elif event_type == 'deleted':
            return 'deleted'
        elif event_type == 'moved':
            return 'moved'
        
        return event_type
    
    def _should_ignore(self, path: str) -> bool:
        """
        Проверяет, следует ли игнорировать файл.
        
        Args:
            path: Путь к файлу
            
        Returns:
            True, если файл следует игнорировать, иначе False
        """
        # Получаем имя файла
        basename = os.path.basename(path)
        
        # Игнорируем скрытые файлы и файлы синхронизации
        if basename.startswith('.'):
            return True
        
        # Игнорируем временные файлы
        ignore_extensions = [
            '.tmp', '.temp', '.swp', '.swo', '.pyc', '.pyo', '.pyd', '.bak', '.kate-swp'
        ]
        
        for ext in ignore_extensions:
            if basename.endswith(ext):
                return True
        
        # Игнорируем файлы синхронизации
        ignore_files = [
            'sync_state.json', '.sync_backups', '__pycache__'
        ]
        
        for ignore_file in ignore_files:
            if ignore_file in path:
                return True
        
        return False
    
    def _process_buffer(self):
        """Обрабатывает буфер событий."""
        while self.buffer_running:
            # Спим некоторое время
            time.sleep(0.1)
            
            current_time = time.time()
            processed_events = []
            
            # Проверяем буфер на наличие событий
            with self.buffer_lock:
                for path, (event_time, event_type) in self.event_buffer.items():
                    # Если прошло достаточно времени с момента события
                    if current_time - event_time >= self.buffer_time:
                        # Вызываем функцию обратного вызова
                        try:
                            self.callback(path, event_type)
                        except Exception as e:
                            self.logger.error(f"Ошибка обработки события {event_type} для {path}: {e}")
                        
                        # Отмечаем событие как обработанное
                        processed_events.append(path)
                
                # Удаляем обработанные события из буфера
                for path in processed_events:
                    del self.event_buffer[path]


class FileSystemWatcher:
    """
    Компонент для отслеживания изменений файлов в файловой системе.
    
    Использует watchdog для отслеживания изменений и буферизацию событий
    для предотвращения множественных оповещений.
    """
    
    def __init__(self, 
                path_mapper: Any,
                change_callback: Callable[[str, str], None],
                buffer_time: float = 0.5):
        """
        Инициализирует наблюдатель файловой системы.
        
        Args:
            path_mapper: Преобразователь путей
            change_callback: Функция обратного вызова (path, event_type)
            buffer_time: Время буферизации в секундах
        """
        self.path_mapper = path_mapper
        self.change_callback = change_callback
        
        # Обработчик событий
        self.event_handler = BufferedEventHandler(
            callback=change_callback,
            path_mapper=path_mapper,
            buffer_time=buffer_time
        )
        
        # Наблюдатель
        self.observer = Observer()
        
        # Отслеживаемые директории
        self.watched_dirs: Set[str] = set()
        
        self.logger = logging.getLogger(__name__)
    
    def start_watching(self, directories: List[str]) -> None:
        """
        Запускает отслеживание директорий.
        
        Args:
            directories: Список директорий для отслеживания
        """
        # Добавляем директории в список отслеживаемых
        for directory in directories:
            if not os.path.exists(directory):
                self.logger.warning(f"Директория не существует: {directory}")
                continue
            
            # Если директория уже отслеживается, пропускаем
            if directory in self.watched_dirs:
                continue
            
            # Запускаем наблюдение
            self.observer.schedule(
                self.event_handler,
                directory,
                recursive=True
            )
            
            self.watched_dirs.add(directory)
            self.logger.info(f"Запущено отслеживание директории: {directory}")
        
        # Запускаем наблюдатель, если не запущен
        if not self.observer.is_alive():
            self.observer.start()
            self.event_handler.start()
            self.logger.info("Запущен наблюдатель файловой системы")
    
    def stop_watching(self) -> None:
        """Останавливает отслеживание всех директорий."""
        # Останавливаем обработчик событий
        self.event_handler.stop()
        
        # Останавливаем наблюдатель
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        # Очищаем список отслеживаемых директорий
        self.watched_dirs.clear()
        
        self.logger.info("Остановлен наблюдатель файловой системы")
    
    def is_watching(self, directory: str) -> bool:
        """
        Проверяет, отслеживается ли директория.
        
        Args:
            directory: Директория для проверки
            
        Returns:
            True, если директория отслеживается, иначе False
        """
        return directory in self.watched_dirs
    
    def get_watched_directories(self) -> List[str]:
        """
        Возвращает список отслеживаемых директорий.
        
        Returns:
            Список отслеживаемых директорий
        """
        return list(self.watched_dirs)