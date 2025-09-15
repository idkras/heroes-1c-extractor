#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def create_clean_working_documents():
    """
    Создание очищенной версии только с качественными документами
    """
    print("🎯 Создание очищенных рабочих документов")
    print("=" * 60)
    
    # Читаем исходные данные
    json_file = '[prostocvet-1c]/raw/final_working_documents.json'
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        print(f"✅ Загружены исходные данные: {len(source_data['documents'])} документов")
        
        # Фильтруем только качественные документы
        quality_documents = []
        
        for doc in source_data['documents']:
            # Проверяем качество документа
            has_amount = doc['total_amount'] > 0
            has_description = doc['description'] != "Описание не найдено"
            has_number = doc['document_number'] != 'N/A'
            has_counterparty = doc['counterparty'] != "Неизвестный контрагент"
            has_blob_content = len(doc['blob_content']) > 0
            
            # Определяем качество документа
            quality_score = sum([has_amount, has_description, has_number, has_counterparty, has_blob_content])
            
            # Берем только документы с качеством 3+ баллов
            if quality_score >= 3:
                quality_documents.append(doc)
                print(f"   ✅ {doc['document_id']}: {doc['document_type']} - {doc['document_number']} - {doc['total_amount']} руб.")
            else:
                print(f"   ❌ {doc['document_id']}: {doc['document_type']} - {doc['document_number']} - ОТБРАКОВАН")
        
        # Создаем очищенные документы
        clean_documents = {
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'source': '1Cv8.1CD',
                'total_documents': len(quality_documents),
                'original_documents': len(source_data['documents']),
                'filtered_out': len(source_data['documents']) - len(quality_documents),
                'document_types': {
                    'acts': 0,
                    'invoices': 0,
                    'waybills': 0
                }
            },
            'documents': quality_documents
        }
        
        # Подсчитываем типы документов
        for doc in quality_documents:
            doc_type = doc['document_type']
            if doc_type == 'act':
                clean_documents['metadata']['document_types']['acts'] += 1
            elif doc_type == 'invoice':
                clean_documents['metadata']['document_types']['invoices'] += 1
            elif doc_type == 'waybill':
                clean_documents['metadata']['document_types']['waybills'] += 1
        
        # Создаем папку если не существует
        target_dir = '[prostocvet-1c]/raw'
        os.makedirs(target_dir, exist_ok=True)
        
        # Сохраняем очищенные документы в JSON
        clean_json_file = os.path.join(target_dir, 'clean_working_documents.json')
        with open(clean_json_file, 'w', encoding='utf-8') as f:
            json.dump(clean_documents, f, ensure_ascii=False, indent=2, default=str)
        
        # Создаем XML версию
        clean_xml_file = os.path.join(target_dir, 'clean_working_documents.xml')
        create_clean_xml_version(clean_documents, clean_xml_file)
        
        # Создаем CSV версию для удобства
        clean_csv_file = os.path.join(target_dir, 'clean_working_documents.csv')
        create_clean_csv_version(clean_documents, clean_csv_file)
        
        print(f"\n✅ Созданы очищенные рабочие документы:")
        print(f"   📄 JSON: {clean_json_file}")
        print(f"   📄 XML: {clean_xml_file}")
        print(f"   📄 CSV: {clean_csv_file}")
        
        # Показываем статистику
        print(f"\n📊 Статистика очищенных документов:")
        print(f"   - Исходных документов: {clean_documents['metadata']['original_documents']}")
        print(f"   - Отфильтровано: {clean_documents['metadata']['filtered_out']}")
        print(f"   - Качественных документов: {clean_documents['metadata']['total_documents']}")
        print(f"   - Акты: {clean_documents['metadata']['document_types']['acts']}")
        print(f"   - Счета-фактуры: {clean_documents['metadata']['document_types']['invoices']}")
        print(f"   - Накладные: {clean_documents['metadata']['document_types']['waybills']}")
        
        # Проверяем качество очищенных документов
        quality_check_clean(clean_documents)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def create_clean_xml_version(documents, filename):
    """
    Создание XML версии очищенных документов
    """
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CleanWorkingDocuments>
  <Metadata>
    <CreationDate>""" + documents['metadata']['creation_date'] + """</CreationDate>
    <Source>""" + documents['metadata']['source'] + """</Source>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
    <OriginalDocuments>""" + str(documents['metadata']['original_documents']) + """</OriginalDocuments>
    <FilteredOut>""" + str(documents['metadata']['filtered_out']) + """</FilteredOut>
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
</CleanWorkingDocuments>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_content)

def create_clean_csv_version(documents, filename):
    """
    Создание CSV версии очищенных документов
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

def quality_check_clean(documents):
    """
    Проверка качества очищенных документов
    """
    print(f"\n🔍 ПРОВЕРКА КАЧЕСТВА ОЧИЩЕННЫХ ДОКУМЕНТОВ:")
    
    total_docs = documents['metadata']['total_documents']
    docs_with_amounts = 0
    docs_with_descriptions = 0
    docs_with_numbers = 0
    docs_with_counterparties = 0
    docs_with_blob_content = 0
    
    for doc in documents['documents']:
        if doc['total_amount'] > 0:
            docs_with_amounts += 1
        if doc['description'] != "Описание не найдено":
            docs_with_descriptions += 1
        if doc['document_number'] != 'N/A':
            docs_with_numbers += 1
        if doc['counterparty'] != "Неизвестный контрагент":
            docs_with_counterparties += 1
        if len(doc['blob_content']) > 0:
            docs_with_blob_content += 1
    
    print(f"   ✅ Документов с суммами: {docs_with_amounts}/{total_docs}")
    print(f"   ✅ Документов с описаниями: {docs_with_descriptions}/{total_docs}")
    print(f"   ✅ Документов с номерами: {docs_with_numbers}/{total_docs}")
    print(f"   ✅ Документов с контрагентами: {docs_with_counterparties}/{total_docs}")
    print(f"   ✅ Документов с BLOB содержимым: {docs_with_blob_content}/{total_docs}")
    
    # Проверяем что нет брака
    if docs_with_amounts > 0 and docs_with_descriptions > 0:
        print(f"   🎯 КАЧЕСТВО: ОТЛИЧНОЕ - данные пригодны для работы!")
        print(f"   ✅ НЕТ БРАКА - все документы качественные!")
    else:
        print(f"   ⚠️ КАЧЕСТВО: ТРЕБУЕТ ПРОВЕРКИ")

if __name__ == "__main__":
    create_clean_working_documents() 