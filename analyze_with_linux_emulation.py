#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ файла 1Cv8.1CD с использованием эмуляции Linux в macOS
"""

import os
import sys
import subprocess
import tempfile
import csv
import json
import time
from pathlib import Path
from datetime import datetime

def check_linux_emulation():
    """Проверка доступности эмуляции Linux"""
    print("🔍 Проверка эмуляции Linux...")
    
    # Проверяем наличие Rosetta 2
    try:
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        if result.returncode == 0:
            arch = result.stdout.strip()
            print(f"📊 Архитектура: {arch}")
            
            if arch == 'x86_64':
                print("✅ x86_64 архитектура - можно запустить Linux бинарники")
                return True
            elif arch == 'arm64':
                print("⚠️  ARM64 архитектура - нужна эмуляция")
                # Проверяем Rosetta 2
                try:
                    result = subprocess.run(['softwareupdate', '--list-rosetta'], capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ Rosetta 2 доступна")
                        return True
                    else:
                        print("❌ Rosetta 2 не установлена")
                        return False
                except:
                    print("❌ Не удалось проверить Rosetta 2")
                    return False
            else:
                print(f"❌ Неподдерживаемая архитектура: {arch}")
                return False
        else:
            print("❌ Не удалось определить архитектуру")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке архитектуры: {e}")
        return False

def extract_and_prepare_ctool1cd():
    """Извлечение и подготовка ctool1cd"""
    print("\n🔧 Извлечение и подготовка ctool1cd...")
    
    template_path = Path("tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin")
    
    if not template_path.exists():
        print("❌ Архив с утилитой ctool1cd не найден")
        return None
    
    # Создаем директорию для утилиты
    ctool_dir = Path("ctool1cd_ready")
    ctool_dir.mkdir(exist_ok=True)
    
    try:
        import zipfile
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            zip_file.extractall(ctool_dir)
        
        print(f"✅ Утилита извлечена в: {ctool_dir}")
        
        # Копируем Linux версию
        linux_ctool = ctool_dir / "linux" / "ctool1cd"
        if linux_ctool.exists():
            target_ctool = ctool_dir / "ctool1cd"
            import shutil
            shutil.copy2(linux_ctool, target_ctool)
            os.chmod(target_ctool, 0o755)
            print(f"✅ Исполняемый файл готов: {target_ctool}")
            return target_ctool
        else:
            print(f"❌ Linux версия не найдена: {linux_ctool}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении: {e}")
        return None

def test_ctool1cd_with_emulation(ctool_path):
    """Тестирование ctool1cd с эмуляцией"""
    print(f"\n🔍 Тестирование ctool1cd с эмуляцией: {ctool_path}")
    
    try:
        # Пытаемся запустить с помощью arch для эмуляции x86_64
        cmd = ['arch', '-x86_64', str(ctool_path), '--help']
        
        print(f"🚀 Запуск команды: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Справка получена успешно")
            print("📋 Доступные параметры:")
            help_text = result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
            print(help_text)
            return True
        else:
            print("⚠️  Справка не получена")
            print(f"Код возврата: {result.returncode}")
            if result.stderr:
                print(f"Ошибка: {result.stderr}")
            
            # Пробуем без arch
            print("🔄 Пробуем без эмуляции...")
            cmd = [str(ctool_path), '--help']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Справка получена без эмуляции")
                return True
            else:
                print("❌ Утилита не работает")
                return False
    
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут при получении справки")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def analyze_file_with_emulation(ctool_path, file_path, output_csv=None):
    """Анализ файла с эмуляцией"""
    print(f"\n🔍 Анализ файла с эмуляцией: {file_path}")
    
    # Создаем временные файлы
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    
    try:
        # Формируем команду с эмуляцией
        cmd = [
            'arch', '-x86_64', str(ctool_path),
            '-ne',  # Не создавать пустые файлы
            '-sts', temp_csv.name,  # Статистика в CSV
            '-q', str(file_path),    # Путь к файлу 1CD
            '-l', temp_log.name     # Лог файл
        ]
        
        print(f"🚀 Запуск команды: {' '.join(cmd)}")
        print("⚠️  Это может занять 30-60 минут для файла 81GB...")
        
        # Запускаем утилиту
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 часа таймаут
        end_time = time.time()
        
        print(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
        
        if result.returncode == 0:
            print("✅ Анализ завершен успешно")
            
            # Читаем результаты из CSV
            tables_info = []
            try:
                with open(temp_csv.name, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter='|')
                    for row in reader:
                        tables_info.append(row)
                
                print(f"📊 Найдено таблиц: {len(tables_info)}")
                
                # Сохраняем в указанный файл если нужно
                if output_csv:
                    import shutil
                    shutil.copy2(temp_csv.name, output_csv)
                    print(f"💾 Результаты сохранены в: {output_csv}")
                
                return tables_info
                
            except Exception as e:
                print(f"❌ Ошибка при чтении результатов: {e}")
                return None
                
        else:
            print(f"❌ Ошибка при анализе (код: {result.returncode})")
            if result.stderr:
                print(f"Ошибка: {result.stderr}")
            
            # Пытаемся прочитать лог
            try:
                with open(temp_log.name, 'r', encoding='utf-8') as logfile:
                    log_content = logfile.read()
                    if log_content:
                        print(f"📋 Лог ошибки: {log_content}")
            except:
                pass
            
            return None
            
    finally:
        # Удаляем временные файлы
        try:
            os.unlink(temp_csv.name)
            os.unlink(temp_log.name)
        except:
            pass

def generate_report(results, output_file="1cd_analysis_report.json"):
    """Генерация отчета"""
    print("\n📝 Генерация отчета...")
    
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
    
    print(f"📁 Отчет сохранен в: {output_file}")
    return report

def main():
    """Основная функция"""
    
    print("🚀 Анализ файла 1Cv8.1CD с эмуляцией Linux")
    print("=" * 60)
    
    # Проверяем эмуляцию Linux
    if not check_linux_emulation():
        print("❌ Эмуляция Linux недоступна")
        return False
    
    # Извлекаем и подготавливаем ctool1cd
    ctool_path = extract_and_prepare_ctool1cd()
    if not ctool_path:
        print("❌ Не удалось подготовить утилиту ctool1cd")
        return False
    
    # Тестируем утилиту
    if not test_ctool1cd_with_emulation(ctool_path):
        print("❌ Утилита ctool1cd не работает")
        return False
    
    # Анализируем файл
    file_path = "1Cv8.1CD"
    if not Path(file_path).exists():
        print(f"❌ Файл не найден: {file_path}")
        return False
    
    print(f"\n📊 Размер файла: {Path(file_path).stat().st_size / (1024**3):.2f} GB")
    
    # Запускаем анализ
    results = analyze_file_with_emulation(ctool_path, file_path)
    
    if results:
        # Генерируем отчет
        report = generate_report(results)
        
        # Выводим краткую статистику
        print("\n=== КРАТКАЯ СТАТИСТИКА ===")
        print(f"Всего таблиц: {len(results)}")
        print(f"Всего записей: {report['summary']['total_records']:,}")
        print(f"Общий размер данных: {report['summary']['total_data_size'] / (1024**2):.2f} MB")
        
        if report['summary']['largest_table']:
            largest = report['summary']['largest_table']
            print(f"Самая большая таблица: {largest.get('table_name', 'N/A')} "
                  f"({largest.get('records_count', 0):,} записей)")
        
        print("\n✅ Анализ завершен успешно!")
        return True
    else:
        print("\n❌ Анализ завершился с ошибками")
        return False

if __name__ == "__main__":
    main() 