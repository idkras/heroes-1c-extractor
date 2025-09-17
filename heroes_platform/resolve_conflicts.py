#!/usr/bin/env python3
"""
Скрипт для решения конфликтов зависимостей
JTBD: Как разработчик, я хочу автоматически решать конфликты зависимостей,
чтобы обеспечить стабильную работу проекта.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def resolve_dependency_conflicts():
    """Решить конфликты зависимостей"""
    print("🔧 Решение конфликтов зависимостей...")
    
    # Устанавливаем совместимые версии
    commands = [
        # Устанавливаем pydantic совместимую с mcp и fastmcp
        "pip install 'pydantic>=2.11.0,<3.0.0' --force-reinstall",
        
        # Устанавливаем typing-extensions совместимую с selenium
        "pip install 'typing-extensions>=4.14.0,<4.15.0' --force-reinstall",
        
        # Обновляем safety до совместимой версии
        "pip install 'safety>=3.6.1' --force-reinstall",
    ]
    
    for cmd in commands:
        print(f"📦 Выполняю: {cmd}")
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"❌ Ошибка: {stderr}")
        else:
            print(f"✅ Успешно: {stdout[:100]}...")

def check_conflicts():
    """Проверить оставшиеся конфликты"""
    print("\n🔍 Проверка оставшихся конфликтов...")
    
    success, stdout, stderr = run_command("pip check")
    if success:
        print("✅ Конфликтов не найдено!")
        return True
    else:
        print(f"⚠️ Найдены конфликты:\n{stderr}")
        return False

def main():
    """Основная функция"""
    print("🚀 Решение конфликтов зависимостей heroes-platform")
    print("=" * 60)
    
    # Проверяем что мы в правильной директории
    if not Path("pyproject.toml").exists():
        print("❌ Запустите скрипт из корневой директории heroes-platform")
        sys.exit(1)
    
    # Решаем конфликты
    resolve_dependency_conflicts()
    
    # Проверяем результат
    if check_conflicts():
        print("\n🎉 Все конфликты решены!")
        sys.exit(0)
    else:
        print("\n⚠️ Остались конфликты, требуется ручное вмешательство")
        sys.exit(1)

if __name__ == "__main__":
    main()
