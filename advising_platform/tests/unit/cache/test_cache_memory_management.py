#!/usr/bin/env python3
"""
Тесты для системы управления памятью в механизме кеширования.
Следует подходу TDD (Test-Driven Development) и методологии RADAR:
- Recognize: Распознаем проблему утечки памяти
- Analyze: Анализируем причины и возможные решения
- Decide: Решаем, какой подход использовать
- Act: Реализуем решение
- Review: Проверяем результаты

Автор: AI Assistant
Дата: 21 мая 2025
"""

import unittest
import sys
import os
import tempfile
import time
import gc
import random
import string
import threading
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any, Optional

# Добавляем путь к директории проекта для импорта модулей
sys.path.append(os.path.abspath('.'))

# Импортируем тестируемые модули
try:
    from advising_platform.src.cache.cache_manager import CacheManager
    from advising_platform.src.cache.memory_manager import MemoryManager
except ImportError:
    # Если модули не существуют, создадим заглушки для тестов
    class CacheManager:
        pass
    
    class MemoryManager:
        pass

# Индикатор необходимости создания новых модулей
NEED_TO_IMPLEMENT = not ('MemoryManager' in sys.modules)

class TestCacheMemoryManagement(unittest.TestCase):
    """Тесты для системы управления памятью в механизме кеширования."""
    
    def setUp(self):
        """Подготовка к тестам."""
        # Создаем временную директорию для тестовых файлов
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = os.path.join(self.temp_dir.name, 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Инициализируем менеджер памяти
        self.memory_manager = MemoryManager(max_memory_usage=100*1024*1024)  # 100 MB
        
        # Инициализируем менеджер кеша
        self.cache_manager = CacheManager(
            cache_dir=self.cache_dir,
            memory_manager=self.memory_manager
        )
    
    def tearDown(self):
        """Очистка после тестов."""
        # Очищаем временную директорию
        self.temp_dir.cleanup()
        
        # Принудительно запускаем сборщик мусора
        gc.collect()
    
    def _create_test_file(self, size_mb: int) -> str:
        """
        Создает тестовый файл указанного размера.
        
        Args:
            size_mb: Размер файла в мегабайтах
            
        Returns:
            str: Путь к созданному файлу
        """
        file_path = os.path.join(self.temp_dir.name, f'test_file_{size_mb}mb.dat')
        
        # Генерируем случайное содержимое файла
        chunk_size = 1024 * 1024  # 1 MB
        with open(file_path, 'wb') as f:
            for _ in range(size_mb):
                f.write(os.urandom(chunk_size))
        
        return file_path
    
    def test_memory_limit_enforcement(self):
        """
        Тест проверяет, что система соблюдает ограничение на использование памяти.
        Должна срабатывать очистка кеша при превышении лимита.
        """
        if NEED_TO_IMPLEMENT:
            self.skipTest("MemoryManager не реализован")
        
        # Устанавливаем максимальный размер кеша в 50 MB
        self.memory_manager.set_memory_limit(50 * 1024 * 1024)  # 50 MB
        
        # Кешируем файлы общим размером 80 MB (должно вызвать очистку)
        file_paths = []
        for size in [10, 15, 20, 35]:  # Суммарно 80 MB
            file_path = self._create_test_file(size)
            file_paths.append(file_path)
            self.cache_manager.cache_file(file_path)
        
        # Проверяем, что размер кеша не превышает 50 MB
        self.assertLessEqual(self.memory_manager.get_current_usage(), 50 * 1024 * 1024)
    
    def test_lru_eviction_policy(self):
        """
        Тест проверяет, что при очистке кеша используется политика LRU (Least Recently Used).
        """
        if NEED_TO_IMPLEMENT:
            self.skipTest("MemoryManager не реализован")
        
        # Устанавливаем максимальный размер кеша в 30 MB
        self.memory_manager.set_memory_limit(30 * 1024 * 1024)  # 30 MB
        
        # Кешируем три файла
        file_path_1 = self._create_test_file(10)  # 10 MB
        file_path_2 = self._create_test_file(10)  # 10 MB
        file_path_3 = self._create_test_file(10)  # 10 MB
        
        # Кешируем файлы в определенном порядке
        self.cache_manager.cache_file(file_path_1)  # Первый, самый старый
        self.cache_manager.cache_file(file_path_2)  # Второй
        self.cache_manager.cache_file(file_path_3)  # Третий, самый новый
        
        # Обращаемся к второму файлу, делая его самым недавно использованным
        self.cache_manager.get_cached_file(file_path_2)
        
        # Кешируем еще один файл, что должно вызвать вытеснение
        file_path_4 = self._create_test_file(10)  # 10 MB
        self.cache_manager.cache_file(file_path_4)
        
        # Проверяем, что первый файл (самый старый) был вытеснен из кеша
        self.assertFalse(self.cache_manager.is_cached(file_path_1))
        
        # Проверяем, что второй и третий файлы все еще в кеше
        self.assertTrue(self.cache_manager.is_cached(file_path_2))
        self.assertTrue(self.cache_manager.is_cached(file_path_3))
        self.assertTrue(self.cache_manager.is_cached(file_path_4))
    
    def test_ttl_expiration(self):
        """
        Тест проверяет, что записи кеша автоматически удаляются по истечении TTL.
        """
        if NEED_TO_IMPLEMENT:
            self.skipTest("MemoryManager не реализован")
        
        # Устанавливаем TTL (Time To Live) в 2 секунды
        self.memory_manager.set_default_ttl(2)  # 2 секунды
        
        # Кешируем файл
        file_path = self._create_test_file(5)  # 5 MB
        self.cache_manager.cache_file(file_path)
        
        # Проверяем, что файл в кеше
        self.assertTrue(self.cache_manager.is_cached(file_path))
        
        # Ждем истечения TTL
        time.sleep(3)
        
        # Запускаем проверку TTL
        self.memory_manager.cleanup_expired()
        
        # Проверяем, что файл был удален из кеша
        self.assertFalse(self.cache_manager.is_cached(file_path))
    
    def test_fragmented_storage_for_large_files(self):
        """
        Тест проверяет механизм фрагментированного хранения для больших файлов.
        """
        if NEED_TO_IMPLEMENT:
            self.skipTest("MemoryManager не реализован")
        
        # Устанавливаем максимальный размер фрагмента в 10 MB
        self.memory_manager.set_fragment_size(10 * 1024 * 1024)  # 10 MB
        
        # Создаем и кешируем большой файл (60 MB)
        file_path = self._create_test_file(60)  # 60 MB
        self.cache_manager.cache_file(file_path, fragmented=True)
        
        # Проверяем, что файл был разбит на фрагменты
        fragments = self.memory_manager.get_fragments(file_path)
        self.assertEqual(len(fragments), 6)  # 60 MB / 10 MB = 6 фрагментов
        
        # Получаем содержимое кешированного файла
        cached_content = self.cache_manager.get_cached_file(file_path)
        
        # Проверяем размер полученного содержимого
        self.assertEqual(len(cached_content), 60 * 1024 * 1024)
    
    def test_memory_monitoring_trigger(self):
        """
        Тест проверяет, что мониторинг использования памяти 
        автоматически запускает очистку при достижении порога.
        """
        if NEED_TO_IMPLEMENT:
            self.skipTest("MemoryManager не реализован")
        
        # Устанавливаем максимальный размер кеша в 40 MB и порог в 80%
        self.memory_manager.set_memory_limit(40 * 1024 * 1024)  # 40 MB
        self.memory_manager.set_cleanup_threshold(0.8)  # 80%
        
        # Кешируем файлы общим размером чуть больше порога
        file_paths = []
        for size in [10, 10, 13]:  # Суммарно 33 MB (82.5% от 40 MB)
            file_path = self._create_test_file(size)
            file_paths.append(file_path)
            self.cache_manager.cache_file(file_path)
        
        # Запускаем проверку использования памяти
        self.memory_manager.check_memory_usage()
        
        # Проверяем, что размер кеша уменьшился ниже порога
        self.assertLessEqual(
            self.memory_manager.get_current_usage(), 
            0.8 * 40 * 1024 * 1024  # 80% от 40 MB
        )


if __name__ == "__main__":
    unittest.main()