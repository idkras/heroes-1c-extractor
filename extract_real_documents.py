#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_real_documents():
    """
    Извлечение реальных данных документов с анализом связей
    """
    print("🔍 Извлечение реальных данных документов")
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
                    for i in range(min(500, len(table))):  # Анализируем больше записей
                        row = table[i]
                        if not row.is_empty:
                            non_empty_rows.append((i, row))
                    
                    print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                    
                    # Извлекаем данные документов
                    for i, (row_index, row) in enumerate(non_empty_rows[:50], 1):  # Первые 50 записей
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
                            
                            # Анализируем тип документа по полям
                            document_type = analyze_document_type(document, table_name)
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
            output_file = 'real_documents.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML с реальными данными
            create_real_xml(documents)
            
            print(f"\n✅ Извлечение завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def analyze_document_type(document, table_name):
    """
    Анализ типа документа по полям
    """
    fields = document['fields']
    
    # Анализируем по названию таблицы
    if 'VT' in table_name:
        # Это табличная часть документа
        if '_FLD13261' in fields:  # Количество
            quantity = fields['_FLD13261']
            if quantity and quantity > 0:
                if '_FLD13267' in fields and fields['_FLD13267'] > 0:
                    return 'acts'  # Акт выполненных работ
                else:
                    return 'waybills'  # Накладная
    
    # Анализируем по полям
    if '_FLD8313' in fields or '_FLD8311' in fields:  # Поля с ценами
        return 'invoices'  # Счет-фактура
    
    if '_FLD12325' in fields or '_FLD12326' in fields:  # Поля с товарами
        return 'waybills'  # Накладная
    
    return None

def create_real_xml(documents):
    """
    Создание XML с реальными данными
    """
    print(f"\n📄 Создание XML с реальными данными:")
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>""" + documents['metadata']['extraction_date'] + """</ExtractionDate>
    <SourceFile>""" + documents['metadata']['source_file'] + """</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
  </Metadata>
  
  <Acts>
"""
    
    # Добавляем реальные акты
    for i, act in enumerate(documents['acts'][:10], 1):  # Первые 10 актов
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
    
    # Добавляем реальные счета-фактуры
    for i, invoice in enumerate(documents['invoices'][:10], 1):  # Первые 10 счетов
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
    
    # Добавляем реальные накладные
    for i, waybill in enumerate(documents['waybills'][:10], 1):  # Первые 10 накладных
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
    
    with open('real_documents.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"   📄 Создан XML с реальными данными: real_documents.xml")

if __name__ == "__main__":
    extract_real_documents() 