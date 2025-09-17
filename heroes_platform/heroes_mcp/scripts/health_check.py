#!/usr/bin/env python3
"""
Health Check Script for MCP Server
CI/CD Integration for monitoring server health
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def check_server_health() -> dict:
    """Check MCP server health and generate report"""
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "server_status": "healthy",
        "last_check": datetime.now().isoformat(),
        "recommendations": [],  # type: ignore
        "issues_found": [],  # type: ignore
    }

    # Check log file
    log_file = Path("logs/mcp_server.log")
    if log_file.exists():
        try:
            with open(log_file) as f:
                logs = f.readlines()
                error_count = sum(1 for line in logs if "ERROR" in line)
                warning_count = sum(1 for line in logs if "WARNING" in line)

                if error_count > 0:
                    health_report["server_status"] = "degraded"
                    health_report["issues_found"].append(  # type: ignore
                        f"Found {error_count} errors in logs"
                    )
                    health_report["recommendations"].append(  # type: ignore
                        "Review error logs and fix issues"
                    )

                if warning_count > 10:
                    health_report["issues_found"].append(  # type: ignore
                        f"Found {warning_count} warnings in logs"
                    )
                    health_report["recommendations"].append("Review warning patterns")  # type: ignore

        except Exception as e:
            health_report["server_status"] = "unknown"
            health_report["issues_found"].append(f"Could not read log file: {e}")  # type: ignore
    else:
        health_report["server_status"] = "unknown"
        health_report["issues_found"].append("Log file not found")  # type: ignore

    # Check for critical patterns in recent logs
    if log_file.exists():
        try:
            with open(log_file) as f:
                recent_logs = f.readlines()[-50:]  # Last 50 lines

                critical_patterns = [
                    "Workflow.*not available",
                    "object has no attribute",
                    "Import.*could not be resolved",
                    "No module named",
                    "Server.*failed",
                    "startup.*error",
                ]

                for line in recent_logs:
                    for pattern in critical_patterns:
                        if pattern in line:
                            health_report["server_status"] = "critical"
                            health_report["issues_found"].append(  # type: ignore
                                f"Critical pattern found: {pattern}"
                            )
                            break
        except Exception as e:
            health_report["issues_found"].append(f"Error analyzing recent logs: {e}")  # type: ignore

    return health_report


def main():
    """Main function for health check"""
    health_report = check_server_health()

    # Save health report
    output_file = Path("logs/health_report.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(health_report, f, indent=2)

    # Print status
    print(f"Server status: {health_report['server_status']}")

    if health_report["issues_found"]:
        print("Issues found:")
        for issue in health_report["issues_found"]:
            print(f"  - {issue}")

    if health_report["recommendations"]:
        print("Recommendations:")
        for rec in health_report["recommendations"]:
            print(f"  - {rec}")

    # Exit with error code if critical
    if health_report["server_status"] == "critical":
        sys.exit(1)
    elif health_report["server_status"] == "degraded":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
