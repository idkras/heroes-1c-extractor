#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import sys
import os

def find_real_documents():
    """
    Поиск реальных документов: акты, счета-фактуры, номенклатура
    """
    print("🔍 Поиск реальных документов в 1CD файле")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            print(f"📊 Количество таблиц: {len(db.tables)}")
            
            # Ключевые слова для поиска документов
            document_keywords = [
                'акт', 'счет', 'фактур', 'накладн', 'приход', 'расход',
                'document', 'invoice', 'receipt', 'expense', 'income',
                'номенклатур', 'товар', 'справочник', 'reference',
                'цвет', 'flower', 'rose', 'tulip', 'цветы', 'розы'
            ]
            
            # Ищем таблицы с документами
            document_tables = []
            
            for table_name in db.tables.keys():
                table_lower = table_name.lower()
                
                # Проверяем ключевые слова в названии таблицы
                has_keyword = any(keyword in table_lower for keyword in document_keywords)
                
                if has_keyword and len(db.tables[table_name]) > 0:
                    table = db.tables[table_name]
                    
                    # Проверяем наличие непустых записей
                    non_empty_count = 0
                    for i in range(min(10, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_count += 1
                    
                    if non_empty_count > 0:
                        document_tables.append((table_name, len(table), non_empty_count))
            
            print(f"\n✅ Найдено {len(document_tables)} таблиц с документами:")
            
            for i, (table_name, total_count, non_empty_count) in enumerate(document_tables[:10]):
                print(f"\n{i+1}. 📊 {table_name}")
                print(f"   📈 Всего записей: {total_count:,}")
                print(f"   ✅ Непустых записей: {non_empty_count}")
                
                # Показываем структуру таблицы
                table = db.tables[table_name]
                print(f"   📝 Структура полей:")
                for field_name, field_desc in list(table.fields.items())[:10]:
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Показываем пример данных
                for j in range(min(3, len(table))):
                    row = table[j]
                    if not row.is_empty:
                        print(f"   📄 Пример записи #{j}:")
                        
                        # Показываем все поля с данными
                        for field_name in table.fields.keys():
                            try:
                                value = row[field_name]
                                if value is not None and str(value).strip():
                                    print(f"      {field_name}: {value}")
                            except Exception as e:
                                pass
                        break
                
                if i >= 4:  # Показываем только первые 5 таблиц
                    break
            
            # Если не нашли документы, ищем в больших таблицах
            if not document_tables:
                print("\n🔍 Поиск в больших таблицах с данными:")
                
                # Ищем большие таблицы с реальными данными
                large_tables = []
                for table_name in db.tables.keys():
                    table = db.tables[table_name]
                    if len(table) > 10000:  # Большие таблицы
                        non_empty_count = 0
                        for i in range(min(20, len(table))):
                            row = table[i]
                            if not row.is_empty:
                                non_empty_count += 1
                        
                        if non_empty_count > 0:
                            large_tables.append((table_name, len(table), non_empty_count))
                
                large_tables.sort(key=lambda x: x[1], reverse=True)
                
                print(f"📊 Топ-10 больших таблиц с реальными данными:")
                for i, (table_name, total_count, non_empty_count) in enumerate(large_tables[:10]):
                    print(f"  {i+1}. {table_name}: {total_count:,} записей ({non_empty_count} непустых)")
                    
                    # Показываем пример данных из больших таблиц
                    if i < 3:  # Только для первых 3 таблиц
                        table = db.tables[table_name]
                        for j in range(min(5, len(table))):
                            row = table[j]
                            if not row.is_empty:
                                print(f"     📄 Пример записи #{j}:")
                                
                                # Показываем первые 5 полей с данными
                                field_count = 0
                                for field_name in table.fields.keys():
                                    try:
                                        value = row[field_name]
                                        if value is not None and str(value).strip():
                                            print(f"        {field_name}: {value}")
                                            field_count += 1
                                            if field_count >= 5:
                                                break
                                    except Exception as e:
                                        pass
                                break
                    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_real_documents()
    print("\n✅ Поиск завершен") 