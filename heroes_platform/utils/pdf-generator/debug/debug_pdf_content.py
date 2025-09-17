"""
Детальный анализ содержимого PDF для отладки структуры.
"""

import PyPDF2
from pathlib import Path

def debug_pdf_content():
    """Выводит первые 1000 символов PDF для анализа структуры."""
    
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_FINAL.pdf"
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            print("📄 Первые 1000 символов PDF:")
            print("=" * 50)
            print(text[:1000])
            print("=" * 50)
            
            # Ищем конкретные строки
            search_terms = [
                "Ключевые принципы работы",
                "Примеры используемых",
                "Принципы чтения",
                "обезличенных идентификаторов"
            ]
            
            print("\n🔍 Поиск ключевых фраз:")
            for term in search_terms:
                if term in text:
                    print(f"✅ Найдено: '{term}'")
                else:
                    print(f"❌ НЕ найдено: '{term}'")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    debug_pdf_content()