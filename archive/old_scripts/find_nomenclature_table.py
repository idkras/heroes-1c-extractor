#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_nomenclature_table():
    """
    Поиск таблицы с номенклатурой товаров
    """
    print("🔍 Поиск таблицы с номенклатурой товаров")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Ищем таблицы с полями NVC (строки) - это могут быть названия товаров
            nomenclature_tables = []
            
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                
                # Проверяем наличие полей NVC (строки)
                has_nvc_fields = False
                for field_name, field_desc in table.fields.items():
                    if field_desc.type == 'NVC' and field_desc.length > 20:  # Длинные строки
                        has_nvc_fields = True
                        break
                
                if has_nvc_fields and len(table) > 100:  # Таблицы с большим количеством записей
                    # Проверяем наличие непустых записей
                    non_empty_count = 0
                    for i in range(min(50, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_count += 1
                    
                    if non_empty_count > 0:
                        nomenclature_tables.append((table_name, len(table), non_empty_count))
            
            # Сортируем по размеру
            nomenclature_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n📊 Найдено {len(nomenclature_tables)} таблиц с полями NVC (возможная номенклатура):")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(nomenclature_tables[:10]):
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
                                    if data_fields >= 8:  # Показываем первые 8 полей
                                        break
                            except Exception as e:
                                pass
                        
                        found_examples += 1
                        print(f"         ... (показано {data_fields} полей)")
                
                if i >= 4:  # Показываем только первые 5 таблиц
                    break
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_nomenclature_table()
    print("\n✅ Поиск завершен") 