"""
API для работы со стандартами, документацией и абстрактными ссылками.
"""

from advising_platform.src.api.standards.routes import register_standards_api
from advising_platform.src.api.standards.documentation import register_documentation_api

__all__ = ['register_standards_api', 'register_documentation_api']