#!/usr/bin/env python3
"""
Улучшенный конвертер Markdown в Lexical JSON формат
Специально для обработки таблиц
"""

import json
import re
from typing import Dict, Any, List, Optional

class AdvancedLexicalConverter:
    def __init__(self):
        pass
    
    def markdown_to_lexical(self, markdown_content: str) -> str:
        """
        Конвертирует Markdown в Lexical JSON формат с поддержкой таблиц
        """
        try:
            # Разбиваем на строки
            lines = markdown_content.split('\n')
            children = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if self._is_table_header(line):
                    # Обрабатываем таблицу
                    table_node = self._parse_table(lines, i)
                    if table_node:
                        children.append(table_node)
                        # Пропускаем строки таблицы
                        while i < len(lines) and self._is_table_row(lines[i].strip()):
                            i += 1
                        continue
                
                elif line.startswith('#'):
                    # Заголовок
                    children.append(self._parse_heading(line))
                
                elif line.startswith('|'):
                    # Строка таблицы (если не обработана выше)
                    table_node = self._parse_table(lines, i)
                    if table_node:
                        children.append(table_node)
                        while i < len(lines) and self._is_table_row(lines[i].strip()):
                            i += 1
                        continue
                
                elif line.startswith('- ') or line.startswith('* '):
                    # Список
                    list_node = self._parse_list(lines, i)
                    if list_node:
                        children.append(list_node)
                        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                            i += 1
                        continue
                
                elif line.startswith('```'):
                    # Блок кода
                    code_node = self._parse_code_block(lines, i)
                    if code_node:
                        children.append(code_node)
                        while i < len(lines) and not lines[i].strip().startswith('```'):
                            i += 1
                        i += 1  # Пропускаем закрывающий ```
                        continue
                
                elif line:
                    # Обычный параграф
                    children.append(self._parse_paragraph(line))
                
                i += 1
            
            # Создаем корневую структуру
            lexical_structure = {
                "root": {
                    "children": children,
                    "direction": None,
                    "format": "",
                    "indent": 0,
                    "type": "root",
                    "version": 1
                }
            }
            
            return json.dumps(lexical_structure, ensure_ascii=False)
            
        except Exception as e:
            raise Exception(f"Conversion failed: {e}")
    
    def _is_table_header(self, line: str) -> bool:
        """Проверяет, является ли строка заголовком таблицы"""
        return line.startswith('|') and '|' in line[1:] and not self._is_table_separator(line)
    
    def _is_table_separator(self, line: str) -> bool:
        """Проверяет, является ли строка разделителем таблицы"""
        return re.match(r'^\|[\s\-:|]+\|$', line) is not None
    
    def _is_table_row(self, line: str) -> bool:
        """Проверяет, является ли строка строкой таблицы"""
        return line.startswith('|') and '|' in line[1:] and not self._is_table_separator(line)
    
    def _parse_table(self, lines: List[str], start_index: int) -> Optional[Dict[str, Any]]:
        """Парсит таблицу из Markdown"""
        rows = []
        i = start_index
        
        # Парсим заголовок
        if i < len(lines) and self._is_table_header(lines[i]):
            header_row = self._parse_table_row(lines[i])
            rows.append(header_row)
            i += 1
        
        # Пропускаем разделитель
        if i < len(lines) and self._is_table_separator(lines[i]):
            i += 1
        
        # Парсим строки данных
        while i < len(lines) and self._is_table_row(lines[i]):
            data_row = self._parse_table_row(lines[i])
            rows.append(data_row)
            i += 1
        
        if len(rows) < 2:  # Нужен заголовок и хотя бы одна строка данных
            return None
        
        return {
            "children": rows,
            "direction": None,
            "format": "",
            "indent": 0,
            "type": "table",
            "version": 1
        }
    
    def _parse_table_row(self, line: str) -> Dict[str, Any]:
        """Парсит строку таблицы"""
        # Разбиваем по | и убираем пустые элементы
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        
        row_children = []
        for cell_content in cells:
            cell_node = {
                "children": [{
                    "detail": 0,
                    "format": 0,
                    "mode": "normal",
                    "style": "",
                    "text": cell_content,
                    "type": "text",
                    "version": 1
                }],
                "direction": None,
                "format": "",
                "indent": 0,
                "type": "tablecell",
                "version": 1
            }
            row_children.append(cell_node)
        
        return {
            "children": row_children,
            "direction": None,
            "format": "",
            "indent": 0,
            "type": "tablerow",
            "version": 1
        }
    
    def _parse_heading(self, line: str) -> Dict[str, Any]:
        """Парсит заголовок"""
        level = len(line) - len(line.lstrip('#'))
        text = line.lstrip('#').strip()
        
        return {
            "children": [{
                "detail": 0,
                "format": 0,
                "mode": "normal",
                "style": "",
                "text": text,
                "type": "text",
                "version": 1
            }],
            "direction": None,
            "format": "",
            "indent": 0,
            "tag": f"h{level}",
            "type": "heading",
            "version": 1
        }
    
    def _parse_paragraph(self, line: str) -> Dict[str, Any]:
        """Парсит параграф"""
        return {
            "children": [{
                "detail": 0,
                "format": 0,
                "mode": "normal",
                "style": "",
                "text": line,
                "type": "text",
                "version": 1
            }],
            "direction": None,
            "format": "",
            "indent": 0,
            "type": "paragraph",
            "version": 1
        }
    
    def _parse_list(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """Парсит список"""
        items = []
        i = start_index
        
        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
            item_text = lines[i].strip()[2:]  # Убираем '- ' или '* '
            item_node = {
                "children": [{
                    "detail": 0,
                    "format": 0,
                    "mode": "normal",
                    "style": "",
                    "text": item_text,
                    "type": "text",
                    "version": 1
                }],
                "direction": None,
                "format": "",
                "indent": 0,
                "type": "listitem",
                "value": 1,
                "version": 1
            }
            items.append(item_node)
            i += 1
        
        return {
            "children": items,
            "direction": None,
            "format": "",
            "indent": 0,
            "listType": "bullet",
            "start": 1,
            "tag": "ul",
            "type": "list",
            "version": 1
        }
    
    def _parse_code_block(self, lines: List[str], start_index: int) -> Dict[str, Any]:
        """Парсит блок кода"""
        i = start_index + 1
        code_lines = []
        
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i])
            i += 1
        
        code_text = '\n'.join(code_lines)
        
        return {
            "children": [{
                "detail": 0,
                "format": 0,
                "mode": "normal",
                "style": "",
                "text": code_text,
                "type": "text",
                "version": 1
            }],
            "direction": None,
            "format": "",
            "indent": 0,
            "language": "text",
            "type": "code",
            "version": 1
        }

