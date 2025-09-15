#!/usr/bin/env python3
"""
Скрипт для проверки соответствия гипотезы стандарту
с использованием валидатора гипотез.
"""

import sys
import os
import sys
import logging

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Импортируем валидатор гипотез
from advising_platform.src.tools.hypothesis_validator import HypothesisValidator

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("check_hypothesis")

def main():
    """
    Основная функция скрипта для проверки гипотезы.
    """
    # Проверяем количество аргументов
    if len(sys.argv) != 2:
        print("Использование: python check_hypothesis.py <путь_к_файлу_гипотезы>")
        sys.exit(1)
    
    # Получаем путь к файлу гипотезы
    hypothesis_path = sys.argv[1]
    
    # Проверяем существование файла
    if not os.path.exists(hypothesis_path):
        logger.error(f"Файл не найден: {hypothesis_path}")
        sys.exit(1)
    
    try:
        # Читаем содержимое файла
        with open(hypothesis_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Создаем экземпляр валидатора
        validator = HypothesisValidator()
        
        # Выполняем проверку гипотезы
        validation_result = validator.validate_hypothesis(content)
        
        # Генерируем отчет
        report = validator.generate_report(validation_result)
        
        # Выводим отчет
        print(report)
        
        # Возвращаем код выхода в зависимости от результата
        if validation_result["is_valid"]:
            return 0
        else:
            return 1
        
    except Exception as e:
        logger.exception(f"Ошибка при проверке гипотезы: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())