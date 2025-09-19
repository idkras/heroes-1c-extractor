#!/usr/bin/env python3

"""
Конвертация JSON данных в Parquet + DuckDB для оптимизированного анализа
"""

import json
import os
import sys
from typing import Any

import duckdb
import pandas as pd

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def load_json_data(json_file: str) -> dict[str, Any]:
    """Загружает данные из JSON файла"""
    print(f"📁 Загрузка данных из {json_file}...")

    if not os.path.exists(json_file):
        print(f"❌ Файл {json_file} не найден")
        return {}

    try:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Загружено {len(data.get('documents', []))} документов")
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки {json_file}: {e}")
        return {}


def convert_documents_to_dataframe(documents: list[dict[str, Any]]) -> pd.DataFrame:
    """Конвертирует документы в DataFrame"""
    print("🔄 Конвертация документов в DataFrame...")

    rows = []
    for doc in documents:
        # Основные поля
        row = {
            "id": doc.get("id", ""),
            "table_name": doc.get("table_name", ""),
            "row_index": doc.get("row_index", 0),
        }

        # ИСПРАВЛЕНО: Создаем бизнес-поля из технических полей
        if "fields" in doc:
            fields = doc["fields"]

            # Извлекаем бизнес-поля из технических полей
            row["document_number"] = fields.get("_NUMBER", "N/A")

            # ИСПРАВЛЕНО: Ищем дату в разных полях
            date_value = "N/A"
            for field_name, field_value in fields.items():
                if isinstance(field_value, str) and len(field_value) > 10:
                    # Проверяем, содержит ли поле дату
                    if any(char.isdigit() for char in field_value) and any(
                        char in field_value for char in [".", "-", "/"]
                    ):
                        date_value = field_value
                        break
            row["document_date"] = date_value

            row["total_amount"] = fields.get("_FLD4239", 0)
            row["quantity"] = fields.get("_FLD4238", 0)
            row["unit_measure"] = fields.get("_FLD4240", 1)
            row["posted"] = fields.get("_POSTED", False)
            row["marked"] = fields.get("_MARKED", False)

            # Определяем тип документа по table_name
            table_name = doc.get("table_name", "")
            if "JOURNAL" in table_name:
                row["document_type"] = "ЖУРНАЛ"
            elif "DOCUMENT138" in table_name:
                row["document_type"] = "ПЕРЕМЕЩЕНИЕ"
            elif "DOCUMENT156" in table_name:
                row["document_type"] = "РЕАЛИЗАЦИЯ"
            elif "DOCUMENT184" in table_name:
                row["document_type"] = "СЧЕТ-ФАКТУРА"
            else:
                row["document_type"] = "ДОКУМЕНТ"

            # ИСПРАВЛЕНО: Извлекаем магазин из BLOB полей
            row["store_name"] = "N/A"
            if "blobs" in doc:
                for blob_name, blob_data in doc["blobs"].items():
                    if isinstance(blob_data, dict):
                        # Ищем содержимое в value.content
                        if "value" in blob_data and isinstance(
                            blob_data["value"],
                            dict,
                        ):
                            content = blob_data["value"].get("content", "")
                        elif "content" in blob_data:
                            content = blob_data["content"]
                        else:
                            continue

                        if isinstance(content, str) and content.strip():
                            # Ищем магазины в содержимом
                            if "ПЦ022" in content:
                                row["store_name"] = "ПЦ022 (Чеховский)"
                            elif "ПЦ036" in content:
                                row["store_name"] = "ПЦ036 (Южный)"
                            elif "Братиславский" in content:
                                row["store_name"] = "Братиславский"
                            elif "Южный" in content:
                                row["store_name"] = "Южный"
                            elif "Чеховский" in content:
                                row["store_name"] = "Чеховский"
                            break

        # BLOB поля для поиска
        if "blobs" in doc:
            blob_content = ""
            for blob_name, blob_data in doc["blobs"].items():
                if isinstance(blob_data, dict):
                    # ИСПРАВЛЕНО: Правильное извлечение BLOB содержимого
                    if "value" in blob_data and isinstance(blob_data["value"], dict):
                        value_data = blob_data["value"]
                        if "content" in value_data and isinstance(
                            value_data["content"],
                            str,
                        ):
                            content = value_data["content"]
                            if content and content.strip():
                                blob_content += content + " "
                    elif "content" in blob_data and isinstance(
                        blob_data["content"],
                        str,
                    ):
                        content = blob_data["content"]
                        if content and content.strip():
                            blob_content += content + " "
            row["blob_content"] = blob_content.strip()
        else:
            row["blob_content"] = ""

        # Статистика извлечения
        if "extraction_stats" in doc:
            stats = doc["extraction_stats"]
            row["total_blobs"] = stats.get("total_blobs", 0)
            row["successful_blobs"] = stats.get("successful", 0)
            row["failed_blobs"] = stats.get("failed", 0)

        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"✅ Создан DataFrame с {len(df)} строками и {len(df.columns)} столбцами")
    return df


