#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация работы с утилитой ctool1cd для анализа файлов 1CD
"""

import os
import sys
import zipfile
import subprocess
import tempfile
import csv
from pathlib import Path

def extract_ctool1cd():
    """Извлечение утилиты ctool1cd из архива"""
    
    print("🔧 Извлечение утилиты ctool1cd...")
    
    # Путь к архиву с утилитой
    template_path = Path("tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin")
    
    if not template_path.exists():
        print("❌ Архив с утилитой ctool1cd не найден")
        return None
    
    # Создаем временную директорию для извлечения
    temp_dir = Path(tempfile.mkdtemp(prefix="ctool1cd_"))
    
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            zip_file.extractall(temp_dir)
        
        print(f"✅ Утилита извлечена в: {temp_dir}")
        
        # Определяем путь к исполняемому файлу
        if sys.platform.startswith('win'):
            executable = temp_dir / "windows" / "ctool1cd.exe"
        else:
            executable = temp_dir / "linux" / "ctool1cd"
        
        if executable.exists():
            print(f"✅ Исполняемый файл найден: {executable}")
            return executable
        else:
            print(f"❌ Исполняемый файл не найден: {executable}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении: {e}")
        return None

def test_ctool1cd_help(executable_path):
    """Тестирование справки утилиты ctool1cd"""
    
    print("\n📖 Тестирование справки ctool1cd...")
    
    try:
        # Пытаемся запустить с параметром --help
        result = subprocess.run([str(executable_path), "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Справка получена успешно")
            print("📋 Доступные параметры:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("⚠️  Справка не получена, но утилита запустилась")
            print(f"Код возврата: {result.returncode}")
            if result.stderr:
                print(f"Ошибка: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут при получении справки")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

def create_sample_1cd_analysis_script():
    """Создание примера скрипта для анализа файла 1CD"""
    
    print("\n📝 Создание примера скрипта анализа...")
    
    script_content = '''#!/usr/bin/env python3
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
        print("\\n✅ Анализ завершен успешно!")
    else:
        print("\\n❌ Анализ завершен с ошибками")

if __name__ == "__main__":
    main()
'''
    
    script_path = Path("analyze_1cd_example.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Пример скрипта создан: {script_path}")
    return script_path

def create_integration_guide():
    """Создание руководства по интеграции"""
    
    print("\n📚 Создание руководства по интеграции...")
    
    guide_content = '''# Руководство по интеграции с файлами 1CD проекта prosto-svet

## Обзор

Проект tools_ui_1c содержит готовую инфраструктуру для работы с файлами 1CD через утилиту ctool1cd. 
Это позволяет извлекать метаданные и структуру данных из файлов проекта prosto-svet.

## Компоненты

### 1. Утилита ctool1cd
- **Расположение**: `tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin`
- **Функции**: Анализ структуры файловых баз 1С, экспорт метаданных в CSV
- **Поддержка**: Windows (ctool1cd.exe) и Linux (ctool1cd)

### 2. Обработка "Структура хранения базы данных"
- **Расположение**: `tools_ui_1c/src/Инструменты/src/DataProcessors/УИ_СтруктураХраненияБазыДанных`
- **Функции**: Визуализация размеров таблиц, интеграция с ctool1cd

### 3. Общие модули
- **Расположение**: `tools_ui_1c/src/Инструменты/src/CommonModules`
- **Функции**: Работа с файлами, запуск процессов, обработка результатов

## План интеграции

### Этап 1: Подготовка
1. Изучить структуру файлов prosto-svet
2. Определить необходимые данные для извлечения
3. Подготовить тестовые файлы 1CD

### Этап 2: Разработка обработки
1. Создать новую обработку в tools_ui_1c
2. Интегрировать ctool1cd
3. Реализовать парсинг CSV результатов

### Этап 3: Функционал
1. Добавить выбор файлов 1CD
2. Реализовать анализ структуры
3. Создать экспорт результатов

## Пример использования

```python
# Анализ файла 1CD
from pathlib import Path
import subprocess

def analyze_1cd_file(ctool1cd_path, file_1cd_path):
    cmd = [
        str(ctool1cd_path),
        "-ne", "-sts", "output.csv",
        "-q", str(file_1cd_path),
        "-l", "log.txt"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

## Возможности извлечения данных

### Метаданные таблиц
- Имена таблиц
- Количество записей
- Размеры данных и индексов
- Структура полей

### Структура базы
- Связи между таблицами
- Индексы
- Ограничения

### Статистика
- Размеры таблиц
- Пространство на диске
- Производительность

## Рекомендации

1. **Тестирование**: Начните с небольших файлов 1CD
2. **Обработка ошибок**: Добавьте проверки целостности файлов
3. **Производительность**: Используйте пакетную обработку для множества файлов
4. **Безопасность**: Проверяйте пути к файлам и права доступа

## Следующие шаги

1. Создать прототип обработки
2. Протестировать на реальных файлах prosto-svet
3. Добавить специфичную логику для проекта
4. Интегрировать в основную систему
'''
    
    guide_path = Path("integration_guide.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ Руководство создано: {guide_path}")
    return guide_path

def main():
    """Основная функция демонстрации"""
    
    print("🚀 Демонстрация работы с утилитой ctool1cd")
    print("=" * 60)
    
    # Извлекаем утилиту
    executable = extract_ctool1cd()
    
    if executable:
        # Тестируем справку
        test_ctool1cd_help(executable)
        
        # Создаем пример скрипта
        script_path = create_sample_1cd_analysis_script()
        
        # Создаем руководство
        guide_path = create_integration_guide()
        
        print("\n" + "=" * 60)
        print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("=" * 60)
        
        print(f"\n📁 Созданные файлы:")
        print(f"   • Пример скрипта: {script_path}")
        print(f"   • Руководство: {guide_path}")
        
        print(f"\n🔧 Утилита ctool1cd:")
        print(f"   • Исполняемый файл: {executable}")
        print(f"   • Платформа: {'Windows' if sys.platform.startswith('win') else 'Linux'}")
        
        print(f"\n💡 Для использования:")
        print(f"   python3 {script_path} {executable} <путь_к_файлу_1cd>")
        
    else:
        print("❌ Не удалось извлечь утилиту ctool1cd")

if __name__ == "__main__":
    main() 