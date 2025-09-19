#!/usr/bin/env python3
"""
Скрипт для запуска тестов качества notebook
Автоматическая проверка по AI QA стандарту
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_notebook_qa_tests(test_type: str = "all", verbose: bool = True) -> bool:
    """Запуск тестов качества notebook"""

    print("🔍 ЗАПУСК ТЕСТОВ КАЧЕСТВА NOTEBOOK")
    print("=" * 50)

    # Базовые команды pytest
    base_cmd = ["python3", "-m", "pytest", "tests/notebook/test_notebook_qa.py"]

    if verbose:
        base_cmd.append("-v")

    # Выбор типа тестов
    if test_type == "syntax":
        cmd = base_cmd + ["-k", "syntax", "--tb=short"]
        print("🧪 Запуск синтаксических тестов...")

    elif test_type == "data":
        cmd = base_cmd + ["-k", "data", "--tb=short"]
        print("📊 Запуск тестов данных...")

    elif test_type == "performance":
        cmd = base_cmd + ["-k", "performance", "--tb=short"]
        print("⚡ Запуск тестов производительности...")

    elif test_type == "ai_metrics":
        cmd = base_cmd + ["-k", "TestNotebookAIMetrics", "--tb=short"]
        print("🤖 Запуск тестов AI метрик...")

    elif test_type == "all":
        cmd = base_cmd + ["--tb=short"]
        print("🎯 Запуск всех тестов...")

    else:
        print(f"❌ Неизвестный тип тестов: {test_type}")
        return False

    # Запуск тестов
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        print("\n📋 РЕЗУЛЬТАТЫ ТЕСТОВ:")
        print("-" * 30)
        print(result.stdout)

        if result.stderr:
            print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            return True
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
        return False

    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return False


def check_data_files() -> bool:
    """Проверка существования файлов данных"""

    print("\n🔍 ПРОВЕРКА ФАЙЛОВ ДАННЫХ:")
    print("-" * 30)

    data_files = [
        "data/results/parquet/documents.parquet",
        "data/results/duckdb/analysis.duckdb",
        "data/results/test_flowers.parquet",
        "data/results/test_flowers.duckdb",
    ]

    all_exist = True
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path} ({size:,} байт)")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")
            all_exist = False

    return all_exist


def run_notebook_execution_test() -> bool:
    """Тест выполнения notebook"""

    print("\n▶️ ТЕСТ ВЫПОЛНЕНИЯ NOTEBOOK:")
    print("-" * 30)

    from pathlib import Path

    notebook_path = Path("notebooks/parquet_analysis.ipynb")

    if not notebook_path.exists():
        print(f"❌ Notebook не найден: {notebook_path}")
        return False

    try:
        # Импортируем и выполняем код из notebook
        from pathlib import Path

        import duckdb
        import pandas as pd

        # Основные файлы с документами 1С
        DOCUMENTS_PARQUET = Path("data/results/parquet/documents.parquet")
        ANALYSIS_DUCKDB = Path("data/results/duckdb/analysis.duckdb")
        TEST_FLOWERS_PARQUET = Path("data/results/test_flowers.parquet")
        TEST_FLOWERS_DUCKDB = Path("data/results/test_flowers.duckdb")

        print("📊 Анализ документов 1С")
        print("=" * 40)

        # Анализ основного файла с документами
        if DOCUMENTS_PARQUET.exists():
            print(f"📄 {DOCUMENTS_PARQUET.name}:")
            df = pd.read_parquet(DOCUMENTS_PARQUET)
            print(f"  Записей: {len(df):,}")
            print(f"  Колонок: {len(df.columns)}")
            print(f"  Основные колонки: {list(df.columns[:5])}")

            # Покажем примеры данных
            if len(df) > 0:
                print("\n  Примеры записей:")
                sample = df.head(5)
                for idx, row in sample.iterrows():
                    print(
                        f"    {idx}: {row['table_name']} - {row.get('field__NUMBER', 'N/A')}",
                    )
        else:
            print(f"❌ Файл не найден: {DOCUMENTS_PARQUET}")
            return False

        # Анализ тестового файла с цветами
        if TEST_FLOWERS_PARQUET.exists():
            print(f"\n🌸 {TEST_FLOWERS_PARQUET.name}:")
            df = pd.read_parquet(TEST_FLOWERS_PARQUET)
            print(f"  Записей: {len(df)}")
            print(f"  Колонки: {list(df.columns)}")

            if len(df) > 0:
                print("\n  Данные о цветах:")
                for idx, row in df.iterrows():
                    print(
                        f"    {row['document_id']}: {row['flower_type']} - {row['store']} - {row['amount']} руб.",
                    )
        else:
            print(f"❌ Файл не найден: {TEST_FLOWERS_PARQUET}")
            return False

        # Анализ DuckDB файлов
        duckdb_files = [
            (ANALYSIS_DUCKDB, "Основная база с документами"),
            (TEST_FLOWERS_DUCKDB, "Тестовая база с цветами"),
        ]

        for duckdb_file, description in duckdb_files:
            if duckdb_file.exists():
                print(f"\n🗄️ {duckdb_file.name} ({description}):")
                conn = duckdb.connect(str(duckdb_file))
                tables = conn.execute("SHOW TABLES").fetchall()
                for (table_name,) in tables:
                    result = conn.execute(
                        f"SELECT COUNT(*) FROM {table_name}",
                    ).fetchone()
                    count = result[0] if result else 0
                    print(f"  Таблица {table_name}: {count:,} записей")
                conn.close()
            else:
                print(f"❌ Файл не найден: {duckdb_file}")
                return False

        print("\n✅ NOTEBOOK ВЫПОЛНЯЕТСЯ БЕЗ ОШИБОК!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при выполнении notebook: {e}")
        return False


def main() -> None:
    """Главная функция"""

    parser = argparse.ArgumentParser(description="Запуск тестов качества notebook")
    parser.add_argument(
        "--type",
        choices=["all", "syntax", "data", "performance", "ai_metrics"],
        default="all",
        help="Тип тестов для запуска",
    )
    parser.add_argument(
        "--check-data",
        action="store_true",
        help="Проверить файлы данных",
    )
    parser.add_argument(
        "--test-execution",
        action="store_true",
        help="Тестировать выполнение notebook",
    )
    parser.add_argument("--verbose", action="store_true", help="Подробный вывод")

    args = parser.parse_args()

    print("🚀 NOTEBOOK QA TESTING")
    print("=" * 50)

    success = True

    # Проверка файлов данных
    if args.check_data:
        if not check_data_files():
            print("\n❌ НЕ ВСЕ ФАЙЛЫ ДАННЫХ НАЙДЕНЫ!")
            success = False

    # Тест выполнения notebook
    if args.test_execution:
        if not run_notebook_execution_test():
            print("\n❌ NOTEBOOK НЕ ВЫПОЛНЯЕТСЯ!")
            success = False

    # Запуск тестов
    if not run_notebook_qa_tests(args.type, args.verbose):
        success = False

    # Итоговый результат
    print("\n" + "=" * 50)
    if success:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        sys.exit(0)
    else:
        print("💥 НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        sys.exit(1)


if __name__ == "__main__":
    main()
