#!/usr/bin/env python3

"""
BaseExtractor - базовый класс для всех extractors
Устраняет дублирование кода и обеспечивает единую архитектуру
"""

import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

# Добавляем путь к патчам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Применяем патч для onec_dtools
from patches.onec_dtools.onec_dtools_patch import apply_patch

apply_patch()

from onec_dtools.database_reader import DatabaseReader

from src.utils.blob_processor import BlobProcessor
from src.utils.blob_utils import safe_get_blob_content

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Базовый класс для всех extractors

    JTBD:
    Как система рефакторинга, я хочу предоставить единую архитектуру для всех extractors,
    чтобы устранить дублирование кода и улучшить поддерживаемость.
    """

    def __init__(self, db_path: str = "data/raw/1Cv8.1CD"):
        """
        Инициализация базового extractor

        Args:
            db_path: Путь к файлу базы данных 1С
        """
        self.db_path = db_path
        self.db: DatabaseReader | None = None
        self.db_file: Any | None = None  # ИСПРАВЛЕНО: Добавляем файловый объект
        self.results: dict[str, Any] = {}
        self.blob_processor = BlobProcessor()  # ИСПРАВЛЕНО: Добавляем BlobProcessor
        self.metadata: dict[str, Any] = {
            "extraction_date": datetime.now().isoformat(),
            "source_file": db_path,
            "extractor_class": self.__class__.__name__,
        }

    def open_database(self) -> bool:
        """
        Открытие базы данных с обработкой ошибок

        Returns:
            bool: True если база открыта успешно
        """
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"❌ Файл базы данных не найден: {self.db_path}")
                return False

            # ИСПРАВЛЕНО: Сохраняем файловый объект для предотвращения закрытия
            self.db_file = open(self.db_path, "rb")
            self.db = DatabaseReader(self.db_file)
            logger.info("✅ База данных открыта успешно!")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка открытия базы данных: {e}")
            return False

    def get_document_tables(self) -> list[str]:
        """
        Получение списка таблиц документов

        Returns:
            List[str]: Список названий таблиц документов
        """
        if not self.db:
            return []

        return [name for name in self.db.tables.keys() if name.startswith("_DOCUMENT")]

    def get_reference_tables(self) -> list[str]:
        """
        Получение списка справочников

        Returns:
            List[str]: Список названий справочников
        """
        if not self.db:
            return []

        return [name for name in self.db.tables.keys() if name.startswith("_Reference")]

    def get_register_tables(self) -> list[str]:
        """
        Получение списка регистров

        Returns:
            List[str]: Список названий регистров
        """
        if not self.db:
            return []

        return [
            name
            for name in self.db.tables.keys()
            if name.startswith("_AccumRGT") or name.startswith("_InfoRGT")
        ]

    def extract_blob_content(self, value: Any) -> str | None:
        """
        Извлечение содержимого BLOB поля

        Args:
            value: BLOB объект

        Returns:
            Optional[str]: Содержимое BLOB поля или None
        """
        return safe_get_blob_content(value)

    def save_results(self, output_file: str) -> bool:
        """
        Сохранение результатов в JSON файл

        Args:
            output_file: Путь к выходному файлу

        Returns:
            bool: True если сохранение успешно
        """
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"✅ Результаты сохранены в: {output_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результатов: {e}")
            return False

    def log_progress(self, current: int, total: int, message: str = "") -> None:
        """
        Логирование прогресса обработки

        Args:
            current: Текущий элемент
            total: Общее количество элементов
            message: Дополнительное сообщение
        """
        percentage = (current / total * 100) if total > 0 else 0
        progress_msg = f"📊 Прогресс: {current:,}/{total:,} ({percentage:.1f}%)"
        if message:
            progress_msg += f" - {message}"
        logger.info(progress_msg)

    @abstractmethod
    def extract(self) -> dict[str, Any]:
        """
        Абстрактный метод извлечения данных
        Должен быть реализован в наследниках

        Returns:
            Dict[str, Any]: Результаты извлечения
        """

    def run(self) -> dict[str, Any]:
        """
        Запуск полного процесса извлечения

        Returns:
            Dict[str, Any]: Результаты извлечения
        """
        logger.info(f"🚀 Запуск {self.__class__.__name__}")
        logger.info("=" * 60)

        # Открываем базу данных
        if not self.open_database():
            return {"error": "Не удалось открыть базу данных"}

        try:
            # Выполняем извлечение
            self.results = self.extract()
            self.results["metadata"] = self.metadata

            logger.info("✅ Извлечение завершено успешно")
            return self.results

        except Exception as e:
            logger.error(f"❌ Ошибка извлечения: {e}")
            result = {"error": str(e)}
        finally:
            # Закрываем базу данных
            if self.db:
                self.db = None
            if self.db_file:
                self.db_file.close()
                self.db_file = None

        return result

    def process_blob_field(
        self,
        blob_obj: Any,
        field_name: str = "",
        context: str = "",
    ) -> dict[str, Any]:
        """
        Обработка BLOB поля с использованием BlobProcessor

        Args:
            blob_obj: BLOB объект
            field_name: Имя поля
            context: Контекст обработки

        Returns:
            Результат обработки BLOB
        """
        return self.blob_processor.extract_blob_content(blob_obj, context, field_name)
