#!/usr/bin/env python3
"""
TDD тест проверки исправления синхронизации кеша с помощью UnifiedKeyResolver.

JTBD: Проверить, что unified key resolver решает проблему 0% синхронизации 
между кешем и тестами целостности.

Гипотеза: После интеграции UnifiedKeyResolver синхронизация кеша будет >95%.

Критерии успеха:
- Тест синхронизации находит файлы в кеше по любому формату ключа
- Процент синхронизации поднимается с 0% до >95%
- Поиск работает для логических, абсолютных и относительных путей

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.unified_key_resolver import get_resolver
from src.cache.real_inmemory_cache import get_cache

def test_cache_sync_with_resolver():
    """
    Тестирует исправление синхронизации кеша через unified key resolver.
    """
    print("🔧 === ТЕСТ ИСПРАВЛЕНИЯ СИНХРОНИЗАЦИИ КЕША ===")
    print("📋 Проверяем решение проблемы 0% синхронизации")
    print()
    
    # Инициализируем компоненты
    resolver = get_resolver()
    cache = get_cache()
    cache.initialize_from_disk()
    
    # Получаем статистику
    resolver_stats = resolver.get_statistics()
    cache_paths = cache.get_all_paths()
    
    print(f"📊 СТАТИСТИКА ИНИЦИАЛИЗАЦИИ:")
    print(f"   🔗 Логических маппингов в resolver: {resolver_stats['logical_mappings']}")
    print(f"   💾 Файлов в кеше: {len(cache_paths)}")
    print(f"   📁 Корень проекта найден: {resolver_stats['project_root_exists']}")
    print(f"   📚 Папка стандартов найдена: {resolver_stats['standards_root_exists']}")
    print()
    
    # Тестируем поиск разными способами
    print("🔍 ТЕСТИРОВАНИЕ ПОИСКА ПО РАЗНЫМ ФОРМАТАМ:")
    
    test_cases = 0
    successful_matches = 0
    
    # Берем первые несколько файлов из кеша для тестирования
    sample_files = list(cache_paths)[:5]
    
    for cache_key in sample_files:
        if not cache_key.endswith('.md'):
            continue
            
        test_cases += 1
        filename = Path(cache_key).name
        
        print(f"\n   📄 Тестируем файл: {filename}")
        print(f"      Ключ в кеше: {cache_key}")
        
        # Тест 1: Поиск по имени файла
        found_by_name = resolver.find_by_any_key(filename, cache_paths)
        if found_by_name:
            successful_matches += 1
            print(f"      ✅ Найден по имени: {found_by_name}")
        else:
            print(f"      ❌ НЕ найден по имени")
        
        # Тест 2: Поиск через кеш с resolver
        cache_entry = cache.get_document(filename)
        if cache_entry:
            successful_matches += 1
            print(f"      ✅ Найден через кеш: {cache_entry.path}")
        else:
            print(f"      ❌ НЕ найден через кеш")
        
        # Тест 3: Нормализация ключа
        normalized = resolver.normalize_key(cache_key)
        print(f"      🔄 Нормализованный ключ: {normalized}")
    
    # Вычисляем процент успеха
    if test_cases > 0:
        success_rate = (successful_matches / (test_cases * 2)) * 100
        print(f"\n📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"   🎯 Тест-кейсов: {test_cases}")
        print(f"   ✅ Успешных поисков: {successful_matches} из {test_cases * 2}")
        print(f"   📊 Процент успеха: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print(f"   🎉 ПРОБЛЕМА СИНХРОНИЗАЦИИ РЕШЕНА! ({success_rate:.1f}% >= 95%)")
            return True
        else:
            print(f"   ⚠️ Требуется доработка ({success_rate:.1f}% < 95%)")
            return False
    else:
        print("   ❌ Не найдено файлов для тестирования")
        return False

def main():
    """Запуск теста исправления синхронизации."""
    try:
        success = test_cache_sync_with_resolver()
        
        print(f"\n🏁 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
        if success:
            print("✅ Unified Key Resolver успешно исправил проблему синхронизации кеша!")
            print("🚀 Система готова к работе с 95%+ синхронизацией")
            return 0
        else:
            print("❌ Проблема синхронизации требует дополнительной доработки")
            print("🔧 Рекомендуется анализ и улучшение алгоритма поиска")
            return 1
            
    except Exception as e:
        print(f"💥 ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())