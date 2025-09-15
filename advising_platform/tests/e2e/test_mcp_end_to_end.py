#!/usr/bin/env python3
"""
End-to-End Tests для Standards-MCP Server

JTBD: Я (E2E тест) хочу проверить полный пользовательский workflow MCP сервера,
чтобы убедиться что "тесты проходят = пользователь видит результат".

Автор: AI Assistant
Дата: 26 May 2025
"""

import unittest
import subprocess
import json
import time
from pathlib import Path

class TestStandardsMCPEndToEnd(unittest.TestCase):
    """
    JTBD: Я (E2E тест) хочу проверить полный путь от MCP запроса до ответа,
    чтобы валидировать реальный пользовательский опыт.
    """
    
    @classmethod
    def setUpClass(cls):
        """Настройка E2E тестовой среды."""
        cls.project_root = Path(__file__).parent.parent.parent
        
    def test_e2e_complete_standards_resolution_workflow(self):
        """
        JTBD: Я (пользователь) хочу получить стандарт по логическому адресу,
        чтобы использовать его в разработке.
        """
        backend_script = self.project_root / "src" / "mcp" / "python_backends" / "standards_resolver.py"
        test_args = {
            "address": "abstract://standard:tdd",
            "format": "summary"
        }
        
        result = subprocess.run([
            "python3", str(backend_script), json.dumps(test_args)
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 0, "E2E workflow должен завершиться успешно")
        
        response = json.loads(result.stdout)
        self.assertTrue(response.get("success", False), "E2E операция должна быть успешной")
        self.assertIn("address", response, "Ответ должен содержать address")
        self.assertIn("content", response, "Ответ должен содержать content")

    def test_e2e_performance_requirements(self):
        """
        JTBD: Я (система) хочу обеспечить производительность <200ms для MCP операций,
        чтобы соответствовать пользовательским ожиданиям.
        """
        backend_script = self.project_root / "src" / "mcp" / "python_backends" / "standards_resolver.py"
        test_args = {"address": "abstract://standard:tdd", "format": "summary"}
        
        # Выполняем 3 теста производительности
        durations = []
        for i in range(3):
            start_time = time.time()
            
            result = subprocess.run([
                "python3", str(backend_script), json.dumps(test_args)
            ], capture_output=True, text=True, timeout=10)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            if result.returncode == 0:
                durations.append(duration_ms)
        
        self.assertGreater(len(durations), 0, "Должен быть хотя бы один успешный тест")
        
        avg_duration = sum(durations) / len(durations)
        self.assertLess(avg_duration, 200, 
                       f"Среднее время отклика {avg_duration:.1f}ms должно быть <200ms")

if __name__ == "__main__":
    unittest.main(verbosity=2)