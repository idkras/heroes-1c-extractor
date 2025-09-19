#!/usr/bin/env python3
"""
Integration tests for BlobProcessor with real 1C database.

JTBD:
Как тестировщик, я хочу проверить BlobProcessor с реальными данными из 1С,
чтобы убедиться в правильном извлечении BLOB полей из базы данных.
"""

import os
import sys
import pytest
from pathlib import Path
from typing import Any, Dict, List

# Добавляем путь к src для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from processors.blob_processor import BlobProcessor
from onec_dtools import DatabaseReader


class TestBlobProcessorIntegration:
    """Интеграционные тесты для BlobProcessor с реальной 1С базой."""

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
            # Применяем патч для поддержки новых типов полей 1С
            from simple_patch import apply_simple_patch

            apply_simple_patch()

            with open(cdb_file_path, "rb") as f:
                db = DatabaseReader(f)
                yield db
        except Exception as e:
            pytest.skip(f"Не удалось подключиться к 1С базе: {e}")

    @pytest.fixture
    def blob_processor(self):
        """Фикстура для BlobProcessor."""
        return BlobProcessor()

    def test_blob_processor_with_real_database(self, db_connection, blob_processor):
        """
        JTBD:
        Как тестировщик, я хочу проверить BlobProcessor с реальной базой данных,
        чтобы убедиться в правильном извлечении BLOB полей.
        """
        # Arrange
        print(f"\n🔍 Тестирование BlobProcessor с реальной 1С базой")
        print(f"📊 Найдено таблиц: {len(db_connection.tables)}")

        # Находим таблицы с документами
        document_tables = [
            name for name in db_connection.tables.keys() if name.startswith("_DOCUMENT")
        ]
        print(f"📄 Найдено таблиц документов: {len(document_tables)}")

        if not document_tables:
            pytest.skip("Не найдены таблицы документов в базе данных")

        # Берем первую таблицу для тестирования
        table_name = document_tables[0]
        table = db_connection.tables[table_name]
        print(f"🎯 Тестируем таблицу: {table_name} ({len(table)} записей)")

        # Находим непустые записи
        non_empty_rows = []
        for i in range(min(10, len(table))):  # Берем только первые 10 записей
            try:
                row = table[i]
                if not hasattr(row, "is_empty") or not row.is_empty:
                    non_empty_rows.append((i, row))
            except Exception as e:
                print(f"⚠️ Ошибка при проверке записи {i}: {e}")
                continue

        print(f"✅ Найдено {len(non_empty_rows)} непустых записей")

        if not non_empty_rows:
            pytest.skip("Не найдены непустые записи в таблице")

        # Тестируем BlobProcessor на реальных данных
        blob_results = []
        for i, (row_index, row) in enumerate(
            non_empty_rows[:3]
        ):  # Тестируем первые 3 записи
            print(f"\n📋 Анализ записи {i+1} (индекс {row_index}):")

            try:
                # Извлекаем данные строки
                row_list = row.as_list(True) if hasattr(row, "as_list") else []
                if not row_list:
                    print(f"   ⚠️ Пустая строка")
                    continue

                # Создаем словарь полей
                row_dict = {}
                for j, value in enumerate(row_list):
                    if hasattr(value, "name") and value.name and value.name.strip():
                        row_dict[value.name] = value
                    else:
                        row_dict[f"field_{j}"] = value

                print(f"   📊 Полей в записи: {len(row_dict)}")

                # Ищем BLOB поля
                blob_fields = []
                for field_name, value in row_dict.items():
                    if blob_processor._is_blob_object(value):
                        blob_fields.append(field_name)
                        print(f"   🔍 Найдено BLOB поле: {field_name}")

                print(f"   📦 BLOB полей найдено: {len(blob_fields)}")

                # Обрабатываем BLOB поля
                for field_name in blob_fields:
                    value = row_dict[field_name]
                    print(f"   🔄 Обработка BLOB поля: {field_name}")

                    result = blob_processor.process_blob_field(field_name, value)
                    blob_results.append(result)

                    # Проверяем результат
                    assert result["field_type"] == "blob"
                    assert result["field_name"] == field_name

                    if result.get("extraction_methods"):
                        print(
                            f"      ✅ Успешно извлечено методами: {', '.join(result['extraction_methods'])}"
                        )

                        # Проверяем содержимое
                        if "value" in result and result["value"].get("content"):
                            content = result["value"]["content"]
                            print(
                                f"      📄 Содержимое ({len(content)} символов): {content[:100]}{'...' if len(content) > 100 else ''}"
                            )

                            # Анализируем содержимое
                            flower_info = blob_processor.extract_flower_information(
                                content
                            )
                            if flower_info["has_flower_info"]:
                                print(f"      🌸 Найдена цветочная информация!")

                            store_info = blob_processor.extract_store_information(
                                content
                            )
                            if store_info["store_name"]:
                                print(
                                    f"      🏪 Название магазина: {store_info['store_name']}"
                                )
                            if store_info["store_code"]:
                                print(
                                    f"      🏷️ Код магазина: {store_info['store_code']}"
                                )

                            doc_type = blob_processor.determine_document_type(content)
                            if doc_type != "Неизвестно":
                                print(f"      📋 Тип документа: {doc_type}")
                        else:
                            print(f"      ❌ Не удалось извлечь содержимое")
                    else:
                        print(f"      ❌ Не удалось извлечь BLOB данные")
                        if result.get("error"):
                            print(f"         🚫 Ошибка: {result['error']}")

            except Exception as e:
                print(f"   ❌ Ошибка при обработке записи {i+1}: {e}")
                continue

        # Проверяем результаты
        assert len(blob_results) > 0, "Не найдены BLOB поля для тестирования"

        successful_extractions = sum(
            1 for result in blob_results if result.get("extraction_methods")
        )
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"   📦 Всего BLOB полей: {len(blob_results)}")
        print(f"   ✅ Успешно извлечено: {successful_extractions}")
        print(f"   ❌ Неудачных: {len(blob_results) - successful_extractions}")

        if successful_extractions > 0:
            success_rate = (successful_extractions / len(blob_results)) * 100
            print(f"   📈 Процент успеха: {success_rate:.1f}%")

            # Проверяем что процент успеха разумный
            assert success_rate >= 50, f"Слишком низкий процент успеха: {success_rate}%"
        else:
            pytest.fail("Не удалось извлечь ни одного BLOB поля")

    def test_blob_processor_with_specific_table(self, db_connection, blob_processor):
        """
        JTBD:
        Как тестировщик, я хочу проверить BlobProcessor на конкретной таблице,
        чтобы убедиться в правильной обработке BLOB полей.
        """
        # Ищем таблицы с большим количеством записей
        large_tables = []
        for table_name, table in db_connection.tables.items():
            if table_name.startswith("_DOCUMENT") and len(table) > 1000:
                large_tables.append((table_name, len(table)))

        if not large_tables:
            pytest.skip("Не найдены большие таблицы для тестирования")

        # Сортируем по размеру
        large_tables.sort(key=lambda x: x[1], reverse=True)
        table_name, table_size = large_tables[0]

        print(
            f"\n🎯 Тестирование на большой таблице: {table_name} ({table_size:,} записей)"
        )

        table = db_connection.tables[table_name]

        # Анализируем структуру таблицы
        sample_size = min(100, len(table))
        blob_fields_found = set()

        for i in range(sample_size):
            try:
                row = table[i]
                if not hasattr(row, "is_empty") or not row.is_empty:
                    row_list = row.as_list(True) if hasattr(row, "as_list") else []
                    if row_list:
                        for j, value in enumerate(row_list):
                            if blob_processor._is_blob_object(value):
                                field_name = f"field_{j}"
                                if hasattr(value, "name") and value.name:
                                    field_name = value.name
                                blob_fields_found.add(field_name)
            except Exception:
                continue

        print(f"📦 Найдено BLOB полей в выборке: {len(blob_fields_found)}")
        print(f"🔍 BLOB поля: {list(blob_fields_found)[:10]}...")

        # Проверяем что найдены BLOB поля
        assert len(blob_fields_found) > 0, "Не найдены BLOB поля в таблице"

        # Тестируем обработку найденных BLOB полей
        test_results = []
        for i in range(min(10, len(table))):
            try:
                row = table[i]
                if not hasattr(row, "is_empty") or not row.is_empty:
                    row_list = row.as_list(True) if hasattr(row, "as_list") else []
                    if row_list:
                        for j, value in enumerate(row_list):
                            if blob_processor._is_blob_object(value):
                                field_name = f"field_{j}"
                                if hasattr(value, "name") and value.name:
                                    field_name = value.name

                                result = blob_processor.process_blob_field(
                                    field_name, value
                                )
                                test_results.append(result)

                                if (
                                    len(test_results) >= 5
                                ):  # Ограничиваем количество тестов
                                    break
                    if len(test_results) >= 5:
                        break
            except Exception:
                continue

        print(f"🧪 Протестировано BLOB полей: {len(test_results)}")

        # Проверяем результаты
        assert len(test_results) > 0, "Не удалось протестировать BLOB поля"

        successful = sum(
            1 for result in test_results if result.get("extraction_methods")
        )
        print(f"✅ Успешно обработано: {successful}/{len(test_results)}")

        if successful > 0:
            print("🎉 BlobProcessor успешно работает с реальными данными!")
        else:
            print("⚠️ BlobProcessor не смог извлечь данные из BLOB полей")
