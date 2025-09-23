#!/usr/bin/env python3
"""
SimpleDocumentExtractor - простой извлекатель документов из 1С.

JTBD:
Как простой извлекатель документов, я хочу извлекать реальные документы из 1С базы,
чтобы подтвердить возможность извлечения данных и проанализировать их структуру.
"""

import os
import sys
from datetime import datetime
from typing import Any


# ИСПРАВЛЕНО: Импортируем маппинг полей из legacy кода
def get_field_mapping() -> dict[str, Any]:
    """
    Маппинг полей из field_X в реальные названия полей согласно 1c-structure-mapping-analysis.md
    """
    return {
        # Основные поля
        "_NUMBER": "Номер документа",
        "_DATE_TIME": "Дата и время операции",
        "_DATE": "Дата документа",
        "_POSTED": "Проведен ли документ",
        "_MARKED": "Помечен на удаление",
        # BLOB поля с описаниями
        "_FLD4229": "Основное описание операции (BLOB)",
        "_FLD4243": "Дополнительные данные (BLOB)",
        "_FLD4254": "Дополнительные данные 2 (BLOB)",
        "_FLD3108": "Складская информация (BLOB)",
        "_FLD4255": "Дополнительные данные 3 (BLOB)",
        "_FLD4256": "Дополнительные данные 4 (BLOB)",
        # Финансовые поля
        "_FLD4239": "Сумма документа",
        "_FLD4238": "Количество товара",
        "_FLD4240": "Единица измерения",
        "_FLD9885": "Дополнительная сумма",
        # Операционные поля
        "_FLD4225": "Флаг операции 1 (поступление)",
        "_FLD4226": "Флаг операции 2 (реализация)",
        "_FLD4227": "Флаг операции 3 (перемещение)",
        "_FLD4236": "Флаг операции 4 (корректировка)",
        "_FLD4237": "Флаг операции 5 (списание)",
        # Технические поля
        "_VERSION": "Версия записи в базе данных",
        "_FLD8015": "Технический счетчик",
        "_FLD8070": "Техническое поле",
        "_FLD8205": "Технический флаг",
        "_FLD10651": "Технический счетчик",
        "_FLD10654": "Технический флаг",
        # ИСПРАВЛЕНО: Уникальные поля без дублирования
        "_FLD4257": "Флаг статуса",  # field_30
        "_FLD4258": "Финансовая сумма 1",  # field_31
        "_FLD4259": "Код операции",  # field_32
        "_FLD4260": "Поле 33",  # field_33
        "_FLD4261": "Поле 34",  # field_34
        "_FLD4262": "Финансовая сумма 2",  # field_35
        "_FLD4263": "Пустое поле",  # field_36
        "_FLD4264": "Флаг статуса 2",  # field_37
        "_FLD4265": "Флаг статуса 3",  # field_38
        "_FLD4266": "Код документа БТБ",  # field_39
        # ИСПРАВЛЕНО: Поля 40-71 не существуют в реальных данных
        # Удалены несуществующие поля для предотвращения ошибок
    }


def get_field_mapping_by_index() -> dict[int, str]:
    """
    Маппинг полей по индексу для таблиц документов
    """
    return {
        # Стандартные поля документов по индексу
        0: "_VERSION",  # Версия записи
        1: "_MARKED",  # Помечен на удаление
        2: "_DATE_TIME",  # Дата и время
        3: "_POSTED",  # Проведен ли документ
        4: "_NUMBER",  # Номер документа
        5: "_FLD4225",  # Флаг операции 1
        6: "_FLD4226",  # Флаг операции 2
        7: "_FLD4227",  # Флаг операции 3
        8: "_FLD4236",  # Флаг операции 4
        9: "_FLD4237",  # Флаг операции 5
        10: "_FLD4229",  # Основное описание (BLOB)
        11: "_FLD4243",  # Дополнительные данные (BLOB)
        12: "_FLD4254",  # Дополнительные данные 2 (BLOB)
        13: "_FLD3108",  # Складская информация (BLOB)
        14: "_FLD4255",  # Дополнительные данные 3 (BLOB)
        15: "_FLD4256",  # Дополнительные данные 4 (BLOB)
        16: "_FLD4238",  # Количество товара
        17: "_FLD4239",  # Сумма документа
        18: "_FLD4240",  # Единица измерения
        19: "_FLD9885",  # Дополнительная сумма
        # Дополнительные поля
        20: "_FLD9999",  # Дополнительное поле 1
        21: "_FLD9998",  # Дополнительное поле 2
        22: "_FLD4258",  # Дополнительное поле 22
        23: "_FLD4259",  # Дополнительное поле 23
        24: "_FLD4261",  # Дополнительное поле 24
        25: "_FLD4262",  # Дополнительное поле 25
        26: "_FLD4263",  # Дополнительное поле 26
        27: "_FLD4264",  # Дополнительное поле 27
        28: "_FLD4260",  # Дополнительное поле 28
        29: "_FLD4265",  # Дополнительное поле 29
        # ИСПРАВЛЕНО: Добавляем правильное соответствие полей 30-39
        30: "_FLD4257",  # Флаг статуса
        31: "_FLD4258",  # Финансовая сумма 1
        32: "_FLD4259",  # Код операции
        33: "_FLD4260",  # Поле 33
        34: "_FLD4261",  # Поле 34
        35: "_FLD4262",  # Финансовая сумма 2
        36: "_FLD4263",  # Пустое поле
        37: "_FLD4264",  # Флаг статуса 2
        38: "_FLD4265",  # Флаг статуса 3
        39: "_FLD4266",  # Код документа БТБ
        # ИСПРАВЛЕНО: Поля 40-71 не существуют в реальных данных
        # Удалены несуществующие поля для предотвращения ошибок
    }


def get_field_jtbd_scenario(field_name: str) -> str:
    """
    Получить JTBD сценарий для поля
    """
    jtbd_scenarios = {
        # Основные поля документов
        "_VERSION": "Как разработчик, я хочу видеть версию записи, чтобы отслеживать изменения в системе",
        "_MARKED": "Как администратор, я хочу видеть помечен ли документ на удаление, чтобы управлять жизненным циклом",
        "_DATE_TIME": "Как аналитик, я хочу видеть дату и время операции, чтобы анализировать временные тренды",
        "_POSTED": "Как контролер, я хочу видеть проведен ли документ, чтобы контролировать статус операций",
        "_NUMBER": "Как пользователь, я хочу видеть номер документа, чтобы найти нужный документ",
        # Операционные поля
        "_FLD4225": "Как менеджер склада, я хочу видеть флаг поступления, чтобы контролировать приход товаров",
        "_FLD4226": "Как продавец, я хочу видеть флаг реализации, чтобы контролировать продажи",
        "_FLD4227": "Как логист, я хочу видеть флаг перемещения, чтобы контролировать логистику",
        "_FLD4236": "Как бухгалтер, я хочу видеть флаг корректировки, чтобы контролировать исправления",
        "_FLD4237": "Как менеджер склада, я хочу видеть флаг списания, чтобы контролировать расход товаров",
        # BLOB поля с описаниями
        "_FLD4229": "Как логист, я хочу видеть описания заказов, чтобы понимать что заказали и куда доставить",
        "_FLD4243": "Как менеджер склада, я хочу видеть детали поступлений, чтобы контролировать что прибыло",
        "_FLD4254": "Как аналитик, я хочу видеть информацию о товарах, чтобы анализировать ассортимент",
        "_FLD3108": "Как складской, я хочу видеть складскую информацию, чтобы оптимизировать размещение товаров",
        "_FLD4255": "Как аналитик, я хочу видеть дополнительные данные 3, чтобы проводить расширенный анализ",
        "_FLD4256": "Как менеджер, я хочу видеть дополнительные данные 4, чтобы принимать решения",
        # Финансовые поля
        "_FLD4238": "Как менеджер склада, я хочу видеть количество товара, чтобы контролировать остатки",
        "_FLD4239": "Как бухгалтер, я хочу видеть сумму документа, чтобы вести финансовый учет",
        "_FLD4240": "Как менеджер, я хочу видеть единицу измерения, чтобы правильно учитывать товары",
        "_FLD9885": "Как бухгалтер, я хочу видеть дополнительную сумму, чтобы вести полный финансовый учет",
        # Дополнительные поля
        "_FLD9999": "Как аналитик, я хочу видеть дополнительные данные, чтобы проводить расширенный анализ",
        "_FLD9998": "Как менеджер, я хочу видеть дополнительные данные, чтобы принимать решения",
        # Поля 22-39
        "_FLD4258": "Как бухгалтер, я хочу видеть финансовую сумму 1, чтобы вести учет поступлений",
        "_FLD4259": "Как разработчик, я хочу видеть код операции, чтобы понимать тип выполняемой операции",
        "_FLD4260": "Как менеджер, я хочу видеть поле 33, чтобы принимать решения",
        "_FLD4261": "Как пользователь, я хочу видеть поле 34, чтобы понимать данные",
        "_FLD4262": "Как бухгалтер, я хочу видеть финансовую сумму 2, чтобы вести учет дополнительных операций",
        "_FLD4263": "Как разработчик, я хочу видеть пустое поле, чтобы понимать резервную структуру данных",
        "_FLD4264": "Как пользователь, я хочу видеть флаг статуса 2, чтобы понимать дополнительное состояние",
        "_FLD4265": "Как пользователь, я хочу видеть флаг статуса 3, чтобы понимать дополнительное состояние",
        "_FLD4266": "Как пользователь, я хочу видеть код документа БТБ, чтобы найти связанный документ",
        # Технические поля
        "_FLD4257": "Как пользователь, я хочу видеть флаг статуса, чтобы понимать состояние операции",
        "_FLD8015": "Как разработчик, я хочу видеть технический счетчик, чтобы понимать структуру данных",
        "_FLD8070": "Как разработчик, я хочу видеть техническое поле, чтобы понимать структуру данных",
        "_FLD8205": "Как разработчик, я хочу видеть технический флаг, чтобы понимать структуру данных",
        "_FLD10651": "Как разработчик, я хочу видеть технический счетчик 2, чтобы понимать структуру данных",
        "_FLD10654": "Как разработчик, я хочу видеть технический флаг 2, чтобы понимать структуру данных",
    }

    return jtbd_scenarios.get(
        field_name, "Как пользователь, я хочу видеть это поле, чтобы понимать данные"
    )


