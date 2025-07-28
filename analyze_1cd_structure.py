#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ структуры файла 1Cv8.1CD с поддержкой Docker
"""

import os
import sys
import subprocess
import csv
import json
import tempfile
import time
import logging
from pathlib import Path
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('1cd_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OneCDAnalyzer:
    """Класс для анализа файлов 1CD"""
    
    def __init__(self, ctool1cd_path=None, use_docker=True):
        self.ctool1cd_path = ctool1cd_path
        self.use_docker = use_docker
        self.results = {}
        
    def check_docker_available(self):
        """Проверка доступности Docker"""
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def extract_ctool1cd(self):
        """Извлечение утилиты ctool1cd из архива"""
        logger.info("Извлечение утилиты ctool1cd...")
        
        template_path = Path("tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin")
        
        if not template_path.exists():
            logger.error("Архив с утилитой ctool1cd не найден")
            return None
        
        import zipfile
        temp_dir = Path(tempfile.mkdtemp(prefix="ctool1cd_"))
        
        try:
            with zipfile.ZipFile(template_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            logger.info(f"Утилита извлечена в: {temp_dir}")
            
            # Определяем путь к исполняемому файлу
            executable = temp_dir / "linux" / "ctool1cd"
            
            if executable.exists():
                logger.info(f"Исполняемый файл найден: {executable}")
                return executable
            else:
                logger.error(f"Исполняемый файл не найден: {executable}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при извлечении: {e}")
            return None
    
    def build_docker_image(self):
        """Сборка Docker образа с ctool1cd"""
        logger.info("Сборка Docker образа...")
        
        try:
            result = subprocess.run([
                'docker', 'build', '-t', 'ctool1cd', '.'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Docker образ успешно собран")
                return True
            else:
                logger.error(f"Ошибка при сборке образа: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при сборке Docker образа")
            return False
        except Exception as e:
            logger.error(f"Ошибка при сборке: {e}")
            return False
    
    def analyze_file_docker(self, file_path, output_csv=None):
        """Анализ файла через Docker"""
        logger.info(f"Анализ файла через Docker: {file_path}")
        
        # Создаем временные файлы
        temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        
        try:
            # Формируем команду Docker
            cmd = [
                'docker', 'run', '--rm',
                '-v', f'{os.getcwd()}:/data',
                'ctool1cd',
                '-ne',  # Не создавать пустые файлы
                '-sts', '/data/temp_output.csv',  # Статистика в CSV
                '-q', f'/data/{Path(file_path).name}',  # Путь к файлу 1CD
                '-l', '/data/temp_log.txt'  # Лог файл
            ]
            
            logger.info(f"Запуск команды: {' '.join(cmd)}")
            
            # Запускаем Docker контейнер
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 час таймаут
            end_time = time.time()
            
            logger.info(f"Время выполнения: {end_time - start_time:.2f} секунд")
            
            if result.returncode == 0:
                logger.info("Анализ завершен успешно")
                
                # Читаем результаты
                csv_path = Path("temp_output.csv")
                if csv_path.exists():
                    return self.parse_csv_results(csv_path, output_csv)
                else:
                    logger.error("CSV файл с результатами не найден")
                    return None
                    
            else:
                logger.error(f"Ошибка при анализе (код: {result.returncode})")
                if result.stderr:
                    logger.error(f"Ошибка: {result.stderr}")
                
                # Пытаемся прочитать лог
                log_path = Path("temp_log.txt")
                if log_path.exists():
                    with open(log_path, 'r', encoding='utf-8') as logfile:
                        log_content = logfile.read()
                        if log_content:
                            logger.error(f"Лог ошибки: {log_content}")
                
                return None
                
        finally:
            # Удаляем временные файлы
            for temp_file in [temp_csv.name, temp_log.name]:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def analyze_file_native(self, file_path, output_csv=None):
        """Анализ файла нативной утилитой"""
        logger.info(f"Анализ файла нативной утилитой: {file_path}")
        
        if not self.ctool1cd_path:
            self.ctool1cd_path = self.extract_ctool1cd()
        
        if not self.ctool1cd_path:
            logger.error("Не удалось найти утилиту ctool1cd")
            return None
        
        # Создаем временные файлы
        temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        
        try:
            # Формируем команду
            cmd = [
                str(self.ctool1cd_path),
                '-ne',  # Не создавать пустые файлы
                '-sts', temp_csv.name,  # Статистика в CSV
                '-q', str(file_path),    # Путь к файлу 1CD
                '-l', temp_log.name     # Лог файл
            ]
            
            logger.info(f"Запуск команды: {' '.join(cmd)}")
            
            # Запускаем утилиту
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            end_time = time.time()
            
            logger.info(f"Время выполнения: {end_time - start_time:.2f} секунд")
            
            if result.returncode == 0:
                logger.info("Анализ завершен успешно")
                return self.parse_csv_results(Path(temp_csv.name), output_csv)
            else:
                logger.error(f"Ошибка при анализе (код: {result.returncode})")
                if result.stderr:
                    logger.error(f"Ошибка: {result.stderr}")
                return None
                
        finally:
            # Удаляем временные файлы
            for temp_file in [temp_csv.name, temp_log.name]:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def parse_csv_results(self, csv_path, output_csv=None):
        """Парсинг результатов CSV"""
        logger.info(f"Парсинг результатов из: {csv_path}")
        
        try:
            tables_info = []
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='|')
                for row in reader:
                    tables_info.append(row)
            
            logger.info(f"Найдено таблиц: {len(tables_info)}")
            
            # Сохраняем в указанный файл если нужно
            if output_csv:
                import shutil
                shutil.copy2(csv_path, output_csv)
                logger.info(f"Результаты сохранены в: {output_csv}")
            
            return tables_info
            
        except Exception as e:
            logger.error(f"Ошибка при чтении результатов: {e}")
            return None
    
    def generate_report(self, results, output_file="1cd_analysis_report.json"):
        """Генерация отчета"""
        logger.info("Генерация отчета...")
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "file_analyzed": str(Path("1Cv8.1CD").absolute()),
            "total_tables": len(results),
            "tables": results,
            "summary": {
                "total_records": sum(int(table.get('records_count', 0)) for table in results),
                "total_data_size": sum(int(table.get('data_size', 0)) for table in results),
                "largest_table": max(results, key=lambda x: int(x.get('records_count', 0))) if results else None
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Отчет сохранен в: {output_file}")
        return report
    
    def analyze_1cd_file(self, file_path, output_csv=None):
        """Основной метод анализа файла 1CD"""
        logger.info(f"Начало анализа файла: {file_path}")
        
        if not Path(file_path).exists():
            logger.error(f"Файл не найден: {file_path}")
            return None
        
        # Проверяем размер файла
        file_size = Path(file_path).stat().st_size
        logger.info(f"Размер файла: {file_size / (1024**3):.2f} GB")
        
        # Выбираем метод анализа
        if self.use_docker and self.check_docker_available():
            logger.info("Используем Docker для анализа")
            results = self.analyze_file_docker(file_path, output_csv)
        else:
            logger.info("Используем нативную утилиту для анализа")
            results = self.analyze_file_native(file_path, output_csv)
        
        if results:
            # Генерируем отчет
            report = self.generate_report(results)
            
            # Выводим краткую статистику
            logger.info("=== КРАТКАЯ СТАТИСТИКА ===")
            logger.info(f"Всего таблиц: {len(results)}")
            logger.info(f"Всего записей: {report['summary']['total_records']:,}")
            logger.info(f"Общий размер данных: {report['summary']['total_data_size'] / (1024**2):.2f} MB")
            
            if report['summary']['largest_table']:
                largest = report['summary']['largest_table']
                logger.info(f"Самая большая таблица: {largest.get('table_name', 'N/A')} "
                          f"({largest.get('records_count', 0):,} записей)")
            
            return results
        else:
            logger.error("Анализ завершился с ошибками")
            return None

def main():
    """Основная функция"""
    
    if len(sys.argv) < 2:
        print("Использование: python3 analyze_1cd_structure.py <путь_к_файлу_1cd> [выходной_csv]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Создаем анализатор
    analyzer = OneCDAnalyzer(use_docker=True)
    
    # Анализируем файл
    results = analyzer.analyze_1cd_file(file_path, output_csv)
    
    if results:
        print("\n✅ Анализ завершен успешно!")
        print(f"📊 Найдено таблиц: {len(results)}")
        print(f"📁 Результаты сохранены в: 1cd_analysis_report.json")
    else:
        print("\n❌ Анализ завершен с ошибками")
        sys.exit(1)

if __name__ == "__main__":
    main() 