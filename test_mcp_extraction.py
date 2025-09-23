#!/usr/bin/env python3
"""
Тест извлечения данных цветочного бизнеса через MCP сервер
Согласно плану рефакторинга 1c.refactoring.md

JTBD:
Как тестовый скрипт, я хочу продемонстрировать извлечение критических документов,
чтобы показать работу MCP сервера с данными цветочного бизнеса.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from mcp_client import MCPClient


def test_mcp_extraction() -> dict[str, Any]:
    """
    Тест извлечения данных через MCP сервер

    Returns:
        dict[str, Any]: Результаты извлечения данных
    """
    print("🌸 ТЕСТ ИЗВЛЕЧЕНИЯ ДАННЫХ ЦВЕТОЧНОГО БИЗНЕСА ЧЕРЕЗ MCP СЕРВЕР")
    print("=" * 70)

    # Создаем MCP клиент
    client = MCPClient()

    # Путь к базе данных 1С
    database_path = "data/raw/1Cv8.1CD"

    print(f"🔗 Подключение к базе данных: {database_path}")
    print(f"📊 MCP клиент инициализирован")

    # Результаты извлечения
    results = {}

    # 1. Извлекаем документы _DOCUMENT138 (Поступления цветов)
    print("\n🌸 ИЗВЛЕЧЕНИЕ ДОКУМЕНТОВ _DOCUMENT138 (Поступления цветов)...")
    result_138 = client.extract_1c_documents(
        table_name="_DOCUMENT138",
        database_path=database_path,
        limit=10,  # Ограничиваем для тестирования
    )

    print(f"✅ Результат: {result_138.get('success', False)}")
    print(f"📊 Количество документов: {result_138.get('documents_count', 0)}")
    print(f"💬 Сообщение: {result_138.get('message', 'Нет сообщения')}")

    if result_138.get("success"):
        results["documents_138"] = result_138.get("documents", [])
        print(
            f"📋 Первый документ: {list(results['documents_138'][0].keys()) if results['documents_138'] else 'Нет документов'}"
        )
    else:
        print(f"❌ Ошибка: {result_138.get('error', 'Неизвестная ошибка')}")

    # 2. Извлекаем документы _DOCUMENT137 (Продажи цветов)
    print("\n💰 ИЗВЛЕЧЕНИЕ ДОКУМЕНТОВ _DOCUMENT137 (Продажи цветов)...")
    result_137 = client.extract_1c_documents(
        table_name="_DOCUMENT137",
        database_path=database_path,
        limit=10,  # Ограничиваем для тестирования
    )

    print(f"✅ Результат: {result_137.get('success', False)}")
    print(f"📊 Количество документов: {result_137.get('documents_count', 0)}")
    print(f"💬 Сообщение: {result_137.get('message', 'Нет сообщения')}")

    if result_137.get("success"):
        results["documents_137"] = result_137.get("documents", [])
        print(
            f"📋 Первый документ: {list(results['documents_137'][0].keys()) if results['documents_137'] else 'Нет документов'}"
        )
    else:
        print(f"❌ Ошибка: {result_137.get('error', 'Неизвестная ошибка')}")

    # 3. Извлекаем табличные части _DOCUMENT138_VT3118
    print(
        "\n📊 ИЗВЛЕЧЕНИЕ ТАБЛИЧНЫХ ЧАСТЕЙ _DOCUMENT138_VT3118 (Детали поступлений)..."
    )
    result_vt3118 = client.extract_table_parts(
        table_name="_DOCUMENT138_VT3118",
        database_path=database_path,
        limit=10,  # Ограничиваем для тестирования
    )

    print(f"✅ Результат: {result_vt3118.get('success', False)}")
    print(f"📊 Количество записей: {result_vt3118.get('table_parts_count', 0)}")
    print(f"💬 Сообщение: {result_vt3118.get('message', 'Нет сообщения')}")

    if result_vt3118.get("success"):
        results["table_parts_138"] = result_vt3118.get("table_parts", [])
        print(
            f"📋 Первая запись: {list(results['table_parts_138'][0].keys()) if results['table_parts_138'] else 'Нет записей'}"
        )
    else:
        print(f"❌ Ошибка: {result_vt3118.get('error', 'Неизвестная ошибка')}")

    # 4. Создаем плоскую таблицу
    print("\n🔗 СОЗДАНИЕ ПЛОСКОЙ ТАБЛИЦЫ С МАППИНГОМ...")

    documents_list = []
    table_names = []

    if "documents_138" in results:
        documents_list.append(results["documents_138"])
        table_names.append("_DOCUMENT138")
        print(
            f"✅ Добавлены документы _DOCUMENT138: {len(results['documents_138'])} записей"
        )

    if "documents_137" in results:
        documents_list.append(results["documents_137"])
        table_names.append("_DOCUMENT137")
        print(
            f"✅ Добавлены документы _DOCUMENT137: {len(results['documents_137'])} записей"
        )

    if "table_parts_138" in results:
        documents_list.append(results["table_parts_138"])
        table_names.append("_DOCUMENT138_VT3118")
        print(
            f"✅ Добавлены табличные части _DOCUMENT138_VT3118: {len(results['table_parts_138'])} записей"
        )

    print(f"📊 Всего таблиц для обработки: {len(documents_list)}")
    print(f"📋 Имена таблиц: {table_names}")

    if documents_list:
        flat_table_result = client.create_flat_table(
            documents_list=documents_list, table_names=table_names
        )

        print(
            f"✅ Результат создания плоской таблицы: {flat_table_result.get('success', False)}"
        )
        print(
            f"📊 Общее количество записей: {flat_table_result.get('total_records', 0)}"
        )
        print(f"💬 Сообщение: {flat_table_result.get('message', 'Нет сообщения')}")

        if flat_table_result.get("success"):
            flat_table = flat_table_result.get("flat_table", [])
            print(
                f"📋 Первая запись плоской таблицы: {list(flat_table[0].keys()) if flat_table else 'Нет записей'}"
            )

            # Показываем пример записи
            if flat_table:
                print(f"\n📄 Пример записи:")
                for key, value in list(flat_table[0].items())[:10]:  # Первые 10 полей
                    print(f"  {key}: {value}")

            # 5. Сохраняем в Parquet
            print("\n💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В PARQUET...")
            output_path = "data/results/flower_business_analysis.parquet"

            save_result = client.save_to_parquet(
                data=flat_table, output_path=output_path
            )

            print(f"✅ Результат сохранения: {save_result.get('success', False)}")
            print(f"📁 Путь к файлу: {save_result.get('output_path', 'Не указан')}")
            print(f"📊 Размер файла: {save_result.get('file_size_mb', 0)} MB")
            print(f"📋 Количество записей: {save_result.get('records_count', 0)}")
            print(f"📊 Количество колонок: {save_result.get('columns_count', 0)}")
            print(f"💬 Сообщение: {save_result.get('message', 'Нет сообщения')}")

            if not save_result.get("success"):
                print(
                    f"❌ Ошибка сохранения: {save_result.get('error', 'Неизвестная ошибка')}"
                )
        else:
            print(
                f"❌ Ошибка создания плоской таблицы: {flat_table_result.get('error', 'Неизвестная ошибка')}"
            )
    else:
        print("❌ Нет данных для создания плоской таблицы")

    # 6. Анализ результатов
    print("\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ ИЗВЛЕЧЕНИЯ ДАННЫХ ЦВЕТОЧНОГО БИЗНЕСА")
    print("=" * 70)

    # Статистика по документам
    print("\n🌸 ДОКУМЕНТЫ ПОСТУПЛЕНИЙ (_DOCUMENT138):")
    if result_138.get("success"):
        print(
            f"  ✅ Успешно извлечено: {result_138.get('documents_count', 0)} документов"
        )
        print(f"  📊 Статус: {result_138.get('message', 'Нет сообщения')}")
    else:
        print(f"  ❌ Ошибка: {result_138.get('error', 'Неизвестная ошибка')}")

    print("\n💰 ДОКУМЕНТЫ ПРОДАЖ (_DOCUMENT137):")
    if result_137.get("success"):
        print(
            f"  ✅ Успешно извлечено: {result_137.get('documents_count', 0)} документов"
        )
        print(f"  📊 Статус: {result_137.get('message', 'Нет сообщения')}")
    else:
        print(f"  ❌ Ошибка: {result_137.get('error', 'Неизвестная ошибка')}")

    print("\n📊 ТАБЛИЧНЫЕ ЧАСТИ (_DOCUMENT138_VT3118):")
    if result_vt3118.get("success"):
        print(
            f"  ✅ Успешно извлечено: {result_vt3118.get('table_parts_count', 0)} записей"
        )
        print(f"  📊 Статус: {result_vt3118.get('message', 'Нет сообщения')}")
    else:
        print(f"  ❌ Ошибка: {result_vt3118.get('error', 'Неизвестная ошибка')}")

    # Общая статистика
    total_documents = 0
    if result_138.get("success"):
        total_documents += result_138.get("documents_count", 0)
    if result_137.get("success"):
        total_documents += result_137.get("documents_count", 0)
    if result_vt3118.get("success"):
        total_documents += result_vt3118.get("table_parts_count", 0)

    print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
    print(f"  📊 Всего извлечено записей: {total_documents}")
    print(f"  📋 Количество таблиц: {len(documents_list)}")
    print(
        f"  📁 Результат сохранен в: {output_path if 'output_path' in locals() else 'Не сохранен'}"
    )

    print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Анализ BLOB полей - расшифровка данных о цветах")
    print("2. Создание маппинга полей - понятные названия вместо field__X")
    print("3. Анализ логистики - маршруты поставок и продаж")
    print("4. Создание отчетов - сводные таблицы по цветам и магазинам")

    return results


if __name__ == "__main__":
    try:
        results = test_mcp_extraction()
        print("\n✅ Тест завершен успешно")
    except Exception as e:
        print(f"\n❌ Ошибка выполнения теста: {e}")
        import traceback

        traceback.print_exc()
