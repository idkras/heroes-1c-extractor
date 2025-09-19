#!/usr/bin/env python3

"""
Скрипт для запуска автоматической валидации извлеченных данных
Можно запускать отдельно от процесса извлечения
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.validate_blob_results import BlobResultsValidator


def main() -> None:
    """Основная функция"""
    print("🧪 АВТОМАТИЧЕСКАЯ ВАЛИДАЦИЯ ИЗВЛЕЧЕННЫХ ДАННЫХ")
    print("=" * 60)

    # Проверяем наличие результатов
    results_dir = Path("data/results")
    if not results_dir.exists():
        print("❌ Папка с результатами не найдена: data/results")
        print("💡 Запустите извлечение данных сначала:")
        print("   python src/extract_all_available_data.py")
        sys.exit(1)

    # Проверяем наличие файлов результатов
    result_files = (
        list(results_dir.glob("*.json"))
        + list(results_dir.glob("*.parquet"))
        + list(results_dir.glob("*.duckdb"))
    )
    if not result_files:
        print("❌ В папке результатов нет файлов для валидации")
        print("💡 Запустите извлечение данных сначала:")
        print("   python src/extract_all_available_data.py")
        sys.exit(1)

    print(f"📁 Найдено файлов для валидации: {len(result_files)}")

    # Создаем валидатор
    validator = BlobResultsValidator()

    # Запускаем валидацию
    try:
        results = validator.run_validation()

        # Выводим итоговый отчет
        print(f"✅ Валидация завершена. Результаты: {results['summary']}")

        # Возвращаем код выхода
        if results["summary"]["validation_failed"] > 0:
            print("\n❌ Валидация завершена с ошибками")
            print("💡 Проверьте отчет в data/results/validation_report.json")
            sys.exit(1)
        else:
            print("\n✅ Валидация завершена успешно")
            print("📊 Все данные прошли проверку качества")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
