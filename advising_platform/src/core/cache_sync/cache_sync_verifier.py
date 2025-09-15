"""
Модуль для проверки и поддержания синхронизации между кешем и файловой системой.

ВНИМАНИЕ: Этот файл был автоматически обновлен для использования оптимизированного верификатора.
Оригинальная версия сохранена в файле с расширением .bak.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Tuple, Any, Optional, Set, Union

# Настройка логирования
logger = logging.getLogger("cache_sync_verifier")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Импортируем оптимизированный верификатор
try:
    from advising_platform.src.core.cache_sync.optimized_verifier import OptimizedVerifier
    from advising_platform.src.core.cache_sync.optimized_verifier import CacheEntry
    
    # Рекомендуем использовать оптимизированный верификатор
    CacheSyncVerifier = OptimizedVerifier
    logger.info("Используется оптимизированный верификатор кеша")
except ImportError:
    # Если оптимизированный верификатор недоступен, определяем базовую версию
    logger.warning("Оптимизированный верификатор недоступен, используется базовая версия")
    
    class CacheEntry:
        """JTBD:
Я (разработчик) хочу использовать функциональность класса CacheEntry, чтобы эффективно решать соответствующие задачи в системе.
    
    Представление записи в кеше."""
        
        def __init__(
            self,
            path: str,
            content_hash: Optional[str] = None,
            last_modified: Optional[float] = None,
            size: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None
        ):
            """
            Инициализация записи кеша.
            
            Args:
                path: Путь к файлу
                content_hash: Хеш содержимого файла
                last_modified: Время последнего изменения файла
                size: Размер файла в байтах
                metadata: Дополнительные метаданные
            """
            self.path = path
            self.content_hash = content_hash
            self.last_modified = last_modified
            self.size = size
            self.metadata = metadata or {}
        
        def to_dict(self) -> Dict[str, Any]:
            """
            Преобразует запись в словарь.
            
            Returns:
                Словарь с данными записи
            """
            return {
                "path": self.path,
                "content_hash": self.content_hash,
                "last_modified": self.last_modified,
                "size": self.size,
                "metadata": self.metadata
            }
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
            """
            Создает запись из словаря.
            
            Args:
                data: Словарь с данными записи
                
            Returns:
                Экземпляр записи кеша
            """
            return cls(
                path=data["path"],
                content_hash=data.get("content_hash"),
                last_modified=data.get("last_modified"),
                size=data.get("size"),
                metadata=data.get("metadata", {})
            )
    
    
    class CacheSyncVerifier:
        """
        Верификатор синхронизации кеша.
        
        Обеспечивает проверку соответствия между кешем и файловой системой.
        """
        
        def __init__(
            self,
            cache_paths: List[str] = [".cache_state.json"],
            base_dir: str = "."
        ):
            """
            Инициализация верификатора.
            
            Args:
                cache_paths: Список путей к файлам кеша
                base_dir: Базовая директория для проверки файлов
            """
            self.cache_paths = cache_paths
            self.base_dir = os.path.abspath(base_dir)
            self.cache = {}
            
            # Загружаем кеш
            for cache_path in self.cache_paths:
                self.load_cache_from_file(cache_path)
        
        def load_cache_from_file(self, cache_path: str) -> bool:
            """
            Загружает кеш из файла.
            
            Args:
                cache_path: Путь к файлу кеша
                
            Returns:
                True, если загрузка успешна, иначе False
            """
            import json
            
            if not os.path.exists(cache_path):
                logger.info(f"Файл кеша {cache_path} не существует")
                return False
            
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for path, entry_data in data.items():
                    self.cache[path] = CacheEntry.from_dict(entry_data)
                
                logger.info(f"Загружено {len(self.cache)} записей из кеша {cache_path}")
                return True
            except Exception as e:
                logger.error(f"Ошибка при загрузке кеша {cache_path}: {e}")
                return False
        
        def save_cache_to_file(self, cache_path: str) -> bool:
            """
            Сохраняет кеш в файл.
            
            Args:
                cache_path: Путь к файлу кеша
                
            Returns:
                True, если сохранение успешно, иначе False
            """
            import json
            
            try:
                # Преобразуем записи кеша в словари
                data = {path: entry.to_dict() for path, entry in self.cache.items()}
                
                # Создаем директорию, если она не существует
                os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
                
                # Сохраняем данные в файл
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Сохранено {len(self.cache)} записей в кеш {cache_path}")
                return True
            except Exception as e:
                logger.error(f"Ошибка при сохранении кеша {cache_path}: {e}")
                return False
        
        def get_file_metadata(self, file_path: str) -> Tuple[float, int, Optional[str]]:
            """
            Получает метаданные файла.
            
            Args:
                file_path: Путь к файлу
                
            Returns:
                Кортеж (время последнего изменения, размер, хеш содержимого)
            """
            try:
                import hashlib
                
                # Получаем информацию о файле
                stat = os.stat(file_path)
                last_modified = stat.st_mtime
                size = stat.st_size
                
                # Вычисляем хеш содержимого
                content_hash = None
                try:
                    # Ограничиваем размер файла для хеширования (10MB)
                    if size <= 10 * 1024 * 1024:
                        with open(file_path, "rb") as f:
                            content = f.read()
                        content_hash = hashlib.md5(content).hexdigest()
                    else:
                        logger.warning(f"Файл {file_path} слишком большой для проверки ({size} байт)")
                except Exception as e:
                    logger.warning(f"Не удалось вычислить хеш для файла {file_path}: {e}")
                
                return last_modified, size, content_hash
            except Exception as e:
                logger.error(f"Ошибка при получении метаданных файла {file_path}: {e}")
                return 0, 0, None
        
        def scan_filesystem(self) -> List[str]:
            """
            Сканирует файловую систему и возвращает список файлов.
            
            Returns:
                Список путей к файлам
            """
            files = []
            
            # Проходим по всем файлам в базовой директории
            for root, dirs, filenames in os.walk(self.base_dir):
                # Исключаем директории, которые начинаются с точки
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                
                # Добавляем файлы
                for filename in filenames:
                    # Исключаем файлы, которые начинаются с точки
                    if filename.startswith("."):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.base_dir)
                    
                    # Исключаем бинарные и временные файлы
                    extensions_to_skip = [
                        ".pyc", ".pyo", ".so", ".dll", ".exe",
                        ".zip", ".tar", ".gz", ".bz2", ".rar",
                        ".jpg", ".jpeg", ".png", ".gif", ".ico",
                        ".mp3", ".mp4", ".avi", ".mkv", ".mov",
                        ".db", ".sqlite", ".sqlite3",
                        ".tmp", ".temp", ".bak", ".swp"
                    ]
                    
                    if any(rel_path.endswith(ext) for ext in extensions_to_skip):
                        continue
                    
                    # Добавляем файл
                    files.append(rel_path)
            
            logger.info(f"Найдено {len(files)} файлов в файловой системе")
            return files
        
        def verify_sync(self) -> Tuple[List[str], List[str], List[Tuple[str, Dict[str, Any], Dict[str, Any]]]]:
            """
            Проверяет синхронизацию кеша с файловой системой.
            
            Returns:
                Кортеж (файлы, отсутствующие в кеше; файлы, отсутствующие в файловой системе;
                файлы с несоответствием метаданных)
            """
            logger.info("Начало проверки синхронизации кеша с файловой системой")
            
            # Сканируем файловую систему
            files = self.scan_filesystem()
            files_set = set(files)
            cache_keys_set = set(self.cache.keys())
            
            # Находим файлы, отсутствующие в кеше
            missing_in_cache = list(files_set - cache_keys_set)
            
            # Находим файлы, отсутствующие в файловой системе
            missing_in_filesystem = list(cache_keys_set - files_set)
            
            # Проверяем метаданные для файлов, присутствующих и в кеше, и в файловой системе
            metadata_mismatch = []
            common_files = files_set.intersection(cache_keys_set)
            
            logger.info(f"Проверка соответствия метаданных для {len(common_files)} файлов")
            
            for file_path in common_files:
                abs_path = os.path.join(self.base_dir, file_path)
                
                # Проверяем только если файл существует
                if not os.path.exists(abs_path):
                    continue
                
                # Получаем метаданные файла
                last_modified, size, content_hash = self.get_file_metadata(abs_path)
                
                # Проверяем метаданные
                cache_entry = self.cache[file_path]
                
                if size != cache_entry.size:
                    metadata_mismatch.append((
                        file_path,
                        {"size": size, "last_modified": last_modified},
                        {"size": cache_entry.size, "last_modified": cache_entry.last_modified}
                    ))
                    continue
                
                if abs(last_modified - (cache_entry.last_modified or 0)) > 1:
                    metadata_mismatch.append((
                        file_path,
                        {"size": size, "last_modified": last_modified},
                        {"size": cache_entry.size, "last_modified": cache_entry.last_modified}
                    ))
                    continue
                
                # Если размер файла превышает лимит, не проверяем хеш
                if size > 10 * 1024 * 1024:
                    continue
                
                # Проверяем хеш только если он есть в кеше и был вычислен для файла
                if cache_entry.content_hash and content_hash and cache_entry.content_hash != content_hash:
                    metadata_mismatch.append((
                        file_path,
                        {"content_hash": content_hash},
                        {"content_hash": cache_entry.content_hash}
                    ))
            
            logger.info(f"Найдено {len(missing_in_cache)} файлов, отсутствующих в кеше")
            logger.info(f"Найдено {len(missing_in_filesystem)} файлов, отсутствующих в файловой системе")
            logger.info(f"Найдено {len(metadata_mismatch)} файлов с несоответствием метаданных")
            
            return missing_in_cache, missing_in_filesystem, metadata_mismatch
        
        def fix_sync_issues(self) -> bool:
            """
            Исправляет проблемы синхронизации.
            
            Returns:
                True, если все проблемы исправлены успешно, иначе False
            """
            logger.info("Начало исправления несоответствий")
            
            # Проверяем синхронизацию
            missing_in_cache, missing_in_filesystem, metadata_mismatch = self.verify_sync()
            
            # Добавляем отсутствующие в кеше файлы
            for file_path in missing_in_cache:
                abs_path = os.path.join(self.base_dir, file_path)
                
                # Пропускаем несуществующие файлы
                if not os.path.exists(abs_path):
                    continue
                
                # Получаем метаданные файла
                last_modified, size, content_hash = self.get_file_metadata(abs_path)
                
                # Создаем запись в кеше
                self.cache[file_path] = CacheEntry(
                    path=file_path,
                    content_hash=content_hash,
                    last_modified=last_modified,
                    size=size
                )
            
            # Удаляем отсутствующие в файловой системе файлы из кеша
            for file_path in missing_in_filesystem:
                if file_path in self.cache:
                    del self.cache[file_path]
            
            # Обновляем метаданные для файлов с несоответствием
            for file_path, _, _ in metadata_mismatch:
                abs_path = os.path.join(self.base_dir, file_path)
                
                # Пропускаем несуществующие файлы
                if not os.path.exists(abs_path):
                    continue
                
                # Получаем метаданные файла
                last_modified, size, content_hash = self.get_file_metadata(abs_path)
                
                # Обновляем запись в кеше
                self.cache[file_path] = CacheEntry(
                    path=file_path,
                    content_hash=content_hash,
                    last_modified=last_modified,
                    size=size,
                    metadata=self.cache[file_path].metadata if file_path in self.cache else {}
                )
            
            # Сохраняем обновленный кеш
            all_saved = True
            for cache_path in self.cache_paths:
                if not self.save_cache_to_file(cache_path):
                    all_saved = False
            
            if all_saved:
                logger.info("Все несоответствия успешно исправлены")
            else:
                logger.warning("Не удалось сохранить все изменения в кеш")
            
            return all_saved
        
        def update_file_in_cache(self, file_path: str) -> bool:
            """
            Обновляет информацию о файле в кеше.
            
            Args:
                file_path: Путь к файлу
                
            Returns:
                True, если обновление успешно, иначе False
            """
            try:
                # Преобразуем в относительный путь
                rel_path = os.path.relpath(file_path, self.base_dir)
                abs_path = os.path.join(self.base_dir, rel_path)
                
                # Проверяем, существует ли файл
                if not os.path.exists(abs_path):
                    if rel_path in self.cache:
                        del self.cache[rel_path]
                        return all(self.save_cache_to_file(cache_path) for cache_path in self.cache_paths)
                    return True
                
                # Получаем метаданные файла
                last_modified, size, content_hash = self.get_file_metadata(abs_path)
                
                # Обновляем запись в кеше
                self.cache[rel_path] = CacheEntry(
                    path=rel_path,
                    content_hash=content_hash,
                    last_modified=last_modified,
                    size=size,
                    metadata=self.cache[rel_path].metadata if rel_path in self.cache else {}
                )
                
                # Сохраняем кеш
                return all(self.save_cache_to_file(cache_path) for cache_path in self.cache_paths)
            except Exception as e:
                logger.error(f"Ошибка при обновлении файла {file_path} в кеше: {e}")
                return False
        
        def initialize_cache(self) -> bool:
            """
            Инициализирует кеш на основе текущего состояния файловой системы.
            
            Returns:
                True, если инициализация успешна, иначе False
            """
            logger.info("Начало инициализации кеша")
            
            # Очищаем текущий кеш
            self.cache = {}
            
            # Сканируем файловую систему
            files = self.scan_filesystem()
            
            # Добавляем файлы в кеш
            for file_path in files:
                abs_path = os.path.join(self.base_dir, file_path)
                
                # Пропускаем несуществующие файлы
                if not os.path.exists(abs_path):
                    continue
                
                # Получаем метаданные файла
                last_modified, size, content_hash = self.get_file_metadata(abs_path)
                
                # Создаем запись в кеше
                self.cache[file_path] = CacheEntry(
                    path=file_path,
                    content_hash=content_hash,
                    last_modified=last_modified,
                    size=size
                )
            
            # Сохраняем кеш
            all_saved = True
            for cache_path in self.cache_paths:
                if not self.save_cache_to_file(cache_path):
                    all_saved = False
            
            if all_saved:
                logger.info(f"Кеш успешно инициализирован с {len(self.cache)} записями")
            else:
                logger.warning("Не удалось сохранить кеш во все файлы")
            
            return all_saved
