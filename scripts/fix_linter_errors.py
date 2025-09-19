#!/usr/bin/env python3

"""
Автоматическое исправление ошибок линтера
Запускается после создания/изменения кода
"""

import os
import subprocess
import sys
from pathlib import Path


def run_ruff_fix(file_path: str) -> bool:
    """
    JTBD:
    Как система автоматического исправления, я хочу исправить ошибки линтера
    автоматически, чтобы код был готов к использованию без ручного вмешательства.
    """
    try:
        # Запускаем ruff check с автоисправлением в виртуальном окружении
        result = subprocess.run(
            [
                "bash",
                "-c",
                f"source .venv/bin/activate && ruff check --fix {file_path}",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            print(f"✅ {file_path}: Ошибки линтера исправлены автоматически")
            return True
        print(f"⚠️ {file_path}: Остались ошибки, требующие ручного исправления:")
        print(result.stdout)
        return False

    except FileNotFoundError:
        print("❌ Ruff не найден. Установите: pip install ruff")
        return False
    except Exception as e:
        print(f"❌ Ошибка при исправлении {file_path}: {e}")
        return False


def run_ruff_format(file_path: str) -> bool:
    """
    JTBD:
    Как система форматирования кода, я хочу автоматически отформатировать код
    согласно стандартам проекта, чтобы обеспечить единообразие стиля.
    """
    try:
        # Запускаем ruff format в виртуальном окружении
        result = subprocess.run(
            ["bash", "-c", f"source .venv/bin/activate && ruff format {file_path}"],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            print(f"✅ {file_path}: Код отформатирован")
            return True
        print(f"⚠️ {file_path}: Ошибка форматирования:")
        print(result.stderr)
        return False

    except FileNotFoundError:
        print("❌ Ruff не найден. Установите: pip install ruff")
        return False
    except Exception as e:
        print(f"❌ Ошибка при форматировании {file_path}: {e}")
        return False


def fix_file_linter_errors(file_path: str) -> bool:
    """
    JTBD:
    Как система исправления ошибок файла, я хочу исправить все ошибки линтера
    в конкретном файле, чтобы код был готов к использованию.
    """
    print(f"🔧 Исправление ошибок линтера для {file_path}")

    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return False

    # Исправляем ошибки линтера
    fix_success = run_ruff_fix(file_path)

    # Форматируем код
    format_success = run_ruff_format(file_path)

    # Проверяем результат
    if fix_success and format_success:
        print(f"✅ {file_path}: Все ошибки исправлены и код отформатирован")
        return True
    print(f"⚠️ {file_path}: Требуется дополнительное исправление")
    return False


def fix_all_linter_errors() -> None:
    """
    JTBD:
    Как система исправления всех ошибок, я хочу исправить ошибки линтера
    во всех файлах проекта, чтобы весь код соответствовал стандартам.
    """
    print("🔧 Исправление ошибок линтера во всех файлах проекта")

    # Находим все Python файлы
    project_root = Path(__file__).parent.parent
    python_files = []

    for root, dirs, files in os.walk(project_root):
        # Пропускаем виртуальные окружения и кэш
        dirs[:] = [
            d for d in dirs if d not in [".venv", "__pycache__", ".git", "node_modules"]
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    print(f"📁 Найдено {len(python_files)} Python файлов")

    fixed_count = 0
    failed_count = 0

    for file_path in python_files:
        if fix_file_linter_errors(file_path):
            fixed_count += 1
        else:
            failed_count += 1

    print("\n📊 Результат исправления:")
    print(f"   ✅ Исправлено: {fixed_count}")
    print(f"   ❌ Ошибки: {failed_count}")
    print(f"   📁 Всего файлов: {len(python_files)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Исправляем конкретный файл
        file_path = sys.argv[1]
        fix_file_linter_errors(file_path)
    else:
        # Исправляем все файлы
        fix_all_linter_errors()
