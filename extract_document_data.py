#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from onec_dtools.database_reader import DatabaseReader
import json
import sys
import os
from datetime import datetime

def extract_document_data():
    """
    Извлечение данных документов и создание структурированного output'а
    """
    print("🔍 Извлечение данных документов")
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
            
            # Анализируем таблицу _DOCUMENT13139_VT13257 (найдена ранее)
            table_name = '_DOCUMENT13139_VT13257'
            
            if table_name in db.tables:
                table = db.tables[table_name]
                print(f"\n📊 Анализ таблицы: {table_name}")
                print(f"   📈 Всего записей: {len(table):,}")
                
                # Находим непустые записи
                non_empty_rows = []
                for i in range(min(1000, len(table))):  # Анализируем первые 1000 записей
                    row = table[i]
                    if not row.is_empty:
                        non_empty_rows.append((i, row))
                
                print(f"   ✅ Найдено {len(non_empty_rows)} непустых записей")
                
                # Извлекаем данные документов
                for i, (row_index, row) in enumerate(non_empty_rows[:100], 1):  # Первые 100 записей
                    try:
                        # Создаем структуру документа
                        document = {
                            'id': str(i),
                            'row_index': row_index,
                            'document_id': str(getattr(row, '_DOCUMENT13139_IDRREF', '')),
                            'line_number': getattr(row, '_LINENO13258', 0),
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
                        
                        # Определяем тип документа по полям
                        if '_FLD13261' in document['fields']:
                            quantity = document['fields']['_FLD13261']
                            if quantity and quantity > 0:
                                # Это похоже на документ с товарами
                                if '_FLD13267' in document['fields'] and document['fields']['_FLD13267'] > 0:
                                    # Возможно акт выполненных работ
                                    documents['acts'].append(document)
                                else:
                                    # Возможно накладная или счет-фактура
                                    documents['waybills'].append(document)
                        
                        documents['metadata']['total_documents'] += 1
                        
                    except Exception as e:
                        print(f"   ⚠️ Ошибка при обработке записи {i}: {e}")
                        continue
                
                print(f"   📄 Извлечено документов:")
                print(f"      - Акты: {len(documents['acts'])}")
                print(f"      - Накладные: {len(documents['waybills'])}")
                print(f"      - Счета-фактуры: {len(documents['invoices'])}")
            
            # Сохраняем результат в JSON
            output_file = 'extracted_documents.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Результат сохранен в: {output_file}")
            
            # Создаем XML структуру для примера
            create_xml_example(documents)
            
            print(f"\n✅ Извлечение завершено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def create_xml_example(documents):
    """
    Создание примера XML структуры документов
    """
    print(f"\n📄 Создание примера XML структуры:")
    
    xml_example = """<?xml version="1.0" encoding="UTF-8"?>
<Documents>
  <Metadata>
    <ExtractionDate>2024-01-15T10:30:00</ExtractionDate>
    <SourceFile>raw/1Cv8.1CD</SourceFile>
    <TotalDocuments>""" + str(documents['metadata']['total_documents']) + """</TotalDocuments>
  </Metadata>
  
  <Acts>
    <!-- Пример акта выполненных работ -->
    <Act>
      <Number>000000001</Number>
      <Date>2024-01-15</Date>
      <Contractor>ИП Иванов</Contractor>
      <Amount>5000.00</Amount>
      <TablePart>
        <Row>
          <Nomenclature>Букет 'Свадебный'</Nomenclature>
          <Quantity>1</Quantity>
          <Price>5000.00</Price>
          <Amount>5000.00</Amount>
        </Row>
      </TablePart>
    </Act>
  </Acts>
  
  <Invoices>
    <!-- Пример счета-фактуры -->
    <Invoice>
      <Number>000000001</Number>
      <Date>2024-01-15</Date>
      <Contractor>ООО 'Цветочный рай'</Contractor>
      <Amount>12000.00</Amount>
      <TablePart>
        <Row>
          <Nomenclature>Роза красная</Nomenclature>
          <Quantity>100</Quantity>
          <Price>120.00</Price>
          <Amount>12000.00</Amount>
        </Row>
      </TablePart>
    </Invoice>
  </Invoices>
  
  <Waybills>
    <!-- Пример накладной -->
    <Waybill>
      <Number>000000001</Number>
      <Date>2024-01-15</Date>
      <Warehouse>Основной склад</Warehouse>
      <Contractor>ООО 'Цветочный рай'</Contractor>
      <TablePart>
        <Row>
          <Nomenclature>Роза красная</Nomenclature>
          <Quantity>100</Quantity>
          <Price>120.00</Price>
          <Amount>12000.00</Amount>
        </Row>
      </TablePart>
    </Waybill>
  </Waybills>
</Documents>"""
    
    with open('documents_example.xml', 'w', encoding='utf-8') as f:
        f.write(xml_example)
    
    print(f"   📄 Создан пример XML: documents_example.xml")

if __name__ == "__main__":
    extract_document_data() 