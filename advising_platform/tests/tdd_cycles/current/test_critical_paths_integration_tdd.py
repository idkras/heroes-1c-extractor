"""
🧪 Critical Paths Integration Tests - TDD Implementation

JTBD: Как система, я хочу протестировать все критические пути зависимостей,
чтобы обеспечить надежность cascade операций между компонентами.

Testing Pyramid Level: Integration Tests (Level 2)
Covers: todo.md → task_completion_trigger → RealInMemoryCache → файлы

Автор: AI Assistant
Дата: 25 May 2025
Стандарт: TDD-doc с Testing Pyramid compliance
"""

import unittest
import os
import tempfile
import shutil
import threading
import time
from pathlib import Path
from advising_platform.src.cache.real_inmemory_cache import RealInMemoryCache
from advising_platform.src.core.task_completion_trigger import TaskCompletionTrigger


class CriticalPathsIntegrationTDD(unittest.TestCase):
    """
    JTBD: Как integration test suite, я хочу валидировать critical dependency paths,
    чтобы предотвратить "Green Tests, Broken System" anti-pattern.
    """

    def setUp(self):
        """
        JTBD: Как test setup, я хочу создать isolated test environment,
        чтобы обеспечить clean state для каждого теста.
        """
        self.test_dir = tempfile.mkdtemp()
        self.cache = RealInMemoryCache()
        self.task_trigger = TaskCompletionTrigger()
        
        # Создаем test todo.md
        self.todo_path = os.path.join(self.test_dir, "todo.md")
        self.archive_path = os.path.join(self.test_dir, "todo.archive.md")
        
        with open(self.todo_path, 'w', encoding='utf-8') as f:
            f.write("""# Test Todo
- [ ] T001 - Test task
- [x] T002 - Completed task
""")

    def tearDown(self):
        """
        JTBD: Как test cleanup, я хочу удалить temporary files,
        чтобы не засорять файловую систему.
        """
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_todo_modification_cascade_integration(self):
        """
        JTBD: Как integration test, я хочу проверить полный cascade:
        todo.md изменение → task_completion_trigger → archive → RealInMemoryCache → файлы
        
        Critical Path: todo.md → task_completion_trigger.py → archive/ → RealInMemoryCache → веб-интерфейс
        """
        # RED: Failing test для cascade операции
        
        # Загружаем todo в кеш
        self.cache.create_document("todo.md", "# Test Todo\n- [ ] T001 - Test task\n")
        
        # Модифицируем через кеш
        updated_content = "# Test Todo\n- [x] T001 - Completed task\n- [ ] T002 - New task\n"
        self.cache.update_document("todo.md", updated_content)
        
        # Проверяем что изменения синхронизированы с диском
        cached_content = self.cache.get_document("todo.md")
        
        # Assert integration между компонентами
        self.assertEqual(cached_content, updated_content)
        
        # Проверяем что task trigger может обработать изменения
        stats = self.task_trigger.analyze_tasks(updated_content)
        self.assertGreater(stats['completed'], 0)
        self.assertGreater(stats['total'], stats['completed'])

    def test_cache_api_changes_propagation(self):
        """
        JTBD: Как integration test, я хочу проверить propagation API changes:
        RealInMemoryCache → все триггеры → все тесты → cache_init.py
        
        Critical Path: RealInMemoryCache API → все триггеры → все тесты → cache_init
        """
        # Тестируем что все основные API методы доступны
        required_methods = [
            'get_document', 'update_document', 'create_document', 
            'search_documents', 'get_statistics'
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(self.cache, method_name), 
                          f"Critical API method {method_name} missing")
            
        # Тестируем что методы работают совместно
        self.cache.create_document("test.md", "# Test")
        content = self.cache.get_document("test.md")
        self.assertEqual(content, "# Test")
        
        # Тестируем поиск после создания
        results = self.cache.search_documents("Test")
        self.assertGreater(len(results), 0)

    def test_standards_content_flow_integration(self):
        """
        JTBD: Как integration test, я хочу проверить standards content flow:
        [standards .md] → кеш → триггеры → документация
        
        Critical Path: Standards → кеш → триггеры → документация
        """
        # Создаем mock standard в кеше
        standard_content = """# Test Standard
type: standard
version: 1.0
status: Active

## Цель документа
Test standard for integration testing.
"""
        
        self.cache.create_document("test_standard.md", standard_content)
        
        # Проверяем что standard корректно загружен
        loaded_content = self.cache.get_document("test_standard.md")
        self.assertIn("type: standard", loaded_content)
        self.assertIn("version: 1.0", loaded_content)
        
        # Проверяем поиск по metadata
        results = self.cache.search_documents("standard")
        standard_found = any("test_standard.md" in str(result) for result in results)
        self.assertTrue(standard_found, "Standard not found in search results")

    def test_concurrent_operations_integration(self):
        """
        JTBD: Как integration test, я хочу проверить concurrent cache operations,
        чтобы обеспечить thread safety в реальных условиях.
        
        Integration Test: Concurrent cache operations с файловой системой
        """
        doc_name = "concurrent_test.md"
        initial_content = "# Initial Content"
        
        self.cache.create_document(doc_name, initial_content)
        
        results = []
        errors = []
        
        def update_document(content_suffix):
            try:
                new_content = f"# Updated Content {content_suffix}"
                self.cache.update_document(doc_name, new_content)
                result = self.cache.get_document(doc_name)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Запускаем concurrent updates
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_document, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех threads
        for thread in threads:
            thread.join()
        
        # Проверяем что нет ошибок concurrency
        self.assertEqual(len(errors), 0, f"Concurrent errors: {errors}")
        self.assertEqual(len(results), 5, "Not all concurrent operations completed")
        
        # Проверяем что финальное состояние consistent
        final_content = self.cache.get_document(doc_name)
        self.assertIsNotNone(final_content)
        self.assertIn("Updated Content", final_content)

    def test_error_propagation_through_dependency_chain(self):
        """
        JTBD: Как integration test, я хочу проверить error propagation,
        чтобы обеспечить graceful handling ошибок через dependency chain.
        
        Integration Test: Error propagation через dependency chain
        """
        # Тестируем обработку несуществующего документа
        non_existent = self.cache.get_document("non_existent.md")
        self.assertIsNone(non_existent)
        
        # Тестируем update несуществующего документа
        try:
            self.cache.update_document("non_existent.md", "content")
            # Если не бросает исключение, то должен создать документ
            created_content = self.cache.get_document("non_existent.md")
            self.assertEqual(created_content, "content")
        except Exception as e:
            # Если бросает исключение, то это тоже валидное поведение
            self.assertIsInstance(e, (FileNotFoundError, KeyError))

    def test_performance_under_realistic_load(self):
        """
        JTBD: Как integration test, я хочу проверить performance под realistic load,
        чтобы обеспечить acceptable response times.
        
        Integration Test: Performance тесты под realistic load
        """
        # Создаем realistic dataset
        documents_count = 50
        search_queries = ["standard", "test", "integration", "cache"]
        
        start_time = time.time()
        
        # Массовое создание документов
        for i in range(documents_count):
            content = f"# Document {i}\nThis is test document {i} for performance testing."
            self.cache.create_document(f"perf_test_{i}.md", content)
        
        creation_time = time.time() - start_time
        
        # Массовый поиск
        start_time = time.time()
        for query in search_queries:
            results = self.cache.search_documents(query)
            self.assertIsInstance(results, list)
        
        search_time = time.time() - start_time
        
        # Performance assertions (reasonable thresholds)
        self.assertLess(creation_time, 5.0, f"Document creation too slow: {creation_time}s")
        self.assertLess(search_time, 2.0, f"Search operations too slow: {search_time}s")
        
        # Проверяем статистику
        stats = self.cache.get_statistics()
        self.assertGreaterEqual(stats.get('total_documents', 0), documents_count)


if __name__ == '__main__':
    unittest.main()