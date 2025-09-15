#!/usr/bin/env python3
"""
E2E Test: Полный цикл MCP от гипотезы до результата

JTBD: Я хочу протестировать полный workflow MCP,
чтобы убедиться что все модули работают вместе.
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys
import os

sys.path.insert(0, '/home/runner/workspace')

class TestFullE2ECycle:
    """End-to-End тесты полного MCP цикла."""
    
    def test_hypothesis_to_dashboard_workflow(self):
        """Тест: Полный workflow от гипотезы до dashboard."""
        # Arrange - входные данные реальной гипотезы
        hypothesis_input = """
        Гипотеза: Если реализовать MCP-оркестратор с автоматическим логированием и анализом 5 почему, 
        то мы получим устойчивую, воспроизводимую систему AI-инженерии.
        
        Output: Функциональный MCP-сервер с модулями полного цикла разработки
        Outcome: Повышение воспроизводимости процессов на 80%, снижение забытых шагов, рост доверия к AI-процессам в 3+ командах
        Falsifiable if: Команды продолжают пропускать критические шаги или время решения инцидентов не сокращается
        Metrics: missed_steps_count, workflow_completion_rate, incident_resolution_time
        """
        
        # Act - выполняем полный цикл
        
        # 1. Form Hypothesis
        from advising_platform.src.mcp.modules.form_hypothesis import FormHypothesis
        hypothesis_processor = FormHypothesis()
        hypothesis_result = hypothesis_processor.process(hypothesis_input)
        
        # Assert - проверяем результат формирования гипотезы
        assert hypothesis_result["id"].startswith("H")
        assert "MCP-оркестратор" in hypothesis_result["title"]
        assert len(hypothesis_result["metrics"]) >= 3
        assert hypothesis_result["status"] == "draft"
        
        # 2. Build JTBD (пока тестируем что модуль будет создан)
        with pytest.raises(ImportError):
            from advising_platform.src.mcp.modules.build_jtbd import BuildJTBD
        
        # 3. Write PRD (пока тестируем что модуль будет создан)
        with pytest.raises(ImportError):
            from advising_platform.src.mcp.modules.write_prd import WritePRD
        
        # 4. Red Phase Tests (пока тестируем что модуль будет создан)
        with pytest.raises(ImportError):
            from advising_platform.src.mcp.modules.red_phase_tests import RedPhaseTests
        
        # Assert - проверяем что workflow логируется
        assert hypothesis_result is not None
        print(f"✅ E2E Test: Hypothesis {hypothesis_result['id']} processed successfully")
    
    def test_mcp_orchestrator_integration(self):
        """Тест: Интеграция с оркестратором MCP."""
        # Arrange
        workflow_config = {
            "steps": [
                {"module": "form_hypothesis", "required": True},
                {"module": "build_jtbd", "required": True},
                {"module": "write_prd", "required": True},
                {"module": "red_phase_tests", "required": True},
                {"module": "implement_feature", "required": True}
            ]
        }
        
        # Act - создаем оркестратор
        from advising_platform.src.mcp.mcp_orchestrator import MCPOrchestrator
        orchestrator = MCPOrchestrator(workflow_config)
        
        # Assert - проверяем что оркестратор создан
        assert orchestrator is not None
        assert len(orchestrator.config["steps"]) == 5
        
        # Проверяем статус workflow
        status = orchestrator.get_workflow_status()
        assert "current_step" in status
        assert "progress_percent" in status
    
    def test_incident_creation_on_missed_step(self):
        """Тест: Создание инцидента при пропущенном шаге."""
        # Arrange - симулируем пропущенный report_progress
        workflow_state = {
            "current_step": "implement_feature",
            "last_report": None,
            "expected_report_time": "2025-05-27T10:00:00"
        }
        
        # Act & Assert - модуль пока не создан
        with pytest.raises(ImportError):
            from advising_platform.src.mcp.modules.root_cause_analysis import create_incident_for_missed_step
            incident = create_incident_for_missed_step(workflow_state)
    
    def test_dashboard_shows_real_operations(self):
        """Тест: Dashboard показывает реальные операции."""
        # Act - проверяем что dashboard интегрирован
        from advising_platform.src.mcp.mcp_dashboard import mcp_dashboard
        
        dashboard_data = mcp_dashboard.get_live_dashboard()
        
        # Assert - должны быть реальные операции
        assert "stats" in dashboard_data
        assert dashboard_data["stats"]["total_commands"] > 0
        
        # Проверяем что есть recent_commands
        assert "recent_commands" in dashboard_data
        assert len(dashboard_data["recent_commands"]) > 0
        
        print(f"✅ Dashboard shows {dashboard_data['stats']['total_commands']} real operations")


class TestMCPModulesContract:
    """Contract тесты для модулей MCP."""
    
    def test_all_modules_implement_standard_interface(self):
        """Тест: Все модули реализуют стандартный интерфейс."""
        # Arrange - список модулей которые должны быть созданы
        required_modules = [
            "form_hypothesis",
            "build_jtbd", 
            "write_prd",
            "red_phase_tests",
            "implement_feature",
            "run_tests",
            "evaluate_outcome",
            "falsify_or_confirm",
            "root_cause_analysis"
        ]
        
        existing_modules = ["form_hypothesis"]  # Уже созданные
        
        # Act & Assert
        for module_name in required_modules:
            if module_name in existing_modules:
                # Проверяем созданные модули
                module_path = f"advising_platform.src.mcp.modules.{module_name}"
                try:
                    __import__(module_path)
                    print(f"✅ Module {module_name} exists")
                except ImportError:
                    pytest.fail(f"Module {module_name} should exist but doesn't")
            else:
                # Проверяем что остальные модули пока не созданы (Red Phase)
                with pytest.raises(ImportError):
                    __import__(f"advising_platform.src.mcp.modules.{module_name}")
                print(f"🔴 Module {module_name} correctly not implemented yet (Red Phase)")


if __name__ == "__main__":
    # Запуск E2E тестов
    pytest.main([__file__, "-v", "-s"])