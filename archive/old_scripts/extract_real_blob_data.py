#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_real_blob_data():
    """
    Извлечение реальных BLOB данных из документов
    """
    print("🔍 Извлечение реальных BLOB данных")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Анализируем основные таблицы документов
            document_tables = [
                '_DOCUMENT163',  # Большая таблица с реальными данными
                '_DOCUMENT184',  # Таблица с BLOB данными
                '_DOCUMENT154'   # Таблица с суммами
            ]
            
            blob_results = {
                'documents': [],
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_documents': 0,
                    'total_blobs': 0,
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            for table_name in document_tables:
                if table_name in db.tables:
                    print(f"\n📊 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")
                    
                    # Находим непустые записи
                    non_empty_rows = []
                    for i in range(min(20, len(table))):  # Анализируем первые 20 записей
                        row = table[i]
                        if not row.is_empty:
                            non_empty_rows.append((i, row))
                    
                    print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                    
                    # Извлекаем данные документов
                    for i, (row_index, row) in enumerate(non_empty_rows[:5], 1):  # Первые 5 записей
                        try:
                            # Извлекаем данные через as_dict()
                            row_dict = row.as_dict()
                            if not row_dict:
                                continue
                            
                            # Создаем структуру документа
                            document = {
                                'id': f"{table_name}_{i}",
                                'table_name': table_name,
                                'row_index': row_index,
                                'fields': {},
                                'blobs': {}
                            }
                            
                            # Обрабатываем поля
                            for field_name, value in row_dict.items():
                                if value is not None:
                                    # Преобразуем datetime в строку
                                    if isinstance(value, datetime):
                                        value = value.isoformat()
                                    # Преобразуем бинарные данные в строку
                                    elif isinstance(value, bytes):
                                        value = value.hex()
                                    # Обрабатываем Blob объекты
                                    elif hasattr(value, '__class__') and 'Blob' in str(value.__class__):
                                        try:
                                            # Получаем содержимое BLOB через атрибут value
                                            if hasattr(value, 'value'):
                                                blob_content = value.value
                                                document['blobs'][field_name] = {
                                                    'size': len(blob_content) if blob_content else 0,
                                                    'content': blob_content,
                                                    'type': 'text'
                                                }
                                                blob_results['metadata']['total_blobs'] += 1
                                            else:
                                                document['blobs'][field_name] = {'error': 'no value attribute'}
                                        except Exception as e:
                                            document['blobs'][field_name] = {'error': str(e)}
                                    else:
                                        document['fields'][field_name] = value
                            
                            blob_results['documents'].append(document)
                            blob_results['metadata']['total_documents'] += 1
                            
                            # Показываем результат для первой записи
                            if i == 1:
                                print(f"   📄 Пример первой записи:")
                                print(f"      Номер: {document['fields'].get('_NUMBER', 'N/A')}")
                                print(f"      Дата: {document['fields'].get('_DATE_TIME', 'N/A')}")
                                print(f"      Сумма: {document['fields'].get('_FLD3978', 'N/A')}")
                                print(f"      BLOB полей: {len(document['blobs'])}")
                                for blob_name, blob_data in document['blobs'].items():
                                    if 'content' in blob_data:
                                        content = blob_data['content']
                                        if content:
                                            print(f"         {blob_name}: '{content[:100]}{'...' if len(content) > 100 else ''}'")
                                        else:
                                            print(f"         {blob_name}: пустой")
                                    else:
                                        print(f"         {blob_name}: ошибка - {blob_data.get('error', 'unknown')}")
                        
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
                            continue
                    
                    print(f"   📄 Извлечено {len([d for d in blob_results['documents'] if d['table_name'] == table_name])} документов из {table_name}")
            
            # Сохраняем результат в JSON
            output_file = 'real_blob_data.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(blob_results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с реальными BLOB данными
            create_real_blob_xml(blob_results)
            
            print(f"\n✅ Извлечение BLOB завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_real_blob_xml(documents):
    """
    Создание XML с реальными BLOB данными
    """
    print(f"\n📄 Создание XML с реальными BLOB данными:")
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>""" + documents['metadata']['extraction_date'] + """</ExtractionDate>
    <SourceFile>""" + documents['metadata']['source_file'] + """</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
    <TotalBlobs>""" + str(documents['metadata']['total_blobs']) + """</TotalBlobs>
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
      <Blobs>
"""
        for blob_name, blob_data in doc['blobs'].items():
            xml_content += f"""        <{blob_name}>
          <Size>{blob_data.get('size', 0)}</Size>
          <Type>{blob_data.get('type', 'unknown')}</Type>
"""
            if 'content' in blob_data and blob_data['content']:
                xml_content += f"""          <Content>{blob_data['content']}</Content>
"""
            elif 'error' in blob_data:
                xml_content += f"""          <Error>{blob_data['error']}</Error>
"""
            xml_content += f"""        </{blob_name}>
"""
        xml_content += """      </Blobs>
    </Document>
"""
    
    xml_content += """  </Documents>
</Documents>"""
    
    with open('real_blob_data.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML с реальными BLOB данными: real_blob_data.xml")
    
    # Показываем статистику
    print(f"\n📊 Статистика извлечения BLOB:")
    print(f"   - Документов: {documents['metadata']['total_documents']}")
    print(f"   - BLOB полей: {documents['metadata']['total_blobs']}")

if __name__ == "__main__":
    extract_real_blob_data() 