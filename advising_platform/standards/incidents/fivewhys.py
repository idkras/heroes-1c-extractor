"""
Модуль для анализа "5 Почему" в соответствии со стандартом 5 Why Analysis.

Реализует методологию "5 Почему" для анализа корневых причин инцидентов,
обеспечивая структурированный подход к выявлению фундаментальных проблем.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Union

from advising_platform.standards.core.traceable import implements_standard

# Настройка логирования
logger = logging.getLogger(__name__)


@implements_standard("5why_analysis", "1.0", "parser")
def parse_five_whys_from_text(text: str) -> List[Dict[str, str]]:
    """
    Извлекает анализ "5 Почему" из текста инцидента.
    
    Args:
        text: Текст инцидента
    
    Returns:
        Список с вопросами "почему" и ответами
    """
    # Ищем секцию анализа "5 почему"
    section_match = re.search(
        r'(?:##?\s+(?:🔍|:mag:)\s*Анализ\s+корневых\s+причин.*?5\s+почему.*?\n)(.*?)(?:##|\Z)',
        text,
        re.DOTALL | re.IGNORECASE
    )
    
    if not section_match:
        return []
    
    section_text = section_match.group(1).strip()
    
    # Ищем пронумерованные вопросы "почему"
    why_matches = re.finditer(
        r'(?:\d+\.\s+)?(?:\*\*)?(?:Почему|Why)(?:\s+\d+)?(?:\*\*)?\s*[:?]\s*(.*?)\s*(?:-|–|—)\s*(.*?)(?:\n|$)',
        section_text,
        re.DOTALL | re.IGNORECASE
    )
    
    whys = []
    for match in why_matches:
        question = match.group(1).strip()
        answer = match.group(2).strip()
        whys.append({"question": question, "answer": answer})
    
    # Если не нашли по паттерну выше, пробуем другой формат
    if not whys:
        # Пробуем найти список с пунктами "Почему"
        why_matches = re.finditer(
            r'(?:\d+\.\s+|\*\s+)?(?:\*\*)?(?:Почему|Why)(?:\s+\d+)?(?:\*\*)?\s*[:?]\s*(.*?)(?:\n|$)',
            section_text,
            re.DOTALL | re.IGNORECASE
        )
        
        questions = []
        for match in why_matches:
            question = match.group(1).strip()
            questions.append(question)
        
        # Преобразуем в формат вопрос-ответ
        for i, question in enumerate(questions):
            # Для последнего вопроса ответом является корневая причина, если она есть
            if i == len(questions) - 1:
                root_cause_match = re.search(
                    r'(?:##?\s+(?:🌟|:star:)\s*Корневая\s+причина.*?\n)(.*?)(?:##|\Z)',
                    text,
                    re.DOTALL | re.IGNORECASE
                )
                
                if root_cause_match:
                    answer = root_cause_match.group(1).strip()
                else:
                    answer = "Не указано"
            else:
                # Для остальных вопросов ответом является следующий вопрос
                answer = questions[i + 1]
            
            whys.append({"question": question, "answer": answer})
    
    return whys


@implements_standard("5why_analysis", "1.0", "generator")
def generate_five_whys_analysis(problem_statement: str, whys: List[Dict[str, str]]) -> str:
    """
    Генерирует структурированный анализ "5 Почему" на основе предоставленных данных.
    
    Args:
        problem_statement: Исходное утверждение проблемы
        whys: Список с вопросами "почему" и ответами
    
    Returns:
        Отформатированный текст анализа "5 Почему"
    """
    # Проверяем, что у нас есть хотя бы один вопрос
    if not whys:
        return "## 🔍 Анализ корневых причин (5 почему)\n\nНедостаточно данных для анализа 5 почему.\n"
    
    # Генерируем структурированный анализ
    analysis = "## 🔍 Анализ корневых причин (5 почему)\n\n"
    
    # Добавляем исходное утверждение проблемы, если оно предоставлено
    if problem_statement:
        analysis += f"**Исходная проблема**: {problem_statement}\n\n"
    
    # Добавляем вопросы и ответы
    for i, why in enumerate(whys, 1):
        question = why.get("question", "Не указано")
        answer = why.get("answer", "Не указано")
        
        analysis += f"{i}. **Почему {question}** - {answer}\n"
    
    # Добавляем корневую причину (последний ответ)
    if whys:
        root_cause = whys[-1].get("answer", "Не указано")
        analysis += f"\n## 🌟 Корневая причина\n\n{root_cause}\n"
    
    return analysis


@implements_standard("5why_analysis", "1.0", "validator")
def validate_five_whys_analysis(whys: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Проверяет качество анализа "5 Почему".
    
    Args:
        whys: Список с вопросами "почему" и ответами
    
    Returns:
        Результаты валидации
    """
    validation = {
        "is_valid": True,
        "issues": [],
        "recommendations": []
    }
    
    # Проверяем количество вопросов
    if len(whys) < 3:
        validation["is_valid"] = False
        validation["issues"].append("Недостаточное количество вопросов 'почему'. Рекомендуется минимум 3 вопроса.")
    
    if len(whys) > 7:
        validation["recommendations"].append("Большое количество вопросов 'почему'. Рекомендуется не более 5-7 вопросов.")
    
    # Проверяем качество формулировок
    for i, why in enumerate(whys, 1):
        question = why.get("question", "")
        answer = why.get("answer", "")
        
        # Проверяем длину вопроса и ответа
        if len(question.split()) < 3:
            validation["issues"].append(f"Вопрос {i} слишком короткий. Рекомендуется более подробная формулировка.")
        
        if len(answer.split()) < 3:
            validation["issues"].append(f"Ответ {i} слишком короткий. Рекомендуется более подробное объяснение.")
        
        # Проверяем наличие конкретики в ответе
        generic_answers = ["не знаю", "неизвестно", "не указано", "не определено"]
        for generic in generic_answers:
            if generic in answer.lower():
                validation["issues"].append(f"Ответ {i} неконкретный. Рекомендуется предоставить содержательный ответ.")
                break
    
    # Обновляем статус валидности
    validation["is_valid"] = len(validation["issues"]) == 0
    
    return validation


