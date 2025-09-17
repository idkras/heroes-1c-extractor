#!/usr/bin/env python3
"""
PDF Generator Runner - Главный интерфейс для генерации PDF

Использование:
    python run_pdf_generator.py input.md output.pdf
    python run_pdf_generator.py --test
    python run_pdf_generator.py --help
"""

import argparse
import sys
from pathlib import Path

# Import from utils directory (legacy structure)
try:
    from pdf_generator.generators.generate_pdf_final import convert_md_to_pdf_final  # type: ignore
    from utils import validate_markdown_content, create_quality_report  # type: ignore
except ImportError:
    # Fallback for when modules are not available
    def convert_md_to_pdf_final(*args, **kwargs):
        raise ImportError("PDF generator module not available")
    
    def validate_markdown_content(*args, **kwargs):
        return True
    
    def create_quality_report(*args, **kwargs):
        return {}

def main():
    parser = argparse.ArgumentParser(
        description="PDF Generator Utils - Генерация качественных PDF документов"
    )
    
    # Основные команды
    parser.add_argument("input", nargs="?", help="Путь к входному markdown файлу")
    parser.add_argument("output", nargs="?", help="Путь к выходному PDF файлу")
    
    # Опциональные параметры
    parser.add_argument("--test", action="store_true", help="Запустить тесты качества")
    parser.add_argument("--validate", action="store_true", help="Только валидация входного файла")
    parser.add_argument("--quality-report", action="store_true", help="Создать отчет качества")
    parser.add_argument("--generator", choices=["final", "comprehensive", "playwright"], 
                       default="final", help="Выбор генератора PDF")
    
    args = parser.parse_args()
    
    # Запуск тестов
    if args.test:
        run_tests()
        return
    
    # Проверка аргументов
    if not args.input or not args.output:
        print("Ошибка: Необходимо указать входной и выходной файлы")
        print("Пример: python run_pdf_generator.py input.md output.pdf")
        sys.exit(1)
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Проверка существования входного файла
    if not input_path.exists():
        print(f"Ошибка: Файл {input_path} не найден")
        sys.exit(1)
    
    # Валидация содержимого
    print(f"📖 Читаю файл: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = validate_markdown_content(content)
    if issues:
        print("⚠️  Найдены проблемы в исходном файле:")
        for issue in issues:
            print(f"   - {issue}")
        
        if args.validate:
            print("\n❌ Валидация завершена с ошибками")
            sys.exit(1)
        else:
            print("   Продолжаю генерацию...")
    else:
        print("✅ Валидация прошла успешно")
    
    if args.validate:
        print("✅ Валидация завершена успешно")
        return
    
    # Создание PDF
    print(f"🔄 Создаю PDF с генератором '{args.generator}'...")
    
    try:
        if args.generator == "final":
            convert_md_to_pdf_final(str(input_path), str(output_path))
        elif args.generator == "comprehensive":
            from generators.generate_pdf_comprehensive_fix import convert_md_to_pdf_comprehensive
            convert_md_to_pdf_comprehensive(str(input_path), str(output_path))
        elif args.generator == "playwright":
            import asyncio
            from generators.generate_pdf_playwright import convert_md_to_pdf_playwright
            asyncio.run(convert_md_to_pdf_playwright(str(input_path), str(output_path)))
        
        print(f"✅ PDF создан: {output_path}")
        
        # Отчет о качестве
        if args.quality_report:
            print("📊 Создаю отчет качества...")
            try:
                import PyPDF2
                with open(output_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                
                report = create_quality_report(output_path, text)
                
                print(f"\n📋 Отчет качества:")
                print(f"   Размер: {report['file_info']['size']}")
                print(f"   Страниц: {report['file_info']['pages']}")
                print(f"   Слов: {report['text_quality']['word_count']}")
                print(f"   Качество: {report['text_quality']['quality_score']:.1f}/100")
                
            except ImportError:
                print("   Установите PyPDF2 для отчета качества")
        
    except Exception as e:
        print(f"❌ Ошибка создания PDF: {e}")
        sys.exit(1)

def run_tests():
    """Запускает тесты качества PDF"""
    print("🧪 Запускаю тесты качества PDF...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(Path(__file__).parent / "tests"), 
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Все тесты прошли успешно")
        else:
            print("❌ Некоторые тесты не прошли")
            sys.exit(1)
            
    except ImportError:
        print("❌ pytest не установлен. Установите: pip install pytest")
        sys.exit(1)

if __name__ == "__main__":
    main()