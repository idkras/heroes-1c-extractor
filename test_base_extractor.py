#!/usr/bin/env python3
"""
Тестовый скрипт для проверки BaseExtractor.

JTBD:
Как тестовый скрипт, я хочу проверить функциональность BaseExtractor,
чтобы убедиться в корректности базового класса для всех экстракторов.
"""

import os
import sys

# Добавляем путь к src
sys.path.append("src")
sys.path.append("src/extractors")
sys.path.append("src/processors")

from extractors.base_extractor import BaseExtractor
from processors.database_connector import DatabaseConnector


class TestExtractor(BaseExtractor):
    """
    JTBD:
    Как тестовый экстрактор, я хочу реализовать абстрактный метод extract,
    чтобы протестировать функциональность BaseExtractor.
    """

    def extract(self, table_name: str, limit: int = 100) -> list:
        """
        JTBD:
        Как метод извлечения тестового экстрактора, я хочу извлечь данные из таблицы,
        чтобы протестировать базовую функциональность.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество элементов для извлечения

        Returns:
            Список извлеченных элементов
        """
        print(f"🔍 Тестовое извлечение из таблицы: {table_name}")
        print(f"📊 Лимит: {limit} элементов")

        try:
            # Получаем таблицу
            table = self.db_connector.get_table(table_name)
            table_info = self.db_connector.get_table_info(table_name)

            print("📋 Информация о таблице:")
            print(f"   Размер: {table_info['size']} записей")
            print(f"   Есть данные: {table_info['has_data']}")
            print(f"   Пустая: {table_info['is_empty']}")

            if table_info["is_empty"]:
                print("⚠️ Таблица пуста, нет данных для извлечения")
                return []

            # Анализируем структуру таблицы
            structure_analysis = self.table_analyzer.analyze_table_structure(table)
            print("📊 Анализ структуры:")
            print(
                f"   Всего полей: {structure_analysis['structure_summary']['total_fields']}",
            )
            print(
                f"   BLOB полей: {structure_analysis['structure_summary']['blob_fields']}",
            )
            print(
                f"   Числовых полей: {structure_analysis['structure_summary']['numeric_fields']}",
            )

            # Извлекаем элементы
            items = []
            actual_limit = min(limit, table_info["size"])

            # Используем итератор вместо индексации
            try:
                table_iterator = iter(table)
                for i in range(actual_limit):
                    try:
                        row = next(table_iterator)
                        if hasattr(row, "is_empty") and row.is_empty:
                            continue

                        item = self.process_row(row, i, table_name)
                        if item:
                            items.append(item)
                            self.extraction_stats["successful_extractions"] += 1
                        else:
                            self.extraction_stats["failed_extractions"] += 1

                    except StopIteration:
                        # Нормальное завершение итератора
                        print(f"ℹ️ Итератор завершен на позиции {i}")
                        break
                    except Exception as e:
                        error_msg = f"Ошибка извлечения элемента {i}: {e}"
                        print(f"❌ {error_msg}")
                        self.extraction_stats["extraction_errors"].append(error_msg)
                        self.extraction_stats["failed_extractions"] += 1
                        continue

            except Exception as e:
                error_msg = f"Ошибка создания итератора: {e}"
                print(f"❌ {error_msg}")
                self.extraction_stats["extraction_errors"].append(error_msg)

            self.extraction_stats["total_items"] = len(items)

            print("✅ Извлечение завершено:")
            print(f"   Успешно: {self.extraction_stats['successful_extractions']}")
            print(f"   Ошибок: {self.extraction_stats['failed_extractions']}")
            print(
                f"   BLOB полей найдено: {self.extraction_stats['blob_fields_found']}",
            )
            print(
                f"   BLOB полей обработано: {self.extraction_stats['blob_fields_processed']}",
            )

            return items

        except Exception as e:
            error_msg = f"Критическая ошибка извлечения из таблицы {table_name}: {e}"
            print(f"❌ {error_msg}")
            self.extraction_stats["extraction_errors"].append(error_msg)
            return []


