#!/usr/bin/env python3
"""
1C MCP Server

MCP сервер для извлечения данных из 1С баз данных.
Использует FastMCP для быстрой разработки MCP инструментов.
Включает интеграцию с 1C через onec_dtools и pyodbc.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ПРОВЕРКА АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ ПЕРЕД ИНИЦИАЛИЗАЦИЕЙ
def check_command_line_args() -> None:
    """Проверяет аргументы командной строки и выходит если нужно"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--help" or arg == "-h":
            print("1C MCP Server v1.0.0")
            print("Usage: python mcp_server/1c_mcp_server.py [OPTIONS]")
            print("")
            print("Options:")
            print("  --help, -h     Show this help message")
            print("  --version, -v  Show version information")
            print("  --test         Show registered tools and exit")
            print("  --list-tools   List all available MCP tools")
            print("")
            print("Examples:")
            print(
                "  python mcp_server/1c_mcp_server.py              # Start MCP server"
            )
            print(
                "  python mcp_server/1c_mcp_server.py --test       # Show tools and exit"
            )
            print("  python mcp_server/1c_mcp_server.py --list-tools # List all tools")
            print("  mcp run mcp_server/1c_mcp_server.py             # Run via MCP CLI")
            sys.exit(0)

        elif arg == "--version" or arg == "-v":
            print("1C MCP Server v1.0.0")
            print("Protocol: MCP v1.0")
            print("Transport: stdio")
            sys.exit(0)

        elif arg == "--test":
            print(
                "Registered tools: extract_1c_documents, create_flat_table, save_to_parquet, analyze_parquet_files, analyze_document_structure, search_color_data, extract_all_critical_tables"
            )
            sys.exit(0)

        elif arg == "--list-tools":
            tools_list = [
                "extract_1c_documents",
                "create_flat_table",
                "save_to_parquet",
                "analyze_parquet_files",
                "analyze_document_structure",
                "search_color_data",
                "extract_all_critical_tables",
            ]

            print("Available MCP Tools:")
            for i, tool in enumerate(tools_list, 1):
                print(f"  {i:2d}. {tool}")
            print(f"\nTotal: {len(tools_list)} tools")
            sys.exit(0)

        elif arg.startswith("--"):
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            sys.exit(1)


# Проверяем аргументы СРАЗУ только если это не импорт для тестов
if __name__ == "__main__" or len(sys.argv) > 1:
    check_command_line_args()

# Clean import setup - using proper package structure
# Add project root to Python path for imports
current_file = Path(__file__)
project_root = current_file.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP

# Инициализация FastMCP сервера
mcp = FastMCP("1c_mcp")

# Global variables for database connection and extractor
db_connector = None
document_extractor = None


def _connect_to_1c_database(database_path: str) -> bool:
    """
    Примитив подключения к базе данных 1С
    Возвращает True если подключение успешно, False если ошибка
    """
    global db_connector, document_extractor

    try:
        # Импортируем необходимые модули
        from src.extractors.simple_document_extractor import (
            DatabaseConnector,
            SimpleDocumentExtractor,
        )

        # Создаем подключение
        db_connector = DatabaseConnector(database_path)
        db_connector.connect()

        # Создаем экстрактор
        document_extractor = SimpleDocumentExtractor(db_connector)

        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False


