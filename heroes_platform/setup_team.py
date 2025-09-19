#!/usr/bin/env python3
"""
Heroes Platform Team Setup Script
Автоматическая настройка проекта для команды Heroes
"""

import json
import platform
import subprocess
import sys
from pathlib import Path


def print_status(message, status="INFO"):
    """Печать статусных сообщений"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m",
    }
    print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")


def check_python():
    """Проверить версию Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_status("Python 3.11+ required", "ERROR")
        return False
    print_status(
        f"Python {version.major}.{version.minor}.{version.micro} found", "SUCCESS"
    )
    return True


def check_node():
    """Проверить наличие Node.js"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_status(f"Node.js {version} found", "SUCCESS")
            return True
    except:
        pass

    print_status("Node.js not found. Please install Node.js 14+", "ERROR")
    return False


def setup_virtual_environment():
    """Создать и настроить виртуальное окружение"""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / ".venv"

    if not venv_path.exists():
        print_status("Creating virtual environment...", "INFO")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print_status("Virtual environment created", "SUCCESS")
        except subprocess.CalledProcessError:
            print_status("Failed to create virtual environment", "ERROR")
            return False
    else:
        print_status("Virtual environment already exists", "WARNING")

    return True


def install_python_dependencies():
    """Установить Python зависимости"""
    print_status("Installing Python dependencies...", "INFO")
    try:
        # Активируем виртуальное окружение
        project_root = Path(__file__).parent.parent
        venv_python = project_root / ".venv" / "bin" / "python"

        if platform.system() == "Windows":
            venv_python = project_root / ".venv" / "Scripts" / "python.exe"

        # Устанавливаем зависимости
        subprocess.run([str(venv_python), "setup.py"], check=True)
        print_status("Python dependencies installed", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install Python dependencies: {e}", "ERROR")
        return False


def install_node_dependencies():
    """Установить Node.js зависимости"""
    print_status("Installing Node.js dependencies...", "INFO")
    try:
        heroes_platform_path = Path(__file__).parent

        # Устанавливаем figma-developer-mcp
        subprocess.run(
            ["npm", "install", "figma-developer-mcp"],
            cwd=str(heroes_platform_path),
            check=True,
        )
        print_status("Node.js dependencies installed", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install Node.js dependencies: {e}", "ERROR")
        return False


def setup_cursor_config():
    """Настроить конфигурацию Cursor"""
    print_status("Setting up Cursor configuration...", "INFO")

    # Путь к конфигурации Cursor
    cursor_config_path = Path.home() / ".cursor" / "mcp.json"

    if not cursor_config_path.exists():
        print_status(
            "Cursor MCP config not found. Please create it manually.", "WARNING"
        )
        return False

    try:
        # Читаем текущую конфигурацию
        with open(cursor_config_path) as f:
            config = json.load(f)

        # Обновляем figma-mcp конфигурацию
        if "mcpServers" in config and "figma-mcp" in config["mcpServers"]:
            config["mcpServers"]["figma-mcp"] = {
                "command": "python3",
                "args": ["${workspaceFolder}/heroes-platform/run_figma_mcp.py"],
                "env": {"PYTHONPATH": "${workspaceFolder}/heroes-platform"},
            }

            # Сохраняем обновленную конфигурацию
            with open(cursor_config_path, "w") as f:
                json.dump(config, f, indent=2)

            print_status("Cursor configuration updated", "SUCCESS")
            return True
        else:
            print_status("figma-mcp not found in Cursor config", "WARNING")
            return False

    except Exception as e:
        print_status(f"Failed to update Cursor config: {e}", "ERROR")
        return False


def test_figma_mcp():
    """Протестировать Figma MCP сервер"""
    print_status("Testing Figma MCP server...", "INFO")

    try:
        heroes_platform_path = Path(__file__).parent
        test_script = heroes_platform_path / "run_figma_mcp.py"

        # Простой тест запуска
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=str(heroes_platform_path),
            input='{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}\n',
            capture_output=True,
            text=True,
            timeout=10,
        )

        if "get_figma_data" in result.stdout:
            print_status("Figma MCP server test passed", "SUCCESS")
            return True
        else:
            print_status("Figma MCP server test failed", "ERROR")
            return False

    except Exception as e:
        print_status(f"Figma MCP server test failed: {e}", "ERROR")
        return False


def main():
    """Основная функция установки"""
    print_status("🚀 Heroes Platform Team Setup", "INFO")
    print_status("=" * 50, "INFO")

    # Проверяем предварительные требования
    if not check_python():
        sys.exit(1)

    if not check_node():
        sys.exit(1)

    # Настраиваем окружение
    if not setup_virtual_environment():
        sys.exit(1)

    if not install_python_dependencies():
        sys.exit(1)

    if not install_node_dependencies():
        sys.exit(1)

    # Настраиваем Cursor
    setup_cursor_config()

    # Тестируем
    test_figma_mcp()

    print_status("🎉 Setup completed successfully!", "SUCCESS")
    print_status("", "INFO")
    print_status("Next steps:", "INFO")
    print_status("1. Restart Cursor IDE", "INFO")
    print_status("2. Check MCP panel for figma-mcp server", "INFO")
    print_status("3. Test figma tools in Cursor chat", "INFO")


if __name__ == "__main__":
    main()
