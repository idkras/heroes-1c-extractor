#!/usr/bin/env python3
"""
Configuration for PDF Generator Utils
"""

# Default PDF settings
DEFAULT_PDF_CONFIG = {
    "page_size": "A4",
    "margin": "20mm",
    "font_family": "Georgia, Times New Roman, serif",
    "font_size": "10pt",
    "line_height": 1.4,
    "max_width": "165mm",
    "color": "#2d2d2d",
}

# Typography standards
TYPOGRAPHY_STANDARDS = {
    "optimal_line_length_chars": (55, 75),
    "min_line_length_chars": 30,
    "max_line_length_chars": 85,
    "heading_line_height": 1.2,
    "paragraph_spacing": "6pt",
    "heading_spacing_top": "18pt",
    "heading_spacing_bottom": "6pt",
}

# Quality thresholds
QUALITY_THRESHOLDS = {
    "min_text_per_page": 50,
    "max_empty_pages_ratio": 0.3,
    "max_consecutive_spaces": 2,
    "min_word_count": 100,
}

# File paths
DEFAULT_PATHS = {
    "input_dir": "input/",
    "output_dir": "output/",
    "temp_dir": "temp/",
    "test_files_dir": "tests/fixtures/",
}

# Testing configuration
TEST_CONFIG = {
    "timeout_seconds": 30,
    "browser_headless": True,
    "screenshot_on_failure": True,
}
