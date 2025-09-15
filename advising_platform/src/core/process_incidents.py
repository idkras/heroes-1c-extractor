"""
JTBD:
Я (разработчик) хочу использовать функциональность модуля process_incidents, чтобы эффективно решать задачи, связанные с этой частью системы.
"""

import sys
import os

print("Перенаправление на advising_platform/scripts/incidents/process_incidents.py...")

# Добавляем путь к директории проекта в sys.path
sys.path.insert(0, os.path.abspath("."))

# Импортируем и запускаем модуль
from advising_platform.scripts.incidents.process_incidents import process_incidents

if __name__ == "__main__":
    process_incidents.main()
