"""
Интеграция проекта heroes-gpt-bot в RealInMemoryCache как отдельной сущности.

Этот модуль обеспечивает:
1. Регистрацию heroes-gpt-bot в кеш-системе
2. Быстрый доступ к компонентам через abstract:// адреса
3. Автоматическое обновление кеша при изменениях
"""

import os
import logging
from typing import Dict, List, Optional
from .real_inmemory_cache import RealInMemoryCache
from .heroes_gpt_registry import HeroesGPTRegistry

logger = logging.getLogger(__name__)


class HeroesGPTCacheIntegration:
    """Интеграция heroes-gpt-bot в кеш-систему."""
    
    def __init__(self, cache: RealInMemoryCache):
        """Инициализация интеграции."""
        self.cache = cache
        self.registry = HeroesGPTRegistry()
        self.project_metadata = self.registry.get_project_metadata()
    
    def register_project_in_cache(self) -> bool:
        """Регистрирует весь проект heroes-gpt-bot в кеше."""
        try:
            logger.info("🎯 Регистрирую heroes-gpt-bot в кеш-системе...")
            
            # Добавляем все компоненты проекта в кеш
            registered_count = 0
            total_count = len(self.registry.abstract_mappings)
            
            for abstract_addr, physical_path in self.registry.abstract_mappings.items():
                if os.path.exists(physical_path):
                    success = self.cache.add_file(physical_path)
                    if success:
                        registered_count += 1
                        logger.debug(f"✅ Зарегистрирован: {abstract_addr}")
                    else:
                        logger.warning(f"⚠️ Не удалось зарегистрировать: {abstract_addr}")
                else:
                    logger.warning(f"❌ Файл не найден: {physical_path}")
            
            # Добавляем метаданные проекта в кеш
            self._add_project_metadata()
            
            logger.info(f"✅ Зарегистрировано {registered_count}/{total_count} компонентов heroes-gpt-bot")
            return registered_count > 0
            
        except Exception as e:
            logger.error(f"❌ Ошибка регистрации heroes-gpt-bot: {e}")
            return False
    
    def _add_project_metadata(self):
        """Добавляет метаданные проекта в кеш."""
        metadata_content = f"""# Heroes-GPT Bot Project Metadata

Project ID: {self.project_metadata['project_id']}
Name: {self.project_metadata['project_name']}
Description: {self.project_metadata['description']}
Type: {self.project_metadata['type']}
Technologies: {', '.join(self.project_metadata['technologies'])}
Status: {self.project_metadata['status']}
Created: {self.project_metadata['created']}

## Components:
"""
        
        for category, components in self.project_metadata['components'].items():
            metadata_content += f"\n### {category.title()}:\n"
            for component in components:
                abstract_addr = f"abstract://heroes-gpt-bot/{category.replace('_', '/')}/{component}"
                if abstract_addr in self.registry.abstract_mappings:
                    physical_path = self.registry.abstract_mappings[abstract_addr]
                    metadata_content += f"- {component}: {abstract_addr} -> {physical_path}\n"
        
        # Добавляем метаданные как виртуальный файл в кеш
        metadata_path = "[heroes-gpt-bot]/.project_metadata.md"
        self.cache._add_to_cache(metadata_path, metadata_content, "project_metadata")
    
    def get_component_by_abstract_address(self, abstract_addr: str) -> Optional[str]:
        """Получает содержимое компонента по abstract адресу."""
        physical_path = self.registry.get_physical_path(abstract_addr)
        if not physical_path:
            return None
        
        entry = self.cache.get_document(physical_path)
        return entry.content if entry else None
    
    def list_project_components(self, category: Optional[str] = None) -> List[str]:
        """Возвращает список компонентов проекта по категории."""
        return self.registry.list_components(category)
    
    def search_in_project(self, query: str) -> List[Dict[str, str]]:
        """Ищет в компонентах heroes-gpt-bot проекта."""
        results = []
        
        for abstract_addr, physical_path in self.registry.abstract_mappings.items():
            entry = self.cache.get_document(physical_path)
            if entry and query.lower() in entry.content.lower():
                results.append({
                    'abstract_address': abstract_addr,
                    'physical_path': physical_path,
                    'doc_type': entry.doc_type,
                    'size': entry.size
                })
        
        return results
    
    def refresh_project_cache(self) -> Dict[str, bool]:
        """Обновляет кеш всех компонентов проекта."""
        results = {}
        
        for abstract_addr, physical_path in self.registry.abstract_mappings.items():
            try:
                refreshed = self.cache.refresh_file(physical_path)
                results[abstract_addr] = refreshed
            except Exception as e:
                logger.error(f"Ошибка обновления {abstract_addr}: {e}")
                results[abstract_addr] = False
        
        return results
    
    def get_project_statistics(self) -> Dict[str, any]:
        """Возвращает статистику проекта в кеше."""
        stats = {
            'total_components': len(self.registry.abstract_mappings),
            'cached_components': 0,
            'total_size_bytes': 0,
            'components_by_type': {},
            'abstract_addresses': list(self.registry.abstract_mappings.keys())
        }
        
        for physical_path in self.registry.abstract_mappings.values():
            entry = self.cache.get_document(physical_path)
            if entry:
                stats['cached_components'] += 1
                stats['total_size_bytes'] += entry.size
                
                doc_type = entry.doc_type
                if doc_type not in stats['components_by_type']:
                    stats['components_by_type'][doc_type] = 0
                stats['components_by_type'][doc_type] += 1
        
        return stats


def integrate_heroes_gpt_bot(cache: RealInMemoryCache) -> HeroesGPTCacheIntegration:
    """
    Интегрирует проект heroes-gpt-bot в кеш-систему.
    
    Args:
        cache: Экземпляр RealInMemoryCache
        
    Returns:
        HeroesGPTCacheIntegration: Объект интеграции
    """
    integration = HeroesGPTCacheIntegration(cache)
    
    # Регистрируем проект
    success = integration.register_project_in_cache()
    
    if success:
        logger.info("🎉 Heroes-GPT Bot успешно интегрирован в кеш-систему!")
        
        # Выводим статистику
        stats = integration.get_project_statistics()
        logger.info(f"📊 Статистика: {stats['cached_components']}/{stats['total_components']} компонентов в кеше")
        logger.info(f"💾 Размер: {stats['total_size_bytes']} байт")
        
    else:
        logger.error("❌ Не удалось интегрировать Heroes-GPT Bot в кеш-систему")
    
    return integration


if __name__ == "__main__":
    # Демо интеграции
    cache = RealInMemoryCache()
    integration = integrate_heroes_gpt_bot(cache)
    
    # Тестируем поиск
    print("\n🔍 Тест поиска:")
    results = integration.search_in_project("landing")
    for result in results[:3]:  # Первые 3 результата
        print(f"  📄 {result['abstract_address']}")