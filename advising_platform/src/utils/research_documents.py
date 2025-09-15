#!/usr/bin/env python3
"""
Исследовательский скрипт для анализа документов проекта.
Цель: выявить паттерны именования, метаданные, связи между документами
и правила определения актуальных версий.
"""

import os
import re
import json
import hashlib
from collections import defaultdict
from datetime import datetime
import difflib

def collect_markdown_files(root_dir='.', exclude_dirs=None):
    """Собирает все markdown файлы в проекте."""
    if exclude_dirs is None:
        exclude_dirs = ['.git', 'node_modules', '__pycache__', '.roo', '.cursor', '.cache']
    
    markdown_files = []
    for root, dirs, files in os.walk(root_dir):
        # Исключаем указанные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                markdown_files.append(full_path)
    
    print(f"Найдено {len(markdown_files)} markdown-файлов")
    return markdown_files

def analyze_file_naming_patterns(markdown_files):
    """Анализирует паттерны именования файлов в проекте."""
    patterns = defaultdict(list)
    
    # Регулярные выражения для анализа паттернов
    date_pattern = re.compile(r'\d+\s+\w+\s+\d{4}')
    version_pattern = re.compile(r'v\d+(\.\d+)*')
    author_pattern = re.compile(r'by\s+[A-Za-z\s]+')
    prefix_number_pattern = re.compile(r'^\d+(\.\d+)*\s+')
    
    # Дополнительные статистические данные
    extensions = defaultdict(int)
    directories = defaultdict(int)
    prefix_numbers = defaultdict(int)
    
    for file_path in markdown_files:
        filename = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        
        # Подсчет по директориям
        directories[directory] += 1
        
        # Анализ расширения файла
        ext = os.path.splitext(filename)[1]
        extensions[ext] += 1
        
        # Анализ структуры имени файла
        has_date = bool(date_pattern.search(filename))
        has_version = bool(version_pattern.search(filename))
        has_author = bool(author_pattern.search(filename))
        has_prefix_number = bool(prefix_number_pattern.search(filename))
        
        # Если есть префикс-номер, сохраняем его для анализа
        if has_prefix_number:
            prefix_match = prefix_number_pattern.search(filename)
            if prefix_match:
                prefix = prefix_match.group(0).strip()
                prefix_numbers[prefix] += 1
        
        # Сохраняем результаты анализа
        pattern_key = f"date:{has_date}_version:{has_version}_author:{has_author}_prefix:{has_prefix_number}"
        patterns[pattern_key].append(file_path)
    
    # Выводим результаты
    print("\n=== Паттерны именования файлов ===")
    for pattern, files in patterns.items():
        print(f"Паттерн {pattern}: {len(files)} файлов")
        for file in sorted(files)[:3]:  # Показываем первые 3 примера
            print(f"  - {file}")
        if len(files) > 3:
            print(f"  - и еще {len(files) - 3} файлов")
    
    # Выводим дополнительную статистику
    print("\n=== Топ директорий по количеству файлов ===")
    for directory, count in sorted(directories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{directory}: {count} файлов")
    
    print("\n=== Префиксы номеров файлов ===")
    for prefix, count in sorted(prefix_numbers.items(), key=lambda x: x[1], reverse=True):
        print(f"{prefix}: {count} файлов")
    
    return patterns

def extract_metadata_from_file(file_path):
    """Извлекает метаданные из markdown файла."""
    metadata = {
        'title': None,
        'date': None,
        'author': None,
        'version': None,
        'based_on': None,
        'type': None
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем заголовок (первая строка с #)
        title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Ищем дату в формате "updated: DD month YYYY"
        date_match = re.search(r'updated:\s*(\d+\s+\w+\s+\d{4}(?:,\s*\d{2}:\d{2}\s*\w+)?)', content)
        if date_match:
            metadata['date'] = date_match.group(1).strip()
        else:
            # Альтернативный формат даты
            alt_date_match = re.search(r'(\d+\s+\w+\s+\d{4})', content)
            if alt_date_match:
                metadata['date'] = alt_date_match.group(1).strip()
        
        # Ищем автора
        author_match = re.search(r'by\s+([^,\n]+)', content)
        if author_match:
            metadata['author'] = author_match.group(1).strip()
        
        # Ищем версию
        version_match = re.search(r'version[:\s]+(\d+(?:\.\d+)*)', content, re.IGNORECASE)
        if version_match:
            metadata['version'] = version_match.group(1).strip()
        
        # Ищем based_on
        based_on_match = re.search(r'based\s+on:\s+(.*?)(?:$|\n)', content, re.IGNORECASE)
        if based_on_match:
            metadata['based_on'] = based_on_match.group(1).strip()
        
        # Пытаемся определить тип документа по содержимому и пути
        file_path_lower = file_path.lower()
        if 'standard' in file_path_lower:
            metadata['type'] = 'standard'
        elif 'project' in file_path_lower:
            metadata['type'] = 'project_doc'
        elif 'incident' in file_path_lower:
            metadata['type'] = 'incident'
        elif 'todo' in file_path_lower:
            metadata['type'] = 'todo'
        elif 'instruction' in file_path_lower:
            metadata['type'] = 'instruction'

        # Дополнительное определение типа по содержимому
        if 'JTBD' in content or 'Job to be done' in content:
            metadata['type'] = 'jtbd' if not metadata['type'] else metadata['type'] + '_jtbd'
        if 'Root Cause' in content or 'Корневая причина' in content:
            metadata['type'] = 'root_cause' if not metadata['type'] else metadata['type'] + '_root_cause'
            
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
    
    return metadata

def analyze_metadata(markdown_files):
    """Анализирует метаданные в markdown-файлах."""
    metadata_collection = {}
    metadata_stats = {
        'has_title': 0,
        'has_date': 0,
        'has_author': 0,
        'has_version': 0,
        'has_based_on': 0,
        'has_type': 0,
        'total_files': len(markdown_files),
        'by_type': defaultdict(int),
        'by_author': defaultdict(int),
        'date_formats': defaultdict(int),
    }
    
    for file_path in markdown_files:
        metadata = extract_metadata_from_file(file_path)
        metadata_collection[file_path] = metadata
        
        # Собираем статистику
        if metadata['title']:
            metadata_stats['has_title'] += 1
        if metadata['date']:
            metadata_stats['has_date'] += 1
            # Анализируем формат даты
            date_format = re.sub(r'\d+', '#', metadata['date']).strip()
            metadata_stats['date_formats'][date_format] += 1
        if metadata['author']:
            metadata_stats['has_author'] += 1
            metadata_stats['by_author'][metadata['author']] += 1
        if metadata['version']:
            metadata_stats['has_version'] += 1
        if metadata['based_on']:
            metadata_stats['has_based_on'] += 1
        if metadata['type']:
            metadata_stats['has_type'] += 1
            metadata_stats['by_type'][metadata['type']] += 1
    
    # Выводим результаты
    print("\n=== Статистика метаданных ===")
    print(f"Всего файлов: {metadata_stats['total_files']}")
    print(f"С заголовком: {metadata_stats['has_title']} ({metadata_stats['has_title']/metadata_stats['total_files']*100:.1f}%)")
    print(f"С датой: {metadata_stats['has_date']} ({metadata_stats['has_date']/metadata_stats['total_files']*100:.1f}%)")
    print(f"С автором: {metadata_stats['has_author']} ({metadata_stats['has_author']/metadata_stats['total_files']*100:.1f}%)")
    print(f"С версией: {metadata_stats['has_version']} ({metadata_stats['has_version']/metadata_stats['total_files']*100:.1f}%)")
    print(f"Со ссылкой на базовый документ: {metadata_stats['has_based_on']} ({metadata_stats['has_based_on']/metadata_stats['total_files']*100:.1f}%)")
    print(f"С определенным типом: {metadata_stats['has_type']} ({metadata_stats['has_type']/metadata_stats['total_files']*100:.1f}%)")
    
    print("\n=== Форматы дат ===")
    for format, count in sorted(metadata_stats['date_formats'].items(), key=lambda x: x[1], reverse=True):
        print(f"{format}: {count} файлов")
    
    print("\n=== Авторы документов ===")
    for author, count in sorted(metadata_stats['by_author'].items(), key=lambda x: x[1], reverse=True):
        print(f"{author}: {count} файлов")
    
    print("\n=== Типы документов ===")
    for doc_type, count in sorted(metadata_stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"{doc_type}: {count} файлов")
    
    return metadata_collection, metadata_stats

def find_links_in_content(content):
    """Находит markdown-ссылки в содержимом."""
    # Регулярное выражение для поиска markdown-ссылок
    link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
    return link_pattern.findall(content)

def analyze_document_links(markdown_files):
    """Анализирует ссылки между документами."""
    links_by_file = {}
    link_targets = defaultdict(int)
    link_types = defaultdict(int)
    
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = find_links_in_content(content)
            links_by_file[file_path] = links
            
            for link_text, link_target in links:
                link_targets[link_target] += 1
                
                # Классифицируем тип ссылки
                if link_target.startswith('http'):
                    link_types['external'] += 1
                elif link_target.endswith('.md'):
                    link_types['markdown'] += 1
                elif link_target.startswith('#'):
                    link_types['anchor'] += 1
                elif '/' in link_target:
                    link_types['path'] += 1
                else:
                    link_types['other'] += 1
        
        except Exception as e:
            print(f"Ошибка при анализе ссылок в файле {file_path}: {e}")
    
    # Подсчитываем общую статистику
    total_links = sum(len(links) for links in links_by_file.values())
    files_with_links = sum(1 for links in links_by_file.values() if links)
    
    # Выводим результаты
    print("\n=== Статистика ссылок ===")
    print(f"Всего ссылок: {total_links}")
    print(f"Файлов со ссылками: {files_with_links} ({files_with_links/len(markdown_files)*100:.1f}%)")
    
    print("\n=== Типы ссылок ===")
    for link_type, count in sorted(link_types.items(), key=lambda x: x[1], reverse=True):
        print(f"{link_type}: {count} ссылок ({count/total_links*100:.1f}%)")
    
    print("\n=== Топ 10 целевых ссылок ===")
    for target, count in sorted(link_targets.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{target}: {count} раз")
    
    print("\n=== Файлы с наибольшим количеством ссылок ===")
    for file_path, links in sorted(links_by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        if links:
            print(f"{file_path}: {len(links)} ссылок")
    
    return links_by_file, link_targets, link_types

def calculate_file_hash(file_path):
    """Вычисляет хеш содержимого файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Ошибка при вычислении хеша для {file_path}: {e}")
        return None

def find_similar_documents(markdown_files, metadata_collection):
    """Ищет похожие документы и возможные дубликаты."""
    content_hashes = defaultdict(list)
    title_groups = defaultdict(list)
    base_name_groups = defaultdict(list)
    
    # Группируем файлы по содержимому, заголовкам и базовым именам
    for file_path in markdown_files:
        # По содержимому
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            content_hashes[file_hash].append(file_path)
        
        # По заголовку
        title = metadata_collection[file_path]['title']
        if title:
            title_groups[title].append(file_path)
        
        # По базовому имени (без даты и автора)
        filename = os.path.basename(file_path)
        base_name = re.sub(r'\d+\s+\w+\s+\d{4}.*', '', filename).strip()
        base_name = re.sub(r'by\s+[A-Za-z\s]+', '', base_name).strip()
        base_name = re.sub(r'\.md$', '', base_name).strip()
        base_name_groups[base_name].append(file_path)
    
    # Выводим результаты
    print("\n=== Возможные дубликаты (по содержимому) ===")
    for file_hash, files in content_hashes.items():
        if len(files) > 1:
            print(f"Одинаковое содержимое ({len(files)} файлов):")
            for file in sorted(files):
                print(f"  - {file}")
    
    print("\n=== Файлы с одинаковыми заголовками ===")
    for title, files in title_groups.items():
        if len(files) > 1:
            print(f"Заголовок '{title}' ({len(files)} файлов):")
            for file in sorted(files):
                print(f"  - {file}")
    
    print("\n=== Файлы с похожими базовыми именами ===")
    for base_name, files in base_name_groups.items():
        if len(files) > 1 and base_name:  # Исключаем пустые имена
            print(f"Базовое имя '{base_name}' ({len(files)} файлов):")
            for file in sorted(files):
                print(f"  - {file}")
                # Показываем дату, если есть
                date = metadata_collection[file]['date']
                if date:
                    print(f"    Дата: {date}")
    
    # Находим стандарты с несколькими версиями
    print("\n=== Стандарты с несколькими версиями ===")
    standard_versions = defaultdict(list)
    for base_name, files in base_name_groups.items():
        if len(files) > 1:
            # Проверяем, что это стандарты
            if any("standard" in file.lower() for file in files):
                for file in files:
                    date = metadata_collection[file]['date']
                    if date:
                        standard_versions[base_name].append((file, date))
    
    for standard, versions in standard_versions.items():
        if versions:
            print(f"Стандарт '{standard}' ({len(versions)} версий):")
            # Сортируем по дате (предполагается, что более новые версии имеют более позднюю дату)
            for file, date in sorted(versions, key=lambda x: x[1], reverse=True):
                print(f"  - {file} (Дата: {date})")
    
    return {
        'content_hashes': content_hashes,
        'title_groups': title_groups,
        'base_name_groups': base_name_groups,
        'standard_versions': standard_versions
    }

def analyze_file_relationships(metadata_collection, links_by_file):
    """Анализирует зависимости между файлами на основе метаданных и ссылок."""
    based_on_relationships = defaultdict(list)
    link_relationships = defaultdict(list)
    
    # Создаем отображение заголовков в файлы для поиска связей
    title_to_file = {}
    for file_path, metadata in metadata_collection.items():
        if metadata['title']:
            title_to_file[metadata['title']] = file_path
    
    # Анализируем связи based_on
    for file_path, metadata in metadata_collection.items():
        if metadata['based_on']:
            # Ищем файл, на который ссылаются
            for title, target_file in title_to_file.items():
                if title in metadata['based_on']:
                    based_on_relationships[file_path].append((target_file, 'based_on'))
    
    # Анализируем прямые ссылки между документами
    for source_file, links in links_by_file.items():
        for link_text, link_target in links:
            # Проверяем, что это ссылка на markdown-файл
            if link_target.endswith('.md'):
                # Пытаемся найти целевой файл
                target_path = None
                
                # Абсолютный путь
                if os.path.exists(link_target):
                    target_path = link_target
                
                # Относительный путь
                source_dir = os.path.dirname(source_file)
                relative_path = os.path.normpath(os.path.join(source_dir, link_target))
                if os.path.exists(relative_path):
                    target_path = relative_path
                
                if target_path:
                    link_relationships[source_file].append((target_path, 'link'))
    
    # Выводим результаты
    print("\n=== Связи через based_on ===")
    for source, targets in based_on_relationships.items():
        if targets:
            print(f"{source} основан на:")
            for target, rel_type in targets:
                print(f"  - {target}")
    
    print("\n=== Прямые ссылки между файлами ===")
    for source, targets in link_relationships.items():
        if targets:
            print(f"{source} ссылается на:")
            for target, rel_type in targets:
                print(f"  - {target}")
    
    return {
        'based_on_relationships': based_on_relationships,
        'link_relationships': link_relationships
    }

def generate_recommendations(analysis_results):
    """Генерирует рекомендации на основе проведенного анализа."""
    metadata_stats = analysis_results['metadata_stats']
    link_types = analysis_results['link_types']
    standard_versions = analysis_results['similarity_analysis']['standard_versions']
    
    print("\n=== Рекомендации на основе анализа ===")
    
    # Рекомендации по метаданным
    if metadata_stats['has_date'] / metadata_stats['total_files'] < 0.5:
        print("1. Добавить даты в метаданные большего числа документов для лучшего версионирования")
    
    if metadata_stats['has_based_on'] / metadata_stats['total_files'] < 0.3:
        print("2. Улучшить указание связей 'based_on' для отслеживания зависимостей между документами")
    
    # Рекомендации по ссылкам
    if 'markdown' in link_types and link_types['markdown'] > 0:
        print("3. Реализовать систему абстрактных ссылок для замены прямых ссылок на markdown-файлы")
    
    if len(standard_versions) > 0:
        print("4. Внедрить механизм автоматического определения актуальных версий стандартов")
    
    # Общие рекомендации
    print("5. Создать централизованный индекс документов с метаданными для быстрого поиска")
    print("6. Разработать API для получения документов по логическим идентификаторам")
    print("7. Внедрить инструменты для автоматической проверки и обновления ссылок")

def main():
    print("=== Начало анализа документов проекта ===")
    
    # Собираем все markdown-файлы
    markdown_files = collect_markdown_files()
    
    # Анализируем паттерны именования файлов
    naming_patterns = analyze_file_naming_patterns(markdown_files)
    
    # Анализируем метаданные
    metadata_collection, metadata_stats = analyze_metadata(markdown_files)
    
    # Анализируем ссылки между документами
    links_by_file, link_targets, link_types = analyze_document_links(markdown_files)
    
    # Ищем похожие документы и возможные дубликаты
    similarity_analysis = find_similar_documents(markdown_files, metadata_collection)
    
    # Анализируем отношения между файлами
    relationships = analyze_file_relationships(metadata_collection, links_by_file)
    
    # Генерируем рекомендации
    analysis_results = {
        'naming_patterns': naming_patterns,
        'metadata_collection': metadata_collection,
        'metadata_stats': metadata_stats,
        'links_by_file': links_by_file,
        'link_targets': link_targets,
        'link_types': link_types,
        'similarity_analysis': similarity_analysis,
        'relationships': relationships
    }
    
    generate_recommendations(analysis_results)
    
    print("\n=== Сохранение результатов анализа ===")
    # Сохраняем результаты в JSON для дальнейшего использования
    # Исключаем содержимое файлов для уменьшения размера
    serializable_results = {
        'metadata_stats': metadata_stats,
        'link_types': link_types,
        'similarity_analysis': {
            'standard_versions': {k: [(f, d) for f, d in v] for k, v in similarity_analysis['standard_versions'].items()}
        },
        'recommendations': {}  # Здесь можно добавить рекомендации
    }
    
    with open('document_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    print("Результаты анализа сохранены в document_analysis_results.json")
    print("=== Анализ документов завершен ===")

if __name__ == "__main__":
    main()