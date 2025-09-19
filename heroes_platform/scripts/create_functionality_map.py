#!/usr/bin/env python3
"""
Functionality Map Creator

Creates a map of functionality across Python files for better search patterns.
"""

import os
from collections import defaultdict
from pathlib import Path


class FunctionalityMapper:
    """Creates a map of functionality across Python files."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = []
        self.functionality_map = defaultdict(list)
        self.keyword_patterns = {
            "authentication": ["auth", "login", "password", "token", "session"],
            "database": ["db", "database", "sql", "query", "connection"],
            "api": ["api", "endpoint", "request", "response", "http"],
            "file_processing": ["file", "read", "write", "parse", "csv", "json"],
            "testing": ["test", "assert", "mock", "fixture", "pytest"],
            "monitoring": ["log", "monitor", "health", "check", "alert"],
            "workflow": ["workflow", "process", "pipeline", "orchestrator"],
            "analysis": ["analyze", "process", "calculate", "compute"],
            "integration": ["integrate", "connect", "sync", "webhook"],
            "validation": ["validate", "check", "verify", "assert"],
            "configuration": ["config", "settings", "env", "parameter"],
            "documentation": ["doc", "comment", "help", "readme"],
            "utility": ["util", "helper", "common", "shared"],
            "model": ["model", "class", "entity", "data"],
            "service": ["service", "manager", "handler", "controller"],
        }

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

    def analyze_file_functionality(self, file_path: str) -> dict[str, float]:
        """Analyze functionality of a single file."""
        if not os.path.exists(file_path):
            return {}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read().lower()

            functionality_scores = {}

            for category, keywords in self.keyword_patterns.items():
                score = 0
                for keyword in keywords:
                    # Count keyword occurrences
                    count = content.count(keyword)
                    score += count

                # Normalize score
                if score > 0:
                    functionality_scores[category] = min(score / 10.0, 1.0)

            return functionality_scores

        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
            return {}

    def create_functionality_map(self) -> dict[str, list[str]]:
        """Create functionality map across all files."""
        print("🔍 Creating functionality map...")

        for file_path in self.python_files:
            functionality_scores = self.analyze_file_functionality(file_path)

            for category, score in functionality_scores.items():
                if score > 0.1:  # Only include files with significant functionality
                    self.functionality_map[category].append(
                        {"file": file_path, "score": score}
                    )

        # Sort by score for each category
        for category in self.functionality_map:
            self.functionality_map[category].sort(
                key=lambda x: x["score"], reverse=True
            )

        print(
            f"✅ Functionality map created with {len(self.functionality_map)} categories"
        )
        return self.functionality_map

    def analyze_search_patterns(self) -> dict[str, list[str]]:
        """Analyze and create search patterns for each functionality."""
        print("🔍 Creating search patterns...")

        search_patterns = {}

        for category, files in self.functionality_map.items():
            patterns = []

            # Create semantic search patterns
            patterns.append(f"files related to {category}")
            patterns.append(f"code for {category} functionality")
            patterns.append(f"implementation of {category}")

            # Create specific patterns based on category
            if category == "authentication":
                patterns.extend(
                    ["user login", "password verification", "session management"]
                )
            elif category == "database":
                patterns.extend(
                    ["database connection", "sql queries", "data persistence"]
                )
            elif category == "api":
                patterns.extend(["api endpoints", "http requests", "rest api"])
            elif category == "file_processing":
                patterns.extend(["file reading", "data parsing", "csv processing"])
            elif category == "testing":
                patterns.extend(["unit tests", "test cases", "test automation"])
            elif category == "monitoring":
                patterns.extend(
                    ["log monitoring", "health checks", "system monitoring"]
                )
            elif category == "workflow":
                patterns.extend(
                    [
                        "workflow automation",
                        "process orchestration",
                        "pipeline management",
                    ]
                )

            search_patterns[category] = patterns

        print(f"✅ Created search patterns for {len(search_patterns)} categories")
        return search_patterns

    def generate_functionality_report(self, search_patterns: dict[str, list[str]]):
        """Generate functionality map report."""
        report_path = self.project_root / "functionality_map_report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Python Files Functionality Map Report\n\n")
            f.write(f"**Total Python files analyzed:** {len(self.python_files)}\n\n")

            # Functionality categories
            f.write("## Functionality Categories\n\n")

            for category, files in self.functionality_map.items():
                f.write(f"### {category.title()} ({len(files)} files)\n\n")

                # Top files in category
                f.write("**Top files:**\n")
                for file_info in files[:5]:  # Top 5 files
                    f.write(
                        f"- `{file_info['file']}` (score: {file_info['score']:.2f})\n"
                    )
                f.write("\n")

                # Search patterns
                if category in search_patterns:
                    f.write("**Search patterns:**\n")
                    for pattern in search_patterns[category]:
                        f.write(f"- `{pattern}`\n")
                    f.write("\n")

                f.write("---\n\n")

            # Summary statistics
            f.write("## Summary Statistics\n\n")
            f.write("| Category | Files | Avg Score |\n")
            f.write("|----------|-------|-----------|\n")

            for category, files in self.functionality_map.items():
                if files:
                    avg_score = sum(f["score"] for f in files) / len(files)
                    f.write(f"| {category} | {len(files)} | {avg_score:.2f} |\n")

            f.write("\n")

            # Recommendations
            f.write("## Search Pattern Recommendations\n\n")
            f.write("### For AI Agent Search\n\n")
            f.write("1. **Start with semantic search** using category names\n")
            f.write("2. **Use specific patterns** for targeted functionality\n")
            f.write("3. **Check top-scoring files** in relevant categories\n")
            f.write("4. **Combine patterns** for complex functionality\n\n")

            f.write("### Example Search Queries\n\n")
            for category, patterns in search_patterns.items():
                f.write(f"**{category.title()}:**\n")
                for pattern in patterns[:3]:  # Top 3 patterns
                    f.write(f"- `{pattern}`\n")
                f.write("\n")

        print(f"✅ Functionality map report generated: {report_path}")

    def create_search_confidence_rules(self) -> dict[str, float]:
        """Create confidence rules for search patterns."""
        print("🔍 Creating search confidence rules...")

        confidence_rules = {}

        for category, files in self.functionality_map.items():
            if files:
                # Calculate confidence based on number of files and average score
                num_files = len(files)
                avg_score = sum(f["score"] for f in files) / len(files)

                # Confidence formula: (num_files * avg_score) / 100
                confidence = min((num_files * avg_score) / 100.0, 1.0)
                confidence_rules[category] = confidence

        print(f"✅ Created confidence rules for {len(confidence_rules)} categories")
        return confidence_rules


def main():
    """Main function."""
    print("🔍 Starting functionality mapping...")

    mapper = FunctionalityMapper()

    # Load Python files
    if not mapper.load_python_files():
        return

    # Create functionality map
    functionality_map = mapper.create_functionality_map()

    # Create search patterns
    search_patterns = mapper.analyze_search_patterns()

    # Create confidence rules
    confidence_rules = mapper.create_search_confidence_rules()

    # Generate report
    mapper.generate_functionality_report(search_patterns)

    print("✅ Functionality mapping completed!")


if __name__ == "__main__":
    main()
