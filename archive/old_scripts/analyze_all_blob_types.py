#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def analyze_all_blob_types():
    """
    Анализ всех типов BLOB данных и их извлечение
    """
    print("🔍 Анализ всех типов BLOB данных")
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
                
                # Находим первую непустую запись
                row = None
                for i in range(min(100, len(table))):
                    current_row = table[i]
                    if not current_row.is_empty:
                        row = current_row
                        print(f"   ✅ Найдена запись #{i}")
                        break
                
                if row is not None:
                    row_dict = row.as_dict()
                    print(f"\n🔍 Анализ всех BLOB полей:")
                    
                    blob_analysis = {}
                    
                    for field_name, value in row_dict.items():
                        if hasattr(value, '__class__') and 'Blob' in str(value.__class__):
                            print(f"\n📊 Поле {field_name}:")
                            
                            # Анализируем структуру
                            blob_info = {
                                'field_name': field_name,
                                'type': type(value).__name__,
                                'field_type': getattr(value, '_field_type', 'unknown'),
                                'size': getattr(value, '_size', 0),
                                'has_value': hasattr(value, 'value'),
                                'value_type': type(getattr(value, 'value', None)).__name__ if hasattr(value, 'value') else None,
                                'extraction_methods': []
                            }
                            
                            print(f"   Тип поля: {blob_info['field_type']}")
                            print(f"   Размер: {blob_info['size']}")
                            print(f"   Есть value: {blob_info['has_value']}")
                            
                            # Пробуем разные методы извлечения
                            extraction_results = {}
                            
                            # Метод 1: value атрибут
                            if hasattr(value, 'value'):
                                try:
                                    content = value.value
                                    extraction_results['value'] = {
                                        'success': True,
                                        'content': content,
                                        'type': type(content).__name__,
                                        'length': len(content) if content else 0
                                    }
                                    blob_info['extraction_methods'].append('value')
                                    print(f"   ✅ value: '{content[:100]}{'...' if len(str(content)) > 100 else ''}'")
                                except Exception as e:
                                    extraction_results['value'] = {
                                        'success': False,
                                        'error': str(e)
                                    }
                                    print(f"   ❌ value: {e}")
                            
                            # Метод 2: __iter__
                            if hasattr(value, '__iter__'):
                                try:
                                    iterator = iter(value)
                                    content = next(iterator)
                                    extraction_results['iterator'] = {
                                        'success': True,
                                        'content': content,
                                        'type': type(content).__name__,
                                        'length': len(content) if content else 0
                                    }
                                    blob_info['extraction_methods'].append('iterator')
                                    print(f"   ✅ iterator: '{content[:100]}{'...' if len(str(content)) > 100 else ''}'")
                                except Exception as e:
                                    extraction_results['iterator'] = {
                                        'success': False,
                                        'error': str(e)
                                    }
                                    print(f"   ❌ iterator: {e}")
                            
                            # Метод 3: __bytes__
                            if hasattr(value, '__bytes__'):
                                try:
                                    content = bytes(value)
                                    extraction_results['bytes'] = {
                                        'success': True,
                                        'content': content,
                                        'type': type(content).__name__,
                                        'length': len(content) if content else 0
                                    }
                                    blob_info['extraction_methods'].append('bytes')
                                    print(f"   ✅ bytes: {content[:50].hex()}{'...' if len(content) > 50 else ''}")
                                except Exception as e:
                                    extraction_results['bytes'] = {
                                        'success': False,
                                        'error': str(e)
                                    }
                                    print(f"   ❌ bytes: {e}")
                            
                            # Метод 4: __str__
                            try:
                                content = str(value)
                                if content != repr(value):  # Не просто repr
                                    extraction_results['str'] = {
                                        'success': True,
                                        'content': content,
                                        'type': type(content).__name__,
                                        'length': len(content) if content else 0
                                    }
                                    blob_info['extraction_methods'].append('str')
                                    print(f"   ✅ str: '{content[:100]}{'...' if len(content) > 100 else ''}'")
                                else:
                                    extraction_results['str'] = {
                                        'success': False,
                                        'error': 'Same as repr'
                                    }
                                    print(f"   ❌ str: Same as repr")
                            except Exception as e:
                                extraction_results['str'] = {
                                    'success': False,
                                    'error': str(e)
                                }
                                print(f"   ❌ str: {e}")
                            
                            # Метод 5: __len__ + __getitem__
                            if hasattr(value, '__len__') and hasattr(value, '__getitem__'):
                                try:
                                    content = value[0] if len(value) > 0 else None
                                    extraction_results['index'] = {
                                        'success': True,
                                        'content': content,
                                        'type': type(content).__name__,
                                        'length': len(content) if content else 0
                                    }
                                    blob_info['extraction_methods'].append('index')
                                    print(f"   ✅ index: '{content[:100]}{'...' if len(str(content)) > 100 else ''}'")
                                except Exception as e:
                                    extraction_results['index'] = {
                                        'success': False,
                                        'error': str(e)
                                    }
                                    print(f"   ❌ index: {e}")
                            
                            blob_info['extraction_results'] = extraction_results
                            blob_analysis[field_name] = blob_info
                    
                    # Сохраняем анализ
                    analysis_file = 'blob_analysis.json'
                    with open(analysis_file, 'w', encoding='utf-8') as f:
                        json.dump(blob_analysis, f, ensure_ascii=False, indent=2, default=str)
                    
                    print(f"\n💾 Анализ сохранен в: {analysis_file}")
                    
                    # Показываем статистику
                    print(f"\n📊 Статистика анализа BLOB:")
                    print(f"   - Всего BLOB полей: {len(blob_analysis)}")
                    
                    successful_extractions = 0
                    for field_name, info in blob_analysis.items():
                        if info['extraction_methods']:
                            successful_extractions += 1
                            print(f"   ✅ {field_name}: {', '.join(info['extraction_methods'])}")
                        else:
                            print(f"   ❌ {field_name}: не удалось извлечь")
                    
                    print(f"   - Успешно извлечено: {successful_extractions}/{len(blob_analysis)}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    analyze_all_blob_types() 