#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def analyze_document_journals():
    """
    Анализ журналов документов для поиска информации о товарах
    """
    print("🔍 Анализ журналов документов")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Критерии поиска товаров в журналах
            product_criteria = {
                'номенклатура': {
                    'keywords': ['номенклатура', 'товар', 'product', 'item', 'наименование', 'название'],
                    'expected_fields': ['код', 'наименование', 'вид', 'группа']
                },
                'количество': {
                    'keywords': ['количество', 'к-во', 'qty', 'amount', 'кол-во'],
                    'expected_fields': ['количество', 'к-во', 'qty']
                },
                'цена': {
                    'keywords': ['цена', 'стоимость', 'price', 'cost', 'сумма'],
                    'expected_fields': ['цена', 'стоимость', 'сумма']
                },
                'склад': {
                    'keywords': ['склад', 'warehouse', 'store', 'место'],
                    'expected_fields': ['склад', 'место', 'location']
                },
                'подразделение': {
                    'keywords': ['подразделение', 'department', 'отдел', 'подраздел'],
                    'expected_fields': ['подразделение', 'отдел', 'department']
                }
            }
            
            results = {
                'journals_analyzed': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_journals_analyzed': 0,
                    'records_analyzed': 0,
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
            print(f"🔍 Анализируем первые 10 больших журналов...")
            
            # Анализируем первые 10 больших журналов
            for table_name, record_count in journal_tables[:10]:
                print(f"\n📋 Анализ журнала: {table_name}")
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
                    for product_type, criteria in product_criteria.items():
                        found_keywords[product_type] = []
                        for keyword in criteria['keywords']:
                            matching_fields = [f for f in fields if keyword.lower() in f.lower()]
                            if matching_fields:
                                found_keywords[product_type].extend(matching_fields)
                    
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
                    
                    # Классифицируем содержимое журнала
                    journal_classification = {}
                    for product_type, criteria in product_criteria.items():
                        score = 0
                        reasons = []
                        
                        # Проверяем ключевые слова в полях
                        if found_keywords[product_type]:
                            score += len(found_keywords[product_type]) * 2
                            reasons.append(f"Найдены поля: {found_keywords[product_type]}")
                        
                        # Проверяем значения полей
                        for field, values in field_values.items():
                            for keyword in criteria['keywords']:
                                if any(keyword.lower() in str(value).lower() for value in values):
                                    score += 1
                                    reasons.append(f"Значение в поле {field}: {values}")
                        
                        if score > 0:
                            journal_classification[product_type] = {
                                'score': score,
                                'reasons': reasons,
                                'matching_fields': found_keywords[product_type]
                            }
                    
                    # Выводим результаты классификации
                    if journal_classification:
                        print(f"    🎯 Классификация содержимого:")
                        for product_type, classification in journal_classification.items():
                            print(f"      📄 {product_type}: {classification['score']} баллов")
                            for reason in classification['reasons'][:2]:  # Показываем первые 2 причины
                                print(f"        - {reason}")
                    
                    # Анализируем простые поля
                    simple_fields = [f for f in fields if not f.startswith('_FLD')]
                    if simple_fields:
                        print(f"    📋 Простые поля: {len(simple_fields)}")
                        print(f"      Примеры: {simple_fields[:5]}")
                    
                    # Анализируем значения ключевых полей
                    key_fields = ['_DOCUMENT*_IDRREF', '_KEYFIELD', '_LINENO*', '_PERIOD']
                    for key_field in key_fields:
                        matching_fields = [f for f in fields if key_field.replace('*', '') in f]
                        if matching_fields:
                            for field in matching_fields[:3]:  # Показываем первые 3 поля
                                values = []
                                for record in sample_records[:3]:
                                    if field in record:
                                        value = record[field]
                                        if value is not None and str(value) != '':
                                            values.append(str(value))
                                if values:
                                    print(f"      {field}: {values}")
                    
                    # Ищем числовые поля (количество, цены)
                    numeric_fields = []
                    for field in fields:
                        if any(keyword in field.lower() for keyword in ['количество', 'к-во', 'цена', 'стоимость', 'сумма']):
                            numeric_fields.append(field)
                    
                    if numeric_fields:
                        print(f"    🔢 Числовые поля: {numeric_fields}")
                        
                        # Анализируем значения числовых полей
                        for field in numeric_fields[:3]:  # Анализируем первые 3 числовых поля
                            values = []
                            for record in sample_records[:5]:
                                if field in record:
                                    value = record[field]
                                    if value is not None and str(value) != '':
                                        values.append(str(value))
                            if values:
                                print(f"      {field}: {values}")
                    
                    # Сохраняем результаты
                    results['journals_analyzed'][table_name] = {
                        'record_count': record_count,
                        'fields': fields,
                        'simple_fields': simple_fields,
                        'journal_classification': journal_classification,
                        'field_values': field_values,
                        'numeric_fields': numeric_fields,
                        'sample_records': sample_records[:3]  # Сохраняем первые 3 записи
                    }
                    
                    results['metadata']['total_journals_analyzed'] += 1
                    results['metadata']['records_analyzed'] += len(sample_records)
            
            # Сохраняем результаты
            output_file = 'document_journals_analysis.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в {output_file}")
            print(f"📊 Проанализировано журналов: {results['metadata']['total_journals_analyzed']}")
            print(f"📊 Проанализировано записей: {results['metadata']['records_analyzed']}")
            
            # Выводим краткую сводку
            print(f"\n📋 КРАТКАЯ СВОДКА ЖУРНАЛОВ:")
            for table_name, data in results['journals_analyzed'].items():
                if data['journal_classification']:
                    print(f"  📄 {table_name}:")
                    for product_type, classification in data['journal_classification'].items():
                        print(f"    - {product_type}: {classification['score']} баллов")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_document_journals() 