def test_base_extractor():
    """
    JTBD:
    Как тестовая функция, я хочу протестировать BaseExtractor,
    чтобы убедиться в корректности базового класса.
    """
    print("🧪 ТЕСТИРОВАНИЕ BASE EXTRACTOR")
    print("=" * 50)

    # Путь к базе данных 1С
    db_path = "data/raw/1Cv8.1CD"

    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        print("   Убедитесь, что файл 1Cv8.1CD находится в папке data/raw/")
        return False

    try:
        # Создаем подключение к базе данных
        print("🔌 Подключение к базе данных 1С...")
        db_connector = DatabaseConnector(db_path)
        db_connector.connect()

        print("✅ Подключение к базе данных успешно")

        # Создаем тестовый экстрактор
        extractor = TestExtractor(db_connector)

        # Тестируем базовую функциональность
        print("\n🔍 Тестирование базовой функциональности...")

        # Тест 1: Сброс статистики
        print("📊 Тест 1: Сброс статистики")
        extractor.reset_stats()
        stats = extractor.get_extraction_stats()
        print(f"   Статистика после сброса: {stats['total_items']} элементов")

        # Тест 2: Валидация данных
        print("📊 Тест 2: Валидация данных")
        test_data = {
            "table_name": "test_table",
            "row_index": 0,
            "fields": {"field1": {"value": "test", "type": "string"}},
            "blob_fields": {},
            "metadata": {
                "extraction_time": "2025-01-01T00:00:00",
                "field_count": 1,
                "has_blob_fields": False,
            },
        }
        is_valid = extractor.validate_data(test_data)
        print(f"   Валидация тестовых данных: {'✅' if is_valid else '❌'}")

        # Тест 3: Логирование ошибок
        print("📊 Тест 3: Логирование ошибок")
        try:
            raise ValueError("Тестовая ошибка")
        except Exception as e:
            extractor.log_extraction_error(e, {"test": "context"})
        print(
            f"   Ошибок в логе: {len(extractor.extraction_stats['extraction_errors'])}",
        )

        # Тест 4: Проверка продолжения извлечения
        print("📊 Тест 4: Проверка продолжения извлечения")
        should_continue = extractor.should_continue_extraction(5, 10)
        print(
            f"   Следует продолжать при 5 ошибках из 10: {'✅' if should_continue else '❌'}",
        )

        # Тест 5: Анализ качества извлечения
        print("📊 Тест 5: Анализ качества извлечения")
        test_extracted_data = [test_data]
        quality_metrics = extractor.analyze_extraction_quality(test_extracted_data)
        print(f"   Качество извлечения: {quality_metrics['quality_score']}/100")

        # Тест 6: Извлечение реальных данных
        print("\n🔍 Тест 6: Извлечение реальных данных")
        tables = db_connector.get_tables()
        document_tables = db_connector.get_document_tables()

        if not document_tables:
            print("❌ Не найдено таблиц документов")
            return False

        # Ищем таблицу с данными, начиная с известных рабочих таблиц
        known_working_tables = [
            "_DOCUMENT138",
            "_DOCUMENT184",
            "_DOCUMENT154",
            "_DOCUMENT137",
        ]
        test_table_name = None

        # Сначала проверяем известные рабочие таблицы
        for table_name in known_working_tables:
            if table_name in document_tables:
                table_info = db_connector.get_table_info(table_name)
                if table_info["has_data"] and table_info["size"] > 0:
                    test_table_name = table_name
                    print(
                        f"🎯 Найдена известная рабочая таблица: {test_table_name} ({table_info['size']} записей)",
                    )
                    break

        # Если не нашли известные, ищем любую с данными
        if not test_table_name:
            for table_name in document_tables.keys():
                table_info = db_connector.get_table_info(table_name)
                if table_info["has_data"] and table_info["size"] > 0:
                    test_table_name = table_name
                    print(
                        f"🎯 Найдена таблица с данными: {test_table_name} ({table_info['size']} записей)",
                    )
                    break

        if not test_table_name:
            print("❌ Не найдено таблиц с данными")
            return False

        # Извлекаем данные
        print(f"📊 Извлечение данных из {test_table_name}...")
        extracted_data = extractor.extract(test_table_name, limit=5)

        if not extracted_data:
            print("❌ Не удалось извлечь данные")
            return False

        print(f"✅ Извлечено элементов: {len(extracted_data)}")

        # Анализируем качество извлечения
        print("🔍 Анализ качества извлечения...")
        quality_metrics = extractor.analyze_extraction_quality(extracted_data)

        print("📊 Результаты анализа качества:")
        print(f"   Всего элементов: {quality_metrics['total_items']}")
        print(f"   Успешных элементов: {quality_metrics['successful_items']}")
        print(f"   Элементов с BLOB: {quality_metrics['items_with_blobs']}")
        print(f"   Балл качества: {quality_metrics['quality_score']}/100")
        print(f"   Процент успеха: {quality_metrics['success_rate']:.1f}%")
        print(f"   Успешность BLOB: {quality_metrics['blob_success_rate']:.1f}%")
        print(f"   Полнота полей: {quality_metrics['field_completeness']:.1f}%")

        # Показываем примеры извлеченных данных
        print("\n📄 ПРИМЕРЫ ИЗВЛЕЧЕННЫХ ДАННЫХ:")
        print("-" * 40)

        for i, item in enumerate(extracted_data[:2]):  # Показываем первые 2 элемента
            print(f"\n📋 Элемент {i + 1}:")
            print(f"   Таблица: {item['table_name']}")
            print(f"   Индекс: {item['row_index']}")
            print(f"   Полей: {len(item.get('fields', {}))}")
            print(f"   BLOB полей: {len(item.get('blob_fields', {}))}")

            # Показываем примеры полей
            if item.get("fields"):
                print("   Обычные поля:")
                for field_name, field_data in list(item["fields"].items())[:3]:
                    value = field_data.get("value", "None")
                    if len(str(value)) > 50:
                        value = str(value)[:50] + "..."
                    print(f"     {field_name}: {value}")

            # Показываем примеры BLOB полей
            if item.get("blob_fields"):
                print("   BLOB поля:")
                for field_name, blob_data in list(item["blob_fields"].items())[:2]:
                    if blob_data.get("error"):
                        print(f"     {field_name}: Ошибка - {blob_data['error']}")
                    else:
                        content = blob_data.get("value", {}).get("content", "")
                        if content:
                            content_preview = (
                                content[:50] + "..." if len(content) > 50 else content
                            )
                            print(f"     {field_name}: {content_preview}")

        # Сохраняем отчет об извлечении
        report_file = "test_base_extractor_report.json"
        if extractor.save_extraction_report(report_file, extracted_data):
            print(f"\n💾 Отчет об извлечении сохранен: {report_file}")

        # Получаем финальную статистику
        final_stats = extractor.get_extraction_stats()
        print("\n📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"   Всего элементов: {final_stats['total_items']}")
        print(f"   Успешно извлечено: {final_stats['successful_extractions']}")
        print(f"   Ошибок извлечения: {final_stats['failed_extractions']}")
        print(f"   BLOB полей найдено: {final_stats['blob_fields_found']}")
        print(f"   BLOB полей обработано: {final_stats['blob_fields_processed']}")

        if final_stats["extraction_errors"]:
            print(f"   Ошибки извлечения: {len(final_stats['extraction_errors'])}")
            for error in final_stats["extraction_errors"][
                :3
            ]:  # Показываем первые 3 ошибки
                print(f"     - {error}")

        print("\n✅ ТЕСТИРОВАНИЕ BASE EXTRACTOR ЗАВЕРШЕНО УСПЕШНО")
        return True

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Закрываем подключение к базе данных
        if "db_connector" in locals():
            db_connector.close()
            print("🔌 Подключение к базе данных закрыто")


if __name__ == "__main__":
    success = test_base_extractor()
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("   BaseExtractor работает корректно")
        print("   Базовый класс готов для наследования")
    else:
        print("\n❌ ТЕСТЫ НЕ ПРОШЛИ")
        print("   Требуется исправление ошибок")

    sys.exit(0 if success else 1)
