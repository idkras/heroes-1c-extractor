#!/usr/bin/env python3
"""
Скрипт для управления стандартами по Registry Standard и Task Master подходу.
Выполняет следующие функции:
1. Сканирование директории стандартов
2. Выявление дублирующихся стандартов
3. Удаление .bak файлов
4. Преобразование жестких ссылок в абстрактные

Автор: AI Assistant
Дата: 22 мая 2025
"""

import os
import sys
import re
import shutil
import argparse
import logging
import json
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("standards_manager")

# Константы
STANDARDS_DIR = "[standards .md]"
BACKUP_EXTENSION = ".bak"
ARCHIVE_DIR = os.path.join(STANDARDS_DIR, "[archive]")

# Класс для симуляции DocumentSystem, если не удается импортировать
class SimpleDocumentSystem:
    """Упрощенная версия DocumentSystem для сканирования документов."""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.documents = self.scan_documents()
    
    def scan_documents(self):
        """Сканирует директорию и возвращает список документов."""
        documents = []
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.md') and not file.endswith('.bak'):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Извлекаем метаданные
                        metadata = self.extract_metadata(content, full_path)
                        
                        # Добавляем документ в список
                        documents.append({
                            'path': full_path,
                            'content': content,
                            'content_hash': self.hash_content(content),
                            'metadata': metadata
                        })
                    except Exception as e:
                        logger.error(f"Ошибка при обработке {full_path}: {e}")
        
        return documents
    
    def extract_metadata(self, content, path):
        """Извлекает метаданные из содержимого документа."""
        metadata = {
            'type': 'other',
            'title': os.path.basename(path),
            'author': None,
            'date': None
        }
        
        # Определение типа документа
        if "type: standard" in content:
            metadata['type'] = 'standard'
        elif "type: archived_standard" in content:
            metadata['type'] = 'archived_standard'
        elif "type: jtbd" in content:
            metadata['type'] = 'jtbd'
        
        # Определение автора
        author_match = re.search(r'by\s+(.*?)\s*$', os.path.basename(path))
        if author_match:
            metadata['author'] = author_match.group(1)
        
        # Определение даты из имени файла
        date_match = re.search(r'(\d+\s+[a-z]+\s+\d{4})', os.path.basename(path), re.IGNORECASE)
        if date_match:
            metadata['date'] = date_match.group(1)
        
        # Определение заголовка из содержимого
        title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        return metadata
    
    def hash_content(self, content):
        """Создает простой хеш содержимого."""
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def create_logical_id(self, document):
        """Создает логический идентификатор для документа."""
        # Создаем идентификатор на основе названия документа
        path = document['path']
        filename = os.path.basename(path)
        # Убираем расширение и дату
        clean_name = re.sub(r'\d+\s+[a-z]+\s+\d{4}.*$', '', filename, flags=re.IGNORECASE)
        # Преобразуем в формат для идентификатора
        logical_id = clean_name.strip().lower().replace(' ', '_').replace('.', '_').replace('-', '_')
        return f"standard:{logical_id}"
    
    def convert_hard_links_to_abstract(self, content):
        """
        Преобразует жесткие ссылки на MD-файлы в абстрактные.
        
        Args:
            content: Содержимое документа
            
        Returns:
            str: Обновленное содержимое с абстрактными ссылками
        """
        # Регулярное выражение для поиска ссылок на markdown файлы
        link_pattern = r'\[(.*?)\]\((.*?\.md)\)'
        
        # Функция для замены ссылок
        def replace_link(match):
            text = match.group(1)
            path = match.group(2)
            filename = os.path.basename(path)
            # Создаем логический идентификатор
            clean_name = re.sub(r'\d+\s+[a-z]+\s+\d{4}.*$', '', filename, flags=re.IGNORECASE)
            logical_id = clean_name.strip().lower().replace(' ', '_').replace('.', '_').replace('-', '_')
            return f'[{text}](abstract://standard:{logical_id})'
        
        # Заменяем ссылки
        updated_content = re.sub(link_pattern, replace_link, content)
        return updated_content


class DocumentSystem:
    """Адаптер для SimpleDocumentSystem, если не удается импортировать оригинальный класс."""
    
    def __init__(self, base_dir):
        self.sys = SimpleDocumentSystem(base_dir)
        self.documents = self.sys.documents
    
    def create_logical_id(self, document):
        """Создает логический идентификатор для документа."""
        return self.sys.create_logical_id(document)
    
    def convert_hard_links_to_abstract(self, content):
        """Преобразует жесткие ссылки в абстрактные."""
        return self.sys.convert_hard_links_to_abstract(content)


