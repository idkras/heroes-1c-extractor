"""
Регистрация проекта heroes-gpt-bot в системе кеша с abstract адресацией.

Этот модуль обеспечивает:
1. Маппинг abstract:// адресов для компонентов heroes-gpt-bot
2. Регистрацию проекта как независимой сущности
3. Быстрый доступ к ключевым компонентам
"""

import os
from typing import Dict, List, Optional
from pathlib import Path


class HeroesGPTRegistry:
    """Регистр компонентов проекта heroes-gpt-bot с abstract адресацией."""
    
    def __init__(self):
        """Инициализация регистра."""
        self.project_root = "[heroes-gpt-bot]"
        self.abstract_mappings = self._create_abstract_mappings()
    
    def _create_abstract_mappings(self) -> Dict[str, str]:
        """Создает маппинг abstract:// адресов на физические пути."""
        return {
            # Основные компоненты
            "abstract://heroes-gpt-bot/main": f"{self.project_root}/index.html",
            "abstract://heroes-gpt-bot/api-client": f"{self.project_root}/api-client.html",
            "abstract://heroes-gpt-bot/reviews": f"{self.project_root}/reviews.html",
            "abstract://heroes-gpt-bot/welcome": f"{self.project_root}/welcome.html",
            
            # Templates и документация
            "abstract://heroes-gpt-bot/template/base": f"{self.project_root}/heroesGPT_review_template.md",
            "abstract://heroes-gpt-bot/template/v1.3": f"{self.project_root}/heroesGPT_review_template_v1.3.md",
            "abstract://heroes-gpt-bot/template/v1.4": f"{self.project_root}/heroesGPT_review_template_v1.4.md",
            "abstract://heroes-gpt-bot/docs/readme": f"{self.project_root}/README.md",
            "abstract://heroes-gpt-bot/docs/gdocs-export": f"{self.project_root}/README_GDOCS_EXPORT.md",
            "abstract://heroes-gpt-bot/docs/quality-checklist": f"{self.project_root}/чек-лист-качества-JTBD-анализа.md",
            
            # Review результаты
            "abstract://heroes-gpt-bot/reviews/ingosstrakh": f"{self.project_root}/review-result/ingosstrakh_osago_landing_analysis.md",
            "abstract://heroes-gpt-bot/reviews/directory": f"{self.project_root}/review-result",
            
            # Промпты архив
            "abstract://heroes-gpt-bot/prompts/v2": f"{self.project_root}/promts archive/heroes-gpt_bot-prompt-v2.md",
            "abstract://heroes-gpt-bot/prompts/base": f"{self.project_root}/promts archive/heroes-gpt_bot-prompt.md",
            "abstract://heroes-gpt-bot/prompts/updated": f"{self.project_root}/promts archive/heroesGPT_bot-prompt-updated.md",
            "abstract://heroes-gpt-bot/prompts/directory": f"{self.project_root}/promts archive",
            
            # Веб-компоненты
            "abstract://heroes-gpt-bot/web/styles": f"{self.project_root}/src/css/styles.css",
            "abstract://heroes-gpt-bot/web/app": f"{self.project_root}/src/js/app.js",
            "abstract://heroes-gpt-bot/web/markdown": f"{self.project_root}/src/js/marked.min.js",
            "abstract://heroes-gpt-bot/web/viewer": f"{self.project_root}/markdown-viewer.html",
            
            # Утилиты и API
            "abstract://heroes-gpt-bot/utils/web-links": f"{self.project_root}/add_web_links.py",
            "abstract://heroes-gpt-bot/utils/fix-links": f"{self.project_root}/fix_links.py",
            "abstract://heroes-gpt-bot/utils/test-availability": f"{self.project_root}/test_availability.py",
            "abstract://heroes-gpt-bot/api/gdocs-export": f"{self.project_root}/gdocs_export_api.py",
            "abstract://heroes-gpt-bot/api/simple-export": f"{self.project_root}/simple_gdocs_export.py",
            "abstract://heroes-gpt-bot/api/export-instructions": f"{self.project_root}/simple_gdocs_export_instructions.md",
        }
    
    def get_physical_path(self, abstract_path: str) -> Optional[str]:
        """Получает физический путь по abstract адресу."""
        return self.abstract_mappings.get(abstract_path)
    
    def get_abstract_path(self, physical_path: str) -> Optional[str]:
        """Получает abstract адрес по физическому пути."""
        for abstract, physical in self.abstract_mappings.items():
            if physical == physical_path or physical_path.endswith(physical.replace(f"{self.project_root}/", "")):
                return abstract
        return None
    
    def list_components(self, category: Optional[str] = None) -> List[str]:
        """Возвращает список компонентов по категории."""
        if not category:
            return list(self.abstract_mappings.keys())
        
        return [addr for addr in self.abstract_mappings.keys() 
                if f"/{category}/" in addr or addr.endswith(f"/{category}")]
    
    def get_project_metadata(self) -> Dict[str, any]:
        """Возвращает метаданные проекта для регистрации в кеше."""
        return {
            "project_id": "heroes-gpt-bot",
            "project_name": "HeroesGPT Landing Analytics Platform",
            "description": "Веб-платформа для анализа лендингов с помощью ИИ в стиле Medium.com",
            "type": "web_application",
            "technologies": ["HTML5", "CSS3", "JavaScript", "Markdown", "Python"],
            "components": {
                "web_interface": ["main", "api-client", "reviews", "welcome"],
                "templates": ["base", "v1.3", "v1.4"],
                "prompts": ["v2", "base", "updated"],
                "reviews": ["ingosstrakh", "directory"],
                "utilities": ["web-links", "fix-links", "test-availability"],
                "api": ["gdocs-export", "simple-export"]
            },
            "root_path": self.project_root,
            "abstract_base": "abstract://heroes-gpt-bot/",
            "created": "2025-05-23",
            "status": "active"
        }
    
    def validate_paths(self) -> Dict[str, bool]:
        """Проверяет существование всех зарегистрированных путей."""
        validation_results = {}
        
        for abstract_addr, physical_path in self.abstract_mappings.items():
            try:
                exists = os.path.exists(physical_path)
                validation_results[abstract_addr] = exists
                if not exists:
                    print(f"⚠️ Путь не найден: {abstract_addr} -> {physical_path}")
            except Exception as e:
                validation_results[abstract_addr] = False
                print(f"❌ Ошибка проверки {abstract_addr}: {e}")
        
        return validation_results


def register_heroes_gpt_project():
    """Регистрирует проект heroes-gpt-bot в системе кеша."""
    registry = HeroesGPTRegistry()
    
    print("🎯 Регистрирую проект heroes-gpt-bot...")
    
    # Проверяем пути
    validation = registry.validate_paths()
    valid_paths = sum(1 for v in validation.values() if v)
    total_paths = len(validation)
    
    print(f"✅ Валидных путей: {valid_paths}/{total_paths}")
    
    # Получаем метаданные
    metadata = registry.get_project_metadata()
    print(f"📊 Проект: {metadata['project_name']}")
    print(f"🔧 Технологии: {', '.join(metadata['technologies'])}")
    
    return registry, metadata


if __name__ == "__main__":
    registry, metadata = register_heroes_gpt_project()
    
    print("\n🗂️ Доступные компоненты:")
    for category in ["web_interface", "templates", "prompts", "reviews"]:
        components = registry.list_components(category)
        if components:
            print(f"  {category}: {len(components)} компонентов")