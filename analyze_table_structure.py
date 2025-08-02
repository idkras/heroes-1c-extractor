#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def analyze_table_structure():
    """
    Детальный анализ структуры таблиц
    """
    print("🔍 Детальный анализ структуры таблиц")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Анализируем первые 5 таблиц с данными
            data_tables = []
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                if len(table) > 0:
                    data_tables.append((table_name, len(table)))
            
            data_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📋 Анализ топ-5 таблиц:")
            
            for i, (table_name, record_count) in enumerate(data_tables[:5]):
                print(f"\n{i+1}. 📊 {table_name}: {record_count:,} записей")
                
                table = db.tables[table_name]
                first_row = table[0]
                
                # Анализируем поля
                print(f"   📝 Структура полей:")
                for field_name, field_desc in table.fields.items():
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}, null_exists={field_desc.null_exists}")
                
                # Показываем сырые данные
                print(f"   📄 Сырые данные первой записи:")
                print(f"      Размер записи: {len(first_row._row_bytes)} байт")
                print(f"      Данные: {first_row._row_bytes[:50].hex()}")
                
                # Показываем первые несколько полей
                print(f"   🔍 Значения первых полей:")
                field_names = list(table.fields.keys())[:5]
                for field_name in field_names:
                    try:
                        value = first_row[field_name]
                        print(f"      {field_name}: {value} (тип: {type(value)})")
                    except Exception as e:
                        print(f"      {field_name}: ОШИБКА - {e}")
                
                if i >= 2:  # Показываем только первые 3 таблицы
                    break
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_table_structure()
    print("\n✅ Анализ завершен") 