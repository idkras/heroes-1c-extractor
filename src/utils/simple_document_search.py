#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def simple_document_search():
    """
    Простой поиск документов без анализа BLOB данных
    """
    print("🔍 Простой поиск документов")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Критерии поиска документов
            search_criteria = {
                'поступления': {
                    'keywords': ['поступление', 'приход', 'поставщик', 'машина', 'склад', 'поставка', 'поступл']
                },
                'реализации': {
                    'keywords': ['реализация', 'продажа', 'сделка', 'отгрузка', 'розница', 'продаж', 'реализ']
                },
                'отчеты_розничных_продаж': {
                    'keywords': ['отчет', 'розничн', 'продаж', 'орп', 'розница', 'отчет']
                },
                'чеки_ккм': {
                    'keywords': ['чек', 'ккм', 'касса', 'розничн', 'кассовый', 'чек']
                },
                'перемещения': {
                    'keywords': ['перемещение', 'отправитель', 'получатель', 'склад', 'перемещ', 'перемещ']
                },
                'списания': {
                    'keywords': ['списание', 'розничн', 'склад', 'списыв', 'списание']
                }
            }
            
            results = {
                'documents_found': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_tables_analyzed': 0,
                    'documents_analyzed': 0,
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # Ищем таблицы документов
            document_tables = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' not in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            document_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Найдено {len(document_tables)} таблиц документов")
            print(f"🔍 Анализируем первые 10 больших таблиц...")
            
            # Анализируем первые 10 больших таблиц
            for table_name, record_count in document_tables[:10]:
                print(f"\n📋 Анализ таблицы: {table_name}")
                print(f"📊 Записей: {record_count:,}")
                
                table = db.tables[table_name]
                
                # Анализируем первые 10 записей для классификации
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
                    
                    # Ищем поля с ключевыми словами
                    found_keywords = {}
                    for doc_type, criteria in search_criteria.items():
                        found_keywords[doc_type] = []
                        for keyword in criteria['keywords']:
                            matching_fields = [f for f in fields if keyword.lower() in f.lower()]
                            if matching_fields:
                                found_keywords[doc_type].extend(matching_fields)
                    
                    # Анализируем значения полей (только простые поля)
                    field_values = {}
                    for field in fields[:10]:  # Анализируем первые 10 полей
                        if not field.startswith('_FLD'):  # Исключаем BLOB поля
                            values = []
                            for record in sample_records[:5]:  # Берем первые 5 записей
                                if field in record:
                                    value = record[field]
                                    if value is not None and str(value) != '' and not hasattr(value, 'value'):
                                        values.append(str(value))
                            if values:
                                field_values[field] = list(set(values))[:5]  # Уникальные значения
                    
                    # Классифицируем документы
                    document_classification = {}
                    for doc_type, criteria in search_criteria.items():
                        score = 0
                        reasons = []
                        
                        # Проверяем ключевые слова в полях
                        if found_keywords[doc_type]:
                            score += len(found_keywords[doc_type]) * 2
                            reasons.append(f"Найдены поля: {found_keywords[doc_type]}")
                        
                        # Проверяем значения полей
                        for field, values in field_values.items():
                            for keyword in criteria['keywords']:
                                if any(keyword.lower() in str(value).lower() for value in values):
                                    score += 1
                                    reasons.append(f"Значение в поле {field}: {values}")
                        
                        if score > 0:
                            document_classification[doc_type] = {
                                'score': score,
                                'reasons': reasons,
                                'matching_fields': found_keywords[doc_type]
                            }
                    
                    # Выводим результаты классификации
                    if document_classification:
                        print(f"    🎯 Классификация документов:")
                        for doc_type, classification in document_classification.items():
                            print(f"      📄 {doc_type}: {classification['score']} баллов")
                            for reason in classification['reasons'][:2]:  # Показываем первые 2 причины
                                print(f"        - {reason}")
                    
                    # Анализируем простые поля
                    simple_fields = [f for f in fields if not f.startswith('_FLD')]
                    if simple_fields:
                        print(f"    📋 Простые поля: {len(simple_fields)}")
                        print(f"      Примеры: {simple_fields[:5]}")
                    
                    # Анализируем значения ключевых полей
                    key_fields = ['_NUMBER', '_DATE_TIME', '_POSTED', '_MARKED']
                    for key_field in key_fields:
                        if key_field in fields:
                            values = []
                            for record in sample_records[:3]:
                                if key_field in record:
                                    value = record[key_field]
                                    if value is not None and str(value) != '':
                                        values.append(str(value))
                            if values:
                                print(f"      {key_field}: {values}")
                    
                    # Сохраняем результаты
                    results['documents_found'][table_name] = {
                        'record_count': record_count,
                        'fields': fields,
                        'simple_fields': simple_fields,
                        'document_classification': document_classification,
                        'field_values': field_values,
                        'sample_records': sample_records[:2]  # Сохраняем первые 2 записи
                    }
                    
                    results['metadata']['total_tables_analyzed'] += 1
                    results['metadata']['documents_analyzed'] += len(sample_records)
            
            # Сохраняем результаты
            output_file = 'simple_documents_search.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в {output_file}")
            print(f"📊 Проанализировано таблиц: {results['metadata']['total_tables_analyzed']}")
            print(f"📊 Проанализировано документов: {results['metadata']['documents_analyzed']}")
            
            # Выводим краткую сводку
            print(f"\n📋 КРАТКАЯ СВОДКА:")
            for table_name, data in results['documents_found'].items():
                if data['document_classification']:
                    print(f"  📄 {table_name}:")
                    for doc_type, classification in data['document_classification'].items():
                        print(f"    - {doc_type}: {classification['score']} баллов")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    simple_document_search() 