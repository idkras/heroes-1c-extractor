#!/usr/bin/env python3
"""
Скрипт для преобразования физических ссылок в абстрактные.
"""

from document_abstractions import DocumentRegistry
import sys

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