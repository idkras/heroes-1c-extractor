#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def safe_get_blob_content(value):
    """
    Безопасное извлечение содержимого BLOB поля
    """
    try:
        if hasattr(value, 'value'):
            content = value.value
            if content and len(str(content)) > 0:
                return str(content)
        elif hasattr(value, '__iter__'):
            try:
                iterator = iter(value)
                content = next(iterator)
                if content and len(content) > 0:
                    return str(content)
            except StopIteration:
                pass
        elif hasattr(value, '__bytes__'):
            try:
                content = bytes(value)
                if content and len(content) > 0:
                    return str(content)
            except:
                pass
    except Exception as e:
        return f"Ошибка чтения BLOB: {e}"
    
    return None

def analyze_new_found_documents():
    """
    Анализ новых найденных документов для JTBD сценариев
    ЦЕЛЬ: Понять назначение _DOCUMENT9490_VT9494 (цвета) и _DOCUMENT163 (склады)
    """
    print("🔍 АНАЛИЗ НОВЫХ НАЙДЕННЫХ ДОКУМЕНТОВ")
    print("🎯 ЦЕЛЬ: JTBD сценарии - цвета, склады, магазины")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'document9490_vt9494_analysis': {},
                'document163_analysis': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # 1. АНАЛИЗ _DOCUMENT9490_VT9494 (ЦВЕТА)
            print("\n🔍 ЭТАП 1: Анализ _DOCUMENT9490_VT9494 (цвета)")
            print("-" * 60)
            
            table_name = '_DOCUMENT9490_VT9494'
            if table_name in db.tables:
                table = db.tables[table_name]
                record_count = len(table)
                print(f"📊 Найдено записей: {record_count:,}")
                
                # Ключевые слова для поиска цветов
                color_keywords = [
                    'розовый', 'голубой', 'красный', 'белый', 'желтый', 'синий',
                    'черный', 'зеленый', 'оранжевый', 'фиолетовый', 'цвет', 'цветок'
                ]
                
                # Анализируем первые 100 записей для поиска цветов
                print(f"\n🔍 Анализируем первые 100 записей для поиска цветов...")
                
                color_records = []
                found_colors = set()
                
                for i in range(min(100, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            row_data = row.as_dict()
                            
                            # Ищем ключевые слова в BLOB полях
                            for field_name, field_value in row_data.items():
                                if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    content = safe_get_blob_content(field_value)
                                    if content and len(content) > 10:
                                        # Ищем цвета
                                        for color in color_keywords:
                                            if color.lower() in content.lower():
                                                found_colors.add(color)
                                                if len(color_records) < 20:  # Ограничиваем 20 записями
                                                    color_records.append({
                                                        'record_index': i,
                                                        'field_name': field_name,
                                                        'content': content[:300],
                                                        'found_color': color
                                                    })
                            
                            # Ищем в обычных полях
                            for field_name, field_value in row_data.items():
                                if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    field_str = str(field_value).lower()
                                    for color in color_keywords:
                                        if color.lower() in field_str:
                                            found_colors.add(color)
                                            if len(color_records) < 20:
                                                color_records.append({
                                                    'record_index': i,
                                                    'field_name': field_name,
                                                    'content': str(field_value),
                                                    'found_color': color
                                                })
                    
                    except Exception as e:
                        continue
                
                # Показываем найденные цвета
                print(f"\n🎨 НАЙДЕННЫЕ ЦВЕТА: {', '.join(sorted(found_colors))}")
                print(f"📊 Найдено записей с цветами: {len(color_records)}")
                
                # Показываем образцы записей с цветами
                if color_records:
                    print(f"\n🔍 ОБРАЗЦЫ ЗАПИСЕЙ С ЦВЕТАМИ:")
                    for j, record in enumerate(color_records[:5]):
                        print(f"    📄 Запись {j+1} (индекс {record['record_index']}):")
                        print(f"        🎨 Цвет: {record['found_color']}")
                        print(f"        📋 Поле: {record['field_name']}")
                        print(f"        📋 Содержимое: {record['content']}...")
                        print()
                
                # Анализируем структуру полей
                if len(table) > 0:
                    try:
                        first_record = table[0]
                        if not first_record.is_empty:
                            first_record_data = first_record.as_dict()
                            
                            print(f"📋 СТРУКТУРА ПОЛЕЙ:")
                            print(f"    📊 Всего полей: {len(first_record_data)}")
                            
                            # Показываем первые 15 полей
                            for i, (field_name, field_value) in enumerate(list(first_record_data.items())[:15]):
                                field_type = "BLOB" if str(field_value).startswith('<onec_dtools.database_reader.Blob') else "Обычное"
                                print(f"    {i+1:2d}. {field_name} ({field_type}): {field_value}")
                            
                            # Сохраняем структуру полей
                            fields_structure = {
                                'total_fields': len(first_record_data),
                                'field_names': list(first_record_data.keys()),
                                'field_types': {name: "BLOB" if str(val).startswith('<onec_dtools.database_reader.Blob') else "Обычное" 
                                              for name, val in first_record_data.items()}
                            }
                            
                            results['document9490_vt9494_analysis']['fields_structure'] = fields_structure
                            
                    except Exception as e:
                        print(f"    ⚠️ Ошибка анализа структуры полей: {e}")
                
                # Сохраняем результаты анализа
                results['document9490_vt9494_analysis']['record_count'] = record_count
                results['document9490_vt9494_analysis']['found_colors'] = list(found_colors)
                results['document9490_vt9494_analysis']['color_records'] = color_records
                
            else:
                print(f"❌ Таблица {table_name} не найдена!")
            
            # 2. АНАЛИЗ _DOCUMENT163 (СКЛАДЫ)
            print(f"\n🔍 ЭТАП 2: Анализ _DOCUMENT163 (склады)")
            print("-" * 60)
            
            table_name = '_DOCUMENT163'
            if table_name in db.tables:
                table = db.tables[table_name]
                record_count = len(table)
                print(f"📊 Найдено записей: {record_count:,}")
                
                # Ключевые слова для поиска складов и магазинов
                warehouse_keywords = [
                    'склад', 'магазин', 'братиславский', '045', 'подразделение',
                    'яндекс маркет', 'яндекс директ', 'яндекс-еда', 'интернет магазин'
                ]
                
                # Анализируем первые 100 записей для поиска складов
                print(f"\n🔍 Анализируем первые 100 записей для поиска складов...")
                
                warehouse_records = []
                found_warehouses = set()
                
                for i in range(min(100, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            row_data = row.as_dict()
                            
                            # Ищем ключевые слова в BLOB полях
                            for field_name, field_value in row_data.items():
                                if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    content = safe_get_blob_content(field_value)
                                    if content and len(content) > 10:
                                        # Ищем склады
                                        for warehouse in warehouse_keywords:
                                            if warehouse.lower() in content.lower():
                                                found_warehouses.add(warehouse)
                                                if len(warehouse_records) < 20:
                                                    warehouse_records.append({
                                                        'record_index': i,
                                                        'field_name': field_name,
                                                        'content': content[:300],
                                                        'found_warehouse': warehouse
                                                    })
                            
                            # Ищем в обычных полях
                            for field_name, field_value in row_data.items():
                                if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    field_str = str(field_value).lower()
                                    for warehouse in warehouse_keywords:
                                        if warehouse.lower() in field_str:
                                            found_warehouses.add(warehouse)
                                            if len(warehouse_records) < 20:
                                                warehouse_records.append({
                                                    'record_index': i,
                                                    'field_name': field_name,
                                                    'content': str(field_value),
                                                    'found_warehouse': warehouse
                                                })
                    
                    except Exception as e:
                        continue
                
                # Показываем найденные склады
                print(f"\n🏪 НАЙДЕННЫЕ СКЛАДЫ/МАГАЗИНЫ: {', '.join(sorted(found_warehouses))}")
                print(f"📊 Найдено записей со складами: {len(warehouse_records)}")
                
                # Показываем образцы записей со складами
                if warehouse_records:
                    print(f"\n🔍 ОБРАЗЦЫ ЗАПИСЕЙ СО СКЛАДАМИ:")
                    for j, record in enumerate(warehouse_records[:5]):
                        print(f"    📄 Запись {j+1} (индекс {record['record_index']}):")
                        print(f"        🏪 Склад: {record['found_warehouse']}")
                        print(f"        📋 Поле: {record['field_name']}")
                        print(f"        📋 Содержимое: {record['content']}...")
                        print()
                
                # Анализируем структуру полей
                if len(table) > 0:
                    try:
                        first_record = table[0]
                        if not first_record.is_empty:
                            first_record_data = first_record.as_dict()
                            
                            print(f"📋 СТРУКТУРА ПОЛЕЙ:")
                            print(f"    📊 Всего полей: {len(first_record_data)}")
                            
                            # Показываем первые 15 полей
                            for i, (field_name, field_value) in enumerate(list(first_record_data.items())[:15]):
                                field_type = "BLOB" if str(field_value).startswith('<onec_dtools.database_reader.Blob') else "Обычное"
                                print(f"    {i+1:2d}. {field_name} ({field_type}): {field_value}")
                            
                            # Сохраняем структуру полей
                            fields_structure = {
                                'total_fields': len(first_record_data),
                                'field_names': list(first_record_data.keys()),
                                'field_types': {name: "BLOB" if str(val).startswith('<onec_dtools.database_reader.Blob') else "Обычное" 
                                              for name, val in first_record_data.items()}
                            }
                            
                            results['document163_analysis']['fields_structure'] = fields_structure
                            
                    except Exception as e:
                        print(f"    ⚠️ Ошибка анализа структуры полей: {e}")
                
                # Сохраняем результаты анализа
                results['document163_analysis']['record_count'] = record_count
                results['document163_analysis']['found_warehouses'] = list(found_warehouses)
                results['document163_analysis']['warehouse_records'] = warehouse_records
                
            else:
                print(f"❌ Таблица {table_name} не найдена!")
            
            # Сохраняем все результаты
            with open('new_found_documents_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в new_found_documents_analysis.json")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_new_found_documents()






