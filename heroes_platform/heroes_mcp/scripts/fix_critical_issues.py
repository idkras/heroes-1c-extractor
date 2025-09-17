#!/usr/bin/env python3
"""
Critical Issues Fix Script
Fixes the most critical linting issues that could cause runtime errors.
"""

import re
from pathlib import Path


def fix_whitespace_before_colon(file_path):
    """Fix E203: whitespace before ':'"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix whitespace before colon in type annotations
    content = re.sub(r"(\w+)\s+:\s+", r"\1: ", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_undefined_names(file_path):
    """Fix F821: undefined name errors"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Add missing imports for common undefined names
    if "List[" in content and "from typing import" in content and "List" not in content:
        content = re.sub(
            r"from typing import ([^,\n]+)", r"from typing import \1, List", content
        )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_import_order(file_path):
    """Fix E402: module level import not at top of file"""
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Find imports that are not at the top
    import_lines = []
    other_lines = []
    in_import_section = True

    for line in lines:
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            if in_import_section:
                import_lines.append(line)
            else:
                # Move import to top
                import_lines.append(line)
        else:
            if line.strip() and not line.strip().startswith("#"):
                in_import_section = False
            other_lines.append(line)

    # Reconstruct file with imports at top
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(import_lines)
        f.writelines(other_lines)


def fix_block_comments(file_path):
    """Fix E265: block comment should start with '# '"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix block comments
    content = re.sub(r"^#([^ ])", r"# \1", content, flags=re.MULTILINE)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main function to fix critical issues"""
    # src_dir = Path("src")  # Not used
    # tests_dir = Path("tests")  # Not used

    # Files with critical issues
    critical_files = [
        "tests/integration/test_atomic_operations.py",
        "tests/integration/test_mcp_protocol.py",
        "tests/integration/test_mcp_protocol_compliance.py",
        "tests/integration/test_reflection_checkpoints.py",
        "tests/integration/test_workflow_integration.py",
        "tests/performance/test_performance_optimization.py",
        "tests/security/test_security_validation.py",
        "tests/integration/abstract_links/test_abstract_links.py",
        "tests/test_manual_cases.py",
    ]

    print("🔧 Fixing critical linting issues...")

    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  Fixing {file_path}")
            try:
                fix_whitespace_before_colon(file_path)
                fix_undefined_names(file_path)
                fix_import_order(file_path)
                fix_block_comments(file_path)
            except Exception as e:
                print(f"    Error fixing {file_path}: {e}")

    print("✅ Critical issues fixed!")


if __name__ == "__main__":
    main()
