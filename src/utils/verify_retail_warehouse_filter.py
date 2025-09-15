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

def verify_retail_warehouse_filter():
    """
    Проверка всех найденных документов на соответствие фильтру "вид склада = розница"
    ЦЕЛЬ: Исключить оптовые склады, оставить только розничные для JTBD сценариев
    """
    print("🚨 ПРОВЕРКА ФИЛЬТРА: ВИД СКЛАДА = РОЗНИЦА")
    print("🎯 ЦЕЛЬ: Исключить оптовые склады, оставить только розничные")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'retail_warehouse_verification': {},
                'filtered_documents': {},
                'excluded_documents': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': 'raw/1Cv8.1CD',
                    'filter_criteria': 'вид склада = розница'
                }
            }
            
            # Ключевые слова для определения розничных складов
            retail_keywords = [
                'магазин', 'розница', 'розничный', 'торговая точка', 'тт',
                'фм', 'пц', 'интернет магазин', 'онлайн магазин',
                'яндекс маркет', 'яндекс директ', 'яндекс-еда'
            ]
            
            # Ключевые слова для исключения оптовых складов
            wholesale_keywords = [
                'опт', 'оптовый', 'поставщик', 'производство', 'производственный',
                'склад поставщика', 'база поставщика', 'центральный склад'
            ]
            
            # Список документов для проверки
            documents_to_check = [
                '_DOCUMENT137',           # Отчеты о розничных продажах
                '_DOCUMENT137_VT3035',    # Табличная часть отчетов
                '_DOCUMENT138',           # Перемещения, качество, поступления
                '_DOCUMENT163',           # Склады, магазины, подразделения
                '_DOCUMENT9490_VT9494',  # Цвета, качество цветов
                '_DOCUMENT156'            # Качество
            ]
            
            print(f"\n📊 Проверяем {len(documents_to_check)} документов на соответствие фильтру...")
            
            for doc_name in documents_to_check:
                print(f"\n🔍 ЭТАП: Проверка {doc_name}")
                print("-" * 60)
                
                if doc_name in db.tables:
                    table = db.tables[doc_name]
                    record_count = len(table)
                    print(f"📊 Найдено записей: {record_count:,}")
                    
                    # Анализируем первые 50 записей для определения типа складов
                    retail_records = []
                    wholesale_records = []
                    unclear_records = []
                    
                    for i in range(min(50, len(table))):
                        try:
                            row = table[i]
                            if not row.is_empty:
                                row_data = row.as_dict()
                                
                                # Анализируем содержимое записи
                                record_content = ""
                                is_retail = False
                                is_wholesale = False
                                
                                # Собираем содержимое из всех полей
                                for field_name, field_value in row_data.items():
                                    if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                        content = safe_get_blob_content(field_value)
                                        if content and len(content) > 10:
                                            record_content += " " + content
                                    else:
                                        record_content += " " + str(field_value)
                                
                                record_content = record_content.lower()
                                
                                # Проверяем на розничные ключевые слова
                                for keyword in retail_keywords:
                                    if keyword.lower() in record_content:
                                        is_retail = True
                                        break
                                
                                # Проверяем на оптовые ключевые слова
                                for keyword in wholesale_keywords:
                                    if keyword.lower() in record_content:
                                        is_wholesale = True
                                        break
                                
                                # Классифицируем запись
                                if is_retail and not is_wholesale:
                                    retail_records.append({
                                        'record_index': i,
                                        'content_sample': record_content[:200],
                                        'retail_keywords': [k for k in retail_keywords if k.lower() in record_content]
                                    })
                                elif is_wholesale:
                                    wholesale_records.append({
                                        'record_index': i,
                                        'content_sample': record_content[:200],
                                        'wholesale_keywords': [k for k in wholesale_keywords if k.lower() in record_content]
                                    })
                                else:
                                    unclear_records.append({
                                        'record_index': i,
                                        'content_sample': record_content[:200]
                                    })
                        
                        except Exception as e:
                            continue
                    
                    # Показываем результаты классификации
                    print(f"    ✅ Розничные записи: {len(retail_records)}")
                    print(f"    ❌ Оптовые записи: {len(wholesale_records)}")
                    print(f"    ❓ Неясные записи: {len(unclear_records)}")
                    
                    # Показываем образцы розничных записей
                    if retail_records:
                        print(f"\n    🔍 ОБРАЗЦЫ РОЗНИЧНЫХ ЗАПИСЕЙ:")
                        for j, record in enumerate(retail_records[:3]):
                            print(f"        📄 Запись {j+1} (индекс {record['record_index']}):")
                            print(f"            🏪 Ключевые слова: {', '.join(record['retail_keywords'])}")
                            print(f"            📋 Содержимое: {record['content_sample']}...")
                    
                    # Показываем образцы оптовых записей (для исключения)
                    if wholesale_records:
                        print(f"\n    ⚠️ ОБРАЗЦЫ ОПТОВЫХ ЗАПИСЕЙ (ИСКЛЮЧАЕМ):")
                        for j, record in enumerate(wholesale_records[:2]):
                            print(f"        📄 Запись {j+1} (индекс {record['record_index']}):")
                            print(f"            🏭 Ключевые слова: {', '.join(record['wholesale_keywords'])}")
                            print(f"            📋 Содержимое: {record['content_sample']}...")
                    
                    # Сохраняем результаты проверки
                    doc_verification = {
                        'table_name': doc_name,
                        'total_records': record_count,
                        'analyzed_records': min(50, len(table)),
                        'retail_records_count': len(retail_records),
                        'wholesale_records_count': len(wholesale_records),
                        'unclear_records_count': len(unclear_records),
                        'retail_percentage': round(len(retail_records) / min(50, len(table)) * 100, 1),
                        'retail_samples': retail_records[:5],
                        'wholesale_samples': wholesale_records[:3]
                    }
                    
                    results['retail_warehouse_verification'][doc_name] = doc_verification
                    
                    # Классифицируем документ
                    if len(retail_records) > len(wholesale_records):
                        results['filtered_documents'][doc_name] = {
                            'status': 'INCLUDE',
                            'reason': 'Преобладают розничные записи',
                            'retail_percentage': doc_verification['retail_percentage']
                        }
                        print(f"    ✅ СТАТУС: ВКЛЮЧАЕМ (розничный документ)")
                    elif len(wholesale_records) > len(retail_records):
                        results['excluded_documents'][doc_name] = {
                            'status': 'EXCLUDE',
                            'reason': 'Преобладают оптовые записи',
                            'wholesale_percentage': round(len(wholesale_records) / min(50, len(table)) * 100, 1)
                        }
                        print(f"    ❌ СТАТУС: ИСКЛЮЧАЕМ (оптовый документ)")
                    else:
                        results['filtered_documents'][doc_name] = {
                            'status': 'REVIEW_REQUIRED',
                            'reason': 'Неясная классификация, требуется дополнительный анализ',
                            'retail_percentage': doc_verification['retail_percentage']
                        }
                        print(f"    ❓ СТАТУС: ТРЕБУЕТ ПРОВЕРКИ")
                
                else:
                    print(f"    ❌ Таблица {doc_name} не найдена!")
            
            # Итоговая статистика
            print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА ФИЛЬТРАЦИИ:")
            print("-" * 60)
            
            included_count = len([d for d in results['filtered_documents'].values() if d['status'] == 'INCLUDE'])
            excluded_count = len(results['excluded_documents'])
            review_count = len([d for d in results['filtered_documents'].values() if d['status'] == 'REVIEW_REQUIRED'])
            
            print(f"    ✅ ВКЛЮЧАЕМ: {included_count} документов")
            print(f"    ❌ ИСКЛЮЧАЕМ: {excluded_count} документов")
            print(f"    ❓ ТРЕБУЕТ ПРОВЕРКИ: {review_count} документов")
            
            # Показываем включенные документы
            if included_count > 0:
                print(f"\n✅ ВКЛЮЧЕННЫЕ ДОКУМЕНТЫ (розничные):")
                for doc_name, info in results['filtered_documents'].items():
                    if info['status'] == 'INCLUDE':
                        print(f"    📋 {doc_name}: {info['reason']} ({info['retail_percentage']}% розничных)")
            
            # Показываем исключенные документы
            if excluded_count > 0:
                print(f"\n❌ ИСКЛЮЧЕННЫЕ ДОКУМЕНТЫ (оптовые):")
                for doc_name, info in results['excluded_documents'].items():
                    print(f"    📋 {doc_name}: {info['reason']} ({info['wholesale_percentage']}% оптовых)")
            
            # Показываем документы для проверки
            if review_count > 0:
                print(f"\n❓ ДОКУМЕНТЫ ДЛЯ ДОПОЛНИТЕЛЬНОЙ ПРОВЕРКИ:")
                for doc_name, info in results['filtered_documents'].items():
                    if info['status'] == 'REVIEW_REQUIRED':
                        print(f"    📋 {doc_name}: {info['reason']}")
            
            # Сохраняем все результаты
            with open('retail_warehouse_filter_verification.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты проверки сохранены в retail_warehouse_filter_verification.json")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    verify_retail_warehouse_filter()
