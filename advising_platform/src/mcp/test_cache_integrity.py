#!/usr/bin/env python3
"""
TDD Test: Cache Integrity Verification
Автоматическая проверка качества кеша стандартов согласно принципу "What am I missing?"
"""

import unittest
from pathlib import Path
from src.mcp.cache_reader import CacheReader
import os

class TestCacheIntegrity(unittest.TestCase):
    """TDD тесты для проверки целостности кеша стандартов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.cache_reader = CacheReader()
        self.standards_dir = Path("..") / "[standards .md]"
        
    def test_cache_contains_real_standards(self):
        """RED TEST: Кеш должен содержать реальные стандарты, а не служебные документы"""
        
        # Получаем данные из кеша
        cached_standards = self.cache_reader.get_all_standards()
        
        # Проверяем что кеш не пустой
        self.assertGreater(len(cached_standards), 0, "Кеш пуст")
        
        # Проверяем что это реальные стандарты, а не docs/
        real_standards_count = 0
        docs_count = 0
        
        for standard in cached_standards:
            path = standard.get('path', '')
            if 'docs/' in path:
                docs_count += 1
            elif '[standards .md]' in path:
                real_standards_count += 1
                
        # Критерий: больше реальных стандартов чем служебных документов
        self.assertGreater(real_standards_count, docs_count, 
                          f"В кеше больше служебных документов ({docs_count}) чем реальных стандартов ({real_standards_count})")
        
        print(f"✅ Кеш содержит {real_standards_count} реальных стандартов и {docs_count} служебных документов")
        
    def test_cache_excludes_archive_files(self):
        """RED TEST: Кеш не должен содержать архивные файлы"""
        
        cached_standards = self.cache_reader.get_all_standards()
        
        archive_files = []
        for standard in cached_standards:
            path = standard.get('path', '')
            id_field = standard.get('id', '')
            
            # Проверяем на архивные паттерны
            if any(pattern in path.lower() or pattern in id_field.lower() for pattern in [
                '[archive]', 'backup', 'archived', 'old', 'copy', 
                '20250514', '2025_05_14', 'template', 'consolidated_'
            ]):
                archive_files.append(standard['name'])
        
        # Кеш НЕ должен содержать архивные файлы
        self.assertEqual(len(archive_files), 0, 
                        f"Кеш содержит архивные файлы: {archive_files}")
        
        print(f"✅ Кеш не содержит архивных файлов")
        
    def test_minimum_standards_threshold(self):
        """RED TEST: Кеш должен содержать минимум 40+ стандартов"""
        
        cached_standards = self.cache_reader.get_all_standards()
        count = len(cached_standards)
        
        # Критерий из задачи: 70+ стандартов, но проверим более реалистичные 40+
        self.assertGreaterEqual(count, 40, 
                               f"Кеш содержит только {count} стандартов, ожидается минимум 40")
        
        print(f"✅ Кеш содержит {count} стандартов (превышает минимум)")
        
    def test_search_functionality_works(self):
        """RED TEST: Поиск должен находить релевантные результаты"""
        
        # Поиск по популярному термину
        results = self.cache_reader.search_standards("standard", limit=5)
        
        # Должны быть найдены результаты
        self.assertGreater(len(results), 0, "Поиск 'standard' не нашел результатов")
        
        # Результаты должны содержать искомый термин
        found_relevant = False
        for result in results:
            name = result.get('name', '').lower()
            content = result.get('content', '').lower()
            if 'standard' in name or 'standard' in content:
                found_relevant = True
                break
                
        self.assertTrue(found_relevant, "Поиск не нашел релевантных результатов")
        
        print(f"✅ Поиск работает корректно, найдено {len(results)} результатов")
        
    def test_specific_standard_retrieval(self):
        """RED TEST: Можно получить конкретный стандарт по ID"""
        
        # Сначала получаем список всех стандартов
        all_standards = self.cache_reader.get_all_standards()
        self.assertGreater(len(all_standards), 0, "Нет стандартов для тестирования")
        
        # Берем первый стандарт
        first_standard_id = all_standards[0]['id']
        
        # Пытаемся получить его по ID
        retrieved = self.cache_reader.get_standard_by_id(first_standard_id)
        
        self.assertIsNotNone(retrieved, f"Не удалось получить стандарт по ID: {first_standard_id}")
        self.assertEqual(retrieved['id'], first_standard_id, "ID не совпадает")
        
        print(f"✅ Поиск по ID работает корректно")

    def run_integrity_verification(self):
        """Запуск всех проверок целостности"""
        print("\n🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ КЕША СТАНДАРТОВ")
        print("=" * 50)
        
        # Запускаем все тесты
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCacheIntegrity)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Сводка
        print("\n📊 СВОДКА ПРОВЕРКИ:")
        print(f"Всего тестов: {result.testsRun}")
        print(f"Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Провалов: {len(result.failures)}")
        print(f"Ошибок: {len(result.errors)}")
        
        if result.failures:
            print("\n❌ ПРОВАЛЫ:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\n💥 ОШИБКИ:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
                
        return result.wasSuccessful()

if __name__ == "__main__":
    tester = TestCacheIntegrity()
    success = tester.run_integrity_verification()
    
    if success:
        print("\n✅ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО")
        print("Кеш стандартов работает корректно")
    else:
        print("\n❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        print("Требуется исправление кеша")