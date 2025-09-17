#!/usr/bin/env python3
"""
Comprehensive MCP Commands Tester

Comprehensive testing for all MCP commands with quality validation and cross-check.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from quality.test_mcp_commands_quality import MCPCommandQualityTester
from cross_check.test_cursor_integration import CursorCrossChecker

logger = logging.getLogger(__name__)


class ComprehensiveMCPTester:
    """Comprehensive tester for all MCP commands"""

    def __init__(self):
        self.quality_tester = MCPCommandQualityTester()
        self.cross_checker = CursorCrossChecker()
        self.test_results = {}

    async def test_all_commands(self) -> Dict[str, Any]:
        """
        JTBD: Как тестировщик, я хочу проверить все MCP команды качественно,
        чтобы убедиться что система работает надежно.
        """

        # 🔍 REFLECTION CHECKPOINT 1 - Comprehensive testing setup
        logger.info("REFLECTION: Starting comprehensive MCP command testing")
        logger.info("REFLECTION: Testing quality + cross-check for all commands")

        # GIVEN - список всех команд для тестирования
        commands_to_test = [
            ("standards_list", {}),
            (
                "standards_get",
                {"standard_name": "0.0 task master 10 may 2226 cet by ilya krasinsky"},
            ),
            ("standards_search", {"query": "task master"}),
            (
                "workflow_integration",
                {"workflow_name": "standards", "action": "status"},
            ),
            ("registry_compliance_check", {}),
        ]

        # WHEN - тестирование каждой команды
        for command_name, arguments in commands_to_test:
            logger.info(f"REFLECTION: Testing command: {command_name}")

            # Quality test
            quality_result = await self.quality_tester.test_command_quality(
                command_name, arguments
            )

            # Cross-check test
            cross_check_result = await self.cross_checker.test_command_in_cursor(
                command_name, arguments
            )

            # Combine results
            combined_result = {
                "command": command_name,
                "quality_score": quality_result["quality_score"],
                "cross_check_score": cross_check_result["cross_check_score"],
                "overall_score": (
                    quality_result["quality_score"]
                    + cross_check_result["cross_check_score"]
                )
                / 2,
                "quality_passed": quality_result["passed"],
                "cross_check_passed": cross_check_result["success"],
                "execution_time": max(
                    quality_result["execution_time"],
                    cross_check_result["execution_time"],
                ),
                "overall_passed": quality_result["passed"]
                and cross_check_result["success"],
            }

            self.test_results[command_name] = combined_result

            # 🔍 REFLECTION CHECKPOINT 2 - Command validation
            logger.info(
                f"REFLECTION: {command_name} - Quality: {quality_result['quality_score']:.2f}, Cross-check: {cross_check_result['cross_check_score']:.2f}"
            )

        # THEN - анализ результатов
        overall_results = self.analyze_overall_results()

        # 🔍 REFLECTION CHECKPOINT 3 - Overall assessment
        logger.info(f"REFLECTION: Overall test results: {overall_results}")

        return overall_results

    def analyze_overall_results(self) -> Dict[str, Any]:
        """Analyze overall test results"""

        total_commands = len(self.test_results)
        passed_commands = sum(
            1 for r in self.test_results.values() if r["overall_passed"]
        )
        quality_passed = sum(
            1 for r in self.test_results.values() if r["quality_passed"]
        )
        cross_check_passed = sum(
            1 for r in self.test_results.values() if r["cross_check_passed"]
        )

        avg_quality_score = (
            sum(r["quality_score"] for r in self.test_results.values()) / total_commands
        )
        avg_cross_check_score = (
            sum(r["cross_check_score"] for r in self.test_results.values())
            / total_commands
        )
        avg_overall_score = (
            sum(r["overall_score"] for r in self.test_results.values()) / total_commands
        )

        avg_execution_time = (
            sum(r["execution_time"] for r in self.test_results.values())
            / total_commands
        )

        return {
            "total_commands": total_commands,
            "passed_commands": passed_commands,
            "quality_passed": quality_passed,
            "cross_check_passed": cross_check_passed,
            "success_rate": passed_commands / total_commands,
            "avg_quality_score": avg_quality_score,
            "avg_cross_check_score": avg_cross_check_score,
            "avg_overall_score": avg_overall_score,
            "avg_execution_time": avg_execution_time,
            "overall_passed": passed_commands == total_commands,
            "command_details": self.test_results,
        }

    def get_confident_commands(self) -> List[str]:
        """Get list of commands we are confident work correctly"""

        confident_commands = []

        for command_name, result in self.test_results.items():
            if result["overall_passed"] and result["overall_score"] >= 0.85:
                confident_commands.append(command_name)

        return confident_commands

    def generate_gap_report(self) -> Dict[str, Any]:
        """Generate gap report for failed commands"""

        failed_commands = []
        gap_analysis = {}

        for command_name, result in self.test_results.items():
            if not result["overall_passed"]:
                failed_commands.append(command_name)

                gap_analysis[command_name] = {
                    "quality_gap": (
                        0.85 - result["quality_score"]
                        if result["quality_score"] < 0.85
                        else 0
                    ),
                    "cross_check_gap": (
                        0.85 - result["cross_check_score"]
                        if result["cross_check_score"] < 0.85
                        else 0
                    ),
                    "issues": [],
                }

                if result["quality_score"] < 0.85:
                    gap_analysis[command_name]["issues"].append(
                        "Quality score below threshold"
                    )

                if result["cross_check_score"] < 0.85:
                    gap_analysis[command_name]["issues"].append(
                        "Cross-check score below threshold"
                    )

        return {
            "failed_commands": failed_commands,
            "gap_analysis": gap_analysis,
            "recommendations": self.generate_recommendations(gap_analysis),
        }

    def generate_recommendations(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on gap analysis"""

        recommendations = []

        for command_name, analysis in gap_analysis.items():
            if analysis["quality_gap"] > 0:
                recommendations.append(f"Improve quality testing for {command_name}")

            if analysis["cross_check_gap"] > 0:
                recommendations.append(f"Fix cross-check issues for {command_name}")

        return recommendations


