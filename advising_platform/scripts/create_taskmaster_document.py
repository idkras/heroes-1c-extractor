#!/usr/bin/env python3
"""
Инструмент для создания документов по стандарту TaskMaster.

Создает новый документ в указанной директории с правильным именем файла
и структурой заголовка, соответствующими стандарту TaskMaster.

Использование:
    python create_taskmaster_document.py --type standard --title "Название документа"
"""

import os
import re
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class TaskMasterDocumentCreator:
    """Класс для создания документов по стандарту TaskMaster."""

    # Типы документов
    DOCUMENT_TYPES = {
        "standard": {
            "emoji": "📚",
            "sections": [
                "🎯 Цель стандарта",
                "📋 Требования",
                "🔍 Детали и примеры",
                "📊 Метрики соответствия"
            ],
            "directory": "advising standards .md",
            "base_standard": "Master Task Standard"
        },
        "project": {
            "emoji": "🚀",
            "sections": [
                "🎯 Цель проекта",
                "👥 Участники и роли",
                "📋 Требования",
                "📊 Метрики успеха",
                "⏱️ Сроки и этапы"
            ],
            "directory": "projects",
            "base_standard": "Master Task Standard, Project Standard"
        },
        "incident": {
            "emoji": "🚨",
            "sections": [
                "🎯 Описание инцидента",
                "🔍 Root Cause Analysis",
                "🛠️ Рекомендации по исправлению",
                "🔄 Предлагаемые изменения в процессе",
                "📆 Сроки исправления"
            ],
            "directory": "incidents",
            "base_standard": "Master Task Standard, AI Incident Standard"
        },
        "task": {
            "emoji": "📋",
            "sections": [
                "🎯 Цель задачи",
                "📋 Требования и ограничения",
                "🔍 Шаги выполнения",
                "📊 Критерии приемки"
            ],
            "directory": "tasks",
            "base_standard": "Master Task Standard, Process Standard"
        }
    }

    def __init__(self, root_directory: str = '.'):
        """
        Инициализирует создатель документов.
        
        Args:
            root_directory: Корневая директория проекта
        """
        self.root_directory = root_directory

    def generate_filename(self, title: str, version: str = "1.0", 
                         author: str = "Илья Красинский") -> str:
        """
        Генерирует имя файла по стандарту TaskMaster.
        
        Args:
            title: Название документа
            version: Версия документа
            author: Автор документа
            
        Returns:
            str: Имя файла соответствующее стандарту
        """
        now = datetime.now()
        date_str = now.strftime("%d %b %Y").lower()
        time_str = now.strftime("%H%M")
        
        # Очищаем название от недопустимых символов для имени файла
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
        
        filename = f"{version} {clean_title} by {date_str} {time_str} CET by {author}.md"
        return filename

    def generate_header(self, title: str, doc_type: str, author: str,
                      integrated: Optional[str] = None,
                      status: str = "Draft") -> str:
        """
        Генерирует заголовок документа по стандарту TaskMaster.
        
        Args:
            title: Название документа
            doc_type: Тип документа
            author: Автор документа
            integrated: Дополнительные интегрированные стандарты
            status: Статус документа
            
        Returns:
            str: Заголовок документа
        """
        type_info = self.DOCUMENT_TYPES.get(doc_type, self.DOCUMENT_TYPES["standard"])
        emoji = type_info["emoji"]
        base_standard = type_info["base_standard"]
        
        now = datetime.now()
        date_str = now.strftime("%d %b %Y").lower()
        time_str = now.strftime("%H:%M")
        
        header = f"# {emoji} {title}\n\n"
        header += f"updated: {date_str}, {time_str} CET by {author}  \n"
        header += f"based on: {base_standard}, version 10 may 2025, 17:00 CET  \n"
        
        if integrated:
            header += f"integrated: {integrated}  \n"
            
        header += f"status: {status}\n\n"
        header += "---\n\n"
        
        return header

    def generate_document_structure(self, doc_type: str, custom_sections: Optional[List[str]] = None) -> str:
        """
        Генерирует структуру документа с разделами.
        
        Args:
            doc_type: Тип документа
            custom_sections: Пользовательские разделы (если указаны)
            
        Returns:
            str: Структура документа
        """
        type_info = self.DOCUMENT_TYPES.get(doc_type, self.DOCUMENT_TYPES["standard"])
        sections = custom_sections if custom_sections else type_info["sections"]
        
        structure = ""
        for section in sections:
            structure += f"## {section}\n\n"
            structure += "_Содержание раздела..._\n\n"
            
        return structure

    def get_document_directory(self, doc_type: str, subdir: Optional[str] = None) -> str:
        """
        Возвращает директорию для сохранения документа.
        
        Args:
            doc_type: Тип документа
            subdir: Поддиректория (для проектов)
            
        Returns:
            str: Путь к директории
        """
        type_info = self.DOCUMENT_TYPES.get(doc_type, self.DOCUMENT_TYPES["standard"])
        base_dir = os.path.join(self.root_directory, type_info["directory"])
        
        if subdir:
            return os.path.join(base_dir, subdir)
        return base_dir

    def create_document(self, title: str, doc_type: str, 
                      author: str = "Илья Красинский",
                      version: str = "1.0",
                      subdir: Optional[str] = None,
                      integrated: Optional[str] = None,
                      custom_sections: Optional[List[str]] = None,
                      status: str = "Draft") -> Tuple[bool, str]:
        """
        Создает документ по стандарту TaskMaster.
        
        Args:
            title: Название документа
            doc_type: Тип документа
            author: Автор документа
            version: Версия документа
            subdir: Поддиректория (для проектов)
            integrated: Дополнительные интегрированные стандарты
            custom_sections: Пользовательские разделы
            status: Статус документа
            
        Returns:
            Tuple[bool, str]: Успех операции и путь к созданному файлу
        """
        # Генерируем имя файла и заголовок
        filename = self.generate_filename(title, version, author)
        header = self.generate_header(title, doc_type, author, integrated, status)
        
        # Генерируем структуру документа
        document_content = header + self.generate_document_structure(doc_type, custom_sections)
        
        # Определяем директорию для сохранения
        directory = self.get_document_directory(doc_type, subdir)
        
        # Создаем директорию, если она не существует
        os.makedirs(directory, exist_ok=True)
        
        # Путь к создаваемому файлу
        filepath = os.path.join(directory, filename)
        
        # Проверяем, не существует ли файл
        if os.path.exists(filepath):
            return False, f"Файл {filepath} уже существует"
        
        # Создаем файл
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(document_content)
            return True, filepath
        except Exception as e:
            return False, f"Ошибка при создании файла: {e}"