@mcp.tool()
def extract_1c_documents(
    table_name: str, database_path: str, limit: Optional[int] = None
) -> str:
    """
    JTBD:
    Как инструмент извлечения документов, я хочу извлечь документы из указанной таблицы,
    чтобы получить данные для анализа.

    Args:
        table_name: Имя таблицы для извлечения
        database_path: Путь к файлу базы данных 1С (.1CD)
        limit: Максимальное количество документов (None = все)

    Returns:
        Словарь с извлеченными документами
    """
    try:
        # Подключаемся к базе данных
        if not _connect_to_1c_database(database_path):
            return json.dumps(
                {
                    "success": False,
                    "error": "Не удалось подключиться к базе данных 1С",
                    "table_name": table_name,
                    "database_path": database_path,
                },
                ensure_ascii=False,
            )

        # Извлекаем документы
        if document_extractor is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Экстрактор документов не инициализирован",
                    "table_name": table_name,
                },
                ensure_ascii=False,
            )

        # Выполняем извлечение
        extraction_result = document_extractor.extract_documents(
            table_name, limit=limit
        )

        # Проверяем, что result - это словарь
        if isinstance(extraction_result, list):
            result = {"documents": extraction_result, "extraction_stats": {}}
        elif isinstance(extraction_result, dict):
            result = extraction_result
        else:
            result = {"documents": [], "extraction_stats": {}}

        return json.dumps(
            {
                "success": True,
                "table_name": table_name,
                "documents_count": len(result.get("documents", [])),
                "documents": result.get("documents", []),
                "extraction_stats": result.get("extraction_stats", {}),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in extract_1c_documents: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка извлечения документов: {str(e)}",
                "table_name": table_name,
                "database_path": database_path,
            },
            ensure_ascii=False,
        )


@mcp.tool()
def create_flat_table(documents_list: list, table_names: list) -> str:
    """
    JTBD:
    Как инструмент создания плоской таблицы, я хочу объединить документы из разных таблиц,
    чтобы создать единую структуру данных для анализа.

    Args:
        documents_list: Список списков документов
        table_names: Список имен таблиц

    Returns:
        Словарь с плоской таблицей
    """
    try:
        from src.extractors.flat_table_extractor import FlatTableExtractor

        # Создаем экстрактор плоских таблиц
        flat_extractor = FlatTableExtractor(db_path="")

        # Создаем плоскую таблицу
        result = flat_extractor.extract_flat_table()

        return json.dumps(
            {
                "success": True,
                "flat_table": result.get("flat_table", []),
                "table_names": table_names,
                "total_records": len(result.get("flat_table", [])),
                "creation_stats": result.get("creation_stats", {}),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in create_flat_table: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка создания плоской таблицы: {str(e)}",
                "table_names": table_names,
            },
            ensure_ascii=False,
        )


@mcp.tool()
def save_to_parquet(data: list, output_path: str) -> str:
    """
    JTBD:
    Как инструмент сохранения в Parquet, я хочу сохранить данные в формате Parquet,
    чтобы обеспечить эффективное хранение и быстрый доступ к данным.

    Args:
        data: Данные для сохранения
        output_path: Путь для сохранения файла

    Returns:
        Словарь с результатом сохранения
    """
    try:
        import pandas as pd
        import os

        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Создаем DataFrame
        df = pd.DataFrame(data)

        # ИСПРАВЛЕНО: Конвертируем BLOB поля (bytes) в hex-строки для Parquet
        for col in df.select_dtypes(include=["object"]).columns:
            if df[col].apply(lambda x: isinstance(x, bytes)).any():
                df[col] = df[col].apply(
                    lambda x: x.hex() if isinstance(x, bytes) else x
                )

        # Сохраняем в Parquet
        df.to_parquet(output_path, index=False)

        return json.dumps(
            {
                "success": True,
                "output_path": output_path,
                "records_saved": len(data),
                "file_size_mb": round(
                    Path(output_path).stat().st_size / (1024 * 1024), 2
                ),
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in save_to_parquet: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка сохранения в Parquet: {str(e)}",
                "output_path": output_path,
            },
            ensure_ascii=False,
        )