def save_to_parquet(df: pd.DataFrame, output_file: str) -> None:
    """Сохраняет DataFrame в Parquet формат"""
    print(f"💾 Сохранение в Parquet: {output_file}...")

    try:
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Сохраняем в Parquet
        df.to_parquet(output_file, compression="snappy", index=False)

        # Получаем размер файла
        file_size = os.path.getsize(output_file)
        print(f"✅ Parquet файл сохранен: {file_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"❌ Ошибка сохранения Parquet: {e}")


def create_duckdb_database(parquet_file: str, db_file: str) -> None:
    """Создает DuckDB базу данных из Parquet файла"""
    print(f"🗄️ Создание DuckDB базы: {db_file}...")

    try:
        # Подключаемся к DuckDB
        conn = duckdb.connect(db_file)

        # Создаем таблицу из Parquet файла
        conn.execute(
            f"""
            CREATE TABLE documents AS 
            SELECT * FROM read_parquet('{parquet_file}')
        """,
        )

        # Создаем индексы для быстрого поиска
        print("🔍 Создание индексов...")

        # Индекс по table_name
        conn.execute("CREATE INDEX idx_table_name ON documents(table_name)")

        # Индекс по row_index
        conn.execute("CREATE INDEX idx_row_index ON documents(row_index)")

        # Индекс по BLOB полям (если есть)
        blob_columns = [
            col
            for col in conn.execute("DESCRIBE documents").fetchall()
            if col[0].startswith("blob_")
        ]
        for col_name, _, _, _, _, _ in blob_columns:
            try:
                conn.execute(f"CREATE INDEX idx_{col_name} ON documents({col_name})")
            except:
                pass  # Игнорируем ошибки создания индексов для BLOB полей

        # Закрываем соединение
        conn.close()

        # Получаем размер файла
        file_size = os.path.getsize(db_file)
        print(f"✅ DuckDB база создана: {file_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"❌ Ошибка создания DuckDB: {e}")


def create_analysis_queries(db_file: str) -> None:
    """Создает SQL запросы для анализа данных"""
    print("📊 Создание SQL запросов для анализа...")

    try:
        conn = duckdb.connect(db_file)

        # Анализ по таблицам
        print("\n📋 Анализ по таблицам:")
        result = conn.execute(
            """
            SELECT 
                table_name,
                COUNT(*) as total_records,
                COUNT(DISTINCT id) as unique_documents
            FROM documents 
            GROUP BY table_name 
            ORDER BY total_records DESC
            LIMIT 10
        """,
        ).fetchall()

        for row in result:
            print(f"  {row[0]}: {row[1]:,} записей, {row[2]:,} документов")

        # Анализ BLOB полей
        print("\n📝 Анализ BLOB полей:")
        blob_columns = [
            col
            for col in conn.execute("DESCRIBE documents").fetchall()
            if col[0].startswith("blob_")
        ]
        for col_name, _, _, _, _, _ in blob_columns:
            result = conn.execute(
                f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT({col_name}) as non_null_records,
                    AVG(LENGTH({col_name})) as avg_length
                FROM documents 
                WHERE {col_name} IS NOT NULL
            """,
            ).fetchone()

            if result:
                print(
                    f"  {col_name}: {result[0]:,} записей, {result[1]:,} не пустых, средняя длина {result[2]:.1f}",
                )

        # Поиск цветов в BLOB полях
        print("\n🌸 Поиск цветов в BLOB полях:")
        colors = ["розов", "голуб", "красн", "бел", "желт"]
        for color in colors:
            result = conn.execute(
                f"""
                SELECT COUNT(*) as count
                FROM documents 
                WHERE blob_content LIKE '%{color}%'
            """,
            ).fetchone()

            if result and result[0] > 0:
                print(f"  {color}: {result[0]:,} упоминаний")

        # Поиск типов букетов
        print("\n💐 Поиск типов букетов:")
        bouquet_types = ["флористический", "моно", "яндекс", "композиция"]
        for bouquet_type in bouquet_types:
            result = conn.execute(
                f"""
                SELECT COUNT(*) as count
                FROM documents 
                WHERE blob_content LIKE '%{bouquet_type}%'
            """,
            ).fetchone()

            if result and result[0] > 0:
                print(f"  {bouquet_type}: {result[0]:,} упоминаний")

        # Поиск магазинов
        print("\n🏪 Поиск магазинов:")
        stores = ["ПЦ022", "ПЦ036", "Братиславский", "Южный"]
        for store in stores:
            result = conn.execute(
                f"""
                SELECT COUNT(*) as count
                FROM documents 
                WHERE blob_content LIKE '%{store}%'
            """,
            ).fetchone()

            if result and result[0] > 0:
                print(f"  {store}: {result[0]:,} упоминаний")

        conn.close()

    except Exception as e:
        print(f"❌ Ошибка создания SQL запросов: {e}")


def main():
    """Основная функция"""
    print("🚀 Конвертация JSON в Parquet + DuckDB")
    print("=" * 50)

    # Пути к файлам
    json_file = "all_available_data.json"
    parquet_file = "data/results/heroes_1c_data.parquet"
    db_file = "data/results/heroes_1c_data.duckdb"

    # Загружаем данные
    data = load_json_data(json_file)
    if not data:
        print("❌ Нет данных для конвертации")
        return

    # Конвертируем документы
    documents = data.get("documents", [])
    if not documents:
        print("❌ Нет документов для конвертации")
        return

    # Создаем DataFrame
    df = convert_documents_to_dataframe(documents)

    # Сохраняем в Parquet
    save_to_parquet(df, parquet_file)

    # Создаем DuckDB базу
    create_duckdb_database(parquet_file, db_file)

    # Создаем SQL запросы для анализа
    create_analysis_queries(db_file)

    print("\n✅ Конвертация завершена!")
    print(f"📁 Parquet файл: {parquet_file}")
    print(f"🗄️ DuckDB база: {db_file}")
    print("\n🔍 Для анализа используйте:")
    print(
        f"   python -c \"import duckdb; conn = duckdb.connect('{db_file}'); print(conn.execute('SELECT COUNT(*) FROM documents').fetchone())\"",
    )


if __name__ == "__main__":
    main()
