"""
Heroes Platform - универсальная библиотека для создания AI-ассистированных проектов
с интеграцией MCP серверов, стандартов и workflow.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Ilya Krasinsky"
__email__ = "ilya@magicrick.com"

# Основные модули
from . import shared
from . import src
from . import heroes_mcp

__all__ = [
    "shared",
    "src", 
    "heroes_mcp",
    "__version__",
    "__author__",
    "__email__"
]
