#!/usr/bin/env python3
"""
MCP Logs Monitoring Test Suite
Тестирование мониторинга логов MCP серверов и Output панели Cursor

Автор: AI Assistant
Дата: 10 September 2025
Версия: 1.0.0
"""

import os
import sys
import json
import subprocess
import platform
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogError:
    """Структура для хранения информации об ошибке в логах"""
    timestamp: str
    error_type: str
    error_message: str
    log_file: str
    line_number: int
    severity: str  # critical, high, medium, low

@dataclass
class TestResult:
    """Результат теста мониторинга логов"""
    test_name: str
    status: str  # passed, failed, warning
    errors_found: List[LogError]
    recommendations: List[str]
    evidence: Dict[str, Any]

class MCPLogsMonitor:
    """Мониторинг логов MCP серверов и Cursor IDE"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.cursor_logs_path = self._get_cursor_logs_path()
        self.test_results: List[TestResult] = []
        
    def _get_cursor_logs_path(self) -> Path:
        """Получить путь к логам Cursor в зависимости от ОС"""
        if self.system == "darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Cursor" / "logs"
        elif self.system == "windows":
            return Path(os.environ.get("APPDATA", "")) / "Cursor" / "logs"
        else:  # Linux
            return Path.home() / ".config" / "Cursor" / "logs"
    
    def test_cursor_logs_accessibility(self) -> TestResult:
        """Тест 1: Проверка доступности логов Cursor"""
        test_name = "Cursor Logs Accessibility"
        errors = []
        recommendations = []
        evidence: Dict[str, Any] = {}
        
        try:
            # Проверяем существование директории логов
            if not self.cursor_logs_path.exists():
                errors.append(LogError(
                    timestamp=datetime.now().isoformat(),
                    error_type="DirectoryNotFound",
                    error_message=f"Cursor logs directory not found: {self.cursor_logs_path}",
                    log_file="N/A",
                    line_number=0,
                    severity="critical"
                ))
                recommendations.append("Установите Cursor IDE или проверьте путь к логам")
                evidence["logs_directory"] = "NOT_FOUND"
            else:
                evidence["logs_directory"] = str(self.cursor_logs_path)
                
                # Проверяем доступность для чтения
                if not os.access(self.cursor_logs_path, os.R_OK):
                    errors.append(LogError(
                        timestamp=datetime.now().isoformat(),
                        error_type="PermissionDenied",
                        error_message=f"No read access to logs directory: {self.cursor_logs_path}",
                        log_file="N/A",
                        line_number=0,
                        severity="high"
                    ))
                    recommendations.append("Предоставьте права на чтение директории логов")
                    evidence["permissions"] = "DENIED"
                else:
                    evidence["permissions"] = "GRANTED"
                    
                    # Подсчитываем количество лог-файлов
                    log_files = list(self.cursor_logs_path.rglob("*.log"))
                    evidence["log_files_count"] = str(len(log_files))
                    
                    if len(log_files) == 0:
                        errors.append(LogError(
                            timestamp=datetime.now().isoformat(),
                            error_type="NoLogFiles",
                            error_message="No log files found in Cursor logs directory",
                            log_file="N/A",
                            line_number=0,
                            severity="medium"
                        ))
                        recommendations.append("Запустите Cursor IDE для создания лог-файлов")
            
            status = "passed" if len(errors) == 0 else "failed"
            
        except Exception as e:
            errors.append(LogError(
                timestamp=datetime.now().isoformat(),
                error_type="Exception",
                error_message=f"Unexpected error: {str(e)}",
                log_file="N/A",
                line_number=0,
                severity="critical"
            ))
            recommendations.append("Проверьте системные права и доступность файловой системы")
            evidence["exception"] = str(e)
            status = "failed"
        
        return TestResult(
            test_name=test_name,
            status=status,
            errors_found=errors,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def test_mcp_servers_logs(self) -> TestResult:
        """Тест 2: Анализ логов MCP серверов"""
        test_name = "MCP Servers Logs Analysis"
        errors = []
        recommendations = []
        evidence: Dict[str, Any] = {}
        
        try:
            # Ищем логи MCP серверов
            mcp_log_files = list(self.cursor_logs_path.rglob("*mcp*.log"))
            evidence["mcp_log_files"] = [str(f) for f in mcp_log_files]
            
            if len(mcp_log_files) == 0:
                errors.append(LogError(
                    timestamp=datetime.now().isoformat(),
                    error_type="NoMCPLogs",
                    error_message="No MCP log files found",
                    log_file="N/A",
                    line_number=0,
                    severity="medium"
                ))
                recommendations.append("Настройте MCP серверы в Cursor для создания логов")
            else:
                # Анализируем каждый MCP лог-файл
                for log_file in mcp_log_files:
                    self._analyze_mcp_log_file(log_file, errors, recommendations, evidence)
            
            status = "passed" if len(errors) == 0 else "warning" if any(e.severity in ["medium", "low"] for e in errors) else "failed"
            
        except Exception as e:
            errors.append(LogError(
                timestamp=datetime.now().isoformat(),
                error_type="Exception",
                error_message=f"Error analyzing MCP logs: {str(e)}",
                log_file="N/A",
                line_number=0,
                severity="critical"
            ))
            recommendations.append("Проверьте доступность лог-файлов и права доступа")
            evidence["exception"] = str(e)
            status = "failed"
        
        return TestResult(
            test_name=test_name,
            status=status,
            errors_found=errors,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def _analyze_mcp_log_file(self, log_file: Path, errors: List[LogError], 
                             recommendations: List[str], evidence: Dict[str, Any]):
        """Анализ конкретного MCP лог-файла"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            evidence[f"log_file_{log_file.name}_lines"] = str(len(lines))
            
            # Ищем типичные ошибки MCP серверов
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # JSON-RPC ошибки
                if "Unexpected token" in line:
                    errors.append(LogError(
                        timestamp=datetime.now().isoformat(),
                        error_type="JSONRPCError",
                        error_message=f"JSON-RPC parsing error: {line[:100]}...",
                        log_file=str(log_file),
                        line_number=line_num,
                        severity="high"
                    ))
                    recommendations.append("Исправьте credentials_wrapper.py - перенаправьте логи в stderr")
                
                # MCP сервер ошибки
                elif "Client error for command" in line:
                    errors.append(LogError(
                        timestamp=datetime.now().isoformat(),
                        error_type="MCPClientError",
                        error_message=f"MCP client error: {line[:100]}...",
                        log_file=str(log_file),
                        line_number=line_num,
                        severity="high"
                    ))
                    recommendations.append("Проверьте MCP сервер на соответствие протоколу")
                
                # Ошибки запуска
                elif "spawn" in line and "ENOENT" in line:
                    errors.append(LogError(
                        timestamp=datetime.now().isoformat(),
                        error_type="SpawnError",
                        error_message=f"Process spawn error: {line[:100]}...",
                        log_file=str(log_file),
                        line_number=line_num,
                        severity="critical"
                    ))
                    recommendations.append("Используйте абсолютные пути в mcp.json конфигурации")
                
                # Эмодзи в stdout (признак неправильного вывода)
                elif any(emoji in line for emoji in ["🔐", "✅", "🚀", "🔧", "📊"]):
                    if "stdout" in line.lower() or "print" in line.lower():
                        errors.append(LogError(
                            timestamp=datetime.now().isoformat(),
                            error_type="EmojiInStdout",
                            error_message=f"Emoji detected in stdout: {line[:100]}...",
                            log_file=str(log_file),
                            line_number=line_num,
                            severity="medium"
                        ))
                        recommendations.append("Перенаправьте вывод с эмодзи в stderr")
        
        except Exception as e:
            errors.append(LogError(
                timestamp=datetime.now().isoformat(),
                error_type="FileReadError",
                error_message=f"Cannot read log file {log_file}: {str(e)}",
                log_file=str(log_file),
                line_number=0,
                severity="medium"
            ))
    
    def test_output_panel_simulation(self) -> TestResult:
        """Тест 3: Симуляция проверки Output панели"""
        test_name = "Output Panel Simulation"
        errors = []
        recommendations = []
        evidence: Dict[str, Any] = {}
        
        try:
            # Симулируем проверку Output панели через анализ логов
            output_channels = ["MCP", "Extension Host", "Language Server Protocol", "Terminal"]
            evidence["available_channels"] = output_channels
            
            # Проверяем наличие MCP каналов в логах
            mcp_channels_found = 0
            for log_file in self.cursor_logs_path.rglob("*.log"):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "MCP" in content:
                            mcp_channels_found += 1
                except:
                    continue
            
            evidence["mcp_channels_found"] = str(mcp_channels_found)
            
            if mcp_channels_found == 0:
                errors.append(LogError(
                    timestamp=datetime.now().isoformat(),
                    error_type="NoMCPChannels",
                    error_message="No MCP channels found in Output panel logs",
                    log_file="N/A",
                    line_number=0,
                    severity="medium"
                ))
                recommendations.append("Настройте MCP серверы для появления в Output панели")
            
            status = "passed" if len(errors) == 0 else "warning"
            
        except Exception as e:
            errors.append(LogError(
                timestamp=datetime.now().isoformat(),
                error_type="Exception",
                error_message=f"Error simulating Output panel check: {str(e)}",
                log_file="N/A",
                line_number=0,
                severity="critical"
            ))
            recommendations.append("Проверьте доступность лог-файлов")
            evidence["exception"] = str(e)
            status = "failed"
        
        return TestResult(
            test_name=test_name,
            status=status,
            errors_found=errors,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def test_credentials_wrapper_output(self) -> TestResult:
        """Тест 4: Проверка вывода credentials_wrapper.py"""
        test_name = "Credentials Wrapper Output Check"
        errors = []
        recommendations = []
        evidence: Dict[str, Any] = {}
        
        try:
            # Проверяем файл credentials_wrapper.py
            credentials_wrapper_path = Path("shared/credentials_wrapper.py")
            if not credentials_wrapper_path.exists():
                errors.append(LogError(
                    timestamp=datetime.now().isoformat(),
                    error_type="FileNotFound",
                    error_message=f"credentials_wrapper.py not found: {credentials_wrapper_path}",
                    log_file="N/A",
                    line_number=0,
                    severity="high"
                ))
                recommendations.append("Создайте файл credentials_wrapper.py")
                evidence["credentials_wrapper"] = "NOT_FOUND"
            else:
                with open(credentials_wrapper_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                evidence["credentials_wrapper"] = "FOUND"
                evidence["file_size"] = str(len(content))
                
                # Проверяем на использование stdout вместо stderr
                if "print(" in content and "file=sys.stderr" not in content:
                    errors.append(LogError(
                        timestamp=datetime.now().isoformat(),
                        error_type="StdoutUsage",
                        error_message="credentials_wrapper.py uses stdout instead of stderr",
                        log_file=str(credentials_wrapper_path),
                        line_number=0,
                        severity="high"
                    ))
                    recommendations.append("Измените все print() на print(..., file=sys.stderr)")
                
                # Проверяем на эмодзи в коде
                emojis = ["🔐", "✅", "🚀", "🔧", "📊"]
                for emoji in emojis:
                    if emoji in content:
                        errors.append(LogError(
                            timestamp=datetime.now().isoformat(),
                            error_type="EmojiInCode",
                            error_message=f"Emoji {emoji} found in credentials_wrapper.py",
                            log_file=str(credentials_wrapper_path),
                            line_number=0,
                            severity="medium"
                        ))
                        recommendations.append("Убедитесь, что эмодзи выводятся в stderr")
            
            status = "passed" if len(errors) == 0 else "failed"
            
        except Exception as e:
            errors.append(LogError(
                timestamp=datetime.now().isoformat(),
                error_type="Exception",
                error_message=f"Error checking credentials_wrapper.py: {str(e)}",
                log_file="N/A",
                line_number=0,
                severity="critical"
            ))
            recommendations.append("Проверьте доступность файла credentials_wrapper.py")
            evidence["exception"] = str(e)
            status = "failed"
        
        return TestResult(
            test_name=test_name,
            status=status,
            errors_found=errors,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов мониторинга логов"""
        print("🔍 Starting MCP Logs Monitoring Tests...")
        print(f"📁 Cursor logs path: {self.cursor_logs_path}")
        print(f"💻 System: {self.system}")
        print()
        
        # Запускаем все тесты
        tests = [
            self.test_cursor_logs_accessibility,
            self.test_mcp_servers_logs,
            self.test_output_panel_simulation,
            self.test_credentials_wrapper_output
        ]
        
        for test_func in tests:
            print(f"🧪 Running {test_func.__name__}...")
            result = test_func()
            self.test_results.append(result)
            
            # Выводим результат теста
            status_emoji = {"passed": "✅", "warning": "⚠️", "failed": "❌"}
            print(f"   {status_emoji.get(result.status, '❓')} {result.test_name}: {result.status}")
            
            if result.errors_found:
                print(f"   📊 Errors found: {len(result.errors_found)}")
                for error in result.errors_found[:3]:  # Показываем первые 3 ошибки
                    print(f"      - {error.error_type}: {error.error_message[:80]}...")
                if len(result.errors_found) > 3:
                    print(f"      ... and {len(result.errors_found) - 3} more errors")
            
            print()
        
        # Генерируем итоговый отчет
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Генерация итогового отчета"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        warning_tests = len([r for r in self.test_results if r.status == "warning"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        
        total_errors = sum(len(r.errors_found) for r in self.test_results)
        critical_errors = sum(len([e for e in r.errors_found if e.severity == "critical"]) for r in self.test_results)
        high_errors = sum(len([e for e in r.errors_found if e.severity == "high"]) for r in self.test_results)
        
        # Собираем все рекомендации
        all_recommendations = []
        for result in self.test_results:
            all_recommendations.extend(result.recommendations)
        
        # Убираем дубликаты
        unique_recommendations = list(set(all_recommendations))
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "warnings": warning_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
            },
            "errors": {
                "total": total_errors,
                "critical": critical_errors,
                "high": high_errors,
                "medium": sum(len([e for e in r.errors_found if e.severity == "medium"]) for r in self.test_results),
                "low": sum(len([e for e in r.errors_found if e.severity == "low"]) for r in self.test_results)
            },
            "recommendations": unique_recommendations,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "errors_count": len(r.errors_found),
                    "evidence": r.evidence
                }
                for r in self.test_results
            ],
            "cursor_logs_path": str(self.cursor_logs_path),
            "system": self.system
        }
        
        return report

def main():
    """Главная функция для запуска тестов"""
    monitor = MCPLogsMonitor()
    report = monitor.run_all_tests()
    
    # Выводим итоговый отчет
    print("📊 MCP Logs Monitoring Test Report")
    print("=" * 50)
    print(f"📅 Timestamp: {report['timestamp']}")
    print(f"💻 System: {report['system']}")
    print(f"📁 Cursor logs: {report['cursor_logs_path']}")
    print()
    
    print("📈 Test Summary:")
    print(f"   Total tests: {report['summary']['total_tests']}")
    print(f"   ✅ Passed: {report['summary']['passed']}")
    print(f"   ⚠️  Warnings: {report['summary']['warnings']}")
    print(f"   ❌ Failed: {report['summary']['failed']}")
    print(f"   📊 Success rate: {report['summary']['success_rate']}")
    print()
    
    print("🚨 Error Summary:")
    print(f"   Total errors: {report['errors']['total']}")
    print(f"   🔴 Critical: {report['errors']['critical']}")
    print(f"   🟠 High: {report['errors']['high']}")
    print(f"   🟡 Medium: {report['errors']['medium']}")
    print(f"   🟢 Low: {report['errors']['low']}")
    print()
    
    if report['recommendations']:
        print("💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
        print()
    
    # Сохраняем отчет в файл
    report_file = Path("mcp_logs_monitoring_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Detailed report saved to: {report_file}")
    
    # Возвращаем код выхода в зависимости от результатов
    if report['errors']['critical'] > 0 or report['summary']['failed'] > 0:
        print("❌ Tests failed with critical errors")
        return 1
    elif report['errors']['high'] > 0 or report['summary']['warnings'] > 0:
        print("⚠️  Tests completed with warnings")
        return 2
    else:
        print("✅ All tests passed")
        return 0

if __name__ == "__main__":
    sys.exit(main())
