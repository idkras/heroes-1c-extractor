#!/usr/bin/env python3
"""
Скрипт для анализа стандартов и проверки соответствия требованиям мини-манифеста.

Автоматически проверяет стандарты из указанной директории на наличие всех необходимых
разделов мини-манифеста, формирует отчет о соответствии и предлагает рекомендации по улучшению.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import sys
import json
import argparse
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("analyze_standards")

# Импортируем модуль стандартных манифестов
try:
    from advising_platform.src.core.standards.standard_manifest import (
        StandardManifest,
        StandardManifestValidator,
        ManifestSectionType
    )
except ImportError:
    # В случае запуска вне основного проекта
    # Добавляем путь к проекту
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(script_dir)
    
    try:
        from advising_platform.src.core.standards.standard_manifest import (
            StandardManifest,
            StandardManifestValidator,
            ManifestSectionType
        )
    except ImportError:
        logger.error("Не удалось импортировать модуль StandardManifest")
        sys.exit(1)


class StandardsAnalyzer:
    """Анализатор стандартов для проверки соответствия требованиям мини-манифеста."""
    
    def __init__(self, standards_dir: str = "[standards .md]"):
        """
        Инициализация анализатора.
        
        Args:
            standards_dir: Путь к директории со стандартами
        """
        self.standards_dir = standards_dir
        self.validator = StandardManifestValidator(base_dir=standards_dir)
        self.results = {}
        self.summary = {}
    
    def analyze(self) -> Dict[str, Any]:
        """
        Анализирует все стандарты в указанной директории.
        
        Returns:
            Словарь с результатами анализа
        """
        logger.info(f"Начинаем анализ стандартов в директории {self.standards_dir}")
        
        # Проверяем существование директории
        if not os.path.exists(self.standards_dir):
            logger.error(f"Директория {self.standards_dir} не существует")
            return {"error": f"Директория {self.standards_dir} не существует"}
        
        # Получаем результаты проверки
        self.results = self.validator.validate_directory(self.standards_dir)
        
        # Формируем отчет
        report = self.validator.generate_validation_report(self.standards_dir)
        
        # Добавляем дополнительную статистику и рекомендации
        report = self._enhance_report(report)
        
        logger.info(f"Анализ завершен. Проверено {report['total_files']} файлов")
        return report
    
    def _enhance_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Дополняет отчет дополнительной статистикой и рекомендациями.
        
        Args:
            report: Исходный отчет
            
        Returns:
            Дополненный отчет
        """
        # Категории стандартов
        categories = self._categorize_standards()
        report["categories"] = categories
        
        # Анализ качества контента
        quality_metrics = self._analyze_content_quality()
        report["quality_metrics"] = quality_metrics
        
        # Связи между стандартами
        relationships = self._analyze_relationships()
        report["relationships"] = relationships
        
        # Топ проблемных стандартов
        if report["invalid_files"] > 0:
            problem_files = sorted(
                [(file_path, len(details["missing_sections"])) 
                 for file_path, details in report["invalid_file_details"].items()],
                key=lambda x: x[1],
                reverse=True
            )
            report["top_problem_files"] = problem_files[:5]
        
        # Рекомендации по улучшению
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _categorize_standards(self) -> Dict[str, int]:
        """
        Категоризирует стандарты по директориям.
        
        Returns:
            Словарь {категория: количество стандартов}
        """
        categories = {}
        
        for file_path in self.results.keys():
            # Определяем категорию по поддиректории
            relative_path = os.path.relpath(file_path, self.standards_dir)
            category = os.path.dirname(relative_path).split(os.path.sep)[0]
            
            if not category:
                category = "Без категории"
            
            # Увеличиваем счетчик для категории
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
        
        return categories
    
    def _analyze_content_quality(self) -> Dict[str, Any]:
        """
        Анализирует качество контента стандартов.
        
        Returns:
            Словарь с метриками качества
        """
        total_words = 0
        section_words = {
            "purpose": 0,
            "pain": 0,
            "relations": 0,
            "consequences": 0,
            "other": 0
        }
        standards_count = 0
        
        # Обходим все файлы
        for file_path, is_valid in self.results.items():
            # Читаем содержимое файла
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Создаем манифест
                manifest = StandardManifest.from_markdown(content, file_path)
                standards_count += 1
                
                # Анализируем разделы
                if manifest.purpose:
                    words = len(manifest.purpose.content.split())
                    total_words += words
                    section_words["purpose"] += words
                
                if manifest.pain:
                    words = len(manifest.pain.content.split())
                    total_words += words
                    section_words["pain"] += words
                
                if manifest.relations:
                    words = len(manifest.relations.content.split())
                    total_words += words
                    section_words["relations"] += words
                
                if manifest.consequences:
                    words = len(manifest.consequences.content.split())
                    total_words += words
                    section_words["consequences"] += words
                
                # Подсчитываем слова в остальном контенте
                all_sections_content = ""
                if manifest.purpose:
                    all_sections_content += manifest.purpose.content
                if manifest.pain:
                    all_sections_content += manifest.pain.content
                if manifest.relations:
                    all_sections_content += manifest.relations.content
                if manifest.consequences:
                    all_sections_content += manifest.consequences.content
                
                # Убираем контент разделов из общего контента
                other_content = content
                for section_content in all_sections_content.split("\n"):
                    other_content = other_content.replace(section_content, "")
                
                # Подсчитываем оставшиеся слова
                other_words = len(other_content.split())
                total_words += other_words
                section_words["other"] += other_words
                
            except Exception as e:
                logger.warning(f"Ошибка при анализе контента файла {file_path}: {e}")
        
        # Формируем метрики
        metrics = {
            "total_words": total_words,
            "average_words_per_standard": total_words / standards_count if standards_count > 0 else 0,
            "section_words": section_words,
            "section_percentage": {
                section: (count / total_words * 100) if total_words > 0 else 0
                for section, count in section_words.items()
            }
        }
        
        return metrics
    
    def _analyze_relationships(self) -> Dict[str, Any]:
        """
        Анализирует связи между стандартами.
        
        Returns:
            Словарь со связями между стандартами
        """
        # Словарь для хранения связей {стандарт: [связанные стандарты]}
        relationships = {}
        
        # Словарь для хранения имен стандартов {путь: название}
        standard_names = {}
        
        # Обходим все файлы
        for file_path, is_valid in self.results.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Создаем манифест
                manifest = StandardManifest.from_markdown(content, file_path)
                
                # Сохраняем название стандарта
                standard_names[file_path] = manifest.title
                
                # Анализируем раздел связей
                if manifest.relations:
                    related_standards = self._extract_related_standards(manifest.relations.content)
                    
                    # Сохраняем найденные связи
                    if related_standards:
                        relationships[file_path] = related_standards
            
            except Exception as e:
                logger.warning(f"Ошибка при анализе связей для файла {file_path}: {e}")
        
        # Формируем результат
        result = {
            "standard_names": standard_names,
            "explicit_relationships": relationships,
            "statistics": {
                "standards_with_relationships": len(relationships),
                "total_relationships": sum(len(related) for related in relationships.values())
            }
        }
        
        return result
    
    def _extract_related_standards(self, relations_content: str) -> List[str]:
        """
        Извлекает названия связанных стандартов из раздела связей.
        
        Args:
            relations_content: Содержимое раздела связей
            
        Returns:
            Список названий связанных стандартов
        """
        related_standards = []
        
        # Ищем упоминания стандартов в формате "Стандарт X" или строки в кавычках
        lines = relations_content.split("\n")
        for line in lines:
            # Ищем названия стандартов в кавычках
            import re
            quoted_standards = re.findall(r'"([^"]*)"', line)
            quoted_standards.extend(re.findall(r'"([^"]*)"', line))
            
            # Ищем слово "стандарт" с последующим текстом
            standard_mentions = re.findall(r'[Сс]тандарт\s+([^,.;:]+)', line)
            
            # Добавляем найденные стандарты
            related_standards.extend(quoted_standards)
            related_standards.extend(standard_mentions)
        
        # Удаляем дубликаты и пустые строки
        return list(set(filter(bool, related_standards)))
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """
        Генерирует рекомендации по улучшению стандартов.
        
        Args:
            report: Отчет о проверке
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации по недостающим разделам
        if report["invalid_files"] > 0:
            recommendations.append(
                f"Дополнить {report['invalid_files']} стандартов недостающими разделами мини-манифеста"
            )
            
            # Анализируем, какие разделы чаще всего отсутствуют
            missing_sections_count = {}
            for details in report["invalid_file_details"].values():
                for section in details["missing_sections"]:
                    if section in missing_sections_count:
                        missing_sections_count[section] += 1
                    else:
                        missing_sections_count[section] = 1
            
            most_missing = sorted(
                missing_sections_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            if most_missing:
                recommendations.append(
                    f"Уделить особое внимание разделу '{most_missing[0][0]}', который отсутствует в {most_missing[0][1]} стандартах"
                )
        
        # Рекомендации по качеству контента
        if "quality_metrics" in report:
            metrics = report["quality_metrics"]
            avg_words = metrics["average_words_per_standard"]
            
            if avg_words < 100:
                recommendations.append(
                    f"Расширить содержание стандартов. Текущий средний объем ({avg_words:.0f} слов) недостаточен для полного описания"
                )
            
            # Проверяем баланс разделов
            section_percentage = metrics["section_percentage"]
            if section_percentage["purpose"] < 10:
                recommendations.append(
                    "Улучшить описание целей стандартов в разделе 'Зачем нужен стандарт'"
                )
            
            if section_percentage["pain"] < 10:
                recommendations.append(
                    "Детальнее описать проблемы, которые решают стандарты, в разделе 'Какая боль его вызвала'"
                )
            
            if section_percentage["relations"] < 5:
                recommendations.append(
                    "Уточнить связи между стандартами в разделе 'Какие стандарты он отменяет или дополняет'"
                )
            
            if section_percentage["consequences"] < 10:
                recommendations.append(
                    "Подробнее описать последствия несоблюдения в разделе 'Что будет, если его не соблюдать'"
                )
        
        # Рекомендации по связям
        if "relationships" in report:
            rel_stats = report["relationships"]["statistics"]
            standards_with_rel = rel_stats["standards_with_relationships"]
            total_files = report["total_files"]
            
            if standards_with_rel < total_files / 2:
                recommendations.append(
                    f"Улучшить описание связей между стандартами. Только {standards_with_rel} из {total_files} стандартов содержат явные ссылки на другие стандарты"
                )
        
        # Общие рекомендации
        recommendations.append(
            "Регулярно проводить обзор и обновление стандартов на соответствие текущим потребностям"
        )
        
        return recommendations
    
    def generate_html_report(self, report: Dict[str, Any], output_file: str = "standards_report.html") -> str:
        """
        Генерирует HTML-отчет о результатах анализа.
        
        Args:
            report: Результаты анализа
            output_file: Путь к выходному файлу
            
        Returns:
            Путь к сохраненному файлу отчета
        """
        # Формируем HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по анализу стандартов</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
            flex: 1 1 300px;
        }}
        .stats {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}
        .stat-box {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            flex: 1 1 200px;
            margin: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2980b9;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .progress-bar {{
            background-color: #ecf0f1;
            border-radius: 4px;
            height: 20px;
            width: 100%;
            margin: 10px 0;
        }}
        .progress-fill {{
            background-color: #3498db;
            height: 100%;
            border-radius: 4px;
            text-align: center;
            color: white;
            font-size: 12px;
            line-height: 20px;
        }}
        .recommendations {{
            background-color: #fdebd0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f39c12;
        }}
        .recommendations h3 {{
            color: #d35400;
            margin-top: 0;
        }}
        .recommendations ul {{
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <h1>Отчет по анализу стандартов</h1>
    <p>Дата анализа: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    
    <div class="stats">
        <div class="stat-box">
            <div class="stat-label">Всего стандартов</div>
            <div class="stat-value">{report['total_files']}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Соответствуют требованиям</div>
            <div class="stat-value">{report['valid_files']}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Требуют доработки</div>
            <div class="stat-value">{report['invalid_files']}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Уровень соответствия</div>
            <div class="stat-value">{report['compliance_rate']*100:.1f}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {report['compliance_rate']*100}%"></div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Распределение по категориям</h2>
            <table>
                <tr>
                    <th>Категория</th>
                    <th>Количество</th>
                </tr>
                {
                    ''.join([
                        f'<tr><td>{category}</td><td>{count}</td></tr>' 
                        for category, count in report['categories'].items()
                    ])
                }
            </table>
        </div>
        
        <div class="card">
            <h2>Качество контента</h2>
            <p>Общее количество слов: {report['quality_metrics']['total_words']}</p>
            <p>Среднее количество слов на стандарт: {report['quality_metrics']['average_words_per_standard']:.1f}</p>
            
            <h3>Распределение контента по разделам</h3>
            <table>
                <tr>
                    <th>Раздел</th>
                    <th>Слов</th>
                    <th>Процент</th>
                </tr>
                {
                    ''.join([
                        f'<tr><td>{section.capitalize()}</td><td>{count}</td><td>{report["quality_metrics"]["section_percentage"][section]:.1f}%</td></tr>' 
                        for section, count in report['quality_metrics']['section_words'].items()
                    ])
                }
            </table>
        </div>
    </div>
    
    <div class="card">
        <h2>Стандарты, требующие доработки</h2>
        {
            f'<p>Все стандарты соответствуют требованиям мини-манифеста.</p>'
            if report['invalid_files'] == 0 else
            f'''
            <table>
                <tr>
                    <th>Стандарт</th>
                    <th>Отсутствующие разделы</th>
                </tr>
                {''.join([
                    f'<tr><td>{os.path.basename(file_path)}</td><td>{", ".join(report["invalid_file_details"][file_path]["missing_sections"])}</td></tr>' 
                    for file_path in list(report["invalid_file_details"].keys())[:10]
                ])}
                {f'<tr><td colspan="2">...и еще {len(report["invalid_file_details"]) - 10} стандартов</td></tr>' if len(report["invalid_file_details"]) > 10 else ''}
            </table>
            '''
        }
    </div>
    
    <div class="card">
        <h2>Связи между стандартами</h2>
        <p>Количество стандартов с явными связями: {report['relationships']['statistics']['standards_with_relationships']}</p>
        <p>Общее количество связей: {report['relationships']['statistics']['total_relationships']}</p>
        
        {
            f'''
            <h3>Топ-5 стандартов с наибольшим количеством связей</h3>
            <table>
                <tr>
                    <th>Стандарт</th>
                    <th>Количество связей</th>
                </tr>
                {''.join([
                    f'<tr><td>{report["relationships"]["standard_names"].get(file_path, os.path.basename(file_path))}</td><td>{len(relations)}</td></tr>' 
                    for file_path, relations in sorted(
                        report['relationships']['explicit_relationships'].items(), 
                        key=lambda x: len(x[1]), 
                        reverse=True
                    )[:5]
                ])}
            </table>
            ''' if report['relationships']['explicit_relationships'] else '<p>Не найдено явных связей между стандартами.</p>'
        }
    </div>
    
    <div class="recommendations">
        <h3>Рекомендации по улучшению</h3>
        <ul>
            {
                ''.join([f'<li>{recommendation}</li>' for recommendation in report['recommendations']])
            }
        </ul>
    </div>
</body>
</html>
"""
        
        # Сохраняем в файл
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        logger.info(f"HTML-отчет сохранен в файл {output_file}")
        return output_file


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Анализ стандартов на соответствие требованиям мини-манифеста")
    
    parser.add_argument(
        "--dir", 
        "-d", 
        default="[standards .md]", 
        help="Директория со стандартами для анализа (по умолчанию: [standards .md])"
    )
    
    parser.add_argument(
        "--output", 
        "-o", 
        default="standards_report.html", 
        help="Путь к выходному HTML-файлу отчета (по умолчанию: standards_report.html)"
    )
    
    parser.add_argument(
        "--json", 
        "-j", 
        default=None, 
        help="Путь к выходному JSON-файлу с детальными результатами анализа (опционально)"
    )
    
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Включить подробное логирование"
    )
    
    args = parser.parse_args()
    
    # Настраиваем уровень логирования
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Создаем анализатор
        analyzer = StandardsAnalyzer(standards_dir=args.dir)
        
        # Запускаем анализ
        report = analyzer.analyze()
        
        # Сохраняем JSON, если нужно
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON-отчет сохранен в файл {args.json}")
        
        # Генерируем HTML-отчет
        html_path = analyzer.generate_html_report(report, output_file=args.output)
        
        print(f"\nАнализ завершен. Результаты:")
        print(f"- Проверено стандартов: {report['total_files']}")
        print(f"- Соответствуют требованиям: {report['valid_files']} ({report['compliance_rate']*100:.1f}%)")
        print(f"- Требуют доработки: {report['invalid_files']}")
        print(f"\nОтчет сохранен в файл: {html_path}")
        
        if args.json:
            print(f"Детальные результаты сохранены в: {args.json}")
        
        # Выводим топ-3 рекомендации
        if "recommendations" in report and report["recommendations"]:
            print("\nОсновные рекомендации:")
            for i, recommendation in enumerate(report["recommendations"][:3], 1):
                print(f"{i}. {recommendation}")
    
    except Exception as e:
        logger.exception(f"Ошибка при выполнении анализа: {e}")
        print(f"Произошла ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())