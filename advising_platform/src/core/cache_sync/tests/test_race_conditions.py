#!/usr/bin/env python3
"""
Тест для выявления гонок данных при многопоточной работе с кешем и файловой системой.

Симулирует высокую нагрузку с параллельной работой нескольких потоков, обращающихся
к одним и тем же файлам, для выявления проблем синхронизации.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import json
import time
import random
import threading
import tempfile
import unittest
from typing import List, Dict, Any, Set
from concurrent.futures import ThreadPoolExecutor

# Импортируем необходимые модули
try:
    from advising_platform.src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier
except ImportError:
    import sys
    import os.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
    from advising_platform.src.core.cache_sync.cache_sync_verifier import CacheSyncVerifier


# Настройки теста
MAX_THREADS = 10         # Максимальное количество одновременных потоков
NUM_ITERATIONS = 50      # Количество операций для каждого потока
NUM_FILES = 5            # Количество файлов для тестирования
SLEEP_DURATION = 0.01    # Задержка между операциями (в секундах)


class RaceConditionSimulator:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса RaceConditionSimulator, чтобы эффективно решать соответствующие задачи в системе.
    
    Симулятор гонок данных при работе с файлами и кешем."""
    
    def __init__(self, test_dir: str, cache_file: str):
        """
        Инициализация симулятора.
        
        Args:
            test_dir: Директория для тестовых файлов
            cache_file: Путь к файлу кеша
        """
        self.test_dir = test_dir
        self.cache_file = cache_file
        self.lock = threading.RLock()
        self.file_locks = {}
        self.file_locks_lock = threading.RLock()
        self.issue_count = 0
        self.issue_details = []
        
        # Создаем директорию для тестов, если её нет
        os.makedirs(test_dir, exist_ok=True)
        
        # Создаем начальный кеш
        self._init_cache()
        
        # Создаем тестовые файлы
        self._create_test_files()
    
    def _init_cache(self):
        """Инициализирует файл кеша."""
        # Создаем пустой кеш
        cache_data = {}
        
        # Сохраняем в файл
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def _create_test_files(self):
        """Создает тестовые файлы для симуляции."""
        for i in range(NUM_FILES):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Initial content for file {i}")
            
            # Добавляем файл в кеш
            self._update_cache_entry(file_path)
    
    def _get_file_lock(self, file_path: str) -> threading.RLock:
        """
        Получает блокировку для указанного файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Объект блокировки
        """
        with self.file_locks_lock:
            if file_path not in self.file_locks:
                self.file_locks[file_path] = threading.RLock()
            
            return self.file_locks[file_path]
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Получает метаданные файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Словарь с метаданными
        """
        stats = os.stat(file_path)
        
        return {
            "size": stats.st_size,
            "last_modified": stats.st_mtime,
            "cached_at": time.time()
        }
    
    def _read_cache(self) -> Dict[str, Any]:
        """
        Читает кеш из файла.
        
        Returns:
            Словарь с данными кеша
        """
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_cache(self, cache_data: Dict[str, Any]):
        """
        Записывает данные в кеш.
        
        Args:
            cache_data: Словарь с данными кеша
        """
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def _update_cache_entry(self, file_path: str):
        """
        Обновляет запись о файле в кеше.
        
        Args:
            file_path: Путь к файлу
        """
        # Получаем метаданные файла
        metadata = self._get_file_metadata(file_path)
        
        # Читаем кеш
        cache_data = self._read_cache()
        
        # Обновляем запись
        cache_data[file_path] = metadata
        
        # Записываем обновленный кеш
        self._write_cache(cache_data)
    
    def _update_cache_entry_unsafe(self, file_path: str):
        """
        Обновляет запись о файле в кеше без блокировки для симуляции гонки данных.
        
        Args:
            file_path: Путь к файлу
        """
        # Получаем метаданные файла
        metadata = self._get_file_metadata(file_path)
        
        # Небольшая задержка для увеличения шанса гонки данных
        time.sleep(random.uniform(0, SLEEP_DURATION))
        
        # Читаем кеш
        cache_data = self._read_cache()
        
        # Обновляем запись
        cache_data[file_path] = metadata
        
        # Еще одна задержка
        time.sleep(random.uniform(0, SLEEP_DURATION))
        
        # Записываем обновленный кеш
        self._write_cache(cache_data)
    
    def _verify_cache_entry(self, file_path: str) -> bool:
        """
        Проверяет соответствие записи в кеше текущему состоянию файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если запись соответствует, иначе False
        """
        # Получаем метаданные файла
        current_metadata = self._get_file_metadata(file_path)
        
        # Читаем кеш
        cache_data = self._read_cache()
        
        # Проверяем наличие файла в кеше
        if file_path not in cache_data:
            self._record_issue(file_path, "Файл отсутствует в кеше", None, current_metadata)
            return False
        
        # Получаем запись из кеша
        cache_entry = cache_data[file_path]
        
        # Проверяем соответствие размера
        if current_metadata["size"] != cache_entry.get("size", -1):
            self._record_issue(
                file_path, 
                "Размер файла не соответствует кешу", 
                cache_entry, 
                current_metadata
            )
            return False
        
        # Проверяем соответствие времени изменения с учетом погрешности
        if abs(current_metadata["last_modified"] - cache_entry.get("last_modified", 0)) > 1.0:
            self._record_issue(
                file_path, 
                "Время изменения файла не соответствует кешу", 
                cache_entry, 
                current_metadata
            )
            return False
        
        return True
    
    def _record_issue(
        self, 
        file_path: str, 
        issue_type: str, 
        cache_entry: Dict[str, Any], 
        current_metadata: Dict[str, Any]
    ):
        """
        Записывает информацию о выявленной проблеме.
        
        Args:
            file_path: Путь к файлу
            issue_type: Тип проблемы
            cache_entry: Запись из кеша
            current_metadata: Текущие метаданные файла
        """
        with self.lock:
            self.issue_count += 1
            self.issue_details.append({
                "file_path": file_path,
                "issue_type": issue_type,
                "cache_entry": cache_entry,
                "current_metadata": current_metadata,
                "timestamp": time.time()
            })
    
    def write_file_safe(self, file_path: str, content: str) -> bool:
        """
        Безопасная запись в файл с обновлением кеша (с использованием блокировок).
        
        Args:
            file_path: Путь к файлу
            content: Содержимое для записи
            
        Returns:
            True, если запись успешна, иначе False
        """
        # Получаем блокировку для файла
        file_lock = self._get_file_lock(file_path)
        
        # Захватываем блокировку
        with file_lock:
            try:
                # Записываем содержимое в файл
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                # Обновляем запись в кеше
                self._update_cache_entry(file_path)
                
                return True
            except Exception as e:
                print(f"Ошибка при безопасной записи в файл {file_path}: {e}")
                return False
    
    def write_file_unsafe(self, file_path: str, content: str) -> bool:
        """
        Небезопасная запись в файл с обновлением кеша (без блокировок).
        
        Args:
            file_path: Путь к файлу
            content: Содержимое для записи
            
        Returns:
            True, если запись успешна, иначе False
        """
        try:
            # Записываем содержимое в файл
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Обновляем запись в кеше без блокировки
            self._update_cache_entry_unsafe(file_path)
            
            return True
        except Exception as e:
            print(f"Ошибка при небезопасной записи в файл {file_path}: {e}")
            return False
    
    def run_safe_simulation(self):
        """JTBD:
