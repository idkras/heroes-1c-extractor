"""
Unified Key Resolver - единый резольвер ключей для кеша и тестов.

JTBD: Я (система) хочу иметь единый способ работы с любыми форматами путей,
чтобы устранить проблемы синхронизации кеша и обеспечить совместимость.

Поддерживаемые форматы ключей:
1. Логические: abstract://standard:registry_standard  
2. Относительные: ../[standards .md]/0. core/registry.md
3. Абсолютные: /home/runner/workspace/[standards .md]/0. core/registry.md
4. Канонические: [standards .md]/0. core/registry.md

Разработано через TDD стандарт v2.0 для решения проблемы 0% синхронизации кеша.

Автор: AI Assistant
Дата: 26 May 2025
"""

import os
import re
from typing import Dict, List, Optional, Set
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UnifiedKeyResolver:
    """
    JTBD: Я (резольвер) хочу преобразовывать любые форматы путей в единый канонический,
    чтобы кеш и тесты использовали одинаковые ключи для поиска файлов.
    
    Единый резольвер ключей для всех компонентов системы.
    Устраняет проблему 0% синхронизации между кешем и тестами.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        JTBD: Я (резольвер) хочу инициализироваться с корректным корнем проекта,
        чтобы правильно преобразовывать относительные и абсолютные пути.
        """
        if project_root is None:
            # Определяем корень проекта автоматически
            current_file = Path(__file__).resolve()
            # Поднимаемся до папки, содержащей [standards .md]
            for parent in current_file.parents:
                if (parent / "[standards .md]").exists():
                    project_root = str(parent)
                    break
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.standards_root = self.project_root / "[standards .md]"
        self.todo_root = self.project_root / "[todo · incidents]"
        
        # Кеш для логических адресов
        self._logical_map: Dict[str, str] = {}
        self._build_logical_map()
        
        logger.info(f"UnifiedKeyResolver инициализирован с корнем: {self.project_root}")
    
    def _build_logical_map(self):
        """
        JTBD: Я (резольвер) хочу построить карту логических адресов,
        чтобы быстро находить файлы по abstract:// ссылкам.
        
        Строит карту соответствий логических адресов физическим путям.
        """
        if not self.standards_root.exists():
            logger.warning(f"Папка стандартов не найдена: {self.standards_root}")
            return
        
        # Сканируем все стандарты и строим карту
        for root, dirs, files in os.walk(self.standards_root):
            # Фильтруем архивные папки
            dirs[:] = [d for d in dirs if not self._is_archive_folder(d)]
            
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    logical_id = self._extract_logical_id(file_path)
                    if logical_id:
                        canonical_path = self._to_canonical(str(file_path))
                        self._logical_map[f"abstract://standard:{logical_id}"] = canonical_path
                        logger.debug(f"Mapped: abstract://standard:{logical_id} → {canonical_path}")
    
    def _is_archive_folder(self, folder_name: str) -> bool:
        """Проверяет, является ли папка архивной."""
        archive_patterns = [
            '[archive]', 'archive', 'backup', '20250', 'old', 
            'deprecated', 'consolidated', 'rename', 'template'
        ]
        return any(pattern in folder_name.lower() for pattern in archive_patterns)
    
    def _extract_logical_id(self, file_path: Path) -> Optional[str]:
        """
        JTBD: Я (экстрактор) хочу извлечь логический ID из имени файла,
        чтобы создать abstract:// адрес для стандарта.
        
        Извлекает логический идентификатор из имени файла стандарта.
        """
        filename = file_path.stem.lower()
        
        # Паттерны для извлечения ID стандартов
        patterns = [
            r'(\w+)\s+standard',  # "registry standard" → "registry"
            r'(\w+)[-_]standard',  # "task-standard" → "task"  
            r'^(\w+)\s',          # "registry ..." → "registry"
            r'(\w+)$'             # последнее слово
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                logical_id = match.group(1).replace(' ', '_')
                # Исключаем общие слова
                if logical_id not in ['by', 'ai', 'assistant', 'may', 'cet', 'the', 'and', 'of']:
                    return logical_id
        
        return None
    
    def normalize_key(self, any_key: str) -> str:
        """
        JTBD: Я (нормализатор) хочу привести любой ключ к канонической форме,
        чтобы все компоненты системы использовали одинаковые ключи.
        
        Приводит любой ключ к канонической форме для кеша.
        """
        if not any_key:
            return ""
        
        # 1. Логический адрес
        if any_key.startswith("abstract://"):
            return self.resolve_to_canonical(any_key)
        
        # 2. Абсолютный путь
        if os.path.isabs(any_key):
            return self._to_canonical(any_key)
        
        # 3. Относительный путь
        if any_key.startswith("../"):
            abs_path = str((self.project_root / "advising_platform" / any_key).resolve())
            return self._to_canonical(abs_path)
        
        # 4. Уже канонический
        return any_key
    
    def _to_canonical(self, file_path: str) -> str:
        """
        JTBD: Я (конвертер) хочу преобразовать любой путь в канонический формат,
        чтобы обеспечить единообразие ключей в системе.
        
        Преобразует путь в канонический формат относительно корня проекта.
        """
        try:
            abs_path = Path(file_path).resolve()
            rel_path = abs_path.relative_to(self.project_root)
            return str(rel_path).replace('\\', '/')
        except ValueError:
            # Путь вне корня проекта
            return str(Path(file_path).resolve()).replace('\\', '/')
    
    def resolve_to_canonical(self, logical_key: str) -> str:
        """
        JTBD: Я (резольвер) хочу преобразовать логический адрес в канонический путь,
        чтобы найти физический файл по abstract:// ссылке.
        
        Преобразует логический адрес в канонический путь.
        """
        if logical_key in self._logical_map:
            return self._logical_map[logical_key]
        
        logger.warning(f"Логический адрес не найден: {logical_key}")
        return logical_key
    
    def resolve_to_physical(self, logical_key: str) -> str:
        """
        JTBD: Я (резольвер) хочу получить абсолютный физический путь по логическому адресу,
        чтобы можно было читать файл с диска.
        
        Преобразует логический адрес в абсолютный физический путь.
        """
        canonical = self.resolve_to_canonical(logical_key)
        if canonical == logical_key:  # Не найден
            return ""
        
        return str(self.project_root / canonical)
    
    def get_all_aliases(self, canonical_key: str) -> List[str]:
        """
        JTBD: Я (генератор алиасов) хочу создать все возможные варианты ключа,
        чтобы тесты могли найти файл независимо от формата поиска.
        
        Возвращает все возможные алиасы для канонического ключа.
        """
        aliases = [canonical_key]
        
        # Добавляем абсолютный путь
        abs_path = str(self.project_root / canonical_key)
        aliases.append(abs_path)
        
        # Добавляем относительный путь для кеша
        if canonical_key.startswith("[standards .md]"):
            rel_path = "../" + canonical_key
            aliases.append(rel_path)
        
        # Добавляем только имя файла
        filename = Path(canonical_key).name
        aliases.append(filename)
        
        # Добавляем логический адрес, если есть
        for logical, canonical in self._logical_map.items():
            if canonical == canonical_key:
                aliases.append(logical)
                break
        
        return list(set(aliases))  # Убираем дубликаты
    
    def find_by_any_key(self, search_key: str, available_keys: List[str]) -> Optional[str]:
        """
        JTBD: Я (поисковик) хочу найти файл в списке по любому формату ключа,
        чтобы тесты могли находить файлы независимо от формата хранения в кеше.
        
        Ищет ключ в списке доступных ключей, используя все возможные алиасы.
        """
        canonical = self.normalize_key(search_key)
        aliases = self.get_all_aliases(canonical)
        
        # Ищем прямое совпадение
        for alias in aliases:
            if alias in available_keys:
                return alias
        
        # Ищем частичное совпадение по имени файла
        search_filename = Path(search_key).name
        for key in available_keys:
            if Path(key).name == search_filename:
                return key
        
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """
        JTBD: Я (статистика) хочу предоставить информацию о состоянии резольвера,
        чтобы можно было мониторить корректность работы системы.
        
        Возвращает статистику работы резольвера.
        """
        return {
            'logical_mappings': len(self._logical_map),
            'project_root_exists': self.project_root.exists(),
            'standards_root_exists': self.standards_root.exists(),
            'todo_root_exists': self.todo_root.exists()
        }


# Глобальный экземпляр резольвера
_resolver_instance = None

def get_resolver() -> UnifiedKeyResolver:
    """
    JTBD: Я (фабрика) хочу предоставить единый глобальный экземпляр резольвера,
    чтобы все компоненты системы использовали одну и ту же конфигурацию.
    
    Возвращает глобальный экземпляр UnifiedKeyResolver.
    """
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = UnifiedKeyResolver()
    return _resolver_instance