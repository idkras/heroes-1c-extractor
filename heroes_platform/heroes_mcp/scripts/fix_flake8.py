#!/usr/bin/env python3
"""
Script to fix flake8 errors
"""

import os
import re


def fix_flake8_errors():
    """Fix common flake8 errors"""

    # Fix test file assertions
    test_file = "tests/unit/test_heroes_mcp.py"
    if os.path.exists(test_file):
        with open(test_file) as f:
            content = f.read()

        # Fix E712 comparisons
        content = re.sub(r"== True", "is True", content)
        content = re.sub(r"== False", "is False", content)

        # Fix W293 blank lines with whitespace
        content = re.sub(r"[ \t]+\n", "\n", content)

        with open(test_file, "w") as f:
            f.write(content)
        print(f"Fixed {test_file}")

    # Fix __init__.py files
    init_files = [
        "tests/ai_qa/__init__.py",
        "tests/e2e/__init__.py",
        "tests/integration/__init__.py",
        "tests/security/__init__.py",
        "tests/unit/__init__.py",
    ]

    for init_file in init_files:
        if os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""Test package."""\n')
            print(f"Fixed {init_file}")

    # Fix import issues in test files
    test_files = [
        "tests/integration/test_atomic_operations.py",
        "tests/integration/test_mcp_protocol.py",
        "tests/integration/test_mcp_protocol_compliance.py",
        "tests/integration/test_workflow_integration.py",
        "tests/performance/test_performance_optimization.py",
        "tests/security/test_security_validation.py",
        "tests/test_manual_cases.py",
    ]

    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file) as f:
                content = f.read()

            # Add missing imports
            if "from typing import" in content and "List" not in content:
                content = re.sub(
                    r"from typing import ([^,\n]+)",
                    r"from typing import \1, List, Dict",
                    content,
                )

            # Fix undefined names
            if "MCPServer" in content and "from heroes_mcp import" not in content:
                content = re.sub(
                    r"class TestWorkflowIntegration:",
                    r"from heroes_mcp import HeroesMCPServer as MCPServer\n\nclass TestWorkflowIntegration:",
                    content,
                )

            with open(test_file, "w") as f:
                f.write(content)
            print(f"Fixed {test_file}")

    print("Flake8 fixes completed!")


if __name__ == "__main__":
    fix_flake8_errors()
