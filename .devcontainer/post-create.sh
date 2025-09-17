#!/bin/bash

# Post-create script for Heroes 1C Extractor devcontainer
set -e

echo "🚀 Setting up Heroes 1C Extractor development environment..."

# Update system packages
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install additional system dependencies
echo "🔧 Installing system dependencies..."
apt-get install -y \
    postgresql-client \
    curl \
    wget \
    git \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    wine \
    wine32 \
    wine64 \
    libwine \
    fonts-wine

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3.11 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install project dependencies
echo "📚 Installing project dependencies..."
if [ -f "pyproject.toml" ]; then
    echo "📦 Installing from pyproject.toml..."
    pip install -e ".[dev,mcp]"
else
    echo "⚠️ pyproject.toml not found, installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Install additional 1C-specific dependencies
echo "🔧 Installing 1C-specific dependencies..."
pip install \
    jupyterlab \
    notebook \
    ipykernel \
    pandas \
    pyarrow \
    duckdb \
    numpy \
    matplotlib \
    seaborn \
    plotly \
    openpyxl \
    xlsxwriter \
    lxml \
    beautifulsoup4 \
    requests \
    aiofiles

# Install Jupyter kernel
echo "🔗 Installing Jupyter kernel..."
python -m ipykernel install --user --name=heroes-1c-extractor --display-name="Heroes 1C Extractor (Python 3.11)"

# Set up Git (if not already configured)
echo "🔧 Setting up Git..."
git config --global --add safe.directory /workspaces/heroes-1c-extractor

# Create useful aliases
echo "⚡ Setting up useful aliases..."
cat >> ~/.bashrc << 'EOF'

# Heroes 1C Extractor aliases
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias venv='source .venv/bin/activate'
alias jupyter='jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root'
alias test='python -m pytest'
alias lint='python -m ruff check .'
alias format='python -m black .'
alias extract='python -m src.cli'

# Activate virtual environment by default
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

EOF

# Set up environment variables
echo "🌍 Setting up environment variables..."
cat >> ~/.bashrc << 'EOF'

# Heroes 1C Extractor environment variables
export PYTHONPATH="/workspaces/heroes-1c-extractor/src:/workspaces/heroes-1c-extractor/heroes_platform:/workspaces/heroes-1c-extractor:$PYTHONPATH"
export VIRTUAL_ENV="/workspaces/heroes-1c-extractor/.venv"
export PATH="/workspaces/heroes-1c-extractor/.venv/bin:$PATH"

# 1C-specific environment variables
export WINEARCH=win32
export WINEPREFIX=/home/vscode/.wine

EOF

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Heroes 1C Extractor Environment Variables
# Copy this file and customize for your needs

# Database
DATABASE_URL=postgresql://cocoindex:cocoindex@localhost:5432/cocoindex

# 1C Configuration
ONEC_DTOOLS_PATH=/workspaces/heroes-1c-extractor/tools/onec_dtools
TOOL1CD_PATH=/workspaces/heroes-1c-extractor/tools/tool1cd
WINE_PREFIX=/home/vscode/.wine

# API Keys (add your keys here)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Development
DEBUG=True
LOG_LEVEL=INFO

# MCP Configuration
MCP_CONFIG_PATH=.cursor/mcp.json
EOF
fi

# Set up Wine for 1C tools
echo "🍷 Setting up Wine for 1C tools..."
if [ ! -d "/home/vscode/.wine" ]; then
    echo "🍷 Initializing Wine..."
    winecfg
fi

# Set proper permissions
echo "🔐 Setting proper permissions..."
chmod +x .devcontainer/post-create.sh
chown -R vscode:vscode /workspaces/heroes-1c-extractor

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/raw data/exported data/results logs

echo "✅ Heroes 1C Extractor development environment setup complete!"
echo ""
echo "🎉 You can now:"
echo "  - Run 'jupyter' to start Jupyter Lab"
echo "  - Run 'test' to run tests"
echo "  - Run 'lint' to check code quality"
echo "  - Run 'format' to format code"
echo "  - Run 'extract' to use the 1C extractor CLI"
echo ""
echo "📊 Jupyter Lab will be available at: http://localhost:8888"
echo "🐍 Python virtual environment is activated automatically"
echo "🍷 Wine is configured for 1C tools"
echo "📁 Data directories created: data/raw, data/exported, data/results, logs"
