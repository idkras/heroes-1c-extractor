#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os

def debug_row_structure():
    """
    Диагностика структуры объекта row
    """
    print("🔍 Диагностика структуры объекта row")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Анализируем таблицу _DOCUMENT13139_VT13257
            table_name = '_DOCUMENT13139_VT13257'
            
            if table_name in db.tables:
                table = db.tables[table_name]
                print(f"\n📊 Анализ таблицы: {table_name}")
                print(f"   📈 Всего записей: {len(table):,}")
                
                # Находим первую непустую запись
                row = None
                for i in range(min(100, len(table))):
                    current_row = table[i]
                    if not current_row.is_empty:
                        row = current_row
                        print(f"   ✅ Найдена непустая запись #{i}")
                        break
                
                if row is not None:
                    print(f"\n🔍 Анализ структуры row:")
                    print(f"   Тип объекта: {type(row)}")
                    print(f"   dir(row): {dir(row)}")
                    
                    # Проверяем атрибуты
                    print(f"\n📋 Атрибуты объекта:")
                    for attr in dir(row):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(row, attr)
                                print(f"      {attr}: {type(value)} = {value}")
                            except Exception as e:
                                print(f"      {attr}: Ошибка доступа - {e}")
                    
                    # Проверяем методы
                    print(f"\n🔧 Методы объекта:")
                    for attr in dir(row):
                        if not attr.startswith('_') and callable(getattr(row, attr)):
                            print(f"      {attr}()")
                    
                    # Пробуем получить данные через индексы
                    print(f"\n📊 Попытка доступа через индексы:")
                    try:
                        for i in range(20):  # Первые 20 полей
                            try:
                                value = row[i]
                                print(f"      row[{i}]: {type(value)} = {value}")
                            except Exception as e:
                                print(f"      row[{i}]: Ошибка - {e}")
                    except Exception as e:
                        print(f"      Ошибка при доступе через индексы: {e}")
                    
                    # Проверяем _data атрибут
                    print(f"\n📊 Проверка _data атрибута:")
                    if hasattr(row, '_data'):
                        print(f"      _data: {row._data}")
                        if hasattr(row._data, 'keys'):
                            for key in row._data.keys():
                                print(f"         {key}: {row._data[key]}")
                    else:
                        print(f"      _data: не найден")
                    
                    # Проверяем __dict__
                    print(f"\n📊 Проверка __dict__:")
                    if hasattr(row, '__dict__'):
                        print(f"      __dict__: {row.__dict__}")
                    else:
                        print(f"      __dict__: не найден")
                    
                    # Пробуем получить данные через table.fields
                    print(f"\n📊 Попытка доступа через table.fields:")
                    field_names = list(table.fields.keys())
                    for i, field_name in enumerate(field_names[:5]):  # Первые 5 полей
                        try:
                            # Пробуем разные способы
                            value = None
                            
                            # Способ 1: прямой доступ
                            if hasattr(row, field_name):
                                value = getattr(row, field_name)
                                print(f"      {field_name} (прямой): {value}")
                            
                            # Способ 2: через индексы
                            if value is None:
                                try:
                                    value = row[i]
                                    print(f"      {field_name} (индекс {i}): {value}")
                                except:
                                    pass
                            
                            # Способ 3: через _data
                            if value is None and hasattr(row, '_data'):
                                value = row._data.get(field_name)
                                print(f"      {field_name} (_data): {value}")
                            
                        except Exception as e:
                            print(f"      {field_name}: Ошибка - {e}")
                
                else:
                    print(f"   ❌ Непустые записи не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    debug_row_structure() 