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

def analyze_documents_robust():
    """
    Надежный анализ документов с улучшенной обработкой ошибок
    """
    print("🔍 Надежный анализ документов")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Критерии поиска документов
            search_criteria = {
                'поступления': {
                    'conditions': ['Проведён = Истина', 'СкладОрдер = Центральный склад', 'НомерМашины заполнено'],
                    'keywords': ['поступление', 'приход', 'поставщик', 'машина', 'склад', 'поставка']
                },
                'реализации': {
                    'conditions': ['Проведён = Истина', 'Сделка заполнено', 'Статус = Отгружен'],
                    'keywords': ['реализация', 'продажа', 'сделка', 'отгрузка', 'розница', 'продаж']
                },
                'отчеты_розничных_продаж': {
                    'conditions': ['Проведён = Истина'],
                    'keywords': ['отчет', 'розничн', 'продаж', 'орп', 'розница']
                },
                'чеки_ккм': {
                    'conditions': ['Проведён = Истина', 'Статус чека ККМ = Пробитый'],
                    'keywords': ['чек', 'ккм', 'касса', 'розничн', 'кассовый']
                },
                'перемещения': {
                    'conditions': ['Проведён = Истина', 'СкладОтправитель = Центральный склад', 'СкладПолучатель = Интернет-магазин'],
                    'keywords': ['перемещение', 'отправитель', 'получатель', 'склад', 'перемещ']
                },
                'списания': {
                    'conditions': ['Проведён = Истина', 'Склад.ВидСклада = Розничный'],
                    'keywords': ['списание', 'розничн', 'склад', 'списыв']
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
            print(f"🔍 Анализируем первые 8 больших таблиц...")
            
            # Анализируем первые 8 больших таблиц
            for table_name, record_count in document_tables[:8]:
                print(f"\n📋 Анализ таблицы: {table_name}")
                print(f"📊 Записей: {record_count:,}")
                
                table = db.tables[table_name]
                
                # Анализируем первые 15 записей для классификации
                sample_records = []
                for i in range(min(15, len(table))):
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
                    
                    # Ищем поля с условиями
                    found_conditions = {}
                    for doc_type, criteria in search_criteria.items():
                        found_conditions[doc_type] = []
                        for condition in criteria['conditions']:
                            # Ищем поля, которые могут соответствовать условиям
                            for field in fields:
                                if any(keyword.lower() in field.lower() for keyword in condition.lower().split()):
                                    found_conditions[doc_type].append((condition, field))
                    
                    # Анализируем значения полей
                    field_values = {}
                    for field in fields[:8]:  # Анализируем первые 8 полей
                        values = []
                        for record in sample_records[:5]:  # Берем первые 5 записей
                            if field in record:
                                value = record[field]
                                if value is not None and str(value) != '':
                                    values.append(str(value))
                        if values:
                            field_values[field] = list(set(values))[:5]  # Уникальные значения
                    
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
                    
                    # Классифицируем документы
                    document_classification = {}
                    for doc_type, criteria in search_criteria.items():
                        score = 0
                        reasons = []
                        
                        # Проверяем ключевые слова в полях
                        if found_keywords[doc_type]:
                            score += len(found_keywords[doc_type]) * 2
                            reasons.append(f"Найдены поля: {found_keywords[doc_type]}")
                        
                        # Проверяем условия
                        if found_conditions[doc_type]:
                            score += len(found_conditions[doc_type]) * 3
                            reasons.append(f"Найдены условия: {[c[0] for c in found_conditions[doc_type]]}")
                        
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
                                'matching_fields': found_keywords[doc_type],
                                'matching_conditions': found_conditions[doc_type]
                            }
                    
                    # Выводим результаты классификации
                    if document_classification:
                        print(f"    🎯 Классификация документов:")
                        for doc_type, classification in document_classification.items():
                            print(f"      📄 {doc_type}: {classification['score']} баллов")
                            for reason in classification['reasons'][:2]:  # Показываем первые 2 причины
                                print(f"        - {reason}")
                    
                    # Анализируем BLOB поля
                    if blob_fields:
                        print(f"    🔗 BLOB поля: {blob_fields}")
                        
                        # Анализируем содержимое BLOB полей
                        for blob_field in blob_fields[:2]:  # Анализируем первые 2 BLOB поля
                            print(f"      📄 Анализ {blob_field}:")
                            for i, record in enumerate(sample_records[:3]):
                                try:
                                    value = record[blob_field]
                                    content = safe_get_blob_content(value)
                                    if content:
                                        print(f"        Запись {i+1}: {content[:100]}...")
                                except Exception as e:
                                    print(f"        ⚠️ Ошибка чтения {blob_field}: {e}")
                    
                    # Сохраняем результаты
                    results['documents_found'][table_name] = {
                        'record_count': record_count,
                        'fields': fields,
                        'document_classification': document_classification,
                        'blob_fields': blob_fields,
                        'field_values': field_values,
                        'sample_records': sample_records[:2]  # Сохраняем первые 2 записи
                    }
                    
                    results['metadata']['total_tables_analyzed'] += 1
                    results['metadata']['documents_analyzed'] += len(sample_records)
            
            # Сохраняем результаты
            output_file = 'robust_documents_analysis.json'
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
    analyze_documents_robust() 