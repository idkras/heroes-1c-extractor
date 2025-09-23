#!/usr/bin/env python3
"""
LEGACY: Скрипт для извлечения ВСЕХ данных из критических таблиц через MCP сервер
БЕЗ ФИЛЬТРАЦИИ И ЛИМИТОВ

⚠️ ВНИМАНИЕ: Этот файл помечен как LEGACY
Используйте новые MCP команды вместо этого скрипта
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Optional

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Импортируем функции напрямую
import importlib.util

spec = importlib.util.spec_from_file_location(
    "mcp_server", "mcp_server/1c_mcp_server.py"
)
if spec and spec.loader:
    mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_module)
else:
    raise ImportError("Не удалось загрузить модуль mcp_server")

extract_1c_documents = mcp_module.extract_1c_documents
save_to_parquet = mcp_module.save_to_parquet


def setup_logging() -> None:
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def extract_table_data(table_name: str, database_path: str) -> dict:
    """
    Извлекает ВСЕ данные из указанной таблицы через MCP сервер

    Args:
        table_name: Имя таблицы для извлечения
        database_path: Путь к базе данных 1С

    Returns:
        Словарь с результатами извлечения
    """
    print(f"🔍 Извлечение ВСЕХ данных из {table_name}...")

    try:
        # Извлекаем ВСЕ данные БЕЗ ЛИМИТОВ
        result = extract_1c_documents(
            table_name=table_name,
            database_path=database_path,
            limit=None,  # ВСЕ ДАННЫЕ!
        )

        # Парсим результат
        data = json.loads(result)

        if data.get("success", False):
            print(f"✅ {table_name}: {data.get('documents_count', 0)} записей")
            return {
                "success": True,
                "table_name": table_name,
                "records_count": data.get("documents_count", 0),
                "data": data.get("documents", []),
                "raw_result": data,
            }
        else:
            print(f"❌ {table_name}: {data.get('error', 'Unknown error')}")
            return {
                "success": False,
                "table_name": table_name,
                "error": data.get("error", "Unknown error"),
                "raw_result": data,
            }

    except Exception as e:
        print(f"❌ Ошибка извлечения {table_name}: {e}")
        return {"success": False, "table_name": table_name, "error": str(e)}


def save_table_to_parquet(
    table_data: dict, output_dir: str = "data/results/parquet"
) -> str:
    """
    Сохраняет данные таблицы в Parquet файл

    Args:
        table_data: Данные таблицы
        output_dir: Директория для сохранения

    Returns:
        Путь к сохраненному файлу
    """
    if not table_data.get("success", False):
        print(
            f"❌ Не удалось сохранить {table_data.get('table_name')}: {table_data.get('error')}"
        )
        return "error"

    try:
        # Создаем директорию
        os.makedirs(output_dir, exist_ok=True)

        # Формируем имя файла
        table_name = table_data.get("table_name", "unknown")
        safe_name = table_name.lower().replace("_", "_")
        parquet_file = os.path.join(output_dir, f"{safe_name}_all_data.parquet")

        # Сохраняем через MCP сервер
        result = save_to_parquet(
            data=table_data.get("data", []), output_path=parquet_file
        )

        # Парсим результат
        save_result = json.loads(result)

        if save_result.get("success", False):
            print(f"💾 {table_name} → {parquet_file}")
            print(f"   Записей: {save_result.get('records_saved', 0)}")
            print(f"   Размер: {save_result.get('file_size_mb', 0)} MB")
            return parquet_file
        else:
            print(f"❌ Ошибка сохранения {table_name}: {save_result.get('error')}")
            return "error"

    except Exception as e:
        print(f"❌ Ошибка сохранения {table_name}: {e}")
        return "error"


def main() -> None:
    """Главная функция"""
    print("🚀 ИЗВЛЕЧЕНИЕ ВСЕХ ДАННЫХ ИЗ КРИТИЧЕСКИХ ТАБЛИЦ")
    print("=" * 60)

    setup_logging()

    # Путь к базе данных
    database_path = "data/raw/1Cv8.1CD"

    if not os.path.exists(database_path):
        print(f"❌ База данных не найдена: {database_path}")
        return

    # Критические таблицы для извлечения
    critical_tables = [
        "_DOCUMENT138",  # Поступление товаров (861K записей)
        "_DOCUMENT137",  # Розничные продажи (227K записей)
        "_DOCUMENT138_VT3118",  # Табличные части поступлений
    ]

    print(f"📊 Извлекаем данные из {len(critical_tables)} критических таблиц:")
    for table in critical_tables:
        print(f"   • {table}")

    # Извлекаем данные из каждой таблицы
    results = []

    for i, table_name in enumerate(critical_tables, 1):
        print(f"\n{i}️⃣ Извлечение {table_name}...")

        # Извлекаем данные
        table_data = extract_table_data(table_name, database_path)
        results.append(table_data)

        # Сохраняем в Parquet
        if table_data.get("success", False):
            parquet_file = save_table_to_parquet(table_data)
            if parquet_file:
                table_data["parquet_file"] = parquet_file

    # Итоговая статистика
    successful = sum(1 for r in results if r.get("success", False))
    total_records = sum(r.get("records_count", 0) for r in results)

    print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"   Успешно извлечено: {successful}/{len(critical_tables)} таблиц")
    print(f"   Всего записей: {total_records:,}")
    print(f"   Parquet файлы: data/results/parquet/")

    # Детали по каждой таблице
    for result in results:
        table_name = result.get("table_name", "Unknown")
        if result.get("success", False):
            records = result.get("records_count", 0)
            parquet = result.get("parquet_file", "Не сохранен")
            print(f"   ✅ {table_name}: {records:,} записей → {parquet}")
        else:
            error = result.get("error", "Unknown error")
            print(f"   ❌ {table_name}: {error}")

    return successful > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
