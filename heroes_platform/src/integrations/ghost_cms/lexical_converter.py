#!/usr/bin/env python3
"""
Lexical Converter for Ghost CMS v5.0
Преобразование Markdown в Lexical JSON формат
"""

import json
import re
from typing import List, Dict, Any


class LexicalConverter:
    """
    JTBD: Как конвертер форматов, я хочу преобразовывать Markdown в Lexical,
    чтобы обеспечить правильное отображение контента в Ghost v5.0.
    """

    def __init__(self):
        """Инициализация конвертера"""
        self.node_id_counter = 1

    def markdown_to_lexical(self, markdown_content: str) -> str:
        """
        Преобразует Markdown в Lexical JSON формат
        
        Args:
            markdown_content: Markdown контент
            
        Returns:
            Lexical JSON строка
        """
        lines = markdown_content.split('\n')
        nodes = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                # Пустая строка - параграф
                nodes.append(self._create_paragraph_node(""))
                i += 1
            elif line.startswith('# '):
                # H1 заголовок
                text = line[2:].strip()
                nodes.append(self._create_heading_node(text, 1))
                i += 1
            elif line.startswith('## '):
                # H2 заголовок
                text = line[3:].strip()
                nodes.append(self._create_heading_node(text, 2))
                i += 1
            elif line.startswith('### '):
                # H3 заголовок
                text = line[4:].strip()
                nodes.append(self._create_heading_node(text, 3))
                i += 1
            elif line.startswith('```'):
                # Код блок
                code_content, new_i = self._extract_code_block(lines, i)
                nodes.append(self._create_code_block_node(code_content))
                i = new_i
            elif line.startswith('|') and '|' in line[1:]:
                # Таблица
                table_data, new_i = self._extract_table(lines, i)
                nodes.append(self._create_table_node(table_data))
                i = new_i
            elif line.startswith('!['):
                # Картинка
                image_data = self._extract_image(line)
                nodes.append(self._create_image_node(image_data))
                i += 1
            elif line.startswith('- ') or line.startswith('* '):
                # Список
                text = line[2:].strip()
                nodes.append(self._create_list_item_node(text))
                i += 1
            elif line.startswith('1. '):
                # Нумерованный список
                text = line[3:].strip()
                nodes.append(self._create_list_item_node(text, ordered=True))
                i += 1
            elif line.startswith('> '):
                # Цитата
                quote_text, new_i = self._extract_quote(lines, i)
                nodes.append(self._create_quote_node(quote_text))
                i = new_i
            else:
                # Обычный параграф
                nodes.append(self._create_paragraph_node(line))
                i += 1
        
        lexical_structure = {
            "root": {
                "children": nodes,
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        }
        
        return json.dumps(lexical_structure, ensure_ascii=False)

    def _create_table_node(self, table_data: List[List[str]]) -> Dict[str, Any]:
        """Создает узел таблицы"""
        rows = []
        for row_data in table_data:
            cells = []
            for cell_text in row_data:
                cell = {
                    "children": [
                        {
                            "detail": 0,
                            "format": 0,
                            "mode": "normal",
                            "style": "",
                            "text": cell_text,
                            "type": "text",
                            "version": 1
                        }
                    ],
                    "direction": "ltr",
                    "format": "",
                    "indent": 0,
                    "type": "tablecell",
                    "version": 1
                }
                cells.append(cell)
            
            row = {
                "children": cells,
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "tablerow",
                "version": 1
            }
            rows.append(row)
        
        node = {
            "children": rows,
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "type": "table",
            "version": 1
        }
        return node

    def _create_image_node(self, image_data: Dict[str, str]) -> Dict[str, Any]:
        """Создает узел картинки"""
        node = {
            "altText": image_data.get("alt", ""),
            "height": None,
            "key": None,
            "maxWidth": None,
            "showCaption": False,
            "src": image_data.get("src", ""),
            "type": "image",
            "version": 1,
            "width": None
        }
        return node

    def _create_quote_node(self, quote_text: str) -> Dict[str, Any]:
        """Создает узел цитаты"""
        node = {
            "children": [
                {
                    "children": [
                        {
                            "detail": 0,
                            "format": 0,
                            "mode": "normal",
                            "style": "",
                            "text": quote_text,
                            "type": "text",
                            "version": 1
                        }
                    ],
                    "direction": "ltr",
                    "format": "",
                    "indent": 0,
                    "type": "paragraph",
                    "version": 1
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "type": "quote",
            "version": 1
        }
        return node

    def _create_paragraph_node(self, text: str) -> Dict[str, Any]:
        """Создает узел параграфа"""
        node = {
            "children": [
                {
                    "detail": 0,
                    "format": 0,
                    "mode": "normal",
                    "style": "",
                    "text": text,
                    "type": "text",
                    "version": 1
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "type": "paragraph",
            "version": 1
        }
        return node

    def _create_heading_node(self, text: str, level: int) -> Dict[str, Any]:
        """Создает узел заголовка"""
        node = {
            "children": [
                {
                    "detail": 0,
                    "format": 0,
                    "mode": "normal",
                    "style": "",
                    "text": text,
                    "type": "text",
                    "version": 1
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "tag": f"h{level}",
            "type": "heading",
            "version": 1
        }
        return node

    def _create_code_block_node(self, code_content: str) -> Dict[str, Any]:
        """Создает узел блока кода"""
        node = {
            "children": [
                {
                    "detail": 0,
                    "format": 0,
                    "mode": "normal",
                    "style": "",
                    "text": code_content,
                    "type": "text",
                    "version": 1
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "language": "javascript",
            "type": "code",
            "version": 1
        }
        return node

    def _create_list_item_node(self, text: str, ordered: bool = False) -> Dict[str, Any]:
        """Создает узел элемента списка"""
        node = {
            "children": [
                {
                    "detail": 0,
                    "format": 0,
                    "mode": "normal",
                    "style": "",
                    "text": text,
                    "type": "text",
                    "version": 1
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "tag": "li",
            "type": "listitem",
            "value": 1,
            "version": 1
        }
        return node

    def _extract_code_block(self, lines: List[str], start_index: int) -> tuple[str, int]:
        """Извлекает содержимое блока кода"""
        code_lines = []
        i = start_index + 1
        
        while i < len(lines) and not lines[i].startswith('```'):
            code_lines.append(lines[i])
            i += 1
            
        return '\n'.join(code_lines), i + 1

    def _extract_table(self, lines: List[str], start_index: int) -> tuple[List[List[str]], int]:
        """Извлекает данные таблицы"""
        table_data = []
        i = start_index
        
        # Пропускаем заголовок таблицы
        if i < len(lines) and lines[i].startswith('|'):
            headers = [cell.strip() for cell in lines[i].split('|')[1:-1]]
            table_data.append(headers)
            i += 1
        
        # Пропускаем разделитель
        if i < len(lines) and lines[i].startswith('|') and '---' in lines[i]:
            i += 1
        
        # Читаем данные
        while i < len(lines) and lines[i].startswith('|'):
            row = [cell.strip() for cell in lines[i].split('|')[1:-1]]
            table_data.append(row)
            i += 1
            
        return table_data, i

    def _extract_image(self, line: str) -> dict[str, str]:
        """Извлекает данные картинки из Markdown"""
        # Формат: ![alt](url)
        import re
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        match = re.search(pattern, line)
        
        if match:
            return {
                "alt": match.group(1),
                "src": match.group(2)
            }
        return {"alt": "", "src": ""}

    def _extract_quote(self, lines: List[str], start_index: int) -> tuple[str, int]:
        """Извлекает текст цитаты"""
        quote_lines = []
        i = start_index
        
        while i < len(lines) and lines[i].startswith('> '):
            quote_lines.append(lines[i][2:].strip())
            i += 1
            
        return '\n'.join(quote_lines), i


def test_lexical_converter():
    """Тестирование конвертера"""
    converter = LexicalConverter()
    
    # Тестовый Markdown
    markdown_content = """# Заголовок H1

Это параграф с **жирным текстом** и *курсивом*.

## Заголовок H2

Список элементов:
- Первый элемент
- Второй элемент
- Третий элемент

### Заголовок H3

Нумерованный список:
1. Первый пункт
2. Второй пункт
3. Третий пункт

```javascript
function hello() {
    console.log("Hello, World!");
}
```

Еще один параграф с обычным текстом.
"""
    
    lexical_json = converter.markdown_to_lexical(markdown_content)
    print("Markdown to Lexical conversion:")
    print(json.dumps(json.loads(lexical_json), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_lexical_converter()
