#!/usr/bin/env python3
"""
Анализ логов выполнения команд

JTBD: Как аналитик, я хочу анализировать логи выполнения команд,
чтобы понять, какие команды часто падают и почему.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class CommandLogAnalyzer:
    """Анализатор логов выполнения команд"""

    def __init__(self, log_dir: str = "logs/command_execution"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def analyze_recent_executions(self, days: int = 7) -> dict[str, Any]:
        """Анализирует недавние выполнения команд"""
        results = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "command_frequency": {},
            "error_patterns": {},
            "execution_times": [],
            "recent_errors": [],
        }

        # Анализируем логи за последние N дней
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_file = (
                self.log_dir / f"command_execution_{date.strftime('%Y%m%d')}.jsonl"
            )

            if log_file.exists():
                self._analyze_log_file(log_file, results)

        # Вычисляем статистику
        total_executions = results.get("total_executions", 0)
        if isinstance(total_executions, (int, float)) and total_executions > 0:
            successful_executions = results.get("successful_executions", 0)
            failed_executions = results.get("failed_executions", 0)
            if isinstance(successful_executions, (int, float)) and isinstance(
                failed_executions, (int, float)
            ):
                results["success_rate"] = successful_executions / total_executions * 100
                results["failure_rate"] = failed_executions / total_executions * 100

        return results

    def _analyze_log_file(self, log_file: Path, results: dict[str, Any]) -> None:
        """Анализирует один лог файл"""
        try:
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        self._process_log_entry(entry, results)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")

    def _process_log_entry(
        self, entry: dict[str, Any], results: dict[str, Any]
    ) -> None:
        """Обрабатывает одну запись лога"""
        results["total_executions"] += 1

        status = entry.get("status", "UNKNOWN")
        if status == "COMPLETED":
            results["successful_executions"] += 1
        elif status == "FAILED":
            results["failed_executions"] += 1

        # Анализируем данные
        data = entry.get("data", {})

        # Частота команд
        if "artifact_path" in data:
            artifact_path = data["artifact_path"]
            if artifact_path:
                results["command_frequency"][artifact_path] = (
                    results["command_frequency"].get(artifact_path, 0) + 1
                )

        # Время выполнения
        if "execution_time" in data:
            results["execution_times"].append(data["execution_time"])

        # Ошибки
        if status == "FAILED" and "error" in data:
            error = data["error"]
            results["error_patterns"][error] = (
                results["error_patterns"].get(error, 0) + 1
            )
            results["recent_errors"].append(
                {
                    "timestamp": entry.get("timestamp"),
                    "error": error,
                    "execution_id": entry.get("execution_id"),
                }
            )

    def generate_report(self, days: int = 7) -> str:
        """Генерирует отчет об анализе"""
        analysis = self.analyze_recent_executions(days)

        report = f"""
# 📊 Отчет по выполнению команд

**Период**: последние {days} дней
**Дата генерации**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📈 Общая статистика

- **Всего выполнений**: {analysis["total_executions"]}
- **Успешных**: {analysis["successful_executions"]} ({analysis.get("success_rate", 0):.1f}%)
- **Неудачных**: {analysis["failed_executions"]} ({analysis.get("failure_rate", 0):.1f}%)

## 🔥 Самые частые команды

"""

        # Топ-5 команд
        sorted_commands = sorted(
            analysis["command_frequency"].items(), key=lambda x: x[1], reverse=True
        )
        for i, (command, count) in enumerate(sorted_commands[:5], 1):
            report += f"{i}. `{command}` - {count} раз\n"

        report += "\n## ❌ Паттерны ошибок\n\n"

        # Топ-5 ошибок
        sorted_errors = sorted(
            analysis["error_patterns"].items(), key=lambda x: x[1], reverse=True
        )
        for i, (error, count) in enumerate(sorted_errors[:5], 1):
            report += f"{i}. `{error}` - {count} раз\n"

        if analysis["execution_times"]:
            avg_time = sum(analysis["execution_times"]) / len(
                analysis["execution_times"]
            )
            max_time = max(analysis["execution_times"])
            min_time = min(analysis["execution_times"])

            report += "\n## ⏱️ Время выполнения\n\n"
            report += f"- **Среднее время**: {avg_time:.2f} сек\n"
            report += f"- **Максимальное время**: {max_time:.2f} сек\n"
            report += f"- **Минимальное время**: {min_time:.2f} сек\n"

        if analysis["recent_errors"]:
            report += "\n## 🚨 Последние ошибки\n\n"
            for error in analysis["recent_errors"][-5:]:  # Последние 5 ошибок
                report += f"- **{error['timestamp']}**: `{error['error']}`\n"

        return report


def main():
    """Основная функция"""
    analyzer = CommandLogAnalyzer()

    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    else:
        days = 7

    report = analyzer.generate_report(days)
    print(report)

    # Сохраняем отчет
    report_file = (
        Path("logs/command_execution")
        / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 Отчет сохранен: {report_file}")


if __name__ == "__main__":
    main()
