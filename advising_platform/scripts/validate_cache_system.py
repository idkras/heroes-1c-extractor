#!/usr/bin/env python3
"""
Скрипт для автоматической валидации системы кэширования документов.

Проверяет основные функции API кэша и его интеграцию с системой архивации.
Результаты валидации записываются в лог.
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cache_validation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cache_validator")

class CacheValidator:
    """
    Класс для валидации системы кэширования.
    """
    
    def __init__(self, api_base_url="http://localhost:5003", working_dir="."):
        """
        Инициализирует валидатор кэша.
        
        Args:
            api_base_url: Базовый URL API сервера
            working_dir: Рабочая директория для создания тестовых файлов
        """
        self.api_base_url = api_base_url
        self.cache_api = f"{api_base_url}/api/cache"
        self.working_dir = Path(working_dir)
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def run_all_tests(self):
        """
        Запускает все тесты валидации.
        
        Returns:
            Результаты тестирования
        """
        logger.info("Начало валидации системы кэширования")
        
        # Запускаем тесты
        self._test_cache_stats()
        self._test_get_document()
        self._test_cache_invalidation()
        self._test_preload_directory()
        self._test_clear_cache()
        self._test_file_watcher()
        self._test_archive_integration()
        
        # Выводим итоговые результаты
        success_rate = (self.test_results["passed_tests"] / self.test_results["total_tests"]) * 100 if self.test_results["total_tests"] > 0 else 0
        logger.info(f"Валидация завершена. Успешных тестов: {self.test_results['passed_tests']}/{self.test_results['total_tests']} ({success_rate:.1f}%)")
        
        return self.test_results
    
    def _record_test_result(self, test_name, passed, details=""):
        """
        Записывает результат теста.
        
        Args:
            test_name: Название теста
            passed: Результат (True - успешно, False - ошибка)
            details: Дополнительная информация о тесте
        """
        self.test_results["total_tests"] += 1
        if passed:
            self.test_results["passed_tests"] += 1
            logger.info(f"✅ ТЕСТ ПРОЙДЕН: {test_name}")
        else:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ ТЕСТ НЕ ПРОЙДЕН: {test_name}")
        
        self.test_results["test_details"].append({
            "name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def _test_cache_stats(self):
        """
        Проверяет получение статистики кэша.
        """
        test_name = "Получение статистики кэша"
        
        try:
            response = requests.get(f"{self.cache_api}/stats")
            if response.status_code == 200:
                stats = response.json()
                
                # Проверяем наличие ключевых полей
                required_keys = ["cache_size", "max_cache_size", "hit_count", "miss_count", "uptime_seconds"]
                all_keys_present = all(key in stats for key in required_keys)
                
                if all_keys_present:
                    details = f"Размер кэша: {stats['cache_size']}/{stats['max_cache_size']}, Hit rate: {stats.get('hit_rate', 0)}"
                    self._record_test_result(test_name, True, details)
                else:
                    missing_keys = [key for key in required_keys if key not in stats]
                    self._record_test_result(test_name, False, f"Отсутствуют ключевые поля: {missing_keys}")
            else:
                self._record_test_result(test_name, False, f"Код ответа: {response.status_code}, тело: {response.text}")
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
    
    def _test_get_document(self):
        """
        Проверяет получение документа из кэша.
        """
        test_name = "Получение документа из кэша"
        test_document = "[standards .md]/communication-protocol-20250515.md"
        
        try:
            response = requests.get(f"{self.cache_api}/get", params={"path": test_document})
            if response.status_code == 200:
                data = response.json()
                
                if "content" in data and len(data["content"]) > 0:
                    self._record_test_result(test_name, True, f"Получен документ: {test_document}")
                else:
                    self._record_test_result(test_name, False, "Документ получен, но содержимое пустое")
            else:
                self._record_test_result(test_name, False, f"Код ответа: {response.status_code}, тело: {response.text}")
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
    
    def _test_cache_invalidation(self):
        """
        Проверяет инвалидацию документа в кэше.
        """
        test_name = "Инвалидация документа в кэше"
        test_document = "[standards .md]/communication-protocol-20250515.md"
        
        try:
            # Сначала получаем документ, чтобы он точно был в кэше
            pre_request = requests.get(f"{self.cache_api}/get", params={"path": test_document})
            
            # Теперь инвалидируем его
            response = requests.post(
                f"{self.cache_api}/invalidate",
                json={"path": test_document},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success", False):
                    self._record_test_result(test_name, True, f"Инвалидирован документ: {test_document}")
                else:
                    self._record_test_result(test_name, False, f"Инвалидация не выполнена: {data.get('error', 'Неизвестная ошибка')}")
            else:
                self._record_test_result(test_name, False, f"Код ответа: {response.status_code}, тело: {response.text}")
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
    
    def _test_preload_directory(self):
        """
        Проверяет предзагрузку директории в кэш.
        """
        test_name = "Предзагрузка директории в кэш"
        test_directory = "[standards .md]"
        
        try:
            response = requests.post(
                f"{self.cache_api}/preload",
                json={"directory": test_directory, "recursive": True},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success", False):
                    self._record_test_result(test_name, True, f"Предзагружено {data.get('count', 0)} документов из {test_directory}")
                else:
                    self._record_test_result(test_name, False, f"Предзагрузка не выполнена: {data.get('error', 'Неизвестная ошибка')}")
            else:
                self._record_test_result(test_name, False, f"Код ответа: {response.status_code}, тело: {response.text}")
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
    
    def _test_clear_cache(self):
        """
        Проверяет очистку кэша.
        """
        test_name = "Очистка кэша"
        
        try:
            response = requests.post(f"{self.cache_api}/clear")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success", False):
                    self._record_test_result(test_name, True, f"Удалено {data.get('count', 0)} документов из кэша")
                else:
                    self._record_test_result(test_name, False, f"Очистка не выполнена: {data.get('error', 'Неизвестная ошибка')}")
            else:
                self._record_test_result(test_name, False, f"Код ответа: {response.status_code}, тело: {response.text}")
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
    
    def _test_file_watcher(self):
        """
        Проверяет отслеживание изменений в файлах.
        """
        test_name = "Отслеживание изменений в файлах"
        test_file_path = self.working_dir / "[todo · incidents]/test_cache_file.md"
        
        try:
            # Создаем тестовый файл
            with open(test_file_path, "w") as f:
                f.write("# Тестовый документ для валидации кэша\n\nЭтот файл будет удален автоматически.")
            
            logger.info(f"Создан тестовый файл: {test_file_path}")
            time.sleep(1)  # Даем время на обработку файловой системой
            
            # Получаем документ из кэша (должен быть miss, так как файл новый)
            response1 = requests.get(f"{self.cache_api}/get", params={"path": str(test_file_path)})
            
            # Изменяем файл
            with open(test_file_path, "a") as f:
                f.write("\n\nДобавлена новая строка для проверки отслеживания изменений.")
            
            logger.info(f"Тестовый файл изменен: {test_file_path}")
            time.sleep(2)  # Даем время на обработку изменений
            
            # Снова получаем документ (должна быть актуальная версия)
            response2 = requests.get(f"{self.cache_api}/get", params={"path": str(test_file_path)})
            
            # Удаляем тестовый файл
            test_file_path.unlink()
            logger.info(f"Тестовый файл удален: {test_file_path}")
            
            # Проверяем результаты
            if response1.status_code == 200 and response2.status_code == 200:
                content1 = response1.json().get("content", "")
                content2 = response2.json().get("content", "")
                
                if "Добавлена новая строка" in content2 and "Добавлена новая строка" not in content1:
                    self._record_test_result(test_name, True, "Файловый наблюдатель корректно отслеживает изменения")
                else:
                    self._record_test_result(test_name, False, "Изменения в файле не отслеживаются корректно")
            else:
                self._record_test_result(test_name, False, "Ошибка при получении документа")
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
            try:
                if test_file_path.exists():
                    test_file_path.unlink()
            except:
                pass
    
    def _test_archive_integration(self):
        """
        Проверяет интеграцию с системой архивации.
        """
        test_name = "Интеграция с системой архивации"
        
        # Путь к тестовому документу для архивации
        test_file_path = self.working_dir / "[todo · incidents]/test_archive_integration.md"
        archived_path = self.working_dir / "[todo · incidents]/[archive]/test_archive_integration.md"
        
        try:
            # Создаем директорию архива, если её нет
            archive_dir = self.working_dir / "[todo · incidents]/[archive]"
            if not archive_dir.exists():
                archive_dir.mkdir(exist_ok=True)
                logger.info(f"Создана директория архива: {archive_dir}")
            
            # Создаем тестовый файл
            with open(test_file_path, "w") as f:
                f.write("""# Тестовый документ для проверки архивации

