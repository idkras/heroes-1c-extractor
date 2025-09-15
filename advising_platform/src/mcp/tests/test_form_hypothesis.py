#!/usr/bin/env python3
"""
TDD Red Phase: Тесты для form_hypothesis.py
Пишем тесты ПЕРЕД реализацией согласно mcp.todo
"""

import unittest
import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

class TestFormHypothesis(unittest.TestCase):
    """Тесты для модуля формирования гипотез."""
    
    def setUp(self):
        """Подготовка тестовых данных."""
        self.sample_hypothesis_text = """
        Если реализовать MCP-сервер как оркестратор модулей с поддержкой логирования,
        то мы получим устойчивую, воспроизводимую систему AI-инженерии.
        
        Output: Репозитории с рабочим MCP-сервером
        Outcome: Повышение воспроизводимости в 3+ командах
        Falsifiable if: Команды продолжают пропускать критические шаги
        """
        
        self.expected_hypothesis_structure = {
            "hypothesis": str,
            "output": str,
            "outcome": str,
            "falsifiable_if": str,
            "metrics": list,
            "timestamp": str,
            "id": str
        }
    
    def test_hypothesis_parser_basic(self):
        """ТЕСТ: Парсинг гипотезы из текста в JSON."""
        # Этот тест должен ПРОВАЛИТЬСЯ до реализации
        try:
            from advising_platform.src.mcp.modules.form_hypothesis import parse_hypothesis_text
            result = parse_hypothesis_text(self.sample_hypothesis_text)
            
            # Проверяем структуру
            self.assertIsInstance(result, dict)
            self.assertIn("hypothesis", result)
            self.assertIn("output", result)
            self.assertIn("outcome", result)
            self.assertIn("falsifiable_if", result)
            
        except ImportError:
            self.fail("❌ RED PHASE: form_hypothesis.py модуль не существует - это ожидаемо!")
    
    def test_hypothesis_validation(self):
        """ТЕСТ: Валидация структуры гипотезы."""
        try:
            from advising_platform.src.mcp.modules.form_hypothesis import validate_hypothesis
            
            valid_hypothesis = {
                "hypothesis": "Если X, то Y",
                "output": "Конкретный результат",
                "outcome": "Измеримый эффект",
                "falsifiable_if": "Условие провала"
            }
            
            invalid_hypothesis = {
                "hypothesis": "Если X, то Y"
                # Отсутствуют обязательные поля
            }
            
            self.assertTrue(validate_hypothesis(valid_hypothesis))
            self.assertFalse(validate_hypothesis(invalid_hypothesis))
            
        except ImportError:
            self.fail("❌ RED PHASE: validate_hypothesis не реализован")
    
    def test_hypothesis_json_output(self):
        """ТЕСТ: Сохранение гипотезы в hypothesis.json."""
        try:
            from advising_platform.src.mcp.modules.form_hypothesis import save_hypothesis_json
            
            hypothesis_data = {
                "hypothesis": "Тестовая гипотеза",
                "output": "Тестовый output",
                "outcome": "Тестовый outcome",
                "falsifiable_if": "Тестовое условие"
            }
            
            output_path = "/tmp/test_hypothesis.json"
            result = save_hypothesis_json(hypothesis_data, output_path)
            
            self.assertTrue(result)
            self.assertTrue(Path(output_path).exists())
            
            # Проверяем что JSON валидный
            with open(output_path, 'r') as f:
                loaded_data = json.load(f)
                self.assertEqual(loaded_data["hypothesis"], hypothesis_data["hypothesis"])
            
        except ImportError:
            self.fail("❌ RED PHASE: save_hypothesis_json не реализован")
    
    def test_mcp_command_integration(self):
        """ТЕСТ: Интеграция с MCP командной системой."""
        try:
            from advising_platform.src.mcp.modules.form_hypothesis import form_hypothesis_command
            
            request = {
                "text": self.sample_hypothesis_text,
                "output_path": "/tmp/test_hypothesis.json"
            }
            
            result = form_hypothesis_command(request)
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertIn("hypothesis_id", result)
            self.assertIn("output_file", result)
            
        except ImportError:
            self.fail("❌ RED PHASE: form_hypothesis_command не реализован")
    
    def test_protocol_completion_integration(self):
        """ТЕСТ: Интеграция с Protocol Completion."""
        try:
            from advising_platform.src.mcp.modules.form_hypothesis import form_hypothesis_command
            from advising_platform.src.mcp.protocol_completion import protocol_manager
            
            # Очищаем лог операций
            protocol_manager.operations_log = []
            
            request = {"text": self.sample_hypothesis_text}
            result = form_hypothesis_command(request)
            
            # Проверяем что операция залогирована
            self.assertGreater(len(protocol_manager.operations_log), 0)
            
            last_operation = protocol_manager.operations_log[-1]
            self.assertEqual(last_operation["command"], "form-hypothesis")
            
        except ImportError:
            self.fail("❌ RED PHASE: Protocol Completion не интегрирован")
    
    def test_trigger_next_steps(self):
        """ТЕСТ: Автоматический триггер следующих шагов."""
        try:
            from advising_platform.src.mcp.modules.form_hypothesis import form_hypothesis_command
            
            request = {"text": self.sample_hypothesis_text}
            result = form_hypothesis_command(request)
            
            # Проверяем что предлагаются следующие шаги
            self.assertIn("next_steps", result)
            self.assertIn("build_jtbd", result["next_steps"])
            
        except ImportError:
            self.fail("❌ RED PHASE: trigger_next_steps не реализован")

if __name__ == "__main__":
    print("🔴 RED PHASE: Запуск тестов ПЕРЕД реализацией")
    print("Ожидается что все тесты провалятся - это нормально!")
    print("=" * 60)
    
    unittest.main(verbosity=2)