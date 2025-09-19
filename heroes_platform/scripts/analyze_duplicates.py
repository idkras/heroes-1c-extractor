#!/usr/bin/env python3
"""
Script Duplicate Analyzer

Analyzes Python files for potential duplicates and similar functionality.
"""

import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path


class DuplicateAnalyzer:
    """Analyzes Python files for duplicates and similar functionality."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = []
        self.content_hashes = defaultdict(list)
        self.function_patterns = defaultdict(list)
        self.class_patterns = defaultdict(list)

    def load_python_files(self, index_file: str = "python_files_index.txt"):
        """Load Python files from index."""
        index_path = self.project_root / index_file

        if not index_path.exists():
            print(f"❌ Index file not found: {index_path}")
            return False

        with open(index_path) as f:
            self.python_files = [line.strip() for line in f if line.strip()]

        print(f"✅ Loaded {len(self.python_files)} Python files")
        return True

    def analyze_content_duplicates(self) -> dict[str, list[str]]:
        """Analyze content-based duplicates."""
        print("🔍 Analyzing content duplicates...")

        for file_path in self.python_files:
            if not os.path.exists(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Remove comments and whitespace for comparison
                clean_content = self._clean_content(content)
                content_hash = hashlib.md5(clean_content.encode()).hexdigest()

                self.content_hashes[content_hash].append(file_path)

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")

        # Find duplicates
        duplicates = {
            hash_val: files
            for hash_val, files in self.content_hashes.items()
            if len(files) > 1
        }

        print(f"✅ Found {len(duplicates)} content duplicates")
        return duplicates

    def analyze_function_patterns(self) -> dict[str, list[str]]:
        """Analyze function patterns for similar functionality."""
        print("🔍 Analyzing function patterns...")

        function_patterns = defaultdict(list)

        for file_path in self.python_files:
            if not os.path.exists(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract function definitions
                functions = self._extract_functions(content)

                for func_name, func_content in functions.items():
                    # Create pattern based on function signature and key operations
                    pattern = self._create_function_pattern(func_content)
                    function_patterns[pattern].append(f"{file_path}:{func_name}")

            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")

        # Find similar functions
        similar_functions = {
            pattern: funcs
            for pattern, funcs in function_patterns.items()
            if len(funcs) > 1
        }

        print(f"✅ Found {len(similar_functions)} similar function patterns")
        return similar_functions

    def analyze_class_patterns(self) -> dict[str, list[str]]:
        """Analyze class patterns for similar functionality."""
        print("🔍 Analyzing class patterns...")

        class_patterns = defaultdict(list)

        for file_path in self.python_files:
            if not os.path.exists(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract class definitions
                classes = self._extract_classes(content)

                for class_name, class_content in classes.items():
                    # Create pattern based on class structure
                    pattern = self._create_class_pattern(class_content)
                    class_patterns[pattern].append(f"{file_path}:{class_name}")

            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")

        # Find similar classes
        similar_classes = {
            pattern: classes
            for pattern, classes in class_patterns.items()
            if len(classes) > 1
        }

        print(f"✅ Found {len(similar_classes)} similar class patterns")
        return similar_classes

    def _clean_content(self, content: str) -> str:
        """Clean content for comparison."""
        # Remove comments
        content = re.sub(r"#.*$", "", content, flags=re.MULTILINE)
        content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)

        # Remove extra whitespace
        content = re.sub(r"\s+", " ", content)
        content = content.strip()

        return content

    def _extract_functions(self, content: str) -> dict[str, str]:
        """Extract function definitions from content."""
        functions = {}

        # Pattern for function definitions
        pattern = r"def\s+(\w+)\s*\([^)]*\)\s*:.*?(?=def\s+\w+\s*\(|$)"
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            func_name = match.group(1)
            func_content = match.group(0)
            functions[func_name] = func_content

        return functions

    def _extract_classes(self, content: str) -> dict[str, str]:
        """Extract class definitions from content."""
        classes = {}

        # Pattern for class definitions
        pattern = r"class\s+(\w+).*?(?=class\s+\w+|$)"
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            class_name = match.group(1)
            class_content = match.group(0)
            classes[class_name] = class_content

        return classes

    def _create_function_pattern(self, func_content: str) -> str:
        """Create a pattern for function comparison."""
        # Extract key operations and structure
        lines = func_content.split("\n")
        key_lines = []

        for line in lines:
            line = line.strip()
            if any(
                keyword in line
                for keyword in [
                    "import",
                    "from",
                    "def",
                    "return",
                    "if",
                    "for",
                    "while",
                    "try",
                    "except",
                ]
            ):
                key_lines.append(line)

        return "|".join(key_lines[:5])  # First 5 key lines

    def _create_class_pattern(self, class_content: str) -> str:
        """Create a pattern for class comparison."""
        # Extract class structure
        lines = class_content.split("\n")
        key_lines = []

        for line in lines:
            line = line.strip()
            if any(
                keyword in line
                for keyword in ["class", "def __init__", "def ", "import", "from"]
            ):
                key_lines.append(line)

        return "|".join(key_lines[:10])  # First 10 key lines

    def generate_report(
        self, duplicates: dict, similar_functions: dict, similar_classes: dict
    ):
        """Generate analysis report."""
        report_path = self.project_root / "duplicate_analysis_report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Python Files Duplicate Analysis Report\n\n")
            f.write(f"**Total Python files analyzed:** {len(self.python_files)}\n\n")

            # Content duplicates
            f.write("## Content Duplicates\n\n")
            if duplicates:
                for hash_val, files in duplicates.items():
                    f.write(f"### Duplicate Group (Hash: {hash_val[:8]}...)\n")
                    for file_path in files:
                        f.write(f"- `{file_path}`\n")
                    f.write("\n")
            else:
                f.write("No exact content duplicates found.\n\n")

            # Similar functions
            f.write("## Similar Functions\n\n")
            if similar_functions:
                for pattern, funcs in list(similar_functions.items())[:10]:  # Top 10
                    f.write("### Similar Function Pattern\n")
                    f.write(f"**Pattern:** `{pattern[:100]}...`\n\n")
                    for func in funcs:
                        f.write(f"- `{func}`\n")
                    f.write("\n")
            else:
                f.write("No similar function patterns found.\n\n")

            # Similar classes
            f.write("## Similar Classes\n\n")
            if similar_classes:
                for pattern, classes in list(similar_classes.items())[:10]:  # Top 10
                    f.write("### Similar Class Pattern\n")
                    f.write(f"**Pattern:** `{pattern[:100]}...`\n\n")
                    for cls in classes:
                        f.write(f"- `{cls}`\n")
                    f.write("\n")
            else:
                f.write("No similar class patterns found.\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Content duplicates:** {len(duplicates)}\n")
            f.write(f"- **Similar function patterns:** {len(similar_functions)}\n")
            f.write(f"- **Similar class patterns:** {len(similar_classes)}\n")

        print(f"✅ Report generated: {report_path}")


def main():
    """Main function."""
    print("🔍 Starting Python files duplicate analysis...")

    analyzer = DuplicateAnalyzer()

    # Load Python files
    if not analyzer.load_python_files():
        return

    # Analyze duplicates
    duplicates = analyzer.analyze_content_duplicates()
    similar_functions = analyzer.analyze_function_patterns()
    similar_classes = analyzer.analyze_class_patterns()

    # Generate report
    analyzer.generate_report(duplicates, similar_functions, similar_classes)

    print("✅ Analysis completed!")


if __name__ == "__main__":
    main()
