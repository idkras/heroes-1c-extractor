#!/usr/bin/env python3
"""
Модуль для проверки соответствия гипотез стандарту.
"""

import re
import logging

logger = logging.getLogger("hypothesis_validator")


class HypothesisValidator:
    """
    Валидатор гипотез, проверяющий соответствие документа стандарту гипотез.
    """

    def __init__(self):
        """
        Инициализирует валидатор гипотез.
        """
        # Обязательные разделы гипотезы
        self.required_sections = [
            r"## [🧪📝] Метаданные гипотезы",
            r"(ID|Автор|Дата создания|Последнее обновление|Статус|Приоритет)",
            r"## [🧪🧩] Формулировка гипотезы",
            r"(Мы верим, что|Мы поймем, что это правда)",
            r"## [🧪🔍] Метод проверки гипотезы"
        ]
        
        # Шаблоны для проверки формулировки гипотезы
        self.hypothesis_patterns = {
            "базовый_формат": r"Мы верим, что\s+.+\s+для\s+.+\s+приведет к\s+.+\.",
            "критерий_успеха": r"Мы поймем, что это правда, когда увидим\s+.+\."
        }
        
        # Критерии качественной гипотезы
        self.quality_criteria = [
            "Конкретность",
            "Тестируемость",
            "Фальсифицируемость",
            "Основанность на данных",
            "Причинно-следственная связь",
            "Временное ограничение",
            "Компактность"
        ]

    def extract_hypothesis_sections(self, content):
        """
        Извлекает основные секции из документа гипотезы.
        
        Args:
            content (str): Содержимое документа
            
        Returns:
            dict: Словарь с извлеченными секциями
        """
        sections = {}
        
        # Извлечение метаданных
        metadata_match = re.search(r"## [🧪📝]?\s*Метаданные гипотезы\s*```(.*?)```", 
                                 content, re.DOTALL)
        if metadata_match:
            sections["metadata"] = metadata_match.group(1).strip()
        
        # Извлечение формулировки гипотезы
        hypothesis_match = re.search(r"## [🧪🧩]?\s*Формулировка гипотезы.*?\*\*Мы верим, что\*\*\s*(.*?)\*\*для\*\*\s*(.*?)\*\*приведет к\*\*\s*(.*?)[.\n]", 
                                  content, re.DOTALL)
        if hypothesis_match:
            sections["hypothesis"] = {
                "action": hypothesis_match.group(1).strip(),
                "user_segment": hypothesis_match.group(2).strip(),
                "expected_result": hypothesis_match.group(3).strip()
            }
        
        # Извлечение критерия успеха
        success_match = re.search(r"\*\*Мы поймем, что это правда, когда увидим\*\*\s*(.*?)[.\n]", 
                               content, re.DOTALL)
        if success_match:
            sections["success_criteria"] = success_match.group(1).strip()
        
        # Извлечение метода проверки
        method_match = re.search(r"## [🧪🔍]?\s*Метод проверки гипотезы(.*?)(?:##|\Z)", 
                              content, re.DOTALL)
        if method_match:
            sections["verification_method"] = method_match.group(1).strip()
        
        return sections

    def validate_hypothesis(self, content):
        """
        Проверяет соответствие документа стандарту гипотез.
        
        Args:
            content (str): Содержимое документа
            
        Returns:
            dict: Результат проверки с комментариями
        """
        result = {
            "is_valid": True,
            "missing_sections": [],
            "issues": [],
            "suggestions": [],
            "extracted_sections": self.extract_hypothesis_sections(content)
        }
        
        # Проверка наличия обязательных разделов
        for section_pattern in self.required_sections:
            if not re.search(section_pattern, content, re.IGNORECASE):
                result["is_valid"] = False
                result["missing_sections"].append(section_pattern)
        
        # Проверка формата формулировки гипотезы
        for pattern_name, pattern in self.hypothesis_patterns.items():
            if not re.search(pattern, content, re.IGNORECASE):
                result["is_valid"] = False
                result["issues"].append(f"Отсутствует или некорректно оформлен элемент: {pattern_name}")
        
        # Проверка наличия метрик
        if not re.search(r"[0-9]+%|с\s+[0-9]+\s+до\s+[0-9]+", content):
            result["issues"].append("Не указаны числовые метрики для измерения успеха гипотезы")
        
        # Дополнительные проверки качества
        if not re.search(r"Это произойдет, потому что", content, re.IGNORECASE):
            result["suggestions"].append("Рекомендуется добавить раздел с объяснением причинно-следственной связи")
        
        if not re.search(r"Риски и допущения", content, re.IGNORECASE):
            result["suggestions"].append("Рекомендуется добавить раздел с рисками и допущениями")
        
        # Проверка наличия проверки по качественным критериям
        quality_check_found = False
        for criterion in self.quality_criteria:
            if re.search(criterion, content, re.IGNORECASE):
                quality_check_found = True
                break
        
        if not quality_check_found:
            result["suggestions"].append("Рекомендуется добавить проверку гипотезы по критериям качества")
        
        return result

    def generate_report(self, validation_result):
        """
        Формирует отчет о проверке гипотезы.
        
        Args:
            validation_result (dict): Результат проверки
            
        Returns:
            str: Отчет о проверке
        """
        report = "# Отчет о проверке гипотезы\n\n"
        
        if validation_result["is_valid"]:
            report += "## ✅ Гипотеза соответствует стандарту\n\n"
        else:
            report += "## ❌ Гипотеза не соответствует стандарту\n\n"
            report += "### Отсутствующие обязательные разделы:\n\n"
            for section in validation_result["missing_sections"]:
                report += f"- {section.replace(r'[🧪📝]', '')}\n"
            report += "\n"
        
        if validation_result["issues"]:
            report += "### Выявленные проблемы:\n\n"
            for issue in validation_result["issues"]:
                report += f"- {issue}\n"
            report += "\n"
        
        if validation_result["suggestions"]:
            report += "### Рекомендации по улучшению:\n\n"
            for suggestion in validation_result["suggestions"]:
                report += f"- {suggestion}\n"
            report += "\n"
        
        # Добавляем раздел с извлеченной информацией
        sections = validation_result.get("extracted_sections", {})
        if sections:
            report += "## Извлеченная информация\n\n"
            
            if "metadata" in sections:
                report += "### Метаданные\n\n"
                report += f"```\n{sections['metadata']}\n```\n\n"
            
            hypothesis = sections.get("hypothesis", {})
            if hypothesis:
                report += "### Формулировка гипотезы\n\n"
                report += "Мы верим, что "
                report += f"**{hypothesis.get('action', 'не указано')}** для "
                report += f"**{hypothesis.get('user_segment', 'не указано')}** приведет к "
                report += f"**{hypothesis.get('expected_result', 'не указано')}**.\n\n"
            
            if "success_criteria" in sections:
                report += "### Критерий успеха\n\n"
                report += f"Мы поймем, что это правда, когда увидим **{sections['success_criteria']}**.\n\n"
            
            if "verification_method" in sections:
                report += "### Метод проверки\n\n"
                report += f"{sections['verification_method']}\n\n"
        
        return report


# Пример использования
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Использование: python hypothesis_validator.py <путь_к_файлу_гипотезы>")
        sys.exit(1)
    
    # Чтение файла гипотезы
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
    
    validator = HypothesisValidator()
    validation_result = validator.validate_hypothesis(content)
    report = validator.generate_report(validation_result)
    
    print(report)