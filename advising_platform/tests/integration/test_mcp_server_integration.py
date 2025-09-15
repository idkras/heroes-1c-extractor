#!/usr/bin/env python3
"""
Integration Tests для Standards-MCP Server

JTBD: Я (тестовая система) хочу проверить взаимодействие MCP сервера с Python backends,
чтобы убедиться в корректности полного workflow.

Автор: AI Assistant
Дата: 26 May 2025
"""

import unittest
import subprocess
import json
import time
import os
import signal
from pathlib import Path
from typing import Dict, Any

class TestStandardsMCPIntegration(unittest.TestCase):
    """
    JTBD: Я (интеграционный тест) хочу проверить взаимодействие всех компонентов MCP,
    чтобы выявить проблемы интеграции до production.
    """
    
    @classmethod
    def setUpClass(cls):
        """Настройка тестовой среды."""
        cls.mcp_server_process = None
        cls.project_root = Path(__file__).parent.parent.parent
        cls.mcp_dir = cls.project_root / "src" / "mcp"
        
    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов."""
        if cls.mcp_server_process:
            cls.mcp_server_process.terminate()
            cls.mcp_server_process.wait()

    def test_integration_standards_resolver_with_unified_key_resolver(self):
        """
        JTBD: Я (тест) хочу проверить интеграцию standards_resolver с UnifiedKeyResolver,
        чтобы убедиться в корректности резолвинга адресов.
        """
        # Arrange: подготовка тестовых данных
        test_args = {
            "address": "abstract://standard:tdd",
            "format": "summary"
        }
        
        # Act: вызов Python backend напрямую
        backend_script = self.mcp_dir / "python_backends" / "standards_resolver.py"
        result = subprocess.run([
            "python3", str(backend_script), json.dumps(test_args)
        ], capture_output=True, text=True, timeout=10)
        
        # Assert: проверка результата
        self.assertEqual(result.returncode, 0, f"Backend должен выполниться успешно. Stderr: {result.stderr}")
        
        response = json.loads(result.stdout)
        self.assertTrue(response.get("success", False), f"Операция должна быть успешной: {response}")
        self.assertIn("address", response, "Ответ должен содержать address")
        self.assertIn("content", response, "Ответ должен содержать content")

    def test_integration_all_mcp_backends_respond(self):
        """
        JTBD: Я (тест) хочу проверить что все MCP backends отвечают корректно,
        чтобы убедиться в готовности системы к работе.
        """
        backends_tests = [
            ("standards_resolver.py", {"address": "abstract://standard:tdd", "format": "summary"}),
            ("standards_suggester.py", {"jtbd": "Я хочу создать API", "taskType": "development"}),
            ("compliance_checker.py", {"content": "Test content", "strictMode": False}),
            ("standards_navigator.py", {"query": "TDD testing", "category": "development"})
        ]
        
        for backend_name, test_args in backends_tests:
            with self.subTest(backend=backend_name):
                # Act: вызов backend
                backend_script = self.mcp_dir / "python_backends" / backend_name
                result = subprocess.run([
                    "python3", str(backend_script), json.dumps(test_args)
                ], capture_output=True, text=True, timeout=15)
                
                # Assert: проверка корректного ответа
                self.assertEqual(result.returncode, 0, 
                               f"{backend_name} должен выполниться успешно. Stderr: {result.stderr}")
                
                try:
                    response = json.loads(result.stdout)
                    self.assertIsInstance(response, dict, f"{backend_name} должен возвращать JSON объект")
                    self.assertIn("success", response, f"{backend_name} должен содержать поле success")
                except json.JSONDecodeError as e:
                    self.fail(f"{backend_name} вернул некорректный JSON: {result.stdout}")

    def test_integration_mcp_dashboard_logging(self):
        """
        JTBD: Я (тест) хочу проверить интеграцию MCP Dashboard с операциями,
        чтобы убедиться в корректности логирования команд.
        """
        # Arrange: подготовка тестовых данных для логирования
        test_args = {
            "tool_name": "standards-resolver",
            "parameters": {"address": "test://address", "format": "summary"},
            "result": {"success": True, "content": "test content"},
            "duration_ms": 50.0,
            "status": "success",
            "error_message": ""
        }
        
        # Act: вызов dashboard logger
        logger_script = self.mcp_dir / "python_backends" / "mcp_dashboard_logger.py"
        result = subprocess.run([
            "python3", str(logger_script), json.dumps(test_args)
        ], capture_output=True, text=True, timeout=5)
        
        # Assert: проверка успешного логирования
        self.assertEqual(result.returncode, 0, f"Dashboard logger должен работать. Stderr: {result.stderr}")
        
        response = json.loads(result.stdout)
        self.assertTrue(response.get("success", False), "Логирование должно быть успешным")
        self.assertTrue(response.get("logged", False), "Операция должна быть залогирована")

    def test_integration_cache_synchronization(self):
        """
        JTBD: Я (тест) хочу проверить синхронизацию кеша с операциями MCP,
        чтобы убедиться в корректности работы с кешем.
        """
        # Проверяем что кеш доступен и работает
        cache_test_script = self.project_root / "tests" / "integration" / "test_cache_sync_tdd.py"
        
        if cache_test_script.exists():
            result = subprocess.run([
                "python3", "-m", "pytest", str(cache_test_script), "-v"
            ], capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            # Проверяем что кеш-тесты проходят
            self.assertEqual(result.returncode, 0, 
                           f"Cache sync тесты должны проходить: {result.stdout}")

class TestStandardsMCPContract(unittest.TestCase):
    """
    JTBD: Я (contract тест) хочу проверить соблюдение MCP протокола,
    чтобы убедиться в совместимости с MCP стандартом.
    """
    
    def test_contract_mcp_tool_response_format(self):
        """
        JTBD: Я (тест) хочу проверить что все MCP tools возвращают корректный формат,
        чтобы соблюсти MCP protocol requirements.
        """
        required_fields = ["success"]
        
        # Тестируем каждый backend на соответствие контракту
        backends = [
            ("standards_resolver.py", {"address": "abstract://standard:tdd", "format": "summary"}),
            ("standards_suggester.py", {"jtbd": "Test JTBD", "taskType": "development"}),
            ("compliance_checker.py", {"content": "Test", "strictMode": False}),
            ("standards_navigator.py", {"query": "test", "category": "development"})
        ]
        
        project_root = Path(__file__).parent.parent.parent
        mcp_dir = project_root / "src" / "mcp"
        
        for backend_name, test_args in backends:
            with self.subTest(backend=backend_name):
                backend_script = mcp_dir / "python_backends" / backend_name
                result = subprocess.run([
                    "python3", str(backend_script), json.dumps(test_args)
                ], capture_output=True, text=True, timeout=10)
                
                self.assertEqual(result.returncode, 0, f"{backend_name} должен выполниться")
                
                response = json.loads(result.stdout)
                
                # Проверяем обязательные поля MCP контракта
                for field in required_fields:
                    self.assertIn(field, response, 
                                f"{backend_name} должен содержать поле {field}")
                
                # Проверяем типы данных
                self.assertIsInstance(response["success"], bool,
                                    f"{backend_name}.success должно быть boolean")

if __name__ == "__main__":
    unittest.main(verbosity=2)