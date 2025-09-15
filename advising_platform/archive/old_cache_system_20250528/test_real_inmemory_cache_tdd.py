"""
TDD тесты для проектирования настоящего in-memory кеша.

Цель: Спроектировать через TDD методологию настоящий кеш в памяти
который будет хранить документы, стандарты, задачи и инциденты в RAM
для мгновенного доступа без чтения диска.

Принципы TDD:
1. Red: Написать тест для нужной функциональности (провалится)
2. Green: Написать минимальный код для прохождения теста  
3. Refactor: Улучшить код сохраняя прохождение тестов

Требования к кешу:
- Хранение 200MB данных в памяти
- Загрузка файлов в память при инициализации
- Мгновенный доступ к данным без чтения диска
- Автоматическое обновление при изменении файлов
- Thread-safe операции
"""

import unittest
import os
import time
import threading
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CacheEntry:
    """Запись в кеше с метаданными."""
    path: str
    content: str
    size: int
    modified_time: float
    doc_type: str
    metadata: Dict[str, Any]


class InMemoryCache:
    """
    JTBD: Я (система) хочу хранить документы в памяти для мгновенного доступа,
    чтобы избежать медленного чтения файлов с диска при каждом запросе.
    
    Настоящий in-memory кеш для быстрого доступа к документам.
    Следует принципам TDD стандарта v2.0:
    - Хранение данных в RAM, а не на диске
    - Thread-safe операции через RLock
    - Контроль лимита памяти (200MB по умолчанию) 
    - Мгновенный доступ к документам (<1мс)
    """
    
    def __init__(self, max_size_mb: int = 200):
        """
        JTBD: Я (кеш) хочу инициализироваться с правильными параметрами,
        чтобы контролировать использование памяти и обеспечить thread-safety.
        
        Инициализирует кеш с максимальным размером в MB.
        """
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
                    continue
                    
                # Обходим директорию рекурсивно
                for root, dirs, files in os.walk(base_path):
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
                                    metadata={}
                                )
                                
                                # Проверяем лимит памяти
                                if self.total_size + size <= self.max_size_bytes:
                                    self.cache[file_path] = entry
                                    self.total_size += size
                                    loaded_count += 1
                                
                            except Exception as e:
                                continue
            
            # Обновляем статистику
            self.stats['files_loaded'] = loaded_count
            self.stats['memory_usage_mb'] = self.total_size / (1024 * 1024)
            
            return loaded_count
    
    def _detect_document_type(self, file_path: str, content: str) -> str:
        """Определяет тип документа по пути и содержимому."""
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
        
        Получает документ из кеша. Возвращает None если не найден.
        """
        with self.lock:
            if file_path in self.cache:
                self.stats['hits'] += 1
                return self.cache[file_path]
            else:
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
                    metadata={}
                )
                
                # Проверяем лимит памяти
                if self.total_size + size <= self.max_size_bytes:
                    self.cache[file_path] = new_entry
                    self.total_size += size
                    self.stats['memory_usage_mb'] = self.total_size / (1024 * 1024)
                    return True
                
                return False
                
            except Exception:
                return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        JTBD: Я (администратор) хочу видеть статистику использования кеша,
        чтобы контролировать его эффективность и производительность.
        
        Возвращает статистику использования кеша.
        """
        with self.lock:
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'files_loaded': self.stats['files_loaded'],
                'memory_usage_mb': round(self.total_size / (1024 * 1024), 2),
                'total_documents': len(self.cache),
                'max_memory_mb': self.max_size_bytes / (1024 * 1024),
                'memory_usage_percent': round((self.total_size / self.max_size_bytes) * 100, 1)
            }
    
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


