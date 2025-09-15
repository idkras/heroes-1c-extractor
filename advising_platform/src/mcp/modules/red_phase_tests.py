"""
MCP Module: Red Phase Tests
Генерация TDD тестов на основе PRD требований для цикла фальсификации

Использует аутентичные данные из PRD и JTBD для создания failing tests.
"""

import json
import duckdb
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def mcp_generate_red_phase_tests(prd_file: str, test_type: str = "integration") -> Dict[str, Any]:
    """
    MCP команда: generate-red-phase-tests
    Создает failing TDD тесты на основе PRD требований
    
    Args:
        prd_file: Путь к PRD документу
        test_type: Тип тестов (unit, integration, e2e)
        
    Returns:
        Сгенерированные TDD тесты в Red фазе
    """
    start_time = time.time()
    
    # Загружаем PRD данные
    prd_data = _load_prd_document(prd_file)
    if not prd_data:
        return {"error": f"Не удалось загрузить PRD из {prd_file}"}
    
    # Подключаемся к DuckDB для анализа требований
    conn = duckdb.connect(':memory:')
    
    # Создаем таблицу для анализа PRD требований
    conn.execute("""
        CREATE TABLE prd_requirements (
            feature_id TEXT,
            title TEXT,
            description TEXT,
            acceptance_criteria TEXT,
            priority TEXT,
            estimated_effort TEXT
        )
    """)
    
    # Загружаем PRD требования в DuckDB
    for feature in prd_data.get('prd_document', {}).get('features', []):
        criteria = json.dumps(feature.get('acceptance_criteria', []))
        conn.execute("""
            INSERT INTO prd_requirements VALUES (?, ?, ?, ?, ?, ?)
        """, [
            feature.get('feature_id', ''),
            feature.get('title', ''),
            feature.get('description', ''),
            criteria,
            feature.get('priority', 'Medium'),
            feature.get('estimated_effort', 'Unknown')
        ])
    
    # Генерируем тесты на основе требований
    test_analysis = _analyze_requirements_for_tests(conn, test_type)
    
    # Создаем failing tests (Red фаза TDD)
    red_tests = _generate_failing_tests(test_analysis, prd_data, test_type)
    
    conn.close()
    
    duration_ms = (time.time() - start_time) * 1000
    
    result = {
        "command": "mcp-generate-red-phase-tests",
        "timestamp": datetime.now().isoformat(),
        "source_prd": prd_file,
        "test_type": test_type,
        "generated_tests": red_tests,
        "test_analysis": test_analysis,
        "tdd_phase": "RED",
        "tests_count": len(red_tests.get('test_cases', [])),
        "coverage_metrics": {
            "features_covered": test_analysis.get('testable_features', 0),
            "acceptance_criteria_covered": test_analysis.get('total_criteria', 0),
            "priority_coverage": test_analysis.get('priority_distribution', {})
        },
        "duckdb_processing": True,
        "execution_time_ms": round(duration_ms, 2)
    }
    
    return result


