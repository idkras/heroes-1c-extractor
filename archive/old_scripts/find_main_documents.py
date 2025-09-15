#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os

def find_main_documents():
    """
    Поиск основных таблиц документов (не табличных частей)
    """
    print("🔍 Поиск основных таблиц документов")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Ищем основные таблицы документов (не _VT*)
            main_document_tables = []
            
            for table_name in db.tables.keys():
                # Ищем таблицы документов, но НЕ табличные части
                if '_DOCUMENT' in table_name and '_VT' not in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Проверяем наличие непустых записей
                        non_empty_count = 0
                        for i in range(min(50, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            main_document_tables.append((table_name, len(table), non_empty_count))
            
            # Сортируем по размеру
            main_document_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 Найдено {len(main_document_tables)} основных таблиц документов:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(main_document_tables[:10], 1):
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
                    try:
                        row_dict = row.as_dict()
                        for field_name, value in row_dict.items():
                            if value is not None:
                                if isinstance(value, bytes):
                                    value = value.hex()
                                print(f"         {field_name}: {value}")
                    except Exception as e:
                        print(f"         Ошибка извлечения: {e}")
                    print()
            
            # Ищем журналы документов
            print(f"\n🔍 Поиск журналов документов:")
            journal_tables = []
            
            for table_name in db.tables.keys():
                if 'JOURNAL' in table_name and '_DOCUMENT' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        non_empty_count = 0
                        for i in range(min(50, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            journal_tables.append((table_name, len(table), non_empty_count))
            
            journal_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 Найдено {len(journal_tables)} журналов документов:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(journal_tables[:5], 1):
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
    find_main_documents() 