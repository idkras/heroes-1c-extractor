#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def analyze_flowers_data():
    """
    Детальный анализ таблицы _REFERENCE66 с данными о цветах
    """
    print("🔍 Детальный анализ таблицы _REFERENCE66 с данными о цветах")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Анализируем таблицу _REFERENCE66
            table_name = '_REFERENCE66'
            
            if table_name in db.tables:
                table = db.tables[table_name]
                print(f"\n📊 Анализ таблицы: {table_name}")
                print(f"   📈 Всего записей: {len(table):,}")
                
                # Показываем структуру таблицы
                print(f"\n📝 Структура полей:")
                for field_name, field_desc in table.fields.items():
                    print(f"   - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Находим непустые записи
                non_empty_rows = []
                for i in range(min(100, len(table))):
                    row = table[i]
                    if not row.is_empty:
                        non_empty_rows.append((i, row))
                
                print(f"\n✅ Найдено {len(non_empty_rows)} непустых записей в первых 100:")
                
                # Анализируем непустые записи
                for idx, (row_num, row) in enumerate(non_empty_rows[:20]):
                    print(f"\n📄 Запись #{row_num}:")
                    print(f"   Размер: {len(row._row_bytes)} байт")
                    
                    # Показываем все поля с данными
                    print(f"   📝 Поля с данными:")
                    for field_name in table.fields.keys():
                        try:
                            value = row[field_name]
                            if value is not None and str(value).strip():
                                print(f"      {field_name}: {value}")
                        except Exception as e:
                            pass
                
                # Ищем ключевые слова в данных
                print(f"\n🔍 Поиск ключевых слов:")
                keywords = ['цвет', 'rose', 'tulip', 'flower', 'товар', 'номенклатура', 'наименование', 'описание', 'роза', 'калла', 'гимнокалициум']
                found_keywords = []
                
                for row_num, row in non_empty_rows[:50]:
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
                    print(f"   ✅ Найдены ключевые слова:")
                    for row_num, field_name, keyword, value in found_keywords[:10]:
                        print(f"      Строка {row_num}, поле {field_name}: '{keyword}' в '{value[:100]}...'")
                else:
                    print(f"   ❌ Ключевые слова не найдены")
                
                # Анализируем связи с другими таблицами
                print(f"\n🔗 Анализ связей:")
                rref_fields = []
                for field_name in table.fields.keys():
                    if 'RREF' in field_name:
                        rref_fields.append(field_name)
                
                if rref_fields:
                    print(f"   📋 RREF поля (ссылки на другие таблицы):")
                    for field_name in rref_fields:
                        print(f"      - {field_name}")
                    
                    # Показываем примеры RREF значений
                    print(f"   📄 Примеры RREF значений:")
                    for row_num, row in non_empty_rows[:3]:
                        print(f"      Запись #{row_num}:")
                        for field_name in rref_fields:
                            try:
                                value = row[field_name]
                                if value:
                                    print(f"         {field_name}: {value}")
                            except:
                                pass
                
            else:
                print(f"❌ Таблица {table_name} не найдена")
                
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_flowers_data()
    print("\n✅ Анализ завершен") 