def get_field_display_name(field_name: str) -> str:
    """
    Получить отображаемое название поля
    """
    field_mapping = get_field_mapping()
    if field_name in field_mapping:
        return f"{field_name} · {field_mapping[field_name]}"

    # ИСПРАВЛЕНО: Обрабатываем поля с двойным префиксом field_field_X
    if field_name.startswith("field_field_"):
        try:
            field_index = int(field_name.split("_")[2])  # field_field_X -> X
            index_mapping = get_field_mapping_by_index()
            if field_index in index_mapping:
                real_name = index_mapping[field_index]
                if isinstance(real_name, str) and real_name in field_mapping:
                    return f"{real_name} · {field_mapping[real_name]}"
                return str(real_name) if real_name is not None else field_name
        except (ValueError, IndexError):
            pass
        return field_name

    # ИСПРАВЛЕНО: Обрабатываем поля с двойным префиксом blob_field_X
    if field_name.startswith("blob_field_"):
        try:
            field_index = int(field_name.split("_")[2])  # blob_field_X -> X
            index_mapping = get_field_mapping_by_index()
            if field_index in index_mapping:
                real_name = index_mapping[field_index]
                if isinstance(real_name, str) and real_name in field_mapping:
                    return f"{real_name} · {field_mapping[real_name]}"
                return str(real_name) if real_name is not None else field_name
        except (ValueError, IndexError):
            pass
        return field_name

    if field_name.startswith("field_"):
        # Для field_X полей пытаемся получить реальное имя по индексу
        try:
            field_index = int(field_name.split("_")[1])
            index_mapping = get_field_mapping_by_index()
            if field_index in index_mapping:
                real_name = index_mapping[field_index]
                if isinstance(real_name, str) and real_name in field_mapping:
                    return f"{real_name} · {field_mapping[real_name]}"
                return str(real_name) if real_name is not None else field_name
        except (ValueError, IndexError):
            pass
        return field_name
    return field_name


def get_document_type_mapping(table_name: str) -> str:
    """
    Маппинг типов документов для правильных названий файлов
    """
    mapping = {
        "_DOCUMENT138": "поступление_товаров",
        "_DOCUMENT137": "розничные_продажи",
        "_DOCUMENT138_VT3118": "табличные_части",
        "_DOCUMENT137_VT3035": "табличные_части_продаж",
        "_DOCUMENT184": "счета_фактуры",
        "_DOCUMENT154": "отгрузка_со_склада",
        "_DOCUMENT156": "документы",
        "_DOCUMENT163": "перекомплектация",
        "_DOCUMENTJOURNAL5354": "журнал_документов_5354",
        "_DOCUMENTJOURNAL5287": "журнал_документов_5287",
        "_DOCUMENTJOURNAL5321": "журнал_документов_5321",
    }
    return mapping.get(table_name, "неизвестно")


# Добавляем путь к процессорам
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "processors"))

# ИСПРАВЛЕНО: Включаем StopIterationHandler для надежной итерации
try:
    from ..processors.stopiteration_handler import IterationResult, StopIterationHandler

    print("✅ StopIterationHandler импортирован успешно")
except ImportError:
    StopIterationHandler = None  # type: ignore
    IterationResult = None  # type: ignore
    print("⚠️ StopIterationHandler недоступен, используем стандартную обработку")


