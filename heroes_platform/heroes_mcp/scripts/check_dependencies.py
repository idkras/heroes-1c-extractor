#!/usr/bin/env python3
"""
Dependency Checker for MCP Server
Diagnoses import and dependency issues
"""

import importlib
import sys
from pathlib import Path
from typing import Any


def check_python_version() -> Any:
    """Check Python version"""
    print(f"🐍 Python version: {sys.version}")
    print("✅ Python version OK")
    return True


def check_required_packages() -> Any:
    """Check required packages"""
    required_packages = ["mcp", "asyncio", "json", "logging", "pathlib", "typing"]

    missing_packages: list[Any] = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)

    return len(missing_packages) == 0


def check_file_structure() -> Any:
    """Check file structure"""
    base_path = Path(__file__).parent
    required_files = ["src/heroes_mcp.py", "requirements.txt", "pyproject.toml"]

    missing_files: list[Any] = []

    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)

    return len(missing_files) == 0


def main() -> Any:
    """Main diagnostic function"""
    print("🔍 MCP Server Dependency Checker")
    print("=" * 40)

    # Check Python version
    print("\n1. Python Version Check:")
    python_ok = check_python_version()

    # Check required packages
    print("\n2. Required Packages Check:")
    packages_ok = check_required_packages()

    # Check file structure
    print("\n3. File Structure Check:")
    files_ok = check_file_structure()

    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY:")
    print(f"Python: {'✅' if python_ok else '❌'}")
    print(f"Packages: {'✅' if packages_ok else '❌'}")
    print(f"Files: {'✅' if files_ok else '❌'}")

    if python_ok and packages_ok and files_ok:
        print("\n🎉 All checks passed! Server should be ready to run.")
        print("💡 Try: python3 run_server.py")
    else:
        print("\n⚠️  Some issues found. Please fix them before running the server.")
        if not packages_ok:
            print("💡 Install missing packages: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
