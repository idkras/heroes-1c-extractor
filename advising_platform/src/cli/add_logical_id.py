#!/usr/bin/env python3
"""
Скрипт для добавления логического идентификатора документу.
"""

import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from advising_platform.advising_platform.src.core.document_abstractions import DocumentRegistry, DocumentIdentifier, DocumentMetadata
except ImportError:
    print("Не удалось импортировать модуль document_abstractions.")
    sys.exit(1)

def create_logical_id(file_path, doc_type=None, primary_id=None, secondary_id=None):
    """
    Создает логический идентификатор для документа и добавляет его в реестр.
    
    Args:
        file_path: Путь к файлу документа
        doc_type: Тип документа (standard, project, incident, etc.)
        primary_id: Первичный идентификатор (имя стандарта, проекта и т.д.)
        secondary_id: Вторичный идентификатор (подтип документа для проектов)
    
    Returns:
        Созданный логический идентификатор или None, если не удалось создать
    """
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не существует")
        return None
    
    # Нормализуем путь
    file_path = os.path.normpath(file_path)
    
    # Инициализируем реестр документов
    registry = DocumentRegistry()
    
    # Проверяем, есть ли уже идентификатор для этого документа
    for identifier, metadata in registry.id_mapping.items():
        if metadata.path == file_path:
            print(f"Документ {file_path} уже имеет идентификатор: {identifier}")
            return identifier
    
    # Если документ еще не проиндексирован, добавляем его
    if file_path not in registry.documents:
        try:
            metadata = DocumentMetadata.from_file(file_path)
            registry.documents[file_path] = metadata
            print(f"Документ {file_path} успешно добавлен в реестр")
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")
            return None
    else:
        metadata = registry.documents[file_path]
    
    # Если тип не указан, пытаемся определить его
    if not doc_type:
        doc_type = metadata.doc_type or DocumentIdentifier.DOC_TYPE_OTHER
    
    # Если первичный идентификатор не указан, генерируем его из имени файла
    if not primary_id:
        # Получаем имя файла без расширения
        basename = os.path.basename(file_path)
        primary_id = os.path.splitext(basename)[0].lower().replace(' ', '_')
    
    # Создаем идентификатор
    identifier = DocumentIdentifier(doc_type, primary_id, secondary_id)
    
    # Добавляем его в маппинг
    registry.id_mapping[identifier.to_string()] = metadata
    print(f"Создан логический идентификатор: {identifier.to_string()}")
    
    # Сохраняем реестр
    try:
        registry.export_to_json()
        print("Реестр документов успешно обновлен")
    except Exception as e:
        print(f"Ошибка при сохранении реестра: {e}")
    
    return identifier.to_string()

def main():
    if len(sys.argv) < 2:
        print("Использование: python add_logical_id.py <путь_к_файлу> [тип_документа] [первичный_id] [вторичный_id]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else None
    primary_id = sys.argv[3] if len(sys.argv) > 3 else None
    secondary_id = sys.argv[4] if len(sys.argv) > 4 else None
    
    create_logical_id(file_path, doc_type, primary_id, secondary_id)

if __name__ == "__main__":
    main()