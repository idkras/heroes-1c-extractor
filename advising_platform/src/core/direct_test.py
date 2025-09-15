#!/usr/bin/env python3
"""
Прямой тест унифицированного интерфейса для работы с документами.
Исключает проверку синхронизации кеша для быстрого тестирования.
"""

import os
import sys
import time
import tempfile
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("direct_test")

def run_test():
    """
    Запускает прямое тестирование документ-менеджера.
    """
    # Гарантируем, что текущая директория - корень проекта
    os.chdir(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    try:
        # Импортируем модуль document_manager
        from src.core.document_manager import MarkdownDocument, DocumentManager
        
        # Создаем временную директорию для тестов
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_document.md")
            
            # Тестовое содержимое
            content = """# Тестовый документ

by Тестовый Автор
updated: 20 May 2025
version: 1.0

## Раздел 1

Содержимое раздела 1.

## Раздел 2

Содержимое раздела 2.
"""
            
            # Тест 1: Создание и чтение документа
            logger.info("Тест 1: Создание и чтение документа")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            document = MarkdownDocument(test_file)
            
            # Проверяем метаданные
            assert document.title == "Тестовый документ", f"Ожидался заголовок 'Тестовый документ', получено: {document.title}"
            assert document.metadata.get('author') == "Тестовый Автор", f"Ожидался автор 'Тестовый Автор', получено: {document.metadata.get('author')}"
            logger.info(f"Заголовок: {document.title}")
            logger.info(f"Автор: {document.metadata.get('author')}")
            
            # Тест 2: Извлечение разделов
            logger.info("Тест 2: Извлечение разделов")
            sections = document.extract_sections()
            assert "Раздел 1" in sections, "Раздел 1 не найден"
            assert "Раздел 2" in sections, "Раздел 2 не найден"
            logger.info(f"Найдено разделов: {len(sections)}")
            
            # Тест 3: Обновление заголовка
            logger.info("Тест 3: Обновление заголовка")
            document.title = "Обновленный документ"
            assert document.title == "Обновленный документ", f"Ожидался заголовок 'Обновленный документ', получено: {document.title}"
            logger.info(f"Новый заголовок: {document.title}")
            
            # Тест 4: Обновление раздела
            logger.info("Тест 4: Обновление раздела")
            document.update_section("Раздел 1", "Обновленное содержимое раздела 1.")
            document.save()
            
            # Читаем документ заново для проверки изменений
            new_document = MarkdownDocument(test_file)
            new_sections = new_document.extract_sections()
            
            assert "Раздел 1" in new_sections, "Раздел 1 не найден после обновления"
            assert "Обновленное содержимое раздела 1." in new_sections["Раздел 1"], "Содержимое Раздела 1 не обновлено"
            logger.info(f"Обновленный Раздел 1: {new_sections['Раздел 1']}")
            
            # Тест 5: Создание нового раздела
            logger.info("Тест 5: Создание нового раздела")
            new_document.update_section("Новый раздел", "Содержимое нового раздела.")
            new_document.save()
            
            # Читаем документ еще раз для проверки нового раздела
            final_document = MarkdownDocument(test_file)
            final_sections = final_document.extract_sections()
            
            assert "Новый раздел" in final_sections, "Новый раздел не найден"
            assert "Содержимое нового раздела." in final_sections["Новый раздел"], "Содержимое нового раздела не совпадает"
            logger.info(f"Новый раздел: {final_sections['Новый раздел']}")
            
            # Тест 6: Работа с DocumentManager
            logger.info("Тест 6: Работа с DocumentManager")
            manager = DocumentManager(temp_dir)
            
            # Создаем новый документ через менеджер
            new_doc_path = "manager_test.md"
            manager_doc = manager.create_document(
                new_doc_path,
                "# Документ через менеджер\n\nСоздан для тестирования DocumentManager."
            )
            
            assert manager_doc is not None, "Документ не создан через DocumentManager"
            assert manager_doc.title == "Документ через менеджер", f"Неверный заголовок: {manager_doc.title}"
            logger.info(f"Создан документ через менеджер: {new_doc_path}")
            
            # Получаем документ через менеджер
            retrieved_doc = manager.get_document(new_doc_path)
            assert retrieved_doc is not None, "Не удалось получить документ через DocumentManager"
            assert retrieved_doc.title == "Документ через менеджер", f"Неверный заголовок полученного документа: {retrieved_doc.title}"
            logger.info(f"Получен документ через менеджер: {new_doc_path}")
            
            logger.info("Все тесты успешно пройдены!")
            return True
            
    except AssertionError as e:
        logger.error(f"Тест не пройден: {e}")
        return False
    except Exception as e:
        logger.error(f"Ошибка при выполнении теста: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    run_test()