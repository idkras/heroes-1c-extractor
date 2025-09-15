#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os

def debug_blob_structure():
    """
    Диагностика структуры Blob объекта
    """
    print("🔍 Диагностика структуры Blob объекта")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Анализируем таблицу _DOCUMENT163
            table_name = '_DOCUMENT163'
            
            if table_name in db.tables:
                table = db.tables[table_name]
                print(f"\n📊 Анализ таблицы: {table_name}")
                print(f"   📈 Всего записей: {len(table):,}")
                
                # Находим первую непустую запись с BLOB
                row = None
                for i in range(min(100, len(table))):
                    current_row = table[i]
                    if not current_row.is_empty:
                        row_dict = current_row.as_dict()
                        for field_name, value in row_dict.items():
                            if hasattr(value, '__class__') and 'Blob' in str(value.__class__):
                                row = current_row
                                print(f"   ✅ Найдена запись #{i} с BLOB полем {field_name}")
                                break
                        if row:
                            break
                
                if row is not None:
                    row_dict = row.as_dict()
                    print(f"\n🔍 Анализ структуры Blob:")
                    
                    for field_name, value in row_dict.items():
                        if hasattr(value, '__class__') and 'Blob' in str(value.__class__):
                            print(f"\n📊 Поле {field_name}:")
                            print(f"   Тип объекта: {type(value)}")
                            print(f"   dir(blob): {dir(value)}")
                            
                            # Проверяем атрибуты
                            print(f"\n📋 Атрибуты объекта:")
                            for attr in dir(value):
                                if not attr.startswith('_'):
                                    try:
                                        attr_value = getattr(value, attr)
                                        print(f"      {attr}: {type(attr_value)} = {attr_value}")
                                    except Exception as e:
                                        print(f"      {attr}: Ошибка доступа - {e}")
                            
                            # Проверяем методы
                            print(f"\n🔧 Методы объекта:")
                            for attr in dir(value):
                                if not attr.startswith('_') and callable(getattr(value, attr)):
                                    print(f"      {attr}()")
                            
                            # Пробуем получить данные
                            print(f"\n📊 Попытка получения данных:")
                            try:
                                # Пробуем разные способы
                                if hasattr(value, 'data'):
                                    print(f"      value.data: {value.data}")
                                if hasattr(value, 'get_data'):
                                    print(f"      value.get_data(): {value.get_data()}")
                                if hasattr(value, 'read'):
                                    print(f"      value.read(): {value.read()}")
                                if hasattr(value, 'content'):
                                    print(f"      value.content: {value.content}")
                                if hasattr(value, 'bytes'):
                                    print(f"      value.bytes: {value.bytes}")
                                if hasattr(value, '__bytes__'):
                                    print(f"      bytes(value): {bytes(value)}")
                                if hasattr(value, '__str__'):
                                    print(f"      str(value): {str(value)}")
                                if hasattr(value, '__repr__'):
                                    print(f"      repr(value): {repr(value)}")
                            except Exception as e:
                                print(f"      Ошибка при получении данных: {e}")
                            
                            # Проверяем __dict__
                            print(f"\n📊 Проверка __dict__:")
                            if hasattr(value, '__dict__'):
                                print(f"      __dict__: {value.__dict__}")
                            else:
                                print(f"      __dict__: не найден")
                            
                            break
                
                else:
                    print(f"   ❌ BLOB поля не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    debug_blob_structure() 