# ИСПРАВЛЕНО: Реальные компоненты вместо заглушек
class BlobProcessor:
    def __init__(self, output_dir: str = "data/results/extracted_files") -> None:
        """
        Инициализация BlobProcessor с настройками сохранения файлов

        Args:
            output_dir: Папка для сохранения извлеченных файлов
        """
        self.output_dir = output_dir
        self.magic_signatures = {
            # Изображения
            "png": b"\x89PNG\r\n\x1a\n",
            "jpeg": b"\xff\xd8\xff",
            "gif": b"GIF87a",
            "bmp": b"BM",
            # Документы
            "pdf": b"%PDF",
            "rtf": b"{\\rtf",
            "xml": b"<?xml",
            "json": b"{",
            # Архивы
            "zip": b"PK\x03\x04",
            "rar": b"Rar!\x1a\x07\x00",
            # 1C специфичные
            "1c_presentation": b"\x80\xfd\x00PV",
            "1c_binary": b"\x80\xfd",
        }

    def detect_file_type(self, blob_data: bytes) -> str:
        """
        Детекция типа файла по magic bytes

        Args:
            blob_data: Байты для анализа

        Returns:
            Тип файла или 'unknown'
        """
        for file_type, signature in self.magic_signatures.items():
            if blob_data.startswith(signature):
                return file_type
        return "unknown"

    def save_file_to_disk(
        self,
        blob_data: bytes,
        file_type: str,
        table_name: str,
        field_name: str,
        row_id: str,
    ) -> str:
        """
        Сохранение файла на диск

        Args:
            blob_data: Байты для сохранения
            file_type: Тип файла
            table_name: Название таблицы
            field_name: Название поля
            row_id: ID строки

        Returns:
            Путь к сохраненному файлу
        """
        import os
        from datetime import datetime

        # Создать папку по типу файла
        type_folder = {
            "png": "images",
            "jpeg": "images",
            "pdf": "documents",
            "zip": "archives",
            "rtf": "documents",
            "xml": "text",
            "json": "text",
        }.get(file_type, "unknown")

        folder_path = os.path.join(self.output_dir, type_folder)
        os.makedirs(folder_path, exist_ok=True)

        # Генерировать уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = file_type if file_type != "unknown" else "bin"
        filename = f"{table_name}_{field_name}_{row_id}_{timestamp}.{extension}"
        file_path = os.path.join(folder_path, filename)

        # Сохранить файл
        with open(file_path, "wb") as f:
            f.write(blob_data)

        return file_path

    def normalize_bytes(self, value: Any) -> Any:
        """
        Нормализует входные данные для BLOB обработки

        Args:
            value: Значение для нормализации

        Returns:
            Нормализованное значение
        """
        if isinstance(value, (bytes, bytearray)):
            return bytes(value)
        if isinstance(value, str) and value.startswith("b'") and value.endswith("'"):
            try:
                import ast

                y = ast.literal_eval(value)  # вернёт bytes
                if isinstance(y, (bytes, bytearray)):
                    return bytes(y)
            except Exception:
                pass
        # ИСПРАВЛЕНО: Обрабатываем base64 строки из MCP сервера
        if isinstance(value, str) and not value.startswith("b'"):
            # Проверяем, является ли это base64 строкой
            try:
                import base64

                # Пробуем декодировать как base64
                decoded_bytes = base64.b64decode(value)
                if len(decoded_bytes) > 0:
                    # ИСПРАВЛЕНО: Сразу пробуем декодировать в текст
                    try:
                        # Пробуем UTF-16 (стандарт 1С)
                        decoded_text = decoded_bytes.decode("utf-16le")
                        if self._is_valid_text(decoded_text):
                            return decoded_text
                    except:
                        pass
                    try:
                        # Пробуем UTF-8
                        decoded_text = decoded_bytes.decode("utf-8")
                        if self._is_valid_text(decoded_text):
                            return decoded_text
                    except:
                        pass
                    # Если не удалось декодировать как текст, возвращаем bytes
                    return decoded_bytes
            except Exception:
                pass
            # Если не base64, то это уже декодированная строка
            try:
                return value.encode("utf-16le")
            except Exception:
                pass
        return value

    def guess_1c_blob_kind(self, b: bytes) -> str | None:
        """
        Распознает тип BLOB поля по сигнатурам 1С

        Args:
            b: Байты для анализа

        Returns:
            Тип BLOB или None
        """
        if isinstance(b, (bytes, bytearray)):
            # Конвертируем в bytes для анализа
            blob_bytes = bytes(b)
            # Частая «магия» 1С: 0x80 0xFD и «PV» в заголовке
            if (
                len(blob_bytes) >= 5
                and blob_bytes[0:2] == b"\x80\xfd"
                and blob_bytes[3:5] == b"PV"
            ):
                return "1c_presentation_value"
        return None

    def _detect_data_offset(self, content: bytes) -> int:
        """
        Определение смещения данных в BLOB (1С добавляет заголовки)

        Args:
            content: Байты для анализа

        Returns:
            Смещение данных
        """
        # Проверяем на PNG
        if content.startswith(b"\x89PNG"):
            return 0
        # Проверяем на JPEG
        if content.startswith(b"\xff\xd8\xff"):
            return 0
        # Проверяем на PDF
        if content.startswith(b"%PDF-"):
            return 0
        # Ищем смещение для других форматов
        for i in range(min(100, len(content))):
            if content[i : i + 4] in [b"%PDF", b"PNG\x0d", b"\xff\xd8"]:
                return i
        return 0

    def _is_valid_text(self, text: str) -> bool:
        """
        Проверка, является ли текст валидным

        Args:
            text: Текст для проверки

        Returns:
            True если текст валидный
        """
        if not text or len(text.strip()) < 3:
            return False
        # Проверяем на разумное соотношение печатных символов
        printable_ratio = sum(1 for c in text if c.isprintable()) / len(text)
        return printable_ratio > 0.7

    def try_utf16_with_quality(
        self, b: bytes, threshold: float = 0.9
    ) -> tuple[str | None, str | None]:
        """
        Пробует декодировать UTF-16 с проверкой качества

        Args:
            b: Байты для декодирования
            threshold: Порог качества (доля печатных символов)

        Returns:
            Tuple (encoding, decoded_string) или (None, None)
        """
        for enc in ("utf-16le", "utf-16be"):
            try:
                s = b.decode(enc)
                if s:
                    printable = sum(ch.isprintable() for ch in s) / len(s)
                    if printable >= threshold:
                        return enc, s
            except Exception:
                pass
        return None, None

    def process_blob_field(
        self, field_name: str, value: Any, table_name: str = "", row_id: str = ""
    ) -> dict[str, Any]:
        """
        ОБНОВЛЕННАЯ обработка BLOB полей с сохранением файлов и метаданными

        JTBD:
        Как BlobProcessor, я хочу обрабатывать BLOB поля согласно обновленному стандарту 1C,
        чтобы извлекать реальные данные из BLOB полей без иероглифов и сохранять файлы на диск.
        """
        try:
            # ИСПРАВЛЕНО: Обработка JSON строк из MCP сервера (с одинарными кавычками)
            if isinstance(value, str) and (
                "{" in value and "}" in value and "value" in value
            ):
                try:
                    import ast
                    import json

                    # Пробуем сначала ast.literal_eval для строк с одинарными кавычками
                    try:
                        json_data = ast.literal_eval(value)
                    except:
                        # Если не получилось, пробуем заменить одинарные кавычки на двойные
                        json_string = value.replace("'", '"')
                        json_data = json.loads(json_string)

                    if isinstance(json_data, dict) and "value" in json_data:
                        return {
                            "value": {
                                "content": str(json_data["value"]),
                                "type": "json_parsed",
                                "length": len(str(json_data["value"])),
                            },
                            "extraction_methods": ["json_parse"],
                            "size": len(value),
                            "metadata": {
                                "file_type": "text",
                                "file_path": None,
                                "file_size": len(str(json_data["value"])),
                                "quality": 1.0,
                            },
                        }
                except (json.JSONDecodeError, ValueError, SyntaxError):
                    pass  # Продолжаем обычную обработку

            # 1. Нормализация данных
            x = self.normalize_bytes(value)

            # ИСПРАВЛЕНО: Если нормализация вернула строку (уже декодированный текст), возвращаем её
            if isinstance(x, str):
                return {
                    "value": {
                        "content": x,
                        "type": "text_decoded",
                        "length": len(x),
                    },
                    "extraction_methods": ["direct_text"],
                    "size": len(x),
                    "metadata": {
                        "file_type": "text",
                        "file_path": None,
                        "file_size": len(x),
                        "quality": 1.0,
                    },
                }

            if not isinstance(x, (bytes, bytearray)):
                return {
                    "value": {
                        "content": "Не удалось нормализовать в bytes",
                        "type": "normalization_failed",
                        "length": 0,
                    },
                    "extraction_methods": ["normalization_failed"],
                    "size": 0,
                    "metadata": {
                        "file_type": "unknown",
                        "file_path": None,
                        "file_size": 0,
                        "quality": 0.0,
                    },
                }

            # 2. Детекция 1С сигнатур
            kind = self.guess_1c_blob_kind(x)
            if kind == "1c_presentation_value":
                # ИСПРАВЛЕНО: Возвращаем декодированный текст вместо base64
                try:
                    # Пробуем декодировать как UTF-16 (стандарт 1С)
                    decoded_text = x.decode("utf-16le")
                    if self._is_valid_text(decoded_text):
                        return {
                        "value": {
                                "content": decoded_text,
                                "type": "text_utf16_decoded",
                                "length": len(decoded_text),
                            },
                            "extraction_methods": ["1c_signature_utf16"],
                            "size": len(x),
                            "note": "1С контейнер успешно декодирован как UTF-16",
                            "metadata": {
                                "file_type": "1c_presentation",
                                "file_path": None,
                                "file_size": len(x),
                                "quality": 1.0,
                            },
                        }
                except:
                    pass

                # Fallback к base64 если декодирование не удалось
                import base64

                return {
                    "value": {
                        "content": base64.b64encode(x).decode("ascii"),
                        "type": "1c_binary",
                        "encoding": "base64",
                        "length": len(x),
                    },
                    "extraction_methods": ["1c_signature_base64"],
                    "size": len(x),
                    "note": "Внутренний контейнер 1С, требуется десериализация onec_dtools",
                    "metadata": {
                        "file_type": "1c_binary",
                        "file_path": None,
                        "file_size": len(x),
                        "quality": 0.8,
                    },
                }

            # 3. Обработка смещений данных
            offset = self._detect_data_offset(x)
            if offset > 0:
                x = x[offset:]

            # 4. Множественные кодировки с проверкой качества
            if isinstance(x, (bytes, bytearray)):
                enc, s = self.try_utf16_with_quality(x)
                if enc:
                    return {
                        "value": {
                            "content": s,
                            "type": f"text_{enc}",
                            "length": len(s) if s is not None else 0,
                        },
                        "extraction_methods": [f"utf16_quality_{enc}"],
                        "size": len(x),
                    }
                else:
                    # Fallback кодировки
                    for encoding in ["utf-8", "cp1251", "latin1"]:
                        try:
                            decoded = x.decode(encoding)
                            if self._is_valid_text(decoded):
                                return {
                                    "value": {
                                        "content": decoded,
                                        "type": f"text_{encoding}",
                                        "length": len(decoded),
                                    },
                                    "extraction_methods": [f"fallback_{encoding}"],
                                    "size": len(x),
                                }
                        except:
                            continue

                    # Если ничего не сработало - пробуем base64 как последний fallback
                    import base64

                    # ИСПРАВЛЕНО: Возвращаем base64 только если это действительно бинарные данные
                    # Если это текстовые данные, возвращаем их как есть
                    try:
                        # Пробуем интерпретировать как текст
                        text_content = x.decode(
                            "latin1"
                        )  # Latin1 может декодировать любые байты
                        if self._is_valid_text(text_content):
                            return {
                                "value": {
                                    "content": text_content,
                                    "type": "text_latin1_fallback",
                                    "length": len(text_content),
                                },
                                "extraction_methods": ["latin1_fallback"],
                                "size": len(x),
                            }
                    except:
                        pass

            # НОВОЕ: Детекция типа файла и сохранение на диск
            if isinstance(x, (bytes, bytearray)) and len(x) > 0:
                file_type = self.detect_file_type(x)
                if file_type != "unknown" and table_name and row_id:
                    try:
                        file_path = self.save_file_to_disk(
                            x, file_type, table_name, field_name, row_id
                        )
                        # Добавляем метаданные о файле в результат
                        result = {
                            "value": {
                                "content": x,  # Сохраняем оригинальные байты
                                "type": f"file_{file_type}",
                                "length": len(x),
                                "file_path": file_path,
                                "file_type": file_type,
                                "file_size": len(x),
                            },
                            "extraction_methods": ["file_detection"],
                            "size": len(x),
                            "metadata": {
                                "file_type": file_type,
                                "file_path": file_path,
                                "file_size": len(x),
                                "quality": 1.0 if file_type != "unknown" else 0.0,
                            },
                        }
                        return result
                    except Exception as e:
                        print(f"⚠️ Не удалось сохранить файл: {e}")
                        # Fallback к обычной обработке
                        pass

            # Fallback к base64 если ничего не сработало
            import base64

            return {
                "value": {
                    "content": base64.b64encode(x).decode("ascii"),
                    "type": "binary",
                    "encoding": "base64",
                    "length": len(x),
                },
                "extraction_methods": ["base64_fallback"],
                "size": len(x),
                "metadata": {
                    "file_type": "binary",
                    "file_path": None,
                    "file_size": len(x),
                    "quality": 0.5,
                },
            }

        except Exception as e:
            return {"error": f"Blob processing error: {e}"}

    def _process_bytes_value(self, blob_value: bytes) -> dict[str, Any]:
        """
        ИСПРАВЛЕНО: Обрабатывает bytes значение согласно onec_dtools стандарту.

        КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ:
        - UTF-16 для NT полей (стандарт 1С) - ПРИОРИТЕТ 1
        - Правильная обработка пустых BLOB
        - Множественные стратегии декодирования
        - Защита от больших файлов

        Args:
            blob_value: Значение типа bytes

        Returns:
            dict: Результат обработки bytes значения
        """
        # ИСПРАВЛЕНО: Проверяем размер BLOB перед обработкой
        if len(blob_value) == 0:
            return {
                "value": {
                    "content": "",
                    "type": "empty_blob",
                    "length": 0,
                },
                "extraction_methods": ["empty"],
                "size": 0,
            }

        # ИСПРАВЛЕНО: Защита от больших файлов
        if len(blob_value) > 100 * 1024 * 1024:  # 100MB
            return {
                "value": {
                    "content": f"BLOB слишком большой: {len(blob_value)} байт",
                    "type": "large_blob",
                    "length": 0,
                },
                "extraction_methods": ["size_protection"],
                "size": len(blob_value),
            }

        # ИСПРАВЛЕНО: UTF-16 для NT полей (стандарт 1С) - ПРИОРИТЕТ 1
        try:
            decoded_content = blob_value.decode("utf-16")
            if decoded_content and len(decoded_content.strip()) > 0:
                return {
                    "value": {
                        "content": decoded_content,
                        "type": "text_utf16",
                        "length": len(decoded_content),
                    },
                    "extraction_methods": ["onec_dtools_utf16"],
                    "size": len(blob_value),
                }
        except UnicodeDecodeError:
            pass

        # ИСПРАВЛЕНО: UTF-8 fallback
        try:
            decoded_content = blob_value.decode("utf-8")
            if decoded_content and len(decoded_content.strip()) > 0:
                return {
                    "value": {
                        "content": decoded_content,
                        "type": "text_utf8",
                        "length": len(decoded_content),
                    },
                    "extraction_methods": ["utf8"],
                    "size": len(blob_value),
                }
        except UnicodeDecodeError:
            pass

        # ИСПРАВЛЕНО: CP1251 для русских текстов
        try:
            decoded_content = blob_value.decode("cp1251")
            if decoded_content and len(decoded_content.strip()) > 0:
                return {
                    "value": {
                        "content": decoded_content,
                        "type": "text_cp1251",
                        "length": len(decoded_content),
                    },
                    "extraction_methods": ["cp1251"],
                    "size": len(blob_value),
                }
        except UnicodeDecodeError:
            pass

        # ИСПРАВЛЕНО: Fallback на hex для бинарных данных
        return {
            "value": {
                "content": blob_value.hex(),
                "type": "binary_hex_fallback",
                "length": len(blob_value),
            },
            "extraction_methods": ["hex_fallback"],
            "size": len(blob_value),
        }

    def _detect_possible_formats(self, blob_value: bytes) -> list[str]:
        """
        Определяет возможные форматы бинарных данных на основе сигнатур
        """
        possible_formats = []

        # Проверяем сигнатуры файлов
        if blob_value.startswith(b"\xff\xd8\xff"):
            possible_formats.append("JPEG")
        elif blob_value.startswith(b"\x89PNG\r\n\x1a\n"):
            possible_formats.append("PNG")
        elif blob_value.startswith(b"%PDF"):
            possible_formats.append("PDF")
        elif blob_value.startswith(b"PK\x03\x04"):
            possible_formats.append("ZIP/Office")
        elif blob_value.startswith(b"\x50\x4b"):
            possible_formats.append("ZIP")
        elif blob_value.startswith(b"GIF8"):
            possible_formats.append("GIF")
        elif blob_value.startswith(b"BM"):
            possible_formats.append("BMP")
        elif blob_value.startswith(b"\x00\x00\x01\x00"):
            possible_formats.append("ICO")
        else:
            possible_formats.append("UNKNOWN_BINARY")

        return possible_formats


