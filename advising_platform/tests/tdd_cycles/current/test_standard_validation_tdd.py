#!/usr/bin/env python3
"""
TDD тесты для валидации стандартов согласно Task Master и Registry требованиям.

Цель: Обеспечить автоматическую проверку соответствия стандартов базовым требованиям
при их создании, обновлении и редактировании.

Принципы TDD:
1. Red: тест проваливается для несоответствующих стандартов
2. Green: тест проходит для корректных стандартов  
3. Refactor: улучшение логики валидации

Автор: AI Assistant
Дата: 25 May 2025
"""

import os
import re
import unittest
from pathlib import Path
from typing import Dict, List, Tuple, Any


class StandardValidationTDD(unittest.TestCase):
    """
    TDD тесты для валидации структуры и содержимого стандартов.
    """
    
    def setUp(self):
        """Подготовка тестовых данных."""
        self.standards_dir = Path("[standards .md]")
        self.test_standard_path = "[standards .md]/3. scenarium · jtbd · hipothises · offering · tone/jtbd scenarium standard 25 may 2025 2140 cet by ai assistant.md"
        
    def test_standard_has_required_metadata_fields(self):
        """
        RED→GREEN: Стандарт должен содержать все обязательные поля метаданных.
        """
        required_fields = [
            'type: standard',
            'standard_id:',
            'logical_id:',
            'updated:',
            'based on:',
            'version:',
            'status:'
        ]
        
        content = self._read_standard_content()
        protected_section = self._extract_protected_section(content)
        
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, protected_section, 
                            f"Обязательное поле '{field}' отсутствует в метаданных")
    
    def test_standard_has_license_section(self):
        """
        RED→GREEN: Стандарт должен содержать секцию лицензии после метаданных.
        """
        content = self._read_standard_content()
        
        # Проверяем наличие секции лицензии
        license_patterns = [
            r"## 📜 Лицензия и условия использования",
            r"Лицензия.*:",
            r"Creative Commons|CC BY-SA|MIT License|Apache License"
        ]
        
        has_license = any(re.search(pattern, content, re.IGNORECASE) 
                         for pattern in license_patterns)
        
        self.assertTrue(has_license, 
                       "Секция лицензии отсутствует или неправильно оформлена")
    
    def test_standard_title_has_emoji(self):
        """
        RED→GREEN: Заголовок стандарта должен содержать эмодзи.
        """
        content = self._read_standard_content()
        title_match = re.search(r'^# (.+)', content, re.MULTILINE)
        
        self.assertIsNotNone(title_match, "Заголовок стандарта не найден")
        
        title = title_match.group(1) if title_match else ""
        has_emoji = any(ord(char) > 127 for char in title)
        
        self.assertTrue(has_emoji, 
                       f"Заголовок '{title}' должен содержать эмодзи")
    
    def test_standard_has_goal_section(self):
        """
        RED→GREEN: Стандарт должен содержать секцию цели документа.
        """
        content = self._read_standard_content()
        
        goal_patterns = [
            r"## 🎯 Цель документа",
            r"## 🎯 Цель стандарта",
            r"## Цель"
        ]
        
        has_goal = any(re.search(pattern, content) for pattern in goal_patterns)
        
        self.assertTrue(has_goal, 
                       "Секция цели документа отсутствует")
    
    def test_standard_filename_format(self):
        """
        RED→GREEN: Название файла должно соответствовать формату стандарта.
        """
        filename = os.path.basename(self.test_standard_path)
        
        # Проверяем базовые требования к названию
        self.assertTrue(filename.endswith('.md'), 
                       "Файл должен иметь расширение .md")
        
        # Проверяем наличие даты в названии
        date_pattern = r'\d{1,2}\s+\w+\s+\d{4}'
        has_date = re.search(date_pattern, filename)
        
        self.assertIsNotNone(has_date, 
                           "Название файла должно содержать дату")
        
        # Проверяем наличие автора
        author_pattern = r'by\s+[\w\s]+\.md$'
        has_author = re.search(author_pattern, filename)
        
        self.assertIsNotNone(has_author, 
                           "Название файла должно содержать автора")
    
    def test_standard_has_proper_abstract_links(self):
        """
        RED→GREEN: Ссылки на другие стандарты должны использовать abstract:// формат.
        """
        content = self._read_standard_content()
        
        # Ищем упоминания стандартов без abstract ссылок
        standard_mentions = re.findall(
            r'[Tt]ask [Mm]aster [Ss]tandard(?!\]\(abstract://)',
            content
        )
        
        self.assertEqual(len(standard_mentions), 0,
                        f"Найдены упоминания Task Master Standard без abstract:// ссылок: {standard_mentions}")
        
        # Проверяем корректность abstract ссылок
        abstract_links = re.findall(r'abstract://[\w:/.]+', content)
        
        for link in abstract_links:
            with self.subTest(link=link):
                self.assertTrue(link.startswith('abstract://'),
                              f"Некорректная abstract ссылка: {link}")
    
    def test_standard_checklist_completion(self):
        """
        RED→GREEN: Проверка выполнения чеклиста Task Master для стандартов.
        """
        content = self._read_standard_content()
        
        # Чеклист из Task Master
        checklist_items = [
            "секция лицензия и условия использования",
            "эмодзи в заголовке", 
            "метаданные в protected section",
            "цель документа",
            "abstract ссылки на стандарты"
        ]
        
        results = {}
        
        # Лицензия
        results["лицензия"] = bool(re.search(r"лицензи|license", content, re.IGNORECASE))
        
        # Эмодзи в заголовке
        title_match = re.search(r'^# (.+)', content, re.MULTILINE)
        results["эмодзи"] = bool(title_match and any(ord(char) > 127 for char in title_match.group(1)))
        
        # Protected section
        results["метаданные"] = bool(re.search(r'PROTECTED SECTION', content))
        
        # Цель документа
        results["цель"] = bool(re.search(r'🎯.*[Цц]ель', content))
        
        # Abstract ссылки
        results["abstract_ссылки"] = bool(re.search(r'abstract://', content))
        
        # Проверяем все пункты чеклиста
        failed_items = [item for item, passed in results.items() if not passed]
        
        self.assertEqual(len(failed_items), 0,
                        f"Не выполнены пункты чеклиста: {failed_items}")
    
    def _read_standard_content(self) -> str:
        """Читает содержимое стандарта."""
        try:
            with open(self.test_standard_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.fail(f"Файл стандарта не найден: {self.test_standard_path}")
        except Exception as e:
            self.fail(f"Ошибка чтения файла: {e}")
    
    def _extract_protected_section(self, content: str) -> str:
        """Извлекает содержимое защищенной секции."""
        pattern = r'<!-- 🔒 PROTECTED SECTION: BEGIN -->(.*?)<!-- 🔒 PROTECTED SECTION: END -->'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            self.fail("Protected section не найдена")
        
        return match.group(1)


class StandardValidationTrigger:
    """
    Триггер для автоматической валидации стандартов при их обновлении.
    """
    
    def __init__(self):
        self.test_suite = unittest.TestLoader().loadTestsFromTestCase(StandardValidationTDD)
    
    def validate_standard(self, standard_path: str) -> Dict[str, Any]:
        """
        Запускает валидацию стандарта и возвращает результаты.
        
        Args:
            standard_path: Путь к файлу стандарта
            
        Returns:
            Dict с результатами валидации
        """
        # Обновляем путь в экземпляре тестового класса
        StandardValidationTDD.test_standard_path = standard_path
        
        # Запускаем тесты
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(self.test_suite)
        
        return {
            'passed': result.wasSuccessful(),
            'total_tests': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'failed_tests': [test.id() for test, _ in result.failures + result.errors],
            'feedback': self._generate_feedback(result)
        }
    
    def _generate_feedback(self, result) -> List[str]:
        """Генерирует фидбек по результатам тестов."""
        feedback = []
        
        if result.wasSuccessful():
            feedback.append("✅ Стандарт соответствует всем требованиям")
        else:
            feedback.append("❌ Обнаружены нарушения требований:")
            
            for test, traceback in result.failures + result.errors:
                test_name = test.id().split('.')[-1]
                
                if 'metadata' in test_name:
                    feedback.append("  • Отсутствуют обязательные поля метаданных")
                elif 'license' in test_name:
                    feedback.append("  • Отсутствует секция лицензии")
                elif 'emoji' in test_name:
                    feedback.append("  • Заголовок не содержит эмодзи")
                elif 'goal' in test_name:
                    feedback.append("  • Отсутствует секция цели документа")
                elif 'filename' in test_name:
                    feedback.append("  • Неверный формат названия файла")
                elif 'abstract' in test_name:
                    feedback.append("  • Ссылки на стандарты не используют abstract:// формат")
                elif 'checklist' in test_name:
                    feedback.append("  • Не выполнен чеклист Task Master")
        
        return feedback


def main():
    """Запуск валидации стандарта."""
    validator = StandardValidationTrigger()
    
    standard_path = "[standards .md]/3. scenarium · jtbd · hipothises · offering · tone/2.0 jtbd scenarium standard 14 may 2025 0730 cet by ai assistant.md"
    
    print("🧪 Запуск TDD валидации стандарта...")
    print("=" * 60)
    
    results = validator.validate_standard(standard_path)
    
    print(f"📊 Результаты тестирования:")
    print(f"   Всего тестов: {results['total_tests']}")
    print(f"   Провалено: {results['failures']}")
    print(f"   Ошибок: {results['errors']}")
    print(f"   Статус: {'✅ ПРОЙДЕН' if results['passed'] else '❌ ПРОВАЛЕН'}")
    
    print("\n💬 Фидбек:")
    for item in results['feedback']:
        print(f"   {item}")
    
    if not results['passed']:
        print(f"\n🔧 Проваленные тесты: {results['failed_tests']}")
        
    return 0 if results['passed'] else 1


if __name__ == "__main__":
    exit(main())