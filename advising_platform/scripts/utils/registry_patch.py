#!/usr/bin/env python
"""
Скрипт для патчинга TaskRegistry недостающим методом find_similar_items.

Это временное решение для обеспечения возможности создания новых задач,
инцидентов и других рабочих элементов.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import sys
import types
import logging
from typing import List, Optional, Tuple, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("registry_patch")

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

def find_similar_items(self, title: str, type=None, threshold=0.7):
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
    
    # Проверка, что self.items существует и является словарем
    if not hasattr(self, 'items') or not isinstance(self.items, dict):
        logger.warning("TaskRegistry.items отсутствует или не является словарем")
        return []
    
    for item in self.items.values():
        # Фильтруем по типу, если указан
        if type and hasattr(item, 'type') and item.type != type:
            continue
        
        # Проверяем, что у элемента есть атрибут title
        if not hasattr(item, 'title'):
            logger.warning(f"Элемент {item} не имеет атрибута 'title'")
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

def add_method_to_registry():
    """
    Добавляет метод find_similar_items в класс TaskRegistry.
    
    Returns:
        True, если метод успешно добавлен, иначе False
    """
    try:
        from advising_platform.src.core.registry.task_registry import TaskRegistry
        
        # Проверяем, есть ли уже такой метод
        if hasattr(TaskRegistry, 'find_similar_items'):
            logger.info("Метод find_similar_items уже существует в TaskRegistry")
            return True
        
        # Добавляем метод в класс
        TaskRegistry.find_similar_items = find_similar_items
        
        logger.info("Метод find_similar_items успешно добавлен в TaskRegistry")
        return True
    
    except ImportError:
        logger.error("Не удалось импортировать TaskRegistry")
        return False
    except Exception as e:
        logger.error(f"Ошибка при добавлении метода: {e}")
        return False

def patch_registry_instance():
    """
    Патчит экземпляр TaskRegistry, полученный через get_registry().
    
    Returns:
        True, если патч успешно применен, иначе False
    """
    try:
        from advising_platform.src.core.registry.task_registry import get_registry
        
        # Получаем экземпляр реестра
        registry = get_registry()
        
        # Проверяем, есть ли уже такой метод
        if hasattr(registry, 'find_similar_items'):
            logger.info("Метод find_similar_items уже существует в экземпляре TaskRegistry")
            return True
        
        # Добавляем метод в экземпляр
        registry.find_similar_items = types.MethodType(find_similar_items, registry)
        
        logger.info("Метод find_similar_items успешно добавлен в экземпляр TaskRegistry")
        return True
    
    except ImportError:
        logger.error("Не удалось импортировать get_registry")
        return False
    except Exception as e:
        logger.error(f"Ошибка при патчинге экземпляра: {e}")
        return False

def apply_patches():
    """Применяет все патчи."""
    class_patched = add_method_to_registry()
    instance_patched = patch_registry_instance()
    
    if class_patched and instance_patched:
        logger.info("Все патчи успешно применены")
        return True
    else:
        logger.error("Не удалось применить все патчи")
        return False

def main():
    """Основная функция."""
    logger.info("Запуск патчинга TaskRegistry...")
    
    if apply_patches():
        logger.info("Патчинг успешно завершен")
        return 0
    else:
        logger.error("Ошибка при патчинге")
        return 1

if __name__ == "__main__":
    sys.exit(main())