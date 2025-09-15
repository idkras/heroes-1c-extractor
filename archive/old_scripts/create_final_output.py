#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def create_final_output():
    """
    Создание финального output'а с актами, счетами-фактурами и накладными
    """
    print("🔍 Создание финального output'а")
    print("=" * 60)
    
    try:
        with open('raw/1Cv8.1CD', 'rb') as f:
            db = DatabaseReader(f)
            
            print(f"✅ База данных открыта успешно!")
            
            # Структура для хранения документов
            documents = {
                'acts': [],
                'invoices': [],
                'waybills': [],
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'total_documents': 0,
                    'source_file': 'raw/1Cv8.1CD'
                }
            }
            
            # Анализируем таблицы документов
            document_tables = [
                '_DOCUMENT13139_VT13257',  # Табличная часть документа
                '_DOCUMENT137_VT8306',     # Табличная часть документа
                '_DOCUMENT12259_VT12322',  # Табличная часть документа
                '_DOCUMENTJOURNAL5354'     # Журнал документов
            ]
            
            for table_name in document_tables:
                if table_name in db.tables:
                    print(f"\n📊 Анализ таблицы: {table_name}")
                    table = db.tables[table_name]
                    print(f"   📈 Всего записей: {len(table):,}")
                    
                    # Находим непустые записи
                    non_empty_rows = []
                    for i in range(min(50, len(table))):
                        row = table[i]
                        if not row.is_empty:
                            non_empty_rows.append((i, row))
                    
                    print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                    
                    # Извлекаем данные документов
                    for i, (row_index, row) in enumerate(non_empty_rows[:10], 1):
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
                                'fields': {}
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
                                    # Преобразуем Blob в строку
                                    elif hasattr(value, '__class__') and 'Blob' in str(value.__class__):
                                        value = str(value)
                                    
                                    document['fields'][field_name] = value
                            
                            # Классифицируем документ
                            document_type = classify_document(document, table_name)
                            if document_type:
                                documents[document_type].append(document)
                            
                            documents['metadata']['total_documents'] += 1
                            
                        except Exception as e:
                            print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
                            continue
                    
                    print(f"   📄 Извлечено из {table_name}:")
                    print(f"      - Акты: {len([d for d in documents['acts'] if d['table_name'] == table_name])}")
                    print(f"      - Накладные: {len([d for d in documents['waybills'] if d['table_name'] == table_name])}")
                    print(f"      - Счета-фактуры: {len([d for d in documents['invoices'] if d['table_name'] == table_name])}")
            
            # Сохраняем результат в JSON
            output_file = 'final_documents.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с финальными данными
            create_final_xml(documents)
            
            print(f"\n✅ Создание финального output'а завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def classify_document(document, table_name):
    """
    Классификация документа по полям
    """
    fields = document['fields']
    
    # Анализируем по полям
    if '_FLD13261' in fields and fields['_FLD13261'] > 0:
        # Поле с количеством
        if '_FLD13267' in fields and fields['_FLD13267'] > 0:
            return 'acts'  # Акт выполненных работ
        else:
            return 'waybills'  # Накладная
    
    if '_FLD8313' in fields or '_FLD8311' in fields:
        # Поля с ценами
        return 'invoices'  # Счет-фактура
    
    if '_FLD12325' in fields or '_FLD12326' in fields:
        # Поля с товарами
        return 'waybills'  # Накладная
    
    # По умолчанию считаем накладной
    return 'waybills'

def create_final_xml(documents):
    """
    Создание XML с финальными данными
    """
    print(f"\n📄 Создание XML с финальными данными:")
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>""" + documents['metadata']['extraction_date'] + """</ExtractionDate>
    <SourceFile>""" + documents['metadata']['source_file'] + """</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
  </Metadata>
  
  <Acts>
"""
    
    # Добавляем акты
    for i, act in enumerate(documents['acts'], 1):
        xml_content += f"""    <Act>
      <ID>{act['id']}</ID>
      <TableName>{act['table_name']}</TableName>
      <RowIndex>{act['row_index']}</RowIndex>
      <Fields>
"""
        for field_name, value in act['fields'].items():
            xml_content += f"""        <{field_name}>{value}</{field_name}>
"""
        xml_content += """      </Fields>
    </Act>
"""
    
    xml_content += """  </Acts>
  
  <Invoices>
"""
    
    # Добавляем счета-фактуры
    for i, invoice in enumerate(documents['invoices'], 1):
        xml_content += f"""    <Invoice>
      <ID>{invoice['id']}</ID>
      <TableName>{invoice['table_name']}</TableName>
      <RowIndex>{invoice['row_index']}</RowIndex>
      <Fields>
"""
        for field_name, value in invoice['fields'].items():
            xml_content += f"""        <{field_name}>{value}</{field_name}>
"""
        xml_content += """      </Fields>
    </Invoice>
"""
    
    xml_content += """  </Invoices>
  
  <Waybills>
"""
    
    # Добавляем накладные
    for i, waybill in enumerate(documents['waybills'], 1):
        xml_content += f"""    <Waybill>
      <ID>{waybill['id']}</ID>
      <TableName>{waybill['table_name']}</TableName>
      <RowIndex>{waybill['row_index']}</RowIndex>
      <Fields>
"""
        for field_name, value in waybill['fields'].items():
            xml_content += f"""        <{field_name}>{value}</{field_name}>
"""
        xml_content += """      </Fields>
    </Waybill>
"""
    
    xml_content += """  </Waybills>
</Documents>"""
    
    with open('final_documents.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML с финальными данными: final_documents.xml")
    
    # Показываем статистику
    print(f"\n📊 Статистика извлечения:")
    print(f"   - Акты: {len(documents['acts'])}")
    print(f"   - Счета-фактуры: {len(documents['invoices'])}")
    print(f"   - Накладные: {len(documents['waybills'])}")
    print(f"   - Всего документов: {documents['metadata']['total_documents']}")

if __name__ == "__main__":
    create_final_output() 