@mcp.tool()
def analyze_parquet_files(directory_path: str) -> str:
    """
    JTBD:
    Как инструмент анализа Parquet файлов, я хочу получить полную информацию о всех файлах в директории,
    чтобы понять структуру данных без ручного анализа каждого файла.

    Args:
        directory_path: Путь к директории с Parquet файлами

    Returns:
        Словарь с анализом всех файлов
    """
    try:
        import glob
        import os
        import duckdb

        # Создаем временное соединение
        con = duckdb.connect(":memory:")

        # Находим все Parquet файлы
        parquet_files = glob.glob(f"{directory_path}/*.parquet")

        if not parquet_files:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Parquet файлы не найдены в {directory_path}",
                    "directory_path": directory_path,
                },
                ensure_ascii=False,
            )

        # Анализируем каждый файл
        files_analysis = []
        total_size = 0

        for file_path in sorted(parquet_files):
            try:
                file_info = {
                    "name": os.path.basename(file_path),
                    "path": file_path,
                    "size_bytes": os.path.getsize(file_path),
                    "size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
                }

                # Получаем количество строк
                row_count = con.execute(
                    f"SELECT COUNT(*) FROM read_parquet('{file_path}')"
                ).fetchone()[0]
                file_info["records_count"] = row_count

                # Получаем информацию о колонках
                if row_count > 0:
                    columns_info = con.execute(
                        f"DESCRIBE SELECT * FROM read_parquet('{file_path}') LIMIT 1"
                    ).fetchall()
                    file_info["columns_count"] = len(columns_info)
                    file_info["columns"] = [col[0] for col in columns_info]

                    # Получаем пример данных
                    try:
                        sample_data = con.execute(
                            f"SELECT * FROM read_parquet('{file_path}') LIMIT 1"
                        ).fetchall()
                        if sample_data:
                            file_info["sample_data"] = list(
                                sample_data[0][:3]
                            )  # Первые 3 поля
                    except Exception as e:
                        file_info["sample_data"] = (
                            f"Ошибка получения примера: {str(e)[:50]}"
                        )
                else:
                    file_info["columns_count"] = 0
                    file_info["columns"] = []
                    file_info["sample_data"] = "Файл пустой"

                files_analysis.append(file_info)
                size_bytes = file_info.get("size_bytes", 0)
                if isinstance(size_bytes, (int, float)):
                    total_size += size_bytes

            except Exception as e:
                files_analysis.append(
                    {
                        "name": os.path.basename(file_path),
                        "path": file_path,
                        "error": f"Ошибка анализа: {str(e)[:100]}",
                    }
                )

        return json.dumps(
            {
                "success": True,
                "directory_path": directory_path,
                "total_files": len(parquet_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "files_analysis": files_analysis,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in analyze_parquet_files: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка анализа Parquet файлов: {str(e)}",
                "directory_path": directory_path,
            },
            ensure_ascii=False,
        )


@mcp.tool()
def analyze_document_structure(file_path: str) -> str:
    """
    JTBD:
    Как инструмент анализа структуры документа, я хочу получить детальную информацию о структуре Parquet файла,
    чтобы понять типы данных и содержимое полей без ручного анализа.

    Args:
        file_path: Путь к Parquet файлу

    Returns:
        Словарь с анализом структуры документа
    """
    try:
        import duckdb

        # Создаем временное соединение
        con = duckdb.connect(":memory:")

        # Проверяем существование файла
        if not os.path.exists(file_path):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Файл не найден: {file_path}",
                    "file_path": file_path,
                },
                ensure_ascii=False,
            )

        # Получаем базовую информацию
        row_count = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{file_path}')"
        ).fetchone()[0]

        if row_count == 0:
            return json.dumps(
                {
                    "success": True,
                    "file_path": file_path,
                    "records_count": 0,
                    "message": "Файл пустой",
                },
                ensure_ascii=False,
            )

        # Получаем структуру колонок
        columns_info = con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{file_path}') LIMIT 1"
        ).fetchall()

        # Анализируем содержимое полей
        fields_analysis = {}
        blob_analysis = {}

        # Проверяем наличие полей fields и blob_fields
        if "fields" in [col[0] for col in columns_info]:
            try:
                sample_fields = con.execute(
                    f"SELECT fields FROM read_parquet('{file_path}') LIMIT 1"
                ).fetchone()[0]
                if sample_fields and isinstance(sample_fields, dict):
                    fields_analysis = {
                        "count": len(sample_fields),
                        "sample_fields": dict(
                            list(sample_fields.items())[:3]
                        ),  # Первые 3 поля
                    }
            except Exception as e:
                fields_analysis = {"error": f"Ошибка анализа fields: {str(e)[:50]}"}

        if "blob_fields" in [col[0] for col in columns_info]:
            try:
                sample_blobs = con.execute(
                    f"SELECT blob_fields FROM read_parquet('{file_path}') LIMIT 1"
                ).fetchone()[0]
                if sample_blobs and isinstance(sample_blobs, dict):
                    blob_analysis = {
                        "count": len(sample_blobs),
                        "sample_blobs": dict(
                            list(sample_blobs.items())[:3]
                        ),  # Первые 3 поля
                    }
            except Exception as e:
                blob_analysis = {"error": f"Ошибка анализа blob_fields: {str(e)[:50]}"}

        # Поиск данных о цветах
        color_analysis = {}
        if "blob_content" in [col[0] for col in columns_info]:
            try:
                color_search = con.execute(
                    f"""
                    SELECT 
                        COUNT(*) as total_records,
                        SUM(CASE WHEN blob_content LIKE '%цвет%' OR blob_content LIKE '%флор%' OR blob_content LIKE '%rose%' OR blob_content LIKE '%тюльпан%' OR blob_content LIKE '%букет%' THEN 1 ELSE 0 END) as color_records
                    FROM read_parquet('{file_path}')
                """
                ).fetchone()
                color_analysis = {
                    "total_records": color_search[0],
                    "color_records": color_search[1],
                    "has_color_data": color_search[1] > 0,
                }
            except Exception as e:
                color_analysis = {"error": f"Ошибка поиска цветов: {str(e)[:50]}"}

        return json.dumps(
            {
                "success": True,
                "file_path": file_path,
                "records_count": row_count,
                "columns_count": len(columns_info),
                "columns": [col[0] for col in columns_info],
                "fields_analysis": fields_analysis,
                "blob_analysis": blob_analysis,
                "color_analysis": color_analysis,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in analyze_document_structure: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка анализа структуры документа: {str(e)}",
                "file_path": file_path,
            },
            ensure_ascii=False,
        )


