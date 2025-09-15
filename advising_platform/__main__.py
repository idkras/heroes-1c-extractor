#!/usr/bin/env python3
"""
Основной модуль платформы для запуска сервисов.
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def start_web_server():
    """Запускает веб-сервер"""
    try:
        from advising_platform.src.web.server import start_server
        start_server()
    except ImportError as e:
        print(f"Ошибка импорта веб-сервера: {e}")
        # Альтернативный запуск
        try:
            from advising_platform.src.web.simple_server import start_server
            start_server()
        except ImportError:
            print("Веб-сервер недоступен")
            sys.exit(1)

def start_api_server():
    """Запускает API-сервер"""
    try:
        from advising_platform.src.api.app import main
        main()
    except ImportError as e:
        print(f"Ошибка импорта API-сервера: {e}")
        sys.exit(1)

def start_mcp_server():
    """Запускает MCP-сервер"""
    try:
        from advising_platform.src.mcp.standards_mcp_server import main
        main()
    except ImportError as e:
        print(f"Ошибка импорта MCP-сервера: {e}")
        sys.exit(1)

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python -m advising_platform [web|api|mcp]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "web":
        start_web_server()
    elif command == "api":
        start_api_server()
    elif command == "mcp":
        start_mcp_server()
    else:
        print(f"Неизвестная команда: {command}")
        print("Доступные команды: web, api, mcp")
        sys.exit(1)

if __name__ == "__main__":
    main()