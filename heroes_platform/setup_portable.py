#!/usr/bin/env python3
"""
Heroes Platform - Portable Setup Script

Этот скрипт настраивает heroes-platform для отчуждаемости между проектами.
Создает .venv внутри heroes-platform/ и устанавливает все зависимости.

Использование:
    python3 setup_portable.py

После выполнения heroes-platform/ можно копировать в любой проект.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Выполнить команду с обработкой ошибок"""
    print(f"🔄 Выполняю: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        if check:
            sys.exit(1)
        return e

def check_python_version():
    """Проверить версию Python"""
    print("🐍 Проверяю версию Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Требуется Python 3.11+, текущая версия: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")

def setup_venv():
    """Создать и настроить .venv"""
    print("\n🔧 Настраиваю виртуальное окружение...")
    
    # Удалить старый .venv если существует
    venv_path = Path(".venv")
    if venv_path.exists():
        print("🗑️ Удаляю старый .venv...")
        shutil.rmtree(venv_path)
    
    # Создать новый .venv
    print("📦 Создаю новый .venv...")
    run_command([sys.executable, "-m", "venv", ".venv"])
    
    # Определить путь к pip в .venv
    if os.name == 'nt':  # Windows
        pip_path = ".venv/Scripts/pip"
        python_path = ".venv/Scripts/python"
    else:  # Unix/Linux/macOS
        pip_path = ".venv/bin/pip"
        python_path = ".venv/bin/python"
    
    # Обновить pip
    print("⬆️ Обновляю pip...")
    run_command([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    
    return python_path, pip_path

def install_dependencies(python_path, pip_path):
    """Установить зависимости"""
    print("\n📚 Устанавливаю зависимости...")
    
    # Установить зависимости heroes-mcp
    if Path("heroes-mcp/requirements.txt").exists():
        print("🔧 Устанавливаю зависимости heroes-mcp...")
        run_command([pip_path, "install", "-r", "heroes-mcp/requirements.txt"])
    
    # Установить зависимости pyproject.toml
    if Path("pyproject.toml").exists():
        print("🔧 Устанавливаю зависимости pyproject.toml...")
        run_command([pip_path, "install", "-e", ".[dev]"])

def test_installation(python_path):
    """Протестировать установку"""
    print("\n🧪 Тестирую установку...")
    
    # Тест heroes-mcp
    if Path("heroes-mcp/src/heroes-mcp.py").exists():
        print("🔧 Тестирую heroes-mcp...")
        result = run_command([python_path, "heroes-mcp/src/heroes-mcp.py", "--test"], check=False)
        if result.returncode == 0:
            print("✅ heroes-mcp работает корректно")
        else:
            print("⚠️ heroes-mcp имеет проблемы, но установка завершена")

def create_activation_script():
    """Создать скрипт активации"""
    print("\n📝 Создаю скрипт активации...")
    
    activation_script = """#!/bin/bash
# Heroes Platform - Activation Script
# Используйте: source activate.sh

echo "🚀 Активирую Heroes Platform..."

# Активировать .venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Виртуальное окружение активировано"
else
    echo "❌ .venv не найден. Запустите setup_portable.py"
    exit 1
fi

# Установить PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"
echo "✅ PYTHONPATH установлен: $(pwd)"

echo "🎉 Heroes Platform готов к работе!"
echo "💡 Доступные команды:"
echo "   python3 heroes-mcp/src/heroes-mcp.py --test"
echo "   python3 -m pytest tests/"
"""
    
    with open("activate.sh", "w") as f:
        f.write(activation_script)
    
    # Сделать исполняемым
    os.chmod("activate.sh", 0o755)
    print("✅ Скрипт активации создан: activate.sh")

def create_readme():
    """Создать README для отчуждаемости"""
    print("\n📖 Создаю README...")
    
    readme_content = """# Heroes Platform - Portable Setup

## 🚀 Быстрый старт

1. **Активировать окружение:**
   ```bash
   source activate.sh
   ```

2. **Протестировать heroes-mcp:**
   ```bash
   python3 heroes-mcp/src/heroes-mcp.py --test
   ```

3. **Запустить тесты:**
   ```bash
   python3 -m pytest tests/
   ```

## 📁 Структура проекта

```
heroes-platform/
├── .venv/                    # Виртуальное окружение
├── heroes-mcp/               # MCP серверы
├── telegram-mcp/             # Telegram MCP
├── playwright-mcp/           # Playwright MCP
├── n8n-mcp/                  # N8N MCP
├── pyproject.toml            # Конфигурация проекта
├── requirements.txt          # Зависимости
├── activate.sh               # Скрипт активации
└── README.md                 # Этот файл
```

## 🔧 Настройка в Cursor

Добавьте в `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "heroes-mcp": {
      "command": "python3",
      "args": [
        "${workspaceFolder}/heroes-platform/heroes-mcp/src/heroes-mcp.py"
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/heroes-platform"
      }
    }
  }
}
```

## 📦 Отчуждаемость

Этот проект полностью отчуждаем:
- ✅ Копируйте `heroes-platform/` в любой проект
- ✅ Запустите `source activate.sh`
- ✅ Все зависимости и модули загружаются автоматически

## 🆘 Устранение неполадок

### Проблема: "Module not found"
```bash
source activate.sh
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

### Проблема: "MCP server not found"
- Убедитесь, что Cursor IDE перезапущен
- Проверьте путь в `.cursor/mcp.json`
- Активируйте .venv: `source activate.sh`

### Проблема: "Dependencies missing"
```bash
source activate.sh
pip install -r heroes-mcp/requirements.txt
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте, что .venv активирован
2. Убедитесь, что PYTHONPATH установлен
3. Перезапустите Cursor IDE
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ README создан: README.md")

def main():
    """Основная функция"""
    print("🚀 Heroes Platform - Portable Setup")
    print("=" * 50)
    
    # Проверить, что мы в правильной директории
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml не найден. Запустите из директории heroes-platform/")
        sys.exit(1)
    
    # Проверить версию Python
    check_python_version()
    
    # Настроить .venv
    python_path, pip_path = setup_venv()
    
    # Установить зависимости
    install_dependencies(python_path, pip_path)
    
    # Протестировать установку
    test_installation(python_path)
    
    # Создать скрипт активации
    create_activation_script()
    
    # Создать README
    create_readme()
    
    print("\n🎉 Heroes Platform настроен для отчуждаемости!")
    print("\n📋 Следующие шаги:")
    print("1. source activate.sh")
    print("2. python3 heroes-mcp/src/heroes-mcp.py --test")
    print("3. Скопируйте heroes-platform/ в любой проект")
    print("\n✅ Готово! Проект полностью отчуждаем.")

if __name__ == "__main__":
    main()
