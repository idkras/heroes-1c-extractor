#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_product_data():
    """
    Ищет данные о товарах/цветах в реальных таблицах
    """
    print("🔍 Поиск данных о товарах/цветах")
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
                'номенклатура', 'товары', 'цветы', 'розы', 'тюльпаны',
                'наименование', 'описание', 'название'
            ]
            
            # Ищем таблицы с ключевыми словами и реальными данными
            product_tables = []
            
            for table_name in db.tables.keys():
                table_lower = table_name.lower()
                
                # Проверяем ключевые слова в названии таблицы
                has_keyword = any(keyword in table_lower for keyword in keywords)
                
                if has_keyword and len(db.tables[table_name]) > 0:
                    table = db.tables[table_name]
                    
                    # Проверяем наличие непустых записей
                    non_empty_count = 0
                    for i in range(min(10, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_count += 1
                    
                    if non_empty_count > 0:
                        product_tables.append((table_name, len(table), non_empty_count))
            
            print(f"\n✅ Найдено {len(product_tables)} таблиц с товарами и реальными данными:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(product_tables[:10]):
                print(f"\n{i+1}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем структуру таблицы
                table = db.tables[table_name]
                print(f"   📝 Структура полей:")
                for field_name, field_desc in list(table.fields.items())[:10]:
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Показываем пример данных
                for j in range(min(5, len(table))):
                    row = table[j]
                    if not row.is_empty:
                        print(f"   📄 Пример записи #{j}:")
                        
                        # Показываем все поля с данными
                        for field_name in table.fields.keys():
                            try:
                                value = row[field_name]
                                if value is not None and str(value).strip():
                                    print(f"      {field_name}: {value}")
                            except Exception as e:
                                pass
                        break
                
                if i >= 4:  # Показываем только первые 5 таблиц
                    break
            
            # Если не нашли по ключевым словам, ищем в больших таблицах
            if not product_tables:
                print("\n🔍 Поиск в больших таблицах с реальными данными:")
                
                # Ищем большие таблицы с реальными данными
                large_tables = []
                for table_name in db.tables.keys():
                    table = db.tables[table_name]
                    if len(table) > 1000:  # Большие таблицы
                        non_empty_count = 0
                        for i in range(min(10, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            large_tables.append((table_name, len(table), non_empty_count))
                
                large_tables.sort(key=lambda x: x[1], reverse=True)
                
                print(f"📊 Топ-5 больших таблиц с реальными данными:")
                for i, (table_name, total_count, non_empty_count) in enumerate(large_tables[:5]):
                    print(f"  {i+1}. {table_name}: {total_count:,} записей ({non_empty_count} непустых)")
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_product_data()
    print("\n✅ Поиск завершен") 