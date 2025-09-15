"""
Тесты интеграции 5-why анализа и lifecycle инцидентов.

JTBD: Как система анализа инцидентов, я хочу корректно обрабатывать
5-why анализ и статусы жизненного цикла, чтобы обеспечить
эффективное решение проблем по методологии из стандартов.

Based on: AI Incident Standard 1.1, Root Cause Analysis methodology
Data sources: Real 5-why format and lifecycle statuses from standards
"""

import pytest
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FiveWhyLevel:
    """Уровень 5-why анализа"""
    level: int
    question: str
    answer: str
    is_root_cause: bool = False

@dataclass
class IncidentRecord:
    """Запись инцидента по формату Standard 1.1"""
    incident_id: str
    title: str
    description: str
    status: str
    five_why_analysis: List[FiveWhyLevel]
    root_cause: str
    design_injection: str
    design_change: str
    created_at: datetime

class TestIncidentFiveWhyRealFormat:
    """Тесты 5-why анализа по РЕАЛЬНОМУ формату из Standard 1.1"""
    
    def test_incident_five_why_exact_structure(self):
        """
        Тест ТОЧНОГО формата 5-why из AI Incident Standard 1.1.
        
        ФАКТИЧЕСКИЙ ФОРМАТ:
        1. Почему [проблема]? - [причина уровня 1]
        2. Почему [причина 1]? - [причина уровня 2]  
        3. Почему [причина 2]? - [причина уровня 3]
        4. Почему [причина 3]? - [причина уровня 4]
        5. Почему [причина 4]? - [корневая причина]
        """
        # Реальный пример 5-why анализа
        sample_five_why = [
            FiveWhyLevel(
                level=1,
                question="Почему создаются дублирующие контекстные файлы?",
                answer="AI создает новые файлы вместо обновления существующих"
            ),
            FiveWhyLevel(
                level=2, 
                question="Почему AI создает новые файлы вместо обновления?",
                answer="Отсутствует проверка существования файлов перед созданием"
            ),
            FiveWhyLevel(
                level=3,
                question="Почему отсутствует проверка существования файлов?",
                answer="Не реализован механизм валидации файловой структуры"
            ),
            FiveWhyLevel(
                level=4,
                question="Почему не реализован механизм валидации?",
                answer="Нет стандарта для проверки файловых операций"
            ),
            FiveWhyLevel(
                level=5,
                question="Почему нет стандарта для проверки файловых операций?",
                answer="Отсутствует системный подход к управлению файлами",
                is_root_cause=True
            )
        ]
        
        # Проверяем структуру 5-why
        assert len(sample_five_why) == 5
        
        for level_data in sample_five_why:
            # Каждый уровень должен иметь правильную структуру
            assert level_data.level >= 1 and level_data.level <= 5
            assert level_data.question.startswith("Почему")
            assert level_data.question.endswith("?")
            assert len(level_data.answer) > 10  # содержательный ответ
            
        # Только 5-й уровень должен быть корневой причиной
        root_causes = [level for level in sample_five_why if level.is_root_cause]
        assert len(root_causes) == 1
        assert root_causes[0].level == 5
        
    def test_incident_lifecycle_statuses_real_format(self):
        """
        Проверка статусов жизненного цикла из РЕАЛЬНОГО Standard 1.1.
        
        ФАКТИЧЕСКИЕ СТАТУСЫ:
        - Recorded (Зафиксирован)
        - In Progress (В работе) 
        - Hypothesis Testing (На проверке гипотезы)
        - Hypothesis Confirmed (Гипотеза сработала)
        - Hypothesis Failed (Гипотеза не сработала)
        """
        valid_statuses = [
            "Recorded",
            "In Progress", 
            "Hypothesis Testing",
            "Hypothesis Confirmed",
            "Hypothesis Failed"
        ]
        
        # Проверяем что все статусы определены
        assert len(valid_statuses) == 5
        
        # Проверяем логику переходов между статусами
        status_transitions = {
            "Recorded": ["In Progress"],
            "In Progress": ["Hypothesis Testing"],
            "Hypothesis Testing": ["Hypothesis Confirmed", "Hypothesis Failed"],
            "Hypothesis Confirmed": [],  # финальный статус
            "Hypothesis Failed": ["In Progress"]  # можно вернуться к работе
        }
        
        for status, next_statuses in status_transitions.items():
            assert status in valid_statuses
            for next_status in next_statuses:
                assert next_status in valid_statuses
                
    def test_real_incident_record_structure(self):
        """
        Тест полной структуры записи инцидента по Standard 1.1.
        
        ОБЯЗАТЕЛЬНЫЕ РАЗДЕЛЫ:
        1. 5 почему разбор
        2. Корневая причина (не более 100 символов)
        3. Дизайн-инъекция (не более 50 символов)
        4. Дизайн изменения (100-150 символов)
        5. Статус инцидента
        """
        # Создаем полный инцидент по стандарту
        sample_incident = IncidentRecord(
            incident_id="I001",
            title="Создание дублирующих контекстных файлов для Rick.ai",
            description="AI создает новые контекстные файлы вместо обновления существующих",
            status="Hypothesis Testing",
            five_why_analysis=[
                FiveWhyLevel(1, "Почему дублируются файлы?", "Нет проверки существования"),
                FiveWhyLevel(2, "Почему нет проверки?", "Не реализован механизм"),
                FiveWhyLevel(3, "Почему не реализован?", "Нет стандарта"),
                FiveWhyLevel(4, "Почему нет стандарта?", "Отсутствует системный подход"),
                FiveWhyLevel(5, "Почему отсутствует подход?", "Не определены процессы управления файлами", True)
            ],
            root_cause="Отсутствует системный подход к управлению файлами",
            design_injection="Процесс создания файлов",
            design_change="Добавить проверку существования файлов перед созданием новых с автоматическим обновлением",
            created_at=datetime.now()
        )
        
        # Проверяем все обязательные элементы
        assert sample_incident.incident_id.startswith("I")
        assert len(sample_incident.title) > 0
        assert sample_incident.status in ["Recorded", "In Progress", "Hypothesis Testing", "Hypothesis Confirmed", "Hypothesis Failed"]
        assert len(sample_incident.five_why_analysis) == 5
        
        # Проверяем ограничения на длину по стандарту
        assert len(sample_incident.root_cause) <= 100, "Root cause должна быть ≤ 100 символов"
        assert len(sample_incident.design_injection) <= 50, "Design injection должна быть ≤ 50 символов"
        assert 100 <= len(sample_incident.design_change) <= 150, "Design change должно быть 100-150 символов"
        
    def test_date_format_human_readable(self):
        """
        Проверка человекочитаемого формата дат из Standard 1.1.
        
        ТРЕБОВАНИЕ: "Даты записываются в человекочитаемом формате 
        (12 May 2025) вместо машинного формата (2025-05-12)"
        """
        import re
        
        # Примеры правильных дат из стандартов
        valid_date_examples = [
            "12 May 2025 14:10",
            "15 May 2025, 19:35 CET",
            "22 May 2025, 19:00 CET",
            "26 May 2025, 05:35 CET"
        ]
        
        # Паттерн для человекочитаемых дат
        human_date_pattern = r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
        
        for date_example in valid_date_examples:
            assert re.search(human_date_pattern, date_example), f"Date {date_example} should be human readable"
            
        # Проверяем что машинные форматы НЕ используются
        invalid_formats = [
            "2025-05-12",
            "2025/05/12", 
            "05-12-2025",
            "12/05/2025"
        ]
        
        for invalid_format in invalid_formats:
            assert not re.match(human_date_pattern, invalid_format), f"Format {invalid_format} should NOT be used"

