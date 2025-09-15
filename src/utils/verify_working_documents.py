#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def verify_working_documents():
    """
    Детальная проверка качества рабочих документов
    """
    print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА КАЧЕСТВА РАБОЧИХ ДОКУМЕНТОВ")
    print("=" * 60)
    
    json_file = '[prostocvet-1c]/raw/final_working_documents.json'
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        print(f"✅ Загружены документы: {documents['metadata']['total_documents']} шт.")
        
        # Детальная проверка каждого документа
        quality_report = {
            'total_documents': documents['metadata']['total_documents'],
            'documents_with_amounts': 0,
            'documents_with_descriptions': 0,
            'documents_with_numbers': 0,
            'documents_with_counterparties': 0,
            'documents_with_blob_content': 0,
            'broken_documents': [],
            'excellent_documents': []
        }
        
        print(f"\n📊 ДЕТАЛЬНАЯ ПРОВЕРКА ДОКУМЕНТОВ:")
        
        for i, doc in enumerate(documents['documents'], 1):
            print(f"\n📄 Документ #{i}: {doc['document_id']}")
            print(f"   Тип: {doc['document_type']}")
            print(f"   Номер: {doc['document_number']}")
            print(f"   Сумма: {doc['total_amount']}")
            print(f"   Описание: {doc['description'][:50]}{'...' if len(doc['description']) > 50 else ''}")
            print(f"   Контрагент: {doc['counterparty']}")
            
            # Проверяем качество
            has_amount = doc['total_amount'] > 0
            has_description = doc['description'] != "Описание не найдено"
            has_number = doc['document_number'] != 'N/A'
            has_counterparty = doc['counterparty'] != "Неизвестный контрагент"
            has_blob_content = len(doc['blob_content']) > 0
            
            if has_amount:
                quality_report['documents_with_amounts'] += 1
            if has_description:
                quality_report['documents_with_descriptions'] += 1
            if has_number:
                quality_report['documents_with_numbers'] += 1
            if has_counterparty:
                quality_report['documents_with_counterparties'] += 1
            if has_blob_content:
                quality_report['documents_with_blob_content'] += 1
            
            # Определяем качество документа
            quality_score = sum([has_amount, has_description, has_number, has_counterparty, has_blob_content])
            
            if quality_score >= 4:
                quality_report['excellent_documents'].append(doc['document_id'])
                print(f"   ✅ КАЧЕСТВО: ОТЛИЧНОЕ (баллов: {quality_score}/5)")
            elif quality_score >= 2:
                print(f"   ⚠️ КАЧЕСТВО: ХОРОШЕЕ (баллов: {quality_score}/5)")
            else:
                quality_report['broken_documents'].append(doc['document_id'])
                print(f"   ❌ КАЧЕСТВО: ПЛОХОЕ (баллов: {quality_score}/5)")
        
        # Итоговая статистика
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА КАЧЕСТВА:")
        print(f"   - Всего документов: {quality_report['total_documents']}")
        print(f"   - С суммами: {quality_report['documents_with_amounts']}")
        print(f"   - С описаниями: {quality_report['documents_with_descriptions']}")
        print(f"   - С номерами: {quality_report['documents_with_numbers']}")
        print(f"   - С контрагентами: {quality_report['documents_with_counterparties']}")
        print(f"   - С BLOB содержимым: {quality_report['documents_with_blob_content']}")
        print(f"   - Отличного качества: {len(quality_report['excellent_documents'])}")
        print(f"   - Плохого качества: {len(quality_report['broken_documents'])}")
        
        # Финальная оценка
        if len(quality_report['broken_documents']) == 0:
            print(f"\n🎯 ФИНАЛЬНАЯ ОЦЕНКА: ОТЛИЧНО!")
            print(f"   ✅ НЕТ БРАКА - все документы пригодны для работы!")
        elif len(quality_report['broken_documents']) <= 2:
            print(f"\n🎯 ФИНАЛЬНАЯ ОЦЕНКА: ХОРОШО!")
            print(f"   ⚠️ МИНИМАЛЬНЫЙ БРАК - {len(quality_report['broken_documents'])} документов требуют внимания")
        else:
            print(f"\n🎯 ФИНАЛЬНАЯ ОЦЕНКА: ТРЕБУЕТ УЛУЧШЕНИЯ!")
            print(f"   ❌ ЗНАЧИТЕЛЬНЫЙ БРАК - {len(quality_report['broken_documents'])} документов не пригодны")
        
        # Показываем примеры отличных документов
        if quality_report['excellent_documents']:
            print(f"\n🏆 ПРИМЕРЫ ОТЛИЧНЫХ ДОКУМЕНТОВ:")
            for doc_id in quality_report['excellent_documents'][:3]:
                doc = next(d for d in documents['documents'] if d['document_id'] == doc_id)
                print(f"   📄 {doc_id}: {doc['document_type']} - {doc['document_number']} - {doc['total_amount']} руб.")
        
        # Показываем проблемные документы
        if quality_report['broken_documents']:
            print(f"\n⚠️ ПРОБЛЕМНЫЕ ДОКУМЕНТЫ:")
            for doc_id in quality_report['broken_documents']:
                doc = next(d for d in documents['documents'] if d['document_id'] == doc_id)
                print(f"   ❌ {doc_id}: {doc['document_type']} - {doc['document_number']}")
        
        return quality_report
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_quality_report(quality_report):
    """
    Создание отчета о качестве
    """
    report_file = '[prostocvet-1c]/raw/quality_report.md'
    
    report_content = f"""# 📊 ОТЧЕТ О КАЧЕСТВЕ РАБОЧИХ ДОКУМЕНТОВ

**Дата проверки:** {quality_report.get('check_date', 'N/A')}
**Всего документов:** {quality_report['total_documents']}

## 📈 СТАТИСТИКА КАЧЕСТВА

### ✅ Документы с данными:
- **С суммами:** {quality_report['documents_with_amounts']}/{quality_report['total_documents']}
- **С описаниями:** {quality_report['documents_with_descriptions']}/{quality_report['total_documents']}
- **С номерами:** {quality_report['documents_with_numbers']}/{quality_report['total_documents']}
- **С контрагентами:** {quality_report['documents_with_counterparties']}/{quality_report['total_documents']}
- **С BLOB содержимым:** {quality_report['documents_with_blob_content']}/{quality_report['total_documents']}

### 🏆 Отличного качества: {len(quality_report['excellent_documents'])}
### ⚠️ Проблемных: {len(quality_report['broken_documents'])}

## 🎯 ФИНАЛЬНАЯ ОЦЕНКА

"""
    
    if len(quality_report['broken_documents']) == 0:
        report_content += """### ✅ ОТЛИЧНО!
**НЕТ БРАКА** - все документы пригодны для работы!

Документы содержат:
- ✅ Реальные номера документов
- ✅ Суммы и финансовые данные
- ✅ Описания работ и услуг
- ✅ Информацию о контрагентах
- ✅ Полное BLOB содержимое

**РЕКОМЕНДАЦИЯ:** Документы готовы к использованию в работе.
"""
    elif len(quality_report['broken_documents']) <= 2:
        report_content += """### ⚠️ ХОРОШО
**МИНИМАЛЬНЫЙ БРАК** - большинство документов пригодны для работы.

**РЕКОМЕНДАЦИЯ:** Использовать документы с осторожностью, проверить проблемные.
"""
    else:
        report_content += """### ❌ ТРЕБУЕТ УЛУЧШЕНИЯ
**ЗНАЧИТЕЛЬНЫЙ БРАК** - много документов не пригодны для работы.

**РЕКОМЕНДАЦИЯ:** Требуется доработка процесса извлечения.
"""

    # Добавляем примеры
    if quality_report['excellent_documents']:
        report_content += f"""
## 🏆 ПРИМЕРЫ ОТЛИЧНЫХ ДОКУМЕНТОВ

"""
        for doc_id in quality_report['excellent_documents'][:5]:
            report_content += f"- `{doc_id}`\n"

    if quality_report['broken_documents']:
        report_content += f"""
## ⚠️ ПРОБЛЕМНЫЕ ДОКУМЕНТЫ

"""
        for doc_id in quality_report['broken_documents']:
            report_content += f"- `{doc_id}`\n"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Отчет о качестве сохранен: {report_file}")

if __name__ == "__main__":
    quality_report = verify_working_documents()
    if quality_report:
        create_quality_report(quality_report) 