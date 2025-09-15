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

def analyze_document138_detailed():
    """
    Детальный анализ найденной ключевой таблицы _DOCUMENT138
    ЦЕЛЬ: Извлечь все записи с ключевыми словами и понять структуру
    """
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ _DOCUMENT138")
    print("🎯 ЦЕЛЬ: Извлечь все записи с ключевыми словами")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'document138_analysis': {},
                'keyword_records': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': 'raw/1Cv8.1CD',
                    'table_name': '_DOCUMENT138'
                }
            }
            
            # Анализируем таблицу _DOCUMENT138
            table_name = '_DOCUMENT138'
            if table_name in db.tables:
                table = db.tables[table_name]
                record_count = len(table)
                print(f"📊 Найдено записей: {record_count:,}")
                
                # Ключевые слова для поиска
                keywords = {
                    'перемещение': ['перемещение', 'перемещ'],
                    'качество': ['некондиция', 'брак', 'дефект', 'качество'],
                    'поступление': ['приход', 'поступл', 'поступление'],
                    'возврат': ['возврат', 'рекламация'],
                    'флористика': ['флористический', 'флор', 'цвет', 'цветы'],
                    'склад': ['склад', 'склады', 'отгрузки', 'получатель']
                }
                
                # Счетчики для каждого ключевого слова
                keyword_counts = {keyword: 0 for keyword in keywords.keys()}
                
                # Собираем записи с ключевыми словами
                keyword_records = {keyword: [] for keyword in keywords.keys()}
                
                # Анализируем первые 1000 записей для поиска ключевых слов
                print(f"\n🔍 Анализируем первые 1000 записей для поиска ключевых слов...")
                
                for i in range(min(1000, len(table))):
                    try:
                        row = table[i]
                        if not row.is_empty:
                            row_data = row.as_dict()
                            
                            # Ищем ключевые слова в BLOB полях
                            found_keywords = set()
                            
                            for field_name, field_value in row_data.items():
                                if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    content = safe_get_blob_content(field_value)
                                    if content and len(content) > 10:
                                        # Ищем ключевые слова
                                        for keyword, variations in keywords.items():
                                            for variation in variations:
                                                if variation.lower() in content.lower():
                                                    found_keywords.add(keyword)
                                                    keyword_counts[keyword] += 1
                                                    
                                                    # Сохраняем запись с ключевым словом
                                                    if len(keyword_records[keyword]) < 10:  # Ограничиваем 10 записями на ключевое слово
                                                        keyword_records[keyword].append({
                                                            'record_index': i,
                                                            'field_name': field_name,
                                                            'content': content[:300],
                                                            'full_record': {k: v for k, v in row_data.items() if not str(v).startswith('<onec_dtools.database_reader.Blob')}
                                                        })
                            
                            # Ищем ключевые слова в обычных полях
                            for field_name, field_value in row_data.items():
                                if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                    field_str = str(field_value).lower()
                                    for keyword, variations in keywords.items():
                                        for variation in variations:
                                            if variation.lower() in field_str:
                                                found_keywords.add(keyword)
                                                keyword_counts[keyword] += 1
                                
                            # Показываем прогресс каждые 100 записей
                            if (i + 1) % 100 == 0:
                                print(f"    📊 Обработано записей: {i + 1:,}")
                                for keyword, count in keyword_counts.items():
                                    if count > 0:
                                        print(f"        🎯 {keyword}: {count} записей")
                    
                    except Exception as e:
                        if i < 10:  # Показываем ошибки только для первых 10 записей
                            print(f"    ⚠️ Ошибка при чтении записи {i}: {e}")
                        continue
                
                # Показываем итоговую статистику по ключевым словам
                print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА ПО КЛЮЧЕВЫМ СЛОВАМ:")
                print("-" * 60)
                
                for keyword, count in keyword_counts.items():
                    if count > 0:
                        print(f"🎯 {keyword}: {count} записей")
                    else:
                        print(f"❌ {keyword}: не найдено")
                
                # Анализируем структуру полей на основе первых записей
                print(f"\n🔍 АНАЛИЗ СТРУКТУРЫ ПОЛЕЙ:")
                print("-" * 60)
                
                if len(table) > 0:
                    try:
                        first_record = table[0]
                        if not first_record.is_empty:
                            first_record_data = first_record.as_dict()
                            
                            print(f"📋 Всего полей: {len(first_record_data)}")
                            print(f"📋 Структура полей:")
                            
                            # Показываем первые 20 полей
                            for i, (field_name, field_value) in enumerate(list(first_record_data.items())[:20]):
                                field_type = "BLOB" if str(field_value).startswith('<onec_dtools.database_reader.Blob') else "Обычное"
                                print(f"    {i+1:2d}. {field_name} ({field_type}): {field_value}")
                            
                            # Сохраняем структуру полей
                            fields_structure = {
                                'total_fields': len(first_record_data),
                                'field_names': list(first_record_data.keys()),
                                'field_types': {name: "BLOB" if str(val).startswith('<onec_dtools.database_reader.Blob') else "Обычное" 
                                              for name, val in first_record_data.items()}
                            }
                            
                            results['document138_analysis']['fields_structure'] = fields_structure
                            
                    except Exception as e:
                        print(f"    ⚠️ Ошибка анализа структуры полей: {e}")
                
                # Сохраняем результаты анализа
                results['document138_analysis']['record_count'] = record_count
                results['document138_analysis']['keyword_counts'] = keyword_counts
                results['keyword_records'] = keyword_records
                
                # Сохраняем все результаты
                with open('document138_detailed_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"\n✅ Результаты сохранены в document138_detailed_analysis.json")
                
                # Показываем образцы найденных записей
                print(f"\n🔍 ОБРАЗЦЫ НАЙДЕННЫХ ЗАПИСЕЙ:")
                print("-" * 60)
                
                for keyword, records in keyword_records.items():
                    if records:
                        print(f"\n🎯 {keyword.upper()} (найдено {len(records)} записей):")
                        for j, record in enumerate(records[:3]):  # Показываем первые 3 записи
                            print(f"    📄 Запись {j+1} (индекс {record['record_index']}):")
                            print(f"        📋 Поле: {record['field_name']}")
                            print(f"        📋 Содержимое: {record['content']}...")
                            print()
                
                return results
                
            else:
                print(f"❌ Таблица {table_name} не найдена!")
                return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    analyze_document138_detailed()
