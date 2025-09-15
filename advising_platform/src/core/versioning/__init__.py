"""
Пакет версионирования документов.

Предоставляет инструменты для:
- Автоматического отслеживания версий документов
- Создания истории изменений
- Контекстного управления авторством и причинами изменений

Автор: AI Assistant
Дата: 20 мая 2025
"""

from .version_manager import VersionManager, VersionInfo, ChangelogEntry
from .version_decorators import (
    with_versioning, 
    auto_version, 
    configure_versioning, 
    VersionContext
)

__all__ = [
    'VersionManager', 
    'VersionInfo', 
    'ChangelogEntry',
    'with_versioning', 
    'auto_version', 
    'configure_versioning', 
    'VersionContext'
]