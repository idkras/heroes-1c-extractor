#!/usr/bin/env python3
"""
Инструмент для проверки соответствия документов стандартам.
Интегрируется с API платформы для обеспечения соблюдения стандартов при создании документов.
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path

class StandardsValidator:
    """
    Класс для проверки соответствия документов стандартам.
    Проверяет, были ли прочитаны необходимые стандарты перед созданием документа,
    выполняет предварительную валидацию и предоставляет чек-листы.
    """
    
    def __init__(self, config_path=None):
        """
        Инициализация валидатора стандартов.
        
        Args:
            config_path (str, optional): Путь к файлу конфигурации. По умолчанию None.
        """
        self.required_standards = {
            "standard:registry": "[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.1 registry standard 14 may 2025 0430 cet by ai assistant.md",
            "standard:ai_qa": "[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.2 ai qa standard 14 may 2025 0550 cet by ai assistant.md"
        }
        
        self.log_file = "data/standards_access_log.json"
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.required_standards = config.get('required_standards', self.required_standards)
                self.log_file = config.get('log_file', self.log_file)
    
    def load_access_log(self):
        """
        Загружает журнал доступа к стандартам.
        
        Returns:
            dict: Журнал доступа к стандартам.
        """
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"accessed_standards": {}, "last_update": ""}
    
    def save_access_log(self, log_data):
        """
        Сохраняет журнал доступа к стандартам.
        
        Args:
            log_data (dict): Журнал доступа к стандартам.
        """
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def log_standard_access(self, standard_path):
        """
        Регистрирует доступ к стандарту.
        
        Args:
            standard_path (str): Путь к стандарту.
            
        Returns:
            bool: True, если доступ успешно зарегистрирован.
        """
        log_data = self.load_access_log()
        current_time = datetime.datetime.now().isoformat()
        
        if standard_path not in log_data["accessed_standards"]:
            log_data["accessed_standards"][standard_path] = []
        
        log_data["accessed_standards"][standard_path].append(current_time)
        log_data["last_update"] = current_time
        
        self.save_access_log(log_data)
        return True
    
    def check_standards_compliance(self, document_path):
        """
        Проверяет соответствие стандартам перед созданием документа.
        
        Args:
            document_path (str): Путь к создаваемому документу.
            
        Returns:
            tuple: (bool, list) Результат проверки и список непрочитанных стандартов.
        """
        access_log = self.load_access_log()
        missing_standards = []
        
        for standard_id, standard_path in self.required_standards.items():
            if standard_path not in access_log["accessed_standards"]:
                missing_standards.append(standard_path)
        
        if missing_standards:
            return False, missing_standards
        
        return True, []
    
    def get_checklist_by_document_type(self, document_path):
        """
        Возвращает чек-лист в зависимости от типа документа.
        
        Args:
            document_path (str): Путь к документу.
            
        Returns:
            list: Чек-лист для создания документа.
        """
        base_checklist = [
            "- [ ] Проверить соответствие стандарту registry_standard",
            "- [ ] Проверить соответствие стандарту ai_qa_standard",
            "- [ ] Убедиться, что документ использует абстрактные ссылки вместо физических путей"
        ]
        
        if "incident" in document_path.lower():
            incident_checklist = base_checklist + [
                "- [ ] Проверить, что исполнен протокол коммуникации при инциденте",
                "- [ ] Провести анализ '5 почему' для выявления корневых причин"
            ]
            return incident_checklist
        
        if "task" in document_path.lower():
            task_checklist = base_checklist + [
                "- [ ] Задача имеет четкие критерии Definition of Done",
                "- [ ] Определен приоритет задачи"
            ]
            return task_checklist
        
        return base_checklist
    
    def get_template_by_document_type(self, document_path):
        """
        Возвращает путь к шаблону в зависимости от типа документа.
        
        Args:
            document_path (str): Путь к документу.
            
        Returns:
            str or None: Путь к шаблону или None, если шаблон не найден.
        """
        if "incident" in document_path.lower():
            return "templates/incident_template.md"
        
        if "task" in document_path.lower():
            return "templates/task_template.md"
        
        return None

def main():
    """
    Основная функция для запуска инструмента валидации стандартов из командной строки.
    """
    parser = argparse.ArgumentParser(description="Проверка соответствия документов стандартам.")
    parser.add_argument("document_path", help="Путь к проверяемому или создаваемому документу.")
    parser.add_argument("--log", action="store_true", help="Регистрировать доступ к стандарту.")
    parser.add_argument("--standard", help="Путь к стандарту для регистрации доступа.")
    parser.add_argument("--config", help="Путь к файлу конфигурации.")
    
    args = parser.parse_args()
    
    validator = StandardsValidator(args.config)
    
    if args.log and args.standard:
        if validator.log_standard_access(args.standard):
            print(f"✅ Доступ к стандарту {args.standard} зарегистрирован")
        else:
            print(f"❌ Не удалось зарегистрировать доступ к стандарту {args.standard}")
        return 0
    
    compliance, missing_standards = validator.check_standards_compliance(args.document_path)
    
    if not compliance:
        print("⚠️ ВНИМАНИЕ: Перед созданием документа необходимо ознакомиться со следующими стандартами:")
        for path in missing_standards:
            print(f"   - {path}")
        return 1
    
    print(f"✅ Все необходимые стандарты прочитаны. Можно создавать документ: {args.document_path}")
    
    checklist = validator.get_checklist_by_document_type(args.document_path)
    print("\n📋 Чек-лист для создания документа:")
    for item in checklist:
        print(item)
    
    template_path = validator.get_template_by_document_type(args.document_path)
    if template_path:
        print(f"\n📝 Рекомендуемый шаблон: {template_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())