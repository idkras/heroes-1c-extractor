#!/usr/bin/env python3
"""
Триггер диагностики кеша с контрольными суммами.

JTBD: Как система, я хочу иметь стандартный триггер диагностики кеша,
чтобы всегда выводить актуальную информацию в едином формате.

Использует реальные переменные и вычисления, а не статический текст.
Автор: AI Assistant
Дата: 24 May 2025
"""

import sys
import os
import hashlib
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def calculate_file_hash(filepath: str) -> str:
    """Вычисляет SHA256 хеш файла"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def get_cache_diagnostics():
    """Получает реальную диагностику кеша с вычислениями"""
    
    from src.cache.real_inmemory_cache import get_cache
    
    # Инициализируем кеш
    cache = get_cache()
    cache.clear()
    cache.initialize_from_disk()
    
    # Полные названия папок (НЕ сокращенные!)
    folder_mappings = {
        '0. core standards': '0. core standards',
        '1. process · goalmap · task · incidents · tickets · qa': '1. process · goalmap · task · incidents · tickets · qa', 
        '2. projects · context · next actions': '2. projects · context · next actions',
        '3. scenarium · jtbd · hipothises · offering · tone': '3. scenarium · jtbd · hipothises · offering · tone',
        '4. dev · design · qa': '4. dev · design · qa',
        '6. advising · review · supervising': '6. advising · review · supervising',
        '8. auto · n8n': '8. auto · n8n'
    }
    
    standards = cache.get_documents_by_type('standard')
    archive_patterns = ['[archive]', 'archive', 'backup', '20250', 'old', 'deprecated', 'consolidated', 'rename']
    
    folder_results = []
    total_files = 0
    total_matches = 0
    
    # Реальные вычисления для каждой папки
    for folder_key, folder_full_name in folder_mappings.items():
        folder_files = []
        hash_matches = 0
        
        # Находим файлы папки (только активные)
        for standard in standards:
            if any(pattern in standard.path.lower() for pattern in archive_patterns):
                continue
            if folder_key in standard.path:
                folder_files.append(standard)
        
        # Вычисляем РЕАЛЬНЫЕ хеш-суммы
        for standard in folder_files:
            cache_hash = hashlib.sha256(standard.content.encode('utf-8')).hexdigest()
            disk_hash = calculate_file_hash(standard.path)
            
            if disk_hash and cache_hash == disk_hash:
                hash_matches += 1
        
        count = len(folder_files)
        sync_percent = (hash_matches / count * 100) if count > 0 else 0
        
        folder_results.append({
            'name': folder_full_name,
            'count': count,
            'sync_percent': sync_percent
        })
        
        total_files += count
        total_matches += hash_matches
    
    # Общая синхронизация
    overall_sync = (total_matches / total_files * 100) if total_files > 0 else 0
    
    # Ключевые файлы с РЕАЛЬНЫМИ подсчетами
    key_files = {}
    
    # todo.md
    try:
        with open('[todo · incidents]/todo.md', 'r', encoding='utf-8') as f:
            todo_content = f.read()
        
        open_tasks = todo_content.count('- [ ]')
        completed_tasks = todo_content.count('- [x]')
        hypotheses = todo_content.lower().count('гипотеза') + todo_content.lower().count('hypothesis')
        
        todo_cache = cache.get_document('[todo · incidents]/todo.md')
        if todo_cache:
            disk_hash = hashlib.sha256(todo_content.encode('utf-8')).hexdigest()
            cache_hash = hashlib.sha256(todo_cache.content.encode('utf-8')).hexdigest()
            todo_sync = 100 if disk_hash == cache_hash else 0
        else:
            todo_sync = 0
        
        key_files['todo'] = {
            'open_tasks': open_tasks,
            'completed_tasks': completed_tasks,
            'hypotheses': hypotheses,
            'sync_percent': todo_sync
        }
    except:
        key_files['todo'] = {'open_tasks': 0, 'completed_tasks': 0, 'hypotheses': 0, 'sync_percent': 0}
    
    # ai.incidents.md
    try:
        with open('[todo · incidents]/ai.incidents.md', 'r', encoding='utf-8') as f:
            incidents_content = f.read()
        
        open_incidents = incidents_content.count('- [ ]')
        completed_incidents = incidents_content.count('- [x]')
        
        inc_cache = cache.get_document('[todo · incidents]/ai.incidents.md')
        if inc_cache:
            disk_hash = hashlib.sha256(incidents_content.encode('utf-8')).hexdigest()
            cache_hash = hashlib.sha256(inc_cache.content.encode('utf-8')).hexdigest()
            inc_sync = 100 if disk_hash == cache_hash else 0
        else:
            inc_sync = 0
        
        key_files['incidents'] = {
            'open_incidents': open_incidents,
            'completed_incidents': completed_incidents,
            'sync_percent': inc_sync
        }
    except:
        key_files['incidents'] = {'open_incidents': 0, 'completed_incidents': 0, 'sync_percent': 0}
    
    return {
        'folders': folder_results,
        'total_files': total_files,
        'total_matches': total_matches,
        'overall_sync': overall_sync,
        'key_files': key_files
    }

def format_diagnostic_report(diagnostics):
    """Форматирует диагностику в стандартный шаблон"""
    
    # Заголовок
    report = "🔍 **ЧЕСТНАЯ ДИАГНОСТИКА КЕША С КОНТРОЛЬНЫМИ СУММАМИ:**\n\n"
    
    # Папки стандартов
    report += "📋 **Распределение по папкам стандартов:**\n"
    for folder in diagnostics['folders']:
        count = folder['count']
        sync = folder['sync_percent']
        name = folder['name']
        unit = 'стандарт' if count == 1 else ('стандарта' if 2 <= count <= 4 else 'стандартов')
        report += f"→ {name}: {count} {unit} · {sync:.0f}% хеш-сумма\n"
    
    # Общая синхронизация
    total = diagnostics['total_files']
    matches = diagnostics['total_matches'] 
    overall = diagnostics['overall_sync']
    report += f"\n📊 **ОБЩАЯ СИНХРОНИЗАЦИЯ**: {matches}/{total} файлов = {overall:.1f}%\n\n"
    
    # Ключевые файлы
    report += "🧪 **КЛЮЧЕВЫЕ ФАЙЛЫ** с контрольными суммами:\n"
    
    todo = diagnostics['key_files']['todo']
    todo_sync_icon = '✅' if todo['sync_percent'] == 100 else '❌'
    report += f"✓ todo.md: {todo['open_tasks']} открытых задач, {todo['completed_tasks']} выполненных, {todo['hypotheses']} гипотез, хеш-сумма: {todo_sync_icon} {todo['sync_percent']:.0f}%\n"
    
    inc = diagnostics['key_files']['incidents']
    inc_sync_icon = '✅' if inc['sync_percent'] == 100 else '❌'
    report += f"✓ ai.incidents.md: {inc['open_incidents']} открытых инцидентов, {inc['completed_incidents']} выполненных, хеш-сумма: {inc_sync_icon} {inc['sync_percent']:.0f}%"
    
    return report

def main():
    """Запускает диагностику и выводит отчет"""
    print("🔄 Запуск диагностики кеша...")
    
    diagnostics = get_cache_diagnostics()
    report = format_diagnostic_report(diagnostics)
    
    print(report)
    
    # Возвращаем данные для использования в report_progress()
    return report

if __name__ == "__main__":
    main()