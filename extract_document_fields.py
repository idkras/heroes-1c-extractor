#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_document_fields():
    """
    Извлечение полей документов с правильным доступом к данным
    """
    print("🔍 Извлечение полей документов")
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
            
            # Анализируем таблицу _DOCUMENT13139_VT13257
            table_name = '_DOCUMENT13139_VT13257'
            
            if table_name in db.tables:
                table = db.tables[table_name]
                print(f"\n📊 Анализ таблицы: {table_name}")
                print(f"   📈 Всего записей: {len(table):,}")
                
                # Показываем структуру полей
                print(f"   📝 Структура полей:")
                for field_name, field_desc in table.fields.items():
                    print(f"      - {field_name}: тип={field_desc.type}, длина={field_desc.length}")
                
                # Находим непустые записи
                non_empty_rows = []
                for i in range(min(50, len(table))):  # Анализируем первые 50 записей
                    row = table[i]
                    if not row.is_empty:
                        non_empty_rows.append((i, row))
                
                print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                
                # Извлекаем данные документов
                for i, (row_index, row) in enumerate(non_empty_rows[:10], 1):  # Первые 10 записей
                    try:
                        # Создаем структуру документа
                        document = {
                            'id': f"{table_name}_{i}",
                            'table_name': table_name,
                            'row_index': row_index,
                            'fields': {}
                        }
                        
                        # Извлекаем все поля напрямую
                        for field_name, field_desc in table.fields.items():
                            try:
                                # Пробуем разные способы доступа к полю
                                value = None
                                
                                # Способ 1: прямой доступ
                                if hasattr(row, field_name):
                                    value = getattr(row, field_name)
                                
                                # Способ 2: доступ через индексы
                                if value is None:
                                    field_index = list(table.fields.keys()).index(field_name)
                                    if hasattr(row, '__getitem__'):
                                        value = row[field_index]
                                
                                # Способ 3: доступ через _data
                                if value is None and hasattr(row, '_data'):
                                    value = row._data.get(field_name)
                                
                                # Способ 4: доступ через __dict__
                                if value is None and hasattr(row, '__dict__'):
                                    value = row.__dict__.get(field_name)
                                
                                if value is not None:
                                    # Преобразуем бинарные данные в строку
                                    if isinstance(value, bytes):
                                        value = value.hex()
                                    document['fields'][field_name] = value
                                
                            except Exception as e:
                                print(f"      ⚠️ Ошибка при извлечении поля {field_name}: {e}")
                                continue
                        
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
            output_file = 'document_fields.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_documents, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с реальными данными
            create_fields_xml(all_documents)
            
            print(f"\n✅ Извлечение завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_fields_xml(documents):
    """
    Создание XML с полями документов
    """
    print(f"\n📄 Создание XML с полями документов:")
    
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
    
    with open('document_fields.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML с полями документов: document_fields.xml")

if __name__ == "__main__":
    extract_document_fields() 