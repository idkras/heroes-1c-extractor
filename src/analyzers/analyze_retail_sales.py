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

def analyze_retail_sales():
    """
    Детальный анализ документов "Отчет о розничных продажах"
    """
    print("🔍 Детальный анализ документов 'Отчет о розничных продажах'")
    print("🎯 ЦЕЛЬ: Извлечь данные о розничных продажах и качестве товаров")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'retail_sales_documents': [],
                'journal_analysis': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': 'raw/1Cv8.1CD',
                    'total_retail_documents': 0,
                    'total_journal_records': 0
                }
            }
            
            print("\n🔍 Этап 1: Анализ таблицы _DOCUMENT184 (Отчет о розничных продажах)")
            print("-" * 60)
            
            # Анализируем таблицу _DOCUMENT184
            if '_DOCUMENT184' in db.tables:
                table = db.tables['_DOCUMENT184']
                record_count = len(table)
                print(f"📊 Найдено записей: {record_count:,}")
                
                results['metadata']['total_retail_documents'] = record_count
                
                # Анализируем первые 20 записей
                sample_records = []
                for i in range(min(20, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            # Получаем данные записи
                            row_data = row.as_dict()
                            sample_records.append(row_data)
                            
                            print(f"    📄 Запись {i+1}:")
                            print(f"        📋 Номер: {row_data.get('_NUMBER', 'N/A')}")
                            print(f"        📅 Дата: {row_data.get('_DATE_TIME', 'N/A')}")
                            print(f"        ✅ Проведен: {row_data.get('_POSTED', 'N/A')}")
                            
                            # Ищем BLOB поля
                            blob_fields = []
                            for field_name, field_value in row_data.items():
                                if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    blob_fields.append(field_name)
                            
                            if blob_fields:
                                print(f"        🔍 BLOB поля: {blob_fields}")
                                
                                # Анализируем содержимое BLOB полей
                                for blob_field in blob_fields[:3]:  # Анализируем первые 3 BLOB поля
                                    try:
                                        blob_value = row_data[blob_field]
                                        content = safe_get_blob_content(blob_value)
                                        if content:
                                            print(f"        📋 {blob_field}: {content[:150]}...")
                                    except Exception as e:
                                        print(f"        ⚠️ Ошибка чтения BLOB {blob_field}: {e}")
                            
                            print()  # Пустая строка для разделения
                    
                    except Exception as e:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                # Сохраняем результаты анализа
                table_analysis = {
                    'table_name': '_DOCUMENT184',
                    'record_count': record_count,
                    'sample_records': sample_records,
                    'fields': list(sample_records[0].keys()) if sample_records else []
                }
                results['retail_sales_documents'].append(table_analysis)
                
                print(f"✅ Проанализировано {len(sample_records)} записей")
            else:
                print("❌ Таблица _DOCUMENT184 не найдена!")
            
            print("\n🔍 Этап 2: Анализ журнала _DOCUMENT184_VT4940")
            print("-" * 60)
            
            # Анализируем журнал документов (табличную часть)
            journal_table_name = '_DOCUMENT184_VT4940'
            if journal_table_name in db.tables:
                table = db.tables[journal_table_name]
                record_count = len(table)
                print(f"📊 Найдено записей в журнале: {record_count:,}")
                
                results['metadata']['total_journal_records'] = record_count
                
                # Анализируем первые 15 записей
                sample_records = []
                for i in range(min(15, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            # Получаем данные записи
                            row_data = row.as_dict()
                            sample_records.append(row_data)
                            
                            print(f"    📄 Запись {i+1}:")
                            
                            # Показываем основные поля
                            for field_name, field_value in row_data.items():
                                if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    print(f"        📋 {field_name}: {field_value}")
                            
                            # Ищем BLOB поля
                            blob_fields = []
                            for field_name, field_value in row_data.items():
                                if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    blob_fields.append(field_name)
                            
                            if blob_fields:
                                print(f"        🔍 BLOB поля: {blob_fields}")
                                
                                # Анализируем содержимое BLOB полей
                                for blob_field in blob_fields[:2]:  # Анализируем первые 2 BLOB поля
                                    try:
                                        blob_value = row_data[blob_field]
                                        content = safe_get_blob_content(blob_value)
                                        if content:
                                            print(f"        📋 {blob_field}: {content[:150]}...")
                                    except Exception as e:
                                        print(f"        ⚠️ Ошибка чтения BLOB {blob_field}: {e}")
                            
                            print()  # Пустая строка для разделения
                    
                    except Exception as e:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                # Сохраняем результаты анализа журнала
                journal_analysis = {
                    'table_name': journal_table_name,
                    'record_count': record_count,
                    'sample_records': sample_records,
                    'fields': list(sample_records[0].keys()) if sample_records else []
                }
                results['journal_analysis'][journal_table_name] = journal_analysis
                
                print(f"✅ Проанализировано {len(sample_records)} записей журнала")
            else:
                print(f"❌ Журнал {journal_table_name} не найден!")
            
            print("\n🔍 Этап 3: Поиск связанных документов")
            print("-" * 60)
            
            # Ищем связанные документы
            related_documents = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' not in table_name:
                    if '184' in table_name or 'розничн' in table_name.lower():
                        table = db.tables[table_name]
                        if len(table) > 0:
                            related_documents.append((table_name, len(table)))
            
            if related_documents:
                print(f"📊 Найдено связанных документов: {len(related_documents)}")
                for table_name, record_count in related_documents:
                    print(f"  📋 {table_name} ({record_count:,} записей)")
            else:
                print("📊 Связанные документы не найдены")
            
            # Сохраняем результаты
            with open('retail_sales_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в retail_sales_analysis.json")
            print(f"📊 Найдено документов розничных продаж: {results['metadata']['total_retail_documents']}")
            print(f"📊 Найдено записей в журнале: {results['metadata']['total_journal_records']}")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_retail_sales()
