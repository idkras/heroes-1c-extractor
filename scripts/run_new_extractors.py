#!/usr/bin/env python3
"""
Скрипт для запуска новых extractors и создания parquet файлов
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем путь к src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from extractors.flat_table_extractor import FlatTableExtractor
from extractors.document_extractor import DocumentExtractor
from extractors.reference_extractor import ReferenceExtractor


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def run_flat_table_extractor():
    """Запуск FlatTableExtractor"""
    print("🔍 Запуск FlatTableExtractor...")

    try:
        extractor = FlatTableExtractor("data/raw/1Cv8.1CD")

        # Извлекаем плоскую таблицу
        results = extractor.extract_flat_table()

        # Сохраняем в Parquet
        parquet_path = extractor.save_to_parquet()
        print(f"✅ FlatTableExtractor завершен: {parquet_path}")

        return True

    except Exception as e:
        print(f"❌ Ошибка FlatTableExtractor: {e}")
        return False


def run_document_extractor():
    """Запуск DocumentExtractor"""
    print("🔍 Запуск DocumentExtractor...")

    try:
        extractor = DocumentExtractor("data/raw/1Cv8.1CD")

        # Извлекаем документы
        results = extractor.extract_documents()

        # Сохраняем в Parquet
        parquet_path = extractor.save_to_parquet()
        print(f"✅ DocumentExtractor завершен: {parquet_path}")

        return True

    except Exception as e:
        print(f"❌ Ошибка DocumentExtractor: {e}")
        return False


def run_reference_extractor():
    """Запуск ReferenceExtractor"""
    print("🔍 Запуск ReferenceExtractor...")

    try:
        extractor = ReferenceExtractor("data/raw/1Cv8.1CD")

        # Извлекаем справочники
        results = extractor.extract_references()

        # Сохраняем в Parquet
        parquet_path = extractor.save_to_parquet()
        print(f"✅ ReferenceExtractor завершен: {parquet_path}")

        return True

    except Exception as e:
        print(f"❌ Ошибка ReferenceExtractor: {e}")
        return False


def main():
    """Главная функция"""
    print("🚀 ЗАПУСК НОВЫХ EXTRACTORS")
    print("=" * 50)

    setup_logging()

    # Проверяем наличие базы данных
    db_path = "data/raw/1Cv8.1CD"
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False

    # Создаем директорию для результатов
    os.makedirs("data/results/parquet", exist_ok=True)

    # Запускаем extractors
    results = []

    print("\n1️⃣ Запуск FlatTableExtractor...")
    results.append(run_flat_table_extractor())

    print("\n2️⃣ Запуск DocumentExtractor...")
    results.append(run_document_extractor())

    print("\n3️⃣ Запуск ReferenceExtractor...")
    results.append(run_reference_extractor())

    # Проверяем результаты
    successful = sum(results)
    total = len(results)

    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   Успешно: {successful}/{total}")
    print(f"   Parquet файлы созданы в: data/results/parquet/")

    if successful > 0:
        print("✅ Notebook теперь найдет parquet файлы!")
        return True
    else:
        print("❌ Ни один extractor не завершился успешно")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
