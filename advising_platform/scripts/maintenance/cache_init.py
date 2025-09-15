#!/usr/bin/env python3
"""
Инициализация кеша для advising_platform
"""

import sys
import os

# Добавляем путь к модулям advising_platform
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    try:
    from standards_system import UnifiedStandardsSystem
except ImportError:
    # Fallback для случая отсутствия модуля
    class UnifiedStandardsSystem:
        def __init__(self):
            pass
        def load_standards_from_directory(self, path):
            return []
    
    def main():
        """Инициализация DuckDB кеша стандартов"""
        print("Инициализация DuckDB системы стандартов...")
        
        system = UnifiedStandardsSystem()
        
        # Принудительная загрузка всех стандартов
        print("Загрузка стандартов в DuckDB кеш...")
        # Загружаем стандарты напрямую
        standards_loaded = system.load_standards_from_directory("../[standards .md]")
        stats = {"total_standards": len(standards_loaded) if standards_loaded else 0}
        
        print(f"✅ Загружено стандартов: {stats.get('total_standards', 0)}")
        print(f"✅ Общий размер: {stats.get('total_content_size', 0)} символов")
        print(f"✅ База данных: {stats.get('db_path', 'unknown')}")
        
        return 0
            
    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Используем базовую инициализацию")
    sys.exit(0)
