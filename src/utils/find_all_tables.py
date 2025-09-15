#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def find_all_tables():
    """
    Поиск всех таблиц и их классификация
    """
    print("🔍 Поиск всех таблиц")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Общее количество таблиц: {len(db.tables)}")
            
            # Классификация таблиц
            table_categories = {
                'documents': [],
                'references': [],
                'journals': [],
                'registers': [],
                'other': []
            }
            
            # Анализируем все таблицы
            for table_name in db.tables.keys():
                table = db.tables[table_name]
                record_count = len(table)
                
                # Классифицируем таблицы
                if '_DOCUMENT' in table_name:
                    if '_VT' in table_name:
                        table_categories['journals'].append((table_name, record_count))
                    else:
                        table_categories['documents'].append((table_name, record_count))
                elif '_Reference' in table_name:
                    table_categories['references'].append((table_name, record_count))
                elif '_AccumRGT' in table_name or '_InfoRGT' in table_name:
                    table_categories['registers'].append((table_name, record_count))
                else:
                    table_categories['other'].append((table_name, record_count))
            
            # Сортируем по размеру
            for category in table_categories:
                table_categories[category].sort(key=lambda x: x[1], reverse=True)
            
            # Выводим результаты
            print(f"\n📋 КЛАССИФИКАЦИЯ ТАБЛИЦ:")
            
            print(f"\n📄 ДОКУМЕНТЫ ({len(table_categories['documents'])} таблиц):")
            for i, (table_name, record_count) in enumerate(table_categories['documents'][:10]):
                print(f"  {i+1}. {table_name} ({record_count:,} записей)")
            
            print(f"\n📋 СПРАВОЧНИКИ ({len(table_categories['references'])} таблиц):")
            for i, (table_name, record_count) in enumerate(table_categories['references'][:10]):
                print(f"  {i+1}. {table_name} ({record_count:,} записей)")
            
            print(f"\n📊 ЖУРНАЛЫ ({len(table_categories['journals'])} таблиц):")
            for i, (table_name, record_count) in enumerate(table_categories['journals'][:10]):
                print(f"  {i+1}. {table_name} ({record_count:,} записей)")
            
            print(f"\n📈 РЕГИСТРЫ ({len(table_categories['registers'])} таблиц):")
            for i, (table_name, record_count) in enumerate(table_categories['registers'][:10]):
                print(f"  {i+1}. {table_name} ({record_count:,} записей)")
            
            print(f"\n🔍 ПРОЧИЕ ({len(table_categories['other'])} таблиц):")
            for i, (table_name, record_count) in enumerate(table_categories['other'][:10]):
                print(f"  {i+1}. {table_name} ({record_count:,} записей)")
            
            # Анализируем первые 5 больших таблиц каждого типа
            results = {
                'table_categories': table_categories,
                'sample_analysis': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_tables': len(db.tables),
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # Анализируем образцы таблиц
            for category, tables in table_categories.items():
                if tables:
                    print(f"\n🔍 АНАЛИЗ ОБРАЗЦОВ {category.upper()}:")
                    
                    sample_analysis = []
                    for table_name, record_count in tables[:3]:  # Анализируем первые 3 таблицы
                        print(f"\n📋 Анализ таблицы: {table_name}")
                        print(f"📊 Записей: {record_count:,}")
                        
                        table = db.tables[table_name]
                        
                        # Анализируем первые 5 записей
                        sample_records = []
                        for i in range(min(5, len(table))):
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
                            
                            # Простые поля
                            simple_fields = [f for f in fields if not f.startswith('_FLD')]
                            print(f"    📋 Простые поля: {len(simple_fields)}")
                            if simple_fields:
                                print(f"      Примеры: {simple_fields[:5]}")
                            
                            # Анализируем значения ключевых полей
                            key_fields = ['_IDRREF', '_VERSION', '_MARKED', '_DATE_TIME', '_CODE', '_DESCRIPTION', '_NUMBER', '_POSTED']
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
                            
                            sample_analysis.append({
                                'table_name': table_name,
                                'record_count': record_count,
                                'fields': fields,
                                'simple_fields': simple_fields,
                                'sample_records': sample_records[:2]
                            })
                    
                    results['sample_analysis'][category] = sample_analysis
            
            # Сохраняем результаты
            output_file = 'all_tables_analysis.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в {output_file}")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    find_all_tables() 