"""
JTBD: Я (система) хочу иметь настоящий in-memory кеш для мгновенного доступа к документам,
чтобы избежать медленного чтения файлов с диска при каждом запросе.

Настоящий in-memory кеш разработанный через TDD стандарт v2.0.
Заменяет все существующие неработающие кеш-системы единым решением.

Модуль следует принципам TDD стандарта:
- Red-Green-Refactor цикл разработки
- JTBD документация для каждого компонента
- Хранение данных в RAM, а не на диске
- Thread-safe операции через RLock
- Контроль лимита памяти (200MB по умолчанию)
- Мгновенный доступ к документам (<1мс)

Автор: AI Assistant через TDD стандарт
Дата: 22 May 2025
"""

import os
import time
import threading
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Импорт UnifiedKeyResolver для решения проблемы синхронизации
try:
    from ..core.unified_key_resolver import get_resolver
except ImportError:
    try:
        from src.core.unified_key_resolver import get_resolver
    except ImportError:
        get_resolver = None

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """
    JTBD: Я (запись кеша) хочу хранить всю необходимую информацию о документе,
    чтобы обеспечить быстрый доступ и корректную синхронизацию.
    
    Запись в кеше с метаданными документа.
    """
    path: str
    content: str
    size: int
    modified_time: float
    doc_type: str
    metadata: Dict[str, Any]