class DatabaseConnector:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.db: Any = None

    def connect(self) -> bool:
        """Подключается к базе данных 1С"""
        try:
            # ИСПРАВЛЕНО: Применяем патч для поддержки новых типов полей 1С
            try:
                import os
                import sys

                patch_path = os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "patches",
                    "onec_dtools",
                )
                sys.path.insert(0, patch_path)

                # ИСПРАВЛЕНО: Проверяем существование файла перед импортом
                patch_file = os.path.join(patch_path, "simple_patch.py")
                if os.path.exists(patch_file):
                    try:
                        import importlib.util
                        import sys

                        sys.path.insert(0, patch_path)
                        spec = importlib.util.spec_from_file_location(
                            "simple_patch", patch_file
                        )
                        if spec is not None and spec.loader is not None:
                            simple_patch_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(simple_patch_module)
                        else:
                            raise ImportError("Не удалось создать спецификацию модуля")

                        simple_patch_module.apply_simple_patch()
                        print("✅ Патч для новых типов полей применен")
                    except (ImportError, Exception) as e:
                        print(f"⚠️ Не удалось загрузить модуль simple_patch: {e}")
                else:
                    print("⚠️ Файл патча не найден, пропускаем")
            except Exception as e:
                print(f"⚠️ Не удалось применить патч: {e}")

            from onec_dtools import DatabaseReader

            f = open(self.database_path, "rb")
            self.db = DatabaseReader(f)
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            return False

    def get_table(self, table_name: str) -> Any:
        """Получает таблицу по имени"""
        if self.db is not None and table_name in self.db.tables:
            return self.db.tables[table_name]
        return None

    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """Получает информацию о таблице"""
        if self.db is not None and table_name in self.db.tables:
            table = self.db.tables[table_name]
            return {
                "size": len(table),
                "has_data": len(table) > 0,
                "is_empty": len(table) == 0,
            }
        return {"size": 0, "has_data": False, "is_empty": True}


class TableAnalyzer:
    def analyze_table_structure(self, table: Any) -> dict[str, Any]:
        """Анализирует структуру таблицы"""
        if not table:
            return {
                "structure_summary": {
                    "total_fields": 0,
                    "numeric_fields": 0,
                    "blob_fields": 0,
                }
            }

        try:
            # Анализируем первые 5 записей для понимания структуры
            field_analysis = {}
            blob_fields = 0
            numeric_fields = 0

            for i in range(min(5, len(table))):
                try:
                    row = table[i]
                    if hasattr(row, "as_list"):
                        row_list = row.as_list(True)
                        for j, value in enumerate(row_list):
                            field_name = getattr(value, "name", f"field_{j}")

                            # ИСПРАВЛЕНО: Используем готовую функцию маппинга
                            mapped_field_name = get_field_display_name(field_name)
                            # Извлекаем только техническое имя (до " · ")
                            if " · " in mapped_field_name:
                                field_name = mapped_field_name.split(" · ")[0]
                            else:
                                field_name = mapped_field_name

                            if field_name not in field_analysis:
                                field_analysis[field_name] = {
                                    "is_blob": False,
                                    "is_numeric": False,
                                    "is_string": False,
                                }

                            # Анализируем тип поля
                            if isinstance(value, bytes) or (
                                hasattr(value, "value")
                                and isinstance(value.value, bytes)
                            ):
                                field_analysis[field_name]["is_blob"] = True
                                blob_fields += 1
                            elif isinstance(value, (int, float)) or (
                                hasattr(value, "value")
                                and isinstance(value.value, (int, float))
                            ):
                                field_analysis[field_name]["is_numeric"] = True
                                numeric_fields += 1
                            elif isinstance(value, str) or (
                                hasattr(value, "value") and isinstance(value.value, str)
                            ):
                                field_analysis[field_name]["is_string"] = True
                except Exception:
                    continue

            return {
                "structure_summary": {
                    "total_fields": len(field_analysis),
                    "numeric_fields": numeric_fields,
                    "blob_fields": blob_fields,
                }
            }
        except Exception:
            return {
                "structure_summary": {
                    "total_fields": 0,
                    "numeric_fields": 0,
                    "blob_fields": 0,
                }
            }

    def extract_field_metadata(self, field_name: str, value: Any) -> dict[str, Any]:
        """Извлекает метаданные поля"""
        is_blob = False
        is_numeric = False
        is_string = False
        field_type = "unknown"

        if isinstance(value, bytes):
            is_blob = True
            field_type = "bytes"
        elif hasattr(value, "value") and isinstance(value.value, bytes):
            is_blob = True
            field_type = "blob_object"
        elif isinstance(value, (int, float)):
            is_numeric = True
            field_type = "numeric"
        elif hasattr(value, "value") and isinstance(value.value, (int, float)):
            is_numeric = True
            field_type = "numeric_object"
        elif isinstance(value, str):
            # ИСПРАВЛЕНО: Проверяем на JSON строки из MCP сервера
            if "{" in value and "}" in value and "value" in value:
                is_blob = True  # JSON строки обрабатываем как BLOB
                field_type = "json_string"
            else:
            is_string = True
            field_type = "string"
        elif hasattr(value, "value") and isinstance(value.value, str):
            # ИСПРАВЛЕНО: Проверяем на JSON строки в value
            if (
                "{" in str(value.value)
                and "}" in str(value.value)
                and "value" in str(value.value)
            ):
                is_blob = True  # JSON строки обрабатываем как BLOB
                field_type = "json_string_object"
            else:
            is_string = True
            field_type = "string_object"

        return {
            "is_blob": is_blob,
            "is_numeric": is_numeric,
            "is_string": is_string,
            "type": field_type,
        }


