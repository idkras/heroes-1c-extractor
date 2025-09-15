#!/usr/bin/env python3
"""
Protocol Completion - добавление report_progress() во все MCP команды
Автономная реализация для задачи T034
"""

import json
from datetime import datetime
from typing import Dict, Any

class ProtocolCompletionManager:
    """Менеджер для добавления Protocol Completion во все MCP операции"""
    
    def __init__(self):
        self.operations_log = []
        
    def report_mcp_progress(self, command: str, params: Dict[str, Any], result: Dict[str, Any], duration_ms: float):
        """Отчет о прогрессе MCP операции для пользователя"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Форматируем красивый отчет для пользователя
        progress_report = f"""
🔌 MCP ОПЕРАЦИЯ ВЫПОЛНЕНА
⏰ {timestamp} | 🚀 {command} | ⚡ {duration_ms:.1f}мс

📥 Входные параметры:
{self._format_params(params)}

📤 Результат:
{self._format_result(result)}

✅ Статус: {'УСПЕШНО' if result.get('success', True) else 'ОШИБКА'}
"""
        
        # Логируем операцию
        operation_log = {
            "timestamp": timestamp,
            "command": command,
            "params": params,
            "result": result,
            "duration_ms": duration_ms,
            "success": result.get('success', True)
        }
        
        self.operations_log.append(operation_log)
        
        # Выводим отчет пользователю
        print(progress_report)
        
        # Возвращаем для интеграции с другими системами
        return progress_report
    
    def _format_params(self, params: Dict[str, Any]) -> str:
        """Форматирует параметры для красивого вывода"""
        if not params:
            return "  (нет параметров)"
        
        formatted = []
        for key, value in params.items():
            if isinstance(value, str) and len(value) > 50:
                value = value[:47] + "..."
            formatted.append(f"  • {key}: {value}")
        
        return "\n".join(formatted)
    
    def _format_result(self, result: Dict[str, Any]) -> str:
        """Форматирует результат для красивого вывода"""
        if not result:
            return "  (пустой результат)"
        
        # Основные поля для отображения
        important_fields = ['success', 'message', 'content_length', 'compliance_score', 'task_id', 'incident_id']
        formatted = []
        
        for field in important_fields:
            if field in result:
                formatted.append(f"  • {field}: {result[field]}")
        
        # Добавляем счетчики если есть
        for key, value in result.items():
            if key not in important_fields and isinstance(value, (int, float)):
                formatted.append(f"  • {key}: {value}")
        
        return "\n".join(formatted) if formatted else "  ✅ Операция выполнена успешно"
    
    def get_operations_summary(self) -> str:
        """Получает сводку всех выполненных операций"""
        if not self.operations_log:
            return "📊 MCP операций пока не выполнялось"
        
        total_ops = len(self.operations_log)
        successful_ops = len([op for op in self.operations_log if op['success']])
        avg_duration = sum(op['duration_ms'] for op in self.operations_log) / total_ops
        
        recent_ops = self.operations_log[-3:]  # Последние 3 операции
        
        summary = f"""
🔌 СВОДКА MCP ОПЕРАЦИЙ
📊 Всего: {total_ops} | ✅ Успешных: {successful_ops} | ⚡ Среднее время: {avg_duration:.1f}мс

🔄 Последние операции:"""
        
        for op in reversed(recent_ops):
            status = "✅" if op['success'] else "❌"
            summary += f"\n{status} {op['timestamp']} {op['command']} ({op['duration_ms']:.1f}мс)"
        
        return summary

# Глобальный экземпляр для использования во всех MCP командах
protocol_manager = ProtocolCompletionManager()

def report_mcp_progress(command: str, params: Dict[str, Any], result: Dict[str, Any], duration_ms: float):
    """Функция-обертка для удобного использования в MCP командах"""
    return protocol_manager.report_mcp_progress(command, params, result, duration_ms)

def get_mcp_summary():
    """Получает сводку MCP операций"""
    return protocol_manager.get_operations_summary()

if __name__ == "__main__":
    # Демонстрация работы
    manager = ProtocolCompletionManager()
    
    # Пример операции
    test_params = {"address": "task_master", "format": "summary"}
    test_result = {"success": True, "content_length": 1500, "message": "Стандарт успешно найден"}
    
    manager.report_mcp_progress("standards-resolver", test_params, test_result, 45.2)
    
    print("\n" + "="*60)
    print(manager.get_operations_summary())