@mcp.tool()
def search_color_data(file_path: str, keywords: Optional[list] = None) -> str:
    """
    JTBD:
    Как инструмент поиска данных о цветах, я хочу найти все записи содержащие информацию о цветах,
    чтобы получить конкретные примеры данных без ручного поиска.

    Args:
        file_path: Путь к Parquet файлу
        keywords: Список ключевых слов для поиска (по умолчанию: цвет, флор, rose, тюльпан, букет)

    Returns:
        Словарь с найденными данными о цветах
    """
    try:
        import duckdb

        if keywords is None:
            keywords = ["цвет", "флор", "rose", "тюльпан", "букет"]

        # Создаем временное соединение
        con = duckdb.connect(":memory:")

        # Проверяем существование файла
        if not os.path.exists(file_path):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Файл не найден: {file_path}",
                    "file_path": file_path,
                },
                ensure_ascii=False,
            )

        # Строим SQL запрос для поиска
        where_conditions = []
        for keyword in keywords:
            where_conditions.append(f"blob_content LIKE '%{keyword}%'")

        where_clause = " OR ".join(where_conditions)

        # Ищем записи с цветами
        color_records = con.execute(
            f"""
            SELECT table_name, document_type, blob_content
            FROM read_parquet('{file_path}')
            WHERE {where_clause}
            LIMIT 10
        """
        ).fetchall()

        # Получаем общую статистику
        total_records = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{file_path}')"
        ).fetchone()[0]
        color_count = con.execute(
            f"""
            SELECT COUNT(*) FROM read_parquet('{file_path}')
            WHERE {where_clause}
        """
        ).fetchone()[0]

        return json.dumps(
            {
                "success": True,
                "file_path": file_path,
                "keywords": keywords,
                "total_records": total_records,
                "color_records_found": color_count,
                "sample_records": [
                    {
                        "table_name": record[0],
                        "document_type": record[1],
                        "blob_content": (
                            record[2][:200] + "..."
                            if len(record[2]) > 200
                            else record[2]
                        ),
                    }
                    for record in color_records
                ],
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in search_color_data: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка поиска данных о цветах: {str(e)}",
                "file_path": file_path,
                "keywords": keywords,
            },
            ensure_ascii=False,
        )


