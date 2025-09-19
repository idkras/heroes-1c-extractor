#!/usr/bin/env python3
"""
PDF Quality Tests Collection

Автоматизированные тесты качества PDF документов.
"""

# Основные тесты качества
from .test_comprehensive_pdf_quality import test_generator_compliance, test_pdf_exists
from .test_pdf_visual_quality import (
    test_pdf_no_empty_pages,
    test_pdf_no_spacing_holes,
    test_pdf_proper_font_usage,
)

__all__ = [
    "test_pdf_no_spacing_holes",
    "test_pdf_proper_font_usage",
    "test_pdf_no_empty_pages",
    "test_pdf_exists",
    "test_generator_compliance",
]
