#!/usr/bin/env python3
"""
Ruff Monitor - Автоматический мониторинг и исправление проблем качества кода
"""

import json
import logging
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RuffMonitor:
    def __init__(self, workspace_root: str = ".") -> Any:
        self.workspace_root = Path(workspace_root).resolve()

    def check_ruff_installed(self) -> bool:
        """Проверяет, установлен ли Ruff"""
        try:
            result = subprocess.run(  # nosec B607,B603
                ["ruff", "--version"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )
            if result.returncode == 0:
                logger.info(f"Ruff найден: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.error("Ruff не найден. Установите: pip install ruff")
            return False
        return False

    def get_problems(self) -> list[dict[str, Any]]:
        """Получает список проблем от Ruff"""
        try:
            result = subprocess.run(  # nosec B607,B603
                ["ruff", "check", ".", "--output-format", "json"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )

            if result.returncode == 0 and not result.stdout.strip():
                logger.info("Проблем не найдено!")
                return []

            problems = json.loads(result.stdout)
            logger.info(f"Найдено {len(problems)} проблем")
            return problems

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Ошибка при получении проблем: {e}")
            return []

    def apply_auto_fixes(self) -> bool:
        """Применяет автоматические исправления"""
        logger.info("Применяю автоматические исправления...")

        try:
            # Ruff check --fix
            result = subprocess.run(  # nosec B607,B603
                ["ruff", "check", ".", "--fix"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )

            if result.returncode == 0:
                logger.info("Авто-фиксы применены успешно")
            else:
                logger.warning(f"Ошибка при применении авто-фиксов: {result.stderr}")

            # Ruff format
            result = subprocess.run(  # nosec B607,B603
                ["ruff", "format", "."],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )

            if result.returncode == 0:
                logger.info("Форматирование применено успешно")
            else:
                logger.warning(f"Ошибка при форматировании: {result.stderr}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при применении исправлений: {e}")
            return False

    def run_monitoring_cycle(self) -> bool:
        """Выполняет один цикл мониторинга и исправления"""
        logger.info("=== Начинаю цикл мониторинга ===")

        # Получаем проблемы
        problems = self.get_problems()
        if not problems:
            logger.info("Проблем не найдено - цикл завершен")
            return True

        # Применяем авто-фиксы
        self.apply_auto_fixes()

        # Проверяем результат
        remaining_problems = self.get_problems()
        if remaining_problems:
            logger.info(
                f"Осталось {len(remaining_problems)} проблем для ручного исправления"
            )
            return False

        logger.info("Все проблемы исправлены!")
        return True


def main() -> Any:
    """Главная функция"""
    monitor = RuffMonitor()

    if not monitor.check_ruff_installed():
        sys.exit(1)

    monitor.run_monitoring_cycle()


if __name__ == "__main__":
    main()
