#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Система разрешения abstract адресов в физические пути.

Восстанавливает потерянную функциональность логических адресов вместо физических путей:
- abstract://standard:task_master → [standards .md]/0. core standards/0.0 task master...
- abstract://task:todo → [todo · incidents]/todo.md
- abstract://incident:ai → [todo · incidents]/ai.incidents.md

Основанный на найденных в коде примерах abstract:// ссылок.
"""

import os
import json
import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AbstractMapping:
    """Маппинг abstract адреса на физический путь."""
    logical_id: str       # task:todo, standard:task_master
    physical_path: str    # реальный путь к файлу
    doc_type: str        # task, standard, incident, project
    title: str           # человеко-читаемый заголовок
    description: str = ""  # описание

class AbstractResolver:
    """Класс для разрешения abstract адресов."""
    
    def __init__(self):
        """Инициализация резолвера."""
        self.mappings: Dict[str, AbstractMapping] = {}
        self.cache_file = "advising_platform/data/abstract_mappings.json"
        self._load_mappings()
        self._register_core_mappings()
    
    def _load_mappings(self):
        """Загружает маппинги из кеша."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for logical_id, mapping_data in data.items():
                    self.mappings[logical_id] = AbstractMapping(
                        logical_id=logical_id,
                        physical_path=mapping_data.get('physical_path', ''),
                        doc_type=mapping_data.get('doc_type', 'unknown'),
                        title=mapping_data.get('title', ''),
                        description=mapping_data.get('description', '')
                    )
                
                logger.info(f"Загружено {len(self.mappings)} abstract маппингов")
        except Exception as e:
            logger.warning(f"Не удалось загрузить abstract маппинги: {e}")
    
    def _save_mappings(self):
        """Сохраняет маппинги в кеш."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            data = {}
            for logical_id, mapping in self.mappings.items():
                data[logical_id] = {
                    'physical_path': mapping.physical_path,
                    'doc_type': mapping.doc_type,
                    'title': mapping.title,
                    'description': mapping.description
                }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранено {len(self.mappings)} abstract маппингов")
        except Exception as e:
            logger.error(f"Ошибка при сохранении abstract маппингов: {e}")
    
    def _register_core_mappings(self):
        """Регистрирует основные маппинги системы."""
        core_mappings = [
            # Задачи и инциденты
            AbstractMapping(
                logical_id="task:todo",
                physical_path="[todo · incidents]/todo.md",
                doc_type="task",
                title="Основной список задач",
                description="Центральный файл со всеми задачами проекта"
            ),
            AbstractMapping(
                logical_id="incident:ai",
                physical_path="[todo · incidents]/ai.incidents.md", 
                doc_type="incident",
                title="Инциденты AI системы",
                description="Журнал инцидентов и проблем AI системы"
            ),
            
            # Стандарты - основные
            AbstractMapping(
                logical_id="standard:task_master",
                physical_path="[standards .md]/0. core standards/0.0 task master 10 may 2226 cet by ilya krasinsky.md",
                doc_type="standard",
                title="Task Master Standard",
                description="Основной стандарт для работы с задачами"
            ),
            AbstractMapping(
                logical_id="standard:process_task",
                physical_path="[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.4 process task standard 14 may 2025 0640 cet by ai assistant.md",
                doc_type="standard", 
                title="Process Task Standard",
                description="Стандарт процессов работы с задачами"
            ),
            AbstractMapping(
                logical_id="standard:ticket",
                physical_path="[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.5 ticket standard 14 may 2025 0650 cet by ai assistant.md",
                doc_type="standard",
                title="Ticket Standard", 
                description="Стандарт оформления тикетов"
            ),
            AbstractMapping(
                logical_id="standard:hypothesis",
                physical_path="[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.8 hypothesis standard 15 may 2025 1745 cet by ai assistant.md",
                doc_type="standard",
                title="Hypothesis Standard",
                description="Стандарт работы с гипотезами"
            ),
            AbstractMapping(
                logical_id="standard:ai_incident", 
                physical_path="[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.9 ai incident standard 15 may 2025 2042 cet by ai assistant.md",
                doc_type="standard",
                title="AI Incident Standard",
                description="Стандарт обработки инцидентов AI"
            ),
            
            # Директории
            AbstractMapping(
                logical_id="dir:standards",
                physical_path="[standards .md]",
                doc_type="directory",
                title="Директория стандартов",
                description="Основная директория со всеми стандартами"
            ),
            AbstractMapping(
                logical_id="dir:archive",
                physical_path="[standards .md]/[archive]",
                doc_type="directory", 
                title="Архив стандартов",
                description="Архивные и устаревшие стандарты"
            ),
            AbstractMapping(
                logical_id="dir:todo_incidents",
                physical_path="[todo · incidents]",
                doc_type="directory",
                title="Задачи и инциденты",
                description="Директория с задачами и инцидентами"
            ),
        ]
        
        # Регистрируем все маппинги
        for mapping in core_mappings:
            self.mappings[mapping.logical_id] = mapping
        
        # Сохраняем в кеш
        self._save_mappings()
        
        logger.info(f"Зарегистрировано {len(core_mappings)} основных abstract маппингов")
    
    def resolve(self, abstract_address: str) -> Optional[str]:
        """
        Разрешает abstract адрес в физический путь.
        
        Args:
            abstract_address: Abstract адрес (abstract://task:todo или task:todo)
            
        Returns:
            Optional[str]: Физический путь или None
        """
        # Нормализуем адрес - убираем protocol prefix
        normalized = abstract_address
        if normalized.startswith("abstract://"):
            normalized = normalized[11:]  # убираем "abstract://"
        
        # Ищем в маппингах
        mapping = self.mappings.get(normalized)
        if mapping:
            return mapping.physical_path
        
        # Если не найден, логируем и возвращаем исходный адрес
        logger.warning(f"Abstract адрес не найден: {abstract_address}")
        return abstract_address
    
    def resolve_to_absolute_path(self, abstract_address: str) -> Optional[str]:
        """
        Разрешает abstract адрес в абсолютный физический путь.
        
        Args:
            abstract_address: Abstract адрес
            
        Returns:
            Optional[str]: Абсолютный путь или None
        """
        relative_path = self.resolve(abstract_address)
        if relative_path and relative_path != abstract_address:
            # Конвертируем относительный путь в абсолютный
            if relative_path.startswith("["):
                # Убираем квадратные скобки из имен директорий
                clean_path = relative_path.replace("[", "").replace("]", "")
                return os.path.abspath(clean_path)
            else:
                return os.path.abspath(relative_path)
        return None
    
    def register_mapping(self, logical_id: str, physical_path: str, 
                        doc_type: str, title: str, description: str = "") -> bool:
        """
        Регистрирует новый abstract маппинг.
        
        Args:
            logical_id: Логический идентификатор (task:new_task)
            physical_path: Физический путь к файлу
            doc_type: Тип документа
            title: Заголовок
            description: Описание
            
        Returns:
            bool: True, если регистрация успешна
        """
        try:
            mapping = AbstractMapping(
                logical_id=logical_id,
                physical_path=physical_path,
                doc_type=doc_type,
                title=title,
                description=description
            )
            
            self.mappings[logical_id] = mapping
            self._save_mappings()
            
            logger.info(f"Зарегистрирован abstract маппинг: {logical_id} → {physical_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при регистрации маппинга {logical_id}: {e}")
            return False
    
    def get_mappings_by_type(self, doc_type: str) -> List[AbstractMapping]:
        """
        Возвращает все маппинги заданного типа.
        
        Args:
            doc_type: Тип документа
            
        Returns:
            List[AbstractMapping]: Список маппингов
        """
        return [mapping for mapping in self.mappings.values() 
                if mapping.doc_type == doc_type]
    
    def convert_text_links(self, text: str, to_abstract: bool = True) -> str:
        """
        Конвертирует ссылки в тексте между abstract и физическими путями.
        
        Args:
            text: Исходный текст
            to_abstract: True - в abstract, False - в физические пути
            
        Returns:
            str: Текст с конвертированными ссылками
        """
        if to_abstract:
            # Конвертируем физические пути в abstract
            for logical_id, mapping in self.mappings.items():
                # Заменяем физические пути на abstract ссылки
                text = text.replace(
                    f"[{mapping.title}]({mapping.physical_path})",
                    f"[{mapping.title}](abstract://{logical_id})"
                )
        else:
            # Конвертируем abstract в физические пути
            import re
            abstract_pattern = r'\[([^\]]+)\]\(abstract://([^)]+)\)'
            
            def replace_abstract(match):
                link_text = match.group(1)
                logical_id = match.group(2)
                physical_path = self.resolve(logical_id)
                return f"[{link_text}]({physical_path})"
            
            text = re.sub(abstract_pattern, replace_abstract, text)
        
        return text
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику по abstract маппингам.
        
        Returns:
            Dict[str, Any]: Статистика
        """
        stats = {
            'total_mappings': len(self.mappings),
            'by_type': {},
            'mappings_list': []
        }
        
        # Подсчитываем по типам
        for mapping in self.mappings.values():
            doc_type = mapping.doc_type
            stats['by_type'][doc_type] = stats['by_type'].get(doc_type, 0) + 1
            
            stats['mappings_list'].append({
                'logical_id': mapping.logical_id,
                'physical_path': mapping.physical_path,
                'doc_type': mapping.doc_type,
                'title': mapping.title
            })
        
        return stats

# Глобальный экземпляр резолвера
_resolver_instance = None

def get_resolver() -> AbstractResolver:
    """Возвращает глобальный экземпляр резолвера."""
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = AbstractResolver()
    return _resolver_instance

def resolve_abstract_path(abstract_address: str) -> str:
    """
    Быстрая функция для разрешения abstract адреса.
    
    Args:
        abstract_address: Abstract адрес
        
    Returns:
        str: Физический путь
    """
    resolver = get_resolver()
    resolved = resolver.resolve(abstract_address)
    return resolved if resolved else abstract_address

def main():
    """Тестирование системы abstract адресов."""
    print("🎯 Тестирование системы abstract адресов...")
    
    resolver = AbstractResolver()
    
    # Тестируем разрешение основных адресов
    test_addresses = [
        "abstract://task:todo",
        "abstract://standard:task_master", 
        "abstract://incident:ai",
        "task:todo",
        "standard:ticket"
    ]
    
    print("\n✅ Тестирование разрешения адресов:")
    for address in test_addresses:
        resolved = resolver.resolve(address)
        print(f"  {address} → {resolved}")
    
    # Статистика
    stats = resolver.get_statistics()
    print(f"\n📊 Статистика abstract маппингов:")
    print(f"  Всего маппингов: {stats['total_mappings']}")
    print(f"  По типам: {stats['by_type']}")
    
    print(f"\n🎉 Система abstract адресов восстановлена!")

if __name__ == "__main__":
    main()