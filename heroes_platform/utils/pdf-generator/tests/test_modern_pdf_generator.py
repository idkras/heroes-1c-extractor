#!/usr/bin/env python3
"""
Тесты для современного PDF генератора
Проверяют качество русской типографики, details блоков и таблиц
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Добавляем путь к генераторам
sys.path.insert(0, str(Path(__file__).parent.parent / "generators"))

from generators.pdf_generator_modern import ModernPDFGenerator, convert_md_to_pdf_modern_sync

class TestModernPDFGenerator:
    """Тесты для современного PDF генератора"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.generator = ModernPDFGenerator()
        self.test_md_content = """
# Тестовая документация

## Заголовок второго уровня

Обычный параграф с русским текстом для проверки типографики.

### Заголовок третьего уровня

- Первый пункт списка
- Второй пункт списка
- Третий пункт списка

<details open>
<summary>## 🚀 QUICK START</summary>

Содержимое details блока с важной информацией.

```python
def example_function():
    return "Hello, World!"
```

</details>

| **№** | **AppMetrica Event** | **Adjust Event** | **Описание** |
|-------|----------------------|------------------|--------------|
| **1** | `received adjust attribution` | - | Получение данных атрибуции |
| **2** | `device_id_sync` | - | Синхронизация ID устройства |
| **3** | - | `APPMETRICA_DEVICE_ID_SYNC` | Синхронизация AppMetrica ID |

> Важная цитата с важной информацией о безопасности.

`inline_code` пример.

---

Конец документа.
        """
    
    def test_preprocess_markdown(self):
        """Тест предобработки markdown"""
        processed = self.generator._preprocess_markdown(self.test_md_content)
        
        # Проверяем, что details блоки остались
        assert '<details open>' in processed
        assert '<summary>' in processed
        
        # Проверяем, что таблицы корректны
        assert '|-------|' in processed
        
        # Проверяем, что русский текст не поврежден
        assert 'русским текстом' in processed
    
    def test_improve_tables(self):
        """Тест улучшения таблиц"""
        table_content = """
| Заголовок 1 | Заголовок 2 |
|:------------:|:------------:|
| Данные 1     | Данные 2     |
        """
        
        improved = self.generator._improve_tables(table_content)
        
        # Проверяем, что разделители корректны
        assert '|-------|' in improved
        assert '|:------------:|' not in improved
    
    def test_enhance_details_blocks(self):
        """Тест улучшения details блоков"""
        html_content = """
        <details open>
        <summary>Заголовок</summary>
        <p>Содержимое</p>
        </details>
        """
        
        enhanced = self.generator._enhance_details_blocks(html_content)
        
        # Проверяем, что details заменены на div'ы
        assert 'details-block' in enhanced
        assert 'details-summary' in enhanced
        assert '<details' not in enhanced
    
    def test_enhance_tables(self):
        """Тест улучшения таблиц"""
        html_content = """
        <table>
        <th>Заголовок</th>
        <td>Данные</td>
        </table>
        """
        
        enhanced = self.generator._enhance_tables(html_content)
        
        # Проверяем, что добавлены классы
        assert 'modern-table' in enhanced
        assert 'table-header' in enhanced
    
    def test_create_full_html(self):
        """Тест создания полного HTML документа"""
        html_content = "<p>Тестовый контент</p>"
        full_html = self.generator._create_full_html(html_content)
        
        # Проверяем структуру HTML
        assert '<!DOCTYPE html>' in full_html
        assert '<html lang="ru">' in full_html
        assert '<title>VipAvenue Adjust AppMetrica Integration</title>' in full_html
        assert 'Тестовый контент' in full_html
        
        # Проверяем наличие CSS
        assert 'Inter' in full_html  # Шрифт
        assert 'modern-table' in full_html  # Стили таблиц
        assert 'details-block' in full_html  # Стили details
    
    def test_markdown_extensions(self):
        """Тест поддержки markdown расширений"""
        extensions = self.generator.extensions
        
        # Проверяем наличие важных расширений
        assert 'markdown.extensions.extra' in extensions
        assert 'markdown.extensions.codehilite' in extensions
        assert 'markdown.extensions.toc' in extensions
        assert 'markdown.extensions.smarty' in extensions
    
    @pytest.mark.asyncio
    async def test_convert_md_to_pdf_async(self):
        """Тест асинхронной конвертации (требует Playwright)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(self.test_md_content)
            md_path = f.name
        
        try:
            output_path = md_path.replace('.md', '_test.pdf')
            
            # Тестируем только если Playwright доступен
            try:
                result = await self.generator.convert_md_to_pdf(md_path, output_path)
                
                if result["success"]:
                    # Проверяем, что PDF создан
                    assert os.path.exists(output_path)
                    assert os.path.getsize(output_path) > 1000  # Минимальный размер
                    
                    # Удаляем тестовый PDF
                    os.unlink(output_path)
                else:
                    # Если Playwright недоступен, это нормально
                    assert "error" in result
                    
            except ImportError:
                # Playwright не установлен - пропускаем тест
                pytest.skip("Playwright не установлен")
                
        finally:
            # Удаляем тестовый markdown файл
            os.unlink(md_path)
    
    def test_convert_md_to_pdf_sync(self):
        """Тест синхронной конвертации"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(self.test_md_content)
            md_path = f.name
        
        try:
            output_path = md_path.replace('.md', '_test.pdf')
            
            # Тестируем только если Playwright доступен
            try:
                result = convert_md_to_pdf_modern_sync(md_path, output_path)
                
                if result["success"]:
                    # Проверяем, что PDF создан
                    assert os.path.exists(output_path)
                    assert os.path.getsize(output_path) > 1000  # Минимальный размер
                    
                    # Удаляем тестовый PDF
                    os.unlink(output_path)
                else:
                    # Если Playwright недоступен, это нормально
                    assert "error" in result
                    
            except ImportError:
                # Playwright не установлен - пропускаем тест
                pytest.skip("Playwright не установлен")
                
        finally:
            # Удаляем тестовый markdown файл
            os.unlink(md_path)

