#!/usr/bin/env python3
"""
Скрипт для извлечения нескольких документов с применением маппинга
и создания плоской таблицы с реальными данными.
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Добавляем путь к src для импорта модулей
sys.path.append("src")

from extractors.flat_table_extractor import FlatTableExtractor
from processors.database_connector import DatabaseConnector
from extract_all_available_data import get_field_mapping, get_field_mapping_by_index


def extract_documents_with_mapping():
    """
    Извлекает несколько документов, применяет маппинг и создает плоскую таблицу.
    """
    print("🚀 НАЧИНАЕМ ИЗВЛЕЧЕНИЕ ДОКУМЕНТОВ С МАППИНГОМ")
    print("=" * 80)

    # 1. Подключение к базе данных
    print("📊 ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ...")
    db_path = "data/raw/1Cv8.1CD"

    if not os.path.exists(db_path):
        print(f"❌ ОШИБКА: Файл {db_path} не найден!")
        return None

    try:
        connector = DatabaseConnector(db_path)
        connector.connect()
        print("✅ Подключение к базе данных успешно!")
    except Exception as e:
        print(f"❌ ОШИБКА подключения: {e}")
        return None

    # 2. Создание экстрактора с маппингом
    print("\n🔧 СОЗДАНИЕ ЭКСТРАКТОРА С МАППИНГОМ...")
    extractor = FlatTableExtractor(db_path)

    # 3. Извлечение документов
    print("\n📄 ИЗВЛЕЧЕНИЕ ДОКУМЕНТОВ...")
    try:
        # Используем метод extract_flat_table для извлечения всех документов
        results = extractor.extract_flat_table()
        print(f"✅ Извлечено {len(results.get('flat_data', []))} сущностей")
    except Exception as e:
        print(f"❌ ОШИБКА извлечения: {e}")
        return None

    # 4. Создание плоской таблицы
    print("\n📊 СОЗДАНИЕ ПЛОСКОЙ ТАБЛИЦЫ...")
    flat_data = results.get("flat_data", [])

    if not flat_data:
        print("❌ Нет данных для создания таблицы!")
        return None

    # Создаем DataFrame
    df = pd.DataFrame(flat_data)

    # 5. Применяем маппинг полей
    print("\n🗺️ ПРИМЕНЕНИЕ МАППИНГА ПОЛЕЙ...")
    field_mapping = get_field_mapping()
    field_mapping_by_index = get_field_mapping_by_index()

    # Переименовываем поля согласно маппингу
    column_mapping = {}
    for col in df.columns:
        if col.startswith("field__"):
            field_name = col.replace("field__", "")
            if field_name in field_mapping:
                column_mapping[col] = field_mapping[field_name]
            elif field_name in field_mapping_by_index:
                column_mapping[col] = field_mapping_by_index[field_name]

    df_renamed = df.rename(columns=column_mapping)

    # 6. Сохраняем результаты
    print("\n💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ...")

    # JSON файл
    json_path = "data/results/documents_with_mapping.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # Конвертируем datetime объекты в строки для JSON сериализации
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    # Обрабатываем данные для JSON
    processed_flat_data = []
    for record in flat_data:
        processed_record = {}
        for key, value in record.items():
            processed_record[key] = convert_datetime(value)
        processed_flat_data.append(processed_record)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "total_entities": len(flat_data),
                    "total_columns": len(df.columns),
                    "mapped_columns": len(column_mapping),
                    "extraction_date": datetime.now().isoformat(),
                },
                "flat_data": processed_flat_data,
                "column_mapping": column_mapping,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    # Parquet файл - конвертируем datetime в строки
    parquet_path = "data/results/documents_with_mapping.parquet"

    # Конвертируем datetime колонки в строки для Parquet
    df_for_parquet = df_renamed.copy()
    for col in df_for_parquet.columns:
        if df_for_parquet[col].dtype == "object":
            # Проверяем, содержит ли колонка datetime объекты
            if (
                df_for_parquet[col]
                .dropna()
                .apply(lambda x: isinstance(x, datetime))
                .any()
            ):
                df_for_parquet[col] = df_for_parquet[col].apply(
                    lambda x: x.isoformat() if isinstance(x, datetime) else x
                )

    df_for_parquet.to_parquet(parquet_path, index=False)

    print(f"✅ Результаты сохранены:")
    print(f"   - JSON: {json_path}")
    print(f"   - Parquet: {parquet_path}")

    # 7. Выводим пример плоской таблицы
    print("\n📋 ПРИМЕР ПЛОСКОЙ ТАБЛИЦЫ:")
    print("=" * 80)

    # Показываем первые 5 строк с переименованными колонками
    print("🔍 ПЕРВЫЕ 5 СТРОК ПЛОСКОЙ ТАБЛИЦЫ:")
    print(df_renamed.head().to_string())

    print(f"\n📊 СТАТИСТИКА:")
    print(f"   - Всего сущностей: {len(df)}")
    print(f"   - Всего колонок: {len(df.columns)}")
    print(f"   - Переименовано колонок: {len(column_mapping)}")

    # Показываем статистику по колонкам
    print(f"\n📈 СТАТИСТИКА ПО КОЛОНКАМ:")
    for col in df_renamed.columns:
        non_null_count = df_renamed[col].notna().sum()
        null_count = df_renamed[col].isna().sum()
        print(f"   - {col}: {non_null_count} заполнено, {null_count} пустых")

    # Показываем примеры значений для ключевых полей
    print(f"\n🔍 ПРИМЕРЫ ЗНАЧЕНИЙ КЛЮЧЕВЫХ ПОЛЕЙ:")
    key_fields = [
        "entity_type",
        "document_type",
        "created_date",
        "total_amount",
        "is_posted",
    ]

    for field in key_fields:
        if field in df_renamed.columns:
            unique_values = df_renamed[field].dropna().unique()
            print(f"   - {field}: {len(unique_values)} уникальных значений")
            if len(unique_values) <= 10:
                print(f"     Примеры: {list(unique_values)}")
            else:
                print(f"     Примеры: {list(unique_values[:5])}...")

    return df_renamed


def main():
    """Основная функция."""
    print("🎯 ИЗВЛЕЧЕНИЕ ДОКУМЕНТОВ С МАППИНГОМ И ПЛОСКОЙ ТАБЛИЦЕЙ")
    print("=" * 80)

    try:
        df = extract_documents_with_mapping()
        if df is not None:
            print("\n✅ УСПЕШНО! Плоская таблица создана с применением маппинга.")
            print("📁 Результаты сохранены в data/results/")
        else:
            print("\n❌ ОШИБКА! Не удалось создать плоскую таблицу.")
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
