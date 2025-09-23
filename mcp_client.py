#!/usr/bin/env python3
"""
MCP Client для работы с 1С MCP сервером
Согласно стандарту 4.1 MCP Workflow Standard

JTBD:
Как MCP клиент, я хочу взаимодействовать с MCP сервером 1С,
чтобы извлекать данные через стандартизированный интерфейс.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class MCPClient:
    """
    Клиент для работы с MCP сервером 1С
    """

    def __init__(self, server_path: Optional[str] = None) -> None:
        """
        Инициализация MCP клиента

        Args:
            server_path: Путь к MCP серверу
        """
        if server_path is None:
            # Автоматически находим путь к серверу
            project_root = Path(__file__).parent
            server_path = str(project_root / "mcp_server" / "onec_mcp_server.py")

        self.server_path = Path(server_path)
        self.server_process = None

        print(f"🔗 MCP клиент инициализирован")
        print(f"📁 Путь к серверу: {self.server_path}")

    def _run_mcp_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Выполнение команды через MCP сервер

        Args:
            command: Команда для выполнения
            **kwargs: Параметры команды

        Returns:
            Результат выполнения команды
        """
        try:
            # Создаем команду для выполнения
            cmd = [
                sys.executable,
                str(self.server_path),
                "--command",
                command,
                "--params",
                json.dumps(kwargs),
            ]

            # Выполняем команду
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 минут таймаут
            )

            if result.returncode == 0:
                # Парсим JSON ответ
                try:
                    result_data: Dict[str, Any] = json.loads(result.stdout)
                    return result_data
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Не удалось распарсить JSON ответ",
                        "raw_output": result.stdout,
                    }
            else:
                return {
                    "success": False,
                    "error": f"Ошибка выполнения команды: {result.stderr}",
                    "returncode": result.returncode,
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Таймаут выполнения команды (5 минут)"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка выполнения: {str(e)}"}

    def extract_1c_documents(
        self, table_name: str, database_path: str, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Извлечение документов из таблицы 1С

        Args:
            table_name: Имя таблицы
            database_path: Путь к базе данных
            limit: Ограничение количества записей

        Returns:
            Результат извлечения документов
        """
        print(f"📊 Извлечение документов из {table_name}...")

        params: Dict[str, Any] = {
            "table_name": table_name,
            "database_path": database_path,
        }

        if limit is not None:
            params["limit"] = limit

        return self._run_mcp_command("extract_1c_documents", **params)

    def create_flat_table(
        self, documents_list: List[List[Dict[str, Any]]], table_names: List[str]
    ) -> Dict[str, Any]:
        """
        Создание плоской таблицы из документов

        Args:
            documents_list: Список списков документов
            table_names: Список имен таблиц

        Returns:
            Результат создания плоской таблицы
        """
        print(f"🔗 Создание плоской таблицы из {len(documents_list)} таблиц...")

        params: Dict[str, Any] = {
            "documents_list": documents_list,
            "table_names": table_names,
        }

        return self._run_mcp_command("create_flat_table", **params)

    def extract_table_parts(
        self, table_name: str, database_path: str, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Извлечение табличных частей из таблицы 1С

        Args:
            table_name: Имя таблицы с табличными частями
            database_path: Путь к базе данных
            limit: Ограничение количества записей

        Returns:
            Результат извлечения табличных частей
        """
        print(f"📊 Извлечение табличных частей из {table_name}...")

        params: Dict[str, Any] = {
            "table_name": table_name,
            "database_path": database_path,
        }

        if limit is not None:
            params["limit"] = limit

        return self._run_mcp_command("extract_table_parts", **params)

    def save_to_parquet(
        self, data: List[Dict[str, Any]], output_path: str
    ) -> Dict[str, Any]:
        """
        Сохранение данных в Parquet

        Args:
            data: Данные для сохранения
            output_path: Путь для сохранения

        Returns:
            Результат сохранения
        """
        print(f"💾 Сохранение {len(data)} записей в {output_path}...")

        params: Dict[str, Any] = {"data": data, "output_path": output_path}

        return self._run_mcp_command("save_to_parquet", **params)

    def get_database_info(self) -> Dict[str, Any]:
        """
        Получение информации о базе данных

        Returns:
            Информация о базе данных
        """
        print("📊 Получение информации о базе данных...")

        return self._run_mcp_command("get_database_info")


# Пример использования
if __name__ == "__main__":

    def main() -> None:
        """Основная функция для тестирования MCP клиента."""
        # Создаем клиент
        client = MCPClient()

        # Тестируем подключение
        info = client.get_database_info()
        print(f"📊 Информация о базе: {info}")

        # Тестируем извлечение документов
        result = client.extract_1c_documents(
            table_name="_DOCUMENT138", database_path="data/raw/1Cv8.1CD", limit=10
        )
        print(f"📋 Результат извлечения: {result}")

    main()
