#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_complete_blob_data():
    """
    Полное извлечение BLOB данных с обработкой всех типов
    """
    print("🔍 Полное извлечение BLOB данных")
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
            
            complete_results = {
                'documents': [],
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_documents': 0,
                    'total_blobs': 0,
                    'successful_extractions': 0,
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
                    for i in range(min(10, len(table))):  # Анализируем первые 10 записей
                        row = table[i]
                        if not row.is_empty:
                            non_empty_rows.append((i, row))
                    
                    print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                    
                    # Извлекаем данные документов
                    for i, (row_index, row) in enumerate(non_empty_rows[:3], 1):  # Первые 3 записи
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
                                'blobs': {},
                                'extraction_stats': {
                                    'total_blobs': 0,
                                    'successful': 0,
                                    'failed': 0
                                }
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
                                        document['extraction_stats']['total_blobs'] += 1
                                        
                                        blob_data = {
                                            'field_type': getattr(value, '_field_type', 'unknown'),
                                            'size': getattr(value, '_size', 0),
                                            'extraction_methods': []
                                        }
                                        
                                        # Метод 1: value атрибут
                                        if hasattr(value, 'value'):
                                            try:
                                                content = value.value
                                                if content:
                                                    blob_data['value'] = {
                                                        'content': content,
                                                        'type': type(content).__name__,
                                                        'length': len(content)
                                                    }
                                                    blob_data['extraction_methods'].append('value')
                                                    document['extraction_stats']['successful'] += 1
                                            except Exception as e:
                                                blob_data['value_error'] = str(e)
                                        
                                        # Метод 2: iterator
                                        if hasattr(value, '__iter__'):
                                            try:
                                                iterator = iter(value)
                                                content = next(iterator)
                                                if content:
                                                    blob_data['iterator'] = {
                                                        'content': content,
                                                        'type': type(content).__name__,
                                                        'length': len(content)
                                                    }
                                                    blob_data['extraction_methods'].append('iterator')
                                                    document['extraction_stats']['successful'] += 1
                                            except Exception as e:
                                                blob_data['iterator_error'] = str(e)
                                        
                                        # Метод 3: bytes
                                        if hasattr(value, '__bytes__'):
                                            try:
                                                content = bytes(value)
                                                if content:
                                                    blob_data['bytes'] = {
                                                        'content': content.hex(),
                                                        'type': type(content).__name__,
                                                        'length': len(content)
                                                    }
                                                    blob_data['extraction_methods'].append('bytes')
                                                    document['extraction_stats']['successful'] += 1
                                            except Exception as e:
                                                blob_data['bytes_error'] = str(e)
                                        
                                        # Метод 4: str
                                        try:
                                            content = str(value)
                                            if content and content != repr(value):
                                                blob_data['str'] = {
                                                    'content': content,
                                                    'type': type(content).__name__,
                                                    'length': len(content)
                                                }
                                                blob_data['extraction_methods'].append('str')
                                                document['extraction_stats']['successful'] += 1
                                        except Exception as e:
                                            blob_data['str_error'] = str(e)
                                        
                                        # Если ни один метод не сработал
                                        if not blob_data['extraction_methods']:
                                            document['extraction_stats']['failed'] += 1
                                            blob_data['error'] = 'No extraction method worked'
                                        
                                        document['blobs'][field_name] = blob_data
                                        complete_results['metadata']['total_blobs'] += 1
                                        
                                        if blob_data['extraction_methods']:
                                            complete_results['metadata']['successful_extractions'] += 1
                                        
                                    else:
                                        document['fields'][field_name] = value
                            
                            complete_results['documents'].append(document)
                            complete_results['metadata']['total_documents'] += 1
                            
                            # Показываем результат для первой записи
                            if i == 1:
                                print(f"   📄 Пример первой записи:")
                                print(f"      Номер: {document['fields'].get('_NUMBER', 'N/A')}")
                                print(f"      Дата: {document['fields'].get('_DATE_TIME', 'N/A')}")
                                print(f"      Сумма: {document['fields'].get('_FLD3978', 'N/A')}")
                                print(f"      BLOB полей: {document['extraction_stats']['total_blobs']}")
                                print(f"      Успешно извлечено: {document['extraction_stats']['successful']}")
                                print(f"      Ошибок: {document['extraction_stats']['failed']}")
                                
                                for blob_name, blob_data in document['blobs'].items():
                                    if blob_data['extraction_methods']:
                                        methods = ', '.join(blob_data['extraction_methods'])
                                        print(f"         ✅ {blob_name}: {methods}")
                                    else:
                                        print(f"         ❌ {blob_name}: не извлечено")
                        
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
                            continue
                    
                    print(f"   📄 Извлечено {len([d for d in complete_results['documents'] if d['table_name'] == table_name])} документов из {table_name}")
            
            # Сохраняем результат в JSON
            output_file = 'complete_blob_data.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(complete_results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с полными BLOB данными
            create_complete_blob_xml(complete_results)
            
            print(f"\n✅ Полное извлечение BLOB завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_complete_blob_xml(documents):
    """
    Создание XML с полными BLOB данными
    """
    print(f"\n📄 Создание XML с полными BLOB данными:")
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>""" + documents['metadata']['extraction_date'] + """</ExtractionDate>
    <SourceFile>""" + documents['metadata']['source_file'] + """</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
    <TotalBlobs>""" + str(documents['metadata']['total_blobs']) + """</TotalBlobs>
    <SuccessfulExtractions>""" + str(documents['metadata']['successful_extractions']) + """</SuccessfulExtractions>
  </Metadata>
  
  <Documents>
"""
    
    # Добавляем все документы
    for i, doc in enumerate(documents['documents'], 1):
        xml_content += f"""    <Document>
      <ID>{doc['id']}</ID>
      <TableName>{doc['table_name']}</TableName>
      <RowIndex>{doc['row_index']}</RowIndex>
      <ExtractionStats>
        <TotalBlobs>{doc['extraction_stats']['total_blobs']}</TotalBlobs>
        <Successful>{doc['extraction_stats']['successful']}</Successful>
        <Failed>{doc['extraction_stats']['failed']}</Failed>
      </ExtractionStats>
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
          <FieldType>{blob_data['field_type']}</FieldType>
          <Size>{blob_data['size']}</Size>
          <ExtractionMethods>{', '.join(blob_data['extraction_methods'])}</ExtractionMethods>
"""
            # Добавляем содержимое для каждого метода
            for method in ['value', 'iterator', 'bytes', 'str']:
                if method in blob_data:
                    content = blob_data[method]['content']
                    if isinstance(content, bytes):
                        content = content.hex()
                    xml_content += f"""          <{method.capitalize()}>{content}</{method.capitalize()}>
"""
            xml_content += f"""        </{blob_name}>
"""
        xml_content += """      </Blobs>
    </Document>
"""
    
    xml_content += """  </Documents>
</Documents>"""
    
    with open('complete_blob_data.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML с полными BLOB данными: complete_blob_data.xml")
    
    # Показываем статистику
    print(f"\n📊 Статистика полного извлечения BLOB:")
    print(f"   - Документов: {documents['metadata']['total_documents']}")
    print(f"   - BLOB полей: {documents['metadata']['total_blobs']}")
    print(f"   - Успешно извлечено: {documents['metadata']['successful_extractions']}")

if __name__ == "__main__":
    extract_complete_blob_data() 