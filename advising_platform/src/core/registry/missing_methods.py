"""
Дополнительные методы для TaskRegistry.

Содержит методы, отсутствующие в текущей реализации TaskRegistry,
но необходимые для правильной работы WorkItemProcessor.

Автор: AI Assistant
Дата: 20 мая 2025
"""

from typing import List, Optional, Tuple, Dict, Any
from advising_platform.src.core.registry.task_registry import WorkItem, WorkItemType


def find_similar_items(
    self,
    title: str,
    type: Optional[WorkItemType] = None,
    threshold: float = 0.7
) -> List[Tuple[WorkItem, float]]:
    """
    Находит элементы с похожими названиями.
    
    Args:
        title: Название для поиска
        type: Тип элемента для фильтрации
        threshold: Минимальная степень сходства (от 0 до 1)
        
    Returns:
        Список кортежей (элемент, степень сходства)
    """
    if not title:
        return []
    
    # Преобразуем заголовок в нижний регистр для регистронезависимого поиска
    title_lower = title.lower()
    
    similar_items = []
    for item in self.items.values():
        # Фильтруем по типу, если указан
        if type and item.type != type:
            continue
        
        # Вычисляем простую степень сходства на основе общих слов
        item_title_lower = item.title.lower()
        
        # Простое вычисление сходства
        similarity = compute_similarity(title_lower, item_title_lower)
        
        # Добавляем элемент, если сходство превышает порог
        if similarity >= threshold:
            similar_items.append((item, similarity))
    
    # Сортируем по убыванию степени сходства
    similar_items.sort(key=lambda x: x[1], reverse=True)
    
    # Ограничиваем количество результатов
    return similar_items[:5]


def compute_similarity(text1: str, text2: str) -> float:
    """
    Вычисляет степень сходства между двумя строками.
    
    Args:
        text1: Первая строка
        text2: Вторая строка
        
    Returns:
        Степень сходства (от 0 до 1)
    """
    # Разбиваем строки на слова
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    # Если одна из строк пуста, возвращаем 0
    if not words1 or not words2:
        return 0.0
    
    # Вычисляем количество общих слов
    common_words = words1.intersection(words2)
    
    # Вычисляем коэффициент Жаккара
    similarity = len(common_words) / (len(words1) + len(words2) - len(common_words))
    
    # Дополнительно учитываем вхождение одной строки в другую
    if text1 in text2 or text2 in text1:
        similarity += 0.3
        similarity = min(1.0, similarity)  # Не больше 1
    
    return similarity