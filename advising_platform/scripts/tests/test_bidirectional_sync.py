#!/usr/bin/env python3
"""
Файл-переадресация для совместимости с существующими скриптами.
Основная реализация перемещена в advising_platform/scripts/tests/test_bidirectional_sync.py
"""

import os
import sys
import subprocess

# Запускаем модуль напрямую через subprocess, чтобы избежать проблем с импортом
target_path = os.path.join('advising_platform', 'scripts', 'tests', 'test_bidirectional_sync.py')

if os.path.exists(target_path):
    print(f"Перенаправление на {target_path}...")
    result = subprocess.run([sys.executable, target_path] + sys.argv[1:])
    sys.exit(result.returncode)
else:
    print(f"Ошибка: файл {target_path} не найден.")
    print("Убедитесь, что вы находитесь в корневой директории проекта.")
    sys.exit(1)