@mcp.tool()
def extract_all_critical_tables(database_path: str) -> str:
    """
    JTBD:
    Как инструмент извлечения всех критических таблиц, я хочу извлечь ВСЕ данные
    из критических таблиц без лимитов, чтобы получить полную картину данных.

    Args:
        database_path: Путь к файлу базы данных 1С (.1CD)

    Returns:
        Словарь с результатами извлечения всех критических таблиц
    """
    try:
        # Критические таблицы для извлечения
        critical_tables = [
            "_DOCUMENT138",  # Поступление товаров (861K записей)
            "_DOCUMENT137",  # Розничные продажи (227K записей)
            "_DOCUMENT138_VT3118",  # Табличные части поступления
        ]

        results = {}
        total_records = 0

        for table_name in critical_tables:
            print(f"🔍 Извлечение из таблицы: {table_name}")

            # Извлекаем ВСЕ данные без лимитов
            extraction_result = extract_1c_documents(
                table_name, database_path, limit=None
            )
            result_data = json.loads(extraction_result)

            if result_data.get("success"):
                records_count = result_data.get("documents_count", 0)
                results[table_name] = {
                    "success": True,
                    "records_count": records_count,
                    "documents": result_data.get("documents", []),
                }
                total_records += records_count
                print(f"✅ {table_name}: {records_count} записей")
            else:
                results[table_name] = {
                    "success": False,
                    "error": result_data.get("error", "Unknown error"),
                }
                print(f"❌ {table_name}: {result_data.get('error', 'Unknown error')}")

        return json.dumps(
            {
                "success": True,
                "critical_tables": results,
                "total_records": total_records,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in extract_all_critical_tables: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка извлечения критических таблиц: {str(e)}",
                "database_path": database_path,
            },
            ensure_ascii=False,
        )


@mcp.resource(uri="1c_database_info/{database_path}")
def get_1c_database_info(database_path: str) -> str:
    """
    JTBD:
    Как ресурс информации о базе данных, я хочу получить метаданные о базе данных 1С,
    чтобы понять структуру и доступные таблицы.

    Args:
        database_path: Путь к файлу базы данных 1С (.1CD)

    Returns:
        Словарь с информацией о базе данных
    """
    try:
        # Подключаемся к базе данных
        if not _connect_to_1c_database(database_path):
            return json.dumps(
                {
                    "success": False,
                    "error": "Не удалось подключиться к базе данных 1С",
                    "database_path": database_path,
                },
                ensure_ascii=False,
            )

        # Получаем информацию о базе данных
        if db_connector is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Подключение к базе данных не инициализировано",
                    "database_path": database_path,
                },
                ensure_ascii=False,
            )

        # Получаем список таблиц
        tables_info = db_connector.get_table("")

        return json.dumps(
            {
                "success": True,
                "database_path": database_path,
                "tables_count": len(tables_info),
                "tables": tables_info,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Error in get_1c_database_info: {e}")
        return json.dumps(
            {
                "success": False,
                "error": f"Ошибка получения информации о базе данных: {str(e)}",
                "database_path": database_path,
            },
            ensure_ascii=False,
        )


# Добавляем метод run() для совместимости с MCP CLI
def run() -> None:
    """Run the MCP server - compatibility method for MCP CLI"""
    # MCP CLI не передает аргументы, поэтому запускаем сервер напрямую
    main()


# Добавляем объект сервера для MCP CLI
server = mcp


def main() -> None:
    """Главная функция запуска сервера"""

    # Аргументы уже проверены в начале файла

    # Обычный режим - запуск MCP сервера
    logger.info("Starting 1C MCP Server with FastMCP")
    logger.info(f"Server name: {mcp.name}")

    # Логируем доступные инструменты
    tools = "extract_1c_documents, create_flat_table, save_to_parquet, analyze_parquet_files, analyze_document_structure, search_color_data, extract_all_critical_tables"
    logger.info(f"Available tools: {tools}")

    # Запуск сервера через stdio (стандарт MCP)
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
