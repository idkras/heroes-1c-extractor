#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_main_references():
    """
    Поиск основных таблиц справочников (не CHNGR)
    """
    print("🔍 Поиск основных таблиц справочников")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Ищем основные таблицы справочников (не CHNGR)
            main_reference_tables = []
            
            for table_name in db.tables.keys():
                table_lower = table_name.lower()
                
                # Исключаем CHNGR таблицы (это изменения)
                if 'chngr' in table_lower:
                    continue
                
                # Проверяем ключевые слова справочников
                reference_keywords = [
                    'reference', 'справочник', 'номенклатур', 'товар',
                    'наименование', 'описание', 'код', 'название'
                ]
                
                has_keyword = any(keyword in table_lower for keyword in reference_keywords)
                
                if has_keyword and len(db.tables[table_name]) > 0:
                    table = db.tables[table_name]
                    
                    # Проверяем наличие непустых записей
                    non_empty_count = 0
                    for i in range(min(50, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_count += 1
                    
                    if non_empty_count > 0:
                        main_reference_tables.append((table_name, len(table), non_empty_count))
            
            print(f"\n✅ Найдено {len(main_reference_tables)} основных таблиц справочников:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(main_reference_tables[:10]):
                print(f"\n{i+1}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем структуру таблицы
                table = db.tables[table_name]
                print(f"   📝 Структура полей:")
                for field_name, field_desc in list(table.fields.items())[:15]:
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Показываем примеры данных
                print(f"   📄 Примеры данных:")
                found_examples = 0
                for j in range(min(100, len(table))):
                    row = table[j]
                    if not row.is_empty and found_examples < 3:
                        print(f"      Запись #{j}:")
                        
                        # Показываем поля с данными
                        data_fields = 0
                        for field_name in table.fields.keys():
                            try:
                                value = row[field_name]
                                if value is not None and str(value).strip():
                                    print(f"         {field_name}: {value}")
                                    data_fields += 1
                                    if data_fields >= 10:  # Показываем первые 10 полей
                                        break
                            except Exception as e:
                                pass
                        
                        found_examples += 1
                        print(f"         ... (показано {data_fields} полей)")
                
                if i >= 4:  # Показываем только первые 5 таблиц
                    break
            
            # Если не нашли основные справочники, ищем в больших таблицах
            if not main_reference_tables:
                print("\n🔍 Поиск в больших таблицах с данными:")
                
                # Ищем большие таблицы с реальными данными
                large_tables = []
                for table_name in db.tables.keys():
                    table = db.tables[table_name]
                    if len(table) > 100000:  # Большие таблицы
                        non_empty_count = 0
                        for i in range(min(50, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            large_tables.append((table_name, len(table), non_empty_count))
                
                large_tables.sort(key=lambda x: x[1], reverse=True)
                
                print(f"📊 Топ-10 больших таблиц с данными:")
                for i, (table_name, total_count, non_empty_count) in enumerate(large_tables[:10]):
                    print(f"  {i+1}. {table_name}: {total_count:,} записей ({non_empty_count} непустых)")
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_main_references()
    print("\n✅ Поиск завершен") 