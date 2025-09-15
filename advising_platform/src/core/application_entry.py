#!/usr/bin/env python3
"""
Единый entry point для всех модулей платформы.

Цель: Устранить дублирование 182+ функций main() в кодовой базе.
Все модули должны импортировать и использовать этот единый entry point.

Автор: AI Assistant
Дата: 22 May 2025
"""

import sys
import os
import logging
from pathlib import Path
from typing import Callable, Dict, Any, Optional


class ApplicationEntry:
    """Единый entry point для всех модулей платформы."""
    
    def __init__(self, module_name: str = None):
        """
        Инициализация entry point.
        
        Args:
            module_name: Имя модуля, который использует entry point
        """
        self.module_name = module_name or self._get_calling_module()
        self.logger = self._setup_logging()
        
    def _get_calling_module(self) -> str:
        """Определяет имя вызывающего модуля."""
        import inspect
        frame = inspect.currentframe()
        try:
            # Поднимаемся по стеку до вызывающего модуля
            caller_frame = frame.f_back.f_back
            if caller_frame:
                return Path(caller_frame.f_code.co_filename).stem
            return "unknown_module"
        finally:
            del frame
    
    def _setup_logging(self) -> logging.Logger:
        """Настройка логирования для модуля."""
        logger = logging.getLogger(self.module_name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.module_name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def run_main(self, main_function: Callable, *args, **kwargs) -> Any:
        """
        Запускает main функцию модуля с единым обработчиком ошибок.
        
        Args:
            main_function: Функция main модуля
            *args: Позиционные аргументы для main
            **kwargs: Именованные аргументы для main
            
        Returns:
            Результат выполнения main функции
        """
        try:
            self.logger.info(f"Запуск модуля {self.module_name}")
            
            # Устанавливаем рабочую директорию
            self._setup_working_directory()
            
            # Добавляем пути к модулям
            self._setup_module_paths()
            
            # Запускаем main функцию
            result = main_function(*args, **kwargs)
            
            self.logger.info(f"Модуль {self.module_name} завершился успешно")
            return result
            
        except KeyboardInterrupt:
            self.logger.info(f"Модуль {self.module_name} прерван пользователем")
            return 130  # Стандартный код для Ctrl+C
            
        except Exception as e:
            self.logger.error(f"Ошибка в модуле {self.module_name}: {e}")
            self.logger.debug(f"Полная трассировка:", exc_info=True)
            return 1
    
    def _setup_working_directory(self):
        """Устанавливает правильную рабочую директорию."""
        # Определяем корневую директорию проекта
        current_dir = Path.cwd()
        
        # Если мы в подпапке, поднимаемся до корня проекта
        if 'advising_platform' in str(current_dir):
            while current_dir.name != 'advising_platform' and current_dir.parent != current_dir:
                current_dir = current_dir.parent
            
            if current_dir.name == 'advising_platform':
                os.chdir(current_dir)
    
    def _setup_module_paths(self):
        """Добавляет необходимые пути к модулям."""
        current_dir = Path.cwd()
        
        # Добавляем основные пути
        paths_to_add = [
            str(current_dir),
            str(current_dir / 'src'),
            str(current_dir / 'src' / 'core'),
            str(current_dir / 'src' / 'cache'),
            str(current_dir / 'src' / 'api'),
        ]
        
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
    
    def run_cli_main(self, main_function: Callable, description: str = None) -> Any:
        """
        Запускает CLI main функцию с обработкой аргументов.
        
        Args:
            main_function: Функция main для CLI
            description: Описание CLI модуля
            
        Returns:
            Результат выполнения
        """
        import argparse
        
        parser = argparse.ArgumentParser(
            description=description or f"CLI модуль {self.module_name}"
        )
        parser.add_argument(
            '--verbose', '-v', 
            action='store_true',
            help='Включить подробный вывод'
        )
        parser.add_argument(
            '--debug',
            action='store_true', 
            help='Включить режим отладки'
        )
        
        args = parser.parse_args()
        
        if args.debug:
            self.logger.setLevel(logging.DEBUG)
        elif args.verbose:
            self.logger.setLevel(logging.INFO)
        
        return self.run_main(main_function, args)
    
    def run_test_main(self, main_function: Callable) -> Any:
        """
        Запускает test main функцию.
        
        Args:
            main_function: Функция main для тестов
            
        Returns:
            Результат выполнения тестов
        """
        self.logger.info(f"Запуск тестов в модуле {self.module_name}")
        return self.run_main(main_function)


def create_entry_point(module_name: str = None) -> ApplicationEntry:
    """
    Создает entry point для модуля.
    
    Args:
        module_name: Имя модуля (определяется автоматически если не указан)
        
    Returns:
        Экземпляр ApplicationEntry
    """
    return ApplicationEntry(module_name)


def run_main(main_function: Callable, *args, **kwargs) -> Any:
    """
    Быстрый запуск main функции через единый entry point.
    
    Args:
        main_function: Функция main модуля
        *args: Позиционные аргументы
        **kwargs: Именованные аргументы
        
    Returns:
        Результат выполнения
    """
    entry = create_entry_point()
    return entry.run_main(main_function, *args, **kwargs)


def run_cli_main(main_function: Callable, description: str = None) -> Any:
    """
    Быстрый запуск CLI main функции.
    
    Args:
        main_function: Функция main для CLI
        description: Описание CLI
        
    Returns:
        Результат выполнения
    """
    entry = create_entry_point()
    return entry.run_cli_main(main_function, description)


def run_test_main(main_function: Callable) -> Any:
    """
    Быстрый запуск test main функции.
    
    Args:
        main_function: Функция main для тестов
        
    Returns:
        Результат выполнения
    """
    entry = create_entry_point()
    return entry.run_test_main(main_function)


# Пример использования в модулях:
# 
# Старый код:
# def main():
#     # код модуля
#     pass
# 
# if __name__ == '__main__':
#     main()
#
# Новый код:
# from src.core.application_entry import run_main
# 
# def main():
#     # код модуля  
#     pass
#
# if __name__ == '__main__':
#     run_main(main)