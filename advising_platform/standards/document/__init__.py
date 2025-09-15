"""
Модули для работы с документами в соответствии со стандартами.

Включает реализации для работы с абстрактными ссылками, индексации документов,
метаданными и другими аспектами документооборота согласно актуальным стандартам.
"""

from advising_platform.standards.document.abstract_links import (
    abstract_link_registry,
    create_abstract_link,
    resolve_abstract_link,
    extract_abstract_links,
    replace_abstract_links,
    register_abstract_link_resolver
)

__all__ = [
    'abstract_link_registry',
    'create_abstract_link',
    'resolve_abstract_link',
    'extract_abstract_links',
    'replace_abstract_links',
    'register_abstract_link_resolver'
]