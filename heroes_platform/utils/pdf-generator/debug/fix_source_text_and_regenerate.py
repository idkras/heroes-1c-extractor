#!/usr/bin/env python3
"""
Исправление исходного текста и создание финальной версии PDF.
"""

import re
from pathlib import Path

def fix_source_text_typography(content):
    """Исправляет типографику в исходном тексте."""
    
    # Правильные русские кавычки
    content = re.sub(r'"([^"]*)"', r'«\1»', content)
    
    # Правильные тире
    content = content.replace('--', '—')
    content = re.sub(r'\s+-\s+', ' — ', content)
    
    # Неразрывные пробелы (дополнительные правила)
    nbsp = '\u00A0'
    
    # Числительные с единицами
    content = re.sub(r'(\d+)\s+(лет|года|дней|часов|минут)', rf'\1{nbsp}\2', content)
    
    # Сокращения
    content = re.sub(r'(ст\.|п\.|ч\.|рис\.|табл\.)\s+(\d+)', rf'\1{nbsp}\2', content)
    content = re.sub(r'(ФЗ)-(\d+)', rf'\1-{nbsp}\2', content)
    
    # Инициалы и сокращения
    content = re.sub(r'([А-ЯЁ]\.)\s+([А-ЯЁ]\.)', rf'\1{nbsp}\2', content)
    
    # Предлоги и союзы в начале строки
    content = re.sub(r'\n\s*(а|и|в|к|с|о|у|за|на|до|от|по|для|при|без|под|над)\s+', rf'\n\1{nbsp}', content)
    
    return content

def structure_long_paragraphs(content):
    """Разбивает длинные абзацы на более читаемые части."""
    
    paragraphs = content.split('\n\n')
    structured_paragraphs = []
    
    for paragraph in paragraphs:
        # Пропускаем заголовки, списки и таблицы
        if (paragraph.startswith('#') or 
            paragraph.startswith('|') or 
            paragraph.startswith('•') or 
            paragraph.startswith('*') or
            len(paragraph) < 300):
            structured_paragraphs.append(paragraph)
            continue
        
        # Разбиваем длинные абзацы
        sentences = re.split(r'([.!?]+)', paragraph)
        
        if len(sentences) > 6:  # Длинный абзац
            current_part = ""
            sentence_count = 0
            parts = []
            
            for i in range(0, len(sentences), 2):
                if i < len(sentences):
                    sentence = sentences[i].strip()
                    punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
                    
                    if sentence:
                        current_part += sentence + punctuation + " "
                        sentence_count += 1
                        
                        # Разбиваем на части по 2-3 предложения
                        if sentence_count >= 3:
                            parts.append(current_part.strip())
                            current_part = ""
                            sentence_count = 0
            
            if current_part.strip():
                parts.append(current_part.strip())
            
            # Добавляем структурированные части
            structured_paragraphs.extend(parts)
        else:
            structured_paragraphs.append(paragraph)
    
    return '\n\n'.join(structured_paragraphs)

def main():
    """Основная функция для исправления текста и создания PDF."""
    
    # Путь к исходному файлу
    source_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU.md"
    
    if not Path(source_file).exists():
        print(f"Файл не найден: {source_file}")
        return
    
    # Читаем исходный файл
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Исправление типографики и структуры текста...")
    
    # Исправляем типографику
    content = fix_source_text_typography(content)
    
    # Структурируем длинные абзацы
    content = structure_long_paragraphs(content)
    
    # Сохраняем исправленный файл
    fixed_file = source_file.replace('.md', '_fixed.md')
    with open(fixed_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Исправленный текст сохранен: {fixed_file}")
    
    # Создаем PDF из исправленного текста
    from generators.generate_pdf_comprehensive_fix import convert_md_to_pdf_comprehensive
    
    pdf_file = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Final_Fixed.pdf"
    
    convert_md_to_pdf_comprehensive(fixed_file, pdf_file)
    
    print(f"PDF создан из исправленного текста: {pdf_file}")
    
    # Удаляем старый PDF
    old_pdf = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Comprehensive.pdf"
    if Path(old_pdf).exists():
        Path(old_pdf).unlink()
        print(f"Старый PDF удален: {old_pdf}")

if __name__ == "__main__":
    main()