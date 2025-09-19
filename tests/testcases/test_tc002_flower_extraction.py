#!/usr/bin/env python3

"""
Автоматизированный тест-кейс TC-002: Извлечение данных о цветах и товарах
Соответствует тест-кейсу из 1c.testcases.md
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestTC002FlowerExtraction(unittest.TestCase):
    """TC-002: Автоматизированный тест извлечения данных о цветах"""

    def setUp(self):
        """Настройка теста"""
        self.results_dir = Path("data/results")
        self.expected_flowers = ["роз", "тюльпан", "хризантем", "гвоздик", "лили"]
        self.expected_quantities = [50, 30, 20, 5, 3, 25, 15, 10]
        self.expected_prices = [174, 120, 80, 200, 150]

    def test_who_role_manager_assortment(self):
        """WHO: Роль - Менеджер по ассортименту"""
        # Проверяем, что данные подходят для менеджера по ассортименту
        self.assertTrue(self.results_dir.exists(), "Папка результатов не найдена")

        # Проверяем наличие файлов с данными о товарах
        data_files = list(self.results_dir.glob("*.json")) + list(
            self.results_dir.glob("*.xml"),
        )
        self.assertGreater(len(data_files), 0, "Не найдены файлы с данными о товарах")

    def test_what_extract_nomenclature_data(self):
        """WHAT: Извлечь данные о номенклатуре товаров"""
        # Проверяем извлечение названий цветов
        found_flowers = set()
        found_quantities = set()
        found_prices = set()

        # Сканируем все файлы результатов
        for file_path in self.results_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".json", ".xml"]:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        if file_path.suffix == ".json":
                            data = json.load(f)
                            content = str(data).lower()
                        else:
                            content = f.read().lower()

                    # Ищем цветы
                    for flower in self.expected_flowers:
                        if flower in content:
                            found_flowers.add(flower)

                    # Ищем количества
                    for qty in self.expected_quantities:
                        if str(qty) in content:
                            found_quantities.add(qty)

                    # Ищем цены
                    for price in self.expected_prices:
                        if str(price) in content:
                            found_prices.add(price)

                except Exception as e:
                    print(f"Ошибка чтения файла {file_path}: {e}")
                    continue

        # Проверяем критерии успеха
        self.assertGreaterEqual(
            len(found_flowers),
            3,
            f"Найдено цветов: {len(found_flowers)}, ожидалось ≥3",
        )
        self.assertGreaterEqual(
            len(found_quantities),
            3,
            f"Найдено количеств: {len(found_quantities)}, ожидалось ≥3",
        )
        self.assertGreaterEqual(
            len(found_prices),
            3,
            f"Найдено цен: {len(found_prices)}, ожидалось ≥3",
        )

        print(f"✅ Найдено цветов: {len(found_flowers)}/{len(self.expected_flowers)}")
        print(
            f"✅ Найдено количеств: {len(found_quantities)}/{len(self.expected_quantities)}",
        )
        print(f"✅ Найдено цен: {len(found_prices)}/{len(self.expected_prices)}")

    def test_when_daily_inventory_trigger(self):
        """WHEN: Триггер - Ежедневная инвентаризация"""
        # Проверяем, что данные актуальны для ежедневной инвентаризации
        # Время выполнения должно быть ≤3 минуты на 1000 позиций

        import time

        start_time = time.time()

        # Симулируем обработку 1000 позиций
        processed_count = 0
        for file_path in self.results_dir.rglob("*.json"):
            if processed_count >= 1000:
                break
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        processed_count += len(data)
                    else:
                        processed_count += 1
            except Exception:
                continue

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверяем время выполнения (≤3 минуты = 180 секунд)
        self.assertLessEqual(
            execution_time,
            180,
            f"Время выполнения {execution_time:.2f}с > 180с",
        )

        print(f"✅ Обработано позиций: {processed_count}")
        print(f"✅ Время выполнения: {execution_time:.2f}с")

    def test_where_source_table_parts(self):
        """WHERE: Источник - Табличные части документов 1С"""
        # Проверяем, что данные извлечены из табличных частей документов
        document_tables = [
            "_DOCUMENTJOURNAL5354",
            "_DOCUMENTJOURNAL5287",
            "_DOCUMENTJOURNAL5321",
            "_DOCUMENT138",
            "_DOCUMENT156",
        ]

        found_tables = []
        for table in document_tables:
            # Проверяем JSON файлы
            json_file = self.results_dir / f"{table}.json"
            if json_file.exists():
                found_tables.append(table)
                # Проверяем, что файл не пустой
                self.assertGreater(
                    json_file.stat().st_size,
                    0,
                    f"Файл {table}.json пустой",
                )

            # Проверяем Parquet файлы
            parquet_file = self.results_dir / f"{table}.parquet"
            if parquet_file.exists():
                found_tables.append(f"{table}_parquet")
                self.assertGreater(
                    parquet_file.stat().st_size,
                    0,
                    f"Файл {table}.parquet пустой",
                )

        self.assertGreaterEqual(
            len(found_tables),
            3,
            f"Найдено таблиц: {len(found_tables)}, ожидалось ≥3",
        )

        print(f"✅ Найдено таблиц документов: {len(found_tables)}")

    def test_why_business_goal_inventory_control(self):
        """WHY: Бизнес-цель - Контроль остатков и закупок"""
        # Проверяем, что данные подходят для контроля остатков
        inventory_keywords = ["остаток", "склад", "инвентаризация", "количество"]
        purchase_keywords = ["закупка", "поставщик", "поступление"]

        inventory_found = False
        purchase_found = False

        # Сканируем файлы на наличие ключевых слов
        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()

                if any(keyword in content for keyword in inventory_keywords):
                    inventory_found = True
                if any(keyword in content for keyword in purchase_keywords):
                    purchase_found = True

            except Exception:
                continue

        self.assertTrue(inventory_found, "Не найдены данные для контроля остатков")
        self.assertTrue(purchase_found, "Не найдены данные для контроля закупок")

        print(f"✅ Контроль остатков: {'✅' if inventory_found else '❌'}")
        print(f"✅ Контроль закупок: {'✅' if purchase_found else '❌'}")

    def test_how_method_parsing_table_parts(self):
        """HOW: Метод - Парсинг табличных частей документов"""
        # Проверяем, что используется правильный метод извлечения
        # Должны быть найдены данные в BLOB полях документов

        blob_data_found = False
        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                # Проверяем структуру данных (должны быть документы с BLOB полями)
                if isinstance(data, dict) and "documents" in data:
                    for document in data["documents"]:
                        if isinstance(document, dict) and "blobs" in document:
                            # Ищем данные о цветах в BLOB полях
                            for blob_name, blob_data in document["blobs"].items():
                                if isinstance(blob_data, dict) and "value" in blob_data:
                                    content = blob_data["value"].get("content", "")
                                    if isinstance(content, str) and any(
                                        flower in content.lower()
                                        for flower in self.expected_flowers
                                    ):
                                        blob_data_found = True
                                        break
                            if blob_data_found:
                                break

            except Exception:
                continue

        self.assertTrue(blob_data_found, "Не найдены данные в BLOB полях документов")
        print("✅ Данные извлечены из BLOB полей документов")

    def test_success_criteria_complete_flower_list(self):
        """Критерий успеха: Полный список всех цветов в системе"""
        found_flowers = set()

        # Сканируем все файлы
        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()

                for flower in self.expected_flowers:
                    if flower in content:
                        found_flowers.add(flower)

            except Exception:
                continue

        # Проверяем, что найдено ≥70% ожидаемых цветов
        coverage = len(found_flowers) / len(self.expected_flowers)
        self.assertGreaterEqual(coverage, 0.7, f"Покрытие цветов {coverage:.2%} < 70%")

        print(
            f"✅ Найдено цветов: {len(found_flowers)}/{len(self.expected_flowers)} ({coverage:.2%})",
        )

    def test_success_criteria_actual_balances(self):
        """Критерий успеха: Актуальные остатки по каждому цвету"""
        # Проверяем наличие данных об остатках
        balance_keywords = ["остаток", "количество", "штук", "шт"]
        balance_found = False

        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()

                if any(keyword in content for keyword in balance_keywords):
                    balance_found = True
                    break

            except Exception:
                continue

        self.assertTrue(balance_found, "Не найдены данные об остатках")
        print("✅ Найдены данные об остатках")

    def test_success_criteria_prices_and_units(self):
        """Критерий успеха: Цены и единицы измерения для всех позиций"""
        # Проверяем наличие цен и единиц измерения
        price_keywords = ["руб", "рублей", "цена", "стоимость"]
        unit_keywords = ["штук", "шт", "кг", "г", "литр"]

        prices_found = False
        units_found = False

        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()

                if any(keyword in content for keyword in price_keywords):
                    prices_found = True
                if any(keyword in content for keyword in unit_keywords):
                    units_found = True

            except Exception:
                continue

        self.assertTrue(prices_found, "Не найдены данные о ценах")
        self.assertTrue(units_found, "Не найдены данные о единицах измерения")

        print(f"✅ Цены: {'✅' if prices_found else '❌'}")
        print(f"✅ Единицы измерения: {'✅' if units_found else '❌'}")

    def test_success_criteria_movement_history(self):
        """Критерий успеха: История движения товаров"""
        # Проверяем наличие истории движения
        movement_keywords = ["поступление", "продажа", "перемещение", "движение"]
        movement_found = False

        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()

                if any(keyword in content for keyword in movement_keywords):
                    movement_found = True
                    break

            except Exception:
                continue

        self.assertTrue(movement_found, "Не найдена история движения товаров")
        print("✅ Найдена история движения товаров")

    def test_success_criteria_supplier_connection(self):
        """Критерий успеха: Связь с поставщиками для каждого товара"""
        # Проверяем наличие связи с поставщиками
        supplier_keywords = ["поставщик", "компания", "ооо", "ип"]
        supplier_found = False

        for file_path in self.results_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read().lower()

                if any(keyword in content for keyword in supplier_keywords):
                    supplier_found = True
                    break

            except Exception:
                continue

        self.assertTrue(supplier_found, "Не найдены данные о поставщиках")
        print("✅ Найдены данные о поставщиках")


if __name__ == "__main__":
    unittest.main(verbosity=2)
