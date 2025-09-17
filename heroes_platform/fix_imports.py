#!/usr/bin/env python3
"""
Скрипт для массового исправления импортов в heroes-platform
Исправляет импорты mcp_server → heroes_mcp и credentials_manager → shared.credentials_manager
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Исправляет импорты в одном файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Исправления импортов
        replacements = [
            # mcp_server → heroes_mcp
            (r'from heroes_mcp.src.heroes_mcp_server import', 'from heroes_mcp.src.heroes_mcp_server import'),
            (r'import heroes_mcp.src.heroes_mcp_server as mcp_server', 'import heroes_mcp.src.heroes_mcp_server as mcp_server'),
            (r'from mcp_server\.', 'from heroes_mcp.src.'),
            
            # credentials_manager → shared.credentials_manager
            (r'from shared.credentials_manager import', 'from shared.credentials_manager import'),
            (r'import shared.credentials_manager as credentials_manager', 'import shared.credentials_manager as credentials_manager'),
            (r'from \.credentials_manager import', 'from shared.credentials_manager import'),
            (r'from heroes_mcp\.src\.credentials_manager import', 'from shared.credentials_manager import'),
            
            # Исправления для тестов
            (r'from heroes_mcp.src.heroes_mcp_server import', 'from heroes_mcp.src.heroes_mcp_server import'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Записываем только если были изменения
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Исправлен: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в файле {file_path}: {e}")
        return False

def main():
    """Основная функция"""
    heroes_platform_path = Path(__file__).parent
    fixed_count = 0
    total_count = 0
    
    # Ищем все Python файлы
    for py_file in heroes_platform_path.rglob("*.py"):
        # Пропускаем __pycache__ и .venv
        if "__pycache__" in str(py_file) or ".venv" in str(py_file):
            continue
            
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print(f"\n📊 Результат:")
    print(f"   Всего файлов: {total_count}")
    print(f"   Исправлено: {fixed_count}")
    print(f"   Без изменений: {total_count - fixed_count}")

if __name__ == "__main__":
    main()
