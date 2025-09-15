#!/usr/bin/env python3
"""
Скрипт для проверки и исправления информации о правообладателе в лицензионных соглашениях стандартов.

Ищет во всех стандартах секции с лицензиями и проверяет корректность указания правообладателя.
Генерирует отчет о найденных несоответствиях и предлагает исправления.
"""

import os
import re
import glob
import json
from datetime import datetime

# Конфигурация
STANDARDS_DIR = './standards .md'
OUTPUT_REPORT_PATH = './license_validation_report.json'
CORRECT_OWNER = 'Илья Красинский'
INCORRECT_OWNER = 'Magic Rick Inc., штат Делавэр, США'
MAGIC_RICK_ROLE = 'Magic Rick Inc. представляет интересы Ильи Красинского в защите всех его интеллектуальных и авторских прав'

def find_license_sections(content):
    """
    Находит секции лицензионных соглашений в содержимом документа.
    
    Args:
        content: Содержимое документа
        
    Returns:
        list: Найденные секции лицензионных соглашений
    """
    license_sections = []
    
    # Ищем различные варианты заголовков лицензионных разделов
    license_headers = [
        r'#+\s*Лицензи[ия]',
        r'#+\s*Авторск[ие]{0,2}\s*прав[ао]',
        r'#+\s*Лицензирование',
        r'#+\s*Правообладат[ие]{0,2}л[ья]?',
        r'Правообладатель:'
    ]
    
    for header_pattern in license_headers:
        # Ищем секцию от заголовка до следующего заголовка или конца документа
        matches = re.finditer(f'({header_pattern}.*?)(?=#+|$)', content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            license_sections.append(match.group(1))
    
    return license_sections

def check_file_license(file_path):
    """
    Проверяет корректность указания правообладателя в файле.
    
    Args:
        file_path: Путь к файлу для проверки
        
    Returns:
        dict: Результаты проверки
    """
    result = {
        "file": file_path,
        "has_license_section": False,
        "incorrect_owner": False,
        "license_sections": [],
        "suggested_corrections": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        license_sections = find_license_sections(content)
        
        if license_sections:
            result["has_license_section"] = True
            result["license_sections"] = license_sections
            
            # Проверяем наличие некорректного указания правообладателя
            for section in license_sections:
                if INCORRECT_OWNER in section:
                    result["incorrect_owner"] = True
                    # Создаем исправленный текст
                    corrected_section = section.replace(INCORRECT_OWNER, CORRECT_OWNER)
                    
                    # Добавляем упоминание роли Magic Rick Inc., если его нет
                    if MAGIC_RICK_ROLE not in corrected_section:
                        corrected_section = re.sub(
                            r'(Правообладатель:.*?)\n',
                            f'\\1\n> {MAGIC_RICK_ROLE}.\n',
                            corrected_section
                        )
                    
                    result["suggested_corrections"].append({
                        "original": section,
                        "corrected": corrected_section
                    })
        
        return result
    
    except Exception as e:
        print(f"Ошибка при проверке файла {file_path}: {e}")
        return result

def scan_standards_for_license_issues():
    """
    Сканирует все стандарты на наличие проблем с указанием правообладателя.
    
    Returns:
        dict: Результаты сканирования
    """
    print(f"=== Проверка правообладателя в лицензиях ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files_checked": 0,
        "files_with_license": 0,
        "files_with_incorrect_owner": 0,
        "file_results": []
    }
    
    # Ищем все markdown-файлы в директории стандартов
    md_files = glob.glob(f"{STANDARDS_DIR}/**/*.md", recursive=True)
    
    for file_path in md_files:
        print(f"Проверка файла: {file_path}")
        file_result = check_file_license(file_path)
        
        results["files_checked"] += 1
        
        if file_result["has_license_section"]:
            results["files_with_license"] += 1
            
            if file_result["incorrect_owner"]:
                results["files_with_incorrect_owner"] += 1
                print(f"  ⚠️ Найдено некорректное указание правообладателя")
            else:
                print(f"  ✓ Правообладатель указан корректно")
                
        else:
            print(f"  ℹ️ Секция лицензии не найдена")
        
        results["file_results"].append(file_result)
    
    # Сохраняем результаты в файл
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Отчет сохранен в {OUTPUT_REPORT_PATH}")
    
    # Выводим общую статистику
    print("\n=== Результаты проверки ===")
    print(f"Проверено файлов: {results['files_checked']}")
    print(f"Файлы с лицензиями: {results['files_with_license']}")
    print(f"Файлы с некорректным правообладателем: {results['files_with_incorrect_owner']}")
    
    # Выводим список файлов с проблемами
    if results["files_with_incorrect_owner"] > 0:
        print("\nФайлы с некорректным указанием правообладателя:")
        for file_result in results["file_results"]:
            if file_result["incorrect_owner"]:
                print(f"  - {file_result['file']}")
    
    return results

def generate_correction_script(results):
    """
    Генерирует скрипт для автоматического исправления проблем с указанием правообладателя.
    
    Args:
        results: Результаты сканирования
        
    Returns:
        str: Содержимое скрипта для исправления
    """
    script_content = """#!/usr/bin/env python3
\"\"\"
Скрипт для автоматического исправления указания правообладателя в лицензиях стандартов.
Сгенерирован автоматически на основе результатов проверки.
\"\"\"

import re
import os
from datetime import datetime

# Конфигурация
CORRECT_OWNER = 'Илья Красинский'
INCORRECT_OWNER = 'Magic Rick Inc., штат Делавэр, США'
MAGIC_RICK_ROLE = 'Magic Rick Inc. представляет интересы Ильи Красинского в защите всех его интеллектуальных и авторских прав'
BACKUP_SUFFIX = f'.bak_{datetime.now().strftime("%d%m%Y")}'

# Файлы для исправления
FILES_TO_FIX = [
"""
    
    # Добавляем список файлов для исправления
    for file_result in results["file_results"]:
        if file_result["incorrect_owner"]:
            script_content += f"    '{file_result['file']}',\n"
    
    script_content += """
]

def create_backup(file_path):
    \"\"\"Создает резервную копию файла\"\"\"
    backup_path = file_path + BACKUP_SUFFIX
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dest:
                dest.write(src.read())
        print(f"✓ Создана резервная копия: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании резервной копии {file_path}: {e}")
        return False

def fix_license_owner(file_path):
    \"\"\"Исправляет указание правообладателя в файле\"\"\"
    try:
        # Создаем резервную копию
        if not create_backup(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем некорректного правообладателя
        if INCORRECT_OWNER in content:
            content = content.replace(INCORRECT_OWNER, CORRECT_OWNER)
            
            # Добавляем упоминание роли Magic Rick Inc. после правообладателя, если его нет
            if MAGIC_RICK_ROLE not in content:
                content = re.sub(
                    r'(Правообладатель:.*?)\\n',
                    f'\\\\1\\n> {MAGIC_RICK_ROLE}.\\n',
                    content
                )
            
            # Записываем обновленный контент
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Исправлен правообладатель в файле: {file_path}")
            return True
        else:
            print(f"ℹ️ Некорректный правообладатель не найден в файле: {file_path}")
            return False
    
    except Exception as e:
        print(f"✗ Ошибка при исправлении файла {file_path}: {e}")
        return False

def main():
    \"\"\"Основная функция скрипта\"\"\"
    print(f"=== Исправление указания правообладателя ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    fixed_count = 0
    error_count = 0
    
    for file_path in FILES_TO_FIX:
        print(f"\\nОбработка файла: {file_path}")
        if os.path.exists(file_path):
            if fix_license_owner(file_path):
                fixed_count += 1
            else:
                error_count += 1
        else:
            print(f"✗ Файл не найден: {file_path}")
            error_count += 1
    
    print(f"\\n=== Результаты исправления ===")
    print(f"Всего файлов: {len(FILES_TO_FIX)}")
    print(f"Успешно исправлено: {fixed_count}")
    print(f"Ошибок: {error_count}")

if __name__ == "__main__":
    main()
"""
    
    return script_content

def create_correction_script(results):
    """
    Создает скрипт для автоматического исправления проблем с указанием правообладателя.
    
    Args:
        results: Результаты сканирования
    """
    script_content = generate_correction_script(results)
    script_path = "./scripts/fix_license_owner.py"
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Делаем скрипт исполняемым
        os.chmod(script_path, 0o755)
        
        print(f"\nСоздан скрипт для автоматического исправления: {script_path}")
        print("Чтобы исправить все проблемы, выполните команду:")
        print(f"  python {script_path}")
    
    except Exception as e:
        print(f"Ошибка при создании скрипта: {e}")

def main():
    """Основная функция скрипта."""
    results = scan_standards_for_license_issues()
    
    if results["files_with_incorrect_owner"] > 0:
        create_correction_script(results)
    else:
        print("\nВсе файлы с лицензиями содержат корректное указание правообладателя!")

if __name__ == "__main__":
    main()