#!/usr/bin/env python3
"""
JTBD: Как временный тестовый скрипт, я хочу запускать тесты без pytest,
чтобы обойти системную проблему с модулем platform.
"""

import importlib.util
import sys
from pathlib import Path


def run_test_file(test_file_path):
    """
    JTBD: Как тестовый раннер, я хочу запускать отдельные тестовые файлы,
    чтобы обеспечить тестирование без pytest.
    """
    print(f"Running tests from: {test_file_path}")

    # Загружаем модуль
    spec = importlib.util.spec_from_file_location("test_module", test_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Ищем функции, начинающиеся с test_
    test_functions = []
    for name in dir(module):
        if name.startswith('test_') and callable(getattr(module, name)):
            test_functions.append(name)

    print(f"Found {len(test_functions)} test functions")

    # Запускаем тесты
    passed = 0
    failed = 0

    for test_name in test_functions:
        test_func = getattr(module, test_name)
        try:
            print(f"  Running {test_name}...", end=" ")
            test_func()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1

    return passed, failed


def main():
    """
    JTBD: Как основной тестовый раннер, я хочу запускать все тесты,
    чтобы обеспечить полное тестирование проекта.
    """
    print("🧪 Running Tests (Pytest Alternative)")
    print("=" * 50)

    # Находим все тестовые файлы
    test_files = []
    tests_dir = Path("tests")

    if tests_dir.exists():
        for test_file in tests_dir.rglob("*.py"):
            if test_file.name.startswith("test_") or test_file.name == "simple_test.py":
                test_files.append(test_file)

    if not test_files:
        print("❌ No test files found!")
        return 1

    print(f"Found {len(test_files)} test files")
    print()

    total_passed = 0
    total_failed = 0

    # Запускаем тесты
    for test_file in test_files:
        passed, failed = run_test_file(test_file)
        total_passed += passed
        total_failed += failed
        print()

    # Результаты
    print("=" * 50)
    print("📊 Test Results:")
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  📈 Total: {total_passed + total_failed}")

    if total_failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
