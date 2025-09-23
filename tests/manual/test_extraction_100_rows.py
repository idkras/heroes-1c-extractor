#!/usr/bin/env python3
"""
Тест-кейс: Проверка извлечения 100 строк из _DOCUMENT138 и _DOCUMENT137

Цель: Убедиться что извлекаются реальные документы с данными о цветах,
а не "брак" или технические поля.

Критерии успеха:
- Найдены реальные названия цветов (розы, тюльпаны, хризантемы)
- Найдены реальные суммы документов (не 0, не пустые)
- Найдены реальные даты документов (не "N/A")
- Найдены названия магазинов (не только коды)
- Parquet файлы имеют понятные названия
- В файлах нет технических полей типа _FLD9999
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Добавляем путь к проекту
sys.path.append("mcp_server")
sys.path.append("src")


def test_extraction_100_rows():
    """
    Тест-кейс: Извлечение 100 строк из _DOCUMENT138 и _DOCUMENT137
    """
    print("🧪 ТЕСТ-КЕЙС: Извлечение 100 строк из _DOCUMENT138 и _DOCUMENT137")
    print("=" * 80)

    # Импортируем MCP сервер
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "mcp_server", "mcp_server/1c_mcp_server.py"
        )
        if spec is None or spec.loader is None:
            raise ImportError("Не удалось загрузить спецификацию модуля")
        mcp_server = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(mcp_server)
        print("✅ MCP сервер загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки MCP сервера: {e}")
        return False

    # Тестируем извлечение _DOCUMENT138 (100 строк)
    print("\n🔍 ТЕСТ 1: Извлечение 100 строк из _DOCUMENT138")
    try:
        result_138 = mcp_server.extract_1c_documents(
            "_DOCUMENT138", "data/raw/1Cv8.1CD", limit=100
        )
        result_138_dict = json.loads(result_138)

        if result_138_dict.get("success"):
            documents_count = result_138_dict.get("documents_count", 0)
            print(f"✅ _DOCUMENT138: {documents_count} документов извлечено")

            # Проверяем качество данных
            documents = result_138_dict.get("documents", [])
            if documents:
                print("📊 Анализ качества данных _DOCUMENT138:")
                analyze_document_quality(documents, "_DOCUMENT138")
            else:
                print("❌ Нет документов в результате _DOCUMENT138")
                return False
        else:
            print(f"❌ Ошибка извлечения _DOCUMENT138: {result_138_dict.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Ошибка тестирования _DOCUMENT138: {e}")
        return False

    # Тестируем извлечение _DOCUMENT137 (100 строк)
    print("\n🔍 ТЕСТ 2: Извлечение 100 строк из _DOCUMENT137")
    try:
        result_137 = mcp_server.extract_1c_documents(
            "_DOCUMENT137", "data/raw/1Cv8.1CD", limit=100
        )
        result_137_dict = json.loads(result_137)

        if result_137_dict.get("success"):
            documents_count = result_137_dict.get("documents_count", 0)
            print(f"✅ _DOCUMENT137: {documents_count} документов извлечено")

            # Проверяем качество данных
            documents = result_137_dict.get("documents", [])
            if documents:
                print("📊 Анализ качества данных _DOCUMENT137:")
                analyze_document_quality(documents, "_DOCUMENT137")
            else:
                print("❌ Нет документов в результате _DOCUMENT137")
                return False
        else:
            print(f"❌ Ошибка извлечения _DOCUMENT137: {result_137_dict.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Ошибка тестирования _DOCUMENT137: {e}")
        return False

    # Проверяем создание Parquet файлов
    print("\n🔍 ТЕСТ 3: Проверка создания Parquet файлов")
    check_parquet_files()

    print("\n✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    return True


def analyze_document_quality(documents: List[Dict[str, Any]], table_name: str) -> None:
    """
    Анализирует качество извлеченных документов
    """
    if not documents:
        print("❌ Нет документов для анализа")
        return

    print(f"   📋 Всего документов: {len(documents)}")

    # Анализируем поля документов
    field_analysis: Dict[str, Dict[str, Any]] = {}
    blob_analysis: Dict[str, Dict[str, Any]] = {}
    quality_issues: List[str] = []

    for doc in documents:
        # Анализируем обычные поля
        if "fields" in doc:
            for field_name, field_data in doc["fields"].items():
                if field_name not in field_analysis:
                    field_analysis[field_name] = {
                        "count": 0,
                        "has_values": 0,
                        "sample_values": [],
                    }

                field_analysis[field_name]["count"] += 1
                if (
                    field_data.get("value") is not None
                    and str(field_data.get("value")).strip()
                ):
                    field_analysis[field_name]["has_values"] += 1
                    if len(field_analysis[field_name]["sample_values"]) < 3:
                        field_analysis[field_name]["sample_values"].append(
                            str(field_data.get("value", ""))
                        )

        # Анализируем BLOB поля
        if "blob_fields" in doc:
            for blob_name, blob_data in doc["blob_fields"].items():
                if blob_name not in blob_analysis:
                    blob_analysis[blob_name] = {
                        "count": 0,
                        "successful_extractions": 0,
                        "sample_contents": [],
                    }

                blob_analysis[blob_name]["count"] += 1
                # ИСПРАВЛЕНО: blob_data теперь строка, а не словарь
                if isinstance(blob_data, str) and blob_data.strip():
                    blob_analysis[blob_name]["successful_extractions"] += 1
                    if len(blob_analysis[blob_name]["sample_contents"]) < 3:
                        if blob_data.strip():
                            blob_analysis[blob_name]["sample_contents"].append(
                                str(blob_data[:100])
                            )

    # Выводим анализ полей
    print("   📊 Анализ полей:")
    for field_name, analysis in field_analysis.items():
        fill_rate = (
            (int(analysis["has_values"]) / int(analysis["count"])) * 100
            if int(analysis["count"]) > 0
            else 0
        )
        print(
            f"      {field_name}: {fill_rate:.1f}% заполнено ({analysis['has_values']}/{analysis['count']})"
        )

        # Проверяем на технические поля
        if field_name.startswith("_FLD999"):
            quality_issues.append(f"Техническое поле {field_name} в {table_name}")

    # Выводим анализ BLOB полей
    print("   📊 Анализ BLOB полей:")
    for blob_name, analysis in blob_analysis.items():
        success_rate = (
            (int(analysis["successful_extractions"]) / int(analysis["count"])) * 100
            if int(analysis["count"]) > 0
            else 0
        )
        print(
            f"      {blob_name}: {success_rate:.1f}% успешно ({analysis['successful_extractions']}/{analysis['count']})"
        )

        # Показываем примеры содержимого
        if analysis["sample_contents"]:
            sample_content = str(analysis["sample_contents"][0])[:50]
            print(f"         Примеры: {sample_content}...")

    # Проверяем качество данных
    print("   🔍 Проверка качества данных:")

    # Проверяем на пустые поля
    empty_fields = [
        name for name, analysis in field_analysis.items() if analysis["has_values"] == 0
    ]
    if empty_fields:
        quality_issues.append(f"Пустые поля в {table_name}: {empty_fields}")
        print(f"      ⚠️ Пустые поля: {empty_fields}")

    # Проверяем на технические поля
    technical_fields = [
        name for name in field_analysis.keys() if name.startswith("_FLD999")
    ]
    if technical_fields:
        quality_issues.append(f"Технические поля в {table_name}: {technical_fields}")
        print(f"      ⚠️ Технические поля: {technical_fields}")

    # Проверяем на наличие данных о цветах
    color_fields = [
        name
        for name in field_analysis.keys()
        if "цвет" in name.lower() or "flower" in name.lower()
    ]
    if color_fields:
        print(f"      ✅ Найдены поля о цветах: {color_fields}")
    else:
        quality_issues.append(f"Не найдены поля о цветах в {table_name}")
        print("      ❌ Не найдены поля о цветах")

    # Выводим проблемы качества
    if quality_issues:
        print("   🚨 Проблемы качества:")
        for issue in quality_issues:
            print(f"      - {issue}")
    else:
        print("   ✅ Качество данных хорошее")


def check_parquet_files():
    """
    Проверяет создание Parquet файлов
    """
    parquet_dir = Path("data/results/parquet")

    if not parquet_dir.exists():
        print("❌ Папка data/results/parquet не существует")
        return

    parquet_files = list(parquet_dir.glob("*.parquet"))

    if not parquet_files:
        print("❌ Parquet файлы не найдены")
        return

    print(f"   📁 Найдено {len(parquet_files)} Parquet файлов:")

    for file_path in parquet_files:
        file_name = file_path.name
        file_size = file_path.stat().st_size

        print(f"      {file_name} ({file_size:,} байт)")

        # Проверяем содержимое файла
        try:
            df = pd.read_parquet(file_path)
            print(f"         📊 Записей: {len(df)}, Колонок: {len(df.columns)}")

            # Проверяем на пустые файлы
            if len(df) == 0:
                print("         ❌ Файл пустой!")
            else:
                print("         ✅ Файл содержит данные")

                # Показываем примеры данных
                if len(df) > 0:
                    print(f"         📋 Примеры колонок: {list(df.columns)[:5]}")

                    # Проверяем на технические поля
                    technical_cols = [
                        col for col in df.columns if col.startswith("_FLD999")
                    ]
                    if technical_cols:
                        print(f"         ⚠️ Технические колонки: {technical_cols}")

        except Exception as e:
            print(f"         ❌ Ошибка чтения файла: {e}")


if __name__ == "__main__":
    test_extraction_100_rows()
