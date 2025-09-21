"""
ReferenceExtractor - извлекатель справочников из 1C базы данных.

Согласно плану рефакторинга, этот класс должен:
1. Извлекать 21 справочник из базы данных
2. Анализировать структуру справочников
3. Валидировать качество извлечения
4. Сохранять результаты в структурированном виде
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Добавляем путь к src для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from extractors.base_extractor import BaseExtractor
from processors.database_connector import DatabaseConnector


class ReferenceExtractor(BaseExtractor):
    """
    Извлекатель справочников из 1C базы данных.

    Согласно анализу данных, в базе есть 21 справочник:
    - Номенклатура, Склады, Подразделения, Контрагенты
    - Кассы, Единицы измерения, Цены, Скидки
    - И другие справочники
    """

    def __init__(self, db_path: str):
        """
        Инициализация извлекателя справочников.

        Args:
            db_path: Путь к файлу базы данных 1C
        """
        # Создаем DatabaseConnector
        db_connector = DatabaseConnector(db_path)
        super().__init__(db_connector)

        # Настраиваем логирование
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        self.references_data = []
        self.extraction_stats = {
            "total_references": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extraction_errors": [],
        }

    def extract(self, table_name: str, limit: int = 100) -> List[Dict]:
        """
        Реализация абстрактного метода extract из BaseExtractor.

        Args:
            table_name: Имя таблицы для извлечения
            limit: Максимальное количество элементов для извлечения

        Returns:
            Список извлеченных элементов
        """
        try:
            # Подключаемся к базе данных если не подключены
            if (
                not hasattr(self.db_connector, "_file_handle")
                or self.db_connector._file_handle is None
            ):
                self.db_connector.connect()

            # Получаем таблицу
            table = self.db_connector.get_table(table_name)
            if not table:
                return []

            extracted_data = []

            # Извлекаем данные с ограничением
            for i, row in enumerate(table):
                if i >= limit:
                    break

                # Обрабатываем строку
                processed_row = self.process_row(row, i, table_name)
                if processed_row:
                    extracted_data.append(processed_row)

            return extracted_data

        except Exception as e:
            self.log_extraction_error(e, {"table_name": table_name, "limit": limit})
            return []

    def extract_references(self) -> Dict[str, Any]:
        """
        Извлекает все справочники из базы данных.

        Returns:
            Словарь с результатами извлечения справочников
        """
        try:
            self.logger.info("🔍 Начинаю извлечение справочников...")

            # Подключаемся к базе данных
            self.db_connector.connect()

            # Получаем список всех таблиц
            all_tables = self.db_connector.get_tables()
            self.logger.info(f"📊 Найдено таблиц: {len(all_tables)}")

            # Фильтруем справочники
            reference_tables = self._filter_reference_tables(all_tables)
            self.logger.info(f"📊 Найдено справочников: {len(reference_tables)}")

            # Извлекаем каждый справочник
            for table_name, table_info in reference_tables.items():
                try:
                    self.logger.info(f"🔍 Извлекаю справочник: {table_name}")
                    reference_data = self._extract_single_reference(table_name)
                    if reference_data:
                        self.references_data.append(reference_data)
                        self.extraction_stats["successful_extractions"] += 1
                    else:
                        self.extraction_stats["failed_extractions"] += 1
                        self.extraction_stats["extraction_errors"].append(
                            f"Не удалось извлечь {table_name}"
                        )
                except Exception as e:
                    self.logger.error(f"❌ Ошибка при извлечении {table_name}: {e}")
                    self.extraction_stats["failed_extractions"] += 1
                    self.extraction_stats["extraction_errors"].append(
                        f"Ошибка в {table_name}: {str(e)}"
                    )

            self.extraction_stats["total_references"] = len(reference_tables)

            # Создаем результат
            result = {
                "extraction_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_references": self.extraction_stats["total_references"],
                    "successful_extractions": self.extraction_stats[
                        "successful_extractions"
                    ],
                    "failed_extractions": self.extraction_stats["failed_extractions"],
                },
                "references": self.references_data,
                "extraction_stats": self.extraction_stats,
            }

            self.logger.info(
                f"✅ Извлечение завершено: {self.extraction_stats['successful_extractions']}/{self.extraction_stats['total_references']} справочников"
            )
            return result

        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка при извлечении справочников: {e}")
            raise
        finally:
            self.db_connector.close()

    def _filter_reference_tables(self, all_tables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Фильтрует таблицы, оставляя только справочники.

        Args:
            all_tables: Словарь всех таблиц

        Returns:
            Словарь справочников
        """
        reference_tables = {}

        for table_name, table_info in all_tables.items():
            # Ищем таблицы справочников по паттернам
            if any(
                pattern in table_name.upper()
                for pattern in ["_REFERENCE", "REFERENCE_", "СПРАВОЧНИК"]
            ):
                reference_tables[table_name] = table_info
            # Также проверяем по содержимому
            elif (
                "reference" in table_name.lower() or "справочник" in table_name.lower()
            ):
                reference_tables[table_name] = table_info

        return reference_tables

    def _extract_single_reference(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает один справочник.

        Args:
            table_name: Имя таблицы справочника

        Returns:
            Данные справочника или None
        """
        try:
            # Убеждаемся, что база данных подключена
            if (
                not hasattr(self.db_connector, "_file_handle")
                or self.db_connector._file_handle is None
            ):
                self.db_connector.connect()

            # Получаем таблицу
            table = self.db_connector.get_table(table_name)
            if not table:
                return None

            # Анализируем структуру таблицы

            # Извлекаем данные
            reference_data = {
                "table_name": table_name,
                "type": self._determine_reference_type(table_name),
                "status": "extracted",
                "reference_data": {},
                "extraction_timestamp": datetime.now().isoformat(),
                "table_info": table_info,
            }

            # Извлекаем первые несколько записей для анализа
            try:
                sample_records = []
                for i, record in enumerate(table):
                    if i >= 5:  # Ограничиваемся 5 записями для анализа
                        break
                    # Конвертируем Row в словарь для JSON сериализации
                    if hasattr(record, "as_list"):
                        try:
                            record_list = record.as_list(True)
                            record_dict = {}

                            # Получаем реальные имена полей из метаданных таблицы
                            table = self.db_connector.get_table(table_name)
                            if hasattr(table, "fields"):
                                field_names = list(table.fields.keys())
                            else:
                                field_names = []

                            for j, value in enumerate(record_list):
                                # Используем реальные имена полей из метаданных
                                if j < len(field_names):
                                    field_name = field_names[j]
                                else:
                                    field_name = f"field_{j}"

                                # Правильная обработка BLOB данных
                                if hasattr(value, "value") and isinstance(
                                    value.value, bytes
                                ):
                                    # UTF-16 для NT полей (стандарт 1С)
                                    try:
                                        decoded_value = value.value.decode("utf-16")
                                        record_dict[field_name] = decoded_value
                                    except UnicodeDecodeError:
                                        try:
                                            decoded_value = value.value.decode("utf-8")
                                            record_dict[field_name] = decoded_value
                                        except UnicodeDecodeError:
                                            record_dict[field_name] = value.value.hex()
                                else:
                                    record_dict[field_name] = (
                                        str(value) if value is not None else None
                                    )
                            sample_records.append(record_dict)
                        except Exception as e:
                            self.logger.warning(
                                f"⚠️ Не удалось конвертировать запись {i}: {e}"
                            )
                            sample_records.append({"error": str(e), "field_count": 0})
                    else:
                        sample_records.append(
                            {
                                "error": "Не удалось получить данные записи",
                                "field_count": 0,
                            }
                        )

                reference_data["sample_records"] = sample_records
                reference_data["total_records"] = table_info.get("size", 0)

            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось извлечь записи из {table_name}: {e}")
                reference_data["sample_records"] = []
                reference_data["total_records"] = 0

            return reference_data

        except Exception as e:
            self.logger.error(f"❌ Ошибка при извлечении {table_name}: {e}")
            return None

    def _determine_reference_type(self, table_name: str) -> str:
        """
        Определяет тип справочника по имени таблицы и метаданным.

        Args:
            table_name: Имя таблицы

        Returns:
            Тип справочника
        """
        try:
            # Получаем метаданные таблицы для более точного определения

            # Анализируем содержимое таблицы для определения типа
            table = self.db_connector.get_table(table_name)
            if table:
                # Анализируем первые записи для определения типа
                sample_data = []
                for i, record in enumerate(table):
                    if i >= 3:  # Анализируем первые 3 записи
                        break
                    if hasattr(record, "as_list"):
                        try:
                            record_list = record.as_list(True)
                            sample_data.append([str(value) for value in record_list])
                        except:
                            continue

                # Анализируем содержимое для определения типа справочника
                if sample_data:
                    content_analysis = self._analyze_reference_content(
                        sample_data, table_name
                    )
                    if content_analysis != "Неизвестный справочник":
                        return content_analysis

            # Fallback на анализ имени таблицы
            type_mapping = {
                "Номенклатура": ["номенклатура", "товар", "product", "item"],
                "Склады": ["склад", "warehouse", "склады", "storage"],
                "Подразделения": ["подразделение", "department", "отдел", "division"],
                "Контрагенты": ["контрагент", "counterparty", "клиент", "partner"],
                "Кассы": ["касса", "cash", "кассы", "register"],
                "Единицы измерения": ["единица", "unit", "мера", "measure"],
                "Цены": ["цена", "price", "цены", "pricing"],
                "Скидки": ["скидка", "discount", "скидки", "discounts"],
            }

            table_lower = table_name.lower()
            for ref_type, keywords in type_mapping.items():
                if any(keyword in table_lower for keyword in keywords):
                    return ref_type

        except Exception as e:
            self.logger.warning(
                f"⚠️ Ошибка при определении типа справочника {table_name}: {e}"
            )

        return "Неизвестный справочник"

    def _analyze_reference_content(
        self, sample_data: List[List[str]], table_name: str
    ) -> str:
        """
        Анализирует содержимое справочника для определения его типа.

        Args:
            sample_data: Образцы данных из таблицы
            table_name: Имя таблицы

        Returns:
            Определенный тип справочника
        """
        # Объединяем все данные для анализа
        all_content = " ".join([" ".join(row) for row in sample_data]).lower()

        # Паттерны для определения типов справочников
        patterns = {
            "Номенклатура": ["товар", "product", "наименование", "артикул", "код"],
            "Склады": ["склад", "warehouse", "адрес", "место", "хранение"],
            "Контрагенты": [
                "контрагент",
                "клиент",
                "поставщик",
                "покупатель",
                "организация",
            ],
            "Подразделения": ["подразделение", "отдел", "department", "структура"],
            "Кассы": ["касса", "cash", "регистр", "регистратор"],
            "Единицы измерения": ["единица", "unit", "мера", "кг", "шт", "м"],
            "Цены": ["цена", "price", "стоимость", "руб", "рублей"],
            "Скидки": ["скидка", "discount", "процент", "%", "скидочная"],
        }

        # Подсчитываем совпадения для каждого типа
        type_scores = {}
        for ref_type, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in all_content)
            if score > 0:
                type_scores[ref_type] = score

        # Возвращаем тип с наибольшим количеством совпадений
        if type_scores:
            return max(type_scores, key=type_scores.get)

        return "Неизвестный справочник"

    def save_results(
        self, output_path: str = "data/results/references_extraction.json"
    ) -> str:
        """
        Сохраняет результаты извлечения справочников.

        Args:
            output_path: Путь для сохранения результатов

        Returns:
            Путь к сохраненному файлу
        """
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Сохраняем результаты
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.references_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 Результаты сохранены: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении результатов: {e}")
            raise

    def get_extraction_summary(self) -> Dict[str, Any]:
        """
        Возвращает сводку по извлечению справочников.

        Returns:
            Словарь со статистикой извлечения
        """
        return {
            "total_references": self.extraction_stats["total_references"],
            "successful_extractions": self.extraction_stats["successful_extractions"],
            "failed_extractions": self.extraction_stats["failed_extractions"],
            "success_rate": (
                self.extraction_stats["successful_extractions"]
                / max(self.extraction_stats["total_references"], 1)
                * 100
            ),
            "extraction_errors": self.extraction_stats["extraction_errors"],
        }


if __name__ == "__main__":
    # Тестирование ReferenceExtractor
    print("🔍 Тестирование ReferenceExtractor...")

    # Создаем экстрактор
    extractor = ReferenceExtractor("data/raw/1Cv8.1CD")

    # Извлекаем справочники
    results = extractor.extract_references()

    # Выводим результаты
    print(f"📊 Результаты извлечения:")
    print(f"   Всего справочников: {results['extraction_info']['total_references']}")
    print(
        f"   Успешно извлечено: {results['extraction_info']['successful_extractions']}"
    )
    print(f"   Ошибок: {results['extraction_info']['failed_extractions']}")

    # Сохраняем результаты
    output_path = extractor.save_results()
    print(f"💾 Результаты сохранены: {output_path}")
