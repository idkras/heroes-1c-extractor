#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_data_tables():
    """
    Ищет таблицы с реальными данными
    """
    print("🔍 Поиск таблиц с реальными данными")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Ищем таблицы с данными
            data_tables = []
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                if len(table) > 0:
                    data_tables.append((table_name, len(table)))
            
            # Сортируем по количеству записей
            data_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n✅ Найдено {len(data_tables)} таблиц с данными:")
            print("\n📊 Топ-20 таблиц по количеству записей:")
            
            for i, (table_name, record_count) in enumerate(data_tables[:20]):
                print(f"  {i+1:2d}. {table_name}: {record_count:,} записей")
                
                # Показываем структуру первых 5 таблиц
                if i < 5:
                    table = db.tables[table_name]
                    first_row = table[0]
                    fields = list(first_row.as_dict().keys())
                    print(f"       📝 Поля: {fields[:10]}{'...' if len(fields) > 10 else ''}")
                    
                    # Показываем первые значения
                    if record_count > 0:
                        sample_data = first_row.as_dict()
                        print(f"       📄 Пример данных: {str(sample_data)[:200]}...")
                    print()
            
            # Ищем таблицы с BLOB данными
            print("\n🔍 Поиск таблиц с BLOB данными (изображения):")
            blob_tables = []
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                if len(table) > 0:
                    first_row = table[0]
                    fields = list(first_row.as_dict().keys())
                    # Ищем поля с изображениями
                    if any('image' in field.lower() or 'blob' in field.lower() or 'picture' in field.lower() for field in fields):
                        blob_tables.append((table_name, len(table)))
            
            if blob_tables:
                print(f"✅ Найдено {len(blob_tables)} таблиц с BLOB данными:")
                for table_name, record_count in blob_tables[:10]:
                    print(f"  📊 {table_name}: {record_count:,} записей")
            else:
                print("❌ Таблицы с BLOB данными не найдены")
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_data_tables()
    print("\n✅ Поиск завершен") 