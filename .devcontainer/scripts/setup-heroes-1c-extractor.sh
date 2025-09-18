#!/bin/bash
set -e

echo "🚀 Setting up Heroes 1C Extractor in Dev Container..."

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate

# Установка зависимостей
if [ -f "pyproject.toml" ]; then
    echo "📦 Installing Python dependencies from pyproject.toml..."
    pip install -e ".[dev,mcp]"
elif [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

# Создание необходимых директорий
mkdir -p logs data/raw data/exported data/results config

# Настройка прав доступа
chmod +x .devcontainer/scripts/*.sh 2>/dev/null || true

# Setup 1C Tools
if [ -d "tools/onec_dtools" ]; then
    echo "🔧 Setting up 1C Tools..."
    echo "✅ onec_dtools directory found"
fi

if [ -d "tools/tool1cd" ]; then
    echo "🔧 Setting up Tool1CD..."
    echo "✅ tool1cd directory found"
fi

# Setup Wine for 1C tools
echo "🍷 Setting up Wine for 1C tools..."
if [ ! -d "/home/vscode/.wine" ]; then
    echo "🍷 Initializing Wine..."
    winecfg
fi

# Создание .cursorrules для Dev Container
cat > .cursorrules << 'EOF'
# Dev Container Rules for Heroes 1C Extractor

## Environment
- Working in Dev Container with Python 3.11
- All dependencies are pre-installed
- Wine is configured for 1C tools
- Use absolute paths within container: /workspace/

## Heroes 1C Extractor
- Main source: /workspace/src/
- 1C tools: /workspace/tools/
- Data: /workspace/data/
- Logs: /workspace/logs/
- Tests: /workspace/tests/

## Development
- Always activate virtual environment: source .venv/bin/activate
- Use container paths, not host paths
- 1C tools run in Wine environment
- All file operations use /workspace/ paths
- CLI available via: python -m src.cli
EOF

echo "✅ Heroes 1C Extractor setup completed!"

