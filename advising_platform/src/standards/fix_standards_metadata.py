#!/usr/bin/env python3
"""
Скрипт для автоматического исправления метаданных стандартов.

GREEN фаза TDD: исправляет недостающие метаданные в стандартах
для достижения соответствия Task Master и Registry Standard.

Автор: AI Assistant  
Дата: 22 May 2025
"""

import os
import re
import sys
from datetime import datetime

def fix_standard_metadata(file_path):
    """Исправляет метаданные в стандарте."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, есть ли уже метаданные
        if '<!-- 🔒 PROTECTED SECTION: BEGIN -->' in content:
            print(f"✅ {os.path.basename(file_path)} - метаданные уже есть")
            return True
        
        # Создаем метаданные
        filename = os.path.basename(file_path)
        
        # Определяем версию из имени файла
        version_match = re.search(r'v?(\d+\.\d+)', filename)
        version = version_match.group(1) if version_match else "1.0"
        
        # Извлекаем теги из содержимого и имени файла
        tags = ["standard"]
        if "design" in filename.lower() or "дизайн" in content.lower():
            tags.append("design")
        if "qa" in filename.lower() or "качество" in content.lower():
            tags.append("quality")
        if "web" in filename.lower():
            tags.append("web")
        if "interface" in filename.lower() or "интерфейс" in content.lower():
            tags.append("interface")
        
        metadata = f"""<!-- 🔒 PROTECTED SECTION: BEGIN -->
type: standard
version: {version}
status: Active
updated: 22 May 2025, 15:47 CET by AI Assistant
tags: {", ".join(tags)}
<!-- 🔒 PROTECTED SECTION: END -->

"""
        
        # Добавляем метаданные в начало файла
        new_content = metadata + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {os.path.basename(file_path)} - метаданные добавлены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в {file_path}: {e}")
        return False

def main():
    """Основная функция скрипта."""
    standards_dir = "[standards .md]"
    
    if not os.path.exists(standards_dir):
        print(f"❌ Директория {standards_dir} не найдена")
        return
    
    # Проблемные файлы из тестов
    problem_files = [
        "[standards .md]/4. interface · design/[archive]/rename_backups/design_standard_v1.0.md"
    ]
    
    fixed_count = 0
    total_count = 0
    
    # Исправляем конкретные проблемные файлы
    for file_path in problem_files:
        if os.path.exists(file_path):
            total_count += 1
            if fix_standard_metadata(file_path):
                fixed_count += 1
    
    # Ищем другие файлы без метаданных
    for root, dirs, files in os.walk(standards_dir):
        for file in files:
            if file.endswith('.md') and 'standard' in file.lower():
                file_path = os.path.join(root, file)
                
                if file_path not in problem_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if 'type: standard' not in content and len(content) > 100:
                            total_count += 1
                            if fix_standard_metadata(file_path):
                                fixed_count += 1
                    except Exception:
                        continue
    
    print(f"\n📊 Результат: исправлено {fixed_count} из {total_count} стандартов")

if __name__ == "__main__":
    main()