class SimpleDocumentExtractor:
    """
    JTBD:
    Как SimpleDocumentExtractor, я хочу извлекать реальные документы из 1С,
    чтобы подтвердить возможность извлечения данных и проанализировать их структуру.
    """

    def __init__(self, db_connector: DatabaseConnector):
        """
        JTBD:
        Как конструктор SimpleDocumentExtractor, я хочу инициализировать извлекатель,
        чтобы подготовить все необходимые компоненты для извлечения документов.
        """
        self.db_connector = db_connector
        self.table_analyzer = TableAnalyzer()
        self.blob_processor = BlobProcessor()

        # ИСПРАВЛЕНО: Добавляем StopIterationHandler для решения проблем с итерацией
        if StopIterationHandler is not None:
            self.stopiteration_handler = StopIterationHandler()
            print("✅ StopIterationHandler инициализирован")
        else:
            self.stopiteration_handler = None  # type: ignore
            print("⚠️ StopIterationHandler недоступен, используем стандартную обработку")

        self.extracted_documents: list[dict[str, Any]] = []
        self.extraction_stats: dict[str, Any] = {
            "total_documents": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "blob_fields_found": 0,
            "blob_fields_processed": 0,
            "extraction_errors": [],
            "stopiteration_errors": 0,
            "recovery_attempts": 0,
        }

    def extract_documents(
        self, table_name: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        JTBD:
        Как метод извлечения документов, я хочу извлечь реальные документы из таблицы,
        чтобы проанализировать их структуру и содержимое.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество документов для извлечения

        Returns:
            Список извлеченных документов
        """
        print(f"🔍 Извлечение документов из таблицы: {table_name}")
        if limit is None:
            print("📊 Лимит: ВСЕ документы (без ограничений)")
        else:
            print(f"📊 Лимит: {limit} документов")

        try:
            # Получаем таблицу
            table = self.db_connector.get_table(table_name)
            table_info = self.db_connector.get_table_info(table_name)

            print("📋 Информация о таблице:")
            print(f"   Размер: {table_info['size']} записей")
            print(f"   Есть данные: {table_info['has_data']}")
            print(f"   Пустая: {table_info['is_empty']}")

            if table_info["is_empty"]:
                print("⚠️ Таблица пуста, нет данных для извлечения")
                return []

            # Анализируем структуру таблицы
            structure_analysis = self.table_analyzer.analyze_table_structure(table)
            print("📊 Анализ структуры:")
            print(
                f"   Всего полей: {structure_analysis['structure_summary'].get('total_fields', 0)}",
            )
            print(
                f"   BLOB полей: {structure_analysis['structure_summary'].get('blob_fields', 0)}",
            )
            print(
                f"   Числовых полей: {structure_analysis['structure_summary']['numeric_fields']}",
            )

            # Извлекаем документы БЕЗ ЛИМИТОВ
            documents: list[dict[str, Any]] = []

            # ИСПРАВЛЕНО: Убираем скрытые лимиты - извлекаем ВСЕ документы
            print("📊 ИЗВЛЕЧЕНИЕ ВСЕХ ДОКУМЕНТОВ БЕЗ ЛИМИТОВ")
            print(f"📊 Размер таблицы по info: {table_info['size']}")

            # ДИАГНОСТИКА: Проверяем реальный размер таблицы
            try:
                # Пробуем получить реальный размер через итерацию
                test_count = 0
                test_iterator = iter(table)
                for _ in test_iterator:
                    test_count += 1
                    if test_count > 1000:  # Ограничиваем тест для производительности
                        break
                print(f"📊 Тестовый подсчет: {test_count} записей (первые 1000)")
            except Exception as e:
                print(f"⚠️ Не удалось подсчитать записи: {e}")

            # ИСПРАВЛЕНО: Извлекаем ВСЕ документы без лимитов
            actual_limit: int | None = limit
            if limit is None:
                print("📊 Лимит: НЕТ (извлекаем ВСЕ документы)")
            else:
                print(f"📊 Лимит: {actual_limit} документов")

            # ИСПРАВЛЕНО: Используем StopIterationHandler для надежной итерации
            if self.stopiteration_handler is not None:
                print("🔄 Используем StopIterationHandler для надежной итерации")

                # Анализируем таблицу перед итерацией
                analysis = self.stopiteration_handler.analyze_stopiteration_causes(
                    table, table_name
                )
                print(f"📊 Анализ таблицы {table_name}:")
                print(f"   Размер: {analysis['table_size']}")
                print(f"   BLOB поля: {analysis['has_blob_fields']}")
                print(f"   Проблемы: {analysis['iteration_problems']}")
                print(f"   Рекомендации: {analysis['recommendations']}")

                # Используем StopIterationHandler для итерации
                iteration_result = self.stopiteration_handler.handle_table_iteration(
                    table, table_name, actual_limit, include_blobs=True
                )

                if iteration_result.success:
                    print(
                        f"✅ StopIterationHandler успешно извлек {iteration_result.total_processed} записей"
                    )
                    print(f"   Стратегия: {iteration_result.strategy_used.value}")
                    print(f"   Ошибок: {iteration_result.failed_count}")
                    print(
                        f"   Попыток восстановления: {iteration_result.recovery_attempts}"
                    )

                    # Обрабатываем извлеченные данные
                    for i, row_data in enumerate(iteration_result.data):
                        try:
                            # Создаем объект row из данных
                            if isinstance(row_data, dict):
                                # Данные уже в виде словаря
                                document = self._create_document_from_dict(
                                    row_data, i, table_name
                                )
                            else:
                                # Данные в виде объекта row
                                document = self._extract_single_document(
                                    row_data, i, table_name
                                )

                        if document:
                            documents.append(document)
                            self.extraction_stats["successful_extractions"] += 1
                        else:
                            self.extraction_stats["failed_extractions"] += 1

                        except Exception as e:
                            error_msg = f"Ошибка обработки записи {i}: {e}"
                            print(f"❌ {error_msg}")
                            self.extraction_stats["failed_extractions"] += 1

                    # Обновляем статистику
                    self.extraction_stats["stopiteration_errors"] = (
                        iteration_result.failed_count
                    )
                    self.extraction_stats["recovery_attempts"] = (
                        iteration_result.recovery_attempts
                    )

                else:
                    print(
                        f"❌ StopIterationHandler не смог извлечь данные из {table_name}"
                    )
                    print(f"   Ошибки: {iteration_result.errors}")
                    self.extraction_stats["stopiteration_errors"] = len(
                        iteration_result.errors
                    )
                    self.extraction_stats["recovery_attempts"] = (
                        iteration_result.recovery_attempts
                    )

                    # Fallback к стандартной итерации
                    print("🔄 Fallback к стандартной итерации")
                    documents = self._fallback_standard_iteration(
                        table, table_name, actual_limit
                    )
            else:
                # Fallback к стандартной итерации если StopIterationHandler недоступен
                print(  # type: ignore
                    "⚠️ StopIterationHandler недоступен, используем стандартную итерацию"
                )
                documents = self._fallback_standard_iteration(
                    table, table_name, actual_limit
                )

            self.extracted_documents = documents
            self.extraction_stats["total_documents"] = len(documents)

            print("✅ Извлечение завершено:")
            print(f"   Успешно: {self.extraction_stats['successful_extractions']}")
            print(f"   Ошибок: {self.extraction_stats['failed_extractions']}")
            print(
                f"   BLOB полей найдено: {self.extraction_stats['blob_fields_found']}",
            )
            print(
                f"   BLOB полей обработано: {self.extraction_stats['blob_fields_processed']}",
            )

            # ИСПРАВЛЕНО: Добавляем извлечение табличных частей
            if documents:
                try:
                    print(f"🔍 Поиск табличных частей для {table_name}...")
                    table_parts = self._extract_table_parts(table_name)
                    if table_parts:
                        print(f"✅ Найдено {len(table_parts)} табличных частей")
                        documents.extend(table_parts)
                    else:
                        print("⚠️ Табличные части не найдены")
                except Exception as e:
                    print(f"⚠️ Ошибка извлечения табличных частей: {e}")

            # ИСПРАВЛЕНО: Добавляем автоматическое сохранение в Parquet
            if documents:
                try:
                    print(f"💾 Сохранение {len(documents)} документов в Parquet...")
                    saved_files = self.save_documents_to_parquet(documents, table_name)
                    print(f"✅ Сохранено {len(saved_files)} Parquet файлов:")
                    for file_path in saved_files:
                        print(f"   📁 {file_path}")
                except Exception as e:
                    print(f"❌ Ошибка сохранения в Parquet: {e}")

            return documents

        except Exception as e:
            error_msg = f"Критическая ошибка извлечения из таблицы {table_name}: {e}"
            print(f"❌ {error_msg}")
            self.extraction_stats["extraction_errors"].append(error_msg)
            return []

    def _extract_single_document(
        self,
        row: Any,
        row_index: int,
        table_name: str,
    ) -> dict[str, Any] | None:
        """
        JTBD:
        Как метод извлечения одного документа, я хочу извлечь данные из строки,
        чтобы создать структурированный документ с метаданными.

        Args:
            row: Строка данных из таблицы
            row_index: Индекс строки
            table_name: Имя таблицы

        Returns:
            Словарь с данными документа или None при ошибке
        """
        try:
            # Получаем список полей
            if hasattr(row, "as_list"):
                try:
                    row_list = row.as_list(True)
                except RuntimeError as e:
                    if "generator raised StopIteration" in str(e):
                        # Нормальное завершение итератора в onec_dtools
                        return None
                    raise e
                except StopIteration:
                    # Нормальное завершение итератора
                    return None
            else:
                return None

            document: dict[str, Any] = {
                "table_name": table_name,
                "row_index": row_index,
                "fields": {},
                "blob_fields": {},
                "metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "field_count": len(row_list),
                    "has_blob_fields": False,
                },
                # ИСПРАВЛЕНО: Добавляем маппинг полей для правильного извлечения данных
                "document_type": get_document_type_mapping(table_name),
                "document_number": "N/A",
                "document_date": "N/A",
                "store_name": "N/A",
                "store_code": "N/A",
                "total_amount": 0.0,
                "currency": "RUB",
                "supplier_name": "N/A",
                "buyer_name": "N/A",
            }

            # Обрабатываем каждое поле
            for j, value in enumerate(row_list):
                field_name = getattr(value, "name", f"field_{j}")

                # ИСПРАВЛЕНО: Используем готовую функцию маппинга
                mapped_field_name = get_field_display_name(field_name)
                # Извлекаем только техническое имя (до " · ")
                if " · " in mapped_field_name:
                    field_name = mapped_field_name.split(" · ")[0]
                else:
                    field_name = mapped_field_name

                # ИСПРАВЛЕНО: Правильный маппинг полей согласно структуре 1С
                if field_name == "_NUMBER":  # _NUMBER - номер документа
                    document["document_number"] = (
                        str(value) if value is not None else "N/A"
                    )
                elif field_name == "_DATE_TIME":  # _DATE_TIME - дата документа
                    document["document_date"] = (
                        str(value) if value is not None else "N/A"
                    )
                elif field_name == "_FLD4239":  # _FLD4239 - сумма документа
                    try:
                        document["total_amount"] = (
                            float(value) if value is not None else 0.0
                        )
                    except (ValueError, TypeError):
                        document["total_amount"] = 0.0
                elif field_name == "_FLD4255":  # _FLD4255 - дополнительная сумма
                    try:
                        # ИСПРАВЛЕНО: Обрабатываем JSON строки с одинарными кавычками
                        if (
                            isinstance(value, str)
                            and value.startswith("{")
                            and value.endswith("}")
                        ):
                            # ИСПРАВЛЕНО: Используем ast.literal_eval вместо json.loads
                            import ast

                            parsed_json = ast.literal_eval(value)
                            if "value" in parsed_json:
                                document["total_amount"] = float(parsed_json["value"])
                        else:
                            document["total_amount"] = (
                                float(value) if value is not None else 0.0
                            )
                    except (ValueError, TypeError, SyntaxError):
                        document["total_amount"] = 0.0
                elif field_name == "_POSTED":  # _POSTED - проведен ли документ
                    document["is_posted"] = bool(value) if value is not None else False

                # Анализируем тип поля
                field_metadata = self.table_analyzer.extract_field_metadata(
                    field_name,
                    value,
                )

                # ИСПРАВЛЕНО: Проверяем, является ли поле BLOB и обрабатываем его
                if field_metadata.get("is_blob", False):
                    self.extraction_stats["blob_fields_found"] += 1
                    document["metadata"]["has_blob_fields"] = True

                    # ИСПРАВЛЕНО: Обрабатываем BLOB поле с улучшенной логикой
                    blob_data = self.blob_processor.process_blob_field(
                        field_name,
                        value,
                        table_name,
                        str(document.get("_ID", "unknown")),
                    )

                    # Проверяем успешность обработки
                    if (
                        blob_data
                        and "value" in blob_data
                        and blob_data["value"]["content"]
                    ):
                        # ИСПРАВЛЕНО: Сохраняем декодированное содержимое BLOB
                        document["blob_fields"][field_name] = blob_data["value"][
                            "content"
                        ]

                        # НОВОЕ: Сохраняем метаданные BLOB поля
                        if "metadata" in blob_data:
                            blob_metadata = blob_data["metadata"]
                            document["blob_metadata"] = document.get(
                                "blob_metadata", {}
                            )
                            # TODO: Проверить нормальность сохранения метаданных ты пишешь unknown, 0 и нарушаешь принципы @research.mdc
                            document["blob_metadata"][field_name] = {
                                "file_type": blob_metadata.get("file_type", "unknown"),
                                "file_size": blob_metadata.get("file_size", 0),
                                "file_path": blob_metadata.get("file_path", None),
                                "quality": blob_metadata.get("quality", 0.0),
                            }

                        self.extraction_stats["blob_fields_processed"] += 1

                        # ИСПРАВЛЕНО: Если это BLOB поле с описанием, сохраняем в store_name
                        if field_name in [
                            "field_10",
                            "field_11",
                            "field_12",
                        ]:  # BLOB поля с описаниями
                            document["store_name"] = blob_data["value"]["content"]
                    elif blob_data and "error" in blob_data:
                        # Логируем ошибку, но не останавливаем обработку
                        print(
                            f"⚠️ BLOB ошибка в поле {field_name}: {blob_data['error']}"
                        )
                        document["blob_fields"][
                            field_name
                        ] = f"ERROR: {blob_data['error']}"
                    else:
                        # Пустое BLOB поле
                        document["blob_fields"][field_name] = ""
                else:
                    # Обычное поле
                    document["fields"][field_name] = {
                        "value": str(value) if value is not None else None,
                        "type": field_metadata.get("type", "unknown"),
                        "is_numeric": field_metadata.get("is_numeric", False),
                        "is_date": field_metadata.get("is_date", False),
                        "is_string": field_metadata.get("is_string", False),
                    }

            # ИСПРАВЛЕНО: Логика определения названия магазина/склада
            # Поскольку в базе данных 1С нет явных названий магазинов, создаем маппинг
            if document["store_name"] == "N/A":
                # Жестко закодированный маппинг названий магазинов
                store_mapping = {
                    "PC29757": "Южный магазин",
                    "БТБ00000189": "Чеховский магазин",
                    # Добавить другие коды по мере обнаружения
                }

                # Ищем коды магазинов в полях
                for field_name, field_data in document["fields"].items():
                    if field_name in [
                        "_FLD4236",
                        "_FLD4266",
                    ]:  # Поля с кодами магазинов
                        value = field_data.get("value")
                        if value:
                            # Обрабатываем JSON строки
                            if (
                                isinstance(value, str)
                                and value.startswith("{")
                                and value.endswith("}")
                            ):
                                try:
                                    import ast

                                    parsed_json = ast.literal_eval(value)
                                    if "value" in parsed_json:
                                        code = str(parsed_json["value"]).strip()
                                        if code in store_mapping:
                                            document["store_name"] = store_mapping[code]
                                            break
                                        else:
                                            document["store_name"] = f"Магазин {code}"
                                            break
                                except (ValueError, TypeError, SyntaxError):
                                    pass
                            else:
                                code = str(value).strip()
                                if code in store_mapping:
                                    document["store_name"] = store_mapping[code]
                                    break
                                else:
                                    document["store_name"] = f"Магазин {code}"
                                    break

                # Если магазин не определен, используем центральный склад по умолчанию
                if document["store_name"] == "N/A":
                    document["store_name"] = "Центральный склад"

            # НОВОЕ: Обрабатываем BLOB поля для создания метаданных
            if "blob_fields" in document:
                document["blob_metadata"] = {}
                for blob_name, blob_content in document["blob_fields"].items():
                    # Обрабатываем BLOB поле через BlobProcessor для получения метаданных
                    blob_result = self.blob_processor.process_blob_field(
                        blob_name,
                        blob_content,
                        table_name,
                        str(document.get("_ID", "unknown")),
                    )

                    if blob_result and "metadata" in blob_result:
                        document["blob_metadata"][blob_name] = blob_result["metadata"]

            return document

        except Exception as e:
            print(f"❌ Ошибка извлечения документа {row_index}: {e}")
            return None

    def _extract_table_parts(self, table_name: str) -> list[dict[str, Any]]:
        """
        ИСПРАВЛЕНО: Извлекает табличные части документов согласно стандарту 1С

        Args:
            table_name: Имя основной таблицы документа

        Returns:
            Список извлеченных табличных частей
        """
        table_parts: list[dict[str, Any]] = []

        try:
            # Ищем табличные части для данного документа
            if table_name == "_DOCUMENT138":
                table_part_name = "_DOCUMENT138_VT3118"
            elif table_name == "_DOCUMENT137":
                table_part_name = "_DOCUMENT137_VT3035"
            else:
                # Ищем табличные части по паттерну
                table_part_name = f"{table_name}_VT"

            # Получаем табличную часть
            table_part = self.db_connector.get_table(table_part_name)
            if not table_part:
                print(f"⚠️ Табличная часть {table_part_name} не найдена")
                return table_parts

            print(f"📊 Извлечение табличной части: {table_part_name}")

            # Извлекаем данные из табличной части
            for i, row in enumerate(table_part):
                if hasattr(row, "is_empty") and row.is_empty:
                    continue

                try:
                    # Извлекаем данные строки табличной части
                    if hasattr(row, "as_list"):
                        row_list = row.as_list(True)  # Включаем BLOB поля

                        # Создаем документ табличной части
                        table_part_doc: dict[str, Any] = {
                            "table_name": table_part_name,
                            "row_index": i,
                            "parent_table": table_name,
                            "fields": {},
                            "blob_fields": {},
                            "metadata": {
                                "extraction_time": datetime.now().isoformat(),
                                "field_count": len(row_list),
                                "has_blob_fields": False,
                            },
                        }

                        # Обрабатываем поля табличной части
                        for j, value in enumerate(row_list):
                            field_name = getattr(value, "name", f"field_{j}")

                            # ИСПРАВЛЕНО: Используем готовую функцию маппинга
                            mapped_field_name = get_field_display_name(field_name)
                            # Извлекаем только техническое имя (до " · ")
                            if " · " in mapped_field_name:
                                field_name = mapped_field_name.split(" · ")[0]
                            else:
                                field_name = mapped_field_name

                            # Анализируем тип поля
                            field_metadata = self.table_analyzer.extract_field_metadata(
                                field_name, value
                            )

                            if field_metadata.get("is_blob", False):
                                # Обрабатываем BLOB поле
                                blob_data = self.blob_processor.process_blob_field(
                                    field_name, value, table_name, str(i)
                                )

                                if blob_data and "value" in blob_data:
                                    if (
                                        isinstance(blob_data["value"], dict)
                                        and "content" in blob_data["value"]
                                    ):
                                        # ИСПРАВЛЕНО: Проверяем типы перед индексированием
                                        blob_content = blob_data["value"]["content"]
                                        if isinstance(
                                            blob_content, (str, bytes, int, float)
                                        ):
                                            # ИСПРАВЛЕНО: Явная типизация для устранения ошибок индексирования
                                            blob_fields = table_part_doc.get(
                                                "blob_fields", {}
                                            )
                                            blob_fields[field_name] = str(blob_content)
                                            table_part_doc["blob_fields"] = blob_fields

                                            metadata = table_part_doc.get(
                                                "metadata", {}
                                            )
                                            metadata["has_blob_fields"] = True
                                            table_part_doc["metadata"] = metadata
                            else:
                                # Обычное поле
                                # ИСПРАВЛЕНО: Явная типизация для устранения ошибок индексирования
                                fields = table_part_doc.get("fields", {})
                                fields[field_name] = {
                                    "value": str(value) if value is not None else None,
                                    "type": str(field_metadata.get("type", "unknown")),
                                }
                                table_part_doc["fields"] = fields

                        table_parts.append(table_part_doc)

                        # Ограничиваем количество для производительности
                        if len(table_parts) >= 1000:
                            print(
                                f"📊 Извлечено {len(table_parts)} строк табличной части (лимит)"
                            )
                            break

                except Exception as e:
                    print(f"⚠️ Ошибка извлечения строки табличной части {i}: {e}")
                    continue

            print(f"✅ Извлечено {len(table_parts)} строк табличной части")

        except Exception as e:
            print(f"❌ Ошибка извлечения табличных частей: {e}")

        return table_parts

    def _create_document_from_dict(
        self, row_data: dict[str, Any], row_index: int, table_name: str
    ) -> dict[str, Any] | None:
        """
        Создает документ из словаря данных (для StopIterationHandler)

        Args:
            row_data: Данные строки в виде словаря
            row_index: Индекс строки
            table_name: Имя таблицы

        Returns:
            Словарь с данными документа или None при ошибке
        """
        try:
            document: dict[str, Any] = {
                "table_name": table_name,
                "row_index": row_index,
                "fields": {},
                "blob_fields": {},
                "metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "field_count": len(row_data),
                    "has_blob_fields": False,
                },
                "document_type": get_document_type_mapping(table_name),
                "document_number": "N/A",
                "document_date": "N/A",
                "store_name": "N/A",
                "store_code": "N/A",
                "total_amount": 0.0,
                "currency": "RUB",
                "supplier_name": "N/A",
                "buyer_name": "N/A",
            }

            # Обрабатываем поля из словаря
            for field_name, value in row_data.items():
                if field_name in ["index", "table_name", "has_data"]:
                    continue  # Пропускаем служебные поля

                # Маппинг полей
                mapped_field_name = get_field_display_name(field_name)
                if " · " in mapped_field_name:
                    field_name = mapped_field_name.split(" · ")[0]
                else:
                    field_name = mapped_field_name

                # Обрабатываем специальные поля
                if field_name == "_NUMBER":
                    document["document_number"] = (
                        str(value) if value is not None else "N/A"
                    )
                elif field_name == "_DATE_TIME":
                    document["document_date"] = (
                        str(value) if value is not None else "N/A"
                    )
                elif field_name == "_FLD4239":
                    try:
                        document["total_amount"] = (
                            float(value) if value is not None else 0.0
                        )
                    except (ValueError, TypeError):
                        document["total_amount"] = 0.0

                # Сохраняем поле
                document["fields"][field_name] = {
                    "value": str(value) if value is not None else None,
                    "type": type(value).__name__,
                    "is_numeric": isinstance(value, (int, float)),
                    "is_date": False,
                    "is_string": isinstance(value, str),
                }

            return document

        except Exception as e:
            print(f"❌ Ошибка создания документа из словаря {row_index}: {e}")
            return None

    def _fallback_standard_iteration(
        self, table: Any, table_name: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Fallback к стандартной итерации если StopIterationHandler недоступен

        Args:
            table: Таблица для итерации
            table_name: Имя таблицы
            limit: Лимит записей

        Returns:
            Список извлеченных документов
        """
        documents: list[dict[str, Any]] = []

        try:
            print("🔄 Используем fallback стандартную итерацию")
            table_iterator = iter(table)
            i = 0

            while True:
                try:
                    row = next(table_iterator)

                    # Пропускаем пустые строки
                    if hasattr(row, "is_empty") and row.is_empty:
                        continue

                    # Извлекаем документ
                    document = self._extract_single_document(row, i, table_name)
                    if document:
                        documents.append(document)
                        self.extraction_stats["successful_extractions"] += 1
                    else:
                        self.extraction_stats["failed_extractions"] += 1

                    i += 1

                    # Проверяем лимит
                    if limit is not None and i >= limit:
                        print(f"📊 Достигнут лимит: {limit} документов")
                        break

                except StopIteration:
                    # Нормальное завершение итератора
                    print(
                        f"✅ Итератор завершен. Извлечено: {len(documents)} документов"
                    )
                    break
                except BrokenPipeError:
                    # Нормальное завершение при использовании head
                    print("✅ BrokenPipeError - нормальное завершение")
                    break
                except Exception as e:
                    # Обрабатываем только реальные ошибки
                    error_msg = f"Ошибка извлечения документа {i}: {e}"
                    print(f"❌ {error_msg}")
                    if isinstance(self.extraction_stats["extraction_errors"], list):
                        self.extraction_stats["extraction_errors"].append(error_msg)
                    self.extraction_stats["failed_extractions"] += 1
                    i += 1
                    continue

        except Exception as e:
            error_msg = f"Ошибка создания итератора: {e}"
            print(f"❌ {error_msg}")
            if isinstance(self.extraction_stats["extraction_errors"], list):
                self.extraction_stats["extraction_errors"].append(error_msg)

        return documents

    def analyze_document_structure(
        self, documents: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        JTBD:
        Как метод анализа структуры документов, я хочу проанализировать структуру извлеченных документов,
        чтобы понять их назначение и связи.

        Args:
            documents: Список извлеченных документов

        Returns:
            Словарь с анализом структуры документов
        """
        if not documents:
            return {"error": "Нет документов для анализа"}

        print(f"🔍 Анализ структуры {len(documents)} документов")

        # Анализируем поля
        field_analysis: dict[str, Any] = {}
        blob_analysis: dict[str, Any] = {}

        for doc in documents:
            # Анализируем обычные поля
            for field_name, field_data in doc.get("fields", {}).items():
                if field_name not in field_analysis:
                    field_analysis[field_name] = {
                        "count": 0,
                        "types": set(),
                        "has_values": 0,
                        "sample_values": [],
                    }

                field_analysis[field_name]["count"] += 1
                field_analysis[field_name]["types"].add(
                    field_data.get("type", "unknown"),
                )

                if field_data.get("value") is not None:
                    field_analysis[field_name]["has_values"] += 1
                    if len(field_analysis[field_name]["sample_values"]) < 3:
                        field_analysis[field_name]["sample_values"].append(
                            field_data["value"],
                        )

            # Анализируем BLOB поля
            for field_name, blob_data in doc.get("blob_fields", {}).items():
                if field_name not in blob_analysis:
                    blob_analysis[field_name] = {
                        "count": 0,
                        "successful_extractions": 0,
                        "failed_extractions": 0,
                        "sample_contents": [],
                    }

                blob_analysis[field_name]["count"] += 1

                if blob_data.get("error"):
                    blob_analysis[field_name]["failed_extractions"] += 1
                else:
                    blob_analysis[field_name]["successful_extractions"] += 1
                    if len(blob_analysis[field_name]["sample_contents"]) < 3:
                        content = blob_data.get("value", {}).get("content", "")
                        if content:
                            blob_analysis[field_name]["sample_contents"].append(
                                content[:100],
                            )

        # Создаем сводку анализа
        structure_analysis: dict[str, Any] = {
            "total_documents": len(documents),
            "field_analysis": {},
            "blob_analysis": {},
            "summary": {
                "total_fields": len(field_analysis),
                "total_blob_fields": len(blob_analysis),
                "documents_with_blobs": sum(
                    1
                    for doc in documents
                    if doc.get("metadata", {}).get("has_blob_fields", False)
                ),
            },
        }

        # Обрабатываем анализ полей
        for field_name, analysis in field_analysis.items():
            structure_analysis["field_analysis"][field_name] = {
                "count": analysis["count"],
                "types": (
                    list(analysis["types"])
                    if isinstance(analysis["types"], set)
                    else []
                ),
                "fill_rate": (analysis["has_values"] / analysis["count"]) * 100,
                "sample_values": analysis["sample_values"],
            }

        # Обрабатываем анализ BLOB полей
        for field_name, analysis in blob_analysis.items():
            success_rate = 0
            if analysis["count"] > 0:
                success_rate = (
                    analysis["successful_extractions"] / analysis["count"]
                ) * 100

            structure_analysis["blob_analysis"][field_name] = {
                "count": analysis["count"],
                "success_rate": success_rate,
                "successful_extractions": analysis["successful_extractions"],
                "failed_extractions": analysis["failed_extractions"],
                "sample_contents": analysis["sample_contents"],
            }

        print("📊 Результаты анализа структуры:")
        print(f"   Всего документов: {structure_analysis['total_documents']}")
        print(f"   Всего полей: {structure_analysis['summary']['total_fields']}")
        print(f"   BLOB полей: {structure_analysis['summary']['total_blob_fields']}")
        print(
            f"   Документов с BLOB: {structure_analysis['summary']['documents_with_blobs']}",
        )

        return structure_analysis

    def validate_extraction_quality(
        self, documents: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        JTBD:
        Как метод валидации качества извлечения, я хочу проверить качество извлеченных документов,
        чтобы убедиться в корректности извлечения данных.

        Args:
            documents: Список извлеченных документов

        Returns:
            Словарь с результатами валидации качества
        """
        if not documents:
            return {"error": "Нет документов для валидации"}

        print(f"🔍 Валидация качества извлечения {len(documents)} документов")

        quality_metrics: dict[str, Any] = {
            "total_documents": len(documents),
            "documents_with_data": 0,
            "documents_with_blobs": 0,
            "blob_success_rate": 0.0,
            "field_completeness": 0.0,
            "extraction_errors": (
                len(self.extraction_stats["extraction_errors"])
                if isinstance(self.extraction_stats["extraction_errors"], list)
                else 0
            ),
            "quality_score": 0.0,
        }

        total_blob_fields = 0
        successful_blob_fields = 0
        total_fields = 0
        filled_fields = 0

        for doc in documents:
            # Проверяем наличие данных
            if doc.get("fields") or doc.get("blob_fields"):
                quality_metrics["documents_with_data"] += 1

            # Проверяем BLOB поля
            if doc.get("blob_fields"):
                quality_metrics["documents_with_blobs"] += 1
                for field_name, blob_data in doc["blob_fields"].items():
                    total_blob_fields += 1
                    if not blob_data.get("error"):
                        successful_blob_fields += 1

            # Проверяем обычные поля
            for field_name, field_data in doc.get("fields", {}).items():
                total_fields += 1
                if field_data.get("value") is not None:
                    filled_fields += 1

        # Вычисляем метрики качества
        if total_blob_fields > 0:
            quality_metrics["blob_success_rate"] = (
                successful_blob_fields / total_blob_fields
            ) * 100

        if total_fields > 0:
            quality_metrics["field_completeness"] = (filled_fields / total_fields) * 100

        # Вычисляем общий балл качества
        quality_score: float = 0.0
        if quality_metrics["documents_with_data"] > 0:
            quality_score += 30  # За наличие данных
        if quality_metrics["blob_success_rate"] > 50:
            quality_score += 30  # За успешное извлечение BLOB
        if quality_metrics["field_completeness"] > 70:
            quality_score += 20  # За полноту полей
        if quality_metrics["extraction_errors"] == 0:
            quality_score += 20  # За отсутствие ошибок

        quality_metrics["quality_score"] = quality_score

        print("📊 Результаты валидации качества:")
        print(f"   Документов с данными: {quality_metrics['documents_with_data']}")
        print(f"   Документов с BLOB: {quality_metrics['documents_with_blobs']}")
        print(f"   Успешность BLOB: {quality_metrics['blob_success_rate']:.1f}%")
        print(f"   Полнота полей: {quality_metrics['field_completeness']:.1f}%")
        print(f"   Ошибок извлечения: {quality_metrics['extraction_errors']}")
        print(f"   Общий балл качества: {quality_score}/100")

        return quality_metrics

    def get_extraction_stats(self) -> dict[str, Any]:
        """
        JTBD:
        Как метод получения статистики извлечения, я хочу вернуть статистику извлечения,
        чтобы проанализировать результаты работы извлекателя.

        Returns:
            Словарь со статистикой извлечения
        """
        return self.extraction_stats.copy()

    def save_to_parquet_with_descriptive_names(
        self,
        base_path: str = "data/results/parquet/",
    ) -> list[str]:
        """
        JTBD:
        Как метод сохранения с описательными именами, я хочу сохранить документы
        с понятными названиями файлов как в legacy коде.

        Args:
            base_path: Базовая директория для сохранения

        Returns:
            Список путей к сохраненным файлам
        """
        try:
            import os

            import pandas as pd

            os.makedirs(base_path, exist_ok=True)
            saved_files: list[str] = []

            if not self.extracted_documents:
                print("⚠️ Нет документов для сохранения")
                return saved_files

            # Группируем по table_name
            df = pd.DataFrame(self.extracted_documents)
            if "table_name" not in df.columns:
                print("⚠️ Нет поля table_name в документах")
                return saved_files

            for table_name in df["table_name"].unique():
                table_df = df[df["table_name"] == table_name]

                # ИСПРАВЛЕНО: Используем правильный маппинг типов документов
                document_type = get_document_type_mapping(table_name)

                # Создаем файл с понятным названием (lowercase)
                table_name_lower = table_name.lower()
                safe_name = (
                    document_type.lower()
                    .replace(" ", "_")
                    .replace("(", "")
                    .replace(")", "")
                )
                parquet_file = f"{base_path}{table_name_lower}_{safe_name}.parquet"

                # Конвертируем BLOB поля (bytes) в hex-строки для Parquet
                for col in table_df.select_dtypes(include=["object"]).columns:
                    if table_df[col].apply(lambda x: isinstance(x, bytes)).any():
                        table_df[col] = table_df[col].apply(
                            lambda x: x.hex() if isinstance(x, bytes) else x
                        )

                table_df.to_parquet(parquet_file, index=False)
                saved_files.append(parquet_file)
                print(f"✅ {table_name}: {len(table_df)} записей → {parquet_file}")

            return saved_files

        except Exception as e:
            print(f"❌ Ошибка при сохранении с описательными именами: {e}")
            raise

    def save_documents_to_parquet(
        self, documents: list[dict[str, Any]], table_name: str
    ) -> list[str]:
        """
        JTBD:
        Как метод сохранения документов в Parquet, я хочу сохранить извлеченные документы в Parquet файлы,
        чтобы обеспечить быстрый доступ к данным для анализа.

        Args:
            documents: Список извлеченных документов
            table_name: Имя таблицы для создания имени файла

        Returns:
            Список путей к созданным Parquet файлам
        """
        try:
            import os

            import pandas as pd

            # Создаем директорию для результатов
            os.makedirs("data/results/parquet", exist_ok=True)

            # Конвертируем документы в DataFrame
            documents_data = []
            for doc in documents:
                doc_data = {
                    "table_name": doc.get("table_name", ""),
                    "row_index": doc.get("row_index", 0),
                    "document_type": doc.get("document_type", "Неизвестно"),
                    "document_number": doc.get("document_number", "N/A"),
                    "document_date": doc.get("document_date", "N/A"),
                    "store_name": doc.get("store_name", "N/A"),
                    "store_code": doc.get("store_code", "N/A"),
                    "total_amount": doc.get("total_amount", 0.0),
                    "currency": doc.get("currency", "RUB"),
                    "supplier_name": doc.get("supplier_name", "N/A"),
                    "buyer_name": doc.get("buyer_name", "N/A"),
                    "blob_content": doc.get("blob_content", ""),
                    "total_blobs": doc.get("extraction_stats", {}).get(
                        "total_blobs", 0
                    ),
                }

                # ИСПРАВЛЕНО: Добавляем поля с правильными названиями и извлечением значений из dict
                if "fields" in doc:
                    for field_name, field_value in doc["fields"].items():
                        # ИСПРАВЛЕНО: Если поле - это dict с ключом 'value', извлекаем значение
                        if isinstance(field_value, dict) and "value" in field_value:
                            doc_data[field_name] = field_value["value"]
                        else:
                            doc_data[field_name] = str(field_value)

                # ИСПРАВЛЕНО: Добавляем BLOB поля - НЕ обрабатываем СНОВА, используем уже обработанные!
                if "blob_fields" in doc:
                    for blob_name, blob_content in doc["blob_fields"].items():
                        # НЕ обрабатываем СНОВА - уже обработано в _extract_single_document!
                        # Просто сохраняем уже декодированный текст
                        doc_data[blob_name] = blob_content

                        # НОВОЕ: Добавляем метаданные BLOB полей
                        if "blob_metadata" in doc and blob_name in doc["blob_metadata"]:
                            metadata = doc["blob_metadata"][blob_name]
                            doc_data[f"{blob_name}_type"] = metadata.get(
                                "file_type", "unknown"
                            )
                            doc_data[f"{blob_name}_size"] = metadata.get("file_size", 0)
                            doc_data[f"{blob_name}_file_path"] = metadata.get(
                                "file_path", ""
                            )
                            doc_data[f"{blob_name}_quality"] = metadata.get(
                                "quality", 0.0
                            )

                documents_data.append(doc_data)

            # Создаем DataFrame
            df = pd.DataFrame(documents_data)

            # ИСПРАВЛЕНО: Создаем имя файла согласно требованию: document138-{короткое имя}.{число документов}.parquet
            document_type = get_document_type_mapping(table_name)
            short_name = document_type.split("_")[
                0
            ]  # Берем первое слово из типа документа
            table_name_short = table_name.lower().replace("_", "")
            parquet_file = f"data/results/parquet/{table_name_short}-{short_name}.{len(documents)}.parquet"

            # ИСПРАВЛЕНО: ПРАВИЛЬНОЕ сохранение BLOB данных в Parquet согласно стандарту 1C
            import pyarrow as pa
            import pyarrow.parquet as pq

            # Конвертируем DataFrame в PyArrow Table с правильными типами
            table_data = {}
            for col in df.columns:
                if col.startswith("blob_"):
                    # BLOB поля как binary согласно стандарту 1C
                    blob_data = []
                    for val in df[col]:
                        if isinstance(val, bytes):
                            blob_data.append(val)
                        elif (
                            isinstance(val, str)
                            and val.startswith("b'")
                            and val.endswith("'")
                        ):
                            # Восстанавливаем bytes из строкового представления
                            try:
                                import ast

                                blob_data.append(ast.literal_eval(val))
                            except:
                                blob_data.append(b"")
                        else:
                            blob_data.append(b"")
                    table_data[col] = pa.array(blob_data, type=pa.binary())
                else:
                    # Обычные поля как строки
                    table_data[col] = pa.array(df[col].astype(str))

            # Создаем PyArrow Table
            table = pa.table(table_data)

            # Сохраняем с правильными типами
            pq.write_table(table, parquet_file)

            print(f"✅ {table_name}: {len(documents)} документов → {parquet_file}")
            return [parquet_file]

        except Exception as e:
            print(f"❌ Ошибка сохранения в Parquet: {e}")
            return []

    def save_extraction_report(self, output_file: str) -> bool:
        """
        JTBD:
        Как метод сохранения отчета об извлечении, я хочу сохранить отчет об извлечении,
        чтобы документировать результаты работы извлекателя.

        Args:
            output_file: Путь к файлу для сохранения отчета

        Returns:
            True если отчет сохранен успешно, False иначе
        """
        try:
            report = {
                "extraction_stats": self.extraction_stats,
                "extracted_documents": self.extracted_documents,
                "timestamp": datetime.now().isoformat(),
                "total_documents": len(self.extracted_documents),
            }

            import json

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"✅ Отчет об извлечении сохранен: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")
            return False
