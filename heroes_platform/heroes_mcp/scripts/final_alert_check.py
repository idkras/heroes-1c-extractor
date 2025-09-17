#!/usr/bin/env python3
"""
Final Alert Check Script
CI/CD Integration for final critical issues check and alerts
"""

import json
import sys
from pathlib import Path


def check_final_alerts():
    """Check for critical issues and generate final alerts"""
    analysis_file = Path("logs/log_analysis.json")

    if not analysis_file.exists():
        print("❌ Log analysis file not found")
        return False

    try:
        with open(analysis_file) as f:
            data = json.load(f)

        critical_count = len(data.get("critical_issues", []))
        error_count = data.get("statistics", {}).get("error_count", 0)

        if critical_count > 0 or error_count > 10:
            print(
                f"🚨 CRITICAL: {critical_count} critical issues, {error_count} total errors"
            )
            print("::error::MCP Server has critical issues that need attention")
            return False
        else:
            print("✅ Server health check passed")
            return True

    except Exception as e:
        print(f"❌ Error reading analysis file: {e}")
        return False


def main():
    """Main function"""
    success = check_final_alerts()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
