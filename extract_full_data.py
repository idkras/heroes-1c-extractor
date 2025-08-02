#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение полных данных документов из BLOB файлов и метаданных
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import struct

class FullDataExtractor:
    def __init__(self, raw_dir):
        self.raw_dir = Path(raw_dir)
        self.results = {
            'documents': {},
            'catalogs': {},
            'blob_data': {}
        }
    
    def extract_blob_data(self):
        """Извлекает данные из BLOB файлов"""
        print("Извлекаю данные из BLOB файлов...")
        
        # Ищем все BLOB файлы
        blob_dirs = list(self.raw_dir.glob("*.blob"))
        
        for blob_dir in blob_dirs:
            if blob_dir.is_dir():
                print(f"Обрабатываю {blob_dir.name}")
                
                for blob_file in blob_dir.glob("*"):
                    if blob_file.is_file():
                        try:
                            # Читаем как бинарный файл
                            with open(blob_file, 'rb') as f:
                                content = f.read()
                            
                            # Пытаемся декодировать как текст
                            try:
                                text_content = content.decode('utf-8', errors='ignore')
                                self.results['blob_data'][blob_file.name] = {
                                    'type': 'text',
                                    'content': text_content,
                                    'size': len(content)
                                }
                            except:
                                # Если не текст, сохраняем как бинарные данные
                                self.results['blob_data'][blob_file.name] = {
                                    'type': 'binary',
                                    'size': len(content),
                                    'hex_preview': content[:100].hex()
                                }
                            
                            print(f"  Обработан {blob_file.name}: {len(content)} байт")
                            
                        except Exception as e:
                            print(f"Ошибка обработки {blob_file}: {e}")
    
    def extract_document_content(self):
        """Извлекает содержимое документов из метаданных"""
        print("Извлекаю содержимое документов...")
        
        # Читаем историю пользователей
        history_file = self.raw_dir / "_USERSWORKHISTORY.xml"
        if not history_file.exists():
            print(f"Файл {history_file} не найден")
            return
        
        with open(history_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем все документы
        document_pattern = r'<Record>\s*<_ID>([^<]+)</_ID>\s*<_USERID>([^<]+)</_USERID>\s*<_URL>([^<]+)</_URL>\s*<_DATE>([^<]+)</_DATE>\s*<_URLHASH>([^<]+)</_URLHASH>\s*</Record>'
        
        matches = re.findall(document_pattern, content, re.DOTALL)
        
        for match in matches:
            record_id, user_id, url, date, url_hash = match
            
            # Парсим URL
            url_match = re.search(r'e1cib/data/([^?]+)\?ref=([a-f0-9]+)', url)
            if url_match:
                doc_type, doc_ref = url_match.groups()
                
                # Создаем запись документа
                doc_record = {
                    'record_id': record_id,
                    'user_id': user_id,
                    'document_type': doc_type,
                    'document_ref': doc_ref,
                    'date': date,
                    'url_hash': url_hash,
                    'url': url
                }
                
                # Классифицируем документ
                if 'Документ.' in doc_type:
                    if doc_type not in self.results['documents']:
                        self.results['documents'][doc_type] = []
                    self.results['documents'][doc_type].append(doc_record)
                elif 'Справочник.' in doc_type:
                    if doc_type not in self.results['catalogs']:
                        self.results['catalogs'][doc_type] = []
                    self.results['catalogs'][doc_type].append(doc_record)
        
        print(f"Найдено документов: {sum(len(docs) for docs in self.results['documents'].values())}")
        print(f"Найдено справочников: {sum(len(catalogs) for catalogs in self.results['catalogs'].values())}")
    
    def analyze_users_data(self):
        """Анализирует данные пользователей"""
        print("Анализирую данные пользователей...")
        
        users_file = self.raw_dir / "V8USERS.xml"
        if not users_file.exists():
            print(f"Файл {users_file} не найден")
            return
        
        try:
            tree = ET.parse(users_file)
            root = tree.getroot()
            
            users = []
            for record in root.findall('.//Record'):
                user_data = {}
                for field in record.findall('./*'):
                    user_data[field.tag] = field.text
                
                if user_data:
                    users.append(user_data)
            
            self.results['users'] = users
            print(f"Найдено пользователей: {len(users)}")
            
        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
    
    def extract_nomenclature_data(self):
        """Извлекает данные номенклатуры"""
        print("Извлекаю данные номенклатуры...")
        
        # Ищем в BLOB данных записи номенклатуры
        nomenclature_data = []
        
        for blob_name, blob_info in self.results['blob_data'].items():
            if blob_info['type'] == 'text':
                content = blob_info['content']
                
                # Ищем записи номенклатуры
                if 'Номенклатура' in content or 'цвет' in content.lower() or 'flower' in content.lower():
                    nomenclature_data.append({
                        'blob_file': blob_name,
                        'content': content,
                        'size': blob_info['size']
                    })
        
        self.results['nomenclature'] = nomenclature_data
        print(f"Найдено записей номенклатуры: {len(nomenclature_data)}")
    
    def save_results(self):
        """Сохраняет результаты"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Сохраняем общий отчет
        report_file = self.raw_dir / f"full_data_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # Сохраняем детальные отчеты
        for doc_type, docs in self.results['documents'].items():
            if docs:
                doc_file = self.raw_dir / "documents" / f"{doc_type.replace('.', '_')}_{timestamp}.json"
                doc_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(doc_file, 'w', encoding='utf-8') as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)
        
        for catalog_type, catalogs in self.results['catalogs'].items():
            if catalogs:
                catalog_file = self.raw_dir / "catalogs" / f"{catalog_type.replace('.', '_')}_{timestamp}.json"
                catalog_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(catalog_file, 'w', encoding='utf-8') as f:
                    json.dump(catalogs, f, ensure_ascii=False, indent=2)
        
        # Сохраняем данные номенклатуры
        if self.results.get('nomenclature'):
            nom_file = self.raw_dir / f"nomenclature_data_{timestamp}.json"
            with open(nom_file, 'w', encoding='utf-8') as f:
                json.dump(self.results['nomenclature'], f, ensure_ascii=False, indent=2)
        
        print(f"Результаты сохранены с временной меткой: {timestamp}")
    
    def generate_summary(self):
        """Генерирует сводный отчет"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': sum(len(docs) for docs in self.results['documents'].values()),
            'total_catalogs': sum(len(catalogs) for catalogs in self.results['catalogs'].values()),
            'total_users': len(self.results.get('users', [])),
            'total_blob_files': len(self.results['blob_data']),
            'total_nomenclature': len(self.results.get('nomenclature', [])),
            'document_types': {k: len(v) for k, v in self.results['documents'].items()},
            'catalog_types': {k: len(v) for k, v in self.results['catalogs'].items()}
        }
        
        summary_file = self.raw_dir / "full_data_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n=== СВОДНЫЙ ОТЧЕТ ПОЛНЫХ ДАННЫХ ===")
        print(f"Всего документов: {summary['total_documents']}")
        print(f"Всего справочников: {summary['total_catalogs']}")
        print(f"Пользователей: {summary['total_users']}")
        print(f"BLOB файлов: {summary['total_blob_files']}")
        print(f"Записей номенклатуры: {summary['total_nomenclature']}")
        print("\nДокументы по типам:")
        for doc_type, count in summary['document_types'].items():
            print(f"  {doc_type}: {count}")
        print("\nСправочники по типам:")
        for catalog_type, count in summary['catalog_types'].items():
            print(f"  {catalog_type}: {count}")

def main():
    raw_dir = "./[prostocvet-1c]/raw"
    
    extractor = FullDataExtractor(raw_dir)
    
    print("=== ИЗВЛЕЧЕНИЕ ПОЛНЫХ ДАННЫХ ===")
    print(f"Рабочая директория: {raw_dir}")
    
    # Извлекаем данные
    extractor.extract_blob_data()
    extractor.extract_document_content()
    extractor.analyze_users_data()
    extractor.extract_nomenclature_data()
    
    # Сохраняем результаты
    extractor.save_results()
    extractor.generate_summary()
    
    print("\n=== ИЗВЛЕЧЕНИЕ ПОЛНЫХ ДАННЫХ ЗАВЕРШЕНО ===")

if __name__ == "__main__":
    main() 