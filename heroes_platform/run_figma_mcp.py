#!/usr/bin/env python3
"""
Figma MCP Server Wrapper
Запускает figma-developer-mcp с правильными переменными окружения
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root():
    """Получить корневую директорию проекта"""
    return Path(__file__).parent.parent


def get_heroes_platform_path():
    """Получить путь к heroes-platform"""
    return Path(__file__).parent


def get_node_path():
    """Получить путь к Node.js"""
    # Попробуем найти Node.js в системном PATH
    try:
        result = subprocess.run(["which", "node"], capture_output=True, text=True)
        if result.returncode == 0:
            node_path = result.stdout.strip()
            # Получаем директорию Node.js
            return str(Path(node_path).parent)
    except:
        pass

    # Fallback на стандартные пути
    common_paths = [
        "/usr/local/bin",
        "/usr/bin",
        "/opt/homebrew/bin",
        "/usr/local/Cellar/node/24.7.0/bin",
    ]

    for path in common_paths:
        if Path(path).exists() and Path(path, "node").exists():
            return path

    return None


def get_figma_api_key():
    """Получить Figma API ключ через credentials_manager"""
    try:
        # Импортируем credentials_manager
        import sys

        from heroes_platform.shared.credentials_manager import get_credential

        # Получаем API ключ через credentials_manager
        api_key = get_credential("figma_api_key")
        if api_key:
            return api_key
    except Exception as e:
        print(
            f"ERROR: Error getting Figma API key from credentials_manager: {e}",
            file=sys.stderr,
        )

    return None


def main():
    """Основная функция запуска"""
    print("🎨 Starting Figma MCP Server...", file=sys.stderr)

    # Получаем пути
    heroes_platform_path = get_heroes_platform_path()
    node_path = get_node_path()

    if not node_path:
        print("ERROR: Node.js not found in system PATH", file=sys.stderr)
        sys.exit(1)

    # Проверяем наличие figma-developer-mcp
    figma_mcp_path = (
        heroes_platform_path / "node_modules" / ".bin" / "figma-developer-mcp"
    )
    if not figma_mcp_path.exists():
        print(
            f"ERROR: figma-developer-mcp not found at {figma_mcp_path}", file=sys.stderr
        )
        sys.exit(1)

    # Получаем API ключ
    api_key = get_figma_api_key()
    if not api_key:
        print("ERROR: Figma API key not found in keychain", file=sys.stderr)
        sys.exit(1)

    # Настраиваем переменные окружения
    env = os.environ.copy()
    env["FIGMA_API_KEY"] = api_key
    env["PATH"] = f"{node_path}:{env.get('PATH', '')}"

    # Запускаем figma-developer-mcp
    cmd = [str(figma_mcp_path), "--stdio"]

    print(f"RUNNING: {' '.join(cmd)}", file=sys.stderr)
    print(f"WORKDIR: {heroes_platform_path}", file=sys.stderr)
    print(f"API_KEY: {'*' * 8}{api_key[-4:]}", file=sys.stderr)

    try:
        # Запускаем процесс
        process = subprocess.Popen(
            cmd,
            cwd=str(heroes_platform_path),
            env=env,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        # Ждем завершения
        process.wait()
        sys.exit(process.returncode)

    except KeyboardInterrupt:
        print("\nSTOPPING: Stopping Figma MCP Server...", file=sys.stderr)
        process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Error running figma-developer-mcp: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