# Main test function
async def test_all_mcp_commands():
    """Test all MCP commands comprehensively"""

    print("🔍 Starting Comprehensive MCP Commands Testing...")
    print("=" * 60)

    tester = ComprehensiveMCPTester()
    results = await tester.test_all_commands()

    print("\n📊 TEST RESULTS:")
    print("=" * 60)
    print(f"Total commands tested: {results['total_commands']}")
    print(f"Commands passed: {results['passed_commands']}")
    print(f"Success rate: {results['success_rate']:.1%}")
    print(f"Average quality score: {results['avg_quality_score']:.2f}")
    print(f"Average cross-check score: {results['avg_cross_check_score']:.2f}")
    print(f"Average overall score: {results['avg_overall_score']:.2f}")
    print(f"Average execution time: {results['avg_execution_time']:.2f}s")

    print("\n📋 COMMAND DETAILS:")
    print("=" * 60)
    for command_name, details in results["command_details"].items():
        status = "✅ PASSED" if details["overall_passed"] else "❌ FAILED"
        print(f"{command_name}: {status}")
        print(
            f"  Quality: {details['quality_score']:.2f} {'✅' if details['quality_passed'] else '❌'}"
        )
        print(
            f"  Cross-check: {details['cross_check_score']:.2f} {'✅' if details['cross_check_passed'] else '❌'}"
        )
        print(f"  Overall: {details['overall_score']:.2f}")
        print()

    # Get confident commands
    confident_commands = tester.get_confident_commands()
    print("🎯 CONFIDENT COMMANDS:")
    print("=" * 60)
    for command in confident_commands:
        print(f"✅ {command}")

    # Generate gap report
    gap_report = tester.generate_gap_report()
    if gap_report["failed_commands"]:
        print("\n🚨 FAILED COMMANDS:")
        print("=" * 60)
        for command in gap_report["failed_commands"]:
            print(f"❌ {command}")

        print("\n📋 RECOMMENDATIONS:")
        print("=" * 60)
        for recommendation in gap_report["recommendations"]:
            print(f"• {recommendation}")

    print("\n" + "=" * 60)
    if results["overall_passed"]:
        print("🎉 ALL TESTS PASSED! MCP server is working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED. Check recommendations above.")

    return results


if __name__ == "__main__":
    asyncio.run(test_all_mcp_commands())
