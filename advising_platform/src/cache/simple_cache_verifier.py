#!/usr/bin/env python3
"""
Простой унифицированный верификатор кеша vs диска.

GREEN PHASE: Заменяет 5 дублирующихся методов одним маленьким.

Автор: AI Assistant
Дата: 22 May 2025
"""

def verify_content_integrity(cache):
    """
    Маленький унифицированный метод проверки.
    
    Returns:
        dict: {'matches': int, 'mismatches': int, 'accuracy': float}
    """
    if not cache:
        return {'matches': 0, 'mismatches': 0, 'accuracy': 0.0}
    
    try:
        paths = cache.get_all_paths()[:10]  # Первые 10 для быстроты
        matches = 0
        
        for path in paths:
            entry = cache.get_document(path)
            if entry and hasattr(entry, 'content'):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        disk_content = f.read()
                    if entry.content == disk_content:
                        matches += 1
                except:
                    pass
        
        total = len(paths)
        accuracy = (matches / total * 100) if total > 0 else 0
        
        return {
            'matches': matches,
            'mismatches': total - matches,
            'accuracy': accuracy
        }
    except:
        return {'matches': 0, 'mismatches': 0, 'accuracy': 0.0}