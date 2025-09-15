#!/bin/bash
# Скрипт для архивации завершенных задач

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

echo "Запуск архивации завершенных задач..."
python -m advising_platform.src.tools.task.archive_completed_tasks
echo "Архивация завершена"