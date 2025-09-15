#!/usr/bin/env python3
"""
Скрипт для объединения всех next_actions.md из папок проектов в один файл в корне projects/.
После выполнения локальные файлы next_actions.md будут перемещены в архив.
"""

import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

def create_backup(file_path):
    """
    Создает резервную копию файла.
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Путь к резервной копии
    """
    backup_dir = Path("backups") / "next_actions"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{Path(file_path).name}_{timestamp}.bak"
    
    shutil.copy2(file_path, backup_path)
    print(f"💾 Создана резервная копия: {backup_path}")
    
    return backup_path

def extract_project_section(content, project_name):
    """
    Извлекает секцию с задачами конкретного проекта из next_actions.md.
    
    Args:
        content: Содержимое файла
        project_name: Имя проекта
    
    Returns:
        Словарь с информацией о проекте и его задачах
    """
    # Пытаемся найти заголовок проекта
    project_title = None
    responsible = None
    
    # Ищем заголовок проекта и ответственного
    title_match = re.search(r'#+\s+.*' + re.escape(project_name) + r'.*?@(\w+)', content, re.IGNORECASE)
    if title_match:
        responsible = title_match.group(1)
    
    # Определим, есть ли заголовок проекта в content
    if not title_match:
        # Если нет, создаем структуру сами
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if non_empty_lines:
            # Извлекаем информацию из имени файла
            project_title = f"### {project_name}"
            tasks = content
        else:
            return None
    else:
        # Если заголовок проекта найден, извлекаем все содержимое между ним и следующим заголовком
        pattern = r'(#+\s+.*' + re.escape(project_name) + r'.*?)(?=#+\s+|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            tasks = match.group(1)
        else:
            # Если не удалось извлечь содержимое, берем весь контент
            tasks = content
    
    return {
        "title": project_title,
        "responsible": responsible,
        "tasks": tasks
    }

def merge_next_actions():
    """
    Объединяет все next_actions.md из папок проектов в один файл в корне projects/.
    """
    projects_dir = Path("projects")
    if not projects_dir.exists() or not projects_dir.is_dir():
        print("❌ Ошибка: директория projects не существует.")
        return 1
    
    # Путь к общему файлу next_actions.md
    root_next_actions = projects_dir / "next_actions.md"
    
    # Если файл существует, создаем резервную копию
    if root_next_actions.exists():
        create_backup(root_next_actions)
    
    # Ищем все next_actions.md в подпапках
    project_next_actions = []
    for project_dir in [d for d in projects_dir.iterdir() if d.is_dir()]:
        next_actions_file = project_dir / "next_actions.md"
        if next_actions_file.exists() and next_actions_file.is_file():
            project_next_actions.append((project_dir.name, next_actions_file))
    
    if not project_next_actions:
        print("✅ Не найдено локальных next_actions.md для объединения.")
        return 0
    
    # Читаем содержимое общего файла next_actions.md, если он существует
    root_content = ""
    if root_next_actions.exists():
        with open(root_next_actions, 'r', encoding='utf-8') as f:
            root_content = f.read()
    
    # Собираем структуру проектов из общего файла
    root_projects = {}
    if root_content:
        # Ищем все заголовки проектов
        project_headers = re.findall(r'#+\s+(.*?)\s+@(\w+)', root_content)
        
        for project_header in project_headers:
            project_name = project_header[0].strip()
            responsible = project_header[1]
            
            # Ищем содержимое проекта
            pattern = r'#+\s+' + re.escape(project_name) + r'\s+@' + re.escape(responsible) + r'(.*?)(?=#+\s+|\Z)'
            match = re.search(pattern, root_content, re.DOTALL)
            if match:
                project_content = match.group(1).strip()
                root_projects[project_name] = {
                    "responsible": responsible,
                    "content": project_content
                }
    
    # Обрабатываем каждый найденный файл next_actions.md
    for project_name, file_path in project_next_actions:
        print(f"🔍 Обработка: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Ошибка при чтении файла {file_path}: {str(e)}")
            continue
        
        # Извлекаем секцию проекта
        project_data = extract_project_section(content, project_name)
        if not project_data:
            print(f"⚠️ Не удалось извлечь данные проекта из {file_path}")
            continue
        
        # Создаем резервную копию файла
        create_backup(file_path)
        
        # Добавляем извлеченные данные в общий файл
        if project_name in root_projects:
            # Если проект уже есть в общем файле, обновляем задачи
            print(f"⚠️ Проект {project_name} уже существует в общем файле. Обновляем задачи.")
            # Здесь можно реализовать более сложную логику слияния
        
        # Добавляем проект в общий файл
        root_projects[project_name] = {
            "responsible": project_data["responsible"] or "Ответственный",
            "content": project_data["tasks"]
        }
        
        # Удаляем исходный файл
        try:
            os.rename(file_path, str(file_path) + ".bak")
            print(f"✅ Файл {file_path} перемещен в {file_path}.bak")
        except Exception as e:
            print(f"❌ Ошибка при перемещении файла {file_path}: {str(e)}")
    
    # Формируем обновленное содержимое общего файла
    new_content = []
    
    # Сохраняем заголовок и метаданные из исходного файла
    header_match = re.search(r'^(.*?)\n#+\s+', root_content, re.DOTALL)
    if header_match:
        new_content.append(header_match.group(1).strip())
    else:
        new_content.append(f"""# 📋 Журнал задач по всем проектам

updated: {datetime.now().strftime("%d %b %Y, %H:%M")} CET by AI Assistant  
based on: Process Task Standard, версия 10 may 2025, 17:45 CET

## 👥 Структура команды

- **@Илья Красинский** - руководитель команды и эксперт
- **@Маргарита** - отвечает за качество процессов 
- **@Константин** - менеджер проектов
- **@Алдар** - менеджер команды
- **@Юст** - дата-саентист
""")
    
    # Добавляем новый раздел обновлений
    new_content.append(f"\n## 📊 Обновление от {datetime.now().strftime('%d %b %Y, %H:%M')} CET by AI Assistant\n")
    new_content.append("### 🌟 Обновленные задачи\n")
    
    # Добавляем разделы проектов
    for project_name, project_data in root_projects.items():
        responsible = project_data["responsible"]
        content = project_data["content"]
        
        # Формируем заголовок проекта
        if not content.startswith(f"### {project_name}"):
            new_content.append(f"#### {project_name} @{responsible}")
        
        # Добавляем содержимое проекта
        new_content.append(content.strip())
        new_content.append("")  # Пустая строка для разделения проектов
    
    # Записываем обновленное содержимое в общий файл
    with open(root_next_actions, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_content))
    
    print(f"✅ Объединенный файл next_actions.md создан: {root_next_actions}")
    return 0

if __name__ == "__main__":
    sys.exit(merge_next_actions())