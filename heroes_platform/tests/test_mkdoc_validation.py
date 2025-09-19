#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обновленной функциональности make_mkdoc
с автоматической валидацией через validate_actual_outcome
"""

import asyncio
import sys

# Добавляем путь к workflows
sys.path.append(
    "/Users/ilyakrasinsky/workspace/vscode.projects/heroes-template/heroes-platform/mcp_server/workflows"
)


async def test_mkdoc_validation():
    """Тестирует make_mkdoc с автоматической валидацией"""
    try:
        import os
        import sys

        sys.path.append(
            os.path.join(os.path.dirname(__file__), "..", "heroes_mcp", "workflows")
        )
        from markdown_mkdoc_workflow import MarkdownMkDocWorkflow

        print("🚀 Тестирование make_mkdoc с автоматической валидацией...")

        # Создаем экземпляр workflow
        workflow = MarkdownMkDocWorkflow()

        # Путь к проекту rickai_docs
        project_path = (
            "/Users/ilyakrasinsky/workspace/vscode.projects/heroes-template/rickai_docs"
        )

        print(f"📁 Проект: {project_path}")
        print("🔧 Запуск make_mkdoc...")

        # Вызываем make_mkdoc
        result = await workflow.make_mkdoc(project_path, clean=True)

        print("✅ Результат:")
        print(result)

        # Парсим JSON результат
        import json

        result_data = json.loads(result)

        if "validation_result" in result_data:
            validation = result_data["validation_result"]
            print("\n🔍 Результаты валидации:")
            print(f"   Статус: {validation.get('validation_status', 'N/A')}")
            print(f"   Локальный URL: {validation.get('local_url', 'N/A')}")

            if validation.get("validation_status") == "success":
                print("   ✅ Валидация прошла успешно!")
            elif validation.get("validation_status") == "warning":
                print("   ⚠️ Валидация с предупреждениями")
                print(f"   Сообщение: {validation.get('message', 'N/A')}")
            else:
                print("   ❌ Валидация не удалась")
                print(f"   Ошибка: {validation.get('error', 'N/A')}")
        else:
            print("❌ Результаты валидации не найдены в ответе")

        return result_data

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Запускаем тест
    result = asyncio.run(test_mkdoc_validation())

    if result:
        print("\n🎯 Тест завершен успешно!")
    else:
        print("\n💥 Тест завершился с ошибкой!")
        sys.exit(1)
