#!/usr/bin/env python3
"""
Скрипт для проверки совместимости зависимостей
JTBD: Как разработчик, я хочу проверить совместимость зависимостей,
чтобы избежать конфликтов версий и проблем с импортами.
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


def check_imports():
    """Проверить импорты критических библиотек"""
    critical_imports = [
        "telethon",
        "nest_asyncio",
        "PyJWT",
        "weasyprint",
        "PyPDF2",
        "gql",
        "tomli",
        "mcp",
        "fastmcp",
    ]

    print("🔍 Проверка импортов критических библиотек...")
    failed_imports = []

    for module in critical_imports:
        success, stdout, stderr = run_command(
            f"python -c 'import {module}; print(f\"✅ {module} импортируется успешно\")'"
        )
        if not success:
            failed_imports.append(module)
            print(f"❌ {module}: {stderr.strip()}")
        else:
            print(stdout.strip())

    return len(failed_imports) == 0, failed_imports


def check_conflicts():
    """Проверить конфликты зависимостей"""
    print("\n🔍 Проверка конфликтов зависимостей...")
    success, stdout, stderr = run_command("pip check")

    if success:
        print("✅ Конфликтов зависимостей не найдено")
        return True, []
    else:
        print("❌ Найдены конфликты:")
        print(stderr)
        return False, stderr.split("\n")


def check_mypy_errors():
    """Проверить количество ошибок mypy"""
    print("\n🔍 Проверка ошибок mypy...")
    success, stdout, stderr = run_command("python -m mypy --version")
    if not success:
        print("❌ mypy не установлен")
        return False, 999

    # Подсчитываем ошибки (упрощенная версия)
    success, stdout, stderr = run_command(
        "find . -name '*.py' -exec python -m mypy {} \\; 2>&1 | grep -c 'error:' || true"
    )
    error_count = int(stdout.strip()) if stdout.strip().isdigit() else 0

    if error_count == 0:
        print("✅ Ошибок mypy не найдено")
    else:
        print(f"⚠️ Найдено {error_count} ошибок mypy")

    return error_count < 50, error_count


def main():
    """Основная функция"""
    print("🚀 Проверка зависимостей heroes-platform")
    print("=" * 50)

    # Проверяем что мы в правильной директории
    if not Path("pyproject.toml").exists():
        print("❌ Запустите скрипт из корневой директории heroes-platform")
        sys.exit(1)

    # Проверяем наличие главного файла зависимостей
    if not Path("requirements_main.txt").exists():
        print("❌ Файл requirements_main.txt не найден")
        print("💡 Создайте его на основе requirements.txt")
        sys.exit(1)

    # Активируем виртуальное окружение
    print("🔧 Активация виртуального окружения...")
    success, stdout, stderr = run_command(
        "source .venv/bin/activate && python --version"
    )
    if not success:
        print("❌ Не удалось активировать .venv")
        sys.exit(1)

    # Выполняем проверки
    imports_ok, failed_imports = check_imports()
    conflicts_ok, conflicts = check_conflicts()
    mypy_ok, mypy_errors = check_mypy_errors()

    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 50)

    if imports_ok:
        print("✅ Все критические импорты работают")
    else:
        print(f"❌ Проблемы с импортами: {failed_imports}")

    if conflicts_ok:
        print("✅ Конфликтов зависимостей нет")
    else:
        print("❌ Есть конфликты зависимостей")

    if mypy_ok:
        print("✅ Количество ошибок mypy в норме")
    else:
        print(f"⚠️ Много ошибок mypy: {mypy_errors}")

    # Общая оценка
    total_score = sum([imports_ok, conflicts_ok, mypy_ok])
    print(f"\n🎯 Общая оценка: {total_score}/3")

    if total_score == 3:
        print("🎉 Все проверки пройдены успешно!")
        return 0
    elif total_score >= 2:
        print("⚠️ Есть незначительные проблемы")
        return 1
    else:
        print("❌ Критические проблемы требуют исправления")
        return 2


if __name__ == "__main__":
    sys.exit(main())
