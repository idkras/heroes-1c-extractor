#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def analyze_real_data():
    """
    Детальный анализ реальных данных в найденных таблицах
    """
    print("🔍 Детальный анализ реальных данных")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Анализируем ключевые таблицы с реальными данными
            key_tables = ['CONFIG', 'PARAMS', 'FILES', 'V8USERS', '_COMMONSETTINGS']
            
            for table_name in key_tables:
                if table_name in db.tables:
                    table = db.tables[table_name]
                    print(f"\n📊 Анализ таблицы: {table_name}")
                    print(f"   📈 Всего записей: {len(table):,}")
                    
                    # Находим непустые записи
                    non_empty_rows = []
                    for i in range(min(20, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_rows.append((i, row))
                    
                    print(f"   ✅ Непустых записей: {len(non_empty_rows)}")
                    
                    # Показываем детали непустых записей
                    for idx, (row_num, row) in enumerate(non_empty_rows[:3]):
                        print(f"\n   📄 Запись #{row_num}:")
                        print(f"      Размер: {len(row._row_bytes)} байт")
                        print(f"      Данные: {row._row_bytes[:100].hex()}")
                        
                        # Показываем все поля с данными
                        print(f"      📝 Поля с данными:")
                        for field_name in table.fields.keys():
                            try:
                                value = row[field_name]
                                if value is not None and str(value).strip():
                                    print(f"         {field_name}: {value}")
                            except Exception as e:
                                pass
                    
                    # Ищем ключевые слова в данных
                    print(f"\n   🔍 Поиск ключевых слов:")
                    keywords = ['цвет', 'rose', 'tulip', 'flower', 'товар', 'номенклатура', 'наименование', 'описание']
                    found_keywords = []
                    
                    for row_num, row in non_empty_rows[:5]:
                        for field_name in table.fields.keys():
                            try:
                                value = row[field_name]
                                if value and isinstance(value, str):
                                    for keyword in keywords:
                                        if keyword.lower() in value.lower():
                                            found_keywords.append((row_num, field_name, keyword, value))
                            except:
                                pass
                    
                    if found_keywords:
                        print(f"      ✅ Найдены ключевые слова:")
                        for row_num, field_name, keyword, value in found_keywords[:3]:
                            print(f"         Строка {row_num}, поле {field_name}: '{keyword}' в '{value[:100]}...'")
                    else:
                        print(f"      ❌ Ключевые слова не найдены")
                    
                    if idx >= 2:  # Показываем только первые 3 таблицы
                        break
                        
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_real_data()
    print("\n✅ Анализ завершен") 