def parse_sections(sections_str: str) -> List[str]:
    """
    Парсит строку с разделами, разделенными запятыми.
    
    Args:
        sections_str: Строка с разделами
        
    Returns:
        List[str]: Список разделов
    """
    return [section.strip() for section in sections_str.split(',') if section.strip()]


def main():
    parser = argparse.ArgumentParser(description='Создание документов по стандарту TaskMaster')
    parser.add_argument('-y', '--type', required=True, 
                        choices=["standard", "project", "incident", "task"],
                        help='Тип документа')
    parser.add_argument('-t', '--title', required=True,
                        help='Название документа')
    parser.add_argument('-a', '--author', default="Илья Красинский",
                        help='Автор документа')
    parser.add_argument('-v', '--version', default="1.0",
                        help='Версия документа')
    parser.add_argument('-s', '--subdir', 
                        help='Поддиректория (для проектов)')
    parser.add_argument('-i', '--integrated', 
                        help='Дополнительные интегрированные стандарты')
    parser.add_argument('-c', '--custom-sections', 
                        help='Пользовательские разделы (разделенные запятыми)')
    parser.add_argument('-S', '--status', default="Draft",
                        choices=["Draft", "In Progress", "Review", "Approved", "Completed", "Archived"],
                        help='Статус документа')
    parser.add_argument('-r', '--root-directory', default='.',
                        help='Корневая директория проекта')
    
    args = parser.parse_args()
    
    creator = TaskMasterDocumentCreator(root_directory=args.root_directory)
    
    custom_sections = None
    if args.custom_sections:
        custom_sections = parse_sections(args.custom_sections)
    
    success, result = creator.create_document(
        title=args.title,
        doc_type=args.type,
        author=args.author,
        version=args.version,
        subdir=args.subdir,
        integrated=args.integrated,
        custom_sections=custom_sections,
        status=args.status
    )
    
    if success:
        print(f"✅ Документ успешно создан: {result}")
    else:
        print(f"❌ Ошибка: {result}")


if __name__ == "__main__":
    main()