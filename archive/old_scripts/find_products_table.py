#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_products_table():
    """
    Поиск таблицы с реальными товарами
    """
    print("🔍 Поиск таблицы с реальными товарами")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Ищем таблицы с большим количеством записей
            large_tables = []
            
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                if len(table) > 1000:  # Таблицы с большим количеством записей
                    # Проверяем наличие непустых записей
                    non_empty_count = 0
                    for i in range(min(100, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_count += 1
                    
                    if non_empty_count > 0:
                        large_tables.append((table_name, len(table), non_empty_count))
            
            # Сортируем по размеру
            large_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 Найдено {len(large_tables)} больших таблиц с данными:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(large_tables[:15]):
                print(f"\n{i+1}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем структуру таблицы
                table = db.tables[table_name]
                print(f"   📝 Структура полей:")
                for field_name, field_desc in list(table.fields.items())[:10]:
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Показываем примеры данных
                print(f"   📄 Примеры данных:")
                found_examples = 0
                for j in range(min(50, len(table))):
                    row = table[j]
                    if not row.is_empty and found_examples < 2:
                        print(f"      Запись #{j}:")
                        
                        # Показываем поля с данными
                        data_fields = 0
                        for field_name in table.fields.keys():
                            try:
                                value = row[field_name]
                                if value is not None and str(value).strip():
                                    print(f"         {field_name}: {value}")
                                    data_fields += 1
                                    if data_fields >= 5:  # Показываем первые 5 полей
                                        break
                            except Exception as e:
                                pass
                        
                        found_examples += 1
                        print(f"         ... (показано {data_fields} полей)")
                
                if i >= 9:  # Показываем только первые 10 таблиц
                    break
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_products_table()
    print("\n✅ Поиск завершен") 