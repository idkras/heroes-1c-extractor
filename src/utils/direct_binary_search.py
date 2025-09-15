#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
from datetime import datetime

def direct_binary_search():
    """
    Прямой поиск по бинарным данным 1CD файла
    Использует hexdump и strings для поиска ключевых слов
    """
    print("🔍 Прямой поиск по бинарным данным 1CD файла")
    print("🎯 ЦЕЛЬ: Найти документы 'корректировка качества товара'")
    print("=" * 60)
    
    results = {
        'binary_search': {},
        'found_patterns': [],
        'metadata': {
            'extraction_date': datetime.now().isoformat(),
            'source_file': 'raw/1Cv8.1CD',
            'search_methods': ['hexdump', 'strings', 'grep']
        }
    }
    
    # Проверяем существование файла
    if not os.path.exists('raw/1Cv8.1CD'):
        print("❌ Файл raw/1Cv8.1CD не найден!")
        return None
    
    print(f"✅ Файл найден: raw/1Cv8.1CD")
    
    # Ключевые слова для поиска
    quality_keywords = [
        "корректировка", "качество", "товар", "брак", "дефект",
        "проверка", "контроль", "отбраковка", "списание", "уценка",
        "некондиция", "реализация", "поступление", "склад",
        "цвет", "цветы", "розы", "тюльпаны", "флористика",
        "биржа", "7цветов", "цветочный", "рай", "флор"
    ]
    
    print(f"\n🔍 Этап 1: Поиск с помощью hexdump")
    print("-" * 60)
    
    # Поиск с помощью hexdump
    for keyword in quality_keywords[:10]:  # Ограничиваем количество для производительности
        try:
            print(f"    🔍 Поиск ключевого слова: '{keyword}'")
            
            # Команда hexdump для поиска
            cmd = f"hexdump -C raw/1Cv8.1CD | grep -A 5 -B 5 '{keyword}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                print(f"        ✅ Найдено в hexdump: {len(result.stdout.splitlines())} строк")
                
                # Сохраняем результаты
                results['binary_search'][f'hexdump_{keyword}'] = {
                    'keyword': keyword,
                    'found_lines': len(result.stdout.splitlines()),
                    'sample_output': result.stdout[:1000]  # Первые 1000 символов
                }
                
                results['found_patterns'].append(keyword)
            else:
                print(f"        ⚠️ Не найдено в hexdump")
                
        except Exception as e:
            print(f"        ❌ Ошибка hexdump для '{keyword}': {e}")
    
    print(f"\n🔍 Этап 2: Поиск с помощью strings")
    print("-" * 60)
    
    # Поиск с помощью strings
    for keyword in quality_keywords[:10]:
        try:
            print(f"    🔍 Поиск ключевого слова: '{keyword}'")
            
            # Команда strings для поиска
            cmd = f"strings raw/1Cv8.1CD | grep -i '{keyword}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.splitlines()
                print(f"        ✅ Найдено в strings: {len(lines)} строк")
                
                # Показываем первые несколько найденных строк
                for i, line in enumerate(lines[:3]):
                    print(f"            {i+1}. {line[:100]}...")
                
                # Сохраняем результаты
                results['binary_search'][f'strings_{keyword}'] = {
                    'keyword': keyword,
                    'found_lines': len(lines),
                    'sample_output': lines[:10]  # Первые 10 строк
                }
                
                if keyword not in results['found_patterns']:
                    results['found_patterns'].append(keyword)
            else:
                print(f"        ⚠️ Не найдено в strings")
                
        except Exception as e:
            print(f"        ❌ Ошибка strings для '{keyword}': {e}")
    
    print(f"\n🔍 Этап 3: Поиск изображений и BLOB данных")
    print("-" * 60)
    
    # Поиск изображений и BLOB данных
    image_patterns = ['JFIF', 'PNG', 'GIF', 'JPEG', 'BMP']
    
    for pattern in image_patterns:
        try:
            print(f"    🔍 Поиск изображений: '{pattern}'")
            
            # Команда hexdump для поиска изображений
            cmd = f"hexdump -C raw/1Cv8.1CD | grep -A 10 -B 10 '{pattern}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                print(f"        ✅ Найдено изображений: {len(result.stdout.splitlines())} строк")
                
                # Сохраняем результаты
                results['binary_search'][f'images_{pattern}'] = {
                    'pattern': pattern,
                    'found_lines': len(result.stdout.splitlines()),
                    'sample_output': result.stdout[:1000]
                }
            else:
                print(f"        ⚠️ Изображения не найдены")
                
        except Exception as e:
            print(f"        ❌ Ошибка поиска изображений '{pattern}': {e}")
    
    print(f"\n🔍 Этап 4: Поиск специфичных данных о цветах")
    print("-" * 60)
    
    # Специфичные поиски для цветов
    flower_patterns = [
        "цвет", "цветы", "розы", "тюльпаны", "флористика",
        "биржа", "7цветов", "цветочный", "рай", "флор"
    ]
    
    for pattern in flower_patterns:
        try:
            print(f"    🔍 Поиск данных о цветах: '{pattern}'")
            
            # Команда strings для поиска
            cmd = f"strings raw/1Cv8.1CD | grep -i '{pattern}' | head -20"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.splitlines()
                print(f"        ✅ Найдено строк: {len(lines)}")
                
                # Показываем найденные строки
                for i, line in enumerate(lines[:5]):
                    print(f"            {i+1}. {line[:100]}...")
                
                # Сохраняем результаты
                results['binary_search'][f'flowers_{pattern}'] = {
                    'pattern': pattern,
                    'found_lines': len(lines),
                    'sample_output': lines[:10]
                }
                
                if pattern not in results['found_patterns']:
                    results['found_patterns'].append(pattern)
            else:
                print(f"        ⚠️ Данные о цветах не найдены")
                
        except Exception as e:
            print(f"        ❌ Ошибка поиска цветов '{pattern}': {e}")
    
    print(f"\n🔍 Этап 5: Поиск документов качества")
    print("-" * 60)
    
    # Поиск документов качества
    quality_patterns = [
        "корректировка", "качество", "товар", "брак", "дефект",
        "проверка", "контроль", "отбраковка", "списание", "уценка"
    ]
    
    for pattern in quality_patterns:
        try:
            print(f"    🔍 Поиск документов качества: '{pattern}'")
            
            # Команда strings для поиска
            cmd = f"strings raw/1Cv8.1CD | grep -i '{pattern}' | head -20"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.splitlines()
                print(f"        ✅ Найдено строк: {len(lines)}")
                
                # Показываем найденные строки
                for i, line in enumerate(lines[:5]):
                    print(f"            {i+1}. {line[:100]}...")
                
                # Сохраняем результаты
                results['binary_search'][f'quality_{pattern}'] = {
                    'pattern': pattern,
                    'found_lines': len(lines),
                    'sample_output': lines[:10]
                }
                
                if pattern not in results['found_patterns']:
                    results['found_patterns'].append(pattern)
            else:
                print(f"        ⚠️ Документы качества не найдены")
                
        except Exception as e:
            print(f"        ❌ Ошибка поиска качества '{pattern}': {e}")
    
    # Сохраняем результаты
    with open('direct_binary_search.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✅ Результаты сохранены в direct_binary_search.json")
    print(f"🎯 Найдено паттернов: {len(results['found_patterns'])}")
    
    if results['found_patterns']:
        print(f"🔍 Найденные паттерны: {', '.join(results['found_patterns'])}")
    
    return results

if __name__ == "__main__":
    direct_binary_search()
