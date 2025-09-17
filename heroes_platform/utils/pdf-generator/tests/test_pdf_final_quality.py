#!/usr/bin/env python3
"""
Финальное тестирование качества PDF документов через анализ исходного кода и результата.
"""

import subprocess
from pathlib import Path
import json
import re

def analyze_pdf_generation_chain():
    """Анализирует всю цепочку генерации PDF."""
    
    results = {
        "generator_analysis": {},
        "source_analysis": {},
        "pdf_analysis": {},
        "issues": [],
        "recommendations": []
    }
    
    # 1. Анализ генератора PDF
    generator_path = "generate_pdf_emergency_fix.py"
    if Path(generator_path).exists():
        with open(generator_path, 'r', encoding='utf-8') as f:
            generator_code = f.read()
        
        # Проверяем критические настройки
        if 'max-width: 180mm' in generator_code:
            results["generator_analysis"]["width"] = "Оптимальная ширина 180mm"
        else:
            results["issues"].append("Ширина полосы набора может быть неоптимальной")
        
        if 'line-height: 1.6' in generator_code:
            results["generator_analysis"]["line_height"] = "Хороший межстрочный интервал"
        else:
            results["issues"].append("Межстрочный интервал требует проверки")
        
        if 'font-family: Arial' in generator_code:
            results["generator_analysis"]["font"] = "Используется Arial"
        else:
            results["issues"].append("Шрифт не определен четко")
    
    # 2. Анализ исходного текста
    source_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/when_security_asked_about_user_data RU_fixed.md"
    if Path(source_path).exists():
        with open(source_path, 'r', encoding='utf-8') as f:
            source_text = f.read()
        
        # Проверяем структуру
        h2_count = source_text.count('## ')
        h3_count = source_text.count('### ')
        results["source_analysis"]["structure"] = f"H2: {h2_count}, H3: {h3_count}"
        
        if h2_count < 3:
            results["issues"].append("Недостаточно заголовков H2 для структурирования")
        
        # Проверяем кавычки
        straight_quotes = source_text.count('"')
        russian_quotes = source_text.count('«')
        results["source_analysis"]["quotes"] = f"Прямые: {straight_quotes}, Русские: {russian_quotes}"
        
        if straight_quotes > 3:
            results["issues"].append("Найдены прямые кавычки в исходном тексте")
    
    # 3. Проверяем результирующий PDF
    pdf_path = "[projects]/rick.ai/knowledge base/in progress/when new lead come/2. when security asked policy/Rick_ai_Security_Documentation_Emergency_Fix.pdf"
    if Path(pdf_path).exists():
        file_size = Path(pdf_path).stat().st_size
        results["pdf_analysis"]["size"] = f"{file_size:,} bytes"
        
        if file_size < 30000:
            results["issues"].append("PDF файл слишком мал")
        elif file_size > 100000:
            results["issues"].append("PDF файл слишком велик")
        else:
            results["pdf_analysis"]["size_status"] = "Размер оптимальный"
    
    # 4. Формируем рекомендации
    if len(results["issues"]) == 0:
        results["recommendations"].append("PDF документ готов к использованию")
    else:
        results["recommendations"].append("Требуется доработка выявленных проблем")
        results["recommendations"].append("Рекомендуется визуальная проверка документа")
    
    return results

def check_all_generators():
    """Проверяет все PDF генераторы в проекте."""
    
    generators = [
        "generate_pdf.py",
        "generate_pdf_final.py", 
        "generate_pdf_improved.py",
        "generate_pdf_emergency_fix.py",
        "generate_pdf_comprehensive_fix.py"
    ]
    
    active_generators = []
    for gen in generators:
        if Path(gen).exists():
            active_generators.append(gen)
    
    print(f"Найдено генераторов PDF: {len(active_generators)}")
    for gen in active_generators:
        print(f"  - {gen}")
    
    return active_generators

def test_pdf_complete_quality():
    """Полный тест качества PDF системы."""
    
    print("Запуск полного анализа качества PDF документов")
    print("=" * 60)
    
    # Проверяем генераторы
    generators = check_all_generators()
    
    # Анализируем качество
    results = analyze_pdf_generation_chain()
    
    print("\nАНАЛИЗ ГЕНЕРАТОРА:")
    for key, value in results["generator_analysis"].items():
        print(f"  {key}: {value}")
    
    print("\nАНАЛИЗ ИСХОДНОГО ТЕКСТА:")
    for key, value in results["source_analysis"].items():
        print(f"  {key}: {value}")
    
    print("\nАНАЛИЗ PDF:")
    for key, value in results["pdf_analysis"].items():
        print(f"  {key}: {value}")
    
    if results["issues"]:
        print(f"\nОБНАРУЖЕНО ПРОБЛЕМ ({len(results['issues'])}):")
        for issue in results["issues"]:
            print(f"  ❌ {issue}")
    
    print("\nРЕКОМЕНДАЦИИ:")
    for rec in results["recommendations"]:
        print(f"  💡 {rec}")
    
    # Сохраняем отчет
    report_file = "pdf_quality_final_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "generators_found": generators,
            "analysis": results,
            "total_issues": len(results["issues"]),
            "status": "ready" if len(results["issues"]) == 0 else "needs_work"
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nПолный отчет сохранен: {report_file}")
    
    print("\n" + "=" * 60)
    if len(results["issues"]) == 0:
        print("СТАТУС: PDF система готова к работе")
    else:
        print(f"СТАТУС: Требуется исправление {len(results['issues'])} проблем")

if __name__ == "__main__":
    test_pdf_complete_quality()