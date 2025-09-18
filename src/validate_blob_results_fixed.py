#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для проверки результатов извлечения BLOB данных
по тест-кейсам из 1c.testcases.md
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Импорты для Parquet и DuckDB
try:
    import duckdb
    import pandas as pd

    PARQUET_DUCKDB_AVAILABLE = True
except ImportError:
    PARQUET_DUCKDB_AVAILABLE = False
    print(
        "⚠️ Parquet/DuckDB не установлены. Установите: pip install pandas pyarrow duckdb"
    )


class BlobResultsValidator:
    """Валидатор результатов извлечения BLOB данных"""

    def __init__(self) -> None:
        self.test_cases: Dict[str, Dict[str, Any]] = {
            "test_case_7": {
                "name": "Проверка Parquet данных о цветах",
                "criteria": [
                    "Найдены названия цветов - розы, тюльпаны, хризантемы",
                    "Найдены количества - сколько каждого цветка продано",
                    "Найдены цены - стоимость за единицу каждого цветка",
                    "Найдены даты - когда продавались цветы",
                    "Найдены магазины - в каких магазинах продавались цветы",
                ],
            },
            "test_case_8": {
                "name": "Проверка DuckDB данных о цветах",
                "criteria": [
                    "SQL запросы работают - можно выполнить SELECT запросы",
                    "Найдены цветы в DuckDB - розы, тюльпаны, хризантемы",
                    "Найдены магазины в DuckDB - все магазины с цветами",
                    "Найдены продажи в DuckDB - когда и сколько продано",
                    "Найдены закупки в DuckDB - откуда пришли цветы",
                ],
            },
            "test_case_9": {
                "name": "Проверка интеграции Parquet + DuckDB для цветов",
                "criteria": [
                    "Данные синхронизированы - одинаковые данные в Parquet и DuckDB",
                    "Найдены цветы в обоих форматах - розы, тюльпаны, хризантемы",
                    "Найдены магазины в обоих форматах - все магазины с цветами",
                    "Найдены продажи в обоих форматах - когда и сколько продано",
                    "Найдены закупки в обоих форматах - откуда пришли цветы",
                ],
            },
        }

        # Ключевые слова для поиска цветов
        self.flower_keywords: List[str] = [
            "роз",
            "тюльпан",
            "хризантем",
            "лили",
            "гвоздик",
            "орхиде",
            "цвет",
            "букет",
            "флор",
            "флористическ",
            "моно",
            "яндекс",
        ]

        # Ключевые слова для поиска магазинов
        self.store_keywords: List[str] = [
            "магазин",
            "склад",
            "пц",
            "чеховск",
            "южн",
            "братиславск",
            "интернет",
            "яндекс",
            "маркет",
            "директ",
            "еда",
        ]

    def validate_parquet_data(self, parquet_path: str) -> Dict[str, Any]:
        """Проверка Parquet данных"""
        print(f"🔍 Проверка Parquet файла: {parquet_path}")

        if not PARQUET_DUCKDB_AVAILABLE:
            return {"error": "Parquet не доступен"}

        if not os.path.exists(parquet_path):
            return {"error": f"Файл не найден: {parquet_path}"}

        try:
            # Читаем Parquet файл
            df = pd.read_parquet(parquet_path)

            results: Dict[str, Any] = {
                "file_path": parquet_path,
                "total_records": len(df),
                "columns": list(df.columns),
                "flower_data_found": 0,
                "store_data_found": 0,
                "flower_keywords_found": [],
                "store_keywords_found": [],
                "validation_passed": True,
                "errors": [],
            }

            # Проверяем наличие данных о цветах
            if "has_flower_data" in df.columns:
                flower_records = df[df["has_flower_data"] == True]
                results["flower_data_found"] = len(flower_records)

                if len(flower_records) > 0:
                    # Анализируем ключевые слова
                    flower_keywords = flower_records["flower_keywords"].dropna()
                    for keywords in flower_keywords:
                        for keyword in keywords.split(", "):
                            if (
                                keyword
                                and keyword not in results["flower_keywords_found"]
                            ):
                                results["flower_keywords_found"].append(keyword)

            # Проверяем наличие данных о магазинах
            if "has_store_data" in df.columns:
                store_records = df[df["has_store_data"] == True]
                results["store_data_found"] = len(store_records)

                if len(store_records) > 0:
                    # Анализируем ключевые слова
                    store_keywords = store_records["store_keywords"].dropna()
                    for keywords in store_keywords:
                        for keyword in keywords.split(", "):
                            if (
                                keyword
                                and keyword not in results["store_keywords_found"]
                            ):
                                results["store_keywords_found"].append(keyword)

            # Проверяем критерии тест-кейса
            if results["flower_data_found"] == 0:
                results["errors"].append("Не найдены данные о цветах")
                results["validation_passed"] = False

            if results["store_data_found"] == 0:
                results["errors"].append("Не найдены данные о магазинах")
                results["validation_passed"] = False

            print(f"✅ Записей в файле: {results['total_records']}")
            print(f"🌸 Данных о цветах: {results['flower_data_found']}")
            print(f"🏪 Данных о магазинах: {results['store_data_found']}")
            print(
                f"🔍 Ключевые слова цветов: {', '.join(results['flower_keywords_found'])}"
            )
            print(
                f"🔍 Ключевые слова магазинов: {', '.join(results['store_keywords_found'])}"
            )

            return results

        except Exception as e:
            return {"error": f"Ошибка чтения Parquet файла: {e}"}

    def validate_duckdb_data(self, duckdb_path: str) -> Dict[str, Any]:
        """Проверка DuckDB данных"""
        print(f"🔍 Проверка DuckDB файла: {duckdb_path}")

        if not PARQUET_DUCKDB_AVAILABLE:
            return {"error": "DuckDB не доступен"}

        if not os.path.exists(duckdb_path):
            return {"error": f"Файл не найден: {duckdb_path}"}

        try:
            # Подключаемся к DuckDB
            conn = duckdb.connect(duckdb_path)

            results: Dict[str, Any] = {
                "file_path": duckdb_path,
                "tables": [],
                "sql_queries_work": False,
                "flower_data_found": 0,
                "store_data_found": 0,
                "validation_passed": True,
                "errors": [],
            }

            # Получаем список таблиц
            tables_result = conn.execute("SHOW TABLES").fetchall()
            results["tables"] = [table[0] for table in tables_result]

            if not results["tables"]:
                results["errors"].append("Нет таблиц в DuckDB")
                results["validation_passed"] = False
                return results

            # Проверяем SQL запросы
            try:
                # Тестовый запрос
                test_query = f"SELECT COUNT(*) FROM {results['tables'][0]}"
                conn.execute(test_query).fetchone()
                results["sql_queries_work"] = True

                # Запрос данных о цветах
                if "has_flower_data" in [
                    col[0]
                    for col in conn.execute(
                        f"DESCRIBE {results['tables'][0]}"
                    ).fetchall()
                ]:
                    flower_query = f"SELECT COUNT(*) FROM {results['tables'][0]} WHERE has_flower_data = true"
                    flower_result = conn.execute(flower_query).fetchone()
                    flower_count = flower_result[0] if flower_result else 0
                    results["flower_data_found"] = flower_count

                # Запрос данных о магазинах
                if "has_store_data" in [
                    col[0]
                    for col in conn.execute(
                        f"DESCRIBE {results['tables'][0]}"
                    ).fetchall()
                ]:
                    store_query = f"SELECT COUNT(*) FROM {results['tables'][0]} WHERE has_store_data = true"
                    store_result = conn.execute(store_query).fetchone()
                    store_count = store_result[0] if store_result else 0
                    results["store_data_found"] = store_count

            except Exception as e:
                results["errors"].append(f"Ошибка SQL запроса: {e}")
                results["validation_passed"] = False

            conn.close()

            print(f"✅ Таблиц в базе: {len(results['tables'])}")
            print(f"🔍 SQL запросы работают: {results['sql_queries_work']}")
            print(f"🌸 Данных о цветах: {results['flower_data_found']}")
            print(f"🏪 Данных о магазинах: {results['store_data_found']}")

            return results

        except Exception as e:
            return {"error": f"Ошибка работы с DuckDB: {e}"}

    def validate_integration(
        self, parquet_path: str, duckdb_path: str
    ) -> Dict[str, Any]:
        """Проверка интеграции Parquet + DuckDB"""
        print("🔍 Проверка интеграции Parquet + DuckDB")

        results: Dict[str, Any] = {
            "parquet_path": parquet_path,
            "duckdb_path": duckdb_path,
            "data_synchronized": False,
            "flower_data_sync": False,
            "store_data_sync": False,
            "validation_passed": True,
            "errors": [],
        }

        # Проверяем Parquet данные
        parquet_results = self.validate_parquet_data(parquet_path)
        if "error" in parquet_results:
            results["errors"].append(f"Ошибка Parquet: {parquet_results['error']}")
            results["validation_passed"] = False
            return results

        # Проверяем DuckDB данные
        duckdb_results = self.validate_duckdb_data(duckdb_path)
        if "error" in duckdb_results:
            results["errors"].append(f"Ошибка DuckDB: {duckdb_results['error']}")
            results["validation_passed"] = False
            return results

        # Сравниваем данные
        parquet_flower_count = parquet_results.get("flower_data_found", 0)
        duckdb_flower_count = duckdb_results.get("flower_data_found", 0)

        parquet_store_count = parquet_results.get("store_data_found", 0)
        duckdb_store_count = duckdb_results.get("store_data_found", 0)

        # Проверяем синхронизацию
        if parquet_flower_count == duckdb_flower_count:
            results["flower_data_sync"] = True
        else:
            results["errors"].append(
                f"Несинхронизированы данные о цветах: Parquet={parquet_flower_count}, DuckDB={duckdb_flower_count}"
            )

        if parquet_store_count == duckdb_store_count:
            results["store_data_sync"] = True
        else:
            results["errors"].append(
                f"Несинхронизированы данные о магазинах: Parquet={parquet_store_count}, DuckDB={duckdb_store_count}"
            )

        results["data_synchronized"] = (
            results["flower_data_sync"] and results["store_data_sync"]
        )

        if not results["data_synchronized"]:
            results["validation_passed"] = False

        print(f"✅ Данные синхронизированы: {results['data_synchronized']}")
        print(f"🌸 Цветы синхронизированы: {results['flower_data_sync']}")
        print(f"🏪 Магазины синхронизированы: {results['store_data_sync']}")

        return results

    def run_validation(self) -> Dict[str, Any]:
        """Запуск полной валидации"""
        print("🧪 ВАЛИДАЦИЯ РЕЗУЛЬТАТОВ ИЗВЛЕЧЕНИЯ BLOB ДАННЫХ")
        print("=" * 80)

        # Ищем файлы результатов
        results_dir = Path("data/results")
        if not results_dir.exists():
            return {"error": "Папка результатов не найдена: data/results"}

        # Ищем Parquet файлы
        parquet_files = list(results_dir.glob("*_blob_1000.parquet"))
        duckdb_files = list(results_dir.glob("*_blob_1000.duckdb"))

        print(f"📁 Найдено Parquet файлов: {len(parquet_files)}")
        print(f"📁 Найдено DuckDB файлов: {len(duckdb_files)}")

        validation_results: Dict[str, Any] = {
            "validation_date": datetime.now().isoformat(),
            "test_cases": {},
            "summary": {
                "total_files_validated": 0,
                "validation_passed": 0,
                "validation_failed": 0,
                "total_errors": 0,
            },
        }

        # Валидируем каждый файл
        for parquet_file in parquet_files:
            table_name = parquet_file.stem.replace("_blob_1000", "")
            print(f"\n{'='*60}")
            print(f"📊 ВАЛИДАЦИЯ ТАБЛИЦЫ: {table_name}")
            print(f"{'='*60}")

            # Валидируем Parquet
            parquet_results = self.validate_parquet_data(str(parquet_file))

            # Ищем соответствующий DuckDB файл
            duckdb_file = results_dir / f"{table_name}_blob_1000.duckdb"
            duckdb_results = None
            integration_results = None

            if duckdb_file.exists():
                # Валидируем DuckDB
                duckdb_results = self.validate_duckdb_data(str(duckdb_file))

                # Валидируем интеграцию
                integration_results = self.validate_integration(
                    str(parquet_file), str(duckdb_file)
                )

            # Сохраняем результаты
            table_results: Dict[str, Any] = {
                "table_name": table_name,
                "parquet_results": parquet_results,
                "duckdb_results": duckdb_results,
                "integration_results": integration_results,
            }

            validation_results["test_cases"][table_name] = table_results

            # Обновляем статистику
            validation_results["summary"]["total_files_validated"] += 1

            if "error" not in parquet_results and parquet_results.get(
                "validation_passed", False
            ):
                validation_results["summary"]["validation_passed"] += 1
            else:
                validation_results["summary"]["validation_failed"] += 1
                validation_results["summary"]["total_errors"] += len(
                    parquet_results.get("errors", [])
                )

        # Сохраняем отчет валидации
        report_path = "data/results/validation_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(validation_results, f, ensure_ascii=False, indent=2)

        print("\n📊 ИТОГОВАЯ СТАТИСТИКА ВАЛИДАЦИИ:")
        print(
            f"📁 Файлов проверено: {validation_results['summary']['total_files_validated']}"
        )
        print(
            f"✅ Валидация прошла: {validation_results['summary']['validation_passed']}"
        )
        print(
            f"❌ Валидация не прошла: {validation_results['summary']['validation_failed']}"
        )
        print(f"🚨 Всего ошибок: {validation_results['summary']['total_errors']}")
        print(f"📄 Отчет сохранен: {report_path}")

        return validation_results


def main() -> bool:
    """Основная функция"""
    print("🧪 ВАЛИДАЦИЯ РЕЗУЛЬТАТОВ ИЗВЛЕЧЕНИЯ BLOB ДАННЫХ")
    print("=" * 80)

    # Создаем валидатор
    validator = BlobResultsValidator()

    # Запускаем валидацию
    results = validator.run_validation()

    if "error" in results:
        print(f"❌ Ошибка валидации: {results['error']}")
        return False

    print("\n✅ Валидация завершена успешно!")
    print("📊 Проверьте отчет в файле data/results/validation_report.json")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
