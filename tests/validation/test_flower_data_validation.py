#!/usr/bin/env python3

"""
Валидационные тесты для данных о цветах
Автоматизирует проверку тест-кейсов TC-002, TC-007, TC-010
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestFlowerDataValidation(unittest.TestCase):
    """Валидационные тесты для данных о цветах"""

    def setUp(self):
        """Настройка тестов"""
        self.results_dir = Path("data/results")
        self.expected_flowers = ["роз", "тюльпан", "хризантем", "гвоздик", "лили"]
        self.expected_colors = ["красн", "желт", "бел", "розов", "голуб"]

    def test_tc002_flower_extraction_completeness(self):
        """TC-002: Проверка полноты извлечения данных о цветах"""
        # Проверяем наличие Parquet файлов с данными о цветах
        parquet_files = list(self.results_dir.glob("*.parquet"))
        self.assertGreater(
            len(parquet_files),
            0,
            "Не найдены Parquet файлы с данными о цветах",
        )

        # Проверяем наличие DuckDB базы
        duckdb_file = self.results_dir / "flowers_analytics.duckdb"
        self.assertTrue(
            duckdb_file.exists(),
            "Не найдена DuckDB база с данными о цветах",
        )

    def test_tc007_parquet_flower_data_quality(self):
        """TC-007: Проверка качества данных о цветах в Parquet"""
        # Проверяем критические таблицы
        critical_tables = [
            "_DOCUMENTJOURNAL5354",
            "_DOCUMENTJOURNAL5287",
            "_DOCUMENTJOURNAL5321",
            "_DOCUMENT138",
            "_DOCUMENT156",
        ]

        for table in critical_tables:
            parquet_file = self.results_dir / f"{table}.parquet"
            if parquet_file.exists():
                # Проверяем размер файла (должен быть > 0)
                self.assertGreater(
                    parquet_file.stat().st_size,
                    0,
                    f"Файл {table}.parquet пустой",
                )

                # Проверяем содержимое файла
                import pandas as pd

                try:
                    df = pd.read_parquet(parquet_file)
                    self.assertGreater(
                        len(df),
                        0,
                        f"Таблица {table} не содержит данных",
                    )

                    # Проверяем наличие данных о цветах
                    if "content" in df.columns:
                        flower_found = False
                        for content in df["content"].dropna():
                            if any(
                                flower in str(content).lower()
                                for flower in self.expected_flowers
                            ):
                                flower_found = True
                                break
                        self.assertTrue(
                            flower_found,
                            f"В таблице {table} не найдены данные о цветах",
                        )

                except Exception as e:
                    self.fail(f"Ошибка чтения Parquet файла {table}: {e}")

    def test_tc010_duckdb_flower_analytics(self):
        """TC-010: Проверка аналитических возможностей DuckDB для цветов"""
        duckdb_file = self.results_dir / "flowers_analytics.duckdb"
        if not duckdb_file.exists():
            self.skipTest("DuckDB файл не найден")

        # Проверяем подключение к DuckDB
        try:
            import duckdb

            conn = duckdb.connect(str(duckdb_file))

            # Проверяем наличие таблиц
            tables = conn.execute("SHOW TABLES").fetchall()
            self.assertGreater(len(tables), 0, "В DuckDB нет таблиц")

            # Проверяем наличие данных о цветах
            for (table_name,) in tables:
                result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                self.assertIsNotNone(
                    result,
                    f"Не удалось получить результат для таблицы {table_name}",
                )
                if result is not None:
                    self.assertGreater(result[0], 0, f"Таблица {table_name} пустая")

                # Проверяем наличие данных о цветах в таблице
                if "content" in [
                    col[0] for col in conn.execute(f"DESCRIBE {table_name}").fetchall()
                ]:
                    flower_query = f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE LOWER(content) LIKE '%роз%'
                    OR LOWER(content) LIKE '%тюльпан%'
                    OR LOWER(content) LIKE '%хризантем%'
                    """
                    flower_result = conn.execute(flower_query).fetchone()
                    self.assertIsNotNone(
                        flower_result,
                        f"Не удалось получить результат запроса для таблицы {table_name}",
                    )
                    if flower_result is not None:
                        flower_count = flower_result[0]
                        self.assertGreater(
                            flower_count,
                            0,
                            f"В таблице {table_name} не найдены данные о цветах",
                        )

            conn.close()

        except Exception as e:
            self.fail(f"Ошибка работы с DuckDB: {e}")

    def test_flower_data_quality_metrics(self):
        """Проверка метрик качества данных о цветах"""
        # Проверяем наличие всех ожидаемых цветов
        found_flowers = set()
        found_colors = set()

        # Сканируем все JSON файлы в results
        json_files = list(self.results_dir.glob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Ищем данные о цветах в содержимом
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            content = value.lower()
                            for flower in self.expected_flowers:
                                if flower in content:
                                    found_flowers.add(flower)
                            for color in self.expected_colors:
                                if color in content:
                                    found_colors.add(color)

            except Exception as e:
                print(f"Ошибка чтения файла {json_file}: {e}")
                continue

        # Проверяем метрики качества
        flower_coverage = len(found_flowers) / len(self.expected_flowers)
        color_coverage = len(found_colors) / len(self.expected_colors)

        self.assertGreaterEqual(
            flower_coverage,
            0.5,
            f"Покрытие цветов {flower_coverage:.2%} < 50%",
        )
        self.assertGreaterEqual(
            color_coverage,
            0.3,
            f"Покрытие цветов {color_coverage:.2%} < 30%",
        )

        print(
            f"Найдено цветов: {len(found_flowers)}/{len(self.expected_flowers)} ({flower_coverage:.2%})",
        )
        print(
            f"Найдено цветов: {len(found_colors)}/{len(self.expected_colors)} ({color_coverage:.2%})",
        )

    def test_flower_business_chain_validation(self):
        """Проверка полной цепочки цветочного бизнеса"""
        # Проверяем наличие данных о закупках
        purchase_data_found = False
        sales_data_found = False
        inventory_data_found = False

        # Сканируем все файлы результатов
        for file_path in self.results_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".json", ".xml"]:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read().lower()

                    # Проверяем ключевые слова для разных этапов бизнеса
                    if any(
                        word in content
                        for word in ["поступление", "закупка", "поставщик"]
                    ):
                        purchase_data_found = True
                    if any(word in content for word in ["продажа", "чек", "кассир"]):
                        sales_data_found = True
                    if any(
                        word in content
                        for word in ["остаток", "инвентаризация", "склад"]
                    ):
                        inventory_data_found = True

                except Exception:
                    continue

        # Проверяем наличие всех этапов цепочки
        self.assertTrue(purchase_data_found, "Не найдены данные о закупках цветов")
        self.assertTrue(sales_data_found, "Не найдены данные о продажах цветов")
        self.assertTrue(inventory_data_found, "Не найдены данные об остатках цветов")

        print("✅ Полная цепочка цветочного бизнеса найдена:")
        print(f"  - Закупки: {'✅' if purchase_data_found else '❌'}")
        print(f"  - Продажи: {'✅' if sales_data_found else '❌'}")
        print(f"  - Остатки: {'✅' if inventory_data_found else '❌'}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