def test_advanced_lexical_converter():
    """
    Тестирует улучшенный Lexical конвертер
    """
    converter = AdvancedLexicalConverter()
    
    # Тестовый Markdown с различными элементами
    test_markdown = """# Заголовок H1

Это **жирный текст** и *курсив*.

## Заголовок H2

### Заголовок H3

Список элементов:
- Первый элемент
- Второй элемент
- Третий элемент

Нумерованный список:
1. Первый пункт
2. Второй пункт
3. Третий пункт

```javascript
function hello() {
    console.log("Hello, World!");
}
```

> Это цитата
> с несколькими строками

| Платформа | API Версия | Статус |
|-----------|------------|--------|
| Ghost 2025 | v5.0 | ✅ Работает |
| Ghost 2022_RU | v2 | ✅ Работает |

![Rick.ai Logo](https://rick.ai/content/images/2021/10/rick-ai-logo.png)

[Ссылка на GitHub](https://github.com/remarkjs/remark)
"""
    
    print("Тестирование улучшенного Lexical конвертера...")
    print("=" * 50)
    
    try:
        lexical_result = converter.markdown_to_lexical(test_markdown)
        print("✅ Конвертация успешна!")
        print(f"Длина Lexical JSON: {len(lexical_result)} символов")
        
        # Проверяем структуру
        parsed = json.loads(lexical_result)
        root_children = parsed.get('root', {}).get('children', [])
        print(f"Количество узлов: {len(root_children)}")
        
        # Показываем первые несколько узлов
        print("\nПервые узлы:")
        for i, node in enumerate(root_children[:3]):
            print(f"  {i+1}. Тип: {node.get('type')}, Тег: {node.get('tag', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        return False

if __name__ == "__main__":
    test_advanced_lexical_converter()
