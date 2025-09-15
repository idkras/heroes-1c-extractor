#!/usr/bin/env python3
"""
Скрипт для преобразования физических ссылок в абстрактные.
"""

import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from advising_platform.advising_platform.src.core.document_abstractions import DocumentRegistry
except ImportError:
    print("Не удалось импортировать модуль document_abstractions.")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Использование: python convert_links.py <путь_к_файлу>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Инициализируем реестр документов
    registry = DocumentRegistry()
    
    # Преобразуем ссылки
    print(f"Преобразование ссылок в файле '{file_path}'...")
    success = registry.update_document_links(file_path, to_abstract=True)
    
    if success:
        print(f"Ссылки успешно преобразованы в абстрактные.")
    else:
        print(f"Не удалось преобразовать ссылки.")

if __name__ == "__main__":
    main()