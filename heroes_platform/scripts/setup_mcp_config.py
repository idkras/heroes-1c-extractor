#!/usr/bin/env python3
"""
Setup MCP Configuration Script

Автоматически создает локальную конфигурацию MCP для проекта.
"""

import json
from pathlib import Path


def setup_mcp_config():
    """Создать локальную конфигурацию MCP"""
    heroes_platform_path = Path(__file__).parent.parent.absolute()
    project_root = heroes_platform_path.parent
    cursor_dir = project_root / ".cursor"

    # Создаем директорию .cursor если не существует
    cursor_dir.mkdir(exist_ok=True)

    # Путь к конфигурации
    mcp_config_path = cursor_dir / "mcp.json"

    # Читаем пример конфигурации
    example_config_path = heroes_platform_path / ".cursor" / "mcp.json.example"

    if not example_config_path.exists():
        print(f"❌ Example config not found: {example_config_path}")
        return False

    try:
        with open(example_config_path) as f:
            config_content = f.read()

        # Заменяем плейсхолдеры на реальные пути
        config_content = config_content.replace(
            "{HEROES_PLATFORM_PATH}", str(heroes_platform_path)
        )

        # Парсим JSON
        config = json.loads(config_content)

        # Сохраняем конфигурацию
        with open(mcp_config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ MCP configuration created: {mcp_config_path}")
        print(f"✅ Heroes Platform path: {heroes_platform_path}")

        return True

    except Exception as e:
        print(f"❌ Error creating MCP config: {e}")
        return False


def main():
    print("🔧 Setting up MCP Configuration...")
    print("=" * 50)

    success = setup_mcp_config()

    if success:
        print("\n🎉 MCP configuration setup completed!")
        print("\n📋 Next steps:")
        print("1. Restart Cursor")
        print("2. Check MCP Tools settings")
        print("3. Test MCP commands")
    else:
        print("\n❌ Failed to setup MCP configuration")


if __name__ == "__main__":
    main()
