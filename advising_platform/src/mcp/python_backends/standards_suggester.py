#!/usr/bin/env python3
"""
Standards Suggester Backend

JTBD: Я (suggester) хочу анализировать JTBD и предлагать релевантные стандарты,
чтобы AI Assistant использовал правильные методологии для текущей задачи.

Интеграция с UnifiedKeyResolver и семантическим анализом контекста.

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Добавляем путь к модулям advising_platform
current_dir = Path(__file__).parent.resolve()
advising_platform_dir = current_dir.parent.parent
sys.path.insert(0, str(advising_platform_dir))

# Динамический импорт для лучшей совместимости
try:
    from advising_platform.src.standards_system import UnifiedStandardsSystem
except ImportError:
    # Direct import
    project_root = current_dir.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from advising_platform.src.standards_system import UnifiedStandardsSystem

class StandardsSuggester:
    """
    JTBD: Я (класс) хочу анализировать контекст задач и предлагать стандарты,
    чтобы AI Assistant получал релевантные методологические рекомендации.
    """
    
    def __init__(self):
        self.system = UnifiedStandardsSystem()
        
        # Инициализируем систему если не загружена
        # Система уже загружена в конструкторе UnifiedStandardsSystem
            
        # Словари ключевых слов для категоризации
        self.task_patterns = {
            "development": [
                "разработка", "код", "программирование", "implementation", "coding",
                "api", "backend", "frontend", "database", "тестирование", "testing",
                "функция", "метод", "класс", "компонент", "модуль"
            ],
            "analysis": [
                "анализ", "исследование", "изучение", "analysis", "research",
                "данные", "статистика", "metrics", "kpi", "отчет", "report",
                "проблема", "причина", "диагностика", "выявление"
            ],
            "design": [
                "дизайн", "проектирование", "архитектура", "design", "architecture", 
                "макет", "прототип", "ui", "ux", "интерфейс", "схема",
                "планирование", "структура", "модель"
            ],
            "process": [
                "процесс", "workflow", "автоматизация", "оптимизация", "улучшение",
                "стандарт", "методология", "framework", "подход", "практика",
                "регламент", "инструкция", "алгоритм"
            ],
            "quality": [
                "качество", "проверка", "валидация", "контроль", "качество",
                "стандарт качества", "compliance", "аудит", "ревью", "review",
                "критерий", "требование", "соответствие"
            ]
        }
    
    def suggest_standards(self, jtbd: str, task_type: str, current_content: str = None, priority: str = "medium") -> dict:
        """
        JTBD: Я (метод) хочу проанализировать задачу и предложить стандарты,
        чтобы вернуть релевантные рекомендации с ранжированием по важности.
        """
        try:
            # 1. Анализируем семантику JTBD
            semantic_profile = self._analyze_semantics(jtbd, current_content)
            
            # 2. Получаем все доступные стандарты
            available_standards = list(self.resolver._logical_map.keys())
            
            # 3. Ранжируем стандарты по релевантности
            ranked_suggestions = []
            for standard_address in available_standards:
                relevance_score = self._calculate_relevance(
                    standard_address, semantic_profile, task_type
                )
                
                if relevance_score > 0.1:  # Фильтруем неподходящие
                    standard_info = self._get_standard_preview(standard_address)
                    ranked_suggestions.append({
                        "address": standard_address,
                        "relevance_score": relevance_score,
                        "title": standard_info["title"],
                        "description": standard_info["description"],
                        "category": standard_info["category"],
                        "reason": self._explain_relevance(standard_address, semantic_profile, task_type)
                    })
            
            # 4. Сортируем по релевантности
            ranked_suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # 5. Применяем фильтр приоритета
            filtered_suggestions = self._apply_priority_filter(ranked_suggestions, priority)
            
            return {
                "success": True,
                "jtbd": jtbd,
                "task_type": task_type,
                "priority": priority,
                "suggestions": filtered_suggestions[:10],  # Топ 10 предложений
                "semantic_analysis": semantic_profile,
                "total_considered": len(available_standards)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Suggestion failed: {str(e)}",
                "jtbd": jtbd
            }
    
    def _analyze_semantics(self, jtbd: str, current_content: str = None) -> dict:
        """
        JTBD: Я (анализатор) хочу извлечь семантические особенности текста,
        чтобы понять суть задачи и контекст работы.
        """
        text_to_analyze = jtbd
        if current_content:
            text_to_analyze += " " + current_content
            
        text_lower = text_to_analyze.lower()
        
        # Анализируем ключевые слова по категориям
        category_scores = {}
        for category, keywords in self.task_patterns.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            category_scores[category] = score / len(keywords)  # Нормализуем
        
        # Извлекаем роли и действия из JTBD
        roles = self._extract_roles(jtbd)
        actions = self._extract_actions(jtbd)
        outcomes = self._extract_outcomes(jtbd)
        
        return {
            "category_scores": category_scores,
            "primary_category": max(category_scores.items(), key=lambda x: x[1])[0],
            "roles": roles,
            "actions": actions,
            "outcomes": outcomes,
            "complexity": self._assess_complexity(text_to_analyze),
            "keywords": self._extract_keywords(text_to_analyze)
        }
    
    def _extract_roles(self, jtbd: str) -> List[str]:
        """Извлекает роли из JTBD формата."""
        roles = []
        
        # Паттерны для поиска ролей
        role_patterns = [
            r"я \(([^)]+)\)",
            r"роль[:\s]+([^,\n]+)",
            r"как ([^,\n]+)",
            r"being a ([^,\n]+)"
        ]
        
        for pattern in role_patterns:
            matches = re.findall(pattern, jtbd.lower())
            roles.extend(matches)
        
        return [role.strip() for role in roles if len(role.strip()) > 2]
    
    def _extract_actions(self, jtbd: str) -> List[str]:
        """Извлекает действия из JTBD."""
        actions = []
        
        # Паттерны для действий
        action_patterns = [
            r"хочет?\s+([^,\n]+)",
            r"хочу\s+([^,\n]+)",
            r"want to ([^,\n]+)",
            r"need to ([^,\n]+)",
            r"создаёт\s+([^,\n]+)",
            r"создать\s+([^,\n]+)"
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, jtbd.lower())
            actions.extend(matches)
        
        return [action.strip() for action in actions if len(action.strip()) > 3]
    
    def _extract_outcomes(self, jtbd: str) -> List[str]:
        """Извлекает ожидаемые результаты."""
        outcomes = []
        
        outcome_patterns = [
            r"чтобы\s+([^,\n]+)",
            r"so that ([^,\n]+)",
            r"результат[:\s]+([^,\n]+)",
            r"цель[:\s]+([^,\n]+)"
        ]
        
        for pattern in outcome_patterns:
            matches = re.findall(pattern, jtbd.lower())
            outcomes.extend(matches)
        
        return [outcome.strip() for outcome in outcomes if len(outcome.strip()) > 3]
    
    def _assess_complexity(self, text: str) -> str:
        """Оценивает сложность задачи."""
        complexity_indicators = {
            "high": ["интеграция", "архитектура", "система", "комплексный", "enterprise"],
            "medium": ["компонент", "модуль", "функция", "процесс", "анализ"],
            "low": ["простой", "базовый", "basic", "quick", "small"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[level] = score
        
        if scores["high"] > 0:
            return "high"
        elif scores["medium"] > scores["low"]:
            return "medium"
        else:
            return "low"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста."""
        # Простое извлечение важных слов
        words = re.findall(r'\b[а-яё]{4,}\b|\b[a-z]{4,}\b', text.lower())
        
        # Фильтруем стоп-слова
        stop_words = {"что", "как", "для", "при", "это", "того", "чтобы", "также", 
                     "может", "быть", "должен", "нужно", "можно", "есть"}
        
        keywords = [word for word in set(words) if word not in stop_words]
        return keywords[:20]  # Топ 20 ключевых слов
    
    def _calculate_relevance(self, standard_address: str, semantic_profile: dict, task_type: str) -> float:
        """Вычисляет релевантность стандарта к задаче."""
        relevance_score = 0.0
        
        # Получаем контент стандарта
        cache_entry = self.cache.get_document(self.resolver.resolve_to_canonical(standard_address))
        if not cache_entry:
            return 0.0
        
        content_lower = cache_entry.content.lower()
        
        # 1. Соответствие категории задачи (вес 40%)
        category_match = semantic_profile["category_scores"].get(task_type, 0)
        relevance_score += category_match * 0.4
        
        # 2. Соответствие ключевых слов (вес 30%)
        keyword_matches = 0
        for keyword in semantic_profile["keywords"]:
            if keyword in content_lower:
                keyword_matches += 1
        
        if semantic_profile["keywords"]:
            keyword_score = keyword_matches / len(semantic_profile["keywords"])
            relevance_score += keyword_score * 0.3
        
        # 3. Соответствие действий JTBD (вес 20%)
        action_matches = 0
        for action in semantic_profile["actions"]:
            if any(word in content_lower for word in action.split()):
                action_matches += 1
        
        if semantic_profile["actions"]:
            action_score = action_matches / len(semantic_profile["actions"])
            relevance_score += action_score * 0.2
        
        # 4. Специальные бонусы (вес 10%)
        # Бонус за упоминание TDD, JTBD, стандартов
        if any(term in content_lower for term in ["tdd", "jtbd", "стандарт", "методология"]):
            relevance_score += 0.1
        
        return min(relevance_score, 1.0)  # Максимум 1.0
    
    def _get_standard_preview(self, standard_address: str) -> dict:
        """Получает краткую информацию о стандарте."""
        cache_entry = self.cache.get_document(self.resolver.resolve_to_canonical(standard_address))
        
        if not cache_entry:
            return {
                "title": standard_address.split(":")[-1],
                "description": "Описание недоступно",
                "category": "unknown"
            }
        
        content = cache_entry.content
        lines = content.split('\n')
        
        # Извлекаем заголовок
        title = standard_address.split(":")[-1]
        for line in lines[:10]:
            if line.startswith('#') and len(line.strip()) > 2:
                title = line.strip('# ').strip()
                break
        
        # Извлекаем описание
        description = "Описание недоступно"
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in ['цель', 'описание', 'jtbd']):
                # Берем следующие строки как описание
                desc_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        desc_lines.append(lines[j].strip())
                if desc_lines:
                    description = ' '.join(desc_lines)[:200] + "..."
                break
        
        # Определяем категорию
        category = self._categorize_standard(content)
        
        return {
            "title": title,
            "description": description,
            "category": category
        }
    
    def _categorize_standard(self, content: str) -> str:
        """Определяет категорию стандарта по содержимому."""
        content_lower = content.lower()
        
        category_scores = {}
        for category, keywords in self.task_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            category_scores[category] = score
        
        if not category_scores or max(category_scores.values()) == 0:
            return "general"
        
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def _explain_relevance(self, standard_address: str, semantic_profile: dict, task_type: str) -> str:
        """Объясняет почему стандарт релевантен."""
        reasons = []
        
        # Причины на основе категории
        if semantic_profile["primary_category"] == task_type:
            reasons.append(f"Соответствует типу задачи '{task_type}'")
        
        # Причины на основе действий
        if semantic_profile["actions"]:
            reasons.append(f"Поддерживает действия: {', '.join(semantic_profile['actions'][:2])}")
        
        # Причины на основе результатов
        if semantic_profile["outcomes"]:
            reasons.append(f"Помогает достичь: {semantic_profile['outcomes'][0]}")
        
        if not reasons:
            reasons.append("Общая применимость к задаче")
        
        return "; ".join(reasons)
    
    def _apply_priority_filter(self, suggestions: List[dict], priority: str) -> List[dict]:
        """Применяет фильтр приоритета к предложениям."""
        if priority == "high":
            # Только самые релевантные (топ 5)
            return [s for s in suggestions if s["relevance_score"] > 0.5][:5]
        elif priority == "low":
            # Все предложения, включая менее релевантные
            return suggestions[:15]
        else:  # medium
            # Сбалансированный набор (топ 8)
            return [s for s in suggestions if s["relevance_score"] > 0.3][:8]


def main():
    """Основная функция для вызова из MCP сервера."""
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python standards_suggester.py <json_args>")
        
        args = json.loads(sys.argv[1])
        
        suggester = StandardsSuggester()
        result = suggester.suggest_standards(
            jtbd=args.get("jtbd"),
            task_type=args.get("taskType", "development"),
            current_content=args.get("currentContent"),
            priority=args.get("priority", "medium")
        )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Script execution failed: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()