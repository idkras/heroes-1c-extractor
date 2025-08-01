#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор данных о цветах из документов 1С
Извлекает информацию о цветах из актов, накладных и счетов-фактур
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime

class FlowerDataAnalyzer:
    def __init__(self, documents_dir):
        self.documents_dir = Path(documents_dir)
        self.results = {
            'summary': {
                'total_documents': 0,
                'acts': 0,
                'invoices': 0,
                'orders': 0,
                'care_records': 0
            },
            'flower_data': [],
            'period': {
                'start': None,
                'end': None
            }
        }
    
    def analyze_documents(self):
        """Анализирует все документы на предмет данных о цветах"""
        print("=== АНАЛИЗ ДАННЫХ О ЦВЕТАХ ИЗ ДОКУМЕНТОВ 1С ===")
        
        # Анализируем акты
        acts_file = self.documents_dir / "acts" / "acts_details_20250801_210741.csv"
        if acts_file.exists():
            self.analyze_acts(acts_file)
        
        # Анализируем счета
        invoices_file = self.documents_dir / "invoices" / "invoices_details_20250801_210741.csv"
        if invoices_file.exists():
            self.analyze_invoices(invoices_file)
        
        # Анализируем заказы
        orders_file = self.documents_dir / "orders" / "orders_details_20250801_210741.csv"
        if orders_file.exists():
            self.analyze_orders(orders_file)
        
        # Анализируем уход за растениями
        care_file = self.documents_dir / "care_records" / "care_records_details_20250801_210741.csv"
        if care_file.exists():
            self.analyze_care_records(care_file)
    
    def analyze_acts(self, file_path):
        """Анализирует акты на предмет данных о цветах"""
        print(f"Анализирую акты: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.results['summary']['acts'] += 1
                self.results['summary']['total_documents'] += 1
                
                # Анализируем дату
                date = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                if not self.results['period']['start'] or date < self.results['period']['start']:
                    self.results['period']['start'] = date
                if not self.results['period']['end'] or date > self.results['period']['end']:
                    self.results['period']['end'] = date
                
                # Добавляем данные о документе
                self.results['flower_data'].append({
                    'type': 'act',
                    'document_type': row['document_type'],
                    'date': row['date'],
                    'user': row['user_name'],
                    'ref': row['document_ref'],
                    'url': row['url']
                })
    
    def analyze_invoices(self, file_path):
        """Анализирует счета на предмет данных о цветах"""
        print(f"Анализирую счета: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.results['summary']['invoices'] += 1
                self.results['summary']['total_documents'] += 1
                
                # Анализируем дату
                date = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                if not self.results['period']['start'] or date < self.results['period']['start']:
                    self.results['period']['start'] = date
                if not self.results['period']['end'] or date > self.results['period']['end']:
                    self.results['period']['end'] = date
                
                # Добавляем данные о документе
                self.results['flower_data'].append({
                    'type': 'invoice',
                    'document_type': row['document_type'],
                    'date': row['date'],
                    'user': row['user_name'],
                    'ref': row['document_ref'],
                    'url': row['url']
                })
    
    def analyze_orders(self, file_path):
        """Анализирует заказы на предмет данных о цветах"""
        print(f"Анализирую заказы: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.results['summary']['orders'] += 1
                self.results['summary']['total_documents'] += 1
                
                # Анализируем дату
                date = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                if not self.results['period']['start'] or date < self.results['period']['start']:
                    self.results['period']['start'] = date
                if not self.results['period']['end'] or date > self.results['period']['end']:
                    self.results['period']['end'] = date
                
                # Добавляем данные о документе
                self.results['flower_data'].append({
                    'type': 'order',
                    'document_type': row['document_type'],
                    'date': row['date'],
                    'user': row['user_name'],
                    'ref': row['document_ref'],
                    'url': row['url']
                })
    
    def analyze_care_records(self, file_path):
        """Анализирует записи ухода за растениями"""
        print(f"Анализирую уход за растениями: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.results['summary']['care_records'] += 1
                self.results['summary']['total_documents'] += 1
                
                # Анализируем дату
                date = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                if not self.results['period']['start'] or date < self.results['period']['start']:
                    self.results['period']['start'] = date
                if not self.results['period']['end'] or date > self.results['period']['end']:
                    self.results['period']['end'] = date
                
                # Добавляем данные о документе
                self.results['flower_data'].append({
                    'type': 'care_record',
                    'document_type': row['document_type'],
                    'date': row['date'],
                    'user': row['user_name'],
                    'ref': row['document_ref'],
                    'url': row['url']
                })
    
    def save_results(self):
        """Сохраняет результаты анализа"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Сохраняем JSON отчет
        json_file = self.documents_dir / f"flower_analysis_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        
        # Сохраняем CSV отчет
        csv_file = self.documents_dir / f"flower_data_{timestamp}.csv"
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            if self.results['flower_data']:
                writer = csv.DictWriter(f, fieldnames=self.results['flower_data'][0].keys())
                writer.writeheader()
                writer.writerows(self.results['flower_data'])
        
        print(f"Результаты сохранены:")
        print(f"  JSON: {json_file}")
        print(f"  CSV: {csv_file}")
    
    def generate_summary(self):
        """Генерирует краткий отчет"""
        print("\n=== КРАТКИЙ ОТЧЕТ ===")
        print(f"Всего документов: {self.results['summary']['total_documents']}")
        print(f"Актов: {self.results['summary']['acts']}")
        print(f"Счетов: {self.results['summary']['invoices']}")
        print(f"Заказов: {self.results['summary']['orders']}")
        print(f"Записей ухода: {self.results['summary']['care_records']}")
        
        if self.results['period']['start'] and self.results['period']['end']:
            print(f"Период: {self.results['period']['start']} - {self.results['period']['end']}")
        
        print("\n=== АНАЛИЗ ЗАВЕРШЕН ===")

def main():
    """Основная функция"""
    documents_dir = Path("[prostocvet-1c]/raw/documents")
    
    if not documents_dir.exists():
        print(f"Директория {documents_dir} не найдена")
        return
    
    analyzer = FlowerDataAnalyzer(documents_dir)
    analyzer.analyze_documents()
    analyzer.save_results()
    analyzer.generate_summary()

if __name__ == "__main__":
    main() 