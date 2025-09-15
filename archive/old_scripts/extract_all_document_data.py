#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_all_document_data():
    """
    Извлечение всех данных документов без классификации
    """
    print("🔍 Извлечение всех данных документов")
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
                            
                            # Извлекаем все поля
                            for field_name, field_desc in table.fields.items():
                                value = getattr(row, field_name, None)
                                if value is not None:
                                    # Преобразуем бинарные данные в строку
                                    if isinstance(value, bytes):
                                        value = value.hex()
                                    document['fields'][field_name] = value
                            
                            all_documents['documents'].append(document)
                            all_documents['metadata']['total_documents'] += 1
                            
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
                            continue
                    
                    print(f"   📄 Извлечено {len([d for d in all_documents['documents'] if d['table_name'] == table_name])} документов из {table_name}")
            
            # Сохраняем результат в JSON
            output_file = 'all_documents.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_documents, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с реальными данными
            create_all_xml(all_documents)
            
            # Анализируем структуру данных
            analyze_data_structure(all_documents)
            
            print(f"\n✅ Извлечение завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_all_xml(documents):
    """
    Создание XML со всеми данными
    """
    print(f"\n📄 Создание XML со всеми данными:")
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>""" + documents['metadata']['extraction_date'] + """</ExtractionDate>
    <SourceFile>""" + documents['metadata']['source_file'] + """</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
  </Metadata>
  
  <AllDocuments>
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
    
    xml_content += """  </AllDocuments>
</Documents>"""
    
    with open('all_documents.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML со всеми данными: all_documents.xml")

def analyze_data_structure(documents):
    """
    Анализ структуры данных
    """
    print(f"\n🔍 Анализ структуры данных:")
    
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
    extract_all_document_data() 