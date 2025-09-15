#!/usr/bin/env python3
"""
TDD Red Phase: Тесты для build_jtbd.py
Преобразует гипотезу в CJM и JTBD-сценарии
"""

import unittest
import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/runner/workspace')

class TestBuildJTBD(unittest.TestCase):
    """Тесты для модуля построения JTBD."""
    
    def setUp(self):
        """Подготовка тестовых данных."""
        self.sample_hypothesis = {
            "id": "H20250527_001",
            "hypothesis": "Если реализовать MCP-сервер как оркестратор модулей, то мы получим устойчивую систему AI-инженерии",
            "output": "Репозитории с рабочим MCP-сервером",
            "outcome": "Повышение воспроизводимости в 3+ командах",
            "falsifiable_if": "Команды продолжают пропускать критические шаги"
        }
    
    def test_jtbd_generation_from_hypothesis(self):
        """ТЕСТ: Генерация JTBD сценариев из гипотезы."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import generate_jtbd_scenarios
            
            result = generate_jtbd_scenarios(self.sample_hypothesis)
            
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            
            # Проверяем структуру JTBD сценария
            first_scenario = result[0]
            self.assertIn("when", first_scenario)
            self.assertIn("role", first_scenario)
            self.assertIn("wants", first_scenario)
            self.assertIn("creates", first_scenario)
            
        except ImportError:
            self.fail("❌ RED PHASE: build_jtbd.py модуль не существует")
    
    def test_customer_journey_mapping(self):
        """ТЕСТ: Создание Customer Journey Map."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import create_customer_journey_map
            
            result = create_customer_journey_map(self.sample_hypothesis)
            
            self.assertIsInstance(result, dict)
            self.assertIn("stages", result)
            self.assertIn("touchpoints", result)
            self.assertIn("pain_points", result)
            self.assertIn("opportunities", result)
            
        except ImportError:
            self.fail("❌ RED PHASE: create_customer_journey_map не реализован")
    
    def test_jtbd_md_output(self):
        """ТЕСТ: Сохранение JTBD в jtbd.md файл."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import save_jtbd_md
            
            jtbd_data = {
                "scenarios": [
                    {
                        "when": "Разрабатываю AI-систему",
                        "role": "AI-инженер",
                        "wants": "воспроизводимый процесс",
                        "creates": "надежную систему"
                    }
                ],
                "customer_journey": {
                    "stages": ["Discovery", "Implementation", "Validation"],
                    "pain_points": ["Непредсказуемость", "Ошибки в процессе"]
                }
            }
            
            output_path = "/tmp/test_jtbd.md"
            result = save_jtbd_md(jtbd_data, output_path)
            
            self.assertTrue(result)
            self.assertTrue(Path(output_path).exists())
            
            # Проверяем что файл содержит markdown структуру
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("# JTBD", content)
                self.assertIn("## Сценарии", content)
                
        except ImportError:
            self.fail("❌ RED PHASE: save_jtbd_md не реализован")
    
    def test_jtbd_standard_compliance(self):
        """ТЕСТ: Соответствие стандарту jtbd.standard.md."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import validate_jtbd_standard
            
            valid_jtbd = {
                "scenarios": [
                    {
                        "when": "Ситуация",
                        "role": "Роль пользователя",
                        "wants": "Желаемый результат",
                        "creates": "Создаваемая ценность"
                    }
                ]
            }
            
            invalid_jtbd = {
                "scenarios": [
                    {
                        "when": "Ситуация"
                        # Отсутствуют обязательные поля
                    }
                ]
            }
            
            self.assertTrue(validate_jtbd_standard(valid_jtbd))
            self.assertFalse(validate_jtbd_standard(invalid_jtbd))
            
        except ImportError:
            self.fail("❌ RED PHASE: validate_jtbd_standard не реализован")
    
    def test_mcp_command_integration(self):
        """ТЕСТ: Интеграция с MCP командной системой."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import build_jtbd_command
            
            request = {
                "hypothesis_data": self.sample_hypothesis,
                "output_path": "/tmp/test_jtbd.md"
            }
            
            result = build_jtbd_command(request)
            
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertIn("jtbd_scenarios", result)
            self.assertIn("output_file", result)
            
        except ImportError:
            self.fail("❌ RED PHASE: build_jtbd_command не реализован")
    
    def test_protocol_completion_integration(self):
        """ТЕСТ: Интеграция с Protocol Completion."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import build_jtbd_command
            from advising_platform.src.mcp.protocol_completion import protocol_manager
            
            # Очищаем лог операций
            protocol_manager.operations_log = []
            
            request = {"hypothesis_data": self.sample_hypothesis}
            result = build_jtbd_command(request)
            
            # Проверяем что операция залогирована
            self.assertGreater(len(protocol_manager.operations_log), 0)
            
            last_operation = protocol_manager.operations_log[-1]
            self.assertEqual(last_operation["command"], "build-jtbd")
            
        except ImportError:
            self.fail("❌ RED PHASE: Protocol Completion не интегрирован")
    
    def test_trigger_next_steps(self):
        """ТЕСТ: Автоматический триггер следующих шагов."""
        try:
            from advising_platform.src.mcp.modules.build_jtbd import build_jtbd_command
            
            request = {"hypothesis_data": self.sample_hypothesis}
            result = build_jtbd_command(request)
            
            # Проверяем что предлагаются следующие шаги
            self.assertIn("next_steps", result)
            self.assertIn("write_prd", result["next_steps"])
            
        except ImportError:
            self.fail("❌ RED PHASE: trigger_next_steps не реализован")

if __name__ == "__main__":
    print("🔴 RED PHASE: Тесты для build_jtbd.py")
    print("Ожидается что все тесты провалятся - это нормально!")
    print("=" * 60)
    
    unittest.main(verbosity=2)