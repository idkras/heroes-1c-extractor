#!/usr/bin/env python3
"""
PDF Generator Utils - Централизованная коллекция утилит для генерации PDF

Рекомендуемый импорт:
    from pdf_generator.generators.pdf_generator_refactored import convert_md_to_pdf_refactored
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "Утилиты для профессиональной генерации PDF документов"

# Главный интерфейс - новый рефакторенный генератор
try:
    from .generators.pdf_generator_refactored import convert_md_to_pdf_refactored
except ImportError:
    pass

# Для продвинутого использования
try:
    from .generators.generate_pdf_playwright import convert_md_to_pdf_playwright
except ImportError:
    # Playwright может быть не установлен
    pass

# Тестирование
try:
    from .tests.test_pdf_visual_quality import (
        test_pdf_no_spacing_holes,
        test_pdf_proper_font_usage,
    )
except ImportError:
    pass

__all__ = [
    "convert_md_to_pdf_refactored",
    "convert_md_to_pdf_playwright",
    "test_pdf_no_spacing_holes",
    "test_pdf_proper_font_usage",
]