date: 15 May 2025
version: 1.0
author: AI Assistant
type: task
category: test
status: done
priority: SMALL TASK

## Описание

Этот документ будет перемещен в архив для тестирования интеграции.
""")
            
            logger.info(f"Создан тестовый файл: {test_file_path}")
            time.sleep(1)  # Даем время на обработку файловой системой
            
            # Получаем документ из кэша
            response1 = requests.get(f"{self.cache_api}/get", params={"path": str(test_file_path)})
            
            # Имитируем архивацию (перемещаем файл)
            import shutil
            shutil.move(str(test_file_path), str(archived_path))
            logger.info(f"Тестовый файл перемещен в архив: {test_file_path} -> {archived_path}")
            time.sleep(2)  # Даем время на обработку изменений
            
            # Проверяем, что документ больше недоступен по старому пути
            response2 = requests.get(f"{self.cache_api}/get", params={"path": str(test_file_path)})
            
            # Проверяем, что документ доступен по новому пути
            response3 = requests.get(f"{self.cache_api}/get", params={"path": str(archived_path)})
            
            # Удаляем тестовый файл
            archived_path.unlink()
            logger.info(f"Тестовый файл удален: {archived_path}")
            
            # Анализируем результаты
            cache_invalidated = response2.json().get("error") is not None or response2.json().get("content", "") == ""
            archive_cached = response3.status_code == 200 and len(response3.json().get("content", "")) > 0
            
            if cache_invalidated and archive_cached:
                self._record_test_result(test_name, True, "Архивация корректно отслеживается системой кэширования")
            else:
                details = f"Инвалидация оригинала: {'✓' if cache_invalidated else '✗'}, Кэширование архива: {'✓' if archive_cached else '✗'}"
                self._record_test_result(test_name, False, f"Проблемы с отслеживанием архивации: {details}")
        
        except Exception as e:
            self._record_test_result(test_name, False, f"Исключение: {str(e)}")
            try:
                if test_file_path.exists():
                    test_file_path.unlink()
                if archived_path.exists():
                    archived_path.unlink()
            except:
                pass

def main():
    """
    Основная функция скрипта.
    """
    parser = argparse.ArgumentParser(description="Валидация системы кэширования документов")
    parser.add_argument("--api-url", default="http://localhost:5003", help="Базовый URL API сервера")
    parser.add_argument("--working-dir", default=".", help="Рабочая директория для создания тестовых файлов")
    parser.add_argument("--report", default="cache_validation_report.json", help="Путь для сохранения отчета о валидации")
    args = parser.parse_args()
    
    # Запускаем валидацию
    validator = CacheValidator(api_base_url=args.api_url, working_dir=args.working_dir)
    results = validator.run_all_tests()
    
    # Сохраняем отчет
    with open(args.report, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Отчет о валидации сохранен в: {args.report}")
    
    # Выходим с кодом ошибки, если есть проблемы
    if results["failed_tests"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()