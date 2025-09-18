#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from datetime import datetime


def search_bratislavskaya_in_results():
    """
    Поиск документов по Братиславской в уже готовых результатах
    """
    print("🔍 Поиск документов по Братиславской в готовых результатах")
    print("🎯 ЦЕЛЬ: Найти все документы, связанные с Братиславской")
    print("=" * 60)

    results = {
        "bratislavskaya_documents": [],
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "source_files": [],
            "total_documents_found": 0,
        },
    }

    # Ключевые слова для поиска
    search_keywords = [
        "братиславская",
        "братиславская",
        "братиславская",
        "братиславская",
        "братиславская"
    ]

    # Файлы для поиска
    result_files = [
        "data/results/all_available_data.json",
        "data/results/real_blob_data.json",
        "data/results/final_documents.json",
        "data/results/retail_sales_analysis.json",
        "data/results/search_documents_results.json"
    ]

    for file_path in result_files:
        if os.path.exists(file_path):
            print(f"\n📊 Анализ файла: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                results["metadata"]["source_files"].append(file_path)
                
                # Поиск в структуре данных
                found_documents = search_in_data_structure(data, search_keywords, file_path)
                
                if found_documents:
                    results["bratislavskaya_documents"].extend(found_documents)
                    print(f"   ✅ Найдено документов: {len(found_documents)}")
                else:
                    print(f"   ❌ Документы не найдены")
                    
            except Exception as e:
                print(f"   ⚠️ Ошибка при чтении файла: {e}")
                continue

    # Сохраняем результаты
    with open('data/results/bratislavskaya_search_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Результаты сохранены в: data/results/bratislavskaya_search_results.json")
    print(f"📊 Всего найдено документов: {len(results['bratislavskaya_documents'])}")

    return results


def search_in_data_structure(data, keywords, file_path):
    """
    Рекурсивный поиск ключевых слов в структуре данных
    """
    found_documents = []
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                search_recursive(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                search_recursive(item, current_path)
        elif isinstance(obj, str):
            obj_lower = obj.lower()
            for keyword in keywords:
                if keyword.lower() in obj_lower:
                    found_documents.append({
                        "file_path": file_path,
                        "path": path,
                        "content": obj,
                        "keyword": keyword
                    })
                    print(f"   🔍 Найдено '{keyword}' в {path}: {obj[:100]}...")
    
    search_recursive(data)
    return found_documents


if __name__ == "__main__":
    search_bratislavskaya_in_results()
