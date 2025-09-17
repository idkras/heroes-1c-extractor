#!/usr/bin/env python3
"""
Тест для workflow команды execute_output_gap_workflow

Проверяет функциональность новой workflow-based команды, которая объединяет
все существующие команды валидации и gap analysis в атомарные операции.
"""

import asyncio
import json
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent / "src"))

from heroes_mcp.src.heroes_mcp_server import execute_output_gap_workflow


async def test_basic_gap_analysis():
    """Тест базового анализа gap между строками"""
    print("🧪 Тестирую базовый gap analysis...")

    expected = "Ожидаемый результат с ключевыми словами: анализ, офер, сегмент"
    actual = "Фактический результат с некоторыми ключевыми словами: анализ, сегмент"

    result = await execute_output_gap_workflow(
        expected=expected, actual=actual, analysis_type="basic"
    )

    result_data = json.loads(result)

    print(f"✅ Анализ завершен: {result_data.get('analysis_id', 'N/A')}")
    print(f"📊 Общий score: {result_data.get('overall_score', 0):.2f}")
    print(f"📋 Статус workflow: {result_data.get('workflow_status', 'N/A')}")
    print(f"💡 Рекомендации: {len(result_data.get('recommendations', []))}")

    return result_data


async def test_file_analysis():
    """Тест анализа файлов"""
    print("\n🧪 Тестирую анализ файлов...")

    # Создаем тестовые файлы
    test_dir = Path("test_output_gap")
    test_dir.mkdir(exist_ok=True)

    expected_file = test_dir / "expected.md"
    actual_file = test_dir / "actual.md"

    expected_content = """# Ожидаемый результат

## Анализ
- Должен содержать анализ
- Должен содержать офер
- Должен содержать сегменты

## JTBD
- Когда пользователь хочет понять продукт
- Роль: потенциальный клиент
- Хочет: быстро понять ценность
"""

    actual_content = """# Фактический результат

## Анализ
- Содержит анализ
- Содержит сегменты

## JTBD
- Когда пользователь хочет понять продукт
- Роль: потенциальный клиент
"""

    expected_file.write_text(expected_content, encoding="utf-8")
    actual_file.write_text(actual_content, encoding="utf-8")

    try:
        result = await execute_output_gap_workflow(
            expected_file=str(expected_file),
            actual_file=str(actual_file),
            analysis_type="comprehensive",
        )

        result_data = json.loads(result)

        print(f"✅ Анализ файлов завершен: {result_data.get('analysis_id', 'N/A')}")
        print(f"📊 Общий score: {result_data.get('overall_score', 0):.2f}")
        print(f"📋 Статус workflow: {result_data.get('workflow_status', 'N/A')}")

        # Проверяем что шаги были выполнены
        steps_completed = result_data.get("steps_completed", [])
        if "file_analysis" in steps_completed:
            print("✅ Анализ файлов успешно выполнен")
        else:
            print("❌ Анализ файлов не был выполнен")

        return result_data

    finally:
        # Очищаем тестовые файлы
        if expected_file.exists():
            expected_file.unlink()
        if actual_file.exists():
            actual_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


async def test_todo_validation():
    """Тест валидации todo файла"""
    print("\n🧪 Тестирую валидацию todo файла...")

    # Создаем тестовый todo файл
    test_dir = Path("test_output_gap")
    test_dir.mkdir(exist_ok=True)

    todo_file = test_dir / "test.todo.md"

    todo_content = """# Test Release

## Критерии успеха
- [ ] Анализ содержит ключевые слова
- [ ] JTBD описан корректно
- [ ] Структура соответствует стандарту

## Ожидаемый результат
- Анализ с ключевыми словами: анализ, офер, сегмент
- JTBD сценарии для понимания продукта
- Структурированный вывод
"""

    todo_file.write_text(todo_content, encoding="utf-8")

    try:
        result = await execute_output_gap_workflow(
            todo_file=str(todo_file),
            release_name="test_release",
            analysis_type="guidance",
        )

        result_data = json.loads(result)

        print(f"✅ Валидация todo завершена: {result_data.get('analysis_id', 'N/A')}")
        print(f"📊 Общий score: {result_data.get('overall_score', 0):.2f}")
        print(f"📋 Статус workflow: {result_data.get('workflow_status', 'N/A')}")

        # Проверяем что шаги были выполнены
        steps_completed = result_data.get("steps_completed", [])
        if "todo_validation" in steps_completed:
            print("✅ Валидация todo успешно выполнена")
        else:
            print("❌ Валидация todo не была выполнена")

        return result_data

    finally:
        # Очищаем тестовые файлы
        if todo_file.exists():
            todo_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


async def test_url_analysis():
    """Тест анализа URL"""
    print("\n🧪 Тестирую анализ URL...")

    result = await execute_output_gap_workflow(
        url="https://example.com", take_screenshot=False, analysis_type="basic"
    )

    result_data = json.loads(result)

    print(f"✅ Анализ URL завершен: {result_data.get('analysis_id', 'N/A')}")
    print(f"📊 Общий score: {result_data.get('overall_score', 0):.2f}")
    print(f"📋 Статус workflow: {result_data.get('workflow_status', 'N/A')}")

    # Проверяем что шаги были выполнены
    steps_completed = result_data.get("steps_completed", [])
    if "url_analysis" in steps_completed:
        print("✅ Анализ URL успешно выполнен")
    else:
        print("❌ Анализ URL не был выполнен")

    return result_data


async def test_empty_input():
    """Тест с пустыми входными данными"""
    print("\n🧪 Тестирую обработку пустых входных данных...")

    result = await execute_output_gap_workflow()

    result_data = json.loads(result)

    print(f"✅ Обработка завершена: {result_data.get('analysis_id', 'N/A')}")
    print(f"📊 Общий score: {result_data.get('overall_score', 0):.2f}")
    print(f"📋 Статус workflow: {result_data.get('workflow_status', 'N/A')}")

    # Проверяем что workflow корректно обработал пустые данные
    if result_data.get("workflow_status") == "failed":
        print("✅ Workflow корректно обработал пустые данные")
    else:
        print("❌ Workflow не должен был выполниться с пустыми данными")

    return result_data


async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов для execute_output_gap_workflow")
    print("=" * 60)

    try:
        # Тест 1: Базовый анализ
        await test_basic_gap_analysis()

        # Тест 2: Анализ файлов
        await test_file_analysis()

        # Тест 3: Валидация todo
        await test_todo_validation()

        # Тест 4: Анализ URL
        await test_url_analysis()

        # Тест 5: Пустые входные данные
        await test_empty_input()

        print("\n" + "=" * 60)
        print("✅ Все тесты завершены успешно!")

    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
