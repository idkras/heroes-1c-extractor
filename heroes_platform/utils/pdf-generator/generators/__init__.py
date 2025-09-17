#!/usr/bin/env python3
"""
PDF Generators Collection

Различные генераторы PDF с разными подходами и технологиями.
"""

# Новый рефакторенный генератор (без WeasyPrint зависимостей)
try:
    from .pdf_generator_refactored import convert_md_to_pdf_refactored
    __all__ = ['convert_md_to_pdf_refactored']
except ImportError:
    __all__ = []

# Временно отключаем все генераторы с WeasyPrint до решения проблем с зависимостями
# try:
#     from .generate_pdf_playwright import convert_md_to_pdf_playwright
#     __all__.append('convert_md_to_pdf_playwright')
# except ImportError:
#     pass

# try:
#     from .generate_pdf_comprehensive_fix import convert_md_to_pdf_comprehensive
#     __all__.append('convert_md_to_pdf_comprehensive')
# except ImportError:
#     pass

# try:
#     from .generate_pdf_improved import convert_md_to_pdf_improved
#     __all__.append('convert_md_to_pdf_improved')
# except ImportError:
#     pass