#!/usr/bin/env python3
"""
Test Rick.ai MCP Integration
Тестирование интеграции Rick.ai с MCP сервером
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.rick_ai.workflow import RickAIWorkflow


async def test_rick_ai_workflow():
    """Test Rick.ai workflow functionality"""
    print("🧪 Testing Rick.ai Workflow Integration")
    print("=" * 50)

    # Initialize workflow
    workflow = RickAIWorkflow()

    # Test 1: Basic workflow initialization
    print("\n1️⃣ Testing workflow initialization")
    print("-" * 30)

    assert workflow.workflow_name == "rick-ai-research-loop"
    assert workflow.version == "v1.0"
    assert workflow.standard_compliance == "Keyword Campaign Grouping Standard v1.0"
    print("✅ Workflow initialization: PASSED")

    # Test 2: Test connection
    print("\n2️⃣ Testing connection")
    print("-" * 30)

    result = await workflow.execute(
        {"command": "authenticate", "session_cookie": "test_session_cookie_123"}
    )

    assert result["status"] == "success"
    assert "Аутентификация успешна" in result["message"]
    print("✅ Authentication test: PASSED")

    # Test 3: Analyze grouping data
    print("\n3️⃣ Testing analysis functionality")
    print("-" * 30)

    sample_widget_groups = [
        {"name": "Organic Traffic", "id": "group_1"},
        {"name": "Paid Advertising", "id": "group_2"},
        {"name": "Social Media", "id": "group_3"},
    ]

    sample_widget_data = {
        "data": {"visits": 1000, "conversions": 50},
        "metadata": {"version": "1.0"},
        "config": {"settings": "default"},
    }

    analysis_result = await workflow.execute(
        {
            "command": "analyze_grouping_data",
            "widget_data": sample_widget_data,
            "widget_groups": sample_widget_groups,
        }
    )

    assert analysis_result["status"] == "success"
    assert "Анализ завершен" in analysis_result["message"]
    print("✅ Analysis test: PASSED")

    # Test 4: Validate grouping rules
    print("\n4️⃣ Testing validation functionality")
    print("-" * 30)

    validation_result = await workflow.execute(
        {
            "command": "validate_grouping_rules",
            "analysis_results": analysis_result.get("data", {}),
        }
    )

    assert validation_result["status"] == "success"
    assert "Валидация завершена" in validation_result["message"]
    print("✅ Validation test: PASSED")

    # Test 5: Generate correction rules
    print("\n5️⃣ Testing correction rules generation")
    print("-" * 30)

    correction_result = await workflow.execute(
        {
            "command": "generate_correction_rules",
            "validation_results": validation_result.get("data", {}),
            "analysis_results": analysis_result.get("data", {}),
        }
    )

    assert correction_result["status"] == "success"
    assert "Сгенерировано" in correction_result["message"]
    print("✅ Correction rules test: PASSED")

    print("\n🎉 All Rick.ai workflow tests PASSED!")
    return True


def test_mcp_integration():
    """Test MCP integration by importing and checking commands"""
    print("\n🔧 Testing MCP Integration")
    print("=" * 50)

    try:
        # Import MCP server module
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from heroes_mcp.src.heroes_mcp_server import rick_ai_workflow

        # Check if workflow is loaded
        assert rick_ai_workflow is not None
        assert hasattr(rick_ai_workflow, "workflow_name")
        assert rick_ai_workflow.workflow_name == "rick-ai-research-loop"

        print("✅ MCP integration: PASSED")
        print("✅ Rick.ai workflow loaded in MCP server")

        return True

    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Rick.ai MCP Integration Test Suite")
    print("=" * 60)

    # Test workflow functionality
    workflow_success = await test_rick_ai_workflow()

    # Test MCP integration
    mcp_success = test_mcp_integration()

    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Workflow Tests: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
    print(f"MCP Integration: {'✅ PASSED' if mcp_success else '❌ FAILED'}")

    if workflow_success and mcp_success:
        print("\n🎉 All tests PASSED! Rick.ai integration is ready.")
        return True
    else:
        print("\n❌ Some tests FAILED. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
