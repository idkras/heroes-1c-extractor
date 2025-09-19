#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Active Validation Protocol команд
"""

import json
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

# Импортируем функции напрямую
import sys

sys.path.append("src")
from heroes_mcp.src.heroes_mcp_server import (
    registry_docs_audit,
    registry_gap_report,
    registry_output_validate,
    registry_release_block,
)


def test_registry_output_validate():
    """Тест команды registry_output_validate"""
    print("🧪 Тестирую registry_output_validate...")

    # Тест с существующим файлом
    result = registry_output_validate(
        jtbd="пользователь может найти сообщения по дате",
        artifact="clients/ifscourse.com/chat.md",
    )

    print("✅ Результат:")
    print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    print()


def test_registry_docs_audit():
    """Тест команды registry_docs_audit"""
    print("🧪 Тестирую registry_docs_audit...")

    result = registry_docs_audit(
        paths="clients/ifscourse.com/chat.md,clients/ifscourse.com/README.md"
    )

    print("✅ Результат:")
    print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    print()


def test_registry_gap_report():
    """Тест команды registry_gap_report"""
    print("🧪 Тестирую registry_gap_report...")

    result = registry_gap_report(
        expected="сообщения сгруппированы по дням с заголовками",
        actual="сообщения в одной куче без группировки",
        decision="fix",
    )

    print("✅ Результат:")
    print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    print()


def test_registry_release_block():
    """Тест команды registry_release_block"""
    print("🧪 Тестирую registry_release_block...")

    result = registry_release_block(until="validation-complete")

    print("✅ Результат:")
    print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    print()


if __name__ == "__main__":
    print("🚀 Тестирование Active Validation Protocol команд")
    print("=" * 60)

    test_registry_output_validate()
    test_registry_docs_audit()
    test_registry_gap_report()
    test_registry_release_block()

    print("✅ Все тесты завершены!")
