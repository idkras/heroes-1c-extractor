#!/usr/bin/env python3

"""
Скрипт автоматизации тест-кейсов для 1С данных
Запускает все тест-кейсы и генерирует отчеты
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class TestCaseRunner:
    """Класс для запуска тест-кейсов"""

    def __init__(self):
        self.results_dir = Path("data/results")
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def run_validation_tests(self):
        """Запуск валидационных тестов"""
        print("🧪 Запуск валидационных тестов...")

        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/validation/",
                    "-v",
                    "--cov=src",
                    "--cov-report=html",
                    "--cov-report=json",
                    "--junitxml=reports/validation-results.xml",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            end_time = time.time()
            execution_time = end_time - start_time

            return {
                "success": result.returncode == 0,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "success": False,
                "execution_time": 0,
                "stdout": "",
                "stderr": str(e),
            }

    def run_testcases(self):
        """Запуск автоматизированных тест-кейсов"""
        print("📋 Запуск автоматизированных тест-кейсов...")

        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/testcases/",
                    "-v",
                    "--cov=src",
                    "--junitxml=reports/testcases-results.xml",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            end_time = time.time()
            execution_time = end_time - start_time

            return {
                "success": result.returncode == 0,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "success": False,
                "execution_time": 0,
                "stdout": "",
                "stderr": str(e),
            }

    def run_playwright_tests(self):
        """Запуск Playwright тестов"""
        print("🎭 Запуск Playwright тестов...")

        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "npx",
                    "playwright",
                    "test",
                    "tests/playwright/",
                    "--reporter=html,json,junit",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            end_time = time.time()
            execution_time = end_time - start_time

            return {
                "success": result.returncode == 0,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "success": False,
                "execution_time": 0,
                "stdout": "",
                "stderr": str(e),
            }

    def generate_report(self, results):
        """Генерация итогового отчета"""
        print("📊 Генерация итогового отчета...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "total_execution_time": 0,
            },
            "test_suites": {
                "validation_tests": results["validation"],
                "testcases": results["testcases"],
                "playwright_tests": results["playwright"],
            },
            "recommendations": [],
        }

        # Подсчет результатов
        for suite_name, suite_result in results.items():
            if suite_result["success"]:
                report["summary"]["passed_tests"] += 1
            else:
                report["summary"]["failed_tests"] += 1
                report["recommendations"].append(f"Исправить ошибки в {suite_name}")

            report["summary"]["total_execution_time"] += suite_result["execution_time"]

        report["summary"]["total_tests"] = len(results)

        # Сохранение отчета
        report_file = (
            self.reports_dir
            / f"testcase_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ Отчет сохранен: {report_file}")
        return report

    def print_summary(self, report):
        """Вывод итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТ-КЕЙСОВ")
        print("=" * 60)

        print(f"🕐 Время выполнения: {report['summary']['total_execution_time']:.2f}с")
        print(f"✅ Успешных тестов: {report['summary']['passed_tests']}")
        print(f"❌ Неудачных тестов: {report['summary']['failed_tests']}")

        print("\n📋 ДЕТАЛИ ПО ТЕСТ-СЬЮТАМ:")
        for suite_name, suite_result in report["test_suites"].items():
            status = "✅ ПРОЙДЕН" if suite_result["success"] else "❌ ПРОВАЛЕН"
            print(f"  - {suite_name}: {status} ({suite_result['execution_time']:.2f}с)")

        if report["recommendations"]:
            print("\n💡 РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"  {i}. {rec}")

        print("=" * 60)

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск всех тест-кейсов...")

        results = {}

        # Запуск валидационных тестов
        results["validation"] = self.run_validation_tests()

        # Запуск тест-кейсов
        results["testcases"] = self.run_testcases()

        # Запуск Playwright тестов
        results["playwright"] = self.run_playwright_tests()

        # Генерация отчета
        report = self.generate_report(results)

        # Вывод итогового отчета
        self.print_summary(report)

        return report


def main():
    """Основная функция"""
    runner = TestCaseRunner()

    # Проверяем наличие данных для тестирования
    if not runner.results_dir.exists():
        print(
            "❌ Папка с результатами не найдена. Запустите извлечение данных сначала.",
        )
        sys.exit(1)

    # Запускаем все тесты
    report = runner.run_all_tests()

    # Возвращаем код выхода
    if report["summary"]["failed_tests"] > 0:
        print("❌ Некоторые тесты провалились")
        sys.exit(1)
    else:
        print("✅ Все тесты прошли успешно")
        sys.exit(0)


if __name__ == "__main__":
    main()
