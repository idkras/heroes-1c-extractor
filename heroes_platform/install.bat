@echo off
REM Heroes Platform Auto-Install Script for Windows
REM Automatically installs all dependencies and sets up the environment

echo 🎯 Heroes Platform Auto-Install
echo ================================

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo [SUCCESS] Python found: 
python --version

REM Check if pip is installed
echo [INFO] Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found. Please install pip
    pause
    exit /b 1
)
echo [SUCCESS] pip found:
python -m pip --version

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Install dependencies using setup.py
echo [INFO] Installing dependencies from pyproject.toml...
if exist "setup.py" (
    python setup.py
) else (
    echo [ERROR] setup.py not found
    pause
    exit /b 1
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
for %%d in (logs output data config tests src) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo [SUCCESS] Created directory: %%d
    ) else (
        echo [WARNING] Directory already exists: %%d
    )
)

REM Copy configuration files
echo [INFO] Copying configuration files...
if exist "..\pyproject.toml" if not exist "pyproject.toml" (
    copy "..\pyproject.toml" "pyproject.toml"
    echo [SUCCESS] Copied pyproject.toml
)

if exist "..\.env" if not exist ".env" (
    copy "..\.env" ".env"
    echo [SUCCESS] Copied .env
)

REM Run tests to verify installation
echo [INFO] Running tests to verify installation...
if exist "run_tests.py" (
    python run_tests.py
    echo [SUCCESS] Tests completed
) else (
    echo [WARNING] run_tests.py not found, skipping tests
)

echo.
echo [SUCCESS] 🎉 Installation completed successfully!
echo.
echo Next steps:
echo 1. Activate virtual environment: .venv\Scripts\activate.bat
echo 2. Start MCP server: cd mcp_server ^&^& python run_mcp_server.py
echo 3. Run tests: python run_tests.py
echo.
echo For more information, see README.md
echo.
pause

