#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def extract_flower_data():
    """
    Извлекает данные о цветах из 1CD файла используя исправленную onec_dtools
    """
    print("🚀 Запуск извлечения данных о цветах из 1CD файла")
    print("=" * 60)
    
    try:
        # Открываем 1CD файл
        print("🔍 Открываем 1CD файл...")
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Выводим список таблиц
            print("\n📋 Доступные таблицы:")
            for i, table_name in enumerate(db.tables.keys()):
                if i < 20:  # Показываем первые 20 таблиц
                    print(f"  {i+1}. {table_name}")
                elif i == 20:
                    print(f"  ... и еще {len(db.tables) - 20} таблиц")
                    break
            
            # Ищем таблицы с данными о товарах/цветах
            print("\n🔍 Поиск таблиц с данными о товарах...")
            product_tables = []
            for table_name in db.tables.keys():
                if any(keyword in table_name.lower() for keyword in ['товар', 'номенклатура', 'справочник', 'цвет', 'flower']):
                    product_tables.append(table_name)
            
            if product_tables:
                print(f"✅ Найдено {len(product_tables)} таблиц с товарами:")
                for table_name in product_tables:
                    print(f"  📊 {table_name}")
                    
                    # Пробуем прочитать данные из первой таблицы
                    table = db.tables[table_name]
                    print(f"    📈 Записей в таблице: {len(table)}")
                    
                    if len(table) > 0:
                        # Читаем первую запись
                        first_row = table[0]
                        print(f"    📝 Первая запись: {first_row.as_dict(read_blobs=True)}")
                        break
            else:
                print("❌ Таблицы с товарами не найдены")
                
                # Показываем все таблицы для анализа
                print("\n📋 Все таблицы для анализа:")
                for table_name in list(db.tables.keys())[:10]:
                    table = db.tables[table_name]
                    print(f"  📊 {table_name}: {len(table)} записей")
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_flower_data()
    print("\n✅ Анализ завершен") 