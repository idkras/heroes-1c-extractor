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

def search_all_missing_documents():
    """
    Поиск всех недостающих документов для JTBD сценариев
    ЦЕЛЬ: Найти справочники, регистры, документы с цветами и типами букетов
    """
    print("🔍 ПОИСК ВСЕХ НЕДОСТАЮЩИХ ДОКУМЕНТОВ")
    print("🎯 ЦЕЛЬ: JTBD сценарии - цвета, типы букетов, склады, подразделения")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            results = {
                'references': {},
                'accumulation_registers': {},
                'document_journals': {},
                'keyword_search': {},
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': 'raw/1Cv8.1CD',
                    'total_tables': len(db.tables)
                }
            }
            
            print(f"\n📊 Всего таблиц в базе: {len(db.tables):,}")
            
            # 1. ПОИСК СПРАВОЧНИКОВ
            print("\n🔍 ЭТАП 1: Поиск справочников")
            print("-" * 60)
            
            reference_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith('_Reference'):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        reference_tables[table_name] = len(table)
            
            print(f"📊 Найдено таблиц справочников: {len(reference_tables)}")
            
            # Анализируем все справочники
            sorted_references = sorted(reference_tables.items(), key=lambda x: x[1], reverse=True)
            
            for i, (table_name, record_count) in enumerate(sorted_references):
                print(f"\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")
                
                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 3 записи
                        sample_records = []
                        blob_samples = []
                        
                        for j in range(min(3, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()
                                    
                                    # Ищем BLOB поля
                                    for field_name, field_value in record_data.items():
                                        if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                            content = safe_get_blob_content(field_value)
                                            if content and len(content) > 10:
                                                blob_samples.append({
                                                    'field': field_name,
                                                    'content': content[:200]
                                                })
                                    
                                    # Сохраняем образец записи
                                    sample_records.append({
                                        'record_index': j,
                                        'data': {k: v for k, v in record_data.items() if not str(v).startswith('<onec_dtools.database_reader.Blob')}
                                    })
                                    
                            except Exception as e:
                                continue
                        
                        # Показываем образцы BLOB содержимого
                        if blob_samples:
                            print(f"    🔍 BLOB поля ({len(blob_samples)}):")
                            for sample in blob_samples[:2]:
                                print(f"        📋 {sample['field']}: {sample['content']}...")
                        
                        # Сохраняем информацию о справочнике
                        ref_info = {
                            'table_name': table_name,
                            'record_count': record_count,
                            'sample_records': sample_records,
                            'blob_samples': blob_samples[:5]
                        }
                        results['references'][table_name] = ref_info
                        
                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа справочника: {e}")
                    continue
            
            # 2. ПОИСК РЕГИСТРОВ НАКОПЛЕНИЯ
            print("\n🔍 ЭТАП 2: Поиск регистров накопления")
            print("-" * 60)
            
            accumulation_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith('_AccumRGT'):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        accumulation_tables[table_name] = len(table)
            
            print(f"📊 Найдено таблиц регистров накопления: {len(accumulation_tables)}")
            
            # Анализируем все регистры накопления
            sorted_accumulation = sorted(accumulation_tables.items(), key=lambda x: x[1], reverse=True)
            
            for i, (table_name, record_count) in enumerate(sorted_accumulation):
                print(f"\n📋 {i+1:2d}. {table_name} ({record_count:,} записей)")
                
                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 2 записи
                        sample_records = []
                        
                        for j in range(min(2, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()
                                    
                                    # Сохраняем образец записи
                                    sample_records.append({
                                        'record_index': j,
                                        'data': {k: v for k, v in record_data.items() if not str(v).startswith('<onec_dtools.database_reader.Blob')}
                                    })
                                    
                            except Exception as e:
                                continue
                        
                        # Сохраняем информацию о регистре
                        acc_info = {
                            'table_name': table_name,
                            'record_count': record_count,
                            'sample_records': sample_records
                        }
                        results['accumulation_registers'][table_name] = acc_info
                        
                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа регистра: {e}")
                    continue
            
            # 3. ПОИСК ДОКУМЕНТОВ ПО КЛЮЧЕВЫМ СЛОВАМ JTBD
            print("\n🔍 ЭТАП 3: Поиск документов по ключевым словам JTBD")
            print("-" * 60)
            
            # Ключевые слова для JTBD сценариев
            jtbd_keywords = {
                'цвет': ['цвет', 'розовый', 'голубой', 'красный', 'белый', 'желтый', 'синий'],
                'букет': ['букет', 'флористический', 'композиция', 'моно', 'яндекс букет'],
                'склад': ['склад', 'братиславский', '045', 'подразделение', 'магазин'],
                'канал': ['яндекс маркет', 'яндекс директ', 'яндекс-еда', 'интернет магазин'],
                'качество': ['качество', 'брак', 'дефект', 'некондиция', 'стандарт', 'премиум']
            }
            
            # Поиск по всем таблицам документов
            document_tables = {}
            for table_name in db.tables.keys():
                if table_name.startswith('_DOCUMENT'):
                    table = db.tables[table_name]
                    if len(table) > 0:
                        document_tables[table_name] = len(table)
            
            print(f"📊 Анализируем {len(document_tables)} таблиц документов...")
            
            keyword_results = {keyword: [] for keyword in jtbd_keywords.keys()}
            
            # Анализируем топ-50 таблиц документов
            sorted_documents = sorted(document_tables.items(), key=lambda x: x[1], reverse=True)
            
            for i, (table_name, record_count) in enumerate(sorted_documents[:50]):
                if i % 10 == 0:
                    print(f"    📊 Обработано таблиц: {i}/{min(50, len(sorted_documents))}")
                
                try:
                    table = db.tables[table_name]
                    if len(table) > 0:
                        # Анализируем первые 3 записи
                        found_keywords = set()
                        
                        for j in range(min(3, len(table))):
                            try:
                                record = table[j]
                                if not record.is_empty:
                                    record_data = record.as_dict()
                                    
                                    # Ищем ключевые слова в BLOB полях
                                    for field_name, field_value in record_data.items():
                                        if str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                            content = safe_get_blob_content(field_value)
                                            if content and len(content) > 10:
                                                # Ищем ключевые слова
                                                for keyword, variations in jtbd_keywords.items():
                                                    for variation in variations:
                                                        if variation.lower() in content.lower():
                                                            found_keywords.add(keyword)
                                                            keyword_results[keyword].append({
                                                                'table_name': table_name,
                                                                'record_count': record_count,
                                                                'field_name': field_name,
                                                                'content_sample': content[:200]
                                                            })
                                    
                                    # Ищем в обычных полях
                                    for field_name, field_value in record_data.items():
                                        if not str(field_value).startswith('<onec_dtools.database_reader.Blob'):
                                            field_str = str(field_value).lower()
                                            for keyword, variations in jtbd_keywords.items():
                                                for variation in variations:
                                                    if variation.lower() in field_str:
                                                        found_keywords.add(keyword)
                                                        keyword_results[keyword].append({
                                                            'table_name': table_name,
                                                            'record_count': record_count,
                                                            'field_name': field_name,
                                                            'content_sample': str(field_value)
                                                        })
                                
                            except Exception as e:
                                continue
                        
                        # Показываем найденные ключевые слова
                        if found_keywords:
                            print(f"    🎯 {table_name}: {', '.join(found_keywords)}")
                            
                except Exception as e:
                    continue
            
            # Показываем результаты поиска по ключевым словам
            print(f"\n📊 РЕЗУЛЬТАТЫ ПОИСКА ПО КЛЮЧЕВЫМ СЛОВАМ:")
            print("-" * 60)
            
            for keyword, matches in keyword_results.items():
                if matches:
                    print(f"\n🎯 {keyword.upper()}: найдено {len(matches)} совпадений")
                    for match in matches[:3]:  # Показываем первые 3
                        print(f"    📋 {match['table_name']} ({match['record_count']:,} записей)")
                        print(f"        📋 Поле: {match['field_name']}")
                        print(f"        📋 Образец: {match['content_sample']}...")
                else:
                    print(f"\n❌ {keyword.upper()}: не найдено")
            
            # Сохраняем результаты поиска по ключевым словам
            results['keyword_search'] = keyword_results
            
            # Сохраняем все результаты
            with open('all_missing_documents_search.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ Результаты сохранены в all_missing_documents_search.json")
            
            # Итоговая статистика
            print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
            print(f"    📋 Справочники: {len(results['references'])} типов")
            print(f"    📋 Регистры накопления: {len(results['accumulation_registers'])} типов")
            print(f"    🔍 Ключевые слова найдены: {sum(1 for v in keyword_results.values() if v)} из {len(jtbd_keywords)}")
            
            return results
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    search_all_missing_documents()