class TestInMemoryCacheTDD(unittest.TestCase):
    """TDD тесты для проектирования in-memory кеша."""
    
    def setUp(self):
        """Настройка каждого теста."""
        self.cache = InMemoryCache(max_size_mb=10)  # Небольшой размер для тестов
        self.test_files = [
            "[standards .md]/0. core standards/registry_standard.md",
            "[todo · incidents]/todo.md"
        ]
    
    def test_cache_initialization(self):
        """Тест 1: Кеш должен инициализироваться с правильными параметрами."""
        # Red phase: тест должен проваливаться пока не реализуем
        self.assertEqual(self.cache.max_size_bytes, 10 * 1024 * 1024)
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(self.cache.total_size, 0)
        self.assertIsNotNone(self.cache.lock)
        
        # Проверяем начальную статистику
        stats = self.cache.get_statistics()
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)
        self.assertEqual(stats['files_loaded'], 0)
    
    def test_load_documents_from_filesystem(self):
        """Тест 2: Кеш должен загружать документы из файловой системы в память."""
        # Red phase: тест провалится пока не реализуем load_documents
        loaded_count = self.cache.load_documents([
            "../[standards .md]",
            "../[todo · incidents]"
        ])
        
        # Проверяем что документы загружены
        self.assertGreater(loaded_count, 0, "Должен загрузить хотя бы один документ")
        self.assertGreater(len(self.cache.cache), 0, "Кеш должен содержать документы")
        self.assertGreater(self.cache.total_size, 0, "Размер кеша должен увеличиться")
        
        # Проверяем статистику
        stats = self.cache.get_statistics()
        self.assertEqual(stats['files_loaded'], loaded_count)
        self.assertGreater(stats['memory_usage_mb'], 0)
    
    def test_get_document_instant_access(self):
        """Тест 3: Получение документа должно быть мгновенным (из памяти, не с диска)."""
        # Сначала загружаем документы
        loaded_count = self.cache.load_documents(["../[standards .md]", "../[todo · incidents]"])
        self.assertGreater(loaded_count, 0, "Должны загрузиться документы")
        
        # Получаем список загруженных файлов для тестирования
        stats = self.cache.get_statistics()
        self.assertGreater(stats['total_documents'], 0, "В кеше должны быть документы")
        
        # Берем первый найденный документ стандарта
        standards = self.cache.get_documents_by_type('standard')
        self.assertGreater(len(standards), 0, "Должны найтись стандарты")
        
        test_file_path = standards[0].path
        
        # Засекаем время доступа к документу
        start_time = time.time()
        entry = self.cache.get_document(test_file_path)
        access_time = time.time() - start_time
        
        # Проверяем что документ найден
        self.assertIsNotNone(entry, "Документ должен быть найден в кеше")
        self.assertIsInstance(entry, CacheEntry)
        self.assertGreater(len(entry.content), 0, "Содержимое должно быть загружено")
        
        # Проверяем что доступ мгновенный (менее 1мс)
        self.assertLess(access_time, 0.001, "Доступ к кешу должен быть мгновенным")
        
        # Проверяем счетчики попаданий
        updated_stats = self.cache.get_statistics()
        self.assertEqual(updated_stats['hits'], 1)
    
    def test_get_documents_by_type_filtering(self):
        """Тест 4: Кеш должен фильтровать документы по типу."""
        # Загружаем документы разных типов
        self.cache.load_documents([
            "../[standards .md]",
            "../[todo · incidents]"
        ])
        
        # Получаем стандарты
        standards = self.cache.get_documents_by_type("standard")
        self.assertGreater(len(standards), 0, "Должны найтись стандарты")
        
        # Получаем задачи
        tasks = self.cache.get_documents_by_type("task")
        self.assertGreater(len(tasks), 0, "Должны найтись задачи")
        
        # Проверяем что типы правильные
        for entry in standards:
            self.assertEqual(entry.doc_type, "standard")
        for entry in tasks:
            self.assertEqual(entry.doc_type, "task")
    
    def test_search_documents_content(self):
        """Тест 5: Кеш должен искать по содержимому документов."""
        # Загружаем документы
        self.cache.load_documents(["../[standards .md]"])
        
        # Ищем по ключевому слову
        results = self.cache.search_documents("registry")
        self.assertGreater(len(results), 0, "Должны найтись документы с 'registry'")
        
        # Проверяем что результаты действительно содержат слово
        for entry in results:
            self.assertIn("registry", entry.content.lower())
    
    def test_cache_refresh_on_file_change(self):
        """Тест 6: Кеш должен обновляться при изменении файлов."""
        # Загружаем документ
        test_file = "../test_cache_file.md"
        
        # Создаем тестовый файл
        with open(test_file, 'w') as f:
            f.write("Original content")
        
        try:
            self.cache.load_documents([os.path.dirname(test_file)])
            original_entry = self.cache.get_document(test_file)
            self.assertIsNotNone(original_entry)
            
            # Изменяем файл
            time.sleep(0.1)  # Чтобы время изменения отличалось
            with open(test_file, 'w') as f:
                f.write("Updated content")
            
            # Обновляем кеш
            updated = self.cache.refresh_file(test_file)
            self.assertTrue(updated, "Файл должен быть обновлен")
            
            # Проверяем что содержимое изменилось
            new_entry = self.cache.get_document(test_file)
            self.assertNotEqual(original_entry.content, new_entry.content)
            self.assertIn("Updated", new_entry.content)
            
        finally:
            # Удаляем тестовый файл
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_memory_limit_enforcement(self):
        """Тест 7: Кеш должен соблюдать лимит памяти."""
        # Создаем кеш с очень маленьким лимитом
        small_cache = InMemoryCache(max_size_mb=1)
        
        # Пытаемся загрузить много документов
        loaded = small_cache.load_documents([
            "../[standards .md]",
            "../[todo · incidents]"
        ])
        
        # Проверяем что размер не превышает лимит
        stats = small_cache.get_statistics()
        self.assertLessEqual(stats['memory_usage_mb'], 1.1, "Не должен превышать лимит памяти")
    
    def test_thread_safety(self):
        """Тест 8: Кеш должен быть thread-safe."""
        # Загружаем документы
        loaded_count = self.cache.load_documents(["../[standards .md]", "../[todo · incidents]"])
        self.assertGreater(loaded_count, 0, "Должны загрузиться документы")
        
        # Получаем первый документ для тестирования
        standards = self.cache.get_documents_by_type('standard')
        self.assertGreater(len(standards), 0, "Должны найтись стандарты")
        test_file_path = standards[0].path
        
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    entry = self.cache.get_document(test_file_path)
                    results.append(entry is not None)
            except Exception as e:
                errors.append(e)
        
        # Запускаем несколько потоков одновременно
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Проверяем что нет ошибок и все получили данные
        self.assertEqual(len(errors), 0, "Не должно быть ошибок в многопоточном доступе")
        self.assertTrue(all(results), "Все потоки должны получить данные")
    
    def test_cache_clear(self):
        """Тест 9: Кеш должен полностью очищаться."""
        # Загружаем документы
        self.cache.load_documents(["../[standards .md]"])
        
        # Проверяем что кеш не пустой
        self.assertGreater(len(self.cache.cache), 0)
        self.assertGreater(self.cache.total_size, 0)
        
        # Очищаем кеш
        self.cache.clear()
        
        # Проверяем что кеш пуст
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(self.cache.total_size, 0)
        
        stats = self.cache.get_statistics()
        self.assertEqual(stats['memory_usage_mb'], 0)


if __name__ == '__main__':
    print("🎯 === TDD ПРОЕКТИРОВАНИЕ IN-MEMORY КЕША ===")
    print("Запуск тестов для проектирования настоящего кеша...")
    unittest.main(verbosity=2)