#!/usr/bin/env python3
"""
Тестирование Node.js PDF генератора через md-to-pdf
Создает PDF из vipavenue-adjust-appmetrica.md для проверки качества
"""

import sys
from pathlib import Path

# Добавляем путь к генераторам
sys.path.insert(0, str(Path(__file__).parent / "generators"))

def test_nodejs_generator():
    """Тестирует Node.js генератор на реальном файле"""
    
    # Путь к исходному markdown файлу
    md_file = Path("../../heroes-template/[rick.ai]/clients/vipavenue.ru/vipavenue-adjust-appmetrica.md")
    
    if not md_file.exists():
        print(f"❌ Файл не найден: {md_file}")
        print("Убедитесь, что вы находитесь в корневой папке проекта")
        return False
    
    # Путь для выходного PDF
    output_pdf = Path("vipavenue-adjust-appmetrica_NODEJS.pdf")
    
    print(f"📖 Читаю файл: {md_file}")
    print(f"📄 Создаю PDF: {output_pdf}")
    
    try:
        # Импортируем Node.js генератор
        from generators.pdf_generator_nodejs import convert_md_to_pdf_nodejs
        
        # Создаем PDF
        print("🔄 Генерирую PDF через md-to-pdf...")
        result = convert_md_to_pdf_nodejs(str(md_file), str(output_pdf))
        
        if result["success"]:
            print(f"✅ PDF успешно создан: {output_pdf}")
            print(f"📊 Размер файла: {result['file_size_kb']:.1f} KB")
            print(f"💬 Сообщение: {result['message']}")
            
            # Проверяем качество
            check_pdf_quality(output_pdf)
            
            return True
        else:
            print(f"❌ Ошибка создания PDF: {result['error']}")
            if 'stdout' in result:
                print(f"📤 stdout: {result['stdout']}")
            if 'stderr' in result:
                print(f"📥 stderr: {result['stderr']}")
            return False
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что Node.js и npm установлены")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_nodejs_advanced_options():
    """Тестирует Node.js генератор с расширенными опциями"""
    
    md_file = Path("../../heroes-template/[rick.ai]/clients/vipavenue.ru/vipavenue-adjust-appmetrica.md")
    output_pdf = Path("vipavenue-adjust-appmetrica_NODEJS_ADVANCED.pdf")
    
    if not md_file.exists():
        print(f"❌ Файл не найден: {md_file}")
        return False
    
    try:
        from generators.pdf_generator_nodejs import convert_md_to_pdf_nodejs_advanced
        
        # Расширенные опции
        options = {
            "format": "A4",
            "margin": "15mm",
            "highlight": True,
            "toc": True,
            "numbered": False
        }
        
        print(f"🔄 Тестирую расширенные опции: {options}")
        result = convert_md_to_pdf_nodejs_advanced(str(md_file), str(output_pdf), options)
        
        if result["success"]:
            print(f"✅ Расширенный PDF создан: {output_pdf}")
            print(f"📊 Размер файла: {result['file_size_kb']:.1f} KB")
            print(f"🔧 Использованные опции: {result['options_used']}")
            return True
        else:
            print(f"❌ Ошибка расширенного генератора: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка расширенного генератора: {e}")
        return False

def check_pdf_quality(pdf_path: Path):
    """Проверяет качество созданного PDF"""
    
    print("\n🔍 Проверка качества PDF:")
    
    # Проверяем размер файла
    size_kb = pdf_path.stat().st_size / 1024
    if size_kb > 100:
        print(f"✅ Размер файла: {size_kb:.1f} KB (нормально)")
    else:
        print(f"⚠️ Размер файла: {size_kb:.1f} KB (возможно слишком маленький)")
    
    # Проверяем, что файл не пустой
    if size_kb > 1:
        print("✅ Файл не пустой")
    else:
        print("❌ Файл слишком маленький")
    
    # Проверяем расширение
    if pdf_path.suffix.lower() == '.pdf':
        print("✅ Правильное расширение .pdf")
    else:
        print("❌ Неправильное расширение файла")
    
    print("\n📋 Рекомендации:")
    print("- Откройте PDF в браузере для проверки отображения")
    print("- Проверьте качество таблиц и details блоков")
    print("- Убедитесь, что русский текст читаем")
    print("- Сравните с PDF от Playwright генератора")

def check_nodejs_dependencies():
    """Проверяет наличие Node.js зависимостей"""
    
    print("🔍 Проверка Node.js зависимостей:")
    
    try:
        import subprocess
        
        # Проверяем Node.js
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
        
        # Проверяем npm
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ npm: {result.stdout.strip()}")
        
        # Проверяем md-to-pdf
        result = subprocess.run(["npx", "md-to-pdf", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"✅ md-to-pdf: {result.stdout.strip()}")
        else:
            print("⚠️ md-to-pdf не установлен, будет установлен автоматически")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки зависимостей: {e}")
        return False

def main():
    """Главная функция"""
    
    print("🚀 Тестирование Node.js PDF генератора (md-to-pdf)")
    print("=" * 60)
    
    # Проверяем зависимости
    print("\n📋 Проверка зависимостей")
    deps_ok = check_nodejs_dependencies()
    
    if not deps_ok:
        print("❌ Зависимости не установлены")
        print("Установите Node.js и npm: https://nodejs.org/")
        return
    
    # Тестируем базовый генератор
    print("\n📋 Тест 1: Базовый Node.js генератор")
    basic_success = test_nodejs_generator()
    
    # Тестируем расширенные опции
    print("\n📋 Тест 2: Расширенные опции")
    advanced_success = test_nodejs_advanced_options()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"Базовый генератор: {'✅' if basic_success else '❌'}")
    print(f"Расширенные опции: {'✅' if advanced_success else '❌'}")
    
    if basic_success or advanced_success:
        print("\n🎉 Тестирование завершено успешно!")
        print("📁 Проверьте созданные PDF файлы:")
        
        pdf_files = list(Path(".").glob("vipavenue-adjust-appmetrica_NODEJS*.pdf"))
        for pdf_file in pdf_files:
            if pdf_file.exists():
                size_kb = pdf_file.stat().st_size / 1024
                print(f"   - {pdf_file.name} ({size_kb:.1f} KB)")
        
        print("\n🔍 Сравнение с Playwright генератором:")
        playwright_files = list(Path(".").glob("vipavenue-adjust-appmetrica_MODERN*.pdf"))
        for pdf_file in playwright_files:
            if pdf_file.exists():
                size_kb = pdf_file.stat().st_size / 1024
                print(f"   - {pdf_file.name} ({size_kb:.1f} KB)")
        
        print("\n💡 Рекомендации:")
        print("- Сравните качество PDF от разных генераторов")
        print("- md-to-pdf обычно дает лучшее качество типографики")
        print("- Playwright лучше для сложных CSS и интерактивности")
        
    else:
        print("\n❌ Все тесты провалились")
        print("🔧 Проверьте установку Node.js и npm")

if __name__ == "__main__":
    main()
