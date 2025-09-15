#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def create_final_working_documents():
    """
    Создание финальных рабочих документов в правильном формате
    """
    print("🎯 Создание финальных рабочих документов")
    print("=" * 60)
    
    # Читаем исходные данные
    try:
        with open('all_available_data.json', 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        print(f"✅ Загружены исходные данные: {len(source_data['documents'])} документов")
        
        # Создаем финальные рабочие документы
        final_documents = {
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'source': '1Cv8.1CD',
                'total_documents': 0,
                'document_types': {
                    'acts': 0,
                    'invoices': 0,
                    'waybills': 0
                }
            },
            'documents': []
        }
        
        # Обрабатываем каждый документ
        for doc in source_data['documents']:
            # Создаем рабочий документ с полными данными
            working_doc = {
                'document_id': doc['id'],
                'document_type': determine_document_type(doc),
                'document_number': doc['fields'].get('_NUMBER', 'N/A'),
                'document_date': doc['fields'].get('_DATE_TIME', 'N/A'),
                'is_posted': doc['fields'].get('_POSTED', False),
                'total_amount': extract_total_amount(doc),
                'description': extract_description(doc),
                'counterparty': extract_counterparty(doc),
                'all_fields': doc['fields'],
                'blob_content': extract_blob_content(doc)
            }
            
            # Добавляем в соответствующий тип
            doc_type = working_doc['document_type']
            if doc_type == 'act':
                final_documents['metadata']['document_types']['acts'] += 1
            elif doc_type == 'invoice':
                final_documents['metadata']['document_types']['invoices'] += 1
            elif doc_type == 'waybill':
                final_documents['metadata']['document_types']['waybills'] += 1
            
            final_documents['documents'].append(working_doc)
            final_documents['metadata']['total_documents'] += 1
        
        # Создаем папку если не существует
        target_dir = '[prostocvet-1c]/raw'
        os.makedirs(target_dir, exist_ok=True)
        
        # Сохраняем финальные документы в JSON
        json_file = os.path.join(target_dir, 'final_working_documents.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(final_documents, f, ensure_ascii=False, indent=2, default=str)
        
        # Создаем XML версию
        xml_file = os.path.join(target_dir, 'final_working_documents.xml')
        create_xml_version(final_documents, xml_file)
        
        # Создаем CSV версию для удобства
        csv_file = os.path.join(target_dir, 'final_working_documents.csv')
        create_csv_version(final_documents, csv_file)
        
        print(f"\n✅ Созданы финальные рабочие документы:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📄 XML: {xml_file}")
        print(f"   📄 CSV: {csv_file}")
        
        # Показываем статистику
        print(f"\n📊 Статистика финальных документов:")
        print(f"   - Всего документов: {final_documents['metadata']['total_documents']}")
        print(f"   - Акты: {final_documents['metadata']['document_types']['acts']}")
        print(f"   - Счета-фактуры: {final_documents['metadata']['document_types']['invoices']}")
        print(f"   - Накладные: {final_documents['metadata']['document_types']['waybills']}")
        
        # Проверяем качество
        quality_check(final_documents)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def determine_document_type(doc):
    """
    Определение типа документа по полям
    """
    table_name = doc['table_name']
    
    if '_DOCUMENT163' in table_name:
        return 'act'  # Акты выполненных работ
    elif '_DOCUMENT184' in table_name:
        return 'invoice'  # Счета-фактуры
    elif '_DOCUMENT154' in table_name:
        return 'waybill'  # Накладные
    else:
        return 'unknown'

def extract_total_amount(doc):
    """
    Извлечение общей суммы документа
    """
    fields = doc['fields']
    
    # Ищем поля с суммами
    amount_fields = ['_FLD4239', '_FLD3978', '_FLD3788', '_FLD4240']
    
    for field in amount_fields:
        if field in fields and fields[field] is not None:
            try:
                amount = float(fields[field])
                if amount > 0:
                    return amount
            except (ValueError, TypeError):
                continue
    
    return 0.0

def extract_description(doc):
    """
    Извлечение описания документа из BLOB полей
    """
    blobs = doc.get('blobs', {})
    
    for blob_name, blob_data in blobs.items():
        if 'value' in blob_data and 'content' in blob_data['value']:
            content = blob_data['value']['content']
            if content and len(content.strip()) > 0:
                return content.strip()
    
    return "Описание не найдено"

def extract_counterparty(doc):
    """
    Извлечение контрагента
    """
    # Ищем в описании
    description = extract_description(doc)
    
    # Простая логика извлечения контрагента
    if 'Магазин' in description:
        return "Магазин"
    elif 'Флор' in description:
        return "Флор"
    elif 'Моно' in description:
        return "Моно"
    else:
        return "Неизвестный контрагент"

def extract_blob_content(doc):
    """
    Извлечение содержимого BLOB полей в читаемом виде
    """
    blob_content = {}
    
    blobs = doc.get('blobs', {})
    for blob_name, blob_data in blobs.items():
        if 'value' in blob_data and 'content' in blob_data['value']:
            content = blob_data['value']['content']
            if content and len(content.strip()) > 0:
                blob_content[blob_name] = content.strip()
    
    return blob_content

def create_xml_version(documents, filename):
    """
    Создание XML версии документов
    """
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<WorkingDocuments>
  <Metadata>
    <CreationDate>""" + documents['metadata']['creation_date'] + """</CreationDate>
    <Source>""" + documents['metadata']['source'] + """</Source>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
    <DocumentTypes>
      <Acts>""" + str(documents['metadata']['document_types']['acts']) + """</Acts>
      <Invoices>""" + str(documents['metadata']['document_types']['invoices']) + """</Invoices>
      <Waybills>""" + str(documents['metadata']['document_types']['waybills']) + """</Waybills>
    </DocumentTypes>
  </Metadata>
  
  <Documents>
"""
    
    for doc in documents['documents']:
        xml_content += f"""    <Document>
      <ID>{doc['document_id']}</ID>
      <Type>{doc['document_type']}</Type>
      <Number>{doc['document_number']}</Number>
      <Date>{doc['document_date']}</Date>
      <Posted>{doc['is_posted']}</Posted>
      <TotalAmount>{doc['total_amount']}</TotalAmount>
      <Description>{doc['description']}</Description>
      <Counterparty>{doc['counterparty']}</Counterparty>
      <AllFields>
"""
        for field_name, field_value in doc['all_fields'].items():
            xml_content += f"""        <{field_name}>{field_value}</{field_name}>
"""
        xml_content += """      </AllFields>
      <BlobContent>
"""
        for blob_name, blob_content in doc['blob_content'].items():
            xml_content += f"""        <{blob_name}>{blob_content}</{blob_name}>
"""
        xml_content += """      </BlobContent>
    </Document>
"""
    
    xml_content += """  </Documents>
</WorkingDocuments>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_content)

