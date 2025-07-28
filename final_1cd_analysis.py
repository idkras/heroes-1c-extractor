#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный анализ файла 1Cv8.1CD с поддержкой Docker
"""

import os
import sys
import subprocess
import tempfile
import csv
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_1cd_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalOneCDAnalyzer:
    """Финальный анализатор файлов 1CD"""
    
    def __init__(self):
        self.results = {}
        
    def check_docker_available(self):
        """Проверка доступности Docker"""
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def check_docker_image(self):
        """Проверка наличия Docker образа"""
        try:
            result = subprocess.run(['docker', 'images', 'ctool1cd'], capture_output=True, text=True, timeout=5)
            return 'ctool1cd' in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def build_docker_image(self):
        """Сборка Docker образа"""
        logger.info("Сборка Docker образа ctool1cd...")
        
        try:
            result = subprocess.run([
                'docker', 'build', '-t', 'ctool1cd', '.'
            ], capture_output=True, text=True, timeout=600)  # 10 минут
            
            if result.returncode == 0:
                logger.info("✅ Docker образ успешно собран")
                return True
            else:
                logger.error(f"❌ Ошибка при сборке образа: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Таймаут при сборке Docker образа")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при сборке: {e}")
            return False
    
    def analyze_file_docker(self, file_path, output_csv=None):
        """Анализ файла через Docker"""
        logger.info(f"🔍 Анализ файла через Docker: {file_path}")
        
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
            
            logger.info(f"🚀 Запуск команды: {' '.join(cmd)}")
            logger.info("⚠️  Это может занять 30-60 минут для файла 81GB...")
            
            # Запускаем Docker контейнер
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 часа таймаут
            end_time = time.time()
            
            logger.info(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
            
            if result.returncode == 0:
                logger.info("✅ Анализ завершен успешно")
                
                # Читаем результаты
                csv_path = Path("temp_output.csv")
                if csv_path.exists():
                    return self.parse_csv_results(csv_path, output_csv)
                else:
                    logger.error("❌ CSV файл с результатами не найден")
                    return None
                    
            else:
                logger.error(f"❌ Ошибка при анализе (код: {result.returncode})")
                if result.stderr:
                    logger.error(f"Ошибка: {result.stderr}")
                
                # Пытаемся прочитать лог
                log_path = Path("temp_log.txt")
                if log_path.exists():
                    with open(log_path, 'r', encoding='utf-8') as logfile:
                        log_content = logfile.read()
                        if log_content:
                            logger.error(f"📋 Лог ошибки: {log_content}")
                
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
        logger.info(f"📊 Парсинг результатов из: {csv_path}")
        
        try:
            tables_info = []
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='|')
                for row in reader:
                    tables_info.append(row)
            
            logger.info(f"📊 Найдено таблиц: {len(tables_info)}")
            
            # Сохраняем в указанный файл если нужно
            if output_csv:
                import shutil
                shutil.copy2(csv_path, output_csv)
                logger.info(f"💾 Результаты сохранены в: {output_csv}")
            
            return tables_info
            
        except Exception as e:
            logger.error(f"❌ Ошибка при чтении результатов: {e}")
            return None
    
    def generate_report(self, results, output_file="final_1cd_analysis_report.json"):
        """Генерация финального отчета"""
        logger.info("📝 Генерация финального отчета...")
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "file_analyzed": str(Path("1Cv8.1CD").absolute()),
            "file_size_gb": Path("1Cv8.1CD").stat().st_size / (1024**3),
            "total_tables": len(results),
            "tables": results,
            "summary": {
                "total_records": sum(int(table.get('records_count', 0)) for table in results),
                "total_data_size": sum(int(table.get('data_size', 0)) for table in results),
                "largest_table": max(results, key=lambda x: int(x.get('records_count', 0))) if results else None,
                "average_records_per_table": sum(int(table.get('records_count', 0)) for table in results) / len(results) if results else 0
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 Отчет сохранен в: {output_file}")
        return report
    
    def print_summary(self, report):
        """Вывод краткой статистики"""
        print("\n" + "=" * 80)
        print("📊 ФИНАЛЬНАЯ СТАТИСТИКА АНАЛИЗА ФАЙЛА 1Cv8.1CD")
        print("=" * 80)
        
        print(f"📁 Файл: {Path('1Cv8.1CD').name}")
        print(f"📊 Размер: {report['file_size_gb']:.2f} GB")
        print(f"📅 Дата анализа: {report['analysis_date']}")
        print()
        
        print(f"📋 Структура базы данных:")
        print(f"   • Всего таблиц: {report['total_tables']:,}")
        print(f"   • Всего записей: {report['summary']['total_records']:,}")
        print(f"   • Общий размер данных: {report['summary']['total_data_size'] / (1024**2):.2f} MB")
        print(f"   • Среднее записей на таблицу: {report['summary']['average_records_per_table']:,.0f}")
        
        if report['summary']['largest_table']:
            largest = report['summary']['largest_table']
            print(f"\n🏆 Самая большая таблица:")
            print(f"   • Имя: {largest.get('table_name', 'N/A')}")
            print(f"   • Записей: {largest.get('records_count', 0):,}")
            print(f"   • Размер данных: {int(largest.get('data_size', 0)) / (1024**2):.2f} MB")
        
        # Топ-10 таблиц по размеру
        if report['tables']:
            print(f"\n📈 Топ-10 таблиц по количеству записей:")
            sorted_tables = sorted(report['tables'], key=lambda x: int(x.get('records_count', 0)), reverse=True)
            for i, table in enumerate(sorted_tables[:10], 1):
                name = table.get('table_name', 'N/A')
                records = int(table.get('records_count', 0))
                size_mb = int(table.get('data_size', 0)) / (1024**2)
                print(f"   {i:2d}. {name:<30} {records:>12,} записей ({size_mb:>8.2f} MB)")
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 80)
    
    def analyze_1cd_file(self, file_path, output_csv=None):
        """Основной метод анализа файла 1CD"""
        logger.info(f"🚀 Начало финального анализа файла: {file_path}")
        
        if not Path(file_path).exists():
            logger.error(f"❌ Файл не найден: {file_path}")
            return None
        
        # Проверяем размер файла
        file_size = Path(file_path).stat().st_size
        logger.info(f"📊 Размер файла: {file_size / (1024**3):.2f} GB")
        
        # Проверяем Docker
        if not self.check_docker_available():
            logger.error("❌ Docker недоступен")
            return None
        
        # Проверяем Docker образ
        if not self.check_docker_image():
            logger.info("🔧 Docker образ не найден, собираем...")
            if not self.build_docker_image():
                logger.error("❌ Не удалось собрать Docker образ")
                return None
        
        # Анализируем файл
        results = self.analyze_file_docker(file_path, output_csv)
        
        if results:
            # Генерируем отчет
            report = self.generate_report(results)
            
            # Выводим статистику
            self.print_summary(report)
            
            return results
        else:
            logger.error("❌ Анализ завершился с ошибками")
            return None

def main():
    """Основная функция"""
    
    print("🚀 ФИНАЛЬНЫЙ АНАЛИЗ ФАЙЛА 1Cv8.1CD")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = FinalOneCDAnalyzer()
    
    # Анализируем файл
    results = analyzer.analyze_1cd_file("1Cv8.1CD")
    
    if results:
        print(f"\n📁 Результаты сохранены в:")
        print(f"   • JSON отчет: final_1cd_analysis_report.json")
        print(f"   • Лог файл: final_1cd_analysis.log")
        print(f"\n🎉 Анализ завершен успешно!")
        return True
    else:
        print(f"\n❌ Анализ завершен с ошибками")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 