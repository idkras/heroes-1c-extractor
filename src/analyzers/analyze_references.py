#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def analyze_references():
    """
    Анализ справочников (склады, подразделения, контрагенты)
    """
    print("🔍 Анализ справочников")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Критерии поиска справочников
            reference_criteria = {
                'склады': {
                    'keywords': ['склад', 'warehouse', 'store', 'склад'],
                    'expected_fields': ['название', 'код', 'вид', 'тип']
                },
                'подразделения': {
                    'keywords': ['подразделение', 'department', 'отдел', 'подраздел'],
                    'expected_fields': ['название', 'код', 'родитель', 'иерархия']
                },
                'контрагенты': {
                    'keywords': ['контрагент', 'counterparty', 'поставщик', 'покупатель'],
                    'expected_fields': ['название', 'код', 'инн', 'адрес']
                },
                'номенклатура': {
                    'keywords': ['номенклатура', 'товар', 'product', 'item'],
                    'expected_fields': ['название', 'код', 'вид', 'группа']
                },
                'кассы': {
                    'keywords': ['касса', 'ккт', 'cash', 'register'],
                    'expected_fields': ['номер', 'название', 'тип', 'склад']
                }
            }
            
            results = {
                'references_found': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_tables_analyzed': 0,
                    'references_analyzed': 0,
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # Ищем таблицы справочников
            reference_tables = []
            for table_name in db.tables.keys():
                if '_Reference' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        reference_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            reference_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Найдено {len(reference_tables)} справочников")
            print(f"🔍 Анализируем первые 15 больших справочников...")
            
            # Анализируем первые 15 больших справочников
            for table_name, record_count in reference_tables[:15]:
                print(f"\n📋 Анализ справочника: {table_name}")
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
                    for ref_type, criteria in reference_criteria.items():
                        found_keywords[ref_type] = []
                        for keyword in criteria['keywords']:
                            matching_fields = [f for f in fields if keyword.lower() in f.lower()]
                            if matching_fields:
                                found_keywords[ref_type].extend(matching_fields)
                    
                    # Анализируем значения полей (только простые поля)
                    field_values = {}
                    for field in fields[:8]:  # Анализируем первые 8 полей
                        if not field.startswith('_FLD'):  # Исключаем BLOB поля
                            values = []
                            for record in sample_records[:5]:  # Берем первые 5 записей
                                if field in record:
                                    value = record[field]
                                    if value is not None and str(value) != '' and not hasattr(value, 'value'):
                                        values.append(str(value))
                            if values:
                                field_values[field] = list(set(values))[:5]  # Уникальные значения
                    
                    # Классифицируем справочники
                    reference_classification = {}
                    for ref_type, criteria in reference_criteria.items():
                        score = 0
                        reasons = []
                        
                        # Проверяем ключевые слова в полях
                        if found_keywords[ref_type]:
                            score += len(found_keywords[ref_type]) * 2
                            reasons.append(f"Найдены поля: {found_keywords[ref_type]}")
                        
                        # Проверяем значения полей
                        for field, values in field_values.items():
                            for keyword in criteria['keywords']:
                                if any(keyword.lower() in str(value).lower() for value in values):
                                    score += 1
                                    reasons.append(f"Значение в поле {field}: {values}")
                        
                        if score > 0:
                            reference_classification[ref_type] = {
                                'score': score,
                                'reasons': reasons,
                                'matching_fields': found_keywords[ref_type]
                            }
                    
                    # Выводим результаты классификации
                    if reference_classification:
                        print(f"    🎯 Классификация справочника:")
                        for ref_type, classification in reference_classification.items():
                            print(f"      📄 {ref_type}: {classification['score']} баллов")
                            for reason in classification['reasons'][:2]:  # Показываем первые 2 причины
                                print(f"        - {reason}")
                    
                    # Анализируем простые поля
                    simple_fields = [f for f in fields if not f.startswith('_FLD')]
                    if simple_fields:
                        print(f"    📋 Простые поля: {len(simple_fields)}")
                        print(f"      Примеры: {simple_fields[:5]}")
                    
                    # Анализируем значения ключевых полей
                    key_fields = ['_IDRREF', '_VERSION', '_MARKED', '_DATE_TIME', '_CODE', '_DESCRIPTION']
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
                    results['references_found'][table_name] = {
                        'record_count': record_count,
                        'fields': fields,
                        'simple_fields': simple_fields,
                        'reference_classification': reference_classification,
                        'field_values': field_values,
                        'sample_records': sample_records[:2]  # Сохраняем первые 2 записи
                    }
                    
                    results['metadata']['total_tables_analyzed'] += 1
                    results['metadata']['references_analyzed'] += len(sample_records)
            
            # Сохраняем результаты
            output_file = 'references_analysis.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в {output_file}")
            print(f"📊 Проанализировано справочников: {results['metadata']['total_tables_analyzed']}")
            print(f"📊 Проанализировано записей: {results['metadata']['references_analyzed']}")
            
            # Выводим краткую сводку
            print(f"\n📋 КРАТКАЯ СВОДКА СПРАВОЧНИКОВ:")
            for table_name, data in results['references_found'].items():
                if data['reference_classification']:
                    print(f"  📄 {table_name}:")
                    for ref_type, classification in data['reference_classification'].items():
                        print(f"    - {ref_type}: {classification['score']} баллов")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_references() 