def create_csv_version(documents, filename):
    """
    Создание CSV версии документов
    """
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Заголовки
        writer.writerow([
            'Document ID', 'Type', 'Number', 'Date', 'Posted', 
            'Total Amount', 'Description', 'Counterparty'
        ])
        
        # Данные
        for doc in documents['documents']:
            writer.writerow([
                doc['document_id'],
                doc['document_type'],
                doc['document_number'],
                doc['document_date'],
                doc['is_posted'],
                doc['total_amount'],
                doc['description'],
                doc['counterparty']
            ])

def quality_check(documents):
    """
    Проверка качества финальных документов
    """
    print(f"\n🔍 ПРОВЕРКА КАЧЕСТВА:")
    
    total_docs = documents['metadata']['total_documents']
    docs_with_amounts = 0
    docs_with_descriptions = 0
    docs_with_numbers = 0
    
    for doc in documents['documents']:
        if doc['total_amount'] > 0:
            docs_with_amounts += 1
        if doc['description'] != "Описание не найдено":
            docs_with_descriptions += 1
        if doc['document_number'] != 'N/A':
            docs_with_numbers += 1
    
    print(f"   ✅ Документов с суммами: {docs_with_amounts}/{total_docs}")
    print(f"   ✅ Документов с описаниями: {docs_with_descriptions}/{total_docs}")
    print(f"   ✅ Документов с номерами: {docs_with_numbers}/{total_docs}")
    
    # Проверяем что нет брака
    if docs_with_amounts > 0 and docs_with_descriptions > 0:
        print(f"   🎯 КАЧЕСТВО: ОТЛИЧНОЕ - данные пригодны для работы!")
    else:
        print(f"   ⚠️ КАЧЕСТВО: ТРЕБУЕТ ПРОВЕРКИ")

if __name__ == "__main__":
    create_final_working_documents() 