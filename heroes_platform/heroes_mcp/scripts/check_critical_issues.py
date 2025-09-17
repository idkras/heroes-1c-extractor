#!/usr/bin/env python3
"""
Check Critical Issues Script
CI/CD Integration for checking critical issues in logs
"""

import json
import sys
from pathlib import Path


def check_critical_issues():
    """Check for critical issues in log analysis"""
    analysis_file = Path("logs/log_analysis.json")

    if not analysis_file.exists():
        print("❌ Log analysis file not found")
        return False

    try:
        with open(analysis_file) as f:
            data = json.load(f)

        critical_count = len(data.get("critical_issues", []))
        error_count = data.get("statistics", {}).get("error_count", 0)

        if critical_count > 0:
            print(f"🚨 Found {critical_count} critical issues")
            return False
        elif error_count > 10:
            print(f"⚠️ Found {error_count} total errors (threshold exceeded)")
            return False
        else:
            print("✅ No critical issues found")
            return True

    except Exception as e:
        print(f"❌ Error reading analysis file: {e}")
        return False


def main():
    """Main function"""
    success = check_critical_issues()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
