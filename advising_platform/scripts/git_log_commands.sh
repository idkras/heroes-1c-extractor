#!/bin/bash

# Создаем директорию для логов, если она не существует
mkdir -p git_logs

# Сохраняем лог коммитов за последние 2 часа
git log --since="2 hours ago" > git_logs/recent_commits.log

# Сохраняем лог с измененными файлами
git log --since="2 hours ago" --name-status > git_logs/recent_changed_files.log

# Сохраняем подробный лог с изменениями (патчи)
git log --since="2 hours ago" -p > git_logs/recent_commits_with_diffs.log

echo "Логи Git сохранены в директории git_logs/"