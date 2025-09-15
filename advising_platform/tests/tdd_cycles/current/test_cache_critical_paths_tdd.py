#!/usr/bin/env python3
"""
🧪 TDD Tests для критических путей кеш-системы (T026)

JTBD: Как система кеширования, я хочу проверить все критические пути взаимодействия,
чтобы обеспечить надежность cascade обновлений и dependency chain'ов.

Основано на: dependency_mapping.md анализе
Стандарт: TDD-doc с полной Testing Pyramid
Автор: AI Assistant
Дата: 25 May 2025
"""

import os
import sys
import time
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем корневую папку проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from advising_platform.src.cache.real_inmemory_cache import RealInMemoryCache
    from advising_platform.src.core.task_completion_trigger import TaskCompletionTrigger
    from advising_platform.safe_file_operations import SafeFileOperations
except ImportError as e:
    print(f"Import error: {e}")
    # Создаем mock классы для тестирования структуры
    class RealInMemoryCache:
        def __init__(self):
            self.cache = {}
        
        def load_document(self, path): 
            return True
        
        def get_document(self, path): 
            return {'content': 'test', 'type': 'standard'}
        
        def update_document(self, path, content): 
            return True
        
        def create_document(self, path, content): 
            return True
        
        def search_documents(self, query): 
            return [{'path': 'test', 'content': 'test'}]
        
        def get_statistics(self): 
            return {'total_documents': 1}
    
    class TaskCompletionTrigger:
        def __init__(self): 
            pass
    
    class SafeFileOperations:
        @staticmethod
        def write_file(path, content):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        @staticmethod
        def read_file(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return True, f.read()
            except:
                return False, None


class CacheCriticalPathsIntegrationTDD(unittest.TestCase):
    """
    🚨 Critical Paths Integration Tests
    
    JTBD: Как integration тест, я хочу проверить все критические пути из dependency mapping,
    чтобы убедиться в отсутствии "Green Tests, Broken System" anti-pattern.
    """
    
    def setUp(self):
        """Инициализация для каждого теста"""
        self.test_dir = tempfile.mkdtemp()
        self.cache = RealInMemoryCache()
        self.trigger = TaskCompletionTrigger()
        
    def tearDown(self):
        """Очистка после каждого теста"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_todo_modification_cascade_integration(self):
        """
        🧪 Critical Path 1: todo.md → task_completion_trigger → archive → RealInMemoryCache → веб-интерфейс
        
        JTBD: Как пользователь, я хочу чтобы изменения в todo.md автоматически обновлялись 
        во всей системе, чтобы все компоненты видели актуальную информацию.
        """
        # Red Phase: тест должен провалиться, пока не реализована полная cascade
        todo_content = """# ToDo Test
        
## T001 - Test Task ⭐⭐⭐
**Статус**: ✅ Выполнено
**JTBD**: Test task for cascade integration
"""
        
        # Создаем тестовый todo.md
        todo_path = os.path.join(self.test_dir, "todo.md")
        SafeFileOperations.write_file(todo_path, todo_content)
        
        # Загружаем в кеш
        self.cache.load_document(todo_path)
        
        # Изменяем через кеш
        updated_content = todo_content.replace("✅ Выполнено", "🟢 В работе")
        result = self.cache.update_document(todo_path, updated_content)
        
        # Assert: изменения должны синхронизироваться с диском
        self.assertTrue(result, "Cache update должен быть успешным")
        
        # Проверяем файл на диске
        disk_content = SafeFileOperations.read_file(todo_path)[1]
        self.assertIn("🟢 В работе", disk_content, "Изменения должны быть записаны на диск")
        
        # Проверяем кеш
        cached_doc = self.cache.get_document(todo_path)
        self.assertIsNotNone(cached_doc, "Документ должен быть в кеше")
        self.assertIn("🟢 В работе", cached_doc['content'], "Кеш должен содержать обновленный контент")
    
    def test_cache_api_changes_propagation(self):
        """
        🧪 Critical Path 2: RealInMemoryCache API → все триггеры → все тесты → cache_init
        
        JTBD: Как система, я хочу чтобы изменения API кеша не ломали зависимые компоненты,
        чтобы обеспечить backward compatibility.
        """
        # Проверяем наличие критических методов API
        required_methods = [
            'load_document', 'get_document', 'update_document', 
            'create_document', 'get_statistics', 'search_documents'
        ]
        
        for method_name in required_methods:
            self.assertTrue(
                hasattr(self.cache, method_name),
                f"RealInMemoryCache должен иметь метод {method_name}"
            )
            method = getattr(self.cache, method_name)
            self.assertTrue(
                callable(method),
                f"Метод {method_name} должен быть вызываемым"
            )
    
    def test_standards_to_cache_flow_integration(self):
        """
        🧪 Critical Path 3: [standards .md] → кеш → триггеры → документация
        
        JTBD: Как система стандартов, я хочу чтобы изменения стандартов автоматически 
        обновлялись в кеше и влияли на работу триггеров.
        """
        # Создаем тестовый стандарт
        standard_content = """# 🧪 Test Standard

type: standard
version: 1.0
status: Active

## 🎯 Цель документа
Test standard для integration testing.

## JTBD
**Когда** система загружает стандарт,
**Роль** test runner,
**Хочет** проверить корректность загрузки,
**Закрывает потребность** в валидации workflow.
"""
        
        standard_path = os.path.join(self.test_dir, "test_standard.md")
        SafeFileOperations.write_file(standard_path, standard_content)
        
        # Загружаем в кеш
        result = self.cache.load_document(standard_path)
        self.assertTrue(result, "Стандарт должен загружаться в кеш")
        
        # Проверяем детекцию типа документа
        doc = self.cache.get_document(standard_path)
        self.assertIsNotNone(doc, "Документ должен быть в кеше")
        self.assertEqual(doc['type'], 'standard', "Тип документа должен определяться как 'standard'")
        
        # Проверяем поиск по содержимому
        search_results = self.cache.search_documents('integration testing')
        self.assertTrue(len(search_results) > 0, "Поиск должен находить документы по содержимому")


class CacheConcurrencyStressTDD(unittest.TestCase):
    """
    🧪 Stress Tests для concurrent operations
    
    JTBD: Как система под нагрузкой, я хочу обеспечить data integrity при concurrent access,
    чтобы избежать race conditions и data corruption.
    """
    
    def setUp(self):
        """Инициализация для stress тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.cache = RealInMemoryCache()
        self.errors = []
    
    def tearDown(self):
        """Очистка после stress тестов"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_concurrent_cache_operations_stress(self):
        """
        🧪 Stress Test: Concurrent cache operations под нагрузкой
        
        JTBD: Как система, я хочу корректно обрабатывать множественные concurrent операции,
        чтобы обеспечить data consistency и избежать race conditions.
        """
        # Создаем тестовый документ
        test_content = "# Test Document\nInitial content for stress testing."
        test_path = os.path.join(self.test_dir, "stress_test.md")
        SafeFileOperations.write_file(test_path, test_content)
        self.cache.load_document(test_path)
        
        def concurrent_update(thread_id):
            """Функция для concurrent обновлений"""
            try:
                for i in range(10):
                    updated_content = f"# Test Document\nUpdated by thread {thread_id}, iteration {i}"
                    result = self.cache.update_document(test_path, updated_content)
                    if not result:
                        self.errors.append(f"Thread {thread_id}: Update failed at iteration {i}")
                    time.sleep(0.01)  # Небольшая пауза для имитации real-world условий
            except Exception as e:
                self.errors.append(f"Thread {thread_id}: Exception {str(e)}")
        
        # Запускаем 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_update, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех threads
        for thread in threads:
            thread.join()
        
        # Assert: не должно быть ошибок
        if self.errors:
            self.fail(f"Concurrent operations failed with errors: {self.errors}")
        
        # Проверяем final consistency
        final_doc = self.cache.get_document(test_path)
        self.assertIsNotNone(final_doc, "Документ должен быть доступен после concurrent updates")
        
        # Проверяем синхронизацию с диском
        disk_content = SafeFileOperations.read_file(test_path)[1]
        self.assertEqual(
            final_doc['content'], 
            disk_content, 
            "Содержимое кеша должно соответствовать содержимому на диске"
        )
    
    def test_error_propagation_through_dependency_chain(self):
        """
        🧪 Error Propagation Test: Проверка распространения ошибок через dependency chain
        
        JTBD: Как система, я хочу корректно обрабатывать и передавать ошибки через всю цепочку зависимостей,
        чтобы обеспечить proper error handling и recovery.
        """
        # Тестируем ошибку при недоступности файла
        non_existent_path = os.path.join(self.test_dir, "non_existent.md")
        
        # Попытка загрузить несуществующий файл
        result = self.cache.load_document(non_existent_path)
        self.assertFalse(result, "Загрузка несуществующего файла должна возвращать False")
        
        # Попытка получить несуществующий документ из кеша
        doc = self.cache.get_document(non_existent_path)
        self.assertIsNone(doc, "Несуществующий документ должен возвращать None")
        
        # Попытка обновить несуществующий документ
        result = self.cache.update_document(non_existent_path, "test content")
        self.assertFalse(result, "Обновление несуществующего документа должно возвращать False")


class CacheEndToEndWorkflowTDD(unittest.TestCase):
    """
    🧪 End-to-End Tests полного user workflow
    
    JTBD: Как end-to-end тест, я хочу проверить полный пользовательский workflow,
    чтобы убедиться что "тесты проходят = пользователь видит результат".
    """
    
    def setUp(self):
        """Инициализация для E2E тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.cache = RealInMemoryCache()
    
    def tearDown(self):
        """Очистка после E2E тестов"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_full_user_workflow_integration(self):
        """
        🧪 E2E Test: Полный user workflow от request до response
        
        JTBD: Как пользователь, я хочу чтобы мои действия с документами работали end-to-end,
        чтобы система была надежной и предсказуемой.
        """
        # 1. User создает новый документ
        new_doc_path = os.path.join(self.test_dir, "user_document.md")
        new_content = """# User Document

## Содержимое
Это документ, созданный пользователем для E2E тестирования.

### JTBD
**Когда** пользователь создает документ,
**Роль** content creator,
**Хочет** чтобы документ сохранился и был доступен,
**Закрывает потребность** в reliable document management.
"""
        
        # 2. Система создает документ через кеш
        result = self.cache.create_document(new_doc_path, new_content)
        self.assertTrue(result, "Создание документа через кеш должно быть успешным")
        
        # 3. User ищет документ
        search_results = self.cache.search_documents("E2E тестирования")
        self.assertTrue(len(search_results) > 0, "Поиск должен находить созданный документ")
        
        # 4. User редактирует документ
        updated_content = new_content.replace("E2E тестирования", "интеграционного тестирования")
        result = self.cache.update_document(new_doc_path, updated_content)
        self.assertTrue(result, "Обновление документа должно быть успешным")
        
        # 5. System verifies changes
        doc = self.cache.get_document(new_doc_path)
        self.assertIsNotNone(doc, "Обновленный документ должен быть доступен")
        self.assertIn("интеграционного тестирования", doc['content'], "Изменения должны быть сохранены")
        
        # 6. Verify disk synchronization
        disk_content = SafeFileOperations.read_file(new_doc_path)[1]
        self.assertEqual(
            doc['content'], 
            disk_content, 
            "Кеш и диск должны быть синхронизированы"
        )
        
        # 7. User gets statistics
        stats = self.cache.get_statistics()
        self.assertIsInstance(stats, dict, "Статистика должна возвращаться как словарь")
        self.assertIn('total_documents', stats, "Статистика должна содержать общее количество документов")
        self.assertTrue(stats['total_documents'] > 0, "Должен быть хотя бы один документ в статистике")


if __name__ == '__main__':
    # Запуск всех тестов с подробным выводом
    unittest.main(verbosity=2)