#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_real_data():
    """
    Ищет таблицы с реальными (не пустыми) данными
    """
    print("🔍 Поиск таблиц с реальными данными")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Ищем таблицы с непустыми записями
            real_data_tables = []
            
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                if len(table) > 0:
                    # Проверяем первые 10 записей на наличие непустых
                    non_empty_count = 0
                    for i in range(min(10, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_count += 1
                    
                    if non_empty_count > 0:
                        real_data_tables.append((table_name, len(table), non_empty_count))
            
            # Сортируем по количеству непустых записей
            real_data_tables.sort(key=lambda x: x[2], reverse=True)
            
            print(f"\n✅ Найдено {len(real_data_tables)} таблиц с реальными данными:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(real_data_tables[:10]):
                print(f"\n{i+1}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем пример непустой записи
                table = db.tables[table_name]
                for j in range(min(10, len(table))):
                    row = table[j]
                    if not row.is_empty:
                        print(f"   📄 Пример непустой записи #{j}:")
                        print(f"      Размер: {len(row._row_bytes)} байт")
                        print(f"      Данные: {row._row_bytes[:50].hex()}")
                        
                        # Показываем первые 3 поля
                        field_names = list(table.fields.keys())[:3]
                        for field_name in field_names:
                            try:
                                value = row[field_name]
                                print(f"      {field_name}: {value}")
                            except Exception as e:
                                print(f"      {field_name}: ОШИБКА - {e}")
                        break
                
                if i >= 4:  # Показываем только первые 5 таблиц
                    break
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_real_data()
    print("\n✅ Поиск завершен") 