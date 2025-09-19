#!/usr/bin/env python3
"""
Google Sheets MCP Server

JTBD: Как MCP сервер, я хочу предоставлять инструменты для работы с Google Sheets,
чтобы пользователи могли читать, записывать и управлять данными в таблицах.

Использует Google Service Account JSON из Mac Keychain для аутентификации.
"""

import json
import logging
import sys
from typing import Any, Optional

# MCP imports
from mcp.server.fastmcp import FastMCP

# Инициализация MCP сервера
mcp = FastMCP("google-sheets-mcp")


# ПРОВЕРКА АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ ПЕРЕД ИНИЦИАЛИЗАЦИЕЙ
def check_command_line_args():
    """Проверяет аргументы командной строки и выходит если нужно"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--help" or arg == "-h":
            print("Google Sheets MCP Server v1.0.0")
            print("Usage: python mcp_google_sheets_server.py [OPTIONS]")
            print("")
            print("Options:")
            print("  --help, -h     Show this help message")
            print("  --version, -v  Show version information")
            print("  --test         Show registered tools and exit")
            print("  --list-tools   List all available MCP tools")
            sys.exit(0)

        elif arg == "--version" or arg == "-v":
            print("Google Sheets MCP Server v1.0.0")
            print("Protocol: MCP v1.0")
            print("Transport: stdio")
            sys.exit(0)

        elif arg == "--test":
            print(
                "Registered tools: google_sheets_read_spreadsheet, google_sheets_write_data, google_sheets_list_spreadsheets, google_sheets_get_sheet_info, google_sheets_create_spreadsheet, google_sheets_delete_spreadsheet, google_sheets_share_spreadsheet, google_sheets_add_worksheet, google_sheets_delete_worksheet, google_sheets_rename_worksheet, google_sheets_copy_worksheet, google_sheets_get_formulas, google_sheets_batch_update, google_sheets_export_to_csv, google_sheets_import_from_csv"
            )
            sys.exit(0)

        elif arg == "--list-tools":
            tools_list = [
                "google_sheets_read_spreadsheet",
                "google_sheets_write_data",
                "google_sheets_list_spreadsheets",
                "google_sheets_get_sheet_info",
                "google_sheets_create_spreadsheet",
                "google_sheets_delete_spreadsheet",
                "google_sheets_share_spreadsheet",
                "google_sheets_add_worksheet",
                "google_sheets_delete_worksheet",
                "google_sheets_rename_worksheet",
                "google_sheets_copy_worksheet",
                "google_sheets_get_formulas",
                "google_sheets_batch_update",
                "google_sheets_export_to_csv",
                "google_sheets_import_from_csv",
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


# КРИТИЧЕСКИ ВАЖНО: Проверяем аргументы СРАЗУ при импорте модуля
check_command_line_args()

from mcp.server.fastmcp import FastMCP

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация MCP сервера
mcp = FastMCP("Google Sheets")


def get_service_account_key() -> Optional[dict[str, Any]]:
    """Получить Service Account ключ через credentials_manager"""
    try:
        # Import credentials_manager
        from credentials_manager import credentials_manager  # type: ignore

        # Get Service Account JSON from credentials_manager
        result = credentials_manager.get_credential("google_service_account_json")
        if not result.success:
            logger.error(f"❌ Ошибка получения Service Account JSON: {result.error}")
            return None

        if result.value is None:
            logger.error("❌ Service Account JSON value is None")
            return None

        return json.loads(result.value)

    except Exception as e:
        logger.error(f"❌ Ошибка получения ключа: {e}")
        return None


def get_google_sheets_client():
    """Получить авторизованный клиент Google Sheets"""
    try:
        import gspread  # type: ignore
        from oauth2client.service_account import (
            ServiceAccountCredentials,  # type: ignore
        )

        # Получить ключ из Keychain
        service_account = get_service_account_key()
        if not service_account:
            raise Exception("Не удалось получить Service Account ключ")

        # Настроить области доступа
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Создать учетные данные
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            service_account, scope
        )

        # Авторизоваться
        client = gspread.authorize(credentials)
        return client

    except ImportError:
        logger.error("❌ Не установлены необходимые библиотеки: gspread, oauth2client")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка создания клиента: {e}")
        return None


@mcp.tool()
def google_sheets_read_spreadsheet(
    spreadsheet_id: str, range_name: str = "A1:Z100"
) -> str:
    """
    Читать данные из Google Sheets

    Args:
        spreadsheet_id: ID таблицы Google Sheets
        range_name: Диапазон ячеек (например, "A1:Z100" или "Sheet1!A1:Z100")

    Returns:
        JSON строка с данными из таблицы
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Получить данные
        if "!" in range_name:
            # Указан конкретный лист
            sheet_name, cell_range = range_name.split("!", 1)
            worksheet = spreadsheet.worksheet(sheet_name)
            values = worksheet.get(cell_range)
        else:
            # Использовать первый лист
            worksheet = spreadsheet.sheet1
            values = worksheet.get(range_name)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "data": values,
                "rows_count": len(values) if values else 0,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка чтения таблицы: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_write_data(spreadsheet_id: str, range_name: str, data: str) -> str:
    """
    Записать данные в Google Sheets

    Args:
        spreadsheet_id: ID таблицы Google Sheets
        range_name: Диапазон ячеек (например, "A1" или "Sheet1!A1")
        data: JSON строка с данными для записи

    Returns:
        JSON строка с результатом операции
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Парсить данные
        try:
            data_list = json.loads(data)
        except json.JSONDecodeError:
            return json.dumps(
                {
                    "success": False,
                    "error": "Неверный формат данных. Ожидается JSON строка",
                },
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Определить лист и диапазон
        if "!" in range_name:
            sheet_name, cell_range = range_name.split("!", 1)
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.sheet1
            cell_range = range_name

        # Записать данные
        if (
            isinstance(data_list, list)
            and len(data_list) > 0
            and isinstance(data_list[0], list)
        ):
            # Массив массивов - записать в диапазон
            worksheet.update(cell_range, data_list)
        else:
            # Одиночное значение или массив - записать в ячейку
            worksheet.update(cell_range, data_list)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "data_written": data_list,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка записи в таблицу: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_list_spreadsheets() -> str:
    """
    Получить список доступных Google Sheets

    Returns:
        JSON строка со списком таблиц
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Получить список таблиц с таймаутом
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Operation timed out")

        # Устанавливаем таймаут 30 секунд
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)

        try:
            spreadsheets = client.openall()
            signal.alarm(0)  # Отключаем таймаут

            result = []
            for spreadsheet in spreadsheets:
                result.append(
                    {
                        "id": spreadsheet.id,
                        "title": spreadsheet.title,
                        "url": spreadsheet.url,
                        "sheets_count": len(spreadsheet.worksheets()),
                    }
                )

        except TimeoutError:
            signal.alarm(0)  # Отключаем таймаут
            return json.dumps(
                {
                    "success": False,
                    "error": "Операция превысила таймаут 30 секунд. Возможно, у вас слишком много таблиц.",
                    "partial_result": True,
                },
                ensure_ascii=False,
            )

        return json.dumps(
            {"success": True, "spreadsheets": result, "count": len(result)},
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка получения списка таблиц: {e}")
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


@mcp.tool()
def google_sheets_get_sheet_info(spreadsheet_id: str) -> str:
    """
    Получить информацию о таблице Google Sheets

    Args:
        spreadsheet_id: ID таблицы Google Sheets

    Returns:
        JSON строка с информацией о таблице
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Получить информацию о листах
        worksheets = []
        for worksheet in spreadsheet.worksheets():
            worksheets.append(
                {
                    "title": worksheet.title,
                    "id": worksheet.id,
                    "row_count": worksheet.row_count,
                    "col_count": worksheet.col_count,
                    "url": worksheet.url,
                }
            )

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "title": spreadsheet.title,
                "url": spreadsheet.url,
                "worksheets": worksheets,
                "worksheets_count": len(worksheets),
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о таблице: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_create_spreadsheet(title: str) -> str:
    """
    Создать новую таблицу Google Sheets

    Args:
        title: Название новой таблицы

    Returns:
        JSON строка с информацией о созданной таблице
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Создать новую таблицу
        spreadsheet = client.create(title)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet.id,
                "title": spreadsheet.title,
                "url": spreadsheet.url,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка создания таблицы: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "title": title}, ensure_ascii=False
        )


