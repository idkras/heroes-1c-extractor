#!/usr/bin/env python3
"""
DatabaseConnector - подключение к 1CD базе данных.

JTBD:
Как компонент подключения к базе данных, я хочу обеспечить надежное подключение к 1С базе,
чтобы другие компоненты могли извлекать данные без забот о деталях подключения.
"""

import os
import sys
from typing import Any

from onec_dtools import DatabaseReader


class DatabaseConnector:
    """
    JTBD:
    Как DatabaseConnector, я хочу управлять подключением к 1С базе данных,
    чтобы обеспечить единую точку доступа к данным для всех экстракторов.
    """

    def __init__(self, file_path: str):
        """
        JTBD:
        Как конструктор DatabaseConnector, я хочу инициализировать подключение к 1С базе,
        чтобы подготовить все необходимые ресурсы для работы с данными.
        """
        self.file_path = file_path
        self.db_reader: DatabaseReader | None = None
        self._patch_applied = False
        self._file_handle = None

    def connect(self) -> DatabaseReader:
        """
        JTBD:
        Как метод подключения, я хочу установить соединение с 1С базой данных,
        чтобы обеспечить доступ к таблицам и данным.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"1С база данных не найдена: {self.file_path}")

        # Применяем патч для поддержки новых типов полей 1С
        self._apply_patch()

        try:
            # Открываем файл и сохраняем handle для предотвращения закрытия
            self._file_handle = open(self.file_path, "rb")
            self.db_reader = DatabaseReader(self._file_handle)
            return self.db_reader
        except ValueError as e:
            if "Unknown field type" in str(e):
                raise ValueError(
                    f"Ошибка типа поля в 1С базе. Убедитесь что патч применен: {e}",
                )
            raise e

    def get_tables(self) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения таблиц, я хочу вернуть все доступные таблицы из базы,
        чтобы экстракторы могли работать с нужными таблицами.
        """
        if not self.db_reader:
            raise RuntimeError("База данных не подключена. Вызовите connect() сначала.")

        return self.db_reader.tables

    def get_table(self, table_name: str) -> Any:
        """
        JTBD:
        Как метод получения таблицы, я хочу вернуть конкретную таблицу по имени,
        чтобы экстракторы могли работать с нужной таблицей.
        """
        tables = self.get_tables()
        if table_name not in tables:
            raise KeyError(f"Таблица '{table_name}' не найдена в базе данных")

        return tables[table_name]

    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения информации о таблице, я хочу вернуть метаданные таблицы,
        чтобы экстракторы могли принимать обоснованные решения о обработке.
        """
        table = self.get_table(table_name)
        return {
            "name": table_name,
            "size": len(table),
            "has_data": len(table) > 0,
            "is_empty": len(table) == 0,
        }

    def get_document_tables(self) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения таблиц документов, я хочу вернуть все таблицы документов,
        чтобы DocumentExtractor мог работать с ними.
        """
        tables = self.get_tables()
        return {
            name: table
            for name, table in tables.items()
            if name.startswith("_DOCUMENT")
        }

    def get_reference_tables(self) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения справочников, я хочу вернуть все таблицы справочников,
        чтобы ReferenceExtractor мог работать с ними.
        """
        tables = self.get_tables()
        return {
            name: table
            for name, table in tables.items()
            if name.startswith("_Reference")
        }

    def get_register_tables(self) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения регистров, я хочу вернуть все таблицы регистров,
        чтобы RegisterExtractor мог работать с ними.
        """
        tables = self.get_tables()
        return {
            name: table
            for name, table in tables.items()
            if name.startswith("_AccumRGT") or name.startswith("_InfoRGT")
        }

    def get_table_parts(self, table_name: str) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения табличных частей, я хочу вернуть все табличные части документа,
        чтобы DocumentExtractor мог извлекать полную структуру документа.
        """
        tables = self.get_tables()
        table_parts = {}

        for table_part_name in tables.keys():
            if table_part_name.startswith(f"{table_name}_VT"):
                table_parts[table_part_name] = tables[table_part_name]

        return table_parts

    def close(self) -> None:
        """
        JTBD:
        Как метод закрытия, я хочу освободить ресурсы подключения,
        чтобы предотвратить утечки памяти и обеспечить корректное завершение.
        """
        if self.db_reader:
            # onec_dtools не требует явного закрытия, но очищаем ссылку
            self.db_reader = None

        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    def _apply_patch(self) -> None:
        """
        JTBD:
        Как метод применения патча, я хочу применить патч для поддержки новых типов полей 1С,
        чтобы избежать ошибок "Unknown field type" при работе с современными базами.
        """
        if self._patch_applied:
            return

        try:
            # Добавляем путь к патчам
            patch_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "patches",
                "onec_dtools",
            )
            sys.path.insert(0, patch_path)

            from patches.onec_dtools.simple_patch import apply_simple_patch

            apply_simple_patch()

            self._patch_applied = True
        except Exception as e:
            raise RuntimeError(f"Не удалось применить патч для onec_dtools: {e}")

    def __enter__(self):
        """Контекстный менеджер для автоматического закрытия."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста."""
        self.close()

    def __str__(self) -> str:
        """Строковое представление для отладки."""
        status = "подключена" if self.db_reader else "не подключена"
        return f"DatabaseConnector(file_path='{self.file_path}', status='{status}')"
