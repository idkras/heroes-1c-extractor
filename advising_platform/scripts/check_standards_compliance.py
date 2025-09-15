#!/usr/bin/env python3
"""
Скрипт для автоматической проверки соответствия документов стандартам перед их созданием.
Проверяет, были ли прочитаны стандарты registry_standard и qa_standard перед созданием документа.

Использование:
    python check_standards_compliance.py [путь к создаваемому документу]

Пример:
    python check_standards_compliance.py "../[todo · incidents]/new_incident.md"
"""

import os
import sys
import json
import re
import datetime
from pathlib import Path

# Ключевые стандарты, которые должны быть прочитаны перед созданием документа
REQUIRED_STANDARDS = {
    "standard:registry": "[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.1 registry standard 14 may 2025 0430 cet by ai assistant.md",
    "standard:ai_qa": "[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.2 ai qa standard 14 may 2025 0550 cet by ai assistant.md"
}

# Файл с историей просмотра стандартов
STANDARDS_ACCESS_LOG = "data/standards_access_log.json"

def load_access_log():
    """Загружает историю просмотра стандартов"""
    if os.path.exists(STANDARDS_ACCESS_LOG):
        with open(STANDARDS_ACCESS_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"accessed_standards": {}, "last_update": ""}

def save_access_log(log_data):
    """Сохраняет историю просмотра стандартов"""
    os.makedirs(os.path.dirname(STANDARDS_ACCESS_LOG), exist_ok=True)
    with open(STANDARDS_ACCESS_LOG, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def log_standard_access(standard_path):
    """Записывает факт просмотра стандарта"""
    log_data = load_access_log()
    current_time = datetime.datetime.now().isoformat()
    
    if standard_path not in log_data["accessed_standards"]:
        log_data["accessed_standards"][standard_path] = []
    
    log_data["accessed_standards"][standard_path].append(current_time)
    log_data["last_update"] = current_time
    
    save_access_log(log_data)
    print(f"✅ Стандарт прочитан: {standard_path}")

def check_standards_compliance(document_path):
    """Проверяет, были ли прочитаны обязательные стандарты перед созданием документа"""
    access_log = load_access_log()
    missing_standards = []
    
    for standard_id, standard_path in REQUIRED_STANDARDS.items():
        if standard_path not in access_log["accessed_standards"]:
            missing_standards.append(standard_path)
    
    if missing_standards:
        print("⚠️ ВНИМАНИЕ: Перед созданием документа необходимо ознакомиться со следующими стандартами:")
        for path in missing_standards:
            print(f"   - {path}")
        return False
    
    print(f"✅ Все необходимые стандарты прочитаны. Можно создавать документ: {document_path}")
    return True

def create_checklists():
    """Создает автоматический чек-лист для проверки соответствия стандартам"""
    checklist = [
        "- [ ] Проверить соответствие стандарту registry_standard",
        "- [ ] Проверить соответствие стандарту ai_qa_standard",
        "- [ ] Убедиться, что документ использует абстрактные ссылки вместо физических путей",
        "- [ ] Проверить, что исполнен протокол коммуникации при инциденте",
        "- [ ] Провести анализ '5 почему' для выявления корневых причин"
    ]
    
    print("\n📋 Чек-лист для создания документа:")
    for item in checklist:
        print(item)

def main():
    if len(sys.argv) != 2:
        print("Использование: python check_standards_compliance.py [путь к создаваемому документу]")
        sys.exit(1)
    
    document_path = sys.argv[1]
    
    # Проверка соответствия стандартам
    is_compliant = check_standards_compliance(document_path)
    
    if not is_compliant:
        print("\n❌ Документ не может быть создан без ознакомления с обязательными стандартами.")
        print("📌 Пожалуйста, прочтите указанные стандарты и повторите попытку.")
        sys.exit(1)
    
    # Создание чек-листа
    create_checklists()
    
    print("\n🎯 Теперь вы можете создать документ, следуя чек-листу.")

if __name__ == "__main__":
    main()