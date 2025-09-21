#!/usr/bin/env python3
"""
Тестовый скрипт для проверки извлечения реальных документов из 1С.

JTBD:
Как тестовый скрипт, я хочу проверить извлечение реальных документов из 1С,
чтобы подтвердить работоспособность SimpleDocumentExtractor.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к src
sys.path.append("src")
sys.path.append("src/extractors")
sys.path.append("src/processors")

from extractors.simple_document_extractor import SimpleDocumentExtractor
from processors.database_connector import DatabaseConnector


def test_simple_extraction():
    """
    JTBD:
    Как тестовая функция, я хочу протестировать извлечение реальных документов,
    чтобы подтвердить работоспособность SimpleDocumentExtractor.
    """
    print("🧪 ТЕСТИРОВАНИЕ ИЗВЛЕЧЕНИЯ РЕАЛЬНЫХ ДОКУМЕНТОВ ИЗ 1С")
    print("=" * 60)

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

        # Получаем список таблиц
        tables = db_connector.get_tables()
        print(f"📋 Найдено таблиц: {len(tables)}")

        # Ищем таблицы документов
        document_tables = db_connector.get_document_tables()
        print(f"📄 Найдено таблиц документов: {len(document_tables)}")

        if not document_tables:
            print("❌ Не найдено таблиц документов")
            return False

        # Ищем таблицу документов с данными, начиная с известных рабочих таблиц
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
                        f"🎯 Найдена известная рабочая таблица: {test_table_name} ({table_info['size']} записей)"
                    )
                    break

        # Если не нашли известные, ищем любую с данными
        if not test_table_name:
            for table_name in document_tables.keys():
                table_info = db_connector.get_table_info(table_name)
                if table_info["has_data"] and table_info["size"] > 0:
                    test_table_name = table_name
                    print(
                        f"🎯 Найдена таблица с данными: {test_table_name} ({table_info['size']} записей)"
                    )
                    break

        if not test_table_name:
            print("❌ Не найдено таблиц документов с данными")
            return False

        # Создаем извлекатель документов
        extractor = SimpleDocumentExtractor(db_connector)

        # Извлекаем документы (ограничиваем до 10 для тестирования)
        print(f"📊 Извлечение документов из {test_table_name}...")
        documents = extractor.extract_documents(test_table_name, limit=10)

        if not documents:
            print("❌ Не удалось извлечь документы")
            return False

        print(f"✅ Извлечено документов: {len(documents)}")

        # Анализируем структуру документов
        print("🔍 Анализ структуры документов...")
        structure_analysis = extractor.analyze_document_structure(documents)

        print(f"📊 Результаты анализа структуры:")
        print(f"   Всего документов: {structure_analysis['total_documents']}")
        print(f"   Всего полей: {structure_analysis['summary']['total_fields']}")
        print(f"   BLOB полей: {structure_analysis['summary']['total_blob_fields']}")
        print(
            f"   Документов с BLOB: {structure_analysis['summary']['documents_with_blobs']}"
        )

        # Валидируем качество извлечения
        print("🔍 Валидация качества извлечения...")
        quality_metrics = extractor.validate_extraction_quality(documents)

        print(f"📊 Результаты валидации качества:")
        print(f"   Документов с данными: {quality_metrics['documents_with_data']}")
        print(f"   Документов с BLOB: {quality_metrics['documents_with_blobs']}")
        print(f"   Успешность BLOB: {quality_metrics['blob_success_rate']:.1f}%")
        print(f"   Полнота полей: {quality_metrics['field_completeness']:.1f}%")
        print(f"   Общий балл качества: {quality_metrics['quality_score']}/100")

        # Показываем примеры извлеченных данных
        print("\n📄 ПРИМЕРЫ ИЗВЛЕЧЕННЫХ ДАННЫХ:")
        print("-" * 40)

        for i, doc in enumerate(documents[:3]):  # Показываем первые 3 документа
            print(f"\n📋 Документ {i+1}:")
            print(f"   Таблица: {doc['table_name']}")
            print(f"   Индекс: {doc['row_index']}")
            print(f"   Полей: {len(doc.get('fields', {}))}")
            print(f"   BLOB полей: {len(doc.get('blob_fields', {}))}")

            # Показываем примеры полей
            if doc.get("fields"):
                print("   Обычные поля:")
                for field_name, field_data in list(doc["fields"].items())[:3]:
                    value = field_data.get("value", "None")
                    if len(str(value)) > 50:
                        value = str(value)[:50] + "..."
                    print(f"     {field_name}: {value}")

            # Показываем примеры BLOB полей
            if doc.get("blob_fields"):
                print("   BLOB поля:")
                for field_name, blob_data in list(doc["blob_fields"].items())[:2]:
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
        report_file = "test_extraction_report.json"
        if extractor.save_extraction_report(report_file):
            print(f"\n💾 Отчет об извлечении сохранен: {report_file}")

        # Получаем статистику извлечения
        stats = extractor.get_extraction_stats()
        print(f"\n📊 СТАТИСТИКА ИЗВЛЕЧЕНИЯ:")
        print(f"   Всего документов: {stats['total_documents']}")
        print(f"   Успешно извлечено: {stats['successful_extractions']}")
        print(f"   Ошибок извлечения: {stats['failed_extractions']}")
        print(f"   BLOB полей найдено: {stats['blob_fields_found']}")
        print(f"   BLOB полей обработано: {stats['blob_fields_processed']}")

        if stats["extraction_errors"]:
            print(f"   Ошибки извлечения: {len(stats['extraction_errors'])}")
            for error in stats["extraction_errors"][:3]:  # Показываем первые 3 ошибки
                print(f"     - {error}")

        print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
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
    success = test_simple_extraction()
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("   SimpleDocumentExtractor работает корректно")
        print("   Реальные документы извлекаются из 1С")
    else:
        print("\n❌ ТЕСТЫ НЕ ПРОШЛИ")
        print("   Требуется исправление ошибок")

    sys.exit(0 if success else 1)
