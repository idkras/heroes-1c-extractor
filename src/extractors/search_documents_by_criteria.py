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

def search_documents_by_criteria():
    """
    Поиск документов по критериям из 1c.todo.md
    Особое внимание на документы "корректировка качества товара"
    """
    print("🔍 Поиск документов по критериям из 1c.todo.md")
    print("🎯 ЦЕЛЬ: Найти документы 'корректировка качества товара'")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Ключевые слова для поиска документов "корректировка качества товара"
            quality_keywords = [
                "корректировка", "качество", "товар", "брак", "дефект",
                "проверка", "контроль", "отбраковка", "списание", "уценка",
                "цвет", "цветы", "розы", "тюльпаны", "флористика"
            ]
            
            # Типы документов для поиска
            document_types = [
                "Поступление товаров услуг",
                "Реализация товаров услуг", 
                "Отчет о розничных продажах",
                "Чек ККМ",
                "Перемещение товаров",
                "Списание товаров услуг",
                "Корректировка качества товара",
                "Акт о браке",
                "Инвентаризация"
            ]
            
            # Поля для проверки
            fields_to_check = [
                "Проведён", "СкладОрдер", "НомерМашины", "Склад",
                "Подразделение", "Статус", "Статус чека ККМ"
            ]
            
            # BLOB поля для связей
            blob_fields_to_check = [
                "ДокументПоступления", "Сделка", "СкладОтправитель", "СкладПолучатель"
            ]
            
            results = {
                'documents': [],
                'quality_documents': [],
                'references': [],
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_tables': len(db.tables),
                    'document_types_found': [],
                    'references_found': [],
                    'quality_keywords_found': [],
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            print("\n🔍 Этап 1: Поиск по типам документов")
            print("-" * 40)
            
            # Ищем таблицы документов
            document_tables = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' not in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            document_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Найдено {len(document_tables)} таблиц документов:")
            for i, (table_name, record_count) in enumerate(document_tables[:10]):
                print(f"  {i+1}. {table_name} ({record_count:,} записей)")
            
            print("\n🔍 Этап 2: Анализ полей документов")
            print("-" * 40)
            
            # Анализируем первые 5 больших таблиц документов
            for table_name, record_count in document_tables[:5]:
                print(f"\n📋 Анализ таблицы: {table_name}")
                print(f"📊 Записей: {record_count:,}")
                
                table = db.tables[table_name]
                
                # Анализируем первые 10 записей для понимания структуры
                sample_records = []
                for i in range(min(10, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            # Получаем данные записи
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
                    for field_name, field_value in sample_records[0].items():
                        if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                            blob_fields.append(field_name)
                    
                    if blob_fields:
                        print(f"    🔍 BLOB поля: {len(blob_fields)}")
                        
                        # Анализируем содержимое BLOB полей
                        for blob_field in blob_fields[:3]:  # Анализируем первые 3 BLOB поля
                            print(f"      📋 Анализ BLOB поля: {blob_field}")
                            
                            # Анализируем первые 5 записей для этого поля
                            blob_contents = []
                            for record in sample_records[:5]:
                                try:
                                    blob_value = record[blob_field]
                                    content = safe_get_blob_content(blob_value)
                                    if content:
                                        blob_contents.append(content)
                                        
                                        # Ищем ключевые слова качества
                                        for keyword in quality_keywords:
                                            if keyword.lower() in content.lower():
                                                if keyword not in results['metadata']['quality_keywords_found']:
                                                    results['metadata']['quality_keywords_found'].append(keyword)
                                                print(f"        🎯 Найдено ключевое слово: '{keyword}' в '{content[:100]}...'")
                                        
                                except Exception as e:
                                    print(f"        ⚠️ Ошибка анализа BLOB: {e}")
                            
                            if blob_contents:
                                print(f"        📊 Найдено {len(blob_contents)} BLOB записей с содержимым")
                    
                    # Сохраняем результаты анализа
                    table_analysis = {
                        'table_name': table_name,
                        'record_count': record_count,
                        'sample_records': sample_records,
                        'fields': fields,
                        'blob_fields': blob_fields,
                        'found_fields': [],
                        'blob_fields': []
                    }
                    
                    # Ищем поля с ключевыми словами
                    for field_name in fields:
                        for keyword in quality_keywords:
                            if keyword.lower() in field_name.lower():
                                table_analysis['found_fields'].append(field_name)
                                if keyword not in results['metadata']['quality_keywords_found']:
                                    results['metadata']['quality_keywords_found'].append(keyword)
                    
                    results['documents'].append(table_analysis)
                else:
                    print(f"    ⚠️ Не удалось прочитать записи")
            
            print("\n🔍 Этап 3: Анализ справочников")
            print("-" * 40)
            
            # Ищем справочники
            reference_tables = []
            for table_name in db.tables.keys():
                if '_Reference' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        reference_tables.append((table_name, len(table)))
            
            if reference_tables:
                print(f"📊 Найдено {len(reference_tables)} справочников:")
                for table_name, record_count in reference_tables[:5]:
                    print(f"  📋 {table_name} ({record_count:,} записей)")
                    
                    # Анализируем справочник
                    table = db.tables[table_name]
                    if len(table) > 0:
                        try:
                            sample_record = table[0]
                            if not sample_record.is_empty:
                                record_data = sample_record.as_dict()
                                fields = list(record_data.keys())
                                
                                reference_analysis = {
                                    'table_name': table_name,
                                    'record_count': record_count,
                                    'fields': fields,
                                    'sample_records': [record_data]
                                }
                                results['references'].append(reference_analysis)
                        except Exception as e:
                            print(f"    ⚠️ Ошибка анализа справочника {table_name}: {e}")
            else:
                print("📊 Найдено 0 справочников:")
                print("🔍 Ищем справочники в других таблицах...")
                
                # Ищем таблицы, которые могут быть справочниками
                potential_references = []
                for table_name in db.tables.keys():
                    if '_VT' not in table_name and '_DOCUMENT' not in table_name:
                        table = db.tables[table_name]
                        if len(table) > 0 and len(table) < 10000:  # Справочники обычно меньше
                            potential_references.append((table_name, len(table)))
                
                # Сортируем по размеру
                potential_references.sort(key=lambda x: x[1])
                
                print(f"📊 Найдено {len(potential_references)} потенциальных справочников:")
                for table_name, record_count in potential_references[:10]:
                    print(f"  📋 {table_name} ({record_count:,} записей)")
                    
                    # Анализируем потенциальный справочник
                    table = db.tables[table_name]
                    if len(table) > 0:
                        try:
                            sample_record = table[0]
                            if not sample_record.is_empty:
                                record_data = sample_record.as_dict()
                                fields = list(record_data.keys())
                                
                                # Ищем поля с ключевыми словами
                                found_fields = []
                                for field_name in fields:
                                    for keyword in quality_keywords:
                                        if keyword.lower() in field_name.lower():
                                            found_fields.append(field_name)
                                            if keyword not in results['metadata']['quality_keywords_found']:
                                                results['metadata']['quality_keywords_found'].append(keyword)
                                
                                if found_fields:
                                    print(f"    🎯 Найдены поля с ключевыми словами: {found_fields}")
                                
                                reference_analysis = {
                                    'table_name': table_name,
                                    'record_count': record_count,
                                    'fields': fields,
                                    'found_fields': found_fields,
                                    'sample_records': [record_data]
                                }
                                results['references'].append(reference_analysis)
                        except Exception as e:
                            print(f"    ⚠️ Ошибка анализа потенциального справочника {table_name}: {e}")
            
            print("\n🔍 Этап 4: Поиск связей между документами")
            print("-" * 40)
            
            # Ищем журналы документов (табличные части)
            journal_tables = []
            for table_name in db.tables.keys():
                if '_DOCUMENT' in table_name and '_VT' in table_name:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        journal_tables.append((table_name, len(table)))
            
            # Сортируем по размеру
            journal_tables.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 Найдено {len(journal_tables)} журналов документов")
            
            # Анализируем первые 3 больших журнала
            for table_name, record_count in journal_tables[:3]:
                print(f"\n📋 Анализ журнала: {table_name}")
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
                    
                    # Ищем BLOB поля
                    blob_fields = []
                    for field_name, field_value in sample_records[0].items():
                        if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                            blob_fields.append(field_name)
                    
                    if blob_fields:
                        print(f"    🔍 BLOB поля: {len(blob_fields)}")
                        
                        # Анализируем содержимое BLOB полей
                        for blob_field in blob_fields[:2]:  # Анализируем первые 2 BLOB поля
                            print(f"      📋 Анализ BLOB поля: {blob_field}")
                            
                            # Анализируем первые 3 записи для этого поля
                            blob_contents = []
                            for record in sample_records[:3]:
                                try:
                                    blob_value = record[blob_field]
                                    content = safe_get_blob_content(blob_value)
                                    if content:
                                        blob_contents.append(content)
                                        
                                        # Ищем ключевые слова качества
                                        for keyword in quality_keywords:
                                            if keyword.lower() in content.lower():
                                                if keyword not in results['metadata']['quality_keywords_found']:
                                                    results['metadata']['quality_keywords_found'].append(keyword)
                                                print(f"        🎯 Найдено ключевое слово: '{keyword}' в '{content[:100]}...'")
                                        
                                except Exception as e:
                                    print(f"        ⚠️ Ошибка анализа BLOB: {e}")
                            
                            if blob_contents:
                                print(f"        📊 Найдено {len(blob_contents)} BLOB записей с содержимым")
            
            # Сохраняем результаты
            with open('search_documents_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в search_documents_results.json")
            print(f"📊 Найдено документов: {len(results['documents'])}")
            print(f"📊 Найдено справочников: {len(results['references'])}")
            print(f"🎯 Найдено ключевых слов качества: {len(results['metadata']['quality_keywords_found'])}")
            
            if results['metadata']['quality_keywords_found']:
                print(f"🔍 Ключевые слова качества: {', '.join(results['metadata']['quality_keywords_found'])}")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    search_documents_by_criteria() 