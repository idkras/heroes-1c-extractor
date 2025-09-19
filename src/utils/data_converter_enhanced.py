#!/usr/bin/env python3

"""
DataConverterEnhanced - улучшенный конвертер данных
Выделен из extract_all_available_data.py для упрощения основного кода
"""

# import json  # Не используется
import os
from typing import Any

import duckdb
import pandas as pd


class DataConverterEnhanced:
    """
    JTBD:
    Как система конвертации данных, я хочу предоставить улучшенную
    функциональность для конвертации результатов извлечения в различные
    форматы, чтобы упростить extract_all_available_data.py и обеспечить
    единый формат вывода.
    """

    def __init__(self) -> None:
        self.conversion_stats = {
            "parquet_files_created": 0,
            "duckdb_files_created": 0,
            "json_files_created": 0,
            "total_records_converted": 0,
        }

    def convert_to_parquet(
        self,
        results: dict[str, Any],
        output_dir: str = "data/results/parquet",
    ) -> bool:
        """
        JTBD:
        Как система конвертации в Parquet, я хочу конвертировать результаты
        извлечения в Parquet формат, чтобы обеспечить быстрый доступ к данным
        для анализа.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Конвертируем документы
            if results.get("documents"):
                documents_df = self._convert_documents_to_dataframe(
                    results["documents"],
                )
                parquet_file = os.path.join(output_dir, "documents_enhanced.parquet")
                documents_df.to_parquet(parquet_file, index=False)
                print(f"✅ Parquet файл создан: {parquet_file}")
                self.conversion_stats["parquet_files_created"] += 1
                self.conversion_stats["total_records_converted"] += len(documents_df)

            # Конвертируем справочники
            if results.get("references"):
                references_df = self._convert_references_to_dataframe(
                    results["references"],
                )
                parquet_file = os.path.join(output_dir, "references_enhanced.parquet")
                references_df.to_parquet(parquet_file, index=False)
                print(f"✅ Parquet файл создан: {parquet_file}")
                self.conversion_stats["parquet_files_created"] += 1
                self.conversion_stats["total_records_converted"] += len(references_df)

            # Конвертируем регистры
            if results.get("registers"):
                registers_df = self._convert_registers_to_dataframe(
                    results["registers"],
                )
                parquet_file = os.path.join(output_dir, "registers_enhanced.parquet")
                registers_df.to_parquet(parquet_file, index=False)
                print(f"✅ Parquet файл создан: {parquet_file}")
                self.conversion_stats["parquet_files_created"] += 1
                self.conversion_stats["total_records_converted"] += len(registers_df)

            return True

        except Exception as e:
            print(f"❌ Ошибка конвертации в Parquet: {e}")
            return False

    def convert_to_duckdb(
        self,
        results: dict[str, Any],
        output_dir: str = "data/results/duckdb",
    ) -> bool:
        """
        JTBD:
        Как система конвертации в DuckDB, я хочу конвертировать результаты
        извлечения в DuckDB базу данных, чтобы обеспечить быстрые аналитические
        запросы.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            duckdb_file = os.path.join(output_dir, "analysis_enhanced.duckdb")
            con = duckdb.connect(duckdb_file)

            # Загружаем документы
            if results.get("documents"):
                documents_df = self._convert_documents_to_dataframe(
                    results["documents"],
                )
                con.execute(
                    "CREATE OR REPLACE TABLE documents_enhanced AS SELECT * FROM documents_df",
                )
                print("✅ Таблица documents_enhanced создана в DuckDB")
                _ = documents_df  # Используем переменную для SQL запроса

            # Загружаем справочники
            if results.get("references"):
                references_df = self._convert_references_to_dataframe(
                    results["references"],
                )
                con.execute(
                    "CREATE OR REPLACE TABLE references_enhanced AS SELECT * FROM references_df",
                )
                print("✅ Таблица references_enhanced создана в DuckDB")
                _ = references_df  # Используем переменную для SQL запроса

            # Загружаем регистры
            if results.get("registers"):
                registers_df = self._convert_registers_to_dataframe(
                    results["registers"],
                )
                con.execute(
                    "CREATE OR REPLACE TABLE registers_enhanced AS SELECT * FROM registers_df",
                )
                print("✅ Таблица registers_enhanced создана в DuckDB")
                _ = registers_df  # Используем переменную для SQL запроса

            # Создаем индексы для быстрого поиска
            self._create_duckdb_indexes(con)

            # Выполняем аналитические запросы
            self._run_analytical_queries(con)

            con.close()
            print(f"✅ DuckDB база создана: {duckdb_file}")
            self.conversion_stats["duckdb_files_created"] += 1
            return True

        except Exception as e:
            print(f"❌ Ошибка конвертации в DuckDB: {e}")
            return False

    def _convert_documents_to_dataframe(
        self,
        documents: list[dict[str, Any]],
    ) -> pd.DataFrame:
        """Конвертировать документы в DataFrame"""
        documents_data = []

        for doc in documents:
            doc_data = {
                "id": doc.get("id", ""),
                "table_name": doc.get("table_name", ""),
                "row_index": doc.get("row_index", 0),
                "document_type": doc.get("document_type", ""),
                "document_number": doc.get("document_number", ""),
                "document_date": doc.get("document_date", ""),
                "total_amount": doc.get("total_amount", 0.0),
                "store_name": doc.get("store_name", ""),
                "store_code": doc.get("store_code", ""),
                "total_blobs": doc.get("extraction_stats", {}).get("total_blobs", 0),
                "successful_blobs": doc.get("extraction_stats", {}).get(
                    "successful",
                    0,
                ),
                "failed_blobs": doc.get("extraction_stats", {}).get("failed", 0),
            }

            # Добавляем поля из fields
            for field_name, value in doc.get("fields", {}).items():
                if isinstance(value, (str, int, float, bool)):
                    doc_data[f"field_{field_name}"] = value
                else:
                    doc_data[f"field_{field_name}"] = str(value)

            documents_data.append(doc_data)

        return pd.DataFrame(documents_data)

    def _convert_references_to_dataframe(
        self,
        references: list[dict[str, Any]],
    ) -> pd.DataFrame:
        """Конвертировать справочники в DataFrame"""
        references_data = []

        for ref in references:
            ref_data = {
                "id": ref.get("id", ""),
                "table_name": ref.get("table_name", ""),
                "row_index": ref.get("row_index", 0),
            }

            # Добавляем поля из fields
            for field_name, value in ref.get("fields", {}).items():
                if isinstance(value, (str, int, float, bool)):
                    ref_data[f"field_{field_name}"] = value
                else:
                    ref_data[f"field_{field_name}"] = str(value)

            references_data.append(ref_data)

        return pd.DataFrame(references_data)

    def _convert_registers_to_dataframe(
        self,
        registers: list[dict[str, Any]],
    ) -> pd.DataFrame:
        """Конвертировать регистры в DataFrame"""
        registers_data = []

        for reg in registers:
            reg_data = {
                "id": reg.get("id", ""),
                "table_name": reg.get("table_name", ""),
                "row_index": reg.get("row_index", 0),
            }

            # Добавляем поля из fields
            for field_name, value in reg.get("fields", {}).items():
                if isinstance(value, (str, int, float, bool)):
                    reg_data[f"field_{field_name}"] = value
                else:
                    reg_data[f"field_{field_name}"] = str(value)

            registers_data.append(reg_data)

        return pd.DataFrame(registers_data)

    def _create_duckdb_indexes(self, con: duckdb.DuckDBPyConnection) -> None:
        """Создать индексы в DuckDB для быстрого поиска"""
        try:
            # Индекс по table_name
            con.execute(
                "CREATE INDEX IF NOT EXISTS idx_table_name_enhanced ON documents_enhanced(table_name)",
            )

            # Индекс по document_type
            con.execute(
                "CREATE INDEX IF NOT EXISTS idx_document_type_enhanced ON documents_enhanced(document_type)",
            )

            # Индекс по total_amount
            con.execute(
                "CREATE INDEX IF NOT EXISTS idx_total_amount_enhanced ON documents_enhanced(total_amount)",
            )

            print("✅ Индексы созданы в DuckDB")
        except Exception as e:
            print(f"⚠️ Ошибка создания индексов: {e}")

    def _run_analytical_queries(self, con: duckdb.DuckDBPyConnection) -> None:
        """Выполнить аналитические запросы"""
        try:
            print("\n📊 Аналитические запросы (улучшенная версия):")

            # Статистика по таблицам
            result = con.execute(
                """
                SELECT
                    table_name,
                    COUNT(*) as total_documents,
                    SUM(total_blobs) as total_blobs,
                    AVG(total_blobs) as avg_blobs_per_doc
                FROM documents_enhanced
                GROUP BY table_name
                ORDER BY total_documents DESC
            """,
            ).fetchdf()
            print("📈 Статистика по таблицам:")
            print(result)

            # Топ таблиц по BLOB полям
            result = con.execute(
                """
                SELECT
                    table_name,
                    SUM(successful_blobs) as successful_blobs,
                    SUM(failed_blobs) as failed_blobs,
                    ROUND(SUM(successful_blobs) * 100.0 / (SUM(successful_blobs) + SUM(failed_blobs)), 2) as success_rate
                FROM documents_enhanced
                WHERE successful_blobs + failed_blobs > 0
                GROUP BY table_name
                ORDER BY successful_blobs DESC
                LIMIT 10
            """,
            ).fetchdf()
            print("\n🏆 Топ таблиц по BLOB полям:")
            print(result)

        except Exception as e:
            print(f"⚠️ Ошибка выполнения аналитических запросов: {e}")

    def get_conversion_stats(self) -> dict[str, Any]:
        """Получить статистику конвертации"""
        return self.conversion_stats.copy()

    def reset_stats(self) -> None:
        """Сбросить статистику конвертации"""
        self.conversion_stats = {
            "parquet_files_created": 0,
            "duckdb_files_created": 0,
            "json_files_created": 0,
            "total_records_converted": 0,
        }
