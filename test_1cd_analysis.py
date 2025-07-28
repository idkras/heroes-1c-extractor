#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое тестирование анализа файла 1CD
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_file_header():
    """Тестирование заголовка файла 1CD"""
    print("🔍 Тестирование заголовка файла 1Cv8.1CD...")
    
    file_path = Path("1Cv8.1CD")
    if not file_path.exists():
        print("❌ Файл 1Cv8.1CD не найден")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        print(f"📄 Заголовок файла: {header.hex()}")
        print(f"📄 ASCII: {header.decode('ascii', errors='ignore')}")
        
        if header.startswith(b'1CDBMSV8'):
            print("✅ Заголовок корректный - это файл 1С:Предприятие 8")
            return True
        else:
            print("❌ Заголовок не соответствует формату 1CD")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return False

def test_ctool1cd_extraction():
    """Тестирование извлечения ctool1cd"""
    print("\n🔧 Тестирование извлечения ctool1cd...")
    
    template_path = Path("tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin")
    
    if not template_path.exists():
        print("❌ Архив с утилитой ctool1cd не найден")
        return False
    
    print(f"✅ Архив найден: {template_path}")
    print(f"📦 Размер архива: {template_path.stat().st_size / (1024**2):.2f} MB")
    
    import zipfile
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            files = zip_file.namelist()
            print(f"📋 Содержимое архива:")
            for file in files:
                print(f"   - {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при анализе архива: {e}")
        return False

def test_docker_availability():
    """Тестирование доступности Docker"""
    print("\n🐳 Тестирование Docker...")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Docker установлен: {result.stdout.strip()}")
            
            # Проверяем daemon
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Docker daemon запущен")
                return True
            else:
                print("⚠️  Docker daemon не запущен")
                return False
        else:
            print("❌ Docker не установлен")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker не найден")
        return False

def test_file_access():
    """Тестирование доступа к файлу"""
    print("\n📁 Тестирование доступа к файлу...")
    
    file_path = Path("1Cv8.1CD")
    if not file_path.exists():
        print("❌ Файл не найден")
        return False
    
    try:
        # Проверяем права доступа
        stat = file_path.stat()
        print(f"✅ Файл доступен")
        print(f"📊 Размер: {stat.st_size / (1024**3):.2f} GB")
        print(f"📅 Модификация: {stat.st_mtime}")
        
        # Проверяем возможность чтения
        with open(file_path, 'rb') as f:
            f.read(1024)  # Читаем первые 1KB
        print("✅ Файл читается")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка доступа к файлу: {e}")
        return False

def create_test_script():
    """Создание тестового скрипта"""
    print("\n📝 Создание тестового скрипта...")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для анализа небольшого участка файла 1CD
"""

import subprocess
import tempfile
import os
from pathlib import Path

def test_small_analysis():
    """Тестирование анализа на небольшом участке"""
    
    # Создаем временные файлы
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    
    try:
        # Тестируем с ограниченным размером
        cmd = [
            'head', '-c', '1048576', '1Cv8.1CD'  # Первые 1MB
        ]
        
        print("🔍 Тестирование чтения первых 1MB файла...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Чтение файла успешно")
            print(f"📊 Прочитано байт: {len(result.stdout)}")
            return True
        else:
            print("❌ Ошибка при чтении файла")
            return False
            
    finally:
        # Удаляем временные файлы
        for temp_file in [temp_csv.name, temp_log.name]:
            try:
                os.unlink(temp_file)
            except:
                pass

if __name__ == "__main__":
    test_small_analysis()
'''
    
    script_path = Path("test_small_analysis.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Тестовый скрипт создан: {script_path}")
    return script_path

def main():
    """Основная функция тестирования"""
    
    print("🚀 Запуск тестирования окружения для анализа 1CD")
    print("=" * 60)
    
    tests = [
        ("Заголовок файла", test_file_header),
        ("Извлечение ctool1cd", test_ctool1cd_extraction),
        ("Доступность Docker", test_docker_availability),
        ("Доступ к файлу", test_file_access),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Создаем тестовый скрипт
    test_script = create_test_script()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n📝 Тестовый скрипт: {test_script}")
    
    if all_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Окружение готово для анализа.")
        print("\n💡 Следующие шаги:")
        print("   1. Запустить Docker Desktop")
        print("   2. Собрать Docker образ: docker build -t ctool1cd .")
        print("   3. Запустить анализ: python3 analyze_1cd_structure.py 1Cv8.1CD")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ. Проверьте окружение.")
    
    return all_passed

if __name__ == "__main__":
    main() 