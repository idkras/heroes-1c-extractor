#!/usr/bin/env python3
"""
StopIterationHandler - обработчик ошибок итерации в onec_dtools.

JTBD:
Как StopIterationHandler, я хочу обрабатывать ошибки StopIteration в onec_dtools,
чтобы обеспечить надежное извлечение данных из всех таблиц 1С без потери данных.

КРИТИЧЕСКИЕ ПРОБЛЕМЫ:
1. 47% справочников (144 из 306) не извлекаются из-за StopIteration ошибок
2. onec_dtools генерирует StopIteration для пустых или поврежденных BLOB полей
3. Неправильная обработка StopIteration приводит к потере данных
4. Отсутствует единая стратегия восстановления после ошибок итерации

РЕШЕНИЕ:
- Множественные стратегии итерации
- Автоматическое восстановление после ошибок
- Анализ причин StopIteration
- Альтернативные методы извлечения данных
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class IterationStrategy(Enum):
    """Стратегии итерации для обработки StopIteration"""

    STANDARD = "standard"  # Стандартная итерация
    SAFE = "safe"  # Безопасная итерация с обработкой ошибок
    CHUNKED = "chunked"  # Итерация по частям
    ALTERNATIVE = "alternative"  # Альтернативные методы
    RECOVERY = "recovery"  # Восстановление после ошибок


@dataclass
class IterationResult:
    """Результат итерации с метаданными"""

    data: List[Any]
    success: bool
    strategy_used: IterationStrategy
    errors: List[str]
    total_processed: int
    failed_count: int
    recovery_attempts: int


class StopIterationHandler:
    """
    Обработчик ошибок StopIteration для onec_dtools.

    КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ:
    - Множественные стратегии итерации
    - Автоматическое восстановление после ошибок
    - Анализ причин StopIteration
    - Альтернативные методы извлечения данных
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Инициализация StopIterationHandler

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or logging.getLogger(__name__)
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        self.chunk_size = 1000

    def handle_table_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        include_blobs: bool = True,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """
        Обрабатывает итерацию по таблице с множественными стратегиями

        Args:
            table: Таблица onec_dtools
            table_name: Имя таблицы
            limit: Лимит записей
            include_blobs: Включать ли BLOB поля
            process_row_func: Функция для обработки каждой строки (опционально)

        Returns:
            Результат итерации с метаданными
        """
        self.logger.info(f"🔄 Начинаем итерацию по таблице {table_name}")

        # Пробуем разные стратегии итерации
        strategies = [
            self._standard_iteration,
            self._safe_iteration,
            self._chunked_iteration,
            self._alternative_iteration,
            self._recovery_iteration,
        ]

        for strategy in strategies:
            try:
                result = strategy(
                    table, table_name, limit, include_blobs, process_row_func
                )
                if result.success:
                    self.logger.info(
                        f"✅ Стратегия {result.strategy_used.value} успешна для {table_name}"
                    )
                    return result
                else:
                    self.logger.warning(
                        f"⚠️ Стратегия {result.strategy_used.value} не удалась для {table_name}"
                    )
            except Exception as e:
                self.logger.error(f"❌ Ошибка стратегии {strategy.__name__}: {e}")
                continue

        # Если все стратегии не удались
        return IterationResult(
            data=[],
            success=False,
            strategy_used=IterationStrategy.RECOVERY,
            errors=["Все стратегии итерации не удались"],
            total_processed=0,
            failed_count=0,
            recovery_attempts=self.max_recovery_attempts,
        )

    def _standard_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        include_blobs: bool = True,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """Стандартная итерация по таблице"""
        data: list[Any] = []
        errors: list[str] = []
        processed = 0

        try:
            for i, row in enumerate(table):
                if limit and i >= limit:
                    break

                try:
                    # Если есть функция обработки строки, используем её
                    if process_row_func:
                        processed_row = process_row_func(row, i, table_name)
                        if processed_row:
                            data.append(processed_row)
                            processed += 1
                    else:
                        # Стандартная обработка
                        if include_blobs and hasattr(row, "as_list"):
                            row_data = row.as_list(True)
                        elif hasattr(row, "as_dict"):
                            row_data = row.as_dict()
                        else:
                            row_data = row

                        data.append(row_data)
                        processed += 1

                except StopIteration:
                    # Нормальное завершение итератора
                    break
                except Exception as e:
                    error_msg = f"Ошибка записи {i}: {e}"
                    errors.append(error_msg)
                    self.logger.warning(f"⚠️ {error_msg}")
                    continue

            return IterationResult(
                data=data,
                success=True,
                strategy_used=IterationStrategy.STANDARD,
                errors=errors,
                total_processed=processed,
                failed_count=len(errors),
                recovery_attempts=0,
            )

        except Exception as e:
            return IterationResult(
                data=data,
                success=False,
                strategy_used=IterationStrategy.STANDARD,
                errors=[f"Критическая ошибка стандартной итерации: {e}"],
                total_processed=processed,
                failed_count=len(errors) + 1,
                recovery_attempts=0,
            )

    def _safe_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        include_blobs: bool = True,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """Безопасная итерация с обработкой всех ошибок"""
        data: list[Any] = []
        errors: list[str] = []
        processed = 0

        try:
            iterator = iter(table)
            i = 0

            while True:
                if limit and i >= limit:
                    break

                try:
                    row = next(iterator)

                    try:
                        # Если есть функция обработки строки, используем её
                        if process_row_func:
                            processed_row = process_row_func(row, i, table_name)
                            if processed_row:
                                data.append(processed_row)
                                processed += 1
                        else:
                            # Стандартная обработка
                            if include_blobs and hasattr(row, "as_list"):
                                row_data = row.as_list(True)
                            elif hasattr(row, "as_dict"):
                                row_data = row.as_dict()
                            else:
                                row_data = row

                            data.append(row_data)
                            processed += 1

                    except StopIteration:
                        # Нормальное завершение итератора
                        break
                    except Exception as e:
                        error_msg = f"Ошибка обработки записи {i}: {e}"
                        errors.append(error_msg)
                        self.logger.warning(f"⚠️ {error_msg}")
                        continue

                    i += 1

                except StopIteration:
                    # Нормальное завершение итератора
                    break
                except Exception as e:
                    error_msg = f"Ошибка итерации {i}: {e}"
                    errors.append(error_msg)
                    self.logger.warning(f"⚠️ {error_msg}")
                    i += 1
                    continue

            return IterationResult(
                data=data,
                success=True,
                strategy_used=IterationStrategy.SAFE,
                errors=errors,
                total_processed=processed,
                failed_count=len(errors),
                recovery_attempts=0,
            )

        except Exception as e:
            return IterationResult(
                data=data,
                success=False,
                strategy_used=IterationStrategy.SAFE,
                errors=[f"Критическая ошибка безопасной итерации: {e}"],
                total_processed=processed,
                failed_count=len(errors) + 1,
                recovery_attempts=0,
            )

    def _chunked_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        include_blobs: bool = True,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """Итерация по частям для больших таблиц"""
        data: list[Any] = []
        errors: list[str] = []
        processed = 0

        try:
            # Получаем размер таблицы
            table_size = len(table) if hasattr(table, "__len__") else None

            if table_size and table_size > self.chunk_size:
                self.logger.info(
                    f"📊 Таблица {table_name} большая ({table_size} записей), используем chunked итерацию"
                )

                # Итерация по частям
                for chunk_start in range(0, table_size, self.chunk_size):
                    if limit and processed >= limit:
                        break

                    chunk_end = min(chunk_start + self.chunk_size, table_size)
                    if limit:
                        chunk_end = min(chunk_end, chunk_start + limit - processed)

                    try:
                        # Извлекаем чанк
                        chunk_data: list[Any] = []
                        for i in range(chunk_start, chunk_end):
                            try:
                                row = table[i]

                                # Если есть функция обработки строки, используем её
                                if process_row_func:
                                    processed_row = process_row_func(row, i, table_name)
                                    if processed_row:
                                        chunk_data.append(processed_row)
                                        processed += 1
                                else:
                                    # Стандартная обработка
                                    if include_blobs and hasattr(row, "as_list"):
                                        row_data = row.as_list(True)
                                    elif hasattr(row, "as_dict"):
                                        row_data = row.as_dict()
                                    else:
                                        row_data = row

                                    chunk_data.append(row_data)
                                    processed += 1

                            except StopIteration:
                                break
                            except Exception as e:
                                error_msg = f"Ошибка записи {i} в чанке {chunk_start}-{chunk_end}: {e}"
                                errors.append(error_msg)
                                self.logger.warning(f"⚠️ {error_msg}")
                                continue

                        data.extend(chunk_data)

                    except Exception as e:
                        error_msg = f"Ошибка чанка {chunk_start}-{chunk_end}: {e}"
                        errors.append(error_msg)
                        self.logger.warning(f"⚠️ {error_msg}")
                        continue
            else:
                # Для маленьких таблиц используем стандартную итерацию
                return self._standard_iteration(
                    table, table_name, limit, include_blobs, process_row_func
                )

            return IterationResult(
                data=data,
                success=True,
                strategy_used=IterationStrategy.CHUNKED,
                errors=errors,
                total_processed=processed,
                failed_count=len(errors),
                recovery_attempts=0,
            )

        except Exception as e:
            return IterationResult(
                data=data,
                success=False,
                strategy_used=IterationStrategy.CHUNKED,
                errors=[f"Критическая ошибка chunked итерации: {e}"],
                total_processed=processed,
                failed_count=len(errors) + 1,
                recovery_attempts=0,
            )

    def _alternative_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        include_blobs: bool = True,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """Альтернативные методы итерации"""
        data: list[Any] = []
        errors: list[str] = []
        processed = 0

        try:
            # Метод 1: Прямой доступ по индексу
            if hasattr(table, "__len__"):
                table_size = len(table)
                max_records = min(limit or table_size, table_size)

                for i in range(max_records):
                    try:
                        row = table[i]

                        # Если есть функция обработки строки, используем её
                        if process_row_func:
                            processed_row = process_row_func(row, i, table_name)
                            if processed_row:
                                data.append(processed_row)
                                processed += 1
                        else:
                            # Стандартная обработка
                            if include_blobs and hasattr(row, "as_list"):
                                row_data = row.as_list(True)
                            elif hasattr(row, "as_dict"):
                                row_data = row.as_dict()
                            else:
                                row_data = row

                            data.append(row_data)
                            processed += 1

                    except StopIteration:
                        break
                    except Exception as e:
                        error_msg = f"Ошибка прямого доступа к записи {i}: {e}"
                        errors.append(error_msg)
                        self.logger.warning(f"⚠️ {error_msg}")
                        continue

                return IterationResult(
                    data=data,
                    success=True,
                    strategy_used=IterationStrategy.ALTERNATIVE,
                    errors=errors,
                    total_processed=processed,
                    failed_count=len(errors),
                    recovery_attempts=0,
                )
            else:
                # Fallback к безопасной итерации
                return self._safe_iteration(
                    table, table_name, limit, include_blobs, process_row_func
                )

        except Exception as e:
            return IterationResult(
                data=data,
                success=False,
                strategy_used=IterationStrategy.ALTERNATIVE,
                errors=[f"Критическая ошибка альтернативной итерации: {e}"],
                total_processed=processed,
                failed_count=len(errors) + 1,
                recovery_attempts=0,
            )

    def _recovery_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        include_blobs: bool = True,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """Восстановление после ошибок с множественными попытками"""
        data: list[Any] = []
        errors: list[str] = []
        processed = 0

        for attempt in range(self.max_recovery_attempts):
            self.logger.info(
                f"🔄 Попытка восстановления {attempt + 1}/{self.max_recovery_attempts} для {table_name}"
            )

            try:
                # Пробуем разные методы восстановления
                if attempt == 0:
                    # Попытка 1: Без BLOB полей
                    result = self._safe_iteration(
                        table,
                        table_name,
                        limit,
                        include_blobs=False,
                        process_row_func=process_row_func,
                    )
                elif attempt == 1:
                    # Попытка 2: Только основные поля
                    result = self._alternative_iteration(
                        table,
                        table_name,
                        limit,
                        include_blobs=False,
                        process_row_func=process_row_func,
                    )
                else:
                    # Попытка 3: Минимальная итерация
                    result = self._minimal_iteration(
                        table, table_name, limit, process_row_func
                    )

                if result.success:
                    self.logger.info(
                        f"✅ Восстановление успешно на попытке {attempt + 1}"
                    )
                    return result
                else:
                    errors.extend(result.errors)
                    self.logger.warning(
                        f"⚠️ Попытка восстановления {attempt + 1} не удалась"
                    )

            except Exception as e:
                error_msg = f"Ошибка попытки восстановления {attempt + 1}: {e}"
                errors.append(error_msg)
                self.logger.error(f"❌ {error_msg}")
                continue

        return IterationResult(
            data=data,
            success=False,
            strategy_used=IterationStrategy.RECOVERY,
            errors=errors,
            total_processed=processed,
            failed_count=len(errors),
            recovery_attempts=self.max_recovery_attempts,
        )

    def _minimal_iteration(
        self,
        table: Any,
        table_name: str,
        limit: Optional[int] = None,
        process_row_func: Optional[Callable] = None,
    ) -> IterationResult:
        """Минимальная итерация для критических случаев"""
        data: list[Any] = []
        errors: list[str] = []
        processed = 0

        try:
            # Минимальная итерация - только основные поля
            for i, row in enumerate(table):
                if limit and i >= limit:
                    break

                try:
                    # Если есть функция обработки строки, используем её
                    if process_row_func:
                        processed_row = process_row_func(row, i, table_name)
                        if processed_row:
                            data.append(processed_row)
                            processed += 1
                    else:
                        # Минимальная обработка - только базовые поля
                        row_data = {
                            "index": i,
                            "table_name": table_name,
                            "has_data": True,
                        }

                        # Пробуем получить только основные поля
                        if hasattr(row, "as_dict"):
                            try:
                                basic_data = row.as_dict()
                                row_data.update(basic_data)
                            except:
                                pass

                        data.append(row_data)
                        processed += 1

                except StopIteration:
                    break
                except Exception as e:
                    error_msg = f"Ошибка минимальной обработки записи {i}: {e}"
                    errors.append(error_msg)
                    continue

            return IterationResult(
                data=data,
                success=True,
                strategy_used=IterationStrategy.RECOVERY,
                errors=errors,
                total_processed=processed,
                failed_count=len(errors),
                recovery_attempts=0,
            )

        except Exception as e:
            return IterationResult(
                data=data,
                success=False,
                strategy_used=IterationStrategy.RECOVERY,
                errors=[f"Критическая ошибка минимальной итерации: {e}"],
                total_processed=processed,
                failed_count=len(errors) + 1,
                recovery_attempts=0,
            )

    def analyze_stopiteration_causes(
        self, table: Any, table_name: str
    ) -> Dict[str, Any]:
        """
        Анализирует причины StopIteration ошибок

        Args:
            table: Таблица для анализа
            table_name: Имя таблицы

        Returns:
            Словарь с анализом причин
        """
        analysis: Dict[str, Any] = {
            "table_name": table_name,
            "table_size": 0,
            "has_blob_fields": False,
            "iteration_problems": [],
            "recommendations": [],
        }

        # Типизируем списки для MyPy
        iteration_problems: list[str] = analysis["iteration_problems"]
        recommendations: list[str] = analysis["recommendations"]

        try:
            # Анализируем размер таблицы
            if hasattr(table, "__len__"):
                analysis["table_size"] = len(table)

            # Анализируем структуру таблицы
            if analysis["table_size"] > 0:
                try:
                    # Пробуем получить первую запись
                    first_row = table[0]
                    if hasattr(first_row, "as_list"):
                        try:
                            row_list = first_row.as_list(True)
                            analysis["has_blob_fields"] = any(
                                isinstance(field, bytes)
                                or (
                                    hasattr(field, "value")
                                    and isinstance(field.value, bytes)
                                )
                                for field in row_list
                            )
                        except:
                            pass
                except:
                    pass

            # Определяем проблемы
            if analysis["table_size"] == 0:
                iteration_problems.append("Пустая таблица")
                recommendations.append("Пропустить таблицу")
            elif analysis["table_size"] > 1000000:
                iteration_problems.append("Очень большая таблица")
                recommendations.append("Использовать chunked итерацию")
            elif analysis["has_blob_fields"]:
                iteration_problems.append("BLOB поля могут вызывать StopIteration")
                recommendations.append("Использовать безопасную итерацию")
            else:
                iteration_problems.append("Неизвестные проблемы")
                recommendations.append("Попробовать все стратегии")

        except Exception as e:
            iteration_problems.append(f"Ошибка анализа: {e}")
            recommendations.append("Использовать восстановление")

        # Обновляем словарь с типизированными списками
        analysis["iteration_problems"] = iteration_problems
        analysis["recommendations"] = recommendations

        return analysis
