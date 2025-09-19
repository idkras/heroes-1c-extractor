#!/usr/bin/env python3

"""
Тест подключения к базе данных 1С с применением патча
"""

import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    # Применяем патч перед импортом
    from patches.onec_dtools.onec_dtools_patch import apply_patch

    apply_patch()

    from onec_dtools.database_reader import DatabaseReader

    print("✅ onec_dtools импортирован с патчем")

    # Пробуем открыть базу данных
    with open("data/raw/1Cv8.1CD", "rb") as f:
        db = DatabaseReader(f)
        print("✅ База данных открыта успешно!")
        print(f"📊 Всего таблиц: {len(db.tables)}")

        # Показываем первые 10 таблиц
        print("\n📋 Первые 10 таблиц:")
        for i, table_name in enumerate(list(db.tables.keys())[:10]):
            table = db.tables[table_name]
            print(f"  {i + 1:2d}. {table_name} ({len(table):,} записей)")

        # Ищем таблицы документов
        document_tables = []
        for table_name in db.tables.keys():
            if table_name.startswith("_DOCUMENT"):
                table = db.tables[table_name]
                if len(table) > 0:
                    document_tables.append((table_name, len(table)))

        # Сортируем по размеру
        document_tables.sort(key=lambda x: x[1], reverse=True)

        print(f"\n📊 Найдено таблиц документов: {len(document_tables)}")
        print("📋 Топ-10 таблиц документов:")
        for i, (table_name, record_count) in enumerate(document_tables[:10]):
            print(f"  {i + 1:2d}. {table_name} ({record_count:,} записей)")

        print("\n✅ Тест завершен успешно!")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
