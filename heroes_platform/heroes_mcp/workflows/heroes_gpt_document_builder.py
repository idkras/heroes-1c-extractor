#!/usr/bin/env python3
"""
HeroesGPT Document Builder
Генератор markdown документов для HeroesGPT Landing Analysis Standard v1.8

JTBD: Я хочу генерировать профессиональные markdown отчеты по результатам анализа лендингов,
чтобы получать структурированную документацию соответствующую стандарту v1.8.

Features:
- Structured markdown generation
- Standard v1.8 compliance
- Reflection checkpoints integration
- Typography cleanup
- Enhanced validation
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class HeroesGPTDocumentBuilder:
    """Генератор markdown документов для HeroesGPT анализа"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.standard_version = "v1.8"

    def generate_markdown_document(
        self, analysis_data: Dict[str, Any], output_path: str = None  # type: ignore
    ) -> str:
        """Генерирует полный markdown документ из данных анализа

        Args:
            analysis_data: Данные анализа лендинга
            output_path: Путь для сохранения файла (опционально)

        Returns:
            Строка с markdown содержимым
        """
        try:
            # Извлекаем основные данные
            landing_url = analysis_data.get("landing_url", "Unknown URL")
            business_context = analysis_data.get("business_context", {})
            stages = analysis_data.get("stages", {})
            offers = analysis_data.get("offers", [])
            segments = analysis_data.get("segments", [])
            reflections = analysis_data.get("reflections", [])

            # Генерируем markdown
            markdown_content = self._build_document_structure(
                landing_url, business_context, stages, offers, segments, reflections
            )

            # Сохраняем файл если указан путь
            if output_path:
                self._save_markdown_file(markdown_content, output_path)

            return markdown_content

        except Exception as e:
            logger.error(f"Error generating markdown document: {e}")
            return f"# Error\n\nFailed to generate document: {str(e)}"

    def _build_document_structure(
        self,
        landing_url: str,
        business_context: Dict[str, Any],
        stages: Dict[str, Any],
        offers: List[Dict[str, Any]],
        segments: List[Dict[str, Any]],
        reflections: List[Dict[str, Any]],
    ) -> str:
        """Строит структуру markdown документа"""

        # Заголовок и метаданные
        header = self._build_header(landing_url, business_context)

        # Executive Summary
        executive_summary = self._build_executive_summary(stages, offers)

        # Основные разделы анализа
        analysis_sections = self._build_analysis_sections(stages)

        # Предложения и рекомендации
        recommendations = self._build_recommendations(offers, segments)

        # Reflection checkpoints
        reflection_section = self._build_reflection_section(reflections)

        # Заключение
        conclusion = self._build_conclusion(landing_url, stages)

        # Собираем полный документ
        full_document = f"""{header}

{executive_summary}

{analysis_sections}

{recommendations}

{reflection_section}

{conclusion}

---

*Документ сгенерирован HeroesGPT Landing Analysis Standard {self.standard_version}*  
*Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return full_document

    def _build_header(self, landing_url: str, business_context: Dict[str, Any]) -> str:
        """Строит заголовок документа"""
        business_type = business_context.get("type", "Unknown")
        target_audience = business_context.get("target_audience", "Unknown")

        return f"""# HeroesGPT Landing Analysis Report

