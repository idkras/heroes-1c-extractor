#!/usr/bin/env python3
"""
Тест для проверки работы Parquet + DuckDB интеграции
"""

import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
import pandas as pd
import json
import os
from pathlib import Path

def test_parquet_duckdb_integration() -> bool:
    """Тест интеграции Parquet + DuckDB"""
    print("🧪 Тестирование Parquet + DuckDB интеграции...")
    
    # Создаем тестовые данные
    test_data = {
        "document_id": ["DOC001", "DOC002", "DOC003"],
        "document_type": ["sale", "purchase", "transfer"],
        "amount": [1000.0, 2000.0, 1500.0],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "store": ["Store A", "Store B", "Store C"],
        "flower_type": ["rose", "tulip", "chrysanthemum"]
    }
    
    # Создаем DataFrame
    df = pd.DataFrame(test_data)
    print(f"📊 Создан DataFrame с {len(df)} записями")
    
    # Конвертируем в Parquet
    parquet_file = "data/results/test_flowers.parquet"
    os.makedirs("data/results", exist_ok=True)
    
    df.to_parquet(parquet_file, engine='pyarrow')
    print(f"💾 Данные сохранены в Parquet: {parquet_file}")
    
    # Проверяем размер файла
    file_size = os.path.getsize(parquet_file)
    print(f"📏 Размер Parquet файла: {file_size} байт")
    
    # Создаем DuckDB базу
    db_file = "data/results/test_flowers.duckdb"
    conn = duckdb.connect(db_file)
    
    # Импортируем Parquet в DuckDB
    conn.execute(f"CREATE TABLE flowers AS SELECT * FROM '{parquet_file}'")
    print(f"🗄️ Данные импортированы в DuckDB: {db_file}")
    
    # Тестируем SQL запросы
    print("\n🔍 Тестирование SQL запросов:")
    
    # Запрос 1: Общая статистика
    result1 = conn.execute("SELECT COUNT(*) as total_records FROM flowers").fetchone()
    print(f"📈 Всего записей: {result1[0]}")
    
    # Запрос 2: Анализ по типам цветов
    result2 = conn.execute("""
        SELECT 
            flower_type,
            COUNT(*) as count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM flowers 
        GROUP BY flower_type
        ORDER BY total_amount DESC
    """).fetchall()
    
    print("🌸 Анализ по типам цветов:")
    for row in result2:
        print(f"  {row[0]}: {row[1]} записей, сумма: {row[2]}, средняя: {row[3]:.2f}")
    
    # Запрос 3: Анализ по магазинам
    result3 = conn.execute("""
        SELECT 
            store,
            COUNT(*) as transactions,
            SUM(amount) as revenue
        FROM flowers 
        GROUP BY store
        ORDER BY revenue DESC
    """).fetchall()
    
    print("\n🏪 Анализ по магазинам:")
    for row in result3:
        print(f"  {row[0]}: {row[1]} транзакций, выручка: {row[2]}")
    
    # Запрос 4: Поиск по цветам
    result4 = conn.execute("""
        SELECT * FROM flowers 
        WHERE flower_type LIKE '%rose%' OR flower_type LIKE '%tulip%'
        ORDER BY amount DESC
    """).fetchall()
    
    print(f"\n🔍 Найдено {len(result4)} записей с розами и тюльпанами")
    
    # Закрываем соединение
    conn.close()
    
    # Проверяем производительность
    import time
    
    # Тест скорости чтения Parquet
    start_time = time.time()
    df_read = pd.read_parquet(parquet_file)
    parquet_time = time.time() - start_time
    
    # Тест скорости чтения JSON (для сравнения)
    json_file = "data/results/test_flowers.json"
    df.to_json(json_file, orient='records', indent=2)
    
    start_time = time.time()
    df_json = pd.read_json(json_file)
    json_time = time.time() - start_time
    
    print(f"\n⚡ Производительность:")
    print(f"  Parquet: {parquet_time:.4f} секунд")
    print(f"  JSON: {json_time:.4f} секунд")
    print(f"  Ускорение: {json_time/parquet_time:.1f}x")
    
    # Проверяем сжатие
    json_size = os.path.getsize(json_file)
    compression_ratio = (1 - file_size / json_size) * 100
    
    print(f"\n📦 Сжатие данных:")
    print(f"  JSON размер: {json_size} байт")
    print(f"  Parquet размер: {file_size} байт")
    print(f"  Экономия места: {compression_ratio:.1f}%")
    
    print("\n✅ Тест Parquet + DuckDB интеграции завершен успешно!")
    return True

if __name__ == "__main__":
    test_parquet_duckdb_integration()
