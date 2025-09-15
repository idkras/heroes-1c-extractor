#!/usr/bin/env python3
"""
Триггер для автоматической валидации стандартов при их создании/обновлении.

Интегрируется с системой событий для запуска TDD тестов при изменении файлов стандартов.
Обеспечивает соответствие Task Master и Registry требованиям.

Автор: AI Assistant
Дата: 25 May 2025
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Добавляем путь к тестам
sys.path.append(os.path.join(os.path.dirname(__file__), '../../tests/tdd_cycles/current'))

try:
    from test_standard_validation_tdd import StandardValidationTrigger
except ImportError as e:
    logging.error(f"Не удалось импортировать TDD тесты: {e}")
    StandardValidationTrigger = None

logger = logging.getLogger(__name__)


class StandardEditTrigger:
    """
    Триггер для валидации стандартов при редактировании.
    """
    
    def __init__(self):
        """Инициализация триггера."""
        self.validator = StandardValidationTrigger() if StandardValidationTrigger else None
        self.standards_patterns = [
            "standards .md",
            "standard",
            ".md"
        ]
    
    def is_standard_file(self, file_path: str) -> bool:
        """
        Определяет, является ли файл стандартом.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            bool: True, если файл является стандартом
        """
        file_path_lower = file_path.lower()
        
        # Проверяем по паттернам
        is_in_standards_dir = "standards .md" in file_path
        is_markdown = file_path.endswith('.md')
        has_standard_in_name = "standard" in file_path_lower
        
        return is_in_standards_dir and is_markdown and has_standard_in_name
    
    def validate_on_edit(self, file_path: str) -> Dict[str, Any]:
        """
        Запускает валидацию при редактировании стандарта.
        
        Args:
            file_path: Путь к отредактированному файлу
            
        Returns:
            Dict с результатами валидации
        """
        if not self.is_standard_file(file_path):
            return {
                'is_standard': False,
                'message': 'Файл не является стандартом'
            }
        
        if not self.validator:
            return {
                'is_standard': True,
                'error': 'TDD валидатор недоступен',
                'passed': False
            }
        
        logger.info(f"🧪 Запуск TDD валидации для стандарта: {file_path}")
        
        try:
            results = self.validator.validate_standard(file_path)
            results['is_standard'] = True
            
            # Логируем результаты
            if results['passed']:
                logger.info(f"✅ Стандарт {file_path} прошел валидацию")
            else:
                logger.warning(f"❌ Стандарт {file_path} не прошел валидацию:")
                for feedback in results['feedback']:
                    logger.warning(f"   {feedback}")
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при валидации стандарта {file_path}: {e}")
            return {
                'is_standard': True,
                'error': str(e),
                'passed': False
            }
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """
        Генерирует отчет по валидации для вывода пользователю.
        
        Args:
            results: Результаты валидации
            
        Returns:
            str: Отформатированный отчет
        """
        if not results.get('is_standard'):
            return "ℹ️ Файл не является стандартом, валидация не требуется"
        
        if results.get('error'):
            return f"❌ Ошибка валидации: {results['error']}"
        
        if results.get('passed'):
            return "✅ Стандарт соответствует всем требованиям Task Master и Registry"
        
        report = ["❌ Стандарт не соответствует требованиям:"]
        report.extend([f"   {feedback}" for feedback in results.get('feedback', [])])
        
        report.append(f"\n📊 Статистика: {results.get('failures', 0)} провалено из {results.get('total_tests', 0)} тестов")
        
        return "\n".join(report)


def main():
    """Демонстрация работы триггера."""
    trigger = StandardEditTrigger()
    
    test_file = "[standards .md]/3. scenarium · jtbd · hipothises · offering · tone/2.0 jtbd scenarium standard 14 may 2025 0730 cet by ai assistant.md"
    
    print("🚀 Демонстрация Standard Validation Trigger")
    print("=" * 50)
    
    results = trigger.validate_on_edit(test_file)
    report = trigger.generate_validation_report(results)
    
    print(report)
    
    return 0 if results.get('passed', False) else 1


if __name__ == "__main__":
    exit(main())