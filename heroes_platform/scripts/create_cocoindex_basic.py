#!/usr/bin/env python3
"""
Basic CocoIndex Creator

Creates basic CocoIndex for key scripts and workflows.
"""

from pathlib import Path


class CocoIndexBasicCreator:
    """Creates basic CocoIndex for key scripts."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.key_directories = [
            "scripts/",
            "workflows/",
            "src/",
            "heroes-platform/heroes_mcp/",
            "heroes-platform/heroes_mcp/scripts/",
            "heroes-platform/heroes_mcp/src/",
            "advising_platform/src/mcp/workflows/",
            "advising_platform/src/mcp/",
        ]

    def find_key_scripts(self) -> list[str]:
        """Find key scripts in important directories."""
        key_scripts = []

        for directory in self.key_directories:
            dir_path = self.project_root / directory
            if dir_path.exists():
                print(f"🔍 Scanning {directory}...")

                # Find Python files
                for py_file in dir_path.rglob("*.py"):
                    if py_file.is_file():
                        key_scripts.append(str(py_file))

        print(f"✅ Found {len(key_scripts)} key scripts")
        return key_scripts

    def create_basic_index(self, key_scripts: list[str]):
        """Create basic index for key scripts."""
        print("🔍 Creating basic CocoIndex...")

        # Create index file
        index_file = self.project_root / "cocoindex_basic_index.txt"

        with open(index_file, "w", encoding="utf-8") as f:
            for script in key_scripts:
                f.write(f"{script}\n")

        print(f"✅ Basic index created: {index_file}")
        return index_file

    def analyze_script_categories(self, key_scripts: list[str]) -> dict[str, list[str]]:
        """Analyze scripts by category."""
        categories = {
            "workflow": [],
            "monitoring": [],
            "utility": [],
            "test": [],
            "integration": [],
            "documentation": [],
            "other": [],
        }

        for script in key_scripts:
            script_name = Path(script).name.lower()

            if any(
                keyword in script_name
                for keyword in ["workflow", "orchestrator", "pipeline"]
            ):
                categories["workflow"].append(script)
            elif any(
                keyword in script_name
                for keyword in ["monitor", "log", "health", "check"]
            ):
                categories["monitoring"].append(script)
            elif any(
                keyword in script_name for keyword in ["util", "helper", "common"]
            ):
                categories["utility"].append(script)
            elif any(keyword in script_name for keyword in ["test", "spec"]):
                categories["test"].append(script)
            elif any(
                keyword in script_name for keyword in ["integrate", "connect", "sync"]
            ):
                categories["integration"].append(script)
            elif any(keyword in script_name for keyword in ["doc", "readme", "help"]):
                categories["documentation"].append(script)
            else:
                categories["other"].append(script)

        return categories

    def generate_basic_report(
        self, key_scripts: list[str], categories: dict[str, list[str]]
    ):
        """Generate basic CocoIndex report."""
        report_file = self.project_root / "cocoindex_basic_report.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# Basic CocoIndex Report\n\n")
            f.write(f"**Total key scripts indexed:** {len(key_scripts)}\n\n")

            # Categories
            f.write("## Script Categories\n\n")

            for category, scripts in categories.items():
                f.write(f"### {category.title()} ({len(scripts)} scripts)\n\n")

                for script in scripts[:10]:  # Top 10 scripts
                    f.write(f"- `{script}`\n")

                if len(scripts) > 10:
                    f.write(f"- ... and {len(scripts) - 10} more\n")

                f.write("\n")

            # Search patterns
            f.write("## Search Patterns for AI Agent\n\n")
            f.write("### Workflow Scripts\n")
            f.write("- `workflow automation`\n")
            f.write("- `process orchestration`\n")
            f.write("- `pipeline management`\n\n")

            f.write("### Monitoring Scripts\n")
            f.write("- `log monitoring`\n")
            f.write("- `health checks`\n")
            f.write("- `system monitoring`\n\n")

            f.write("### Utility Scripts\n")
            f.write("- `utility functions`\n")
            f.write("- `helper scripts`\n")
            f.write("- `common utilities`\n\n")

            f.write("### Integration Scripts\n")
            f.write("- `api integration`\n")
            f.write("- `system connection`\n")
            f.write("- `data sync`\n\n")

            # Confidence levels
            f.write("## Confidence Levels\n\n")
            f.write("| Category | Confidence | Reason |\n")
            f.write("|----------|------------|--------|\n")
            f.write("| workflow | 0.9 | High specificity, clear naming |\n")
            f.write("| monitoring | 0.8 | Specific functionality |\n")
            f.write("| utility | 0.7 | Generic but identifiable |\n")
            f.write("| test | 0.9 | Clear test patterns |\n")
            f.write("| integration | 0.8 | Specific integration patterns |\n")
            f.write("| documentation | 0.9 | Clear documentation patterns |\n")
            f.write("| other | 0.3 | Low specificity, requires manual review |\n")

        print(f"✅ Basic report generated: {report_file}")


def main():
    """Main function."""
    print("🔍 Starting basic CocoIndex creation...")

    creator = CocoIndexBasicCreator()

    # Find key scripts
    key_scripts = creator.find_key_scripts()

    if not key_scripts:
        print("❌ No key scripts found")
        return

    # Create basic index
    index_file = creator.create_basic_index(key_scripts)

    # Analyze categories
    categories = creator.analyze_script_categories(key_scripts)

    # Generate report
    creator.generate_basic_report(key_scripts, categories)

    print("✅ Basic CocoIndex creation completed!")


if __name__ == "__main__":
    main()
