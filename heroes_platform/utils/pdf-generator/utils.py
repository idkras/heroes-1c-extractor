#!/usr/bin/env python3
"""
Utility functions for PDF Generator
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def validate_markdown_content(content: str) -> List[str]:
    """
    Валидирует содержимое markdown файла на типичные проблемы.
    
    Returns:
        List[str]: Список найденных проблем
    """
    issues = []
    
    # Проверка на лишние пробелы
    if re.search(r'\s{3,}', content):
        issues.append("Найдены множественные пробелы")
    
    # Проверка неправильных разделителей таблиц
    if re.search(r'———————[-—]+', content):
        issues.append("Найдены неправильные разделители таблиц")
    
    # Проверка слишком длинных строк
    lines = content.split('\n')
    long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 200]
    if long_lines:
        issues.append(f"Очень длинные строки: {long_lines[:5]}")
    
    # Проверка некорректных ссылок
    if re.search(r'ФЗ-\s+\d+', content):
        issues.append("Неправильные пробелы в номерах ФЗ")
    
    return issues

def analyze_pdf_text_quality(text: str) -> Dict[str, any]:
    """
    Анализирует качество текста из PDF.
    
    Returns:
        Dict с метриками качества
    """
    words = text.split()
    lines = text.split('\n')
    
    # Базовые метрики
    metrics = {
        'word_count': len(words),
        'line_count': len(lines),
        'avg_words_per_line': len(words) / max(len(lines), 1),
        'char_count': len(text)
    }
    
    # Проверка длины строк
    line_lengths = [len(line) for line in lines if line.strip()]
    if line_lengths:
        metrics['avg_line_length'] = sum(line_lengths) / len(line_lengths)
        metrics['min_line_length'] = min(line_lengths)
        metrics['max_line_length'] = max(line_lengths)
    
    # Проверка пробелов
    metrics['multiple_spaces'] = len(re.findall(r'\s{3,}', text))
    metrics['quality_score'] = calculate_quality_score(metrics)
    
    return metrics

def calculate_quality_score(metrics: Dict[str, any]) -> float:
    """
    Рассчитывает общий балл качества PDF (0-100).
    """
    score = 100.0
    
    # Штрафы за проблемы
    if metrics.get('multiple_spaces', 0) > 0:
        score -= 20  # Большой штраф за множественные пробелы
    
    if metrics.get('word_count', 0) < 100:
        score -= 30  # Очень мало текста
    
    avg_line = metrics.get('avg_line_length', 0)
    if avg_line < 30 or avg_line > 85:
        score -= 15  # Неоптимальная длина строк
    
    return max(0.0, score)

def extract_pdf_metadata(pdf_path: Path) -> Dict[str, any]:
    """
    Извлекает метаданные из PDF файла.
    """
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            metadata = {
                'page_count': len(reader.pages),
                'file_size': pdf_path.stat().st_size,
                'file_size_kb': round(pdf_path.stat().st_size / 1024, 1)
            }
            
            # Извлекаем метаданные PDF
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', '')
                })
            
            return metadata
            
    except Exception as e:
        return {'error': str(e)}

def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в читаемый вид.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def create_quality_report(pdf_path: Path, text_content: str) -> Dict[str, any]:
    """
    Создает полный отчет о качестве PDF документа.
    """
    metadata = extract_pdf_metadata(pdf_path)
    text_quality = analyze_pdf_text_quality(text_content)
    
    report = {
        'file_info': {
            'path': str(pdf_path),
            'size': format_file_size(metadata.get('file_size', 0)),
            'pages': metadata.get('page_count', 0)
        },
        'text_quality': text_quality,
        'metadata': metadata,
        'timestamp': str(Path.ctime(Path.now()) if pdf_path.exists() else "unknown")
    }
    
    return report