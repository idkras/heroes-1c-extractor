#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_product_tables():
    """
    Ищет таблицы с данными о товарах/цветах
    """
    print("🔍 Поиск таблиц с данными о товарах/цветах")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Ключевые слова для поиска
            keywords = [
                'товар', 'номенклатура', 'справочник', 'цвет', 'flower',
                'product', 'item', 'catalog', 'reference', 'справочник',
                'номенклатура', 'товары', 'цветы', 'розы', 'тюльпаны'
            ]
            
            # Ищем таблицы с ключевыми словами
            found_tables = []
            for table_name in db.tables.keys():
                table_lower = table_name.lower()
                for keyword in keywords:
                    if keyword in table_lower:
                        found_tables.append(table_name)
                        break
            
            if found_tables:
                print(f"\n✅ Найдено {len(found_tables)} таблиц с товарами:")
                for table_name in found_tables:
                    table = db.tables[table_name]
                    print(f"  📊 {table_name}: {len(table)} записей")
                    
                    # Показываем структуру первой таблицы
                    if len(table) > 0:
                        first_row = table[0]
                        print(f"    📝 Структура: {list(first_row.as_dict().keys())}")
                        break
            else:
                print("\n❌ Таблицы с товарами не найдены по ключевым словам")
                
                # Показываем все таблицы для анализа
                print("\n📋 Анализ всех таблиц:")
                for table_name in list(db.tables.keys()):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        print(f"  📊 {table_name}: {len(table)} записей")
                        
                        # Показываем структуру первых 5 таблиц
                        if len([t for t in db.tables.keys() if db.tables[t] and len(db.tables[t]) > 0]) <= 5:
                            first_row = table[0]
                            print(f"    📝 Структура: {list(first_row.as_dict().keys())}")
                        
                        # Останавливаемся после 10 таблиц
                        if len([t for t in db.tables.keys() if db.tables[t] and len(db.tables[t]) > 0]) >= 10:
                            break
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_product_tables()
    print("\n✅ Поиск завершен") 