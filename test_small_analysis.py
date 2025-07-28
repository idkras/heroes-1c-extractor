#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для анализа небольшого участка файла 1CD
"""

import subprocess
import tempfile
import os
from pathlib import Path

def test_small_analysis():
    """Тестирование анализа на небольшом участке"""
    
    # Создаем временные файлы
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_log = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    
    try:
        # Тестируем с ограниченным размером
        cmd = [
            'head', '-c', '1048576', '1Cv8.1CD'  # Первые 1MB
        ]
        
        print("🔍 Тестирование чтения первых 1MB файла...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Чтение файла успешно")
            print(f"📊 Прочитано байт: {len(result.stdout)}")
            return True
        else:
            print("❌ Ошибка при чтении файла")
            return False
            
    finally:
        # Удаляем временные файлы
        for temp_file in [temp_csv.name, temp_log.name]:
            try:
                os.unlink(temp_file)
            except:
                pass

if __name__ == "__main__":
    test_small_analysis()
