#!/usr/bin/env python3
"""
Пример использования n8n интеграции в Heroes MCP Server

Этот скрипт демонстрирует основные возможности интеграции с n8n.
"""

import json

# Импортируем MCP команды
from heroes_mcp.src.heroes_mcp_server import (
    n8n_activate_workflow,
    n8n_create_workflow,
    n8n_get_executions,
    n8n_health_check,
    n8n_init_integration,
    n8n_list_workflows,
    n8n_trigger_workflow,
)


def main():
    """Основная функция примера"""
    print("🚀 Пример использования n8n интеграции")
    print("=" * 50)

    # 1. Инициализация интеграции
    print("\n1️⃣ Инициализация интеграции с n8n...")
    init_result = n8n_init_integration(
        base_url="http://localhost:5678",
        api_key="your_api_key_here",  # Замените на ваш API ключ
    )

    init_data = json.loads(init_result)
    if "error" in init_data:
        print(f"❌ Ошибка инициализации: {init_data['error']}")
        return

    print(f"✅ Интеграция инициализирована: {init_data['message']}")

    # 2. Проверка состояния n8n сервера
    print("\n2️⃣ Проверка состояния n8n сервера...")
    health_result = n8n_health_check()
    health_data = json.loads(health_result)

    if "error" in health_data:
        print(f"❌ Ошибка проверки состояния: {health_data['error']}")
        return

    print(f"✅ n8n сервер: {health_data['status']}")
    print(f"   Версия: {health_data.get('n8n_version', 'unknown')}")
    print(f"   Время ответа: {health_data.get('response_time', 0):.3f}с")

    # 3. Получение списка workflow
    print("\n3️⃣ Получение списка workflow...")
    workflows_result = n8n_list_workflows(limit=10)
    workflows_data = json.loads(workflows_result)

    if "error" in workflows_data:
        print(f"❌ Ошибка получения workflow: {workflows_data['error']}")
        return

    print(f"✅ Найдено workflow: {workflows_data['total']}")
    for workflow in workflows_data["workflows"][:5]:  # Показываем первые 5
        print(f"   - {workflow['name']} (ID: {workflow['id']})")

    # 4. Создание простого test workflow
    print("\n4️⃣ Создание простого test workflow...")
    test_workflow = {
        "name": "Heroes Test Workflow",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "heroes-test",
                    "responseMode": "responseNode",
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": '{"message": "Hello from Heroes MCP!", "timestamp": "{{ $now }}"}',
                },
                "name": "Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [460, 300],
            },
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Response", "type": "main", "index": 0}]]}
        },
        "active": False,
        "tags": ["heroes", "test"],
    }

    create_result = n8n_create_workflow(json.dumps(test_workflow))
    create_data = json.loads(create_result)

    if "error" in create_data:
        print(f"❌ Ошибка создания workflow: {create_data['error']}")
        return

    workflow_id = create_data["id"]
    print(f"✅ Test workflow создан: {create_data['name']} (ID: {workflow_id})")

    # 5. Активация workflow
    print("\n5️⃣ Активация workflow...")
    activate_result = n8n_activate_workflow(workflow_id)
    activate_data = json.loads(activate_result)

    if "error" in activate_data:
        print(f"❌ Ошибка активации: {activate_data['error']}")
        return

    print(f"✅ Workflow активирован: {activate_data['message']}")

    # 6. Тестирование workflow
    print("\n6️⃣ Тестирование workflow...")
    test_data = {"test": "data", "source": "heroes_mcp_example"}

    trigger_result = n8n_trigger_workflow(workflow_id, json.dumps(test_data))
    trigger_data = json.loads(trigger_result)

    if "error" in trigger_data:
        print(f"❌ Ошибка запуска workflow: {trigger_data['error']}")
        return

    print(f"✅ Workflow запущен: {trigger_data['message']}")
    if trigger_data.get("execution_id"):
        print(f"   Execution ID: {trigger_data['execution_id']}")

    # 7. Получение выполнений
    print("\n7️⃣ Получение списка выполнений...")
    executions_result = n8n_get_executions(workflow_id=workflow_id, limit=5)
    executions_data = json.loads(executions_result)

    if "error" in executions_data:
        print(f"❌ Ошибка получения выполнений: {executions_data['error']}")
        return

    print(f"✅ Выполнений найдено: {executions_data['total']}")
    for execution in executions_data["executions"][:3]:  # Показываем первые 3
        print(
            f"   - {execution.get('id', 'N/A')} ({execution.get('status', 'unknown')})"
        )

    print("\n🎉 Пример завершен успешно!")
    print("\n💡 Дополнительные возможности:")
    print("   - n8n_update_workflow() - обновление workflow")
    print("   - n8n_delete_workflow() - удаление workflow")
    print("   - n8n_deactivate_workflow() - деактивация workflow")
    print("   - n8n_get_execution() - получение деталей выполнения")


if __name__ == "__main__":
    main()
