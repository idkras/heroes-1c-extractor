#!/bin/bash
# Heroes Platform Dependencies Installer
# Автоматическая установка всех зависимостей

set -e

echo "🎯 Heroes Platform Dependencies Installer"
echo "=========================================="

# Проверяем что мы в виртуальном окружении
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated!"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"

# Обновляем pip
echo "📦 Updating pip..."
python -m pip install --upgrade pip

# Устанавливаем основные зависимости
echo "📦 Installing core dependencies..."
pip install --timeout 60 pydantic>=2.9.2 pytest>=8.3.5 hypothesis>=6.138.2 coverage>=7.10.3 numpy>=1.22.0 requests>=2.32.0 python-dotenv>=1.1.0 typing-extensions>=4.7.0 "mcp[cli]>=1.12.4"

# Устанавливаем системные зависимости
echo "📦 Installing system dependencies..."
pip install --timeout 60 psycopg2-binary>=2.9.0 playwright>=1.40.0

# Устанавливаем dev зависимости
echo "📦 Installing development dependencies..."
pip install --timeout 60 black>=25.1.0 ruff>=0.12.9 mypy>=1.17.1 bandit>=1.8.6 safety>=3.6.0 pre-commit>=4.3.0 pytest-asyncio>=1.0.0 pytest-cov>=6.2.0 pytest-html>=4.1.0 pytest-xdist>=3.8.0

# Устанавливаем production зависимости
echo "📦 Installing production dependencies..."
pip install --timeout 60 fastapi>=0.110.0 uvicorn>=0.30.0 sqlalchemy>=2.0.0 alembic>=1.16.0 redis>=5.0.0 celery>=5.3.0

# Устанавливаем браузеры для playwright
echo "🌐 Installing Playwright browsers..."
playwright install

echo ""
echo "🎉 All dependencies installed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Run tests: python run_tests.py"
echo "2. Start MCP server: cd mcp_server && python run_mcp_server.py"
echo "3. Check dependencies: python check_dependencies.py"
