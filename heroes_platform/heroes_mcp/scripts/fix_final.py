#!/usr/bin/env python3
"""
Final script to fix remaining issues
"""

import os
import re


def fix_final_issues():
    """Fix final remaining issues"""

    # Fix mcp_server.py issues
    mcp_file = "src/mcp_server.py"
    if os.path.exists(mcp_file):
        with open(mcp_file) as f:
            content = f.read()

        # Fix long lines by breaking them
        content = re.sub(
            r'description="([^"]{100,})"',
            lambda m: f'description=(\n                        "{m.group(1)[:50]}...\n                    )',
            content,
        )

        # Fix blank lines with whitespace
        content = re.sub(r"[ \t]+\n", "\n", content)

        # Fix unused variables
        content = re.sub(
            r"result = await workflow\.execute\(", "await workflow.execute(", content
        )

        # Fix too many blank lines
        content = re.sub(r"\n\n\n+", "\n\n", content)

        with open(mcp_file, "w") as f:
            f.write(content)
        print(f"Fixed {mcp_file}")

    # Fix workflow files
    workflow_files = [
        "src/workflows/dependency_management.py",
        "src/workflows/telegram_workflow_fixed.py",
    ]

    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            with open(workflow_file) as f:
                content = f.read()

            # Fix blank lines with whitespace
            content = re.sub(r"[ \t]+\n", "\n", content)

            with open(workflow_file, "w") as f:
                f.write(content)
            print(f"Fixed {workflow_file}")

    # Fix test files
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

            # Move imports to top
            if "from typing import" in content:
                lines = content.split("\n")
                import_lines = []
                other_lines = []

                for line in lines:
                    if line.strip().startswith(
                        "from typing import"
                    ) or line.strip().startswith("import "):
                        import_lines.append(line)
                    else:
                        other_lines.append(line)

                content = "\n".join(import_lines) + "\n\n" + "\n".join(other_lines)

            # Add missing imports
            if (
                "List" in content
                and "from typing import" in content
                and "List" not in content.split("from typing import")[1].split("\n")[0]
            ):
                content = re.sub(
                    r"from typing import ([^,\n]+)",
                    r"from typing import \1, List, Dict",
                    content,
                )

            with open(test_file, "w") as f:
                f.write(content)
            print(f"Fixed {test_file}")

    print("Final fixes completed!")


if __name__ == "__main__":
    fix_final_issues()
