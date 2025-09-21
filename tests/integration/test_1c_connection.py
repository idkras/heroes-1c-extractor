#!/usr/bin/env python3
"""
Simple test to check 1C database connection.

JTBD:
Как тестировщик, я хочу проверить подключение к 1С базе данных,
чтобы убедиться в доступности данных для тестирования.
"""

import sys
from pathlib import Path

# Добавляем путь к src для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_1c_database_connection():
    """Проверка подключения к 1С базе данных."""
    print("🔍 Проверка подключения к 1С базе данных...")

    # Проверяем существование файла
    cdb_file_path = Path(__file__).parent.parent.parent / "data" / "raw" / "1Cv8.1CD"
    print(f"📁 Путь к файлу: {cdb_file_path}")
    print(f"📊 Файл существует: {cdb_file_path.exists()}")

    if not cdb_file_path.exists():
        print("❌ Файл 1С базы данных не найден!")
        return False

    print(
        f"📏 Размер файла: {cdb_file_path.stat().st_size / (1024 * 1024 * 1024):.2f} GB"
    )

    try:
        # Применяем патч для поддержки новых типов полей 1С
        try:
            from simple_patch import apply_simple_patch

            apply_simple_patch()
            print("✅ Патч для новых типов полей применен")
        except Exception as e:
            print(f"⚠️ Не удалось применить патч: {e}")

        from onec_dtools import DatabaseReader

        print("✅ onec_dtools импортирован успешно")

        with open(cdb_file_path, "rb") as f:
            print("🔌 Подключение к базе данных...")
            db = DatabaseReader(f)
            print("✅ База данных открыта успешно!")

            print(f"📊 Найдено таблиц: {len(db.tables)}")

            # Показываем первые 10 таблиц
            table_names = list(db.tables.keys())[:10]
            print(f"📋 Первые 10 таблиц: {table_names}")

            # Ищем таблицы документов
            document_tables = [
                name for name in db.tables.keys() if name.startswith("_DOCUMENT")
            ]
            print(f"📄 Таблиц документов: {len(document_tables)}")

            if document_tables:
                print(f"📋 Таблицы документов: {document_tables[:5]}...")

                # Проверяем первую таблицу документов
                first_table = document_tables[0]
                table = db.tables[first_table]
                print(f"🎯 Тестируем таблицу: {first_table}")
                print(f"📊 Записей в таблице: {len(table):,}")

                # Пробуем прочитать первую запись
                try:
                    first_row = table[0]
                    print("✅ Первая запись прочитана успешно")

                    if hasattr(first_row, "as_list"):
                        row_list = first_row.as_list(True)
                        print(f"📋 Полей в записи: {len(row_list)}")

                        # Показываем первые 5 полей
                        for i, field in enumerate(row_list[:5]):
                            field_name = getattr(field, "name", f"field_{i}")
                            field_type = type(field).__name__
                            print(f"   {i + 1}. {field_name}: {field_type}")

                except Exception as e:
                    print(f"⚠️ Ошибка при чтении записи: {e}")

            return True

    except ImportError as e:
        print(f"❌ Ошибка импорта onec_dtools: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False


if __name__ == "__main__":
    success = test_1c_database_connection()
    if success:
        print("🎉 Подключение к 1С базе данных успешно!")
    else:
        print("❌ Ошибка подключения к 1С базе данных!")
        sys.exit(1)
