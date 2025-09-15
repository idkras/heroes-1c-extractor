#!/usr/bin/env python3
"""
MCP Dashboard - Visual Progress Reporter

JTBD: Я (система) хочу наглядно показывать все MCP операции в реальном времени,
чтобы пользователь видел что происходит с Standards-MCP сервером.

Интеграция с report_progress() для визуализации команд MCP протокола.

Автор: AI Assistant
Дата: 26 May 2025
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class MCPCommand:
    """Структура команды MCP для отображения."""
    timestamp: str
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    duration_ms: float
    status: str  # "success", "error", "in_progress"
    error_message: str = ""

class MCPDashboard:
    """
    JTBD: Я (dashboard) хочу визуализировать MCP операции в красивом формате,
    чтобы обеспечить полную прозрачность работы Standards-MCP сервера.
    """
    
    def __init__(self):
        self.commands_history: List[MCPCommand] = []
        self.active_sessions: Dict[str, Any] = {}
        self.stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "avg_response_time": 0.0,
            "uptime_start": datetime.now().isoformat()
        }
    
    def log_mcp_command(self, tool_name: str, parameters: Dict[str, Any], 
                       result: Dict[str, Any], duration_ms: float, 
                       status: str = "success", error_message: str = "") -> None:
        """
        JTBD: Я (метод) хочу записать выполненную MCP команду,
        чтобы отобразить её в dashboard с полной информацией.
        """
        command = MCPCommand(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message
        )
        
        self.commands_history.append(command)
        self._update_stats(command)
        
        # Ограничиваем историю последними 100 командами
        if len(self.commands_history) > 100:
            self.commands_history = self.commands_history[-100:]
    
    def _update_stats(self, command: MCPCommand) -> None:
        """Обновляет статистику dashboard."""
        self.stats["total_commands"] += 1
        
        if command.status == "success":
            self.stats["successful_commands"] += 1
        else:
            self.stats["failed_commands"] += 1
        
        # Обновляем среднее время отклика
        total_time = sum(cmd.duration_ms for cmd in self.commands_history)
        self.stats["avg_response_time"] = total_time / len(self.commands_history)
    
    def generate_progress_report(self) -> str:
        """
        JTBD: Я (генератор) хочу создать красивый отчет для report_progress(),
        чтобы показать текущее состояние MCP сервера в наглядном виде.
        """
        if not self.commands_history:
            return "🔌 Standards-MCP сервер запущен, ожидает команд..."
        
        recent_commands = self.commands_history[-5:]  # Последние 5 команд
        
        report = []
        report.append("🔌 **Standards-MCP Server Dashboard**")
        report.append("")
        
        # Статистика
        success_rate = (self.stats["successful_commands"] / self.stats["total_commands"]) * 100
        report.append(f"📊 **Статистика**: {self.stats['total_commands']} команд | "
                     f"{success_rate:.1f}% успешных | "
                     f"⚡ {self.stats['avg_response_time']:.1f}мс")
        report.append("")
        
        # Последние команды
        report.append("🔄 **Последние MCP команды**:")
        for cmd in recent_commands:
            status_icon = "✅" if cmd.status == "success" else "❌"
            time_str = cmd.timestamp.split("T")[1][:8]  # Только время
            
            report.append(f"{status_icon} `{time_str}` **{cmd.tool_name}** "
                         f"({cmd.duration_ms:.1f}мс)")
            
            # Показываем ключевые параметры
            if cmd.parameters:
                key_params = self._extract_key_parameters(cmd.tool_name, cmd.parameters)
                if key_params:
                    report.append(f"   📝 {key_params}")
            
            # Показываем результат кратко
            if cmd.result and cmd.status == "success":
                summary = self._summarize_result(cmd.tool_name, cmd.result)
                if summary:
                    report.append(f"   💡 {summary}")
            
            if cmd.error_message:
                report.append(f"   ⚠️ {cmd.error_message}")
            
            report.append("")
        
        # Активные сессии
        if self.active_sessions:
            report.append("🎯 **Активные сессии**: " + 
                         ", ".join(self.active_sessions.keys()))
        
        return "\n".join(report)
    
    def _extract_key_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Извлекает ключевые параметры для отображения."""
        if tool_name == "standards-resolver":
            address = parameters.get("address", "")
            format_type = parameters.get("format", "full")
            return f"Резолвинг: {address} → {format_type}"
        
        elif tool_name == "suggest-standards":
            jtbd = parameters.get("jtbd", "")[:50]
            task_type = parameters.get("taskType", "unknown")
            return f"JTBD: {jtbd}... → {task_type}"
        
        elif tool_name == "validate-compliance":
            content_len = len(parameters.get("content", ""))
            strict = parameters.get("strictMode", False)
            return f"Валидация: {content_len} символов, strict={strict}"
        
        elif tool_name == "standards-navigator":
            query = parameters.get("query", "")
            category = parameters.get("category", "")
            return f"Поиск: '{query}' в {category}"
        
        return ""
    
    def _summarize_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """Создает краткое описание результата."""
        if not result.get("success", False):
            return f"Ошибка: {result.get('error', 'Unknown')}"
        
        if tool_name == "standards-resolver":
            format_type = result.get("format", "")
            address = result.get("address", "").split(":")[-1]
            return f"Стандарт '{address}' резолвен в формате {format_type}"
        
        elif tool_name == "suggest-standards":
            count = len(result.get("suggestions", []))
            if count > 0:
                top_title = result["suggestions"][0].get("title", "")[:30]
                return f"Найдено {count} предложений, топ: {top_title}..."
            return "Предложений не найдено"
        
        elif tool_name == "validate-compliance":
            score = result.get("compliance_score", 0)
            status = result.get("status", "unknown")
            violations = result.get("summary", {}).get("total_violations", 0)
            return f"Соответствие: {score:.2f} ({status}), нарушений: {violations}"
        
        elif tool_name == "standards-navigator":
            found = result.get("total_found", 0)
            return f"Найдено стандартов: {found}"
        
        return "Выполнено успешно"
    
    def get_live_dashboard(self) -> Dict[str, Any]:
        """
        JTBD: Я (API) хочу предоставить данные dashboard в JSON формате,
        чтобы фронтенд мог отобразить интерактивную панель.
        """
        return {
            "stats": self.stats,
            "recent_commands": [asdict(cmd) for cmd in self.commands_history[-10:]],
            "active_sessions": self.active_sessions,
            "server_status": "running",
            "last_updated": datetime.now().isoformat()
        }
    
    def start_session(self, session_id: str, description: str) -> None:
        """Начинает новую сессию MCP команд."""
        self.active_sessions[session_id] = {
            "description": description,
            "started_at": datetime.now().isoformat(),
            "commands_count": 0
        }
    
    def end_session(self, session_id: str) -> None:
        """Завершает сессию MCP команд."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

# Глобальный экземпляр dashboard
mcp_dashboard = MCPDashboard()

def report_mcp_progress() -> str:
    """
    JTBD: Я (функция) хочу интегрироваться с report_progress(),
    чтобы показать актуальное состояние MCP сервера.
    """
    return mcp_dashboard.generate_progress_report()

def log_mcp_operation(tool_name: str, parameters: Dict[str, Any], 
                     result: Dict[str, Any], duration_ms: float, 
                     status: str = "success", error_message: str = "") -> None:
    """
    JTBD: Я (логгер) хочу записать MCP операцию для отображения,
    чтобы обеспечить полную трассировку команд сервера.
    """
    mcp_dashboard.log_mcp_command(tool_name, parameters, result, 
                                 duration_ms, status, error_message)

# Пример использования с report_progress()
def demo_mcp_dashboard():
    """Демонстрация работы MCP Dashboard."""
    print("🎯 === DEMO: MCP Dashboard Integration ===")
    
    # Симулируем несколько MCP команд
    log_mcp_operation(
        "standards-resolver",
        {"address": "abstract://standard:tdd", "format": "summary"},
        {"success": True, "format": "summary", "address": "abstract://standard:tdd"},
        45.2
    )
    
    log_mcp_operation(
        "suggest-standards", 
        {"jtbd": "Я хочу создать API", "taskType": "development"},
        {"success": True, "suggestions": [{"title": "API Development Standard"}]},
        67.8
    )
    
    # Показываем отчет
    report = report_mcp_progress()
    print(report)
    
    return report

if __name__ == "__main__":
    demo_mcp_dashboard()