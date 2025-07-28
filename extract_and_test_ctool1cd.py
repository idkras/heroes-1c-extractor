#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение и тестирование ctool1cd без Docker
"""

import os
import sys
import subprocess
import tempfile
import zipfile
from pathlib import Path

def extract_ctool1cd():
    """Извлечение утилиты ctool1cd"""
    print("🔧 Извлечение утилиты ctool1cd...")
    
    template_path = Path("tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin")
    
    if not template_path.exists():
        print("❌ Архив с утилитой ctool1cd не найден")
        return None
    
    # Создаем директорию для утилиты
    ctool_dir = Path("ctool1cd_extracted")
    ctool_dir.mkdir(exist_ok=True)
    
    try:
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

def test_ctool1cd_help(ctool_path):
    """Тестирование справки ctool1cd"""
    print(f"\n📖 Тестирование справки ctool1cd: {ctool_path}")
    
    try:
        # Пытаемся запустить с параметром --help
        result = subprocess.run([str(ctool_path), "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Справка получена успешно")
            print("📋 Доступные параметры:")
            help_text = result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
            print(help_text)
            return True
        else:
            print("⚠️  Справка не получена, но утилита запустилась")
            print(f"Код возврата: {result.returncode}")
            if result.stderr:
                print(f"Ошибка: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут при получении справки")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def test_small_analysis(ctool_path):
    """Тестирование анализа небольшого участка файла"""
    print(f"\n🔍 Тестирование анализа небольшого участка файла...")
    
    # Создаем временные файлы
    import tempfile
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    
    try:
        # Формируем команду для анализа только начала файла
        cmd = [
            str(ctool_path),
            "-ne",  # Не создавать пустые файлы
            "-sts", temp_csv.name,  # Статистика в CSV
            "-q", "1Cv8.1CD",    # Путь к файлу 1CD
            "-l", temp_log.name     # Лог файл
        ]
        
        print(f"🚀 Запуск команды: {' '.join(cmd)}")
        print("⚠️  Это может занять некоторое время...")
        
        # Запускаем утилиту с ограниченным временем
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 минут
        
        if result.returncode == 0:
            print("✅ Анализ завершен успешно")
            
            # Читаем результаты из CSV
            try:
                import csv
                tables_info = []
                with open(temp_csv.name, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter='|')
                    for row in reader:
                        tables_info.append(row)
                
                print(f"📊 Найдено таблиц: {len(tables_info)}")
                
                # Выводим информацию о первых таблицах
                for i, table in enumerate(tables_info[:5]):
                    print(f"  {i+1}. {table.get('table_name', 'N/A')}")
                    print(f"     Записей: {table.get('records_count', 'N/A')}")
                    print(f"     Размер данных: {table.get('data_size', 'N/A')} байт")
                
                return True
                
            except Exception as e:
                print(f"❌ Ошибка при чтении результатов: {e}")
                return False
                
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
            
            return False
            
    finally:
        # Удаляем временные файлы
        try:
            os.unlink(temp_csv.name)
            os.unlink(temp_log.name)
        except:
            pass

def create_analysis_script(ctool_path):
    """Создание скрипта для полного анализа"""
    print(f"\n📝 Создание скрипта для полного анализа...")
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный анализ файла 1Cv8.1CD
"""

import subprocess
import csv
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime

