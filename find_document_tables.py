#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_document_tables():
    """
    Поиск таблиц документов (актов, счетов-фактур, накладных)
    """
    print("🔍 Поиск таблиц документов (актов, счетов-фактур, накладных)")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Ищем таблицы документов
            document_tables = []
            
            for table_name in db.tables.keys():
                # Ищем таблицы документов по названию
                if '_DOCUMENT' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Проверяем наличие непустых записей
                        non_empty_count = 0
                        for i in range(min(50, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            document_tables.append((table_name, len(table), non_empty_count))
            
            # Сортируем по размеру
            document_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 Найдено {len(document_tables)} таблиц документов:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(document_tables[:10], 1):
                print(f"\n{i}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем структуру полей
                table = db.tables[table_name]
                print(f"   📝 Структура полей:")
                for field_name, field_desc in table.fields.items():
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Показываем примеры непустых записей
                print(f"   📄 Примеры непустых записей:")
                non_empty_rows = []
                for i in range(min(5, len(table))):
                    row = table[i]
                    if not row.is_empty:
                        non_empty_rows.append((i, row))
                
                for j, (row_index, row) in enumerate(non_empty_rows[:3], 1):
                    print(f"      Запись #{j}:")
                    for field_name, field_desc in table.fields.items():
                        value = getattr(row, field_name, None)
                        if value is not None:
                            print(f"         {field_name}: {value}")
                    print()
            
            # Ищем табличные части документов
            print(f"\n🔍 Поиск табличных частей документов:")
            vt_tables = []
            
            for table_name in db.tables.keys():
                if '_VT' in table_name and '_DOCUMENT' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        non_empty_count = 0
                        for i in range(min(50, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            vt_tables.append((table_name, len(table), non_empty_count))
            
            vt_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 Найдено {len(vt_tables)} табличных частей документов:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(vt_tables[:5], 1):
                print(f"\n{i}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем структуру полей
                table = db.tables[table_name]
                print(f"   📝 Структура полей:")
                for field_name, field_desc in table.fields.items():
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
            
            print(f"\n✅ Поиск завершен")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    find_document_tables() 