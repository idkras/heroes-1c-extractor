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
                if content and len(str(content)) > 0:
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

def final_blob_analysis():
    """
    Финальный анализ BLOB данных в журналах документов
    """
    print("🔍 Финальный анализ BLOB данных")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'blob_analysis': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_journals_analyzed': 0,
                    'blob_fields_found': 0,
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # Ищем журналы документов
            journal_tables = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        journal_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            journal_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Найдено {len(journal_tables)} журналов документов")
            print(f"🔍 Анализируем первые 5 больших журналов...")
            
            # Анализируем первые 5 больших журналов
            for table_name, record_count in journal_tables[:5]:
                print(f"\n📋 Анализ журнала: {table_name}")
                print(f"📊 Записей: {record_count:,}")
                
                table = db.tables[table_name]
                
                # Анализируем первые 10 записей
                sample_records = []
                for i in range(min(10, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            row_data = row.as_dict()
                            sample_records.append(row_data)
                    except Exception as e:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                if sample_records:
                    print(f"    ✅ Прочитано {len(sample_records)} записей")
                    
                    # Анализируем поля
                    fields = list(sample_records[0].keys())
                    print(f"    📋 Поля: {len(fields)}")
                    
                    # Ищем BLOB поля
                    blob_fields = []
                    for field in fields:
                        if field.startswith('_FLD'):
                            # Проверяем, есть ли BLOB данные в этом поле
                            for record in sample_records[:3]:
                                if field in record:
                                    value = record[field]
                                    if hasattr(value, 'value') or hasattr(value, '__iter__'):
                                        blob_fields.append(field)
                                        break
                    
                    if blob_fields:
                        print(f"    🔗 BLOB поля: {len(blob_fields)}")
                        print(f"      Найдены: {blob_fields[:5]}")
                        
                        # Анализируем содержимое BLOB полей
                        blob_contents = {}
                        for blob_field in blob_fields[:5]:  # Анализируем первые 5 BLOB полей
                            print(f"      📄 Анализ {blob_field}:")
                            contents = []
                            
                            for i, record in enumerate(sample_records[:5]):
                                try:
                                    value = record[blob_field]
                                    content = safe_get_blob_content(value)
                                    if content and content != "None" and len(content) > 0:
                                        contents.append(content)
                                        print(f"        Запись {i+1}: {content[:100]}...")
                                except Exception as e:
                                    print(f"        ⚠️ Ошибка чтения {blob_field}: {e}")
                            
                            if contents:
                                blob_contents[blob_field] = contents
                        
                        # Ищем ключевые слова в BLOB содержимом
                        keywords = ['товар', 'номенклатура', 'количество', 'цена', 'склад', 'подразделение', 
                                  'поставщик', 'покупатель', 'цвет', 'цветы', 'розы', 'тюльпаны']
                        
                        found_keywords = {}
                        for keyword in keywords:
                            found_keywords[keyword] = []
                            for field, contents in blob_contents.items():
                                for content in contents:
                                    if keyword.lower() in content.lower():
                                        found_keywords[keyword].append((field, content[:200]))
                        
                        # Выводим найденные ключевые слова
                        if any(found_keywords.values()):
                            print(f"      🎯 Найденные ключевые слова:")
                            for keyword, matches in found_keywords.items():
                                if matches:
                                    print(f"        - {keyword}: {len(matches)} совпадений")
                                    for field, content in matches[:2]:  # Показываем первые 2 совпадения
                                        print(f"          {field}: {content}")
                        
                        # Сохраняем результаты
                        results['blob_analysis'][table_name] = {
                            'record_count': record_count,
                            'fields': fields,
                            'blob_fields': blob_fields,
                            'blob_contents': blob_contents,
                            'found_keywords': found_keywords,
                            'sample_records': sample_records[:2]  # Сохраняем первые 2 записи
                        }
                        
                        results['metadata']['total_journals_analyzed'] += 1
                        results['metadata']['blob_fields_found'] += len(blob_fields)
                    else:
                        print(f"    ⚠️ BLOB поля не найдены")
            
            # Сохраняем результаты
            output_file = 'final_blob_analysis.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в {output_file}")
            print(f"📊 Проанализировано журналов: {results['metadata']['total_journals_analyzed']}")
            print(f"📊 Найдено BLOB полей: {results['metadata']['blob_fields_found']}")
            
            # Выводим краткую сводку
            print(f"\n📋 КРАТКАЯ СВОДКА BLOB АНАЛИЗА:")
            for table_name, data in results['blob_analysis'].items():
                if data['found_keywords']:
                    print(f"  📄 {table_name}:")
                    for keyword, matches in data['found_keywords'].items():
                        if matches:
                            print(f"    - {keyword}: {len(matches)} совпадений")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    final_blob_analysis() 