#!/usr/bin/env python3
"""
Rick AI Workflow Example
Пример использования Rick.ai Research Loop Workflow
"""

import asyncio

from heroes_platform.heroes_mcp.workflows.rick_ai.workflow import RickAIWorkflow


async def main():
    """Main example function"""
    print("🚀 Rick.ai Research Loop Workflow Example")
    print("=" * 50)

    # Initialize workflow
    workflow = RickAIWorkflow()

    # Example 1: Basic authentication
    print("\n1️⃣ Basic Authentication")
    print("-" * 30)

    auth_result = await workflow.execute(
        {"command": "authenticate", "session_cookie": "example_session_cookie_123"}
    )

    print(f"Status: {auth_result['status']}")
    print(f"Message: {auth_result['message']}")

    # Example 2: Analyze grouping data (without real API calls)
    print("\n2️⃣ Analyze Grouping Data")
    print("-" * 30)

    # Sample data for analysis
    sample_widget_groups = [
        {"name": "Organic Traffic", "id": "group_1"},
        {"name": "Paid Advertising", "id": "group_2"},
        {"name": "Social Media", "id": "group_3"},
        {"name": "A", "id": "group_4"},  # Too short name - will trigger anomaly
    ]

    sample_widget_data = {
        "data": {"visits": 1000, "conversions": 50},
        "metadata": {"version": "1.0", "last_updated": "2025-01-15"},
        "config": {"settings": "default", "grouping_rules": "standard"},
    }

    analysis_result = await workflow.execute(
        {
            "command": "analyze_grouping_data",
            "widget_data": sample_widget_data,
            "widget_groups": sample_widget_groups,
        }
    )

    print(f"Status: {analysis_result.get('status', 'unknown')}")
    print(f"Message: {analysis_result.get('message', 'No message')}")

    if analysis_result.get("status") == "success":
        data = analysis_result.get("data", {})
        print(f"Key Findings: {len(data.get('key_findings', []))}")
        print(f"Error Patterns: {len(data.get('error_patterns', []))}")
        print(f"Data Quality Issues: {len(data.get('data_quality_issues', []))}")
        print(f"Grouping Anomalies: {len(data.get('grouping_anomalies', []))}")
        print(f"Recommendations: {len(data.get('recommendations', []))}")

        # Show some details
        if data.get("key_findings"):
            print(f"  - {data['key_findings'][0]}")
        if data.get("grouping_anomalies"):
            print(f"  - {data['grouping_anomalies'][0]}")

    # Example 3: Validate grouping rules
    print("\n3️⃣ Validate Grouping Rules")
    print("-" * 30)

    validation_result = await workflow.execute(
        {
            "command": "validate_grouping_rules",
            "analysis_results": analysis_result.get("data", {}),
        }
    )

    print(f"Status: {validation_result.get('status', 'unknown')}")
    print(f"Message: {validation_result.get('message', 'No message')}")

    if validation_result.get("status") == "success":
        data = validation_result.get("data", {})
        print(f"Compliance Score: {data.get('compliance_score', 0)}%")
        print(f"Validation Status: {data.get('validation_status', 'unknown')}")
        print(f"Rule Violations: {len(data.get('rule_violations', []))}")
        print(f"Best Practices: {len(data.get('best_practices', []))}")

    # Example 4: Generate correction rules
    print("\n4️⃣ Generate Correction Rules")
    print("-" * 30)

    correction_result = await workflow.execute(
        {
            "command": "generate_correction_rules",
            "validation_results": validation_result.get("data", {}),
            "analysis_results": analysis_result.get("data", {}),
        }
    )

    print(f"Status: {correction_result.get('status', 'unknown')}")
    print(f"Message: {correction_result.get('message', 'No message')}")

    if correction_result.get("status") == "success":
        data = correction_result.get("data", {})
        print(f"Rules Generated: {len(data.get('rules', []))}")
        print(f"Implementation Steps: {len(data.get('implementation_steps', []))}")
        print(f"Recommendations: {len(data.get('recommendations', []))}")

        # Show first rule
        if data.get("rules"):
            rule = data["rules"][0]
            print(f"  Rule {rule.get('rule_id', 'N/A')}: {rule.get('title', 'N/A')}")
            print(f"    Priority: {rule.get('priority', 'N/A')}")
            print(f"    Description: {rule.get('description', 'N/A')}")

    # Example 5: Complete research loop (simulated)
    print("\n5️⃣ Complete Research Loop (Simulated)")
    print("-" * 30)

    # Note: This would normally require real API credentials
    print("Note: Full research loop requires real Rick.ai API credentials")
    print("This example shows the structure without actual API calls")

    research_loop_structure = {
        "workflow_name": "rick-ai-research-loop",
        "version": "v1.0",
        "workflow_stages": [
            "authentication",
            "get_clients",
            "get_widget_groups",
            "get_widget_data",
            "analyze_grouping_data",
            "validate_grouping_rules",
            "generate_correction_rules",
        ],
        "final_report": {
            "summary": "Rick.ai Research Loop completed successfully",
            "key_findings": ["Data structure validated", "Grouping patterns analyzed"],
            "error_patterns": ["Short group names detected"],
            "correction_rules": [
                {
                    "rule_id": "R003",
                    "title": "Стандартизация названий",
                    "priority": "medium",
                }
            ],
            "recommendations": ["Improve naming consistency"],
        },
        "quality_score": 85,
        "compliance_status": "completed",
    }

    print(f"Workflow Stages: {len(research_loop_structure['workflow_stages'])}")
    print(f"Quality Score: {research_loop_structure['quality_score']}%")
    print(f"Compliance Status: {research_loop_structure['compliance_status']}")

    # Show final report summary
    final_report = research_loop_structure["final_report"]
    print(f"Summary: {final_report['summary']}")
    print(f"Key Findings: {len(final_report['key_findings'])}")
    print(f"Error Patterns: {len(final_report['error_patterns'])}")
    print(f"Correction Rules: {len(final_report['correction_rules'])}")

    print("\n✅ Example completed successfully!")
    print("\n📚 Next steps:")
    print("1. Get real Rick.ai session cookie")
    print("2. Replace 'example_session_cookie_123' with real cookie")
    print("3. Add real company_alias, app_id, and widget_id")
    print("4. Run full research loop with real data")


if __name__ == "__main__":
    asyncio.run(main())
