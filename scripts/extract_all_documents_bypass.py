#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from datetime import datetime
import struct
from typing import Optional, List, Any, Dict, Collection

def extract_all_documents_bypass() -> None:
    """
    Извлечение всех документов, обходя проблему с onec_dtools
    Используем прямое чтение файла и поиск по паттернам
    """
    print("🔍 Извлечение ВСЕХ документов (обход onec_dtools)")
    print("🎯 ЦЕЛЬ: Найти все документы, счета-фактуры, накладные, акты")
    print("=" * 60)

    results: Dict[str, Any] = {
        "all_documents": [],
        "document_types": {
            "acts": [],
            "invoices": [],
            "waybills": [],
            "retail_sales": [],
            "other_documents": []
        },
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "source_file": "data/raw/1Cv8.1CD",
            "total_documents_found": 0,
            "extraction_method": "bypass_onec_dtools"
        },
    }

    try:
        # Читаем файл напрямую
        with open("data/raw/1Cv8.1CD", "rb") as f:
            print("✅ Файл открыт для прямого чтения")
            
            # Читаем первые 100MB для поиска паттернов
            chunk_size = 1024 * 1024  # 1MB chunks
            total_read = 0
            max_read = 100 * 1024 * 1024  # 100MB
            
            while total_read < max_read:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                total_read += len(chunk)
                print(f"📊 Прочитано: {total_read // (1024*1024)}MB")
                
                # Ищем паттерны документов
                found_documents = search_document_patterns(chunk, total_read - len(chunk))
                results["all_documents"].extend(found_documents)
                
                # Ищем конкретные типы документов
                search_specific_document_types(chunk, results, total_read - len(chunk))

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Сохраняем результаты
    with open('data/results/all_documents_bypass.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Результаты сохранены в: data/results/all_documents_bypass.json")
    print(f"📊 Всего найдено документов: {len(results['all_documents'])}")
    
    # Статистика по типам
    document_types = results["document_types"]
    if isinstance(document_types, dict):
        for doc_type, docs in document_types.items():
            if isinstance(docs, list) and docs:
                print(f"   📋 {doc_type}: {len(docs)} документов")

    return None


def search_document_patterns(chunk: bytes, offset: int) -> List[Dict[str, Any]]:
    """
    Поиск паттернов документов в бинарных данных
    """
    found_documents: List[Dict[str, Any]] = []
    
    # Паттерны для поиска
    patterns = [
        b"_DOCUMENT",
        b"_NUMBER",
        b"_DATE_TIME",
        b"_POSTED",
        b"_MARKED",
        b"_VERSION",
        b"_FLD",
        b"_IDRREF",
        b"_DOCUMENTTREF",
        b"_DOCUMENTRREF"
    ]
    
    for pattern in patterns:
        pos = 0
        while True:
            pos = chunk.find(pattern, pos)
            if pos == -1:
                break
            
            # Извлекаем контекст вокруг найденного паттерна
            start = max(0, pos - 100)
            end = min(len(chunk), pos + 200)
            context = chunk[start:end]
            
            document = {
                "pattern": pattern.decode('utf-8', errors='ignore'),
                "offset": offset + pos,
                "context": context.decode('utf-8', errors='ignore'),
                "context_hex": context.hex()
            }
            found_documents.append(document)
            
            pos += len(pattern)
    
    return found_documents


def search_specific_document_types(chunk: bytes, results: Dict[str, Any], offset: int) -> None:
    """
    Поиск конкретных типов документов
    """
    # Поиск актов выполненных работ
    if b"_DOCUMENT163" in chunk:
        results["document_types"]["acts"].append({
            "type": "act",
            "table": "_DOCUMENT163",
            "offset": offset,
            "found_in_chunk": True
        })
    
    # Поиск счетов-фактур
    if b"_DOCUMENT184" in chunk:
        results["document_types"]["invoices"].append({
            "type": "invoice",
            "table": "_DOCUMENT184", 
            "offset": offset,
            "found_in_chunk": True
        })
    
    # Поиск накладных
    if b"_DOCUMENT154" in chunk:
        results["document_types"]["waybills"].append({
            "type": "waybill",
            "table": "_DOCUMENT154",
            "offset": offset,
            "found_in_chunk": True
        })
    
    # Поиск розничных продаж
    if b"_DOCUMENT184" in chunk and b"Roznichnaya" in chunk:
        results["document_types"]["retail_sales"].append({
            "type": "retail_sale",
            "table": "_DOCUMENT184",
            "offset": offset,
            "found_in_chunk": True
        })
    
    # Поиск других документов
    other_patterns = [b"_DOCUMENT137", b"_DOCUMENT12259", b"_DOCUMENT13139"]
    for pattern in other_patterns:
        if pattern in chunk:
            results["document_types"]["other_documents"].append({
                "type": "other",
                "table": pattern.decode('utf-8'),
                "offset": offset,
                "found_in_chunk": True
            })


if __name__ == "__main__":
    extract_all_documents_bypass()
