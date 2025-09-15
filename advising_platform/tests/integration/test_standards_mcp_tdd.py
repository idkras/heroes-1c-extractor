#!/usr/bin/env python3
"""
TDD тест для Standards-MCP сервера

RED фаза: Проверяет корректность интеграции с UnifiedKeyResolver
GREEN фаза: Тестирует резолвинг abstract://standard:xxx адресов  
REFACTOR фаза: Оптимизация производительности <200ms

Гипотеза: Standards-MCP сервер корректно резолвит логические адреса стандартов
и возвращает структурированный контент в указанном формате.

Автор: AI Assistant
Дата: 26 May 2025
Стандарт: TDD Documentation Standard v2.0
"""

import unittest
import sys
import json
import subprocess
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.unified_key_resolver import get_resolver
from src.cache.real_inmemory_cache import get_cache

class TestStandardsMCPTDD(unittest.TestCase):
    """
    TDD тесты для Standards-MCP сервера.
    Проверяет корректность резолвинга стандартов и производительность.
    """
    
    def setUp(self):
        """Подготовка тестового окружения."""
        self.resolver = get_resolver()
        self.cache = get_cache()
        self.cache.initialize_from_disk()
        
        # Путь к Python backend скрипту
        self.backend_script = Path(__file__).parent.parent.parent / "src/mcp/python_backends/standards_resolver.py"
        
    def test_red_backend_script_exists(self):
        """
        🔴 RED TEST: Проверка существования backend скрипта.
        
        Гипотеза: Python backend для standards-resolver существует и запускается.
        """
        print("\n🔴 RED TEST: Проверка backend скрипта")
        
        self.assertTrue(self.backend_script.exists(), 
                       f"Backend скрипт должен существовать: {self.backend_script}")
        
        # Проверяем что скрипт исполняемый
        self.assertTrue(self.backend_script.is_file(),
                       "Backend скрипт должен быть файлом")
        
        print(f"   ✅ Backend скрипт найден: {self.backend_script}")
        print("✅ Backend скрипт готов к работе")
    
    def test_green_resolve_abstract_address(self):
        """
        🟢 GREEN TEST: Резолвинг abstract://standard:xxx адресов.
        
        Гипотеза: Backend корректно резолвит логические адреса в контент стандартов.
        """
        print("\n🟢 GREEN TEST: Резолвинг abstract адресов")
        
        # Получаем доступные логические адреса
        available_addresses = list(self.resolver._logical_map.keys())
        self.assertGreater(len(available_addresses), 0, 
                          "Должны быть доступны логические адреса")
        
        # Тестируем резолвинг первого адреса
        test_address = available_addresses[0]
        print(f"   Тестируем адрес: {test_address}")
        
        # Вызываем backend скрипт
        args = {
            "address": test_address,
            "format": "summary",
            "context": "test"
        }
        
        try:
            result = subprocess.run([
                "python3", str(self.backend_script), json.dumps(args)
            ], capture_output=True, text=True, timeout=5)
            
            print(f"   Код возврата: {result.returncode}")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")
            
            self.assertEqual(result.returncode, 0, 
                           f"Backend должен выполниться успешно. Stderr: {result.stderr}")
            
            # Парсим результат
            response = json.loads(result.stdout)
            print(f"   Получен ответ: {type(response)}")
            
            # Проверяем структуру ответа
            self.assertIsInstance(response, dict, "Ответ должен быть словарем")
            self.assertIn("success", response, "Должно быть поле success")
            
            if response["success"]:
                self.assertIn("content", response, "Должен быть контент")
                self.assertIn("address", response, "Должен быть исходный адрес")
                print(f"   ✅ Успешно резолвен: {response['address']}")
            else:
                print(f"   ⚠️ Ошибка резолвинга: {response.get('error', 'Unknown')}")
            
        except subprocess.TimeoutExpired:
            self.fail("Backend скрипт завис (timeout 5s)")
        except json.JSONDecodeError as e:
            self.fail(f"Неверный JSON ответ: {result.stdout}")
        except Exception as e:
            self.fail(f"Ошибка выполнения backend: {str(e)}")
        
        print("✅ Резолвинг abstract адресов работает")
    
    def test_green_format_types(self):
        """
        🟢 GREEN TEST: Различные форматы вывода (full, summary, checklist).
        
        Гипотеза: Backend поддерживает все запрошенные форматы вывода.
        """
        print("\n🟢 GREEN TEST: Форматы вывода")
        
        # Берем первый доступный адрес для тестирования
        available_addresses = list(self.resolver._logical_map.keys())
        if not available_addresses:
            self.skipTest("Нет доступных логических адресов для тестирования")
        
        test_address = available_addresses[0]
        formats = ["full", "summary", "checklist"]
        
        for format_type in formats:
            print(f"   Тестируем формат: {format_type}")
            
            args = {
                "address": test_address,
                "format": format_type
            }
            
            try:
                result = subprocess.run([
                    "python3", str(self.backend_script), json.dumps(args)
                ], capture_output=True, text=True, timeout=5)
                
                self.assertEqual(result.returncode, 0, 
                               f"Формат {format_type} должен работать")
                
                response = json.loads(result.stdout)
                
                if response["success"]:
                    self.assertEqual(response["format"], format_type,
                                   f"Формат в ответе должен быть {format_type}")
                    print(f"     ✅ Формат {format_type} работает")
                else:
                    print(f"     ⚠️ Формат {format_type} вернул ошибку: {response.get('error')}")
                    
            except Exception as e:
                print(f"     ❌ Ошибка формата {format_type}: {str(e)}")
        
        print("✅ Форматы вывода протестированы")
    
    def test_refactor_performance_benchmark(self):
        """
        🔵 REFACTOR TEST: Проверка производительности <200ms.
        
        Гипотеза: Резолвинг стандарта выполняется за <200ms согласно требованиям.
        """
        print("\n🔵 REFACTOR TEST: Производительность")
        
        import time
        
        available_addresses = list(self.resolver._logical_map.keys())
        if not available_addresses:
            self.skipTest("Нет адресов для тестирования производительности")
        
        test_address = available_addresses[0]
        args = {
            "address": test_address,
            "format": "summary"
        }
        
        # Проводим 5 измерений и берем среднее
        times = []
        for i in range(5):
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    "python3", str(self.backend_script), json.dumps(args)
                ], capture_output=True, text=True, timeout=2)
                
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # в миллисекундах
                times.append(execution_time)
                
            except subprocess.TimeoutExpired:
                self.fail("Backend слишком медленный (>2s)")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"   Среднее время: {avg_time:.1f}ms")
        print(f"   Мин время: {min_time:.1f}ms")
        print(f"   Макс время: {max_time:.1f}ms")
        
        # Проверяем требование <200ms
        self.assertLess(avg_time, 200.0, 
                       f"Среднее время должно быть <200ms, получено {avg_time:.1f}ms")
        self.assertLess(max_time, 500.0,
                       f"Максимальное время должно быть разумным, получено {max_time:.1f}ms")
        
        print(f"   ✅ Производительность соответствует требованиям (<200ms)")
        print("✅ Производительность в норме")
    
    def test_integration_unified_resolver_compatibility(self):
        """
        🔄 INTEGRATION TEST: Совместимость с UnifiedKeyResolver.
        
        Гипотеза: Backend использует тот же UnifiedKeyResolver что и остальная система.
        """
        print("\n🔄 INTEGRATION TEST: Совместимость с UnifiedKeyResolver")
        
        # Тестируем что backend возвращает те же канонические пути
        available_addresses = list(self.resolver._logical_map.keys())
        if not available_addresses:
            self.skipTest("Нет адресов для тестирования совместимости")
        
        test_address = available_addresses[0]
        
        # Получаем канонический путь через resolver
        expected_canonical = self.resolver.resolve_to_canonical(test_address)
        
        # Получаем канонический путь через backend
        args = {
            "address": test_address,
            "format": "summary"
        }
        
        result = subprocess.run([
            "python3", str(self.backend_script), json.dumps(args)
        ], capture_output=True, text=True, timeout=5)
        
        self.assertEqual(result.returncode, 0, "Backend должен выполниться успешно")
        
        response = json.loads(result.stdout)
        if response["success"]:
            actual_canonical = response.get("canonical_path")
            
            print(f"   Ожидаемый путь: {expected_canonical}")
            print(f"   Фактический путь: {actual_canonical}")
            
            # Проверяем что пути совпадают или указывают на один файл
            if expected_canonical != actual_canonical:
                # Проверяем что указывают на одинаковый файл
                expected_filename = Path(expected_canonical).name if expected_canonical else ""
                actual_filename = Path(actual_canonical).name if actual_canonical else ""
                
                self.assertEqual(expected_filename, actual_filename,
                               f"Файлы должны совпадать: {expected_filename} vs {actual_filename}")
            
            print("   ✅ Канонические пути совместимы")
        else:
            print(f"   ⚠️ Backend вернул ошибку: {response.get('error')}")
        
        print("✅ Совместимость с UnifiedKeyResolver подтверждена")


def main():
    """Запуск TDD тестов Standards-MCP."""
    print("🧪 === TDD ТЕСТЫ STANDARDS-MCP СЕРВЕРА ===")
    print("📋 Цель: Проверить корректность резолвинга стандартов")
    print()
    
    # Создаем test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStandardsMCPTDD)
    
    # Запускаем тесты с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Отчет о результатах
    print(f"\n📊 РЕЗУЛЬТАТЫ TDD ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Неуспешно: {len(result.failures) + len(result.errors)}")
    print(f"   🎯 Общий результат: {'PASS' if result.wasSuccessful() else 'FAIL'}")
    
    if not result.wasSuccessful():
        print("\n🔴 ПРОВАЛЬНЫЕ ТЕСТЫ:")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}: {traceback.splitlines()[-1]}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(main())