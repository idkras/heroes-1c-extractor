#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_with_methods():
    """
    Извлечение данных документов используя методы as_dict() и as_list()
    """
    print("🔍 Извлечение данных документов")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Структура для хранения всех документов
            all_documents = {
                'documents': [],
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_documents': 0,
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # Анализируем основные таблицы документов
            document_tables = [
                '_DOCUMENT13139_VT13257',  # Найдена ранее
                '_DOCUMENT137_VT8306',     # Большая таблица
                '_DOCUMENT12259_VT12322',  # Таблица с товарами
                '_DOCUMENTJOURNAL5354'     # Журнал документов
            ]
            
            for table_name in document_tables:
                if table_name in db.tables:
                    print(f"\n📊 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")
                    
                    # Находим непустые записи
                    non_empty_rows = []
                    for i in range(min(100, len(table))):  # Анализируем первые 100 записей
                        row = table[i]
                        if not row.is_empty:
                            non_empty_rows.append((i, row))
                    
                    print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                    
                    # Извлекаем данные документов
                    for i, (row_index, row) in enumerate(non_empty_rows[:20], 1):  # Первые 20 записей
                        try:
                            # Создаем структуру документа
                            document = {
                                'id': f"{table_name}_{i}",
                                'table_name': table_name,
                                'row_index': row_index,
                                'fields': {}
                            }
                            
                            # Используем метод as_dict() для извлечения данных
                            try:
                                row_dict = row.as_dict()
                                if row_dict:
                                    for field_name, value in row_dict.items():
                                        if value is not None:
                                            # Преобразуем бинарные данные в строку
                                            if isinstance(value, bytes):
                                                value = value.hex()
                                            document['fields'][field_name] = value
                            except Exception as e:
                                print(f"      ⚠️ Ошибка as_dict(): {e}")
                            
                            # Если as_dict() не сработал, пробуем as_list()
                            if not document['fields']:
                                try:
                                    row_list = row.as_list()
                                    if row_list:
                                        field_names = list(table.fields.keys())
                                        for j, value in enumerate(row_list):
                                            if j < len(field_names) and value is not None:
                                                field_name = field_names[j]
                                                # Преобразуем бинарные данные в строку
                                                if isinstance(value, bytes):
                                                    value = value.hex()
                                                document['fields'][field_name] = value
                                except Exception as e:
                                    print(f"      ⚠️ Ошибка as_list(): {e}")
                            
                            all_documents['documents'].append(document)
                            all_documents['metadata']['total_documents'] += 1
                            
                            # Показываем результат для первой записи
                            if i == 1:
                                print(f"   📄 Пример первой записи:")
                                for field_name, value in document['fields'].items():
                                    if isinstance(value, str) and len(value) > 50:
                                        value = value[:50] + "..."
                                    print(f"      {field_name}: {value}")
                        
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
                            continue
                    
                    print(f"   📄 Извлечено {len([d for d in all_documents['documents'] if d['table_name'] == table_name])} документов из {table_name}")
            
            # Сохраняем результат в JSON
            output_file = 'extracted_with_methods.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_documents, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с реальными данными
            create_methods_xml(all_documents)
            
            # Анализируем структуру данных
            analyze_extracted_data(all_documents)
            
            print(f"\n✅ Извлечение завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_methods_xml(documents):
    """
    Создание XML с данными, извлеченными методами
    """
    print(f"\n📄 Создание XML с данными:")
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>""" + documents['metadata']['extraction_date'] + """</ExtractionDate>
    <SourceFile>""" + documents['metadata']['source_file'] + """</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
  </Metadata>
  
  <Documents>
"""
    
    # Добавляем все документы
    for i, doc in enumerate(documents['documents'], 1):
        xml_content += f"""    <Document>
      <ID>{doc['id']}</ID>
      <TableName>{doc['table_name']}</TableName>
      <RowIndex>{doc['row_index']}</RowIndex>
      <Fields>
"""
        for field_name, value in doc['fields'].items():
            xml_content += f"""        <{field_name}>{value}</{field_name}>
"""
        xml_content += """      </Fields>
    </Document>
"""
    
    xml_content += """  </Documents>
</Documents>"""
    
    with open('extracted_with_methods.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML с данными: extracted_with_methods.xml")

def analyze_extracted_data(documents):
    """
    Анализ извлеченных данных
    """
    print(f"\n🔍 Анализ извлеченных данных:")
    
    # Анализируем поля
    all_fields = set()
    field_counts = {}
    
    for doc in documents['documents']:
        for field_name in doc['fields'].keys():
            all_fields.add(field_name)
            field_counts[field_name] = field_counts.get(field_name, 0) + 1
    
    print(f"   📊 Всего уникальных полей: {len(all_fields)}")
    print(f"   📋 Топ-10 полей по частоте:")
    
    # Сортируем поля по частоте
    sorted_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (field_name, count) in enumerate(sorted_fields[:10], 1):
        print(f"      {i}. {field_name}: {count} раз")
    
    # Анализируем типы данных
    print(f"\n   📊 Анализ типов данных:")
    for doc in documents['documents'][:5]:  # Первые 5 документов
        print(f"      Документ {doc['id']}:")
        for field_name, value in doc['fields'].items():
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"         {field_name}: {value}")

if __name__ == "__main__":
    extract_with_methods() 