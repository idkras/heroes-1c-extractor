#!/usr/bin/env python3
"""
Скрипт для анализа пересечений содержимого между стандартами.

Этот скрипт выявляет похожие стандарты и создает матрицу пересечений,
что помогает в процессе консолидации стандартов.

Использование:
    python analyze_standards_overlap.py [директория]

Аргументы:
    директория - путь к директории со стандартами (по умолчанию: текущая директория)

Примеры:
    python analyze_standards_overlap.py
    python analyze_standards_overlap.py "[standards .md]"
"""

import os
import re
import sys
from pathlib import Path
import difflib
import json
from collections import defaultdict
import argparse

# Цветные обозначения для вывода
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'
BOLD = '\033[1m'

# Регулярные выражения для извлечения информации
TITLE_REGEX = r'^#\s+(.+?)$'
PROTECTED_SECTION_BEGIN = r'<!--\s*🔒\s*PROTECTED SECTION:\s*BEGIN\s*-->'
PROTECTED_SECTION_END = r'<!--\s*🔒\s*PROTECTED SECTION:\s*END\s*-->'
STANDARD_ID_REGEX = r'standard_id:\s*([^\s]+)'
LOGICAL_ID_REGEX = r'logical_id:\s*([^\s]+)'


def extract_metadata(content):
    """Извлекает метаданные из защищенного раздела стандарта."""
    metadata = {}
    
    # Извлекаем заголовок стандарта
    title_match = re.search(TITLE_REGEX, content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Извлекаем защищенный раздел
    protected_match = re.search(
        f"{PROTECTED_SECTION_BEGIN}(.*?){PROTECTED_SECTION_END}",
        content, 
        re.DOTALL
    )
    
    if protected_match:
        protected_content = protected_match.group(1)
        
        # Извлекаем standard_id
        standard_id_match = re.search(STANDARD_ID_REGEX, protected_content)
        if standard_id_match:
            metadata['standard_id'] = standard_id_match.group(1).strip()
        
        # Извлекаем logical_id
        logical_id_match = re.search(LOGICAL_ID_REGEX, protected_content)
        if logical_id_match:
            metadata['logical_id'] = logical_id_match.group(1).strip()
        
        # Извлекаем все строки с related to и integrated
        metadata['related'] = []
        metadata['integrated'] = []
        
        for line in protected_content.split('\n'):
            if 'related to:' in line:
                metadata['related'].append(line.strip())
            elif 'integrated:' in line:
                metadata['integrated'].append(line.strip())
    
    return metadata


def extract_sections(content):
    """Извлекает разделы стандарта на основе заголовков."""
    sections = {}
    
    # Пропускаем защищенный раздел
    if PROTECTED_SECTION_BEGIN in content and PROTECTED_SECTION_END in content:
        parts = content.split(PROTECTED_SECTION_END, 1)
        if len(parts) > 1:
            content = parts[1]
    
    # Находим все заголовки второго уровня (##)
    section_pattern = r'##\s+(.+?)\n(.*?)(?=##|\Z)'
    for match in re.finditer(section_pattern, content, re.DOTALL):
        section_title = match.group(1).strip()
        section_content = match.group(2).strip()
        sections[section_title] = section_content
    
    return sections


def calculate_similarity(text1, text2):
    """Рассчитывает сходство между двумя текстами."""
    if not text1 or not text2:
        return 0.0
    
    # Используем SequenceMatcher для сравнения текстов
    sequence_matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity = sequence_matcher.ratio()
    return similarity


def analyze_section_overlap(standards_data):
    """Анализирует пересечение разделов между стандартами."""
    section_overlap = defaultdict(lambda: defaultdict(dict))
    
    # Для каждой пары стандартов
    standard_ids = list(standards_data.keys())
    for i, standard1_id in enumerate(standard_ids):
        standard1 = standards_data[standard1_id]
        
        for j in range(i+1, len(standard_ids)):
            standard2_id = standard_ids[j]
            standard2 = standards_data[standard2_id]
            
            # Находим общие разделы
            common_sections = set(standard1['sections'].keys()) & set(standard2['sections'].keys())
            
            # Рассчитываем сходство для каждого общего раздела
            for section in common_sections:
                content1 = standard1['sections'][section]
                content2 = standard2['sections'][section]
                
                similarity = calculate_similarity(content1, content2)
                
                # Сохраняем, если сходство больше порога
                if similarity > 0.3:  # можно настроить порог
                    section_overlap[standard1_id][standard2_id][section] = similarity
                    section_overlap[standard2_id][standard1_id][section] = similarity
    
    return section_overlap


def analyze_overall_similarity(standards_data):
    """Анализирует общее сходство между стандартами."""
    overall_similarity = defaultdict(dict)
    
    # Для каждой пары стандартов
    standard_ids = list(standards_data.keys())
    for i, standard1_id in enumerate(standard_ids):
        standard1 = standards_data[standard1_id]
        
        for j in range(i+1, len(standard_ids)):
            standard2_id = standard_ids[j]
            standard2 = standards_data[standard2_id]
            
            # Объединяем все разделы
            content1 = " ".join(standard1['sections'].values())
            content2 = " ".join(standard2['sections'].values())
            
            # Рассчитываем общее сходство
            similarity = calculate_similarity(content1, content2)
            
            # Сохраняем результат
            overall_similarity[standard1_id][standard2_id] = similarity
            overall_similarity[standard2_id][standard1_id] = similarity
    
    return overall_similarity


def identify_duplicates(overall_similarity, threshold=0.8):
    """Определяет дублирующиеся стандарты на основе общего сходства."""
    duplicates = []
    
    for standard1_id, similarities in overall_similarity.items():
        for standard2_id, similarity in similarities.items():
            if similarity >= threshold and standard1_id < standard2_id:  # проверяем только одно направление
                duplicates.append((standard1_id, standard2_id, similarity))
    
    # Сортируем по убыванию сходства
    duplicates.sort(key=lambda x: x[2], reverse=True)
    return duplicates


def print_overlap_report(standards_data, section_overlap, overall_similarity, duplicates):
    """Выводит отчет о пересечениях и дублировании стандартов."""
    print(f"\n{BOLD}== ОТЧЕТ О ПЕРЕСЕЧЕНИЯХ СТАНДАРТОВ =={ENDC}\n")
    
    # Выводим дубликаты
    if duplicates:
        print(f"\n{BOLD}{RED}ОБНАРУЖЕНЫ ПОТЕНЦИАЛЬНЫЕ ДУБЛИКАТЫ:{ENDC}\n")
        for standard1_id, standard2_id, similarity in duplicates:
            print(f"  {RED}• {standards_data[standard1_id]['file']} и {standards_data[standard2_id]['file']}{ENDC}")
            print(f"    Сходство: {similarity:.2%}")
            print(f"    Название 1: {standards_data[standard1_id]['metadata'].get('title', 'Нет заголовка')}")
            print(f"    Название 2: {standards_data[standard2_id]['metadata'].get('title', 'Нет заголовка')}")
            print()
    
    # Выводим стандарты с высоким пересечением разделов
    print(f"\n{BOLD}{YELLOW}СТАНДАРТЫ С ВЫСОКИМ ПЕРЕСЕЧЕНИЕМ РАЗДЕЛОВ:{ENDC}\n")
    for standard1_id, overlaps in section_overlap.items():
        for standard2_id, sections in overlaps.items():
            if sections and standard1_id < standard2_id:  # проверяем только одно направление
                high_overlap_sections = {section: similarity for section, similarity in sections.items() if similarity > 0.6}
                if high_overlap_sections:
                    print(f"  {YELLOW}• {standards_data[standard1_id]['file']} и {standards_data[standard2_id]['file']}{ENDC}")
                    print(f"    Общее сходство: {overall_similarity[standard1_id][standard2_id]:.2%}")
                    print(f"    Разделы с высоким пересечением:")
                    for section, similarity in high_overlap_sections.items():
                        print(f"      - {section}: {similarity:.2%}")
                    print()
    
    # Выводим рекомендации по консолидации
    print(f"\n{BOLD}{GREEN}РЕКОМЕНДАЦИИ ПО КОНСОЛИДАЦИИ:{ENDC}\n")
    
    # Группировка по категориям
    category_groups = defaultdict(list)
    for standard_id, data in standards_data.items():
        file_path = data['file']
        parts = file_path.split('/')
        if len(parts) > 2:
            category = parts[-2]  # Предполагаем, что категория - это предпоследняя часть пути
            if "archive" not in category.lower():  # Исключаем архивные директории
                category_groups[category].append(standard_id)
    
    # Для каждой категории
    for category, standards in category_groups.items():
        if len(standards) > 1:
            print(f"  {GREEN}• Категория: {category}{ENDC}")
            print(f"    Стандартов в категории: {len(standards)}")
            
            # Находим сильно похожие стандарты в этой категории
            category_duplicates = []
            for i, standard1_id in enumerate(standards):
                for j in range(i+1, len(standards)):
                    standard2_id = standards[j]
                    if standard2_id in overall_similarity.get(standard1_id, {}):
                        similarity = overall_similarity[standard1_id][standard2_id]
                        if similarity > 0.4:  # Порог для рекомендации объединения
                            category_duplicates.append((standard1_id, standard2_id, similarity))
            
            # Сортируем по сходству
            category_duplicates.sort(key=lambda x: x[2], reverse=True)
            
            if category_duplicates:
                print(f"    Рекомендуется объединить:")
                for standard1_id, standard2_id, similarity in category_duplicates:
                    print(f"      - {standards_data[standard1_id]['metadata'].get('title', standards_data[standard1_id]['file'])} и {standards_data[standard2_id]['metadata'].get('title', standards_data[standard2_id]['file'])}")
                    print(f"        Сходство: {similarity:.2%}")
            print()
    
    # Общие рекомендации
    if duplicates:
        print(f"  {BOLD}Рекомендация 1:{ENDC} Удалить явные дубликаты и оставить только последние версии стандартов.")
    
    print(f"  {BOLD}Рекомендация 2:{ENDC} Объединить стандарты с высоким пересечением содержания в рамках одной категории.")
    print(f"  {BOLD}Рекомендация 3:{ENDC} Использовать секцию 'integrated' для указания зависимостей вместо дублирования контента.")
    print(f"  {BOLD}Рекомендация 4:{ENDC} Создать иерархию стандартов, где общие принципы вынесены в родительские стандарты.")
    
    print(f"\n{BOLD}ЭКСПОРТ РЕЗУЛЬТАТОВ:{ENDC}")
    export_file = "standards_overlap_analysis.json"
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump({
            'duplicates': duplicates,
            'section_overlap': {k: dict(v) for k, v in section_overlap.items()},
            'overall_similarity': {k: dict(v) for k, v in overall_similarity.items()}
        }, f, ensure_ascii=False, indent=2)
    print(f"  Результаты анализа сохранены в файл: {export_file}")


def analyze_standards_directory(base_dir="."):
    """Анализирует стандарты в указанной директории."""
    # Преобразуем путь в объект Path для кросс-платформенной совместимости
    base_path = Path(base_dir)
    
    print(f"\n{BOLD}Анализ стандартов в директории: {base_path}{ENDC}\n")
    
    # Собираем все файлы .md рекурсивно
    md_files = []
    import glob
    
    for file_path in glob.glob(str(base_path) + '/**/*.md', recursive=True):
        path = Path(file_path)
        # Исключаем файлы в директориях archive
        if "archive" not in str(path).lower():
            md_files.append(path)
    
    print(f"Найдено {len(md_files)} файлов .md (исключая архивы)")
    
    # Собираем данные о стандартах
    standards_data = {}
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем метаданные и разделы
            metadata = extract_metadata(content)
            sections = extract_sections(content)
            
            # Если нет метаданных или разделов, пропускаем файл
            if not metadata or not sections:
                print(f"  {YELLOW}Пропуск файла (не похож на стандарт): {file_path}{ENDC}")
                continue
            
            # Создаем уникальный идентификатор для стандарта
            standard_id = metadata.get('standard_id') or metadata.get('logical_id') or str(file_path.name)
            
            # Сохраняем данные о стандарте
            standards_data[standard_id] = {
                'file': str(file_path),
                'metadata': metadata,
                'sections': sections
            }
            
            print(f"  {GREEN}Обработан стандарт: {standard_id} - {file_path.name}{ENDC}")
            
        except Exception as e:
            print(f"  {RED}Ошибка при обработке файла {file_path}: {e}{ENDC}")
    
    print(f"\nПроанализировано {len(standards_data)} стандартов")
    
    # Если стандартов меньше 2, нечего анализировать
    if len(standards_data) < 2:
        print(f"{YELLOW}Найдено меньше 2 стандартов. Анализ пересечений невозможен.{ENDC}")
        return
    
    # Анализируем пересечения
    section_overlap = analyze_section_overlap(standards_data)
    overall_similarity = analyze_overall_similarity(standards_data)
    duplicates = identify_duplicates(overall_similarity)
    
    # Выводим отчет
    print_overlap_report(standards_data, section_overlap, overall_similarity, duplicates)


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description='Анализ пересечений содержимого между стандартами')
    parser.add_argument('directory', nargs='?', default=".", help='Директория со стандартами (по умолчанию: текущая)')
    args = parser.parse_args()
    
    analyze_standards_directory(args.directory)


if __name__ == "__main__":
    main()