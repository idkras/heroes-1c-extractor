#!/usr/bin/env python3
"""
Тестовый скрипт для прямой отправки сообщений в чат Replit.

Этот скрипт демонстрирует прямое использование функции report_progress
для отправки сообщений в чат Replit.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Используем встроенную функцию Replit для отправки сообщений в чат
def send_to_chat(message):
    """
    Отправляет сообщение в чат Replit, используя функцию report_progress.
    """
    print(f"\nОтправка сообщения в чат Replit: {message[:50]}...")
    
    # Вызываем функцию report_progress напрямую из модуля в Replit
    try:
        # Этот код будет работать только в среде Replit
        from antml.function_calls import report_progress
        report_progress(summary=message)
        print("Сообщение успешно отправлено в чат Replit через antml.function_calls.report_progress")
        return True
    except ImportError:
        try:
            # Альтернативный вариант импорта
            import importlib
            report_progress = getattr(importlib.import_module("report_progress"), "report_progress")
            report_progress(summary=message)
            print("Сообщение успешно отправлено в чат Replit через importlib")
            return True
        except (ImportError, AttributeError):
            try:
                # Если функция report_progress доступна как встроенная функция
                import builtins
                if hasattr(builtins, 'report_progress'):
                    builtins.report_progress(summary=message)
                    print("Сообщение успешно отправлено в чат Replit через builtins")
                    return True
            except Exception as e:
                print(f"Ошибка при отправке через builtins: {str(e)}")
    
    # Если ни один из методов не сработал, используем прямой вызов API
    try:
        # Прямой вызов функции report_progress
        import subprocess
        cmd = [
            "python", "-c", 
            "from antml.function_calls import report_progress; " + 
            f"report_progress(summary='''{message}''')"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("Сообщение успешно отправлено в чат Replit через subprocess")
            return True
        else:
            print(f"Ошибка при отправке через subprocess: {result.stderr}")
    except Exception as e:
        print(f"Ошибка при отправке через subprocess: {str(e)}")
    
    print("Не удалось отправить сообщение в чат Replit. Используем вывод в консоль.")
    print(f"\n[CHAT OUTPUT]\n{message}\n")
    return False

def main():
    """
    Основная функция скрипта.
    """
    # Формируем тестовое сообщение для отправки в чат
    message = """
📊 Тестовое сообщение для проверки интеграции с чатом Replit

✓ Проверка возможности отправки текстовых сообщений
✓ Проверка форматирования и поддержки эмодзи
✓ Тестирование механизма интеграции с чатом

→ Успешная отправка этого сообщения означает, что интеграция работает!
    """
    
    # Отправляем сообщение в чат
    success = send_to_chat(message)
    
    # Проверяем результат
    if success:
        print("Тест интеграции с чатом Replit успешно завершен!")
    else:
        print("Тест интеграции с чатом Replit завершился с ошибками.")

if __name__ == "__main__":
    main()