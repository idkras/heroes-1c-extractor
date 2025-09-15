"""
Инструменты для работы с документами и абстрактными ссылками.

Этот модуль содержит набор инструментов для:
1. Управления абстрактными идентификаторами документов
2. Преобразования ссылок между абстрактными и физическими форматами
3. Регистрации логических идентификаторов для документов
4. Работы с содержимым документов
5. Управления стандартами и их валидации
"""

from pathlib import Path

# Корневая директория проекта
ROOT_DIR = Path(__file__).parent.parent.parent.parent

# Пути к директориям
STANDARDS_DIR = ROOT_DIR / "[standards .md]"
TASKS_DIR = ROOT_DIR / "[todo · incidents]"

# Инструменты для работы со стандартами будут доступны через:
# from advising_platform.src.tools.document.standards_manager import validate_standards

__all__ = [
    'STANDARDS_DIR',
    'TASKS_DIR',
    'ROOT_DIR'
]