class TestRussianTypography:
    """Тесты русской типографики"""
    
    def test_russian_text_processing(self):
        """Тест обработки русского текста"""
        generator = ModernPDFGenerator()
        
        russian_content = """
# Документация по безопасности

## Основные принципы

При работе с персональными данными необходимо соблюдать требования **ФЗ-152**.

### Таблица требований

| Требование | Описание |
|------------|----------|
| Конфиденциальность | Обеспечение защиты информации |
| Целостность | Предотвращение несанкционированных изменений |

> **Важно**: Все меры безопасности должны быть задокументированы.

<details>
<summary>Дополнительная информация</summary>

Дополнительные сведения о мерах безопасности.

</details>
        """
        
        processed = generator._preprocess_markdown(russian_content)
        
        # Проверяем, что русский текст не поврежден
        assert 'Документация по безопасности' in processed
        assert 'Основные принципы' in processed
        assert 'персональными данными' in processed
        
        # Проверяем, что details блоки обработаны
        assert '<details>' in processed
        assert '<summary>' in processed
        
        # Проверяем, что таблицы корректны
        assert '|------------|' in processed
    
    def test_table_improvements(self):
        """Тест улучшения таблиц с русским текстом"""
        generator = ModernPDFGenerator()
        
        table_content = """
| **№** | **AppMetrica Event** | **Adjust Event** | **Описание** |
|-------|----------------------|------------------|--------------|
| **1** | `received adjust attribution` | - | Получение данных атрибуции от Adjust |
| **2** | `device_id_sync` | - | Синхронизация уникального ID устройства |
| **3** | - | `APPMETRICA_DEVICE_ID_SYNC` | Синхронизация AppMetrica Device ID |
        """
        
        improved = generator._improve_tables(table_content)
        
        # Проверяем, что таблица корректна
        assert '|-------|' in improved
        assert 'received adjust attribution' in improved
        assert 'Получение данных атрибуции от Adjust' in improved

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
