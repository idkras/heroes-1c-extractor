#!/usr/bin/env python3
"""
MCP Consistency Validator
Проверяет соответствие MCP команд в коде и документации
"""

import sys
import json
from pathlib import Path

# Добавляем путь к модулям MCP
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'mcp' / 'modules'))

from advising_platform.src.mcp.modules.documentation_validator import DocumentationValidator


def main():
    """Основная функция валидации"""
    validator = MCPDocumentationValidator()
    
    print("🔍 Проверка консистентности MCP команд...")
    
    # Запускаем проверку соответствия команд
    consistency_result = validator._validate_mcp_commands_consistency()
    
    if consistency_result['status'] == 'passed':
        print("✅ Все MCP команды соответствуют документации")
        
        # Выводим статистику
        js_count = len(consistency_result['js_commands']['code'])
        python_count = len(consistency_result['python_commands']['code'])
        total_count = js_count + python_count
        
        print(f"📊 Найдено команд:")
        print(f"   - JavaScript: {js_count}")
        print(f"   - Python: {python_count}")
        print(f"   - Всего: {total_count}")
        
        return 0
        
    else:
        print("❌ Обнаружены несоответствия MCP команд:")
        
        # Показываем проблемы с JS командами
        js_missing = consistency_result['js_commands']['missing']
        js_extra = consistency_result['js_commands']['extra']
        
        if js_missing:
            print(f"   📄 JS команды в коде, но не в документации: {js_missing}")
            
        if js_extra:
            print(f"   📄 JS команды в документации, но не в коде: {js_extra}")
            
        # Показываем проблемы с Python командами
        python_missing = consistency_result['python_commands']['missing']
        python_extra = consistency_result['python_commands']['extra']
        
        if python_missing:
            print(f"   🐍 Python команды в коде, но не в документации: {python_missing}")
            
        if python_extra:
            print(f"   🐍 Python команды в документации, но не в коде: {python_extra}")
            
        return 1


if __name__ == '__main__':
    sys.exit(main())