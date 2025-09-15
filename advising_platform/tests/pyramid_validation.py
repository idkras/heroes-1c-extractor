#!/usr/bin/env python3
"""
Быстрая валидация Testing Pyramid для Standards-MCP

JTBD: Я (валидатор) хочу проверить соблюдение Testing Pyramid,
чтобы предотвратить "Unit Tunnel Vision" anti-pattern.
"""

import subprocess
import os
from pathlib import Path

def validate_mcp_testing_pyramid():
    """Проверяет Testing Pyramid для MCP сервера."""
    project_root = Path(__file__).parent.parent
    os.environ['PYTHONPATH'] = '/home/runner/workspace'
    
    results = {
        "unit_tests": False,
        "integration_tests": False,
        "e2e_tests": False,
        "pyramid_compliance": False,
        "anti_patterns": []
    }
    
    # Проверяем Unit тесты
    unit_test = project_root / "tests" / "unit" / "test_unified_key_resolver_tdd.py"
    if unit_test.exists():
        result = subprocess.run([
            "python", "-m", "pytest", str(unit_test), "-q"
        ], capture_output=True, cwd=project_root)
        results["unit_tests"] = result.returncode == 0
    
    # Проверяем Integration тесты
    integration_dir = project_root / "tests" / "integration"
    if integration_dir.exists():
        result = subprocess.run([
            "python", "-m", "pytest", str(integration_dir), "-q", "--tb=no"
        ], capture_output=True, cwd=project_root)
        results["integration_tests"] = result.returncode == 0
    
    # Проверяем E2E тесты
    e2e_dir = project_root / "tests" / "e2e"
    if e2e_dir.exists():
        results["e2e_tests"] = True  # Директория существует
    
    # Анализируем соблюдение пирамиды
    if results["unit_tests"] and not results["integration_tests"]:
        results["anti_patterns"].append("Unit Tunnel Vision")
    
    results["pyramid_compliance"] = (
        results["unit_tests"] and 
        results["integration_tests"] and 
        len(results["anti_patterns"]) == 0
    )
    
    return results

if __name__ == "__main__":
    results = validate_mcp_testing_pyramid()
    
    print("🔍 Testing Pyramid Validation")
    print("=" * 30)
    print(f"✅ Unit Tests: {'PASS' if results['unit_tests'] else 'FAIL'}")
    print(f"✅ Integration Tests: {'PASS' if results['integration_tests'] else 'FAIL'}")
    print(f"✅ E2E Tests: {'EXISTS' if results['e2e_tests'] else 'MISSING'}")
    print(f"🎯 Pyramid Compliance: {'YES' if results['pyramid_compliance'] else 'NO'}")
    
    if results["anti_patterns"]:
        print(f"⚠️  Anti-patterns: {', '.join(results['anti_patterns'])}")
    else:
        print("✅ No anti-patterns detected")