@implements_standard("5why_analysis", "1.0", "complete_analysis")
def perform_five_whys_analysis(
    problem_statement: str,
    initial_whys: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Выполняет полный анализ "5 Почему" для указанной проблемы.
    
    Args:
        problem_statement: Исходное утверждение проблемы
        initial_whys: Начальные вопросы и ответы (опционально)
    
    Returns:
        Результаты анализа
    """
    whys = initial_whys or []
    
    # Если начальные вопросы не предоставлены, создаем шаблон
    if not whys:
        whys = [
            {"question": "возникла проблема?", "answer": ""}
        ]
    
    # Генерируем анализ
    analysis_text = generate_five_whys_analysis(problem_statement, whys)
    
    # Валидируем анализ
    validation = validate_five_whys_analysis(whys)
    
    return {
        "problem_statement": problem_statement,
        "whys": whys,
        "text": analysis_text,
        "validation": validation
    }


if __name__ == "__main__":
    # Пример использования
    problem = "Код создает отдельные файлы инцидентов вместо использования централизованного хранилища"
    
    whys = [
        {"question": "код создает отдельные файлы вместо использования централизованного хранилища?", 
         "answer": "Функции разработаны до принятия нового стандарта инцидентов"},
        {"question": "функции были разработаны до принятия нового стандарта?", 
         "answer": "Отсутствует механизм проверки соответствия кода стандартам"},
        {"question": "отсутствует механизм проверки соответствия кода стандартам?", 
         "answer": "Не установлена связь между стандартами и реализующим их кодом"},
        {"question": "не установлена связь между стандартами и реализующим их кодом?", 
         "answer": "Отсутствует систематический подход к управлению изменениями стандартов"},
        {"question": "отсутствует систематический подход к управлению изменениями стандартов?", 
         "answer": "Не создана система, автоматически отслеживающая изменения стандартов и инициирующая обновление кода"}
    ]
    
    analysis = perform_five_whys_analysis(problem, whys)
    print(analysis["text"])