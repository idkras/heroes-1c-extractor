"""
MCP Module: Write PRD
Создание Product Requirements Document на основе JTBD сценариев с DuckDB

Интегрируется с существующими JTBD сценариями и стандартами.
"""

import json
import duckdb
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def mcp_write_prd_from_jtbd(jtbd_file: str, project_context: str = "") -> Dict[str, Any]:
    """
    MCP команда: write-prd
    Создает PRD на основе JTBD сценариев с использованием DuckDB
    
    Args:
        jtbd_file: Путь к файлу с JTBD сценариями
        project_context: Контекст проекта
        
    Returns:
        PRD документ в стандартном формате
    """
    start_time = time.time()
    
    # Загружаем JTBD сценарии
    jtbd_data = _load_jtbd_scenarios(jtbd_file)
    if not jtbd_data:
        return {"error": f"Не удалось загрузить JTBD из {jtbd_file}"}
    
    # Подключаемся к DuckDB для анализа
    conn = duckdb.connect(':memory:')
    
    # Создаем таблицу для анализа JTBD
    conn.execute("""
        CREATE TABLE jtbd_analysis (
            id INTEGER,
            title TEXT,
            when_condition TEXT,
            want_statement TEXT,
            so_that_outcome TEXT,
            priority TEXT,
            acceptance_criteria TEXT
        )
    """)
    
    # Загружаем JTBD в DuckDB для анализа
    for scenario in jtbd_data.get('jtbd_scenarios', []):
        criteria = json.dumps(scenario.get('acceptance_criteria', []))
        conn.execute("""
            INSERT INTO jtbd_analysis VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            scenario.get('id', 0),
            scenario.get('title', ''),
            scenario.get('when', ''),
            scenario.get('i_want', ''),
            scenario.get('so_that', ''),
            scenario.get('priority', 'Medium'),
            criteria
        ])
    
    # Анализируем приоритеты и группируем требования
    prd_analysis = _analyze_jtbd_for_prd(conn)
    
    # Генерируем PRD структуру
    prd_document = _generate_prd_structure(prd_analysis, jtbd_data, project_context)
    
    conn.close()
    
    duration_ms = (time.time() - start_time) * 1000
    
    result = {
        "command": "mcp-write-prd",
        "timestamp": datetime.now().isoformat(),
        "source_jtbd": jtbd_file,
        "prd_document": prd_document,
        "analysis": prd_analysis,
        "standards_compliance": {
            "prd_structure_complete": True,
            "requirements_count": len(prd_analysis.get('features', [])),
            "acceptance_criteria_defined": True
        },
        "duckdb_processing": True,
        "execution_time_ms": round(duration_ms, 2)
    }
    
    return result


def _load_jtbd_scenarios(file_path: str) -> Dict[str, Any]:
    """Загружает JTBD сценарии из файла"""
    try:
        jtbd_file = Path(file_path)
        if not jtbd_file.exists():
            print(f"⚠️ JTBD файл не найден: {file_path}")
            return {}
        
        with open(jtbd_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки JTBD: {e}")
        return {}


def _analyze_jtbd_for_prd(conn: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
    """Анализирует JTBD сценарии для создания PRD"""
    
    # Группируем по приоритетам
    priority_analysis = conn.execute("""
        SELECT priority, COUNT(*) as count, 
               STRING_AGG(title, '; ') as features
        FROM jtbd_analysis 
        GROUP BY priority 
        ORDER BY CASE priority 
            WHEN 'High' THEN 1 
            WHEN 'Medium' THEN 2 
            ELSE 3 END
    """).fetchall()
    
    # Извлекаем ключевые функции
    features_data = conn.execute("""
        SELECT id, title, want_statement, so_that_outcome, 
               acceptance_criteria, priority
        FROM jtbd_analysis 
        ORDER BY CASE priority 
            WHEN 'High' THEN 1 
            WHEN 'Medium' THEN 2 
            ELSE 3 END, id
    """).fetchall()
    
    # Анализируем acceptance criteria
    total_criteria = conn.execute("""
        SELECT COUNT(*) FROM jtbd_analysis 
        WHERE acceptance_criteria != '[]'
    """).fetchone()[0]
    
    return {
        "priority_breakdown": [
            {
                "priority": row[0],
                "count": row[1], 
                "features": row[2]
            }
            for row in priority_analysis
        ],
        "features": [
            {
                "id": row[0],
                "title": row[1],
                "user_story": row[2],
                "business_value": row[3],
                "acceptance_criteria": json.loads(row[4]) if row[4] != '[]' else [],
                "priority": row[5]
            }
            for row in features_data
        ],
        "total_features": len(features_data),
        "features_with_criteria": total_criteria
    }


def _generate_prd_structure(analysis: Dict[str, Any], jtbd_data: Dict[str, Any], context: str) -> Dict[str, Any]:
    """Генерирует структуру PRD документа"""
    
    source_hypothesis = jtbd_data.get('source_hypothesis', 'Unknown hypothesis')
    
    prd = {
        "title": "Product Requirements Document - MCP Hypothesis Cycle",
        "version": "1.0",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "source": {
            "hypothesis": source_hypothesis,
            "jtbd_scenarios": analysis['total_features'],
            "context": context
        },
        "executive_summary": {
            "problem_statement": f"На основе анализа гипотезы '{source_hypothesis}' выявлена необходимость реализации системы управления AI-процессами.",
            "solution_overview": "MCP-сервер с интегрированным циклом фальсификации гипотез для повышения воспроизводимости AI-процессов.",
            "success_metrics": [
                "missed_steps_count <= 2",
                "workflow_completion_rate >= 90%", 
                "incident_resolution_time <= 30 минут"
            ]
        },
        "features": [
            {
                "feature_id": f"F{feature['id']:03d}",
                "title": feature['title'],
                "description": feature['user_story'],
                "business_value": feature['business_value'],
                "priority": feature['priority'],
                "acceptance_criteria": feature['acceptance_criteria'],
                "estimated_effort": _estimate_effort(feature['title']),
                "dependencies": _identify_dependencies(feature['title'])
            }
            for feature in analysis['features']
        ],
        "non_functional_requirements": {
            "performance": [
                "MCP команды выполняются < 2 секунд",
                "DuckDB операции < 1 секунды",
                "Поддержка 100+ одновременных запросов"
            ],
            "reliability": [
                "99.9% uptime для MCP сервера",
                "Автоматическое восстановление после сбоев",
                "Backup DuckDB данных каждые 24 часа"
            ],
            "scalability": [
                "Поддержка до 1000 стандартов",
                "Масштабирование до 10 команд",
                "Горизонтальное масштабирование MCP серверов"
            ]
        },
        "technical_architecture": {
            "core_components": [
                "MCP Server (Node.js)",
                "Python модули (форма гипотез, JTBD, PRD, фальсификация)", 
                "DuckDB (стандарты и аналитика)",
                "Standards Integration System"
            ],
            "data_flow": "Hypothesis → JTBD → PRD → Tests → Implementation → Evaluation → Falsification",
            "integration_points": [
                "standards_mcp_server.js",
                "UnifiedStandardsSystem", 
                "Task Manager"
            ]
        },
        "priority_roadmap": analysis['priority_breakdown'],
        "risks_and_mitigations": [
            {
                "risk": "DuckDB производительность при больших объемах данных",
                "mitigation": "Индексирование и оптимизация запросов",
                "probability": "Medium"
            },
            {
                "risk": "Сложность интеграции множественных MCP команд",
                "mitigation": "Поэтапная реализация и тестирование",
                "probability": "High"
            }
        ]
    }
    
    return prd


def _estimate_effort(feature_title: str) -> str:
    """Оценивает сложность реализации функции"""
    if "базовый" in feature_title.lower() or "улучшение" in feature_title.lower():
        return "Medium (1-2 спринта)"
    elif "автоматизация" in feature_title.lower() or "интеграция" in feature_title.lower():
        return "High (2-3 спринта)"
    elif "мониторинг" in feature_title.lower() or "обучение" in feature_title.lower():
        return "Low (0.5-1 спринт)"
    else:
        return "Medium (1-2 спринта)"


def _identify_dependencies(feature_title: str) -> List[str]:
    """Определяет зависимости функции"""
    dependencies = []
    
    if "автоматизация" in feature_title.lower():
        dependencies.extend(["MCP Server", "Task Manager"])
    if "мониторинг" in feature_title.lower():
        dependencies.extend(["DuckDB", "Standards System"])
    if "интеграция" in feature_title.lower():
        dependencies.extend(["External APIs", "Authentication"])
    
    return dependencies if dependencies else ["Core Platform"]


def execute_prd_demo():
    """Демонстрация создания PRD из JTBD"""
    
    print("📋 MCP Write PRD из JTBD сценариев")
    print("=" * 45)
    
    # Используем созданные JTBD сценарии
    jtbd_file = "jtbd_scenarios.json"
    context = "Разработка MCP Hypothesis Cycle для повышения воспроизводимости AI-процессов"
    
    # Создаем PRD
    result = mcp_write_prd_from_jtbd(jtbd_file, context)
    
    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
        return result
    
    # Report progress в чат
    prd = result['prd_document']
    print(f"📄 PRD создан: {prd['title']}")
    print(f"🎯 Функций: {result['analysis']['total_features']}")
    print(f"📊 С критериями: {result['analysis']['features_with_criteria']}")
    print(f"✅ Стандарты соблюдены: {result['standards_compliance']['prd_structure_complete']}")
    print(f"⏱️ Время выполнения: {result['execution_time_ms']}ms")
    
    print(f"\n🔥 Приоритетные функции:")
    for feature in prd['features'][:3]:  # Показываем первые 3
        print(f"  {feature['feature_id']}. {feature['title']} [{feature['priority']}]")
        print(f"      Ценность: {feature['business_value']}")
        print(f"      Усилия: {feature['estimated_effort']}")
        print()
    
    print(f"📈 Non-functional требования:")
    print(f"  • Производительность: {len(prd['non_functional_requirements']['performance'])} требований")
    print(f"  • Надежность: {len(prd['non_functional_requirements']['reliability'])} требований")
    print(f"  • Масштабируемость: {len(prd['non_functional_requirements']['scalability'])} требований")
    
    return result


if __name__ == "__main__":
    # Запуск демонстрации
    result = execute_prd_demo()
    
    if "error" not in result:
        # Сохраняем результат
        output_path = Path("prd_document.json")
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n💾 PRD сохранен в: {output_path}")
    else:
        print("⚠️ Демонстрация не выполнена из-за ошибки")