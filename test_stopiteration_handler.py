#!/usr/bin/env python3
"""
Тест StopIterationHandler для проверки решения проблем с итерацией.

JTBD:
Как тест StopIterationHandler, я хочу проверить работу обработчика ошибок итерации,
чтобы убедиться в решении проблемы с 47% недоступных справочников.
"""

import os
import sys
import logging
from typing import Any

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_stopiteration_handler():
    """Тестирует StopIterationHandler на реальных данных"""

    print("🧪 ТЕСТ STOPITERATIONHANDLER")
    print("=" * 50)

    try:
        # Импортируем необходимые модули
        from processors.stopiteration_handler import (
            StopIterationHandler,
            IterationStrategy,
        )
        from processors.database_connector import DatabaseConnector
        from extractors.reference_extractor import ReferenceExtractor

        print("✅ Модули импортированы успешно")

        # Проверяем наличие файла базы данных
        db_path = "data/raw/1Cv8.1CD"
        if not os.path.exists(db_path):
            print(f"❌ Файл базы данных не найден: {db_path}")
            return False

        print(f"✅ Файл базы данных найден: {db_path}")

        # Создаем StopIterationHandler
        handler = StopIterationHandler()
        print("✅ StopIterationHandler создан")

        # Создаем подключение к базе данных
        db_connector = DatabaseConnector(db_path)
        if not db_connector.connect():
            print("❌ Не удалось подключиться к базе данных")
            return False

        print("✅ Подключение к базе данных установлено")

        # Получаем список таблиц
        tables = db_connector.get_tables()
        print(f"📊 Найдено таблиц: {len(tables)}")

        # Ищем справочники
        reference_tables = []
        for table_name in tables.keys():
            if table_name.startswith("_REFERENCE"):
                table = tables[table_name]
                if hasattr(table, "__len__") and len(table) > 0:
                    reference_tables.append((table_name, len(table)))

        print(f"📚 Найдено справочников: {len(reference_tables)}")

        # Сортируем по размеру
        reference_tables.sort(key=lambda x: x[1], reverse=True)

        # Тестируем на топ-5 справочниках
        test_tables = reference_tables[:5]
        print(f"🧪 Тестируем на {len(test_tables)} справочниках:")

        success_count = 0
        total_processed = 0

        for table_name, table_size in test_tables:
            print(f"\n📋 Тестируем {table_name} ({table_size:,} записей)")

            try:
                # Получаем таблицу
                table = db_connector.get_table(table_name)
                if not table:
                    print(f"❌ Таблица {table_name} недоступна")
                    continue

                # Анализируем таблицу
                analysis = handler.analyze_stopiteration_causes(table, table_name)
                print(
                    f"   📊 Анализ: размер={analysis['table_size']}, BLOB={analysis['has_blob_fields']}"
                )
                print(f"   ⚠️ Проблемы: {analysis['iteration_problems']}")
                print(f"   💡 Рекомендации: {analysis['recommendations']}")

                # Тестируем итерацию
                result = handler.handle_table_iteration(
                    table, table_name, limit=100, include_blobs=True
                )

                if result.success:
                    print(f"   ✅ Успешно извлечено {result.total_processed} записей")
                    print(f"   🔧 Стратегия: {result.strategy_used.value}")
                    print(f"   ❌ Ошибок: {result.failed_count}")
                    print(f"   🔄 Попыток восстановления: {result.recovery_attempts}")
                    success_count += 1
                    total_processed += result.total_processed
                else:
                    print(f"   ❌ Не удалось извлечь данные")
                    print(f"   📝 Ошибки: {result.errors}")

            except Exception as e:
                print(f"   ❌ Ошибка тестирования {table_name}: {e}")
                continue

        # Результаты тестирования
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"   ✅ Успешных справочников: {success_count}/{len(test_tables)}")
        print(
            f"   📈 Общий процент успеха: {(success_count/len(test_tables)*100):.1f}%"
        )
        print(f"   📊 Всего обработано записей: {total_processed:,}")

        if success_count > 0:
            print("✅ StopIterationHandler работает корректно!")
            return True
        else:
            print("❌ StopIterationHandler не смог обработать ни одного справочника")
            return False

    except Exception as e:
        print(f"❌ Критическая ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_reference_extractor_with_handler():
    """Тестирует ReferenceExtractor с StopIterationHandler"""

    print("\n🧪 ТЕСТ REFERENCEEXTRACTOR С STOPITERATIONHANDLER")
    print("=" * 60)

    try:
        from extractors.reference_extractor import ReferenceExtractor

        # Создаем ReferenceExtractor
        db_path = "data/raw/1Cv8.1CD"
        extractor = ReferenceExtractor(db_path)

        print("✅ ReferenceExtractor создан")

        # Проверяем наличие StopIterationHandler
        if (
            hasattr(extractor, "stopiteration_handler")
            and extractor.stopiteration_handler is not None
        ):
            print("✅ StopIterationHandler интегрирован в ReferenceExtractor")
        else:
            print("⚠️ StopIterationHandler не интегрирован в ReferenceExtractor")

        # Тестируем извлечение справочников
        print("🔄 Тестируем извлечение справочников...")

        # Получаем список справочников
        reference_tables = extractor.get_reference_tables()
        print(f"📚 Найдено справочников: {len(reference_tables)}")

        if len(reference_tables) > 0:
            # Тестируем извлечение первого справочника
            first_table = list(reference_tables.keys())[0]
            print(f"🧪 Тестируем извлечение {first_table}...")

            try:
                result = extractor._extract_single_reference(
                    first_table, reference_tables[first_table]
                )

                if result:
                    print(f"✅ Справочник {first_table} извлечен успешно")
                    print(f"   📊 Тип: {result.get('type', 'Неизвестно')}")
                    print(f"   📝 JTBD: {result.get('jtbd_scenario', 'Не определено')}")
                    print(
                        f"   📈 Размер: {result.get('table_info', {}).get('size', 0):,} записей"
                    )
                    return True
                else:
                    print(f"❌ Не удалось извлечь справочник {first_table}")
                    return False

            except Exception as e:
                print(f"❌ Ошибка извлечения {first_table}: {e}")
                return False
        else:
            print("⚠️ Справочники не найдены")
            return False

    except Exception as e:
        print(f"❌ Критическая ошибка тестирования ReferenceExtractor: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТОВ STOPITERATIONHANDLER")
    print("=" * 50)

    # Тест 1: StopIterationHandler
    test1_success = test_stopiteration_handler()

    # Тест 2: ReferenceExtractor с StopIterationHandler
    test2_success = test_reference_extractor_with_handler()

    # Итоговые результаты
    print(f"\n🎯 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(
        f"   StopIterationHandler: {'✅ ПРОЙДЕН' if test1_success else '❌ ПРОВАЛЕН'}"
    )
    print(f"   ReferenceExtractor: {'✅ ПРОЙДЕН' if test2_success else '❌ ПРОВАЛЕН'}")

    if test1_success and test2_success:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! StopIterationHandler готов к использованию")
        exit(0)
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        exit(1)
