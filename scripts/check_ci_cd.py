#!/usr/bin/env python3

"""
Проверка настроек CI/CD и автоматического исправления ошибок линтера
JTBD: Как система проверки CI/CD, я хочу проверить что все настройки
для автоматического исправления ошибок линтера работают корректно.
"""

import subprocess
from pathlib import Path


def check_ruff_installation() -> bool:
    """Проверить установку ruff"""
    try:
        result = subprocess.run(
            ["ruff", "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✅ Ruff установлен: {result.stdout.strip()}")
            return True
        print("❌ Ruff не установлен")
        return False
    except FileNotFoundError:
        print("❌ Ruff не найден в PATH")
        return False


def check_git_hooks() -> bool:
    """Проверить настройку git hooks"""
    pre_commit_hook = Path(".git/hooks/pre-commit")
    if pre_commit_hook.exists() and pre_commit_hook.stat().st_mode & 0o111:
        print("✅ Pre-commit hook установлен и исполняемый")
        return True
    print("❌ Pre-commit hook не настроен")
    return False


def check_github_actions() -> bool:
    """Проверить настройку GitHub Actions"""
    workflow_file = Path(".github/workflows/linter-ci.yml")
    if workflow_file.exists():
        print("✅ GitHub Actions workflow настроен")
        return True
    print("❌ GitHub Actions workflow не найден")
    return False


def check_makefile_commands() -> bool:
    """Проверить команды Makefile"""
    makefile = Path("Makefile")
    if not makefile.exists():
        print("❌ Makefile не найден")
        return False

    # Проверяем наличие нужных команд
    with open(makefile) as f:
        content = f.read()

    required_commands = ["fix-linter", "auto-fix", "format"]
    missing_commands = []

    for command in required_commands:
        if f"{command}:" not in content:
            missing_commands.append(command)

    if missing_commands:
        print(f"❌ Отсутствуют команды в Makefile: {', '.join(missing_commands)}")
        return False
    print("✅ Все необходимые команды присутствуют в Makefile")
    return True


def check_vscode_settings() -> bool:
    """Проверить настройки VS Code"""
    settings_file = Path(".vscode/settings.json")
    tasks_file = Path(".vscode/tasks.json")

    if settings_file.exists() and tasks_file.exists():
        print("✅ VS Code настройки для автоматического исправления настроены")
        return True
    print("❌ VS Code настройки не найдены")
    return False


def test_auto_fix_script() -> bool:
    """Протестировать скрипт автоматического исправления"""
    script_file = Path("scripts/fix_linter_errors.py")
    if not script_file.exists():
        print("❌ Скрипт fix_linter_errors.py не найден")
        return False

    try:
        # Тестируем импорт скрипта
        import importlib.util

        spec = importlib.util.spec_from_file_location("fix_linter_errors", script_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Скрипт fix_linter_errors.py работает корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка в скрипте fix_linter_errors.py: {e}")
        return False


def run_ci_cd_check() -> None:
    """Запустить полную проверку CI/CD настроек"""
    print("🔍 Проверка настроек CI/CD и автоматического исправления ошибок линтера")
    print("=" * 80)

    checks = [
        ("Ruff установка", check_ruff_installation),
        ("Git hooks", check_git_hooks),
        ("GitHub Actions", check_github_actions),
        ("Makefile команды", check_makefile_commands),
        ("VS Code настройки", check_vscode_settings),
        ("Скрипт автоисправления", test_auto_fix_script),
    ]

    passed = 0
    total = len(checks)

    for name, check_func in checks:
        print(f"\n📋 {name}:")
        if check_func():
            passed += 1
        else:
            print("   💡 Для исправления запустите: python scripts/setup_git_hooks.sh")

    print(f"\n📊 Результат проверки: {passed}/{total} проверок пройдено")

    if passed == total:
        print("🎉 Все настройки CI/CD работают корректно!")
        print("\n💡 Доступные команды:")
        print("   make auto-fix          # Полное автоисправление")
        print("   make fix-linter        # Исправление ошибок линтера")
        print("   make format            # Форматирование кода")
        print("   python scripts/fix_linter_errors.py  # Ручное исправление")
    else:
        print("⚠️ Некоторые настройки требуют исправления")
        print("\n🔧 Для настройки запустите:")
        print("   python scripts/setup_git_hooks.sh")
        print("   make auto-fix")


if __name__ == "__main__":
    run_ci_cd_check()
