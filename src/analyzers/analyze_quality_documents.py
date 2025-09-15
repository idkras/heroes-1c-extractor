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

def analyze_quality_documents():
    """
    Детальный анализ документов с ключевыми словами качества
    """
    print("🔍 Детальный анализ документов с ключевыми словами качества")
    print("🎯 ЦЕЛЬ: Найти документы 'корректировка качества товара'")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Ключевые слова для поиска документов "корректировка качества товара"
            quality_keywords = [
                "корректировка", "качество", "товар", "брак", "дефект",
                "проверка", "контроль", "отбраковка", "списание", "уценка",
                "цвет", "цветы", "розы", "тюльпаны", "флористика",
                "некондиция", "реализация", "поступление", "склад"
            ]
            
            results = {
                'quality_documents': [],
                'blob_analysis': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_quality_documents': 0,
                    'quality_keywords_found': [],
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            print("\n🔍 Этап 1: Поиск документов с ключевыми словами качества")
            print("-" * 60)
            
            # Ищем таблицы документов
            document_tables = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' not in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            document_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Анализируем {len(document_tables)} таблиц документов...")
            
            # Анализируем первые 10 больших таблиц документов
            for table_name, record_count in document_tables[:10]:
                print(f"\n📋 Анализ таблицы: {table_name}")
                print(f"📊 Записей: {record_count:,}")
                
                table = db.tables[table_name]
                
                # Анализируем первые 20 записей для поиска ключевых слов
                quality_records = []
                for i in range(min(20, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            # Получаем данные записи
                            row_data = row.as_dict()
                            
                            # Ищем ключевые слова в полях
                            found_keywords = []
                            for field_name, field_value in row_data.items():
                                field_str = str(field_value).lower()
                                for keyword in quality_keywords:
                                    if keyword.lower() in field_str:
                                        if keyword not in found_keywords:
                                            found_keywords.append(keyword)
                            
                            # Если найдены ключевые слова, анализируем детально
                            if found_keywords:
                                print(f"    🎯 Запись {i+1}: найдены ключевые слова: {found_keywords}")
                                
                                # Анализируем BLOB поля
                                blob_contents = {}
                                for field_name, field_value in row_data.items():
                                    if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                        try:
                                            content = safe_get_blob_content(field_value)
                                            if content:
                                                blob_contents[field_name] = content
                                                
                                                # Ищем ключевые слова в BLOB содержимом
                                                for keyword in quality_keywords:
                                                    if keyword.lower() in content.lower():
                                                        if keyword not in results['metadata']['quality_keywords_found']:
                                                            results['metadata']['quality_keywords_found'].append(keyword)
                                                        print(f"        🔍 BLOB {field_name}: '{keyword}' в '{content[:150]}...'")
                                        except Exception as e:
                                            print(f"        ⚠️ Ошибка чтения BLOB {field_name}: {e}")
                                
                                # Сохраняем найденную запись
                                quality_record = {
                                    'record_index': i,
                                    'found_keywords': found_keywords,
                                    'row_data': row_data,
                                    'blob_contents': blob_contents
                                }
                                quality_records.append(quality_record)
                                
                                # Останавливаемся после первых 5 найденных записей
                                if len(quality_records) >= 5:
                                    break
                    
                    except Exception as e:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                if quality_records:
                    print(f"    ✅ Найдено {len(quality_records)} записей с ключевыми словами")
                    
                    # Сохраняем результаты анализа таблицы
                    table_analysis = {
                        'table_name': table_name,
                        'record_count': record_count,
                        'quality_records': quality_records
                    }
                    results['quality_documents'].append(table_analysis)
                    
                    # Останавливаемся после анализа 3 таблиц с результатами
                    if len(results['quality_documents']) >= 3:
                        break
                else:
                    print(f"    ⚠️ Ключевые слова не найдены")
            
            print("\n🔍 Этап 2: Анализ журналов документов")
            print("-" * 60)
            
            # Ищем журналы документов (табличные части)
            journal_tables = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        journal_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            journal_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Анализируем {len(journal_tables)} журналов документов...")
            
            # Анализируем первые 5 больших журналов
            for table_name, record_count in journal_tables[:5]:
                print(f"\n📋 Анализ журнала: {table_name}")
                print(f"📊 Записей: {record_count:,}")
                
                table = db.tables[table_name]
                
                # Анализируем первые 10 записей
                quality_records = []
                for i in range(min(10, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            row_data = row.as_dict()
                            
                            # Ищем ключевые слова в полях
                            found_keywords = []
                            for field_name, field_value in row_data.items():
                                field_str = str(field_value).lower()
                                for keyword in quality_keywords:
                                    if keyword.lower() in field_str:
                                        if keyword not in found_keywords:
                                            found_keywords.append(keyword)
                            
                            # Если найдены ключевые слова, анализируем детально
                            if found_keywords:
                                print(f"    🎯 Запись {i+1}: найдены ключевые слова: {found_keywords}")
                                
                                # Анализируем BLOB поля
                                blob_contents = {}
                                for field_name, field_value in row_data.items():
                                    if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                        try:
                                            content = safe_get_blob_content(field_value)
                                            if content:
                                                blob_contents[field_name] = content
                                                
                                                # Ищем ключевые слова в BLOB содержимом
                                                for keyword in quality_keywords:
                                                    if keyword.lower() in content.lower():
                                                        if keyword not in results['metadata']['quality_keywords_found']:
                                                            results['metadata']['quality_keywords_found'].append(keyword)
                                                        print(f"        🔍 BLOB {field_name}: '{keyword}' в '{content[:150]}...'")
                                        except Exception as e:
                                            print(f"        ⚠️ Ошибка чтения BLOB {field_name}: {e}")
                                
                                # Сохраняем найденную запись
                                quality_record = {
                                    'record_index': i,
                                    'found_keywords': found_keywords,
                                    'row_data': row_data,
                                    'blob_contents': blob_contents
                                }
                                quality_records.append(quality_record)
                                
                                # Останавливаемся после первых 3 найденных записей
                                if len(quality_records) >= 3:
                                    break
                    
                    except Exception as e:
                        print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                if quality_records:
                    print(f"    ✅ Найдено {len(quality_records)} записей с ключевыми словами")
                    
                    # Сохраняем результаты анализа журнала
                    journal_analysis = {
                        'table_name': table_name,
                        'record_count': record_count,
                        'quality_records': quality_records
                    }
                    results['blob_analysis'][table_name] = journal_analysis
                    
                    # Останавливаемся после анализа 2 журналов с результатами
                    if len(results['blob_analysis']) >= 2:
                        break
                else:
                    print(f"    ⚠️ Ключевые слова не найдены")
            
            # Обновляем общую статистику
            results['metadata']['total_quality_documents'] = len(results['quality_documents'])
            
            # Сохраняем результаты
            with open('quality_documents_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в quality_documents_analysis.json")
            print(f"📊 Найдено документов с качеством: {results['metadata']['total_quality_documents']}")
            print(f"🎯 Найдено ключевых слов качества: {len(results['metadata']['quality_keywords_found'])}")
            
            if results['metadata']['quality_keywords_found']:
                print(f"🔍 Ключевые слова качества: {', '.join(results['metadata']['quality_keywords_found'])}")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_quality_documents()
