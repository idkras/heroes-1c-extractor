#!/usr/bin/env python3
"""
Простой клиент для работы с DuckDB системой стандартов
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям
current_dir = Path(__file__).parent.resolve()
advising_platform_dir = current_dir.parent.parent
sys.path.insert(0, str(advising_platform_dir))

from src.standards_system import UnifiedStandardsSystem

def main():
    """Простая проверка системы стандартов"""
    print("🔧 Проверка работы DuckDB системы стандартов...")
    
    try:
        system = UnifiedStandardsSystem()
        
        # Получаем количество стандартов
        result = system.conn.execute("SELECT COUNT(*) FROM standards").fetchone()
        total_standards = result[0] if result else 0
        
        print(f"✅ Подключение к DuckDB: успешно")
        print(f"📊 Загружено стандартов: {total_standards}")
        
        if total_standards > 0:
            # Показываем несколько примеров
            examples = system.conn.execute(
                "SELECT id, name, category FROM standards LIMIT 5"
            ).fetchall()
            
            print("📋 Примеры стандартов:")
            for example in examples:
                print(f"  • {example[1]} ({example[2]})")
                
        # Тестируем поиск
        search_result = system.search_standards("API")
        if search_result:
            print(f"🔍 Поиск 'API': найдено {len(search_result)} результатов")
        
        return {
            "success": True,
            "total_standards": total_standards,
            "system_status": "working"
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {
            "success": False,
            "error": str(e),
            "system_status": "failed"
        }

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["success"] else 1)