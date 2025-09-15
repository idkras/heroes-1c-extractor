#!/usr/bin/env python3
"""
Скрипт для массовой регистрации логических идентификаторов для стандартов.
"""

import os
import re
import json
import argparse
import subprocess
from typing import Dict, List, Optional

def extract_standard_name(filename: str) -> Optional[str]:
    """
    Извлекает имя стандарта из имени файла.
    Например: "1.0 process task standard by 10 may 1745 CET by Ilya Krasinsky.md" -> "process_task_standard"
    """
    basename = os.path.basename(filename)
    
    # Попытка 1: извлечение имени стандарта по стандартному формату
    pattern1 = r'^\d+\.\d+\s+(.+?)\s+(?:standard|by)'
    match = re.search(pattern1, basename, re.IGNORECASE)
    
    # Попытка 2: извлечение имени стандарта у файлов вида "heroes-gpt-bot review standard 1.2..."
    if not match:
        pattern2 = r'^(.+?)\s+standard\s+\d+\.\d+'
        match = re.search(pattern2, basename, re.IGNORECASE)
    
    # Попытка 3: извлечение имени стандарта у файлов вида "heroes-gpt_gdocs_export_standard_1.0.md"
    if not match:
        pattern3 = r'^(.+?)_standard_\d+\.\d+'
        match = re.search(pattern3, basename, re.IGNORECASE)
    
    # Попытка 4: извлечение имени стандарта у файлов вида "Vika Coaching Standard 11 may 2025..."
    if not match:
        pattern4 = r'^(.+?)\s+Standard\s+\d+'
        match = re.search(pattern4, basename, re.IGNORECASE)
    
    if match:
        standard_name = match.group(1).strip()
        # Преобразуем имя в формат snake_case
        standard_name = re.sub(r'\s+', '_', standard_name.lower())
        # Удаляем специальные символы
        standard_name = re.sub(r'[^\w_]', '', standard_name)
        # Заменяем дефисы на подчеркивания для единообразия
        standard_name = standard_name.replace('-', '_')
        return standard_name
    
    return None

def find_standard_files(directory: str = "[standards .md]") -> List[str]:
    """
    Находит все файлы стандартов в указанной директории.
    """
    standard_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and 'standard' in file.lower():
                path = os.path.join(root, file)
                # Исключаем архивы и бэкапы
                if not ('[archive]' in path or 'backups_' in path):
                    standard_files.append(path)
    
    return standard_files

def register_logical_id(path: str, identifier: str) -> bool:
    """
    Регистрирует логический идентификатор для документа.
    """
    import requests
    
    # Использование API для более быстрой регистрации (без запуска отдельного процесса)
    try:
        response = requests.post(
            "http://localhost:5001/indexer/abstract/register",
            json={"path": path, "identifier": identifier}
        )
        if response.status_code == 200 and response.json().get("success"):
            return True
        else:
            print(f"Ошибка API: {response.text}")
            return False
    except Exception as e:
        # Резервный вариант через CLI, если API недоступен
        print(f"Ошибка API, использую CLI: {e}")
        cmd = ["python", "abstract_links_cli.py", "register", path, identifier]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return 'Успешно зарегистрирован' in result.stdout
        except Exception as e:
            print(f"Ошибка при регистрации идентификатора: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Массовая регистрация логических идентификаторов для стандартов.')
    parser.add_argument('--dry-run', action='store_true', help='Только вывести список файлов и идентификаторов без регистрации')
    parser.add_argument('--directory', default='[standards .md]', help='Директория со стандартами')
    
    args = parser.parse_args()
    
    standard_files = find_standard_files(args.directory)
    print(f"Найдено {len(standard_files)} файлов стандартов")
    
    registered_count = 0
    failed_count = 0
    
    for path in standard_files:
        standard_name = extract_standard_name(os.path.basename(path))
        if standard_name:
            logical_id = f"standard:{standard_name}"
            
            if args.dry_run:
                print(f"{path} -> {logical_id}")
            else:
                if register_logical_id(path, logical_id):
                    print(f"✅ {path} -> {logical_id}")
                    registered_count += 1
                else:
                    print(f"❌ Не удалось зарегистрировать: {path} -> {logical_id}")
                    failed_count += 1
        else:
            print(f"⚠️ Не удалось извлечь имя стандарта из: {path}")
            failed_count += 1
    
    if not args.dry_run:
        print(f"\nИтоги регистрации:")
        print(f"Успешно зарегистрировано: {registered_count}")
        print(f"Не удалось зарегистрировать: {failed_count}")

if __name__ == '__main__':
    main()