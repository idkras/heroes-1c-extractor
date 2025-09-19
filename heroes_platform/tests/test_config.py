"""Configuration tests for the project."""

import os

import pytest


def test_pyproject_toml_structure():
    """Test that pyproject.toml has correct structure."""
    try:
        with open("pyproject.toml") as f:
            content = f.read()

        # Check required sections
        assert "[project]" in content
        assert "[build-system]" in content
        assert "[tool." in content

        # Check project metadata
        assert (
            'name = "heroes-platform"' in content
            or 'name = "heroes_platform"' in content
        )
        assert 'version = "1.0.0"' in content
        assert "description" in content

        # Check dependencies
        assert "pydantic" in content

    except FileNotFoundError:
        pytest.fail("pyproject.toml not found")
    except Exception as e:
        pytest.fail(f"Error reading pyproject.toml: {e}")


def test_gitignore_structure():
    """Test that .gitignore excludes necessary files."""
    try:
        with open(".gitignore") as f:
            content = f.read()

        # Check for critical exclusions
        required_exclusions = [".venv", "__pycache__", ".DS_Store", "*.py[cod]"]

        for exclusion in required_exclusions:
            assert exclusion in content, f"Missing exclusion: {exclusion}"

    except FileNotFoundError:
        pytest.fail(".gitignore not found")


def test_required_directories():
    """Test that required directories exist."""
    required_dirs = ["tests", "heroes_mcp", "src"]

    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Required directory {dir_path} not found"


def test_mcp_server_structure():
    """Test that MCP server has correct structure."""
    mcp_server_path = "heroes_mcp"

    if os.path.exists(mcp_server_path):
        required_mcp_files = ["src/heroes_mcp_server.py", "README.md"]

        for file_path in required_mcp_files:
            full_path = os.path.join(mcp_server_path, file_path)
            assert os.path.exists(full_path), f"MCP server file {file_path} not found"
    else:
        pytest.skip("MCP server directory not found")


if __name__ == "__main__":
    pytest.main([__file__])
