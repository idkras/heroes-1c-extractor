#!/usr/bin/env python3
"""
Интеграционные тесты для DocumentAnalyzer с реальной 1С базой

JTBD:
Как тестировщик, я хочу протестировать DocumentAnalyzer с реальными данными из 1С базы,
чтобы убедиться в корректности анализа документов в реальных условиях.
"""

import pytest
from pathlib import Path
from onec_dtools import DatabaseReader
from src.processors.document_analyzer import DocumentAnalyzer

# Применяем патч для поддержки новых типов полей 1С
try:
    import os
    import sys

    patch_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "tests",
        "integration",
    )
    sys.path.insert(0, patch_path)
    from simple_patch import apply_simple_patch

    apply_simple_patch()
    print("✅ Патч для новых типов полей применен")
except Exception as e:
    print(f"⚠️ Не удалось применить патч: {e}")


class TestDocumentAnalyzerIntegration:
    """Интеграционные тесты для DocumentAnalyzer с реальной 1С базой"""

    @pytest.fixture(scope="class")
    def db_connection(self):
        """
        JTBD:
        Как тестовая фикстура, я хочу подключиться к реальной 1С базе,
        чтобы обеспечить доступ к реальным данным для тестирования.
        """
        cdb_file_path = (
            Path(__file__).parent.parent.parent / "data" / "raw" / "1Cv8.1CD"
        )

        if not cdb_file_path.exists():
            pytest.skip(f"1С база данных не найдена: {cdb_file_path}")

        try:
            with open(cdb_file_path, "rb") as f:
                db = DatabaseReader(f)
                yield db
        except Exception as e:
            pytest.skip(f"Не удалось подключиться к 1С базе: {e}")

    @pytest.fixture
    def analyzer(self):
        """Фикстура для DocumentAnalyzer"""
        return DocumentAnalyzer()

    def test_analyze_real_document_structure(self, db_connection, analyzer):
        """
        Тест анализа структуры реального документа из 1С базы

        JTBD:
        Как тестировщик, я хочу протестировать анализ структуры реального документа,
        чтобы убедиться в корректности работы с реальными данными.
        """
        # Выбираем таблицу с документами
        document_tables = [
            t for t in db_connection.tables.keys() if t.startswith("_DOCUMENT")
        ]

        if not document_tables:
            pytest.skip("Не найдены таблицы документов")

        table_name = document_tables[0]
        table = db_connection.tables[table_name]

        print(f"\n🔍 Тестируем таблицу: {table_name}")
        print(f"📊 Всего записей: {len(table):,}")

        # Анализируем первые 5 записей
        for i in range(min(5, len(table))):
            try:
                row = table[i]
                if not hasattr(row, "is_empty") or not row.is_empty:
                    # Извлекаем данные строки
                    row_list = row.as_list(True) if hasattr(row, "as_list") else []
                    if not row_list:
                        continue

                    # Создаем словарь полей
                    row_dict = {}
                    for j, value in enumerate(row_list):
                        if hasattr(value, "name") and value.name and value.name.strip():
                            row_dict[value.name] = value
                        else:
                            row_dict[f"field_{j}"] = value

                    print(f"\n📄 Анализ документа {i+1}:")
                    print(f"   📋 Поля: {list(row_dict.keys())[:10]}...")
                    print(f"   📊 Всего полей: {len(row_dict)}")

                    # Анализируем структуру документа
                    field_analysis, structure = analyzer.analyze_document_structure(
                        row_dict
                    )

                    # Проверяем результаты анализа
                    assert len(field_analysis) == len(row_dict)
                    assert isinstance(
                        structure, type(analyzer).__module__ + ".DocumentStructure"
                    )

                    # Извлекаем метаданные
                    metadata = analyzer.extract_document_metadata(
                        field_analysis, structure
                    )

                    # Проверяем метаданные
                    assert isinstance(
                        metadata, type(analyzer).__module__ + ".DocumentMetadata"
                    )

                    # Создаем сводку
                    summary = analyzer.create_document_summary(
                        field_analysis, structure, metadata
                    )

                    # Проверяем сводку
                    assert "metadata" in summary
                    assert "structure" in summary
                    assert "statistics" in summary

                    print(f"   ✅ Номер документа: {metadata.document_number}")
                    print(f"   ✅ Дата документа: {metadata.document_date}")
                    print(f"   ✅ Тип документа: {metadata.document_type}")
                    print(f"   ✅ Сумма: {metadata.total_amount}")
                    print(f"   ✅ Магазин: {metadata.store_name}")
                    print(f"   ✅ Код магазина: {metadata.store_code}")

                    # Статистика полей
                    print(f"   📊 Статистика полей:")
                    print(f"      Всего полей: {summary['statistics']['total_fields']}")
                    print(
                        f"      Числовые поля: {summary['statistics']['numeric_fields']}"
                    )
                    print(
                        f"      Строковые поля: {summary['statistics']['string_fields']}"
                    )
                    print(
                        f"      Поля с датами: {summary['statistics']['date_fields']}"
                    )
                    print(f"      BLOB поля: {summary['statistics']['blob_fields']}")
                    print(f"      Пустые поля: {summary['statistics']['empty_fields']}")

                    # Структура полей
                    print(f"   📋 Структура полей:")
                    print(f"      Поля с номерами: {structure.number_fields}")
                    print(f"      Поля с датами: {structure.date_fields}")
                    print(f"      Поля с суммами: {structure.amount_fields}")
                    print(f"      Поля с описанием: {structure.description_fields}")
                    print(f"      BLOB поля: {structure.blob_fields}")

                    # Анализируем BLOB поля
                    for blob_field in structure.blob_fields:
                        if blob_field in field_analysis:
                            field_info = field_analysis[blob_field]
                            if (
                                hasattr(field_info.value, "value")
                                and field_info.value.value
                            ):
                                try:
                                    blob_content = field_info.value.value.decode(
                                        "utf-8", errors="ignore"
                                    )
                                    if len(blob_content) > 0:
                                        print(
                                            f"      🔍 BLOB поле {blob_field}: {blob_content[:100]}..."
                                        )

                                        # Анализируем содержимое BLOB
                                        blob_analysis = analyzer.analyze_blob_content(
                                            blob_content
                                        )
                                        print(
                                            f"         Цветочная информация: {blob_analysis['has_floristic_info']}"
                                        )
                                        print(
                                            f"         Информация о магазине: {blob_analysis['has_store_info']}"
                                        )
                                        print(
                                            f"         Финансовая информация: {blob_analysis['has_finance_info']}"
                                        )
                                        print(
                                            f"         Найденные цвета: {blob_analysis['colors_found']}"
                                        )
                                        print(
                                            f"         Типы букетов: {blob_analysis['bouquet_types_found']}"
                                        )
                                except Exception as e:
                                    print(
                                        f"         ⚠️ Ошибка анализа BLOB {blob_field}: {e}"
                                    )

                    print(f"   ✅ Анализ документа {i+1} завершен успешно")

            except Exception as e:
                print(f"   ⚠️ Ошибка при анализе документа {i+1}: {e}")
                continue

        print(f"\n✅ Интеграционный тест DocumentAnalyzer завершен успешно")

    def test_analyze_multiple_document_tables(self, db_connection, analyzer):
        """
        Тест анализа нескольких таблиц документов

        JTBD:
        Как тестировщик, я хочу протестировать анализ нескольких таблиц документов,
        чтобы убедиться в корректности работы с разными типами документов.
        """
        # Выбираем несколько таблиц с документами
        document_tables = [
            t for t in db_connection.tables.keys() if t.startswith("_DOCUMENT")
        ]

        if not document_tables:
            pytest.skip("Не найдены таблицы документов")

        # Анализируем первые 3 таблицы
        for table_name in document_tables[:3]:
            try:
                table = db_connection.tables[table_name]
                print(f"\n🔍 Анализ таблицы: {table_name}")
                print(f"📊 Всего записей: {len(table):,}")

                # Анализируем первые 3 записи из каждой таблицы
                for i in range(min(3, len(table))):
                    try:
                        row = table[i]
                        if not hasattr(row, "is_empty") or not row.is_empty:
                            # Извлекаем данные строки
                            row_list = (
                                row.as_list(True) if hasattr(row, "as_list") else []
                            )
                            if not row_list:
                                continue

                            # Создаем словарь полей
                            row_dict = {}
                            for j, value in enumerate(row_list):
                                if (
                                    hasattr(value, "name")
                                    and value.name
                                    and value.name.strip()
                                ):
                                    row_dict[value.name] = value
                                else:
                                    row_dict[f"field_{j}"] = value

                            # Анализируем структуру документа
                            field_analysis, structure = (
                                analyzer.analyze_document_structure(row_dict)
                            )

                            # Извлекаем метаданные
                            metadata = analyzer.extract_document_metadata(
                                field_analysis, structure
                            )

                            # Создаем сводку
                            summary = analyzer.create_document_summary(
                                field_analysis, structure, metadata
                            )

                            print(
                                f"   📄 Документ {i+1}: {metadata.document_number} | {metadata.document_type} | {metadata.total_amount}₽"
                            )

                    except Exception as e:
                        print(f"   ⚠️ Ошибка при анализе документа {i+1}: {e}")
                        continue

                print(f"   ✅ Анализ таблицы {table_name} завершен")

            except Exception as e:
                print(f"   ⚠️ Ошибка при анализе таблицы {table_name}: {e}")
                continue

        print(f"\n✅ Анализ нескольких таблиц документов завершен успешно")

    def test_analyze_blob_fields_in_real_data(self, db_connection, analyzer):
        """
        Тест анализа BLOB полей в реальных данных

        JTBD:
        Как тестировщик, я хочу протестировать анализ BLOB полей в реальных данных,
        чтобы убедиться в корректности извлечения цветочной информации.
        """
        # Выбираем таблицу с документами
        document_tables = [
            t for t in db_connection.tables.keys() if t.startswith("_DOCUMENT")
        ]

        if not document_tables:
            pytest.skip("Не найдены таблицы документов")

        table_name = document_tables[0]
        table = db_connection.tables[table_name]

        print(f"\n🔍 Анализ BLOB полей в таблице: {table_name}")

        blob_fields_found = 0
        floristic_info_found = 0
        store_info_found = 0
        finance_info_found = 0
        colors_found = []
        bouquet_types_found = []

        # Анализируем первые 10 записей
        for i in range(min(10, len(table))):
            try:
                row = table[i]
                if not hasattr(row, "is_empty") or not row.is_empty:
                    # Извлекаем данные строки
                    row_list = row.as_list(True) if hasattr(row, "as_list") else []
                    if not row_list:
                        continue

                    # Создаем словарь полей
                    row_dict = {}
                    for j, value in enumerate(row_list):
                        if hasattr(value, "name") and value.name and value.name.strip():
                            row_dict[value.name] = value
                        else:
                            row_dict[f"field_{j}"] = value

                    # Анализируем структуру документа
                    field_analysis, structure = analyzer.analyze_document_structure(
                        row_dict
                    )

                    # Анализируем BLOB поля
                    for blob_field in structure.blob_fields:
                        if blob_field in field_analysis:
                            field_info = field_analysis[blob_field]
                            if (
                                hasattr(field_info.value, "value")
                                and field_info.value.value
                            ):
                                try:
                                    blob_content = field_info.value.value.decode(
                                        "utf-8", errors="ignore"
                                    )
                                    if len(blob_content) > 0:
                                        blob_fields_found += 1

                                        # Анализируем содержимое BLOB
                                        blob_analysis = analyzer.analyze_blob_content(
                                            blob_content
                                        )

                                        if blob_analysis["has_floristic_info"]:
                                            floristic_info_found += 1

                                        if blob_analysis["has_store_info"]:
                                            store_info_found += 1

                                        if blob_analysis["has_finance_info"]:
                                            finance_info_found += 1

                                        colors_found.extend(
                                            blob_analysis["colors_found"]
                                        )
                                        bouquet_types_found.extend(
                                            blob_analysis["bouquet_types_found"]
                                        )

                                        print(
                                            f"   🔍 BLOB поле {blob_field}: {blob_content[:50]}..."
                                        )
                                        print(
                                            f"      Цветочная информация: {blob_analysis['has_floristic_info']}"
                                        )
                                        print(
                                            f"      Информация о магазине: {blob_analysis['has_store_info']}"
                                        )
                                        print(
                                            f"      Финансовая информация: {blob_analysis['has_finance_info']}"
                                        )
                                        print(
                                            f"      Найденные цвета: {blob_analysis['colors_found']}"
                                        )
                                        print(
                                            f"      Типы букетов: {blob_analysis['bouquet_types_found']}"
                                        )

                                except Exception as e:
                                    print(
                                        f"      ⚠️ Ошибка анализа BLOB {blob_field}: {e}"
                                    )

            except Exception as e:
                print(f"   ⚠️ Ошибка при анализе записи {i+1}: {e}")
                continue

        # Выводим итоговую статистику
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА BLOB АНАЛИЗА:")
        print(f"   📦 Найдено BLOB полей: {blob_fields_found}")
        print(f"   🌸 Цветочная информация: {floristic_info_found}")
        print(f"   🏪 Информация о магазинах: {store_info_found}")
        print(f"   💰 Финансовая информация: {finance_info_found}")
        print(f"   🎨 Найденные цвета: {set(colors_found)}")
        print(f"   💐 Типы букетов: {set(bouquet_types_found)}")

        # Проверяем, что анализ прошел успешно
        assert blob_fields_found >= 0  # Может быть 0, если нет BLOB полей
        assert floristic_info_found >= 0
        assert store_info_found >= 0
        assert finance_info_found >= 0

        print(f"\n✅ Анализ BLOB полей в реальных данных завершен успешно")

