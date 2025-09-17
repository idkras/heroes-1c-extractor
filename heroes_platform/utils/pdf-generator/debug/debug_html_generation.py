"""
Отладка HTML генерации из markdown для понимания проблемы.
"""

import markdown
from pathlib import Path

def debug_markdown_conversion():
    """Проверяет как markdown преобразуется в HTML."""
    
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    
    with open(source_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Берем первые 500 символов markdown
    print("ИСХОДНЫЙ MARKDOWN:")
    print("=" * 50)
    print(md_content[:500])
    print("=" * 50)
    
    # Конвертируем в HTML
    html_content = markdown.markdown(
        md_content, 
        extensions=['tables', 'fenced_code', 'nl2br', 'attr_list', 'def_list']
    )
    
    # Показываем результат HTML
    print("\nРЕЗУЛЬТАТ HTML:")
    print("=" * 50)
    print(html_content[:800])
    print("=" * 50)
    
    # Проверяем наличие тегов
    tags_to_check = ['<h1>', '<h2>', '<h3>', '<p>', '<ul>', '<li>', '<table>']
    print("\nНАЛИЧИЕ HTML ТЕГОВ:")
    for tag in tags_to_check:
        count = html_content.count(tag)
        print(f"{tag}: {count} раз")
    
    # Сохраняем HTML для проверки
    with open('debug_output.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nHTML сохранен в debug_output.html")

if __name__ == "__main__":
    debug_markdown_conversion()