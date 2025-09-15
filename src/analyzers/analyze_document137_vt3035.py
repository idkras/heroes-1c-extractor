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

def analyze_document137_vt3035():
    """
    Детальный анализ таблицы _DOCUMENT137_VT3035 (Отчет о розничных продажах)
    """
    print("🔍 Детальный анализ таблицы _DOCUMENT137_VT3035")
    print("🎯 ЦЕЛЬ: Отчет о розничных продажах - извлечь первичные данные о качестве товаров")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'document137_vt3035': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': 'raw/1Cv8.1CD',
                    'table_name': '_DOCUMENT137_VT3035',
                    'document_type': 'Отчет о розничных продажах'
                }
            }
            
            print("\n🔍 Этап 1: Анализ таблицы _DOCUMENT137_VT3035")
            print("-" * 60)
            
            # Анализируем таблицу _DOCUMENT137_VT3035
            table_name = '_DOCUMENT137_VT3035'
            if table_name in db.tables:
                table = db.tables[table_name]
                record_count = len(table)
                print(f"📊 Найдено записей: {record_count:,}")
                
                # Анализируем первые 30 записей для понимания структуры
                sample_records = []
                for i in range(min(30, len(table))):
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
                                for blob_field in blob_fields[:3]:  # Анализируем первые 3 BLOB поля
                                    try:
                                        blob_value = row_data[blob_field]
                                        content = safe_get_blob_content(blob_value)
                                        if content:
                                            print(f"        📋 {blob_field}: {content[:200]}...")
                                            
                                            # Ищем ключевые слова качества
                                            quality_keywords = [
                                                "качество", "брак", "дефект", "некондиция", "стандарт",
                                                "премиум", "элит", "цвет", "цветы", "розы", "тюльпаны",
                                                "флористика", "горшечные", "поставка", "приоритет"
                                            ]
                                            
                                            for keyword in quality_keywords:
                                                if keyword.lower() in content.lower():
                                                    print(f"            🎯 Найдено ключевое слово: '{keyword}'")
                                        
                                    except Exception as e:
                                        print(f"        ⚠️ Ошибка чтения BLOB {blob_field}: {e}")
                            
                            print()  # Пустая строка для разделения
                    
                    except Exception as e:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                # Сохраняем результаты анализа
                table_analysis = {
                    'table_name': table_name,
                    'record_count': record_count,
                    'sample_records': sample_records,
                    'fields': list(sample_records[0].keys()) if sample_records else []
                }
                results['document137_vt3035'] = table_analysis
                
                print(f"✅ Проанализировано {len(sample_records)} записей")
                
                # Анализируем структуру полей
                if sample_records:
                    print(f"\n📋 Структура полей:")
                    fields = list(sample_records[0].keys())
                    for i, field_name in enumerate(fields):
                        print(f"    {i+1:2d}. {field_name}")
                
            else:
                print(f"❌ Таблица {table_name} не найдена!")
                print("🔍 Ищем похожие таблицы...")
                
                # Ищем похожие таблицы
                similar_tables = []
                for table_name in db.tables.keys():
                    if '_DOCUMENT137' in table_name and '_VT' in table_name:
                        table = db.tables[table_name]
                        if len(table) > 0:
                            similar_tables.append((table_name, len(table)))
                
                if similar_tables:
                    print(f"📊 Найдено похожих таблиц: {len(similar_tables)}")
                    for table_name, record_count in similar_tables:
                        print(f"  📋 {table_name} ({record_count:,} записей)")
                        
                        # Анализируем первую похожую таблицу
                        if similar_tables:
                            first_table_name, first_record_count = similar_tables[0]
                            print(f"\n🔍 Анализируем первую таблицу: {first_table_name}")
                            
                            table = db.tables[first_table_name]
                            if len(table) > 0:
                                try:
                                    # Анализируем первые 5 записей
                                    sample_records = []
                                    for i in range(min(5, len(table))):
                                        sample_record = table[i]
                                        if not sample_record.is_empty:
                                            record_data = sample_record.as_dict()
                                            sample_records.append(record_data)
                                            
                                            print(f"    📄 Запись {i+1}:")
                                            for field_name, field_value in record_data.items():
                                                if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                                    print(f"        📋 {field_name}: {field_value}")
                                            
                                            print()  # Пустая строка
                                    
                                    # Сохраняем результаты анализа похожей таблицы
                                    similar_table_analysis = {
                                        'table_name': first_table_name,
                                        'record_count': first_record_count,
                                        'sample_records': sample_records,
                                        'fields': list(sample_records[0].keys()) if sample_records else []
                                    }
                                    results['similar_table'] = similar_table_analysis
                                    
                                except Exception as e:
                                    print(f"    ⚠️ Ошибка анализа похожей таблицы: {e}")
                else:
                    print("📊 Похожие таблицы не найдены")
            
            print("\n🔍 Этап 2: Поиск связанных документов")
            print("-" * 60)
            
            # Ищем связанные документы
            related_documents = []
            for table_name in db.tables.keys():
                if '_DOCUMENT137' in table_name and '_VT' not in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        related_documents.append((table_name, len(table)))
            
            if related_documents:
                print(f"📊 Найдено связанных документов: {len(related_documents)}")
                for table_name, record_count in related_documents[:5]:
                    print(f"  📋 {table_name} ({record_count:,} записей)")
                    
                    # Анализируем первый связанный документ
                    if related_documents:
                        first_doc_name, first_doc_count = related_documents[0]
                        print(f"\n🔍 Анализируем связанный документ: {first_doc_name}")
                        
                        table = db.tables[first_doc_name]
                        if len(table) > 0:
                            try:
                                # Анализируем первые 3 записи
                                sample_records = []
                                for i in range(min(3, len(table))):
                                    sample_record = table[i]
                                    if not sample_record.is_empty:
                                        record_data = sample_record.as_dict()
                                        sample_records.append(record_data)
                                        
                                        print(f"    📄 Запись {i+1}:")
                                        for field_name, field_value in record_data.items():
                                            if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                                print(f"        📋 {field_name}: {field_value}")
                                        
                                        print()  # Пустая строка
                                
                                # Сохраняем результаты анализа связанного документа
                                related_doc_analysis = {
                                    'table_name': first_doc_name,
                                    'record_count': first_doc_count,
                                    'sample_records': sample_records,
                                    'fields': list(sample_records[0].keys()) if sample_records else []
                                }
                                results['related_document'] = related_doc_analysis
                                
                            except Exception as e:
                                print(f"    ⚠️ Ошибка анализа связанного документа: {e}")
            else:
                print("📊 Связанные документы не найдены")
            
            # Сохраняем результаты
            with open('document137_vt3035_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в document137_vt3035_analysis.json")
            
            if 'document137_vt3035' in results and results['document137_vt3035']:
                print(f"📊 Проанализирована таблица: {results['document137_vt3035']['table_name']}")
                print(f"📊 Количество записей: {results['document137_vt3035']['record_count']:,}")
                print(f"📊 Количество полей: {len(results['document137_vt3035']['fields'])}")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_document137_vt3035()
