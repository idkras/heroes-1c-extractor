"""
Модуль кеширования для advising_platform.

Предоставляет классы и функции для эффективного кеширования данных и файлов
с контролем использования памяти и потокобезопасностью.
"""

from .real_inmemory_cache import get_cache, RealInMemoryCache
from .critical_section import CriticalSectionManager, critical_section

__all__ = ['get_cache', 'RealInMemoryCache', 'CriticalSectionManager', 'critical_section']