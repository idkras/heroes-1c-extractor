#!/usr/bin/env python3
"""
Скрипт для стандартизации имен файлов контекста в проектах.
Переименовывает файлы в соответствии с форматом domain.context.md.
"""

import os
import re
import sys
from pathlib import Path
import shutil
from datetime import datetime

def create_backup(file_path):
    """
    Создает резервную копию файла.
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Путь к резервной копии
    """
    backup_dir = Path("backups") / "context_files"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{Path(file_path).name}_{timestamp}.bak"
    
    shutil.copy2(file_path, backup_path)
    print(f"💾 Создана резервная копия: {backup_path}")
    
    return backup_path

def detect_context_files(project_path):
    """
    Определяет файлы контекста в указанной директории проекта.
    
    Args:
        project_path: Путь к директории проекта
    
    Returns:
        Список путей к файлам контекста
    """
    # Регулярные выражения для поиска файлов контекста
    context_patterns = [
        r"^([a-zA-Z0-9\.-]+)[\s_]context\.md$",  # domain context.md, domain_context.md
        r"^context\.md$",                         # context.md
        r"^([a-zA-Z0-9\.-]+)\.context\.md$"       # domain.context.md (уже правильный формат)
    ]
    
    # Получаем список всех .md файлов в директории
    md_files = [f for f in project_path.glob("*.md") if f.is_file()]
    context_files = []
    
    for file_path in md_files:
        file_name = file_path.name
        
        # Проверяем по регулярным выражениям
        for pattern in context_patterns:
            if re.match(pattern, file_name):
                context_files.append(file_path)
                break
    
    # Если не нашли ни одного файла по шаблонам, проверяем содержимое
    if not context_files:
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # Читаем первые 500 символов
                    
                    # Ищем ключевые фразы, указывающие на файл контекста
                    context_indicators = [
                        "контекст проекта",
                        "цели проекта",
                        "текущий контекст",
                        "бизнес-метрика",
                        "context.md"
                    ]
                    
                    for indicator in context_indicators:
                        if indicator.lower() in content.lower():
                            context_files.append(file_path)
                            break
            except Exception:
                # Игнорируем ошибки при чтении файла
                pass
    
    return context_files

def standardize_context_files(project_dir):
    """
    Стандартизирует имена файлов контекста в указанной директории проекта.
    
    Args:
        project_dir: Путь к директории проекта
    """
    project_path = Path(project_dir)
    if not project_path.exists() or not project_path.is_dir():
        print(f"❌ Ошибка: директория {project_dir} не существует.")
        return
    
    # Регулярные выражения для поиска файлов контекста
    context_patterns = [
        r"^([a-zA-Z0-9\.-]+)[\s_]context\.md$",  # domain context.md, domain_context.md
        r"^context\.md$",                         # context.md
        r"^([a-zA-Z0-9\.-]+)\.context\.md$"       # domain.context.md (уже правильный формат)
    ]
    
    # Получаем список файлов контекста
    context_files = detect_context_files(project_path)
    
    if not context_files:
        print(f"ℹ️ В директории {project_dir} не найдено файлов контекста.")
        return
    
    print(f"🔍 Найдено файлов контекста: {len(context_files)}")
    
    for file_path in context_files:
        file_name = file_path.name
        
        # Проверяем, является ли файл файлом контекста
        is_context_file = False
        domain_name = None
        
        for pattern in context_patterns:
            match = re.match(pattern, file_name)
            if match:
                is_context_file = True
                if len(match.groups()) > 0:
                    domain_name = match.group(1)
                else:
                    # Если это просто context.md, используем имя директории проекта
                    domain_name = project_path.name
                break
        
        if not is_context_file:
            # Если файл определен по содержимому, используем имя директории проекта
            domain_name = project_path.name
            is_context_file = True
        
        if is_context_file:
            # Если файл уже имеет правильный формат, пропускаем его
            if re.match(r"^[a-zA-Z0-9\.-]+\.context\.md$", file_name):
                print(f"✅ Файл {file_name} уже соответствует стандарту именования.")
                continue
            
            # Стандартизированное имя файла
            standard_name = f"{domain_name}.context.md"
            new_path = project_path / standard_name
            
            # Проверяем, существует ли уже файл с таким именем
            if new_path.exists():
                print(f"⚠️ Файл {standard_name} уже существует. Создаем резервную копию оригинального файла.")
                create_backup(file_path)
                continue
            
            try:
                # Создаем резервную копию перед переименованием
                create_backup(file_path)
                
                # Переименовываем файл
                shutil.copy2(file_path, new_path)
                os.remove(file_path)
                print(f"✅ Файл {file_name} переименован в {standard_name}")
            except Exception as e:
                print(f"❌ Ошибка при переименовании файла {file_name}: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Использование: python standardize_context_files.py <путь к директории проекта | all>")
        print("Примеры:")
        print("  python standardize_context_files.py projects/advising_auto  # Только для указанного проекта")
        print("  python standardize_context_files.py all                    # Для всех проектов")
        return 1
    
    if sys.argv[1].lower() == 'all':
        # Обрабатываем все проекты в директории projects
        projects_dir = Path('projects')
        if not projects_dir.exists() or not projects_dir.is_dir():
            print("❌ Ошибка: директория projects не существует.")
            return 1
        
        projects = [p for p in projects_dir.iterdir() if p.is_dir()]
        for project_dir in projects:
            print(f"\n{'='*50}")
            print(f"🔍 Стандартизация файлов контекста в {project_dir}...")
            standardize_context_files(project_dir)
    else:
        # Обрабатываем только указанный проект
        project_dir = sys.argv[1]
        print(f"🔍 Стандартизация файлов контекста в {project_dir}...")
        standardize_context_files(project_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())