#!/usr/bin/env python3
"""
TDD тест для bidirectional sync кеша с диском.

RED ФАЗА: Создаем тесты которые должны провалиться,
так как bidirectional sync еще не реализован.

Корнер-кейсы и пропущенные тест-кейсы:
1. Обновление документа в кеше → автоматическая запись на диск
2. Создание нового документа в кеше → создание файла на диске  
3. Удаление документа из кеша → удаление файла с диска
4. Конкурентный доступ: изменение кеша и диска одновременно
5. Триггеры изменяют кеш → реальные файлы обновляются
6. Откат изменений при ошибке записи на диск
7. Проверка целостности после каждой операции записи

Автор: AI Assistant  
Дата: 24 May 2025
"""

import sys
import os
import tempfile
import hashlib
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def test_cache_update_syncs_to_disk():
    """RED ТЕСТ: Обновление документа в кеше должно автоматически обновить файл на диске"""
    
    from src.cache.real_inmemory_cache import get_cache
    
    # Создаем временный файл для теста
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        original_content = "# Исходный контент\nТест файл"
        f.write(original_content)
        test_file_path = f.name
    
    try:
        # Инициализируем кеш
        cache = get_cache()
        
        # Загружаем файл в кеш (если есть метод)
        if hasattr(cache, 'load_document'):
            cache.load_document(test_file_path)
        
        # КРИТИЧЕСКИЙ ТЕСТ: Обновляем документ в кеше
        updated_content = "# Обновленный контент\nИзмененный через кеш"
        
        # Это должно ПРОВАЛИТЬСЯ, так как update_document не реализован
        assert hasattr(cache, 'update_document'), "❌ RED ТЕСТ: Метод update_document не существует"
        
        cache.update_document(test_file_path, updated_content)
        
        # Проверяем, что файл на диске обновился
        with open(test_file_path, 'r', encoding='utf-8') as f:
            disk_content = f.read()
        
        assert disk_content == updated_content, f"❌ RED ТЕСТ: Файл на диске не обновился. Ожидали: {updated_content}, получили: {disk_content}"
        
        print("✅ GREEN: Bidirectional sync работает!")
        
    finally:
        # Очищаем временный файл
        os.unlink(test_file_path)

def test_cache_create_document_creates_file():
    """RED ТЕСТ: Создание документа в кеше должно создать файл на диске"""
    
    from src.cache.real_inmemory_cache import get_cache
    
    test_file_path = "test_new_document.md"
    new_content = "# Новый документ\nСоздан через кеш"
    
    try:
        cache = get_cache()
        
        # Это должно ПРОВАЛИТЬСЯ, так как create_document не реализован
        assert hasattr(cache, 'create_document'), "❌ RED ТЕСТ: Метод create_document не существует"
        
        cache.create_document(test_file_path, new_content)
        
        # Проверяем, что файл создался на диске
        assert os.path.exists(test_file_path), f"❌ RED ТЕСТ: Файл {test_file_path} не создался на диске"
        
        with open(test_file_path, 'r', encoding='utf-8') as f:
            disk_content = f.read()
        
        assert disk_content == new_content, f"❌ RED ТЕСТ: Содержимое файла не совпадает"
        
        print("✅ GREEN: Создание документа через кеш работает!")
        
    finally:
        # Очищаем файл если он создался
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_trigger_modifications_sync_to_disk():
    """RED ТЕСТ: Изменения через триггеры должны синхронизироваться с диском"""
    
    from src.cache.real_inmemory_cache import get_cache
    
    # Создаем временный todo файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        original_todo = "- [ ] **T999** Тестовая задача [TEST]\n"
        f.write(original_todo)
        test_todo_path = f.name
    
    try:
        cache = get_cache()
        
        # Симулируем работу триггера: завершение задачи
        if hasattr(cache, 'update_document'):
            completed_todo = "- [x] **T999** Тестовая задача [TEST] · завершено\n"
            cache.update_document(test_todo_path, completed_todo)
            
            # Проверяем синхронизацию с диском
            with open(test_todo_path, 'r', encoding='utf-8') as f:
                disk_content = f.read()
            
            assert "- [x]" in disk_content, "❌ RED ТЕСТ: Изменения триггера не синхронизировались с диском"
            print("✅ GREEN: Триггеры синхронизируются с диском!")
        else:
            print("❌ RED ТЕСТ: update_document не реализован - триггеры не могут синхронизироваться")
            assert False, "Bidirectional sync не реализован"
    
    finally:
        os.unlink(test_todo_path)

