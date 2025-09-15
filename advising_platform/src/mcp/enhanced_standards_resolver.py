#!/usr/bin/env python3
"""
Enhanced Standards Resolver с Protocol Completion
Версия с интегрированным report_progress() для задачи T034
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

def enhanced_standards_resolver(request):
    """Резолвер стандартов с Protocol Completion."""
    
    start_time = datetime.now()
    
    try:
        # Импорт необходимых модулей
        from advising_platform.src.core.unified_key_resolver import UnifiedKeyResolver
        from advising_platform.src.cache.real_inmemory_cache import get_cache
        from advising_platform.src.mcp.mcp_dashboard import log_mcp_operation
    except ImportError as e:
        # Обработка ошибок импорта
        return {
            "success": False,
            "error": f"Import error: {str(e)}",
            "message": "Некоторые модули недоступны"
        }
    
    try:
        address = request.get("address", "")
        format_type = request.get("format", "full")
        context = request.get("context", "")
        
        print(f"🔌 MCP ОПЕРАЦИЯ НАЧАТА: standards-resolver")
        print(f"📥 Параметры: address={address}, format={format_type}")
        
        # Инициализация компонентов
        resolver = UnifiedKeyResolver()
        cache = get_cache()
        
        # Резолвинг адреса через кеш напрямую
        canonical_path = address  # Упрощенная версия
        print(f"🔍 Поиск стандарта: {address}")
        
        # Получение контента из кеша
        cache_entry = cache.get_document(address)
        
        if not cache_entry:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                "success": False,
                "error": f"Content not found for: {address}",
                "canonical_path": canonical_path
            }
            
            # Protocol Completion: отчет об ошибке
            print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
            print(f"⏰ Время выполнения: {duration:.1f}мс")
            print(f"📤 Результат: Контент не найден")
            
            # Логирование
            log_mcp_operation(
                'enhanced-standards-resolver',
                {"address": address, "format": format_type},
                result,
                duration
            )
            
            return result
        
        # Извлекаем строковый контент из CacheEntry
        raw_content = cache_entry.content if hasattr(cache_entry, 'content') else str(cache_entry)
        
        # Обработка контента в зависимости от формата
        if format_type == "summary":
            processed_content = extract_summary(raw_content)
        elif format_type == "checklist":
            processed_content = extract_checklist(raw_content)
        else:
            processed_content = raw_content
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": True,
            "address": address,
            "canonical_path": canonical_path,
            "format": format_type,
            "content": processed_content,
            "content_length": len(processed_content),
            "processing_time_ms": duration
        }
        
        # Protocol Completion: отчет об успехе
        print(f"✅ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"📊 Размер контента: {len(processed_content)} символов")
        print(f"🎯 Формат: {format_type}")
        print(f"📝 Стандарт '{address}' успешно резолвен")
        
        # Логирование операции
        log_mcp_operation(
            'enhanced-standards-resolver',
            {"address": address, "format": format_type},
            {"success": True, "content_found": True, "content_length": len(processed_content)},
            duration
        )
        
        # Триггер следующих шагов
        suggest_next_actions(address, format_type)
        
        return result
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            "success": False,
            "error": str(e),
            "message": "Ошибка при резолвинге стандарта"
        }
        
        # Protocol Completion: отчет об ошибке
        print(f"❌ MCP ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ")
        print(f"⏰ Время выполнения: {duration:.1f}мс")
        print(f"🚨 Ошибка: {str(e)}")
        
        # Логирование ошибки
        try:
            log_mcp_operation(
                'enhanced-standards-resolver',
                request,
                result,
                duration
            )
        except:
            pass
        
        return result

def extract_summary(content: str) -> str:
    """Извлекает краткое описание из стандарта."""
    lines = content.split('\n')
    
    # Ищем секцию с описанием
    for i, line in enumerate(lines):
        if any(marker in line.lower() for marker in ['цель документа', 'описание', 'jtbd']):
            summary_lines = []
            for j in range(i+1, min(i+6, len(lines))):
                if lines[j].strip() and not lines[j].startswith('#'):
                    summary_lines.append(lines[j].strip())
                elif summary_lines:
                    break
            return ' '.join(summary_lines)
    
    # Если не найдено специальной секции, берем первые значимые строки
    for line in lines[:10]:
        if line.strip() and not line.startswith('#') and len(line.strip()) > 50:
            return line.strip()
    
    return "Краткое описание недоступно"

def extract_checklist(content: str) -> list:
    """Извлекает чек-листы из стандарта."""
    checklist = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('- [ ]') or line.startswith('- [x]'):
            item = line.replace('- [ ]', '').replace('- [x]', '').strip()
            if item:
                checklist.append(item)
    
    return checklist

def suggest_next_actions(address: str, format_type: str):
    """Предлагает следующие действия на основе резолвенного стандарта."""
    
    print(f"\n🎯 ПРЕДЛАГАЕМЫЕ СЛЕДУЮЩИЕ ШАГИ:")
    
    if "task" in address.lower():
        print("• Создать задачу через MCP команду create-task")
        print("• Валидировать соответствие через validate-compliance")
    elif "process" in address.lower():
        print("• Применить протокол через protocol-handler")
        print("• Создать чек-лист действий")
    else:
        print("• Изучить связанные стандарты")
        print("• Применить в текущем контексте")
    
    print(f"• Запросить дополнительные стандарты через suggest-standards")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        request_data = json.loads(sys.argv[1])
        result = enhanced_standards_resolver(request_data)
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Enhanced Standards Resolver с Protocol Completion")
        print("Использование: python enhanced_standards_resolver.py '{\"address\": \"task_master\", \"format\": \"summary\"}'")