#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ полных данных из 1CD файла
Поиск документов: акты, накладные, счета, счета-фактуры
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class CompleteOneCAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.results = {
            'documents': {
                'acts': [],
                'invoices': [],
                'waybills': [],
                'accounts': [],
                'invoices_factura': []
            },
            'catalogs': {
                'nomenclature': [],
                'flowers': [],
                'care': []
            },
            'metadata': {
                'users': [],
                'schema': [],
                'history': []
            },
            'blob_data': {}
        }

    def analyze_all_files(self):
        """Анализируем все файлы в папке данных"""
        print("Анализирую все файлы...")
        
        for file_path in self.data_dir.glob("*.xml"):
            print(f"Обрабатываю {file_path.name}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Анализируем каждый файл
                self.analyze_xml_file(file_path.name, content)
                
            except Exception as e:
                print(f"Ошибка обработки {file_path.name}: {e}")

    def analyze_xml_file(self, filename, content):
        """Анализируем конкретный XML файл"""
        
        # Анализ истории пользователей
        if filename == "_USERSWORKHISTORY.xml":
            self.analyze_users_history(content)
        
        # Анализ пользователей
        elif filename == "V8USERS.xml":
            self.analyze_users(content)
        
        # Анализ схемы БД
        elif filename == "DBSCHEMA.xml":
            self.analyze_schema(content)
        
        # Анализ справочников
        elif "REFERENCECHNGR" in filename:
            self.analyze_reference_changes(filename, content)
        
        # Поиск документов в любом файле
        self.search_for_documents(filename, content)

    def analyze_users_history(self, content):
        """Анализируем историю пользователей"""
        print("Анализирую историю пользователей...")
        
        try:
            root = ET.fromstring(content)
            records = root.findall(".//Record")
            
            for record in records:
                url_elem = record.find("_URL")
                if url_elem is not None:
                    url = url_elem.text
                    if url:
                        # Ищем документы в URL
                        if "документ" in url.lower() or "document" in url.lower():
                            doc_type = self.extract_document_type(url)
                            if doc_type:
                                self.results['metadata']['history'].append({
                                    'url': url,
                                    'type': doc_type,
                                    'record': self.extract_record_data(record)
                                })
        
        except Exception as e:
            print(f"Ошибка анализа истории: {e}")

    def extract_document_type(self, url):
        """Извлекаем тип документа из URL"""
        url_lower = url.lower()
        
        if "акт" in url_lower:
            return "act"
        elif "накладн" in url_lower:
            return "waybill"
        elif "счет" in url_lower and "фактур" in url_lower:
            return "invoice_factura"
        elif "счет" in url_lower:
            return "invoice"
        elif "заказ" in url_lower:
            return "order"
        else:
            return "other"

    def extract_record_data(self, record):
        """Извлекаем данные записи"""
        data = {}
        for child in record:
            data[child.tag] = child.text
        return data

    def analyze_users(self, content):
        """Анализируем пользователей"""
        print("Анализирую пользователей...")
        
        try:
            root = ET.fromstring(content)
            records = root.findall(".//Record")
            
            for record in records:
                user_data = self.extract_record_data(record)
                self.results['metadata']['users'].append(user_data)
        
        except Exception as e:
            print(f"Ошибка анализа пользователей: {e}")

    def analyze_schema(self, content):
        """Анализируем схему БД"""
        print("Анализирую схему БД...")
        
        try:
            root = ET.fromstring(content)
            tables = root.findall(".//Table")
            
            for table in tables:
                table_name = table.get('Name', '')
                if table_name:
                    self.results['metadata']['schema'].append({
                        'name': table_name,
                        'fields': self.extract_table_fields(table)
                    })
        
        except Exception as e:
            print(f"Ошибка анализа схемы: {e}")

    def extract_table_fields(self, table):
        """Извлекаем поля таблицы"""
        fields = []
        for field in table.findall(".//Field"):
            field_data = {
                'name': field.get('Name', ''),
                'type': field.get('Type', ''),
                'length': field.get('Length', ''),
                'precision': field.get('Precision', '')
            }
            fields.append(field_data)
        return fields

    def analyze_reference_changes(self, filename, content):
        """Анализируем изменения справочников"""
        print(f"Анализирую изменения справочников: {filename}")
        
        try:
            root = ET.fromstring(content)
            records = root.findall(".//Record")
            
            for record in records:
                ref_data = self.extract_record_data(record)
                self.results['catalogs']['nomenclature'].append({
                    'file': filename,
                    'data': ref_data
                })
        
        except Exception as e:
            print(f"Ошибка анализа справочников: {e}")

    def search_for_documents(self, filename, content):
        """Ищем документы в любом файле"""
        content_lower = content.lower()
        
        # Ищем упоминания документов
        if "акт" in content_lower:
            self.results['documents']['acts'].append({
                'file': filename,
                'matches': self.find_matches(content, "акт")
            })
        
        if "накладн" in content_lower:
            self.results['documents']['waybills'].append({
                'file': filename,
                'matches': self.find_matches(content, "накладн")
            })
        
        if "счет" in content_lower:
            if "фактур" in content_lower:
                self.results['documents']['invoices_factura'].append({
                    'file': filename,
                    'matches': self.find_matches(content, "счет.*фактур")
                })
            else:
                self.results['documents']['invoices'].append({
                    'file': filename,
                    'matches': self.find_matches(content, "счет")
                })

    def find_matches(self, content, pattern):
        """Ищем совпадения в тексте"""
        matches = re.findall(pattern, content, re.IGNORECASE)
        return matches[:10]  # Ограничиваем количество

    def analyze_blob_files(self):
        """Анализируем BLOB файлы"""
        print("Анализирую BLOB файлы...")
        
        for blob_dir in self.data_dir.glob("*.blob"):
            if blob_dir.is_dir():
                print(f"Обрабатываю {blob_dir.name}")
                for blob_file in blob_dir.glob("*"):
                    try:
                        with open(blob_file, 'rb') as f:
                            content = f.read()
                        
                        self.results['blob_data'][blob_file.name] = {
                            'size': len(content),
                            'type': 'binary',
                            'hex_preview': content[:100].hex()
                        }
                    except Exception as e:
                        print(f"Ошибка обработки {blob_file}: {e}")

    def save_results(self):
        """Сохраняем результаты"""
        output_dir = Path("/Users/ilyakrasinsky/workspace/vscode.projects/1C-extractor/docs/reports/complete_analysis")
        output_dir.mkdir(exist_ok=True)
        
        # Сохраняем общие результаты
        with open(output_dir / "complete_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # Сохраняем отдельные файлы
        for doc_type, docs in self.results['documents'].items():
            if docs:
                with open(output_dir / f"{doc_type}.json", 'w', encoding='utf-8') as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)
        
        # Сохраняем метаданные
        with open(output_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.results['metadata'], f, ensure_ascii=False, indent=2)
        
        print(f"Результаты сохранены в {output_dir}")

    def generate_summary(self):
        """Генерируем сводку"""
        print("\n=== СВОДКА АНАЛИЗА ===")
        print(f"Документы найдены:")
        for doc_type, docs in self.results['documents'].items():
            print(f"  {doc_type}: {len(docs)} записей")
        
        print(f"Справочники:")
        for cat_type, cats in self.results['catalogs'].items():
            print(f"  {cat_type}: {len(cats)} записей")
        
        print(f"Метаданные:")
        for meta_type, meta in self.results['metadata'].items():
            print(f"  {meta_type}: {len(meta)} записей")
        
        print(f"BLOB файлы: {len(self.results['blob_data'])}")

def main():
    data_dir = "/Users/ilyakrasinsky/workspace/vscode.projects/1C-extractor/docs/reports/complete_data"
    
    analyzer = CompleteOneCAnalyzer(data_dir)
    analyzer.analyze_all_files()
    analyzer.analyze_blob_files()
    analyzer.save_results()
    analyzer.generate_summary()

if __name__ == "__main__":
    main() 