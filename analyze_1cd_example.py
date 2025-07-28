#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример скрипта для анализа файла 1CD с помощью ctool1cd
"""

import subprocess
import csv
import json
import sys
from pathlib import Path

def analyze_1cd_file(ctool1cd_path, file_1cd_path, output_csv=None):
    """
    Анализ файла 1CD с помощью утилиты ctool1cd
    
    Args:
        ctool1cd_path: Путь к утилите ctool1cd
        file_1cd_path: Путь к файлу 1CD для анализа
        output_csv: Путь для сохранения результатов в CSV (опционально)
    """
    
    print(f"🔍 Анализ файла: {file_1cd_path}")
    
    # Создаем временные файлы для результатов
    import tempfile
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    
    try:
        # Формируем команду запуска ctool1cd
        cmd = [
            str(ctool1cd_path),
            "-ne",  # Не создавать пустые файлы
            "-sts", str(temp_csv.name),  # Статистика в CSV
            "-q", str(file_1cd_path),    # Путь к файлу 1CD
            "-l", str(temp_log.name)     # Лог файл
        ]
        
        print(f"🚀 Запуск команды: {' '.join(cmd)}")
        
        # Запускаем утилиту
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
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
                
                # Выводим информацию о таблицах
                for i, table in enumerate(tables_info[:5]):  # Показываем первые 5
                    print(f"  {i+1}. {table.get('table_name', 'N/A')}")
                    print(f"     Записей: {table.get('records_count', 'N/A')}")
                    print(f"     Размер данных: {table.get('data_size', 'N/A')} байт")
                
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

def main():
    """Основная функция"""
    
    if len(sys.argv) < 3:
        print("Использование: python3 script.py <путь_к_ctool1cd> <путь_к_файлу_1cd> [выходной_csv]")
        sys.exit(1)
    
    ctool1cd_path = Path(sys.argv[1])
    file_1cd_path = Path(sys.argv[2])
    output_csv = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not ctool1cd_path.exists():
        print(f"❌ Утилита ctool1cd не найдена: {ctool1cd_path}")
        sys.exit(1)
    
    if not file_1cd_path.exists():
        print(f"❌ Файл 1CD не найден: {file_1cd_path}")
        sys.exit(1)
    
    # Анализируем файл
    results = analyze_1cd_file(ctool1cd_path, file_1cd_path, output_csv)
    
    if results:
        print("\n✅ Анализ завершен успешно!")
    else:
        print("\n❌ Анализ завершен с ошибками")

if __name__ == "__main__":
    main()