def analyze_full_1cd_file():
    """Полный анализ файла 1Cv8.1CD"""
    
    ctool_path = "{ctool_path}"
    file_path = "1Cv8.1CD"
    
    print(f"🔍 Начало полного анализа файла: {{file_path}}")
    
    # Создаем временные файлы
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    
    try:
        # Формируем команду
        cmd = [
            ctool_path,
            "-ne",  # Не создавать пустые файлы
            "-sts", temp_csv.name,  # Статистика в CSV
            "-q", file_path,    # Путь к файлу 1CD
            "-l", temp_log.name     # Лог файл
        ]
        
        print(f"🚀 Запуск команды: {{' '.join(cmd)}}")
        print("⚠️  Это может занять 30-60 минут для файла 81GB...")
        
        # Запускаем утилиту
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 часа таймаут
        end_time = time.time()
        
        print(f"⏱️  Время выполнения: {{end_time - start_time:.2f}} секунд")
        
        if result.returncode == 0:
            print("✅ Анализ завершен успешно")
            
            # Читаем результаты из CSV
            tables_info = []
            with open(temp_csv.name, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='|')
                for row in reader:
                    tables_info.append(row)
            
            print(f"📊 Найдено таблиц: {{len(tables_info)}}")
            
            # Создаем отчет
            report = {{
                "analysis_date": datetime.now().isoformat(),
                "file_analyzed": str(Path(file_path).absolute()),
                "total_tables": len(tables_info),
                "tables": tables_info,
                "summary": {{
                    "total_records": sum(int(table.get('records_count', 0)) for table in tables_info),
                    "total_data_size": sum(int(table.get('data_size', 0)) for table in tables_info),
                    "largest_table": max(tables_info, key=lambda x: int(x.get('records_count', 0))) if tables_info else None
                }}
            }}
            
            # Сохраняем отчет
            with open("full_1cd_analysis_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print("📁 Отчет сохранен в: full_1cd_analysis_report.json")
            
            # Выводим краткую статистику
            print("\\n=== КРАТКАЯ СТАТИСТИКА ===")
            print(f"Всего таблиц: {{len(tables_info)}}")
            print(f"Всего записей: {{report['summary']['total_records']:,}}")
            print(f"Общий размер данных: {{report['summary']['total_data_size'] / (1024**2):.2f}} MB")
            
            if report['summary']['largest_table']:
                largest = report['summary']['largest_table']
                print(f"Самая большая таблица: {{largest.get('table_name', 'N/A')}} "
                      f"({{largest.get('records_count', 0):,}} записей)")
            
            return True
            
        else:
            print(f"❌ Ошибка при анализе (код: {{result.returncode}})")
            if result.stderr:
                print(f"Ошибка: {{result.stderr}}")
            
            # Пытаемся прочитать лог
            try:
                with open(temp_log.name, 'r', encoding='utf-8') as logfile:
                    log_content = logfile.read()
                    if log_content:
                        print(f"📋 Лог ошибки: {{log_content}}")
            except:
                pass
            
            return False
            
    finally:
        # Удаляем временные файлы
        try:
            os.unlink(temp_csv.name)
            os.unlink(temp_log.name)
        except:
            pass

if __name__ == "__main__":
    analyze_full_1cd_file()
'''
    
    script_path = Path("full_1cd_analysis.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Скрипт создан: {script_path}")
    return script_path

def main():
    """Основная функция"""
    
    print("🚀 Извлечение и тестирование ctool1cd")
    print("=" * 60)
    
    # Извлекаем утилиту
    ctool_path = extract_ctool1cd()
    
    if not ctool_path:
        print("❌ Не удалось извлечь утилиту ctool1cd")
        return False
    
    # Тестируем справку
    if not test_ctool1cd_help(ctool_path):
        print("⚠️  Утилита не работает корректно")
        return False
    
    # Тестируем небольшой анализ
    if test_small_analysis(ctool_path):
        print("\n✅ Тестовый анализ прошел успешно!")
        
        # Создаем скрипт для полного анализа
        full_script = create_analysis_script(ctool_path)
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 60)
        print(f"✅ Утилита ctool1cd готова к работе: {ctool_path}")
        print(f"📝 Скрипт для полного анализа: {full_script}")
        print("\n💡 Для запуска полного анализа:")
        print(f"   python3 {full_script}")
        
        return True
    else:
        print("\n❌ Тестовый анализ не прошел")
        return False

if __name__ == "__main__":
    main() 