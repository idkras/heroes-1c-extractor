#!/usr/bin/env python3
"""
Registry Standard Compliance Checker
Проверяет соответствие всех MCP workflow Registry Standard
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'mcp' / 'modules'))

from documentation_validator import MCPDocumentationValidator


def main():
    """Основная функция проверки Registry Standard compliance"""
    validator = MCPDocumentationValidator()
    
    print("📋 Проверка соответствия Registry Standard...")
    
    # Запускаем проверку Registry Standard compliance
    registry_result = validator._validate_registry_standard_compliance()
    
    if registry_result['status'] == 'passed':
        print("✅ Все workflow соответствуют Registry Standard")
        
        workflow_count = len(registry_result['workflows'])
        print(f"📊 Проверено workflow: {workflow_count}")
        
        return 0
        
    else:
        print("❌ Обнаружены нарушения Registry Standard:")
        
        failed_workflows = []
        for workflow_name, workflow_result in registry_result['workflows'].items():
            if workflow_result['status'] != 'passed':
                failed_workflows.append(workflow_name)
                
                print(f"\n   📋 {workflow_name}:")
                checks = workflow_result.get('checks', {})
                
                if not checks.get('has_input_stage'):
                    print("      - Отсутствует INPUT STAGE")
                    
                if not checks.get('has_output_stage'):
                    print("      - Отсутствует OUTPUT STAGE")
                    
                reflection_info = checks.get('reflection_checkpoints', {})
                if not reflection_info.get('has_minimum'):
                    count = reflection_info.get('count', 0)
                    print(f"      - Недостаточно [reflection] checkpoints: {count} (требуется минимум 1)")
                    
                if not checks.get('has_input_data_types'):
                    print("      - Отсутствуют типы данных в INPUT STAGE")
                    
                step_info = checks.get('step_structure', {})
                if not step_info.get('has_steps'):
                    count = step_info.get('count', 0)
                    print(f"      - Отсутствует структура STEP: {count}")
        
        print(f"\n❌ Провалилось workflow: {len(failed_workflows)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())