## Анализируемый лендинг
**URL:** {landing_url}  
**Тип бизнеса:** {business_type}  
**Целевая аудитория:** {target_audience}  
**Стандарт:** HeroesGPT Landing Analysis Standard {self.standard_version}  
**Дата анализа:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

    def _build_executive_summary(
        self, stages: Dict[str, Any], offers: List[Dict[str, Any]]
    ) -> str:
        """Строит executive summary"""
        total_offers = len(offers)
        completed_stages = len([s for s in stages.values() if s.get("completed", False)])

        return f"""## Executive Summary

### Ключевые результаты анализа
- **Всего этапов выполнено:** {completed_stages}
- **Найдено предложений:** {total_offers}
- **Статус анализа:** {'Завершен' if completed_stages > 5 else 'В процессе'}

### Основные выводы
Анализ лендинга проведен в соответствии со стандартом HeroesGPT v1.8. 
Выявлены ключевые предложения и сегменты аудитории для оптимизации конверсии.

---

"""

    def _build_analysis_sections(self, stages: Dict[str, Any]) -> str:
        """Строит разделы анализа"""
        sections = []

        for stage_name, stage_data in stages.items():
            if stage_data.get("completed", False):
                section_content = self._build_stage_section(stage_name, stage_data)
                sections.append(section_content)

        return "\n".join(sections)

    def _build_stage_section(self, stage_name: str, stage_data: Dict[str, Any]) -> str:
        """Строит раздел для конкретного этапа"""
        stage_title = stage_name.replace("_", " ").title()
        timestamp = stage_data.get("timestamp", "Unknown")

        # Извлекаем ключевые результаты этапа
        key_results = self._extract_stage_results(stage_data)

        return f"""## {stage_title}

**Время выполнения:** {timestamp}

### Результаты этапа
{key_results}

---

"""

    def _extract_stage_results(self, stage_data: Dict[str, Any]) -> str:
        """Извлекает ключевые результаты этапа"""
        results = []

        # Ищем ключевые поля в данных этапа
        for key, value in stage_data.items():
            if key in ["offers", "segments", "classification", "analysis"]:
                if isinstance(value, list) and value:
                    results.append(f"- **{key.title()}:** {len(value)} элементов найдено")
                elif isinstance(value, dict) and value:
                    results.append(f"- **{key.title()}:** {len(value)} параметров проанализировано")
                elif isinstance(value, str):
                    results.append(f"- **{key.title()}:** {value}")

        if not results:
            results.append("- Этап выполнен успешно")

        return "\n".join(results)

    def _build_recommendations(
        self, offers: List[Dict[str, Any]], segments: List[Dict[str, Any]]
    ) -> str:
        """Строит раздел рекомендаций"""
        if not offers and not segments:
            return """## Рекомендации

### Статус
Анализ в процессе. Рекомендации будут доступны после завершения всех этапов.

---

"""

        recommendations = ["## Рекомендации"]

        # Рекомендации по предложениям
        if offers:
            recommendations.append("### По предложениям")
            for i, offer in enumerate(offers[:3], 1):  # Показываем первые 3
                offer_type = offer.get("type", "Unknown")
                priority = offer.get("priority", "Medium")
                recommendations.append(f"{i}. **{offer_type}** (Приоритет: {priority})")

        # Рекомендации по сегментам
        if segments:
            recommendations.append("\n### По сегментам аудитории")
            for i, segment in enumerate(segments[:3], 1):  # Показываем первые 3
                segment_name = segment.get("name", "Unknown")
                size = segment.get("size", "Unknown")
                recommendations.append(f"{i}. **{segment_name}** (Размер: {size})")

        recommendations.append("\n---\n")

        return "\n".join(recommendations)

    def _build_reflection_section(self, reflections: List[Dict[str, Any]]) -> str:
        """Строит раздел reflection checkpoints"""
        if not reflections:
            return ""

        reflection_content = ["## Reflection Checkpoints"]

        for i, reflection in enumerate(reflections, 1):
            checkpoint = reflection.get("checkpoint", f"Checkpoint {i}")
            status = reflection.get("status", "Unknown")
            timestamp = reflection.get("timestamp", "Unknown")

            reflection_content.append(f"### {checkpoint}")
            reflection_content.append(f"**Статус:** {status}")
            reflection_content.append(f"**Время:** {timestamp}")

            if reflection.get("notes"):
                reflection_content.append(f"**Заметки:** {reflection['notes']}")

            reflection_content.append("")

        reflection_content.append("---\n")

        return "\n".join(reflection_content)

    def _build_conclusion(self, landing_url: str, stages: Dict[str, Any]) -> str:
        """Строит заключение"""
        completed_stages = len([s for s in stages.values() if s.get("completed", False)])
        total_stages = len(stages)

        return f"""## Заключение

### Результаты анализа
Анализ лендинга {landing_url} проведен в соответствии со стандартом HeroesGPT v1.8.

**Статистика выполнения:**
- Выполнено этапов: {completed_stages}/{total_stages}
- Процент завершения: {(completed_stages/total_stages*100):.1f}%

### Следующие шаги
1. Реализовать выявленные рекомендации
2. Провести A/B тестирование предложений
3. Мониторить метрики конверсии
4. Повторить анализ через 30 дней

### Контакты
Для вопросов по анализу обращайтесь к команде HeroesGPT.

"""

    def _save_markdown_file(self, content: str, output_path: str) -> None:
        """Сохраняет markdown файл"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Markdown document saved to: {output_path}")

        except Exception as e:
            logger.error(f"Error saving markdown file: {e}")
            raise

    def generate_quick_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Генерирует краткое резюме анализа"""
        landing_url = analysis_data.get("landing_url", "Unknown")
        offers_count = len(analysis_data.get("offers", []))
        segments_count = len(analysis_data.get("segments", []))
        stages_completed = len([
            s for s in analysis_data.get("stages", {}).values() 
            if s.get("completed", False)
        ])

        return f"""# Краткое резюме анализа

**Лендинг:** {landing_url}  
**Предложений найдено:** {offers_count}  
**Сегментов выявлено:** {segments_count}  
**Этапов выполнено:** {stages_completed}  

**Статус:** {'Анализ завершен' if stages_completed > 5 else 'Анализ в процессе'}
"""

    def validate_document_structure(self, markdown_content: str) -> Dict[str, Any]:
        """Валидирует структуру markdown документа"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sections_found": [],
        }

        # Проверяем наличие обязательных разделов
        required_sections = [
            "# HeroesGPT Landing Analysis Report",
            "## Executive Summary",
            "## Рекомендации",
            "## Заключение",
        ]

        for section in required_sections:
            if section in markdown_content:
                sections_found = validation_result.get("sections_found", [])
                if isinstance(sections_found, list):
                    sections_found.append(section)
            else:
                errors = validation_result.get("errors", [])
                if isinstance(errors, list):
                    errors.append(f"Missing required section: {section}")
                validation_result["valid"] = False

        # Проверяем длину документа
        if len(markdown_content) < 500:
            warnings = validation_result.get("warnings", [])
            if isinstance(warnings, list):
                warnings.append("Document seems too short")

        return validation_result


def main():
    """Основная функция для тестирования"""
    # Тестовые данные
    test_analysis_data = {
        "landing_url": "https://test.com",
        "business_context": {"type": "saas", "target_audience": "b2b"},
        "stages": {
            "preprocessing": {"completed": True, "timestamp": "2024-01-01T10:00:00"},
            "inventory": {"completed": True, "timestamp": "2024-01-01T10:05:00"},
        },
        "offers": [
            {"type": "free_trial", "priority": "High"},
            {"type": "demo", "priority": "Medium"},
        ],
        "segments": [
            {"name": "startups", "size": "small"},
            {"name": "enterprise", "size": "large"},
        ],
        "reflections": [
            {"checkpoint": "Stage 1", "status": "completed", "timestamp": "2024-01-01T10:05:00"},
        ],
    }

    # Создаем builder
    builder = HeroesGPTDocumentBuilder()

    # Генерируем документ
    markdown_content = builder.generate_markdown_document(test_analysis_data)

    # Валидируем структуру
    validation = builder.validate_document_structure(markdown_content)

    print(f"Document generated: {len(markdown_content)} characters")
    print(f"Validation result: {validation['valid']}")
    if validation["errors"]:
        print(f"Errors: {validation['errors']}")


if __name__ == "__main__":
    main()
