#!/usr/bin/env python3
"""
MCP команды для верификации корректности данных в кеше vs реальных файлов
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям
current_dir = Path(__file__).parent.resolve()
advising_platform_dir = current_dir.parent.parent
sys.path.insert(0, str(advising_platform_dir))

def verify_cache_vs_filesystem():
    """
    Сравнивает содержимое DuckDB кеша с реальными файлами стандартов
    
    JTBD: Я (система) хочу постоянно проверять, что кеш содержит актуальные данные,
    чтобы исключить расхождения между кешем и файловой системой.
    """
    
    # Читаем реальные стандарты из [standards .md]
    standards_dir = Path("[standards .md]")
    real_standards = []
    
    if standards_dir.exists():
        for md_file in standards_dir.rglob("*.md"):
            # Исключаем архивные файлы
            if "[archive]" not in str(md_file):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        real_standards.append({
                            "path": str(md_file),
                            "name": md_file.name,
                            "content_hash": hash(content[:1000]),  # Хеш первых 1000 символов
                            "size": len(content)
                        })
                except Exception as e:
                    print(f"⚠️ Ошибка чтения {md_file}: {e}")
    
    # Читаем данные из DuckDB кеша
    try:
        from src.standards_system import UnifiedStandardsSystem
        system = UnifiedStandardsSystem()
        
        cached_standards = []
        result = system.conn.execute("SELECT id, name, content FROM standards").fetchall()
        
        for row in result:
            cached_standards.append({
                "id": row[0],
                "name": row[1],
                "content_hash": hash(row[2][:1000]) if row[2] else None,
                "size": len(row[2]) if row[2] else 0
            })
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка доступа к кешу: {e}",
            "verification_failed": True
        }
    
    # Сравниваем данные
    real_count = len(real_standards)
    cached_count = len(cached_standards)
    
    mismatches = []
    missing_in_cache = []
    extra_in_cache = []
    
    # Создаем индексы для быстрого поиска
    real_by_name = {std["name"]: std for std in real_standards}
    cached_by_name = {std["name"]: std for std in cached_standards}
    
    # Проверяем какие файлы отсутствуют в кеше
    for real_std in real_standards:
        if real_std["name"] not in cached_by_name:
            missing_in_cache.append(real_std["name"])
        else:
            cached_std = cached_by_name[real_std["name"]]
            if real_std["content_hash"] != cached_std["content_hash"]:
                mismatches.append({
                    "file": real_std["name"],
                    "real_size": real_std["size"],
                    "cached_size": cached_std["size"]
                })
    
    # Проверяем лишние файлы в кеше
    for cached_std in cached_standards:
        if cached_std["name"] not in real_by_name:
            extra_in_cache.append(cached_std["name"])
    
    return {
        "success": True,
        "real_standards_count": real_count,
        "cached_standards_count": cached_count,
        "missing_in_cache": missing_in_cache,
        "extra_in_cache": extra_in_cache,
        "content_mismatches": mismatches,
        "cache_accuracy": (real_count - len(missing_in_cache) - len(mismatches)) / real_count if real_count > 0 else 0,
        "verification_passed": len(missing_in_cache) == 0 and len(mismatches) == 0 and len(extra_in_cache) == 0
    }

def create_self_doubt_prompt():
    """
    Создает промпт для постоянной самопроверки
    
    Возвращает текст, который нужно добавить в README.md и код для напоминания
    о необходимости проверки результатов.
    """
    
    prompt_text = """
## КРИТИЧЕСКОЕ НАПОМИНАНИЕ ДЛЯ AI ASSISTANT

**Что я не учитываю?** - задавай себе этот вопрос ПЕРЕД каждым ответом пользователю.

### Обязательные проверки:
1. **Проверил ли я данные из первоисточника?** (не полагался на логи/кеш)
2. **Сравнил ли реальность с моими утверждениями?** 
3. **Проверил ли я свои математические вычисления?**
4. **Учел ли я качество данных, а не только количество?**
5. **Обратил ли внимание на все WARNING и ERROR в логах?**

### Если НЕТ хотя бы на один вопрос → ОСТАНОВИСЬ и проверь

### Фразы-триггеры самосомнения:
- "Результат превышает ожидания" → ПРОВЕРИТЬ реальные данные
- "153% выполнения" → ПРОВЕРИТЬ математику и качество
- "Система работает корректно" → ПРОВЕРИТЬ логи на ошибки
- "Все успешно" → НАЙТИ что может быть неуспешно

### Принцип: ДОВЕРЯЙ, НО ПРОВЕРЯЙ свои собственные выводы
"""
    
    return prompt_text

if __name__ == "__main__":
    # Запускаем верификацию
    result = verify_cache_vs_filesystem()
    
    print("🔍 ВЕРИФИКАЦИЯ КЕША vs ФАЙЛОВАЯ СИСТЕМА")
    print(f"📊 Реальных стандартов: {result['real_standards_count']}")
    print(f"📊 В кеше: {result['cached_standards_count']}")
    
    if result.get("missing_in_cache"):
        print(f"❌ Отсутствует в кеше: {len(result['missing_in_cache'])}")
        for file in result["missing_in_cache"][:5]:
            print(f"   - {file}")
    
    if result.get("extra_in_cache"):
        print(f"⚠️ Лишние в кеше: {len(result['extra_in_cache'])}")
        for file in result["extra_in_cache"][:5]:
            print(f"   - {file}")
    
    if result.get("content_mismatches"):
        print(f"🔄 Не совпадает содержимое: {len(result['content_mismatches'])}")
    
    accuracy = result.get("cache_accuracy", 0) * 100
    print(f"🎯 Точность кеша: {accuracy:.1f}%")
    
    if not result.get("verification_passed", False):
        print("❌ ВЕРИФИКАЦИЯ НЕ ПРОЙДЕНА - кеш содержит неточные данные")
        sys.exit(1)
    else:
        print("✅ ВЕРИФИКАЦИЯ ПРОЙДЕНА")