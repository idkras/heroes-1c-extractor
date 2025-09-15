#!/usr/bin/env python3
"""
Тестирование загрузки стандартов в DuckDB кеш
"""

import duckdb
from pathlib import Path
import hashlib
from datetime import datetime

def create_simple_cache():
    """Простое создание кеша с несколькими файлами"""
    print("🔄 Создание простого DuckDB кеша...")
    
    # Создаем базу данных
    conn = duckdb.connect('standards_system.duckdb')
    
    # Создаем таблицы
    conn.execute("""
        CREATE TABLE IF NOT EXISTS standards (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            path VARCHAR NOT NULL,
            content TEXT,
            category VARCHAR,
            description TEXT,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Пробуем загрузить несколько файлов для теста
    test_files = [
        Path("todo.md"),
        Path("README.md"),
        Path("advising_platform/src/standards_system.py")
    ]
    
    loaded_count = 0
    for file_path in test_files:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_id = str(file_path).replace('/', '_').replace('\\', '_')
                word_count = len(content.split())
                description = content[:200] + '...' if len(content) > 200 else content
                
                conn.execute("""
                    INSERT OR REPLACE INTO standards 
                    (id, name, path, content, category, description, word_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    file_id,
                    file_path.stem,
                    str(file_path),
                    content,
                    str(file_path.parent),
                    description,
                    word_count,
                    datetime.now().isoformat()
                ])
                
                loaded_count += 1
                print(f"✅ Загружен: {file_path} ({word_count} слов)")
                
            except Exception as e:
                print(f"❌ Ошибка загрузки {file_path}: {e}")
    
    # Проверяем результат
    count = conn.execute('SELECT COUNT(*) FROM standards').fetchone()[0]
    print(f"\n📊 Всего в кеше: {count} файлов")
    
    if count > 0:
        samples = conn.execute('SELECT name, category, word_count FROM standards LIMIT 3').fetchall()
        print("📋 Примеры в кеше:")
        for row in samples:
            print(f"  - {row[0]} ({row[1]}) - {row[2]} слов")
    
    conn.close()
    return count > 0

def test_cache_reading():
    """Тест чтения из кеша"""
    print("\n🔍 Тестирование чтения из кеша...")
    
    conn = duckdb.connect('standards_system.duckdb')
    
    # Читаем файл из кеша вместо диска
    result = conn.execute("""
        SELECT name, content, word_count 
        FROM standards 
        WHERE name = 'todo' 
        LIMIT 1
    """).fetchone()
    
    if result:
        print(f"✅ Файл найден в кеше: {result[0]} ({result[2]} слов)")
        print(f"📄 Первые 100 символов: {result[1][:100]}...")
        return True
    else:
        print("❌ Файл не найден в кеше")
        return False

if __name__ == "__main__":
    # Создаем кеш
    cache_created = create_simple_cache()
    
    if cache_created:
        # Тестируем чтение
        test_cache_reading()
        print("\n✅ DuckDB кеш работает!")
    else:
        print("\n❌ Не удалось создать кеш")