class RealInMemoryCache:
    """
    JTBD: Я (система) хочу хранить документы в памяти для мгновенного доступа,
    чтобы избежать медленного чтения файлов с диска при каждом запросе.
    
    Настоящий in-memory кеш для быстрого доступа к документам.
    Разработан через TDD стандарт v2.0 с полным следованием принципам:
    - Хранение данных в RAM, а не на диске
    - Thread-safe операции через RLock
    - Контроль лимита памяти (200MB по умолчанию) 
    - Мгновенный доступ к документам (<1мс)
    - JTBD документация всех компонентов
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Реализует паттерн Singleton для единого кеша в системе."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_size_mb: int = 200):
        """
        JTBD: Я (кеш) хочу инициализироваться с правильными параметрами,
        чтобы контролировать использование памяти и обеспечить thread-safety.
        
        Инициализирует кеш с максимальным размером в MB.
        """
        if hasattr(self, '_initialized'):
            return
            
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.total_size = 0
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'files_loaded': 0,
            'memory_usage_mb': 0
        }
        
        # Инициализируем resolver для унифицированных ключей
        self.resolver = get_resolver() if get_resolver else None
        if self.resolver:
            logger.info("UnifiedKeyResolver интегрирован с кешем")
        
        self._initialized = True
        logger.info(f"Инициализирован RealInMemoryCache с лимитом {max_size_mb}MB")
    
    def load_documents(self, base_paths: List[str]) -> int:
        """
        JTBD: Я (кеш) хочу загрузить документы из файловой системы в память,
        чтобы обеспечить мгновенный доступ к ним без чтения диска.
        
        Загружает документы из указанных путей в память. Возвращает количество загруженных.
        """
        with self.lock:
            loaded_count = 0
            
            for base_path in base_paths:
                if not os.path.exists(base_path):
                    logger.warning(f"Путь не существует: {base_path}")
                    continue
                    
                logger.info(f"Загружаем документы из: {base_path}")
                
                # Обходим директорию рекурсивно с фильтрацией архивов
                for root, dirs, files in os.walk(base_path):
                    # Исключаем архивные папки на всех уровнях
                    archive_patterns = ['[archive]', 'archive', 'backup', '20250', 'old', 'deprecated', 'consolidated', 'rename', 'template']
                    dirs[:] = [d for d in dirs if not any(pattern in d.lower() for pattern in archive_patterns)]
                    
                    # Дополнительная проверка: пропускаем если текущая папка архивная
                    current_path_lower = root.lower()
                    is_archive_path = any(pattern in current_path_lower for pattern in archive_patterns)
                    if is_archive_path:
                        continue
                    
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            
                            try:
                                # Читаем файл в память
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Создаем запись кеша
                                size = len(content.encode('utf-8'))
                                modified_time = os.path.getmtime(file_path)
                                doc_type = self._detect_document_type(file_path, content)
                                
                                entry = CacheEntry(
                                    path=file_path,
                                    content=content,
                                    size=size,
                                    modified_time=modified_time,
                                    doc_type=doc_type,
                                    metadata={'loaded_at': datetime.now().isoformat()}
                                )
                                
                                # Проверяем лимит памяти
                                if self.total_size + size <= self.max_size_bytes:
                                    self.cache[file_path] = entry
                                    self.total_size += size
                                    loaded_count += 1
                                    logger.debug(f"Загружен в кеш: {file_path} ({size} bytes)")
                                else:
                                    logger.warning(f"Превышен лимит памяти, пропускаем: {file_path}")
                                
                            except Exception as e:
                                logger.error(f"Ошибка загрузки файла {file_path}: {e}")
                                continue
            
            # Обновляем статистику
            self.stats['files_loaded'] = loaded_count
            self.stats['memory_usage_mb'] = int(self.total_size / (1024 * 1024))
            
            logger.info(f"Загружено в кеш: {loaded_count} документов, использование памяти: {self.stats['memory_usage_mb']:.2f}MB")
            return loaded_count
    
    def _detect_document_type(self, file_path: str, content: str) -> str:
        """
        JTBD: Я (система типизации) хочу правильно определить тип документа,
        чтобы обеспечить корректную фильтрацию и категоризацию.
        
        Определяет тип документа по пути и содержимому.
        """
        if '[standards .md]' in file_path:
            return 'standard'
        elif '[todo · incidents]' in file_path:
            if '## 5-почему анализ' in content or 'incident_' in file_path:
                return 'incident'
            else:
                return 'task'
        elif 'projects' in file_path:
            return 'project'
        else:
            return 'document'
    
    def get_document(self, file_path: str) -> Optional[CacheEntry]:
        """
        JTBD: Я (пользователь) хочу мгновенно получить документ из кеша,
        чтобы избежать медленного чтения с диска.
        
        Получает документ из кеша с поддержкой унифицированных ключей.
        """
        with self.lock:
            # Сначала пробуем прямой поиск
            if file_path in self.cache:
                self.stats['hits'] += 1
                return self.cache[file_path]
            
            # Если не найден и есть resolver, пробуем унифицированный поиск
            if self.resolver:
                available_keys = list(self.cache.keys())
                found_key = self.resolver.find_by_any_key(file_path, available_keys)
                if found_key and found_key in self.cache:
                    self.stats['hits'] += 1
                    return self.cache[found_key]
            
            # Документ не найден
            self.stats['misses'] += 1
            return None
    
    def get_documents_by_type(self, doc_type: str) -> List[CacheEntry]:
        """
        JTBD: Я (пользователь) хочу получить все документы определенного типа,
        чтобы работать с однотипными документами.
        
        Получает все документы указанного типа.
        """
        with self.lock:
            return [entry for entry in self.cache.values() if entry.doc_type == doc_type]
    
    def search_documents(self, query: str) -> List[CacheEntry]:
        """
        JTBD: Я (пользователь) хочу найти документы по содержимому,
        чтобы быстро найти нужную информацию.
        
        Ищет документы по содержимому.
        """
        with self.lock:
            query_lower = query.lower()
            results = []
            
            for entry in self.cache.values():
                if query_lower in entry.content.lower():
                    results.append(entry)
            
            return results
    
    def refresh_file(self, file_path: str) -> bool:
        """
        JTBD: Я (кеш) хочу обновить измененный файл в памяти,
        чтобы отражать актуальное состояние файловой системы.
        
        Обновляет один файл в кеше если он изменился.
        """
        with self.lock:
            if not os.path.exists(file_path):
                # Удаляем из кеша если файл удален
                if file_path in self.cache:
                    old_entry = self.cache[file_path]
                    del self.cache[file_path]
                    self.total_size -= old_entry.size
                    logger.info(f"Удален из кеша: {file_path}")
                    return True
                return False
            
            try:
                current_mtime = os.path.getmtime(file_path)
                
                # Проверяем нужно ли обновление
                if file_path in self.cache:
                    cached_entry = self.cache[file_path]
                    if cached_entry.modified_time >= current_mtime:
                        return False  # Файл не изменился
                    
                    # Удаляем старую запись
                    self.total_size -= cached_entry.size
                
                # Загружаем новое содержимое
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                size = len(content.encode('utf-8'))
                doc_type = self._detect_document_type(file_path, content)
                
                new_entry = CacheEntry(
                    path=file_path,
                    content=content,
                    size=size,
                    modified_time=current_mtime,
                    doc_type=doc_type,
                    metadata={'updated_at': datetime.now().isoformat()}
                )
                
                # Проверяем лимит памяти
                if self.total_size + size <= self.max_size_bytes:
                    self.cache[file_path] = new_entry
                    self.total_size += size
                    self.stats['memory_usage_mb'] = int(self.total_size / (1024 * 1024))
                    logger.info(f"Обновлен в кеше: {file_path}")
                    return True
                
                logger.warning(f"Превышен лимит памяти при обновлении: {file_path}")
                return False
                
            except Exception as e:
                logger.error(f"Ошибка обновления файла {file_path}: {e}")
                return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        JTBD: Я (администратор) хочу видеть статистику использования кеша,
        чтобы контролировать его эффективность и производительность.
        
        Возвращает статистику использования кеша.
        """
        with self.lock:
            hit_rate = 0
            if (self.stats['hits'] + self.stats['misses']) > 0:
                hit_rate = (self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])) * 100
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate_percent': round(hit_rate, 1),
                'files_loaded': self.stats['files_loaded'],
                'memory_usage_mb': round(self.total_size / (1024 * 1024), 2),
                'total_documents': len(self.cache),
                'max_memory_mb': self.max_size_bytes / (1024 * 1024),
                'memory_usage_percent': round((self.total_size / self.max_size_bytes) * 100, 1),
                'document_types': self._get_document_type_stats()
            }
    
    def _get_document_type_stats(self) -> Dict[str, int]:
        """Возвращает статистику по типам документов в кеше."""
        stats = {}
        for entry in self.cache.values():
            stats[entry.doc_type] = stats.get(entry.doc_type, 0) + 1
        return stats
    
    def clear(self) -> None:
        """
        JTBD: Я (система) хочу полностью очистить кеш,
        чтобы освободить память и начать с чистого состояния.
        
        Очищает весь кеш.
        """
        with self.lock:
            self.cache.clear()
            self.total_size = 0
            self.stats['memory_usage_mb'] = 0
            logger.info("Кеш полностью очищен")
    
    def update_document(self, file_path: str, content: str) -> bool:
        """
        JTBD: Я (система) хочу обновить документ в кеше и на диске,
        чтобы обеспечить bidirectional синхронизацию данных с rollback механизмом.
        """
        # Сохраняем предыдущее состояние для rollback
        previous_entry = None
        try:
            with self.lock:
                # Сохраняем текущее состояние кеша для rollback
                if file_path in self.cache:
                    previous_entry = self.cache[file_path]
                
                # Записываем на диск (критическая операция)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Обновляем кеш только после успешной записи
                file_stats = os.stat(file_path)
                doc_type = self._detect_document_type(file_path, content)
                
                self.cache[file_path] = CacheEntry(
                    path=file_path,
                    content=content,
                    size=len(content.encode('utf-8')),
                    modified_time=file_stats.st_mtime,
                    doc_type=doc_type,
                    metadata={}
                )
                
                logger.info(f"Обновлен документ: {file_path}")
                return True
                
        except Exception as e:
            # ROLLBACK: восстанавливаем предыдущее состояние кеша
            if previous_entry:
                self.cache[file_path] = previous_entry
                logger.warning(f"Rollback кеша для {file_path} выполнен")
            elif file_path in self.cache:
                del self.cache[file_path]
                logger.warning(f"Удален некорректный entry {file_path} из кеша")
            
            logger.error(f"Ошибка обновления документа {file_path}: {e}")
            return False
    
    def create_document(self, file_path: str, content: str) -> bool:
        """
        JTBD: Я (система) хочу создать новый документ в кеше и на диске,
        чтобы обеспечить консистентность данных.
        """
        try:
            with self.lock:
                # Создаем директории если путь содержит директорию
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                
                # Создаем файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Добавляем в кеш
                file_stats = os.stat(file_path)
                doc_type = self._detect_document_type(file_path, content)
                
                self.cache[file_path] = CacheEntry(
                    path=file_path,
                    content=content,
                    size=len(content.encode('utf-8')),
                    modified_time=file_stats.st_mtime,
                    doc_type=doc_type,
                    metadata={}
                )
                
                logger.info(f"Создан документ: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка создания документа {file_path}: {e}")
            return False
    
    def get_all_paths(self) -> List[str]:
        """
        JTBD: Я (пользователь) хочу получить список всех путей в кеше,
        чтобы знать какие документы доступны.
        
        Возвращает список всех путей к файлам в кеше.
        """
        with self.lock:
            return list(self.cache.keys())
    
    def initialize_from_disk(self) -> bool:
        """
        Загружает все markdown файлы с диска в кеш.
        
        Returns:
            bool: True если загрузка успешна
        """
        import os
        
        try:
            # ИСПРАВЛЕНО: используем правильные пути с учетом рабочей директории
            import os
            if os.path.basename(os.getcwd()) == 'advising_platform':
                # Если запускаем из подпапки - идем на уровень выше
                base_paths = [
                    "../[standards .md]",  # Все стандарты
                    "../[todo · incidents]",  # Задачи и инциденты
                    "../projects"  # Проекты
                ]
            else:
                # Если запускаем из корня
                base_paths = [
                    "[standards .md]",  # Все стандарты
                    "[todo · incidents]",  # Задачи и инциденты
                    "projects"  # Проекты
                ]
            
            loaded_count = self.load_documents(base_paths)
            
            if loaded_count > 0:
                logger.info(f"Успешно загружено {loaded_count} документов в кеш")
                return True
            else:
                logger.warning("Не удалось загрузить документы в кеш")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке файлов в кеш: {e}")
            return False


# Глобальный экземпляр кеша
cache_instance = RealInMemoryCache()


def get_cache() -> RealInMemoryCache:
    """
    JTBD: Я (система) хочу получить доступ к единому экземпляру кеша,
    чтобы обеспечить консистентность данных во всем приложении.
    
    Возвращает глобальный экземпляр кеша.
    """
    return cache_instance