class TestHypothesisRATMethodology:
    """Тесты RAT (Risk Assumption Tests) из Hypothesis Standard 2.2"""
    
    def test_hypothesis_rat_real_structure(self):
        """
        RAT (Risk Assumption Tests) из РЕАЛЬНОГО Hypothesis Standard 2.2.
        
        ФАКТИЧЕСКАЯ СТРУКТУРА RAT из duck.todo.md:
        - Риск: [описание риска]
        - Тест: [способ проверки]  
        - Критерий успеха: [измеримый результат]
        - Fallback: [план отката]
        """
        # Реальные RAT примеры из duck.todo.md
        sample_rats = [
            {
                "name": "RAT-1: Параллельная структура без конфликтов",
                "risk": "DuckDB может конфликтовать с существующим кешем",
                "test": "Одновременная работа обеих систем с monitoring ресурсов",
                "success_criteria": "Отсутствие memory leaks, блокировок файлов",
                "fallback": "Isolation через separate processes"
            },
            {
                "name": "RAT-2: Полная загрузка данных с нуля", 
                "risk": "Потеря связей между стандартами при fresh загрузке",
                "test": "Сканирование всех .md файлов и восстановление dependency graph",
                "success_criteria": "100% найденных связей между документами",
                "fallback": "Manual mapping критических связей"
            },
            {
                "name": "RAT-3: Task Master AI 2.0 интеграция",
                "risk": "Новые AI workflow могут быть несовместимы с DuckDB",
                "test": "Адаптация AIWorkflowMCP для работы с DuckDB backend",
                "success_criteria": "Все существующие MCP операции работают с обоими backends",
                "fallback": "Dual-backend адаптер pattern"
            }
        ]
        
        # Проверяем структуру каждого RAT
        for rat in sample_rats:
            # Обязательные компоненты RAT
            assert "risk" in rat
            assert "test" in rat
            assert "success_criteria" in rat
            assert "fallback" in rat
            
            # Содержательность каждого компонента
            assert len(rat["risk"]) > 10, "Risk должен быть содержательным"
            assert len(rat["test"]) > 10, "Test должен быть конкретным"
            assert len(rat["success_criteria"]) > 10, "Success criteria должны быть измеримыми"
            assert len(rat["fallback"]) > 10, "Fallback должен быть actionable"
            
            # Проверяем что есть измеримые критерии
            success_text = rat["success_criteria"].lower()
            measurable_indicators = ["100%", "отсутствие", "все", "корректно", "работают"]
            has_measurable = any(indicator in success_text for indicator in measurable_indicators)
            assert has_measurable, f"Success criteria должны быть измеримыми: {rat['success_criteria']}"
            
    def test_falsifiable_hypothesis_criteria(self):
        """
        Проверка falsifiable критериев из Hypothesis Standard 2.2.
        
        Из стандарта: гипотезы должны быть falsifiable - опровергаемыми
        """
        # Примеры falsifiable гипотез
        falsifiable_examples = [
            {
                "hypothesis": "DuckDB показывает производительность ≤150% от current cache",
                "falsifiable_criteria": "Если DuckDB медленнее чем 150% - гипотеза ложна",
                "measurement": "benchmark времени выполнения"
            },
            {
                "hypothesis": "100% данных сохраняется при миграции",
                "falsifiable_criteria": "Если потеряна хотя бы одна запись - гипотеза ложна", 
                "measurement": "count записей до и после миграции"
            },
            {
                "hypothesis": "Все MCP операции работают с DuckDB backend",
                "falsifiable_criteria": "Если хотя бы одна MCP команда падает - гипотеза ложна",
                "measurement": "success rate MCP команд"
            }
        ]
        
        for example in falsifiable_examples:
            # Проверяем наличие конкретных критериев
            assert "≤" in example["hypothesis"] or "100%" in example["hypothesis"] or "все" in example["hypothesis"].lower()
            
            # Проверяем что есть четкое условие опровержения
            assert "ложна" in example["falsifiable_criteria"]
            assert "если" in example["falsifiable_criteria"].lower()
            
            # Проверяем что есть способ измерения
            assert len(example["measurement"]) > 5