def test_concurrent_access_integrity():
    """GREEN ТЕСТ: Конкурентный доступ к кешу с RLock защитой"""
    
    import threading
    import time
    from src.cache.real_inmemory_cache import get_cache
    
    cache = get_cache()
    test_file = "test_concurrent.md"
    
    # Создаем тестовый файл
    cache.create_document(test_file, "Initial content")
    
    results = []
    errors = []
    
    def concurrent_update(thread_id):
        try:
            content = f"Content from thread {thread_id}"
            result = cache.update_document(test_file, content)
            results.append((thread_id, result))
        except Exception as e:
            errors.append((thread_id, str(e)))
    
    # Запускаем 5 потоков одновременно
    threads = []
    for i in range(5):
        t = threading.Thread(target=concurrent_update, args=(i,))
        threads.append(t)
        t.start()
    
    # Ждем завершения всех потоков
    for t in threads:
        t.join()
    
    # Проверяем что нет ошибок
    assert len(errors) == 0, f"Ошибки при конкурентном доступе: {errors}"
    
    # Проверяем что все операции завершились успешно
    assert len(results) == 5, f"Не все потоки завершились: {len(results)}/5"
    
    # Cleanup
    try:
        os.unlink(test_file)
    except:
        pass
    
    print("✅ GREEN ТЕСТ: Concurrent access integrity - ПРОШЕЛ")

def test_rollback_on_disk_write_failure():
    """GREEN ТЕСТ: Rollback кеша при ошибке записи на диск"""
    
    from src.cache.real_inmemory_cache import get_cache
    import tempfile
    
    cache = get_cache()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        original_content = "Original content"
        f.write(original_content)
        test_file_path = f.name
    
    try:
        # Загружаем файл в кеш
        cache.load_documents([os.path.dirname(test_file_path)])
        
        # Получаем текущий entry
        original_entry = cache.get_document(test_file_path)
        assert original_entry is not None, "Файл должен быть в кеше"
        
        # Делаем файл недоступным для записи (симулируем ошибку диска)
        os.chmod(test_file_path, 0o444)  # read-only
        
        # Пытаемся обновить - должно провалиться
        result = cache.update_document(test_file_path, "New content that should fail")
        
        # Проверяем что операция провалилась
        assert result == False, "Операция должна была провалиться"
        
        # Проверяем что кеш НЕ изменился (rollback сработал)
        current_entry = cache.get_document(test_file_path)
        assert current_entry is not None, "Entry не должен исчезнуть из кеша"
        assert current_entry.content == original_content, f"Кеш должен сохранить оригинальное содержимое, получили: {current_entry.content}"
        
        print("✅ GREEN ТЕСТ: Rollback on disk write failure - ПРОШЕЛ")
        
    finally:
        # Cleanup
        try:
            os.chmod(test_file_path, 0o644)  # восстанавливаем права
            os.unlink(test_file_path)
        except:
            pass

def main():
    """Запуск RED фазы TDD тестов"""
    
    print("🔴 === RED ФАЗА TDD: BIDIRECTIONAL CACHE SYNC ===")
    print("Все тесты должны ПРОВАЛИТЬСЯ, так как bidirectional sync не реализован\n")
    
    tests = [
        test_cache_update_syncs_to_disk,
        test_cache_create_document_creates_file, 
        test_trigger_modifications_sync_to_disk,
        test_concurrent_access_integrity,
        test_rollback_on_disk_write_failure
    ]
    
    failed_tests = 0
    
    for test in tests:
        try:
            print(f"🧪 Запуск: {test.__name__}")
            test()
            print(f"⚠️  НЕОЖИДАННО ПРОШЕЛ: {test.__name__}")
        except Exception as e:
            print(f"❌ ОЖИДАЕМО ПРОВАЛИЛСЯ: {test.__name__} - {str(e)}")
            failed_tests += 1
        print()
    
    print(f"🎯 РЕЗУЛЬТАТ RED ФАЗЫ: {failed_tests}/{len(tests)} тестов провалились (как и ожидалось)")
    
    if failed_tests == len(tests):
        print("✅ RED ФАЗА ЗАВЕРШЕНА: Все тесты провалились, можно переходить к GREEN фазе")
    else:
        print("⚠️  ВНИМАНИЕ: Некоторые тесты неожиданно прошли")

if __name__ == "__main__":
    main()