def _load_prd_document(file_path: str) -> Dict[str, Any]:
    """Загружает PRD документ из файла"""
    try:
        prd_file = Path(file_path)
        if not prd_file.exists():
            print(f"⚠️ PRD файл не найден: {file_path}")
            return {}
        
        with open(prd_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки PRD: {e}")
        return {}


def _analyze_requirements_for_tests(conn: duckdb.DuckDBPyConnection, test_type: str) -> Dict[str, Any]:
    """Анализирует PRD требования для генерации тестов"""
    
    # Анализируем приоритеты
    priority_dist = conn.execute("""
        SELECT priority, COUNT(*) as count
        FROM prd_requirements 
        GROUP BY priority 
        ORDER BY CASE priority 
            WHEN 'High' THEN 1 
            WHEN 'Medium' THEN 2 
            ELSE 3 END
    """).fetchall()
    
    # Извлекаем тестируемые функции
    testable_features = conn.execute("""
        SELECT feature_id, title, description, acceptance_criteria, priority
        FROM prd_requirements 
        WHERE acceptance_criteria != '[]'
        ORDER BY CASE priority 
            WHEN 'High' THEN 1 
            WHEN 'Medium' THEN 2 
            ELSE 3 END
    """).fetchall()
    
    # Подсчитываем критерии приемки
    total_criteria = 0
    for feature in testable_features:
        criteria_list = json.loads(feature[3]) if feature[3] != '[]' else []
        total_criteria += len(criteria_list)
    
    return {
        "testable_features": len(testable_features),
        "total_criteria": total_criteria,
        "priority_distribution": {row[0]: row[1] for row in priority_dist},
        "features_data": [
            {
                "feature_id": row[0],
                "title": row[1],
                "description": row[2],
                "acceptance_criteria": json.loads(row[3]) if row[3] != '[]' else [],
                "priority": row[4]
            }
            for row in testable_features
        ]
    }


def _generate_failing_tests(analysis: Dict[str, Any], prd_data: Dict[str, Any], test_type: str) -> Dict[str, Any]:
    """Генерирует failing tests на основе PRD требований"""
    
    test_cases = []
    
    for feature in analysis['features_data']:
        feature_id = feature['feature_id']
        title = feature['title']
        
        # Генерируем тесты для каждого критерия приемки
        for i, criterion in enumerate(feature['acceptance_criteria']):
            test_case = {
                "test_id": f"TEST_{feature_id}_{i+1:02d}",
                "feature_id": feature_id,
                "test_name": f"test_{feature_id.lower()}_{_sanitize_name(criterion)}",
                "description": f"RED Phase Test: {title} - {criterion}",
                "test_type": test_type,
                "expected_to_fail": True,  # RED фаза - тесты должны падать
                "test_code": _generate_test_code(feature, criterion, test_type),
                "assertion_type": _determine_assertion_type(criterion),
                "priority": feature['priority'],
                "acceptance_criterion": criterion
            }
            test_cases.append(test_case)
    
    # Добавляем интеграционные тесты для MCP команд
    if test_type == "integration":
        mcp_tests = _generate_mcp_integration_tests(prd_data)
        test_cases.extend(mcp_tests)
    
    return {
        "test_suite_name": f"PRD_Red_Phase_{test_type.title()}_Tests",
        "tdd_phase": "RED",
        "test_cases": test_cases,
        "test_framework": "pytest",
        "expected_outcome": "ALL_TESTS_FAIL",
        "next_phase": "GREEN - implement features to make tests pass"
    }


def _generate_test_code(feature: Dict[str, Any], criterion: str, test_type: str) -> str:
    """Генерирует код теста для критерия приемки"""
    
    feature_id = feature['feature_id']
    sanitized_name = _sanitize_name(criterion)
    
    if test_type == "unit":
        return f"""
def test_{feature_id.lower()}_{sanitized_name}():
    \"\"\"RED: {criterion}\"\"\"
    # Arrange - подготовка тестовых данных
    test_data = {{
        "feature_id": "{feature_id}",
        "input": "test_input_data"
    }}
    
    # Act - выполнение тестируемой функции
    result = execute_feature_{feature_id.lower()}(test_data)
    
    # Assert - проверка результата (должна падать в RED фазе)
    assert result.success == True, "Feature not implemented yet"
    assert result.meets_criterion("{criterion}") == True
    assert result.performance_acceptable == True
"""
    
    elif test_type == "integration":
        return f"""
def test_mcp_{feature_id.lower()}_integration():
    \"\"\"RED Integration: {criterion}\"\"\"
    # Arrange - настройка MCP команды
    mcp_command = "{feature_id.lower().replace('f', 'mcp-')}"
    test_params = {{
        "input_data": "integration_test_data",
        "feature_context": "{feature['title']}"
    }}
    
    # Act - выполнение MCP команды
    result = execute_mcp_command(mcp_command, test_params)
    
    # Assert - проверка интеграции (должна падать в RED фазе)
    assert result["success"] == True, "MCP command not implemented"
    assert "{criterion}" in result["validation_results"]
    assert result["execution_time_ms"] < 2000
"""
    
    else:  # e2e
        return f"""
def test_e2e_{feature_id.lower()}_workflow():
    \"\"\"RED E2E: {criterion}\"\"\"
    # Arrange - полный workflow setup
    workflow_data = {{
        "hypothesis": "test hypothesis",
        "expected_outcome": "{criterion}"
    }}
    
    # Act - выполнение полного цикла
    result = execute_full_mcp_workflow(workflow_data)
    
    # Assert - проверка E2E результата
    assert result["workflow_completed"] == True
    assert result["hypothesis_validated"] == True
    assert "{criterion}" in result["final_outcome"]
"""


def _generate_mcp_integration_tests(prd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Генерирует интеграционные тесты для MCP команд"""
    
    mcp_commands = [
        "falsify-or-confirm",
        "build-jtbd", 
        "write-prd",
        "evaluate-outcome"
    ]
    
    tests = []
    
    for i, cmd in enumerate(mcp_commands):
        test_case = {
            "test_id": f"TEST_MCP_{i+1:02d}",
            "feature_id": f"MCP_{cmd.upper().replace('-', '_')}",
            "test_name": f"test_mcp_{cmd.replace('-', '_')}_integration",
            "description": f"RED Phase MCP Integration: {cmd} command",
            "test_type": "integration",
            "expected_to_fail": True,
            "test_code": f"""
def test_mcp_{cmd.replace('-', '_')}_integration():
    \"\"\"RED: MCP {cmd} интеграция\"\"\"
    # Arrange
    mcp_params = {{"test_data": "authentic_test_input"}}
    
    # Act  
    result = mcp_client.call("{cmd}", mcp_params)
    
    # Assert (должно падать в RED фазе)
    assert result["success"] == True, "MCP {cmd} not implemented"
    assert result["execution_time_ms"] < 2000
    assert "duckdb_processing" in result
""",
            "assertion_type": "integration",
            "priority": "High",
            "acceptance_criterion": f"MCP команда {cmd} работает корректно"
        }
        tests.append(test_case)
    
    return tests


def _sanitize_name(text: str) -> str:
    """Очищает текст для использования в названии теста"""
    import re
    sanitized = re.sub(r'[^\w\s]', '', text.lower())
    return re.sub(r'\s+', '_', sanitized)[:30]


def _determine_assertion_type(criterion: str) -> str:
    """Определяет тип assertion на основе критерия"""
    if "время" in criterion.lower() or "performance" in criterion.lower():
        return "performance"
    elif "данные" in criterion.lower() or "data" in criterion.lower():
        return "data_validation"
    elif "интеграция" in criterion.lower() or "integration" in criterion.lower():
        return "integration"
    else:
        return "functional"


def execute_red_phase_demo():
    """Демонстрация генерации Red Phase тестов"""
    
    print("🧪 MCP Red Phase Tests - TDD Cycle")
    print("=" * 40)
    
    # Используем созданный PRD
    prd_file = "prd_document.json"
    test_type = "integration"
    
    # Генерируем Red Phase тесты
    result = mcp_generate_red_phase_tests(prd_file, test_type)
    
    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
        return result
    
    # Report progress в чат
    tests = result['generated_tests']
    print(f"🧪 Red Phase тесты созданы: {tests['test_suite_name']}")
    print(f"📊 Тестов сгенерировано: {result['tests_count']}")
    print(f"🎯 Функций покрыто: {result['coverage_metrics']['features_covered']}")
    print(f"📋 Критериев покрыто: {result['coverage_metrics']['acceptance_criteria_covered']}")
    print(f"⏱️ Время выполнения: {result['execution_time_ms']}ms")
    
    print(f"\n🔴 RED Phase - все тесты должны ПАДАТЬ:")
    for test in tests['test_cases'][:3]:  # Показываем первые 3
        print(f"  ❌ {test['test_name']}")
        print(f"      {test['description']}")
        print(f"      Приоритет: {test['priority']}")
        print()
    
    if len(tests['test_cases']) > 3:
        print(f"  ... и еще {len(tests['test_cases']) - 3} тестов")
    
    print(f"\n🎯 Следующая фаза TDD:")
    print(f"  🟢 GREEN: Реализовать функции для прохождения тестов")
    print(f"  🔵 BLUE: Рефакторинг и оптимизация")
    
    return result


if __name__ == "__main__":
    # Запуск демонстрации Red Phase
    result = execute_red_phase_demo()
    
    if "error" not in result:
        # Сохраняем тесты
        output_path = Path("red_phase_tests.json")
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n💾 Red Phase тесты сохранены в: {output_path}")
    else:
        print("⚠️ Демонстрация не выполнена из-за ошибки")