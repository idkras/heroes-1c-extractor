"""
E2E тесты для валидации полного MCP workflow интеграции.
Проверяет что AI ассистент действительно использует MCP команды.
"""

import json
import subprocess
import pytest
from pathlib import Path
import tempfile
import os

class TestMCPWorkflowIntegration:
    """E2E тесты для MCP workflow интеграции"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.test_dir = Path("/home/runner/workspace")
        self.mcp_backends = self.test_dir / "advising_platform" / "src" / "mcp" / "python_backends"
        
    def test_create_task_mcp_command(self):
        """Тест MCP команды create_task"""
        cmd = [
            "python", 
            str(self.mcp_backends / "create_task.py"),
            json.dumps({
                "title": "Test Task",
                "description": "Test task creation via MCP",
                "priority": "medium"
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        response = json.loads(result.stdout)
        assert response["success"] == True
        assert "TASK_" in response["task"]["id"]
        assert response["task"]["title"] == "Test Task"
        
    def test_create_incident_mcp_command(self):
        """Тест MCP команды create_incident"""
        cmd = [
            "python",
            str(self.mcp_backends / "create_incident.py"),
            json.dumps({
                "title": "Test Incident",
                "description": "Test incident creation via MCP",
                "error": "Sample error for testing",
                "priority": "high"
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        response = json.loads(result.stdout)
        assert response["success"] == True
        assert "I" in response["incident"]["id"]
        assert response["incident"]["title"] == "Test Incident"
        
    def test_validate_compliance_mcp_command(self):
        """Тест MCP команды validate_compliance"""
        cmd = [
            "python",
            str(self.mcp_backends / "validate_compliance.py"),
            json.dumps({
                "solution": "Структурированное решение:\n1. Анализ проблемы\n2. Разработка решения\n3. Тестирование\n4. Внедрение\n5. Мониторинг результатов",
                "standards": ["quality", "structure"],
                "type": "solution_validation"
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        response = json.loads(result.stdout)
        assert response["success"] == True
        assert "compliance_score" in response
        assert response["compliance_score"] > 0
        
    def test_form_hypothesis_workflow(self):
        """Тест полного workflow form_hypothesis"""
        # Используем Python код для тестирования
        cmd = [
            "python", "-c", 
            """
import sys
sys.path.insert(0, '/home/runner/workspace')
from advising_platform.src.mcp.modules.form_hypothesis import FormHypothesis

processor = FormHypothesis()
result = processor.process('Тестовая гипотеза для E2E теста')
print('SUCCESS' if result else 'FAILED')
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "SUCCESS" in result.stdout
        
    def test_build_jtbd_workflow(self):
        """Тест полного workflow build_jtbd"""
        cmd = [
            "python", "-c",
            """
import sys
sys.path.insert(0, '/home/runner/workspace')
from advising_platform.src.mcp.modules.build_jtbd import BuildJTBD

processor = BuildJTBD()
hypothesis_data = {
    'id': 'TEST_H001', 
    'title': 'Test Hypothesis',
    'description': 'Test description',
    'output': 'Test output',
    'outcome': 'Test outcome'
}
result = processor.process(hypothesis_data)
print('SUCCESS' if result and 'jtbd' in result else 'FAILED')
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "SUCCESS" in result.stdout
        
    def test_mcp_commands_visibility(self):
        """Тест видимости MCP команд - ключевое требование"""
        # Проверяем что все MCP команды выводят результаты в stdout
        mcp_commands = [
            "create_task.py",
            "create_incident.py", 
            "validate_compliance.py"
        ]
        
        for cmd_file in mcp_commands:
            cmd_path = self.mcp_backends / cmd_file
            assert cmd_path.exists(), f"MCP команда {cmd_file} не найдена"
            
            # Проверяем что команда может быть запущена
            result = subprocess.run(
                ["python", str(cmd_path)], 
                capture_output=True, 
                text=True,
                cwd=self.test_dir
            )
            
            # Команда должна выводить help/описание при запуске без аргументов
            assert len(result.stdout.strip()) > 0, f"Команда {cmd_file} не выводит информацию"
            
    def test_workflow_integration_completeness(self):
        """Тест полноты интеграции workflow"""
        # Проверяем что создан полный набор MCP команд
        required_commands = [
            "create_task.py",
            "create_incident.py",
            "validate_compliance.py",
            "standards_resolver.py"
        ]
        
        for cmd in required_commands:
            cmd_path = self.mcp_backends / cmd
            assert cmd_path.exists(), f"Необходимая MCP команда {cmd} отсутствует"
            
        # Проверяем что созданы workflow модули
        workflow_modules = [
            "form_hypothesis.py",
            "build_jtbd.py", 
            "write_prd.py",
            "red_phase_tests.py"
        ]
        
        modules_dir = self.test_dir / "advising_platform" / "src" / "mcp" / "modules"
        for module in workflow_modules:
            module_path = modules_dir / module
            assert module_path.exists(), f"Необходимый workflow модуль {module} отсутствует"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])