class StandardsManager:
    """Класс для управления стандартами."""
    
    def __init__(self, standards_dir: str = STANDARDS_DIR):
        """
        Инициализирует менеджер стандартов.
        
        Args:
            standards_dir: Директория со стандартами
        """
        self.standards_dir = os.path.abspath(standards_dir)
        self.doc_system = DocumentSystem(self.standards_dir)
        logger.info(f"Инициализирован менеджер стандартов для директории: {self.standards_dir}")
        
        # Загружаем документы
        self.reload_documents()
    
    def reload_documents(self):
        """Перезагружает документы из файловой системы."""
        logger.info("Загрузка документов...")
        self.doc_system = DocumentSystem(self.standards_dir)
        self.documents = self.doc_system.documents
        self.standards = [doc for doc in self.documents if doc['metadata']['type'] in ['standard', 'archived_standard']]
        logger.info(f"Загружено {len(self.documents)} документов, из них {len(self.standards)} стандартов")
        
        # Находим ключевые стандарты
        self.registry_standard = None
        self.task_master_standard = None
        
        for doc in self.standards:
            # Ищем Registry Standard
            if ("registry standard" in doc['path'].lower() and 
                "0.1" in doc['path'] and 
                not "/[archive]/" in doc['path']):
                self.registry_standard = doc
                logger.info(f"Найден Registry Standard: {doc['path']}")
            
            # Ищем Task Master Standard
            if ("task master" in doc['path'].lower() and 
                "0.0" in doc['path'] and 
                not "/[archive]/" in doc['path']):
                self.task_master_standard = doc
                logger.info(f"Найден Task Master Standard: {doc['path']}")
    
    def find_backup_files(self) -> List[str]:
        """
        Находит все .bak файлы в директории стандартов.
        
        Returns:
            Список путей к .bak файлам
        """
        backup_files = []
        for root, _, files in os.walk(self.standards_dir):
            for file in files:
                if file.endswith(BACKUP_EXTENSION):
                    backup_files.append(os.path.join(root, file))
        
        logger.info(f"Найдено {len(backup_files)} .bak файлов")
        return backup_files
    
    def remove_backup_files(self, dry_run: bool = True) -> int:
        """
        Удаляет все .bak файлы.
        
        Args:
            dry_run: Если True, только показывает, какие файлы будут удалены, но не удаляет их
            
        Returns:
            Количество удаленных файлов
        """
        backup_files = self.find_backup_files()
        if not backup_files:
            logger.info("Нет .bak файлов для удаления")
            return 0
        
        count = 0
        for file_path in backup_files:
            if dry_run:
                logger.info(f"[DRY RUN] Будет удалён: {file_path}")
            else:
                try:
                    os.remove(file_path)
                    logger.info(f"Удалён: {file_path}")
                    count += 1
                except Exception as e:
                    logger.error(f"Ошибка при удалении {file_path}: {e}")
        
        action = "Будет удалено" if dry_run else "Удалено"
        logger.info(f"{action} {count} .bak файлов")
        return count
    
    def find_duplicate_standards(self) -> List[List[Dict[str, Any]]]:
        """
        Находит дублирующиеся стандарты по содержимому.
        
        Returns:
            Список групп дублирующихся стандартов
        """
        # Словарь {content_hash: [document1, document2, ...]}
        content_hash_map = {}
        
        for doc in self.standards:
            content_hash = doc.get('content_hash')
            if content_hash not in content_hash_map:
                content_hash_map[content_hash] = []
            content_hash_map[content_hash].append(doc)
        
        # Выбираем только те группы, где больше одного документа
        duplicates = [docs for content_hash, docs in content_hash_map.items() if len(docs) > 1]
        
        # Также ищем по названию (возможно, с разным содержимым)
        title_map = {}
        for doc in self.standards:
            title = doc['metadata'].get('title')
            if title and title.strip():
                if title not in title_map:
                    title_map[title] = []
                title_map[title].append(doc)
        
        # Добавляем группы дубликатов по названию
        for title, docs in title_map.items():
            if len(docs) > 1:
                # Проверяем, не дублируется ли с уже найденными
                content_hashes = {doc.get('content_hash') for doc in docs}
                if len(content_hashes) > 1:  # Разное содержимое, но одинаковое название
                    duplicates.append(docs)
        
        logger.info(f"Найдено {len(duplicates)} групп дублирующихся стандартов")
        return duplicates
    
    def merge_duplicate_standards(self, duplicates: List[List[Dict[str, Any]]], dry_run: bool = True) -> int:
        """
        Объединяет дублирующиеся стандарты.
        
        Args:
            duplicates: Список групп дублирующихся стандартов
            dry_run: Если True, только показывает, что будет сделано, но не изменяет файлы
            
        Returns:
            Количество групп дублирующихся стандартов, которые были объединены
        """
        if not duplicates:
            logger.info("Нет дублирующихся стандартов для объединения")
            return 0
        
        count = 0
        for group in duplicates:
            # Сортируем документы по дате обновления (от новых к старым)
            sorted_group = sorted(group, key=lambda x: x['metadata'].get('date', ''), reverse=True)
            primary = sorted_group[0]  # Самый новый документ становится основным
            
            logger.info(f"Группа дубликатов с одинаковым хешем содержимого или названием:")
            logger.info(f"Основной документ: {primary['path']} ({primary['metadata'].get('date', 'нет даты')})")
            
            # Архивируем остальные документы
            for duplicate in sorted_group[1:]:
                logger.info(f"  Дубликат: {duplicate['path']} ({duplicate['metadata'].get('date', 'нет даты')})")
                
                if not dry_run:
                    # Создаем директорию архива, если она не существует
                    archive_dir = os.path.join(self.standards_dir, "[archive]", "duplicates_archive")
                    os.makedirs(archive_dir, exist_ok=True)
                    
                    # Перемещаем дубликат в архив
                    archive_path = os.path.join(archive_dir, os.path.basename(duplicate['path']))
                    try:
                        shutil.move(duplicate['path'], archive_path)
                        logger.info(f"Перемещен в архив: {archive_path}")
                    except Exception as e:
                        logger.error(f"Ошибка при перемещении {duplicate['path']}: {e}")
            
            count += 1
        
        action = "Будет объединено" if dry_run else "Объединено"
        logger.info(f"{action} {count} групп дублирующихся стандартов")
        return count
    
    def convert_links_to_abstract(self, dry_run: bool = True) -> int:
        """
        Преобразует жесткие ссылки в абстрактные для всех стандартов.
        
        Args:
            dry_run: Если True, только показывает, что будет сделано, но не изменяет файлы
            
        Returns:
            Количество обновленных документов
        """
        count = 0
        for doc in self.standards:
            # Проверяем, есть ли жесткие ссылки в документе
            content = doc['content']
            # Регулярное выражение для поиска ссылок на markdown файлы
            link_pattern = r'\[(.*?)\]\((.*?\.md)\)'
            matches = re.findall(link_pattern, content)
            
            if matches:
                logger.info(f"Стандарт {doc['path']} содержит {len(matches)} жестких ссылок")
                
                if not dry_run:
                    try:
                        # Используем функцию для преобразования ссылок
                        updated_content = self.doc_system.convert_hard_links_to_abstract(content)
                        
                        # Если содержимое изменилось, обновляем файл
                        if updated_content != content:
                            with open(doc['path'], 'w', encoding='utf-8') as f:
                                f.write(updated_content)
                            logger.info(f"Обновлен: {doc['path']}")
                            count += 1
                    except Exception as e:
                        logger.error(f"Ошибка при обновлении {doc['path']}: {e}")
            
        action = "Будет обновлено" if dry_run else "Обновлено"
        logger.info(f"{action} {count} документов с абстрактными ссылками")
        return count
    
    def update_registry_standard(self, dry_run: bool = True) -> bool:
        """
        Обновляет Registry Standard в соответствии с Task Master стандартом.
        
        Args:
            dry_run: Если True, только показывает, что будет сделано, но не изменяет файлы
            
        Returns:
            True, если обновление успешно, иначе False
        """
        if not self.registry_standard:
            logger.error("Registry Standard не найден")
            return False
        
        if not self.task_master_standard:
            logger.error("Task Master Standard не найден")
            return False
        
        logger.info(f"Обновление Registry Standard: {self.registry_standard['path']}")
        logger.info(f"На основе Task Master Standard: {self.task_master_standard['path']}")
        
        if not dry_run:
            try:
                # Обновляем ссылку на Task Master в Registry Standard
                content = self.registry_standard['content']
                
                # Создаем абстрактную ссылку
                logical_id = self.doc_system.create_logical_id(self.task_master_standard)
                updated_content = re.sub(
                    r'\[Task Master Standard\]\((.*?)\)',
                    f'[Task Master Standard](abstract://{logical_id})',
                    content
                )
                
                # Обновляем версию и дату
                now = datetime.now().strftime("%d %b %Y, %H:%M CET")
                updated_content = re.sub(
                    r'updated: .*?by AI Assistant',
                    f'updated: {now} by AI Assistant',
                    updated_content
                )
                
                # Если содержимое изменилось, обновляем файл
                if updated_content != content:
                    with open(self.registry_standard['path'], 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    logger.info(f"Обновлен Registry Standard с абстрактной ссылкой на Task Master")
                    return True
                else:
                    logger.info("Registry Standard не требует обновления")
                    return True
            except Exception as e:
                logger.error(f"Ошибка при обновлении Registry Standard: {e}")
                return False
        
        logger.info("[DRY RUN] Registry Standard будет обновлен с абстрактной ссылкой на Task Master")
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Генерирует отчет о состоянии стандартов.
        
        Returns:
            Словарь с отчетом
        """
        # Получаем статистику по типам документов
        type_stats = {}
        for doc in self.documents:
            doc_type = doc['metadata'].get('type', 'unknown')
            if doc_type not in type_stats:
                type_stats[doc_type] = 0
            type_stats[doc_type] += 1
        
        # Получаем статистику по авторам
        author_stats = {}
        for doc in self.documents:
            author = doc['metadata'].get('author', None)
            if author not in author_stats:
                author_stats[author] = 0
            author_stats[author] += 1
        
        # Находим документы без абстрактных ссылок
        no_abstract_links = []
        for doc in self.standards:
            if "abstract://" not in doc['content']:
                no_abstract_links.append(doc['path'])
        
        report = {
            "total_documents": len(self.documents),
            "total_standards": len(self.standards),
            "document_types": type_stats,
            "authors": author_stats,
            "backup_files": len(self.find_backup_files()),
            "duplicate_groups": len(self.find_duplicate_standards()),
            "documents_without_abstract_links": len(no_abstract_links),
            "documents_without_abstract_links_list": no_abstract_links,
            "registry_standard_found": self.registry_standard is not None,
            "task_master_standard_found": self.task_master_standard is not None
        }
        
        return report


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Управление стандартами по Registry Standard и Task Master подходу')
    parser.add_argument('--dry-run', action='store_true', help='Только показать, что будет сделано, без изменения файлов')
    parser.add_argument('--remove-backups', action='store_true', help='Удалить .bak файлы')
    parser.add_argument('--merge-duplicates', action='store_true', help='Объединить дублирующиеся стандарты')
    parser.add_argument('--convert-links', action='store_true', help='Преобразовать жесткие ссылки в абстрактные')
    parser.add_argument('--update-registry', action='store_true', help='Обновить Registry Standard')
    parser.add_argument('--report', action='store_true', help='Сгенерировать отчет о состоянии стандартов')
    parser.add_argument('--all', action='store_true', help='Выполнить все операции')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    try:
        manager = StandardsManager()
        
        if args.report or args.all:
            report = manager.generate_report()
            logger.info("Отчет о состоянии стандартов:")
            for key, value in report.items():
                if key != "documents_without_abstract_links_list":
                    logger.info(f"{key}: {value}")
            
            if report["documents_without_abstract_links"] > 0:
                logger.info("Документы без абстрактных ссылок:")
                for path in report["documents_without_abstract_links_list"][:10]:  # Показываем только первые 10
                    logger.info(f"  {path}")
                if len(report["documents_without_abstract_links_list"]) > 10:
                    logger.info(f"  ... и еще {len(report['documents_without_abstract_links_list']) - 10} документов")
        
        if args.remove_backups or args.all:
            manager.remove_backup_files(dry_run=args.dry_run)
        
        if args.merge_duplicates or args.all:
            duplicates = manager.find_duplicate_standards()
            manager.merge_duplicate_standards(duplicates, dry_run=args.dry_run)
        
        if args.convert_links or args.all:
            manager.convert_links_to_abstract(dry_run=args.dry_run)
        
        if args.update_registry or args.all:
            manager.update_registry_standard(dry_run=args.dry_run)
        
        logger.info("Операции завершены")
        return 0
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении операций: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())