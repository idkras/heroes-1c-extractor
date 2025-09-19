#!/usr/bin/env python3
"""
Системный мониторинг логов MCP сервера
Автоматический анализ ошибок и интеграция с CI/CD
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class LogMonitor:
    """Системный мониторинг логов MCP сервера"""

    def __init__(self, log_file: Path) -> None:
        """Initialize log monitor with error patterns"""
        self.log_file = log_file
        self.last_position = 0
        self.error_patterns = {
            "workflow_not_available": "Workflow.*not available",
            "attribute_error": ".*object has no attribute.*",
            "import_error": "Import.*could not be resolved",
            "timeout_error": "timeout|hang|завис",
            "connection_error": "connection.*failed|refused",
        }
        self.critical_errors: list[Any] = []

    def monitor_logs(self) -> dict[str, Any]:
        """Мониторинг логов в реальном времени"""
        try:
            with open(self.log_file) as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()

            return self.analyze_new_logs(new_lines)
        except Exception as e:
            return {"error": f"Failed to monitor logs: {e}"}

    def analyze_new_logs(self, lines: list[str]) -> dict[str, Any]:
        """Анализ новых логов"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "new_entries": len(lines),
            "errors_found": 0,
            "critical_errors": [],
            "performance_issues": [],
            "recommendations": [],
        }

        for line in lines:
            try:
                log_entry = json.loads(line.strip())
                self.analyze_log_entry(log_entry, analysis)
            except json.JSONDecodeError:
                # Не JSON лог - проверяем на текстовые ошибки
                self.analyze_text_log(line, analysis)

        return analysis

    def analyze_log_entry(
        self, entry: dict[str, Any], analysis: dict[str, Any]
    ) -> None:
        """Анализ отдельной записи лога"""
        level = entry.get("level", "INFO")
        message = entry.get("message", "")

        # Проверка на критические ошибки
        if level == "ERROR":
            analysis["errors_found"] += 1
            error_info = {
                "timestamp": entry.get("timestamp"),
                "level": level,
                "message": message,
                "module": entry.get("module"),
                "function": entry.get("function"),
                "line": entry.get("line"),
            }
            analysis["critical_errors"].append(error_info)

            # Анализ типа ошибки
            if "Workflow.*not available" in message:
                analysis["recommendations"].append(
                    "Проверить инициализацию workflow файлов"
                )
            elif "object has no attribute" in message:
                analysis["recommendations"].append("Проверить методы workflow классов")
            elif "Import.*could not be resolved" in message:
                analysis["recommendations"].append("Проверить импорты и PYTHONPATH")

        # Проверка производительности
        if "execution_time" in entry:
            exec_time = entry.get("execution_time", 0)
            if exec_time > 5.0:  # Более 5 секунд
                analysis["performance_issues"].append(
                    {
                        "command": entry.get("command"),
                        "execution_time": exec_time,
                        "timestamp": entry.get("timestamp"),
                    }
                )

    def analyze_text_log(self, line: str, analysis: dict[str, Any]) -> None:
        """Анализ текстовых логов"""
        if any(pattern in line.lower() for pattern in ["error", "failed", "exception"]):
            analysis["errors_found"] += 1
            analysis["critical_errors"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": line.strip(),
                    "type": "text_log",
                }
            )

    def generate_report(self) -> dict[str, Any]:
        """Генерация отчета для CI/CD"""
        return {
            "monitor_status": "active",
            "last_check": datetime.now().isoformat(),
            "log_file": str(self.log_file),
            "file_size": self.log_file.stat().st_size if self.log_file.exists() else 0,
            "critical_errors_count": len(self.critical_errors),
            "recommendations": self.get_recommendations(),
        }

    def get_recommendations(self) -> list[str]:
        """Получение рекомендаций на основе анализа"""
        recommendations: list[str] = []

        if len(self.critical_errors) > 10:
            recommendations.append(
                "КРИТИЧНО: Слишком много ошибок - проверить стабильность сервера"
            )

        if any("workflow" in str(error) for error in self.critical_errors):
            recommendations.append("Проверить инициализацию workflow файлов")

        if any("import" in str(error) for error in self.critical_errors):
            recommendations.append("Проверить PYTHONPATH и импорты")

        return recommendations


def main() -> None:
    """Основная функция мониторинга"""
    log_file = Path("logs/mcp_server.log")

    if not log_file.exists():
        print("Лог файл не найден")
        sys.exit(1)

    monitor = LogMonitor(log_file)

    # Непрерывный мониторинг
    while True:
        try:
            analysis = monitor.monitor_logs()

            if analysis["errors_found"] > 0:
                print(f"🚨 НАЙДЕНЫ ОШИБКИ: {analysis['errors_found']}")
                for error in analysis["critical_errors"]:
                    print(f"  - {error['message']}")

                # Генерация отчета для CI/CD
                report = monitor.generate_report()
                with open("logs/monitoring_report.json", "w") as f:
                    json.dump(report, f, indent=2)

            time.sleep(5)  # Проверка каждые 5 секунд

        except KeyboardInterrupt:
            print("\nМониторинг остановлен")
            break
        except Exception as e:
            print(f"Ошибка мониторинга: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