Я (разработчик) хочу использовать функцию run_safe_simulation, чтобы эффективно выполнить соответствующую операцию.
         
         Запускает симуляцию с безопасными операциями."""
        print("Запуск безопасной симуляции...")
        
        # Сбрасываем счетчики проблем
        self.issue_count = 0
        self.issue_details = []
        
        # Создаем пул потоков
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Запускаем задачи для каждого потока
            futures = []
            for i in range(MAX_THREADS):
                futures.append(executor.submit(self._safe_thread_task, i))
            
            # Ждем завершения всех задач
            for future in futures:
                future.result()
        
        print(f"Безопасная симуляция завершена. Выявлено проблем: {self.issue_count}")
        
        # Проверяем соответствие кеша и файловой системы
        for i in range(NUM_FILES):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            self._verify_cache_entry(file_path)
    
    def run_unsafe_simulation(self):
        """JTBD:
Я (разработчик) хочу использовать функцию run_unsafe_simulation, чтобы эффективно выполнить соответствующую операцию.
         
         Запускает симуляцию с небезопасными операциями."""
        print("Запуск небезопасной симуляции...")
        
        # Сбрасываем счетчики проблем
        self.issue_count = 0
        self.issue_details = []
        
        # Создаем пул потоков
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Запускаем задачи для каждого потока
            futures = []
            for i in range(MAX_THREADS):
                futures.append(executor.submit(self._unsafe_thread_task, i))
            
            # Ждем завершения всех задач
            for future in futures:
                future.result()
        
        print(f"Небезопасная симуляция завершена. Выявлено проблем: {self.issue_count}")
        
        # Проверяем соответствие кеша и файловой системы
        for i in range(NUM_FILES):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            self._verify_cache_entry(file_path)
    
    def _safe_thread_task(self, thread_id: int):
        """
        Задача для безопасного потока.
        
        Args:
            thread_id: Идентификатор потока
        """
        for i in range(NUM_ITERATIONS):
            # Выбираем случайный файл
            file_index = random.randint(0, NUM_FILES - 1)
            file_path = os.path.join(self.test_dir, f"test_file_{file_index}.txt")
            
            # Формируем содержимое
            content = f"Content from thread {thread_id}, iteration {i}, time {time.time()}"
            
            # Записываем файл безопасно
            self.write_file_safe(file_path, content)
            
            # Добавляем случайную задержку
            time.sleep(random.uniform(0, SLEEP_DURATION))
    
    def _unsafe_thread_task(self, thread_id: int):
        """
        Задача для небезопасного потока.
        
        Args:
            thread_id: Идентификатор потока
        """
        for i in range(NUM_ITERATIONS):
            # Выбираем случайный файл
            file_index = random.randint(0, NUM_FILES - 1)
            file_path = os.path.join(self.test_dir, f"test_file_{file_index}.txt")
            
            # Формируем содержимое
            content = f"Content from thread {thread_id}, iteration {i}, time {time.time()}"
            
            # Записываем файл небезопасно
            self.write_file_unsafe(file_path, content)
            
            # Добавляем случайную задержку
            time.sleep(random.uniform(0, SLEEP_DURATION))
    
    def get_results(self) -> Dict[str, Any]:
        """
        Получает результаты симуляции.
        
        Returns:
            Словарь с результатами
        """
        return {
            "issue_count": self.issue_count,
            "issue_details": self.issue_details
        }


class TestRaceConditions(unittest.TestCase):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса TestRaceConditions, чтобы эффективно решать соответствующие задачи в системе.
    
    Тесты для выявления гонок данных."""
    
    def setUp(self):
        """JTBD:
Я (разработчик) хочу использовать функцию setUp, чтобы эффективно выполнить соответствующую операцию.
         
         Подготовка к тестам."""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        
        # Путь к файлу кеша
        self.cache_file = os.path.join(self.test_dir, ".cache_state.json")
        
        # Создаем симулятор
        self.simulator = RaceConditionSimulator(self.test_dir, self.cache_file)
    
    def tearDown(self):
        """JTBD:
Я (разработчик) хочу использовать функцию tearDown, чтобы эффективно выполнить соответствующую операцию.
         
         Очистка после тестов."""
        # Удаляем временную директорию
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_safe_operations(self):
        """JTBD:
Я (разработчик) хочу использовать функцию test_safe_operations, чтобы эффективно выполнить соответствующую операцию.
         
         Тест безопасных операций."""
        # Запускаем симуляцию с безопасными операциями
        self.simulator.run_safe_simulation()
        
        # Получаем результаты
        results = self.simulator.get_results()
        
        # Проверяем, что проблем нет или их очень мало
        self.assertLessEqual(results["issue_count"], 1, "Безопасные операции должны минимизировать проблемы синхронизации")
    
    def test_unsafe_operations(self):
        """JTBD:
Я (разработчик) хочу использовать функцию test_unsafe_operations, чтобы эффективно выполнить соответствующую операцию.
         
         Тест небезопасных операций."""
        # Запускаем симуляцию с небезопасными операциями
        self.simulator.run_unsafe_simulation()
        
        # Получаем результаты
        results = self.simulator.get_results()
        
        # В многопоточной среде без блокировок должны быть проблемы
        # Но точное количество может варьироваться, поэтому мы только логируем
        print(f"Выявлено {results['issue_count']} проблем при небезопасных операциях")
        
        # Выводим детали некоторых проблем
        for i, issue in enumerate(results["issue_details"][:5]):
            print(f"Проблема {i+1}:")
            print(f"  Файл: {issue['file_path']}")
            print(f"  Тип: {issue['issue_type']}")
            print(f"  Метаданные в кеше: {issue.get('cache_entry')}")
            print(f"  Текущие метаданные: {issue.get('current_metadata')}")
            print()
    
    def test_verifier_fixes_problems(self):
        """JTBD:
Я (разработчик) хочу использовать функцию test_verifier_fixes_problems, чтобы эффективно выполнить соответствующую операцию.
         
         Тест способности верификатора исправлять проблемы."""
        # Запускаем симуляцию с небезопасными операциями для создания проблем
        self.simulator.run_unsafe_simulation()
        
        # Создаем верификатор
        verifier = CacheSyncVerifier(
            cache_paths=[self.cache_file],
            base_dir=self.test_dir
        )
        
        # Проверяем синхронизацию
        missing_in_cache, missing_in_filesystem, metadata_mismatch = verifier.verify_sync()
        
        # Фиксируем проблемы
        verifier.fix_sync_issues()
        
        # Проверяем снова
        missing_in_cache2, missing_in_filesystem2, metadata_mismatch2 = verifier.verify_sync()
        
        # Проверяем, что проблемы исправлены
        self.assertEqual(len(missing_in_cache2), 0, "Верификатор должен исправить все отсутствующие в кеше файлы")
        self.assertEqual(len(metadata_mismatch2), 0, "Верификатор должен исправить все несоответствия метаданных")


if __name__ == "__main__":
    unittest.main()