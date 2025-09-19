#!/usr/bin/env python3
"""
Тесты для рефакторенного PDF генератора.
TDD подход: сначала тесты, потом реализация.
"""

import os
import tempfile
from pathlib import Path

import pytest

# Импортируем новый генератор
from generators.pdf_generator_refactored import convert_md_to_pdf_refactored


class TestRefactoredPDFGenerator:
    """
    JTBD: Как тестировщик, я хочу проверить новый PDF генератор,
    чтобы убедиться в его качестве и функциональности.
    """

    def test_markdown_extensions_support(self):
        """
        JTBD: Как пользователь, я хочу чтобы details блоки отображались правильно,
        чтобы сохранить структуру сложных документов.

        GIVEN markdown с details блоками
        WHEN конвертирую в PDF
        THEN details блоки читаемы и структурированы
        """
        markdown_content = """
        <details open>
        <summary>## 🚀 QUICK START · 5 минут для разработчика</summary>

        Content inside details block
        - Point 1
        - Point 2
        </details>
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(markdown_content)
            md_file = f.name

        try:
            pdf_file = md_file.replace(".md", ".pdf")

            # Новый генератор должен работать
            success = convert_md_to_pdf_refactored(md_file, pdf_file)
            assert success, "Конвертация должна быть успешной"

            # Проверяем что PDF создался
            assert os.path.exists(pdf_file), "PDF должен создаться"

            # Проверяем размер - если PDF слишком маленький, значит контент потерялся
            pdf_size = os.path.getsize(pdf_file)
            assert pdf_size > 1000, (
                f"PDF слишком маленький ({pdf_size} bytes), контент потерялся"
            )

        finally:
            os.unlink(md_file)
            if os.path.exists(pdf_file):
                os.unlink(pdf_file)

    def test_complex_tables_rendering(self):
        """
        JTBD: Как пользователь, я хочу чтобы таблицы с русским текстом отображались правильно,
        чтобы обеспечить читаемость сложных данных.

        GIVEN таблицы с русским текстом
        WHEN конвертирую в PDF
        THEN таблицы имеют читаемую структуру
        """
        markdown_content = """
        | **№** | **AppMetrica Event** | **Adjust Event** | **Adjust Event Token** |
        |-------|----------------------|------------------|------------------------|
        | **1** | `received adjust attribution on app launch screen` | - | |
        | **2** | `system adjust_id is synced with appmetrica` | - | |
        | **3** | - | `APPMETRICA_DEVICE_ID_SYNC` | `appmetrica_device_id_sync_sep25` |
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(markdown_content)
            md_file = f.name

        try:
            pdf_file = md_file.replace(".md", ".pdf")

            # Новый генератор должен создать качественный PDF
            success = convert_md_to_pdf_refactored(md_file, pdf_file)
            assert success, "Конвертация должна быть успешной"

            # Проверяем что PDF создался
            assert os.path.exists(pdf_file), "PDF должен создаться"

            # Проверяем размер - если PDF слишком маленький, значит контент потерялся
            pdf_size = os.path.getsize(pdf_file)
            assert pdf_size > 1000, (
                f"PDF слишком маленький ({pdf_size} bytes), контент потерялся"
            )

        finally:
            os.unlink(md_file)
            if os.path.exists(pdf_file):
                os.unlink(pdf_file)

    def test_russian_text_typography(self):
        """
        JTBD: Как пользователь, я хочу чтобы русский текст отображался корректно,
        чтобы обеспечить читаемость документа.

        GIVEN русский текст
        WHEN конвертирую в PDF
        THEN типографика корректна
        """
        markdown_content = """
        # Инструкция: Интеграция Adjust с AppMetrica для UTM-трекинга

        Глубокий анализ для мобильной атрибуции и кросс-платформенного трекинга.

        ## 📋 Next Actions

        ### 🔧 Технические задачи
        - [x] Для всех параметров дописать комментарий
        - [ ] Обновить текст запросов разрешений
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(markdown_content)
            md_file = f.name

        try:
            pdf_file = md_file.replace(".md", ".pdf")

            # Новый генератор должен создать качественный PDF
            success = convert_md_to_pdf_refactored(md_file, pdf_file)
            assert success, "Конвертация должна быть успешной"

            # Проверяем что PDF создался
            assert os.path.exists(pdf_file), "PDF должен создаться"

            # Проверяем размер - если PDF слишком маленький, значит контент потерялся
            pdf_size = os.path.getsize(pdf_file)
            assert pdf_size > 2000, (
                f"PDF слишком маленький ({pdf_size} bytes), русский текст потерялся"
            )

        finally:
            os.unlink(md_file)
            if os.path.exists(pdf_file):
                os.unlink(pdf_file)

    def test_vipavenue_document_rendering(self):
        """
        JTBD: Как пользователь, я хочу чтобы vipavenue-adjust-appmetrica.md конвертировался правильно,
        чтобы получить качественный PDF документ.

        GIVEN реальный документ vipavenue-adjust-appmetrica.md
        WHEN конвертирую в PDF
        THEN все элементы отображаются корректно
        """
        vipavenue_md_path = Path(
            "[rick.ai]/knowledge base/in progress/1. when new lead come/when mobile · appmetric · ajust/vipavenue.ru/vipavenue-adjust-appmetrica.md"
        )

        if not vipavenue_md_path.exists():
            pytest.skip("Файл vipavenue-adjust-appmetrica.md не найден")

        # Создаем временный PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_file = f.name

        try:
            # Новый генератор должен создать качественный PDF
            success = convert_md_to_pdf_refactored(str(vipavenue_md_path), pdf_file)
            assert success, "Конвертация должна быть успешной"

            # Проверяем что PDF создался
            assert os.path.exists(pdf_file), "PDF должен создаться"

            # Проверяем размер - если PDF слишком маленький, значит контент потерялся
            pdf_size = os.path.getsize(pdf_file)
            assert pdf_size > 50000, (
                f"PDF слишком маленький ({pdf_size} bytes), сложный контент потерялся"
            )

        finally:
            if os.path.exists(pdf_file):
                os.unlink(pdf_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