@mcp.tool()
def google_sheets_delete_spreadsheet(spreadsheet_id: str) -> str:
    """
    Удалить Google Sheets таблицу

    Args:
        spreadsheet_id: ID таблицы для удаления

    Returns:
        JSON строка с результатом удаления
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Удалить таблицу (требует специальных прав)
        # В gspread нет прямого метода удаления, используем Drive API
        from googleapiclient.discovery import build  # type: ignore  # noqa
        from google.oauth2.service_account import Credentials  # type: ignore

        # Получить credentials
        service_account_key = get_service_account_key()
        if not service_account_key:
            return json.dumps(
                {"success": False, "error": "Не удалось получить Service Account ключ"},
                ensure_ascii=False,
            )

        # Создать Drive API клиент
        credentials = Credentials.from_service_account_info(
            service_account_key, scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=credentials)

        # Удалить файл
        drive_service.files().delete(fileId=spreadsheet_id).execute()

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "message": "Таблица успешно удалена",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка удаления таблицы: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_share_spreadsheet(
    spreadsheet_id: str, email: str, role: str = "reader"
) -> str:
    """
    Поделиться Google Sheets таблицей

    Args:
        spreadsheet_id: ID таблицы
        email: Email пользователя для предоставления доступа
        role: Роль доступа (reader, writer, owner)

    Returns:
        JSON строка с результатом предоставления доступа
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Предоставить доступ
        spreadsheet.share(email, perm_type="user", role=role)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "email": email,
                "role": role,
                "message": f"Доступ предоставлен пользователю {email} с ролью {role}",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка предоставления доступа: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_add_worksheet(
    spreadsheet_id: str, worksheet_name: str, rows: int = 1000, cols: int = 26
) -> str:
    """
    Добавить новый лист в Google Sheets таблицу

    Args:
        spreadsheet_id: ID таблицы
        worksheet_name: Название нового листа
        rows: Количество строк (по умолчанию 1000)
        cols: Количество столбцов (по умолчанию 26)

    Returns:
        JSON строка с результатом добавления листа
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Добавить новый лист
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name, rows=rows, cols=cols
        )

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "worksheet_name": worksheet_name,
                "worksheet_id": worksheet.id,
                "rows": rows,
                "cols": cols,
                "message": f"Лист '{worksheet_name}' успешно добавлен",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка добавления листа: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_delete_worksheet(spreadsheet_id: str, worksheet_name: str) -> str:
    """
    Удалить лист из Google Sheets таблицы

    Args:
        spreadsheet_id: ID таблицы
        worksheet_name: Название листа для удаления

    Returns:
        JSON строка с результатом удаления листа
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Найти и удалить лист
        worksheet = spreadsheet.worksheet(worksheet_name)
        spreadsheet.del_worksheet(worksheet)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "worksheet_name": worksheet_name,
                "message": f"Лист '{worksheet_name}' успешно удален",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка удаления листа: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_rename_worksheet(
    spreadsheet_id: str, old_name: str, new_name: str
) -> str:
    """
    Переименовать лист в Google Sheets таблице

    Args:
        spreadsheet_id: ID таблицы
        old_name: Текущее название листа
        new_name: Новое название листа

    Returns:
        JSON строка с результатом переименования
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Найти и переименовать лист
        worksheet = spreadsheet.worksheet(old_name)
        worksheet.update_title(new_name)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "old_name": old_name,
                "new_name": new_name,
                "message": f"Лист переименован с '{old_name}' на '{new_name}'",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка переименования листа: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_copy_worksheet(
    spreadsheet_id: str, source_worksheet_name: str, new_worksheet_name: str
) -> str:
    """
    Копировать лист в Google Sheets таблице

    Args:
        spreadsheet_id: ID таблицы
        source_worksheet_name: Название исходного листа
        new_worksheet_name: Название нового листа

    Returns:
        JSON строка с результатом копирования
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Найти исходный лист
        source_worksheet = spreadsheet.worksheet(source_worksheet_name)

        # Копировать лист
        new_worksheet = spreadsheet.duplicate_sheet(
            source_worksheet.id,
            insert_sheet_index=None,
            new_sheet_name=new_worksheet_name,
        )

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "source_worksheet_name": source_worksheet_name,
                "new_worksheet_name": new_worksheet_name,
                "new_worksheet_id": new_worksheet.id,
                "message": f"Лист '{source_worksheet_name}' скопирован как '{new_worksheet_name}'",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка копирования листа: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_get_formulas(spreadsheet_id: str, range_name: str = "A1:Z100") -> str:
    """
    Получить формулы из Google Sheets таблицы

    Args:
        spreadsheet_id: ID таблицы
        range_name: Диапазон ячеек (по умолчанию A1:Z100)

    Returns:
        JSON строка с формулами
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Определить лист и диапазон
        if "!" in range_name:
            sheet_name, cell_range = range_name.split("!", 1)
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.sheet1
            cell_range = range_name

        # Получить формулы
        formulas = worksheet.get(cell_range, value_render_option="FORMULA")

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "formulas": formulas,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка получения формул: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_batch_update(spreadsheet_id: str, updates: str) -> str:
    """
    Выполнить пакетное обновление Google Sheets таблицы

    Args:
        spreadsheet_id: ID таблицы
        updates: JSON строка с массивом обновлений

    Returns:
        JSON строка с результатом пакетного обновления
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Парсить обновления
        try:
            updates_list = json.loads(updates)
        except json.JSONDecodeError:
            return json.dumps(
                {
                    "success": False,
                    "error": "Неверный формат обновлений. Ожидается JSON массив",
                },
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Выполнить пакетное обновление
        results = []
        for update in updates_list:
            if "range" in update and "values" in update:
                worksheet = spreadsheet.worksheet(update.get("sheet", "Sheet1"))
                worksheet.update(update["range"], update["values"])
                results.append({"range": update["range"], "status": "updated"})

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "updates_count": len(results),
                "results": results,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка пакетного обновления: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_export_to_csv(
    spreadsheet_id: str, worksheet_name: str = "Sheet1"
) -> str:
    """
    Экспортировать Google Sheets лист в CSV формат

    Args:
        spreadsheet_id: ID таблицы
        worksheet_name: Название листа для экспорта

    Returns:
        JSON строка с CSV данными
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Получить лист
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Получить все данные
        all_values = worksheet.get_all_values()

        # Конвертировать в CSV
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(all_values)
        csv_data = output.getvalue()
        output.close()

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "worksheet_name": worksheet_name,
                "csv_data": csv_data,
                "rows_count": len(all_values),
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка экспорта в CSV: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


@mcp.tool()
def google_sheets_import_from_csv(
    spreadsheet_id: str,
    csv_data: str,
    worksheet_name: str = "Sheet1",
    start_cell: str = "A1",
) -> str:
    """
    Импортировать CSV данные в Google Sheets лист

    Args:
        spreadsheet_id: ID таблицы
        csv_data: CSV данные для импорта
        worksheet_name: Название листа для импорта
        start_cell: Начальная ячейка для импорта

    Returns:
        JSON строка с результатом импорта
    """
    try:
        client = get_google_sheets_client()
        if not client:
            return json.dumps(
                {"success": False, "error": "Не удалось создать клиент Google Sheets"},
                ensure_ascii=False,
            )

        # Открыть таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Получить лист
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Парсить CSV данные
        import csv
        import io

        csv_reader = csv.reader(io.StringIO(csv_data))
        data = list(csv_reader)

        # Записать данные
        worksheet.update(start_cell, data)

        return json.dumps(
            {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "worksheet_name": worksheet_name,
                "start_cell": start_cell,
                "rows_imported": len(data),
                "message": f"Импортировано {len(data)} строк CSV данных",
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"❌ Ошибка импорта CSV: {e}")
        return json.dumps(
            {"success": False, "error": str(e), "spreadsheet_id": spreadsheet_id},
            ensure_ascii=False,
        )


def main():
    """Главная функция запуска сервера"""
    logger.info("🚀 Starting Google Sheets MCP Server")

    # Проверить доступность ключа
    service_account = get_service_account_key()
    if not service_account:
        logger.error("❌ Google Service Account ключ не найден в Keychain")
        sys.exit(1)

    logger.info("✅ Google Service Account ключ найден")

    logger.info("📝 MCP tools will be auto-registered via @mcp.tool() decorators")

    # Запуск сервера
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