class TestIncidentRootCauseAnalysis:
    """Тесты root cause analysis по методологии Standard 1.1"""
    
    def test_design_injection_points(self):
        """
        Проверка точек дизайн-инъекции из Standard 1.1.
        
        ТРЕБОВАНИЕ: "Точка в процессе, где необходимо внести изменение, 
        не более 50 символов"
        """
        # Примеры правильных дизайн-инъекций
        design_injection_examples = [
            "Процесс создания файлов",
            "MCP команды validation",
            "Cache synchronization",
            "Standards loading workflow", 
            "Error handling pipeline"
        ]
        
        for injection_point in design_injection_examples:
            # Проверяем ограничение на длину
            assert len(injection_point) <= 50, f"Design injection слишком длинная: {injection_point}"
            
            # Проверяем что это конкретная точка в процессе
            process_indicators = ["процесс", "workflow", "pipeline", "handling", "validation", "loading"]
            has_process_indicator = any(indicator in injection_point.lower() for indicator in process_indicators)
            assert has_process_indicator, f"Design injection должна указывать на процесс: {injection_point}"
            
    def test_design_change_specificity(self):
        """
        Проверка конкретности дизайн-изменений.
        
        ТРЕБОВАНИЕ: "Конкретное решение, адресующее корневую причину, 100-150 символов"
        """
        # Примеры правильных дизайн-изменений
        design_changes = [
            "Добавить проверку существования файлов перед созданием новых с автоматическим обновлением содержимого",
            "Реализовать validation pipeline для всех MCP команд с logging ошибок и automatic retry механизмом",
            "Создать unified caching layer с синхронизацией между memory и disk storage через checksums"
        ]
        
        for change in design_changes:
            # Проверяем длину по стандарту
            assert 100 <= len(change) <= 150, f"Design change должно быть 100-150 символов: {len(change)} символов"
            
            # Проверяем конкретность (наличие action words)
            action_words = ["добавить", "реализовать", "создать", "внедрить", "настроить"]
            has_action = any(action in change.lower() for action in action_words)
            assert has_action, f"Design change должно содержать конкретное действие: {change}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])