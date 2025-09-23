#!/usr/bin/env python3
"""
Тестирование ReferenceExtractor на реальных данных с лимитом 100 строк
Согласно @research.mdc - быстрый тест для выявления проблем
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append("src")


def test_reference_extractor_sample():
    """Тестирует ReferenceExtractor на семпле данных"""

    print("🧪 ТЕСТ REFERENCEEXTRACTOR НА РЕАЛЬНЫХ ДАННЫХ (СЕМПЛ 100 СТРОК)")
    print("=" * 70)

    try:
        # Импортируем необходимые модули
        from extractors.reference_extractor import ReferenceExtractor

        print("✅ ReferenceExtractor импортирован")

        # Проверяем наличие файла базы данных
        db_path = "data/raw/1Cv8.1CD"
        if not os.path.exists(db_path):
            print(f"❌ Файл базы данных не найден: {db_path}")
            return False

        print(f"✅ Файл базы данных найден: {db_path}")

        # Создаем ReferenceExtractor
        extractor = ReferenceExtractor(db_path)
        print("✅ ReferenceExtractor создан")

        # Получаем список справочников
        print("🔍 Получаем список справочников...")
        reference_tables = extractor.get_reference_tables()
        print(f"📚 Найдено справочников: {len(reference_tables)}")

        if len(reference_tables) == 0:
            print("❌ Справочники не найдены")
            return False

        # ИСПРАВЛЕНО: Выбираем справочники с данными для тестирования
        test_tables = []
        print("🔍 Ищем справочники с данными...")

        # Подключаемся к БД перед проверкой размеров
        if not extractor.db_connector.connect():
            print("❌ Не удалось подключиться к базе данных")
            return False

        for table_name, table_info in reference_tables.items():
            try:
                # Проверяем размер таблицы
                table = extractor.db_connector.get_table(table_name)
                size = len(table) if hasattr(table, "__len__") else 0
                if size > 0:
                    test_tables.append(table_name)
                    print(f"   ✅ {table_name}: {size} строк")
                    if len(test_tables) >= 3:  # Ограничиваем до 3 таблиц
                        break
            except Exception as e:
                print(f"   ❌ Ошибка проверки {table_name}: {e}")

        if not test_tables:
            print("❌ Не найдено справочников с данными для тестирования")
            return False

        print(f"🧪 Тестируем на {len(test_tables)} справочниках с данными:")
        for table_name in test_tables:
            print(f"   - {table_name}")

        # Тестируем извлечение с лимитом 100 строк
        results = {}
        for table_name in test_tables:
            print(f"\n📋 Тестируем {table_name}...")

            try:
                # Извлекаем с лимитом 100 строк
                sample_data = extractor.extract(table_name, limit=100)

                if sample_data:
                    print(f"   ✅ Успешно извлечено {len(sample_data)} записей")

                    # Анализируем структуру данных
                    if len(sample_data) > 0:
                        first_record = sample_data[0]
                        print(f"   📊 Поля в первой записи: {len(first_record)}")
                        print(f"   🔍 Примеры полей: {list(first_record.keys())[:5]}")

                        # Проверяем типы данных
                        data_types = {}
                        for key, value in first_record.items():
                            if isinstance(value, dict):
                                data_types[key] = type(value).__name__
                            else:
                                data_types[key] = type(value).__name__

                        print(
                            f"   📈 Типы данных: {dict(list(data_types.items())[:3])}"
                        )

                        results[table_name] = {
                            "success": True,
                            "record_count": len(sample_data),
                            "sample_data": sample_data[
                                :2
                            ],  # Первые 2 записи для анализа
                            "data_types": data_types,
                        }
                    else:
                        print(f"   ⚠️ Нет данных в записях")
                        results[table_name] = {
                            "success": False,
                            "error": "Нет данных в записях",
                        }
                else:
                    print(f"   ❌ Не удалось извлечь данные")
                    results[table_name] = {
                        "success": False,
                        "error": "Не удалось извлечь данные",
                    }

            except Exception as e:
                print(f"   ❌ Ошибка при извлечении {table_name}: {e}")
                results[table_name] = {"success": False, "error": str(e)}

        # Анализируем результаты
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        successful = sum(1 for r in results.values() if r.get("success", False))
        total = len(results)
        print(f"   ✅ Успешных: {successful}/{total}")
        print(f"   📈 Процент успеха: {(successful/total*100):.1f}%")

        # Сохраняем результаты для анализа
        output_file = "test_reference_sample_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "test_timestamp": datetime.now().isoformat(),
                    "test_tables": test_tables,
                    "results": results,
                    "summary": {
                        "total_tables": total,
                        "successful": successful,
                        "success_rate": (successful / total * 100) if total > 0 else 0,
                    },
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"💾 Результаты сохранены: {output_file}")

        # Выводим проблемы
        print(f"\n⚠️ ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ:")
        for table_name, result in results.items():
            if not result.get("success", False):
                print(
                    f"   ❌ {table_name}: {result.get('error', 'Неизвестная ошибка')}"
                )

        return successful > 0

    except Exception as e:
        print(f"❌ Критическая ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТА REFERENCEEXTRACTOR НА РЕАЛЬНЫХ ДАННЫХ")
    print("=" * 70)

    success = test_reference_extractor_sample()

    if success:
        print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
    else:
        print("❌ ТЕСТ ПРОВАЛЕН")
        exit(1)
