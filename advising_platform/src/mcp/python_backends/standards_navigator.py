#!/usr/bin/env python3
"""
Standards Navigator Backend

JTBD: Я (navigator) хочу предоставить продвинутый поиск и навигацию по стандартам,
чтобы AI Assistant мог быстро находить нужную документацию и связанные стандарты.

Интеграция с поиском, фильтрацией и анализом связей между стандартами.

Автор: AI Assistant
Дата: 26 May 2025
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Set

# Добавляем путь к модулям advising_platform
current_dir = Path(__file__).parent.resolve()
advising_platform_dir = current_dir.parent.parent
sys.path.insert(0, str(advising_platform_dir))

# Динамический импорт для лучшей совместимости
try:
    from advising_platform.src.core.unified_key_resolver import get_resolver
    from advising_platform.src.cache.real_inmemory_cache import get_cache
# Direct import
    project_root = current_dir.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from advising_platform.src.core.unified_key_resolver import get_resolver
    from advising_platform.src.cache.real_inmemory_cache import get_cache

class StandardsNavigator:
    """
    JTBD: Я (класс) хочу обеспечить продвинутую навигацию по стандартам,
    чтобы предоставить мощные возможности поиска, фильтрации и обнаружения связей.
    """
    
    def __init__(self):
        self.resolver = get_resolver()
        self.cache = get_cache()
        
        # Инициализируем кеш если не загружен
        if len(self.cache.get_all_paths()) == 0:
            self.cache.initialize_from_disk()
        
        # Категории стандартов для фильтрации
        self.categories = {
            "core": ["основной", "базовый", "core", "fundamental", "ключевой"],
            "process": ["процесс", "workflow", "алгоритм", "методология", "подход"],
            "development": ["разработка", "development", "код", "программирование", "implementation"],
            "quality": ["качество", "quality", "тестирование", "валидация", "проверка"],
            "design": ["дизайн", "design", "архитектура", "проектирование", "ui", "ux"]
        }
    
    def navigate_standards(self, query: str = None, category: str = None, related_to: str = None, include_archived: bool = False) -> Dict[str, Any]:
        """
        JTBD: Я (метод) хочу предоставить комплексную навигацию по стандартам,
        чтобы вернуть отфильтрованные и релевантные результаты поиска.
        """
        try:
            # 1. Получаем все доступные стандарты
            all_standards = self._get_all_standards_info(include_archived)
            
            # 2. Применяем фильтры
            filtered_standards = all_standards
            
            if category:
                filtered_standards = self._filter_by_category(filtered_standards, category)
            
            if query:
                filtered_standards = self._search_by_query(filtered_standards, query)
            
            if related_to:
                filtered_standards = self._find_related_standards(filtered_standards, related_to)
            
            # 3. Ранжируем результаты
            ranked_results = self._rank_search_results(filtered_standards, query)
            
            # 4. Обогащаем результаты дополнительной информацией
            enriched_results = self._enrich_results(ranked_results)
            
            # 5. Анализируем связи между стандартами
            connections = self._analyze_connections(enriched_results)
            
            return {
                "success": True,
                "query": query,
                "category": category,
                "related_to": related_to,
                "include_archived": include_archived,
                "total_found": len(enriched_results),
                "results": enriched_results,
                "connections": connections,
                "search_metadata": {
                    "categories_available": list(self.categories.keys()),
                    "total_standards": len(all_standards),
                    "search_time": "fast"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Navigation failed: {str(e)}",
                "query": query
            }
    
    def _get_all_standards_info(self, include_archived: bool) -> List[Dict[str, Any]]:
        """Получает информацию о всех доступных стандартах."""
        standards_info = []
        
        # Получаем все логические адреса
        available_addresses = list(self.resolver._logical_map.keys())
        
        for address in available_addresses:
            standard_info = self._extract_standard_metadata(address)
            
            # Фильтруем архивные если не нужны
            if not include_archived and standard_info.get("status") == "archived":
                continue
                
            standards_info.append(standard_info)
        
        return standards_info
    
    def _extract_standard_metadata(self, address: str) -> Dict[str, Any]:
        """Извлекает метаданные стандарта."""
        canonical_path = self.resolver.resolve_to_canonical(address)
        cache_entry = self.cache.get_document(canonical_path)
        
        if not cache_entry:
            return {
                "address": address,
                "title": address.split(":")[-1],
                "description": "Метаданные недоступны",
                "category": "unknown",
                "status": "unknown",
                "tags": [],
                "dependencies": [],
                "last_updated": None,
                "size": 0
            }
        
        content = cache_entry.content
        lines = content.split('\n')
        
        # Извлекаем основные метаданные
        metadata = {
            "address": address,
            "canonical_path": canonical_path,
            "title": self._extract_title(lines),
            "description": self._extract_description(lines),
            "category": self._determine_category(content),
            "status": self._extract_status(lines),
            "tags": self._extract_tags(content),
            "dependencies": self._extract_dependencies(content),
            "last_updated": cache_entry.modified_time,
            "size": cache_entry.size,
            "author": self._extract_author(lines),
            "version": self._extract_version(lines)
        }
        
        return metadata
    
    def _extract_title(self, lines: List[str]) -> str:
        """Извлекает заголовок стандарта."""
        for line in lines[:15]:
            if line.startswith('#') and len(line.strip()) > 3:
                return line.strip('# ').strip()
        return "Без названия"
    
    def _extract_description(self, lines: List[str]) -> str:
        """Извлекает описание стандарта."""
        description_markers = ["описание", "description", "цель", "jtbd", "goal"]
        
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in description_markers):
                # Собираем следующие строки как описание
                desc_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        desc_lines.append(lines[j].strip())
                    elif desc_lines:
                        break
                
                if desc_lines:
                    description = ' '.join(desc_lines)
                    return description[:300] + "..." if len(description) > 300 else description
        
        return "Описание недоступно"
    
    def _determine_category(self, content: str) -> str:
        """Определяет категорию стандарта по содержимому."""
        content_lower = content.lower()
        
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            category_scores[category] = score
        
        if not category_scores or max(category_scores.values()) == 0:
            return "general"
        
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def _extract_status(self, lines: List[str]) -> str:
        """Извлекает статус стандарта."""
        status_markers = ["статус", "status", "состояние"]
        
        for line in lines:
            line_lower = line.lower()
            if any(marker in line_lower for marker in status_markers):
                if "архив" in line_lower or "archived" in line_lower:
                    return "archived"
                elif "черновик" in line_lower or "draft" in line_lower:
                    return "draft"
                elif "активный" in line_lower or "active" in line_lower:
                    return "active"
        
        return "active"  # По умолчанию
    
    def _extract_tags(self, content: str) -> List[str]:
        """Извлекает теги из содержимого."""
        tags = set()
        content_lower = content.lower()
        
        # Ищем явные теги
        tag_patterns = [
            r"теги?[:\s]+([^\n]+)",
            r"tags?[:\s]+([^\n]+)",
            r"ключевые слова[:\s]+([^\n]+)"
        ]
        
        for pattern in tag_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                tag_words = re.findall(r'\w+', match)
                tags.update(tag_words)
        
        # Автоматически определяем теги из контента
        auto_tags = self._auto_detect_tags(content)
        tags.update(auto_tags)
        
        return sorted(list(tags))[:10]  # Максимум 10 тегов
    
    def _auto_detect_tags(self, content: str) -> Set[str]:
        """Автоматически определяет теги из содержимого."""
        tags = set()
        content_lower = content.lower()
        
        # Технические термины
        tech_terms = ["api", "database", "frontend", "backend", "ui", "ux", "tdd", "jtbd"]
        for term in tech_terms:
            if term in content_lower:
                tags.add(term)
        
        # Процессы
        process_terms = ["workflow", "process", "automation", "integration"]
        for term in process_terms:
            if term in content_lower:
                tags.add(term)
        
        return tags
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Извлекает зависимости от других стандартов."""
        dependencies = []
        
        # Ищем ссылки на другие стандарты
        standard_refs = re.findall(r'abstract://standard:([a-z_]+)', content)
        dependencies.extend([f"abstract://standard:{ref}" for ref in standard_refs])
        
        # Ищем упоминания стандартов в тексте
        dependency_patterns = [
            r"основан на\s+([^\n]+)",
            r"использует\s+([^\n]+)",
            r"зависит от\s+([^\n]+)",
            r"based on\s+([^\n]+)"
        ]
        
        for pattern in dependency_patterns:
            matches = re.findall(pattern, content.lower())
            dependencies.extend(matches)
        
        return dependencies[:5]  # Максимум 5 зависимостей
    
    def _extract_author(self, lines: List[str]) -> str:
        """Извлекает автора стандарта."""
        for line in lines[:20]:
            line_lower = line.lower()
            if "автор" in line_lower or "author" in line_lower:
                author_match = re.search(r"автор[:\s]+([^\n,]+)", line_lower)
                if not author_match:
                    author_match = re.search(r"author[:\s]+([^\n,]+)", line_lower)
                if author_match:
                    return author_match.group(1).strip()
        return "Неизвестен"
    
    def _extract_version(self, lines: List[str]) -> str:
        """Извлекает версию стандарта."""
        for line in lines[:20]:
            version_match = re.search(r"v(\d+\.\d+)", line.lower())
            if version_match:
                return version_match.group(1)
        return "1.0"
    
    def _filter_by_category(self, standards: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Фильтрует стандарты по категории."""
        return [std for std in standards if std["category"] == category]
    
    def _search_by_query(self, standards: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Ищет стандарты по текстовому запросу."""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        results = []
        for standard in standards:
            # Проверяем соответствие в разных полях
            matches = 0
            searchable_text = (
                standard["title"] + " " +
                standard["description"] + " " +
                " ".join(standard["tags"])
            ).lower()
            
            for word in query_words:
                if word in searchable_text:
                    matches += 1
            
            if matches > 0:
                standard["search_score"] = matches / len(query_words)
                results.append(standard)
        
        return results
    
    def _find_related_standards(self, standards: List[Dict[str, Any]], related_to: str) -> List[Dict[str, Any]]:
        """Находит стандарты, связанные с указанным."""
        # Получаем информацию о базовом стандарте
        base_standard = None
        for std in standards:
            if related_to in std["address"] or related_to in std["title"].lower():
                base_standard = std
                break
        
        if not base_standard:
            return standards
        
        # Ищем связанные стандарты
        related_results = []
        base_category = base_standard["category"]
        base_tags = set(base_standard["tags"])
        
        for standard in standards:
            if standard["address"] == base_standard["address"]:
                continue
            
            # Вычисляем связанность
            relation_score = 0
            
            # По категории
            if standard["category"] == base_category:
                relation_score += 0.3
            
            # По тегам
            common_tags = base_tags.intersection(set(standard["tags"]))
            if common_tags:
                relation_score += len(common_tags) * 0.2
            
            # По зависимостям
            if any(dep in standard["dependencies"] for dep in [base_standard["address"]]):
                relation_score += 0.5
            
            if relation_score > 0.1:
                standard["relation_score"] = relation_score
                related_results.append(standard)
        
        return related_results
    
    def _rank_search_results(self, standards: List[Dict[str, Any]], query: str = None) -> List[Dict[str, Any]]:
        """Ранжирует результаты поиска по релевантности."""
        if not query:
            # Сортируем по размеру и дате обновления
            return sorted(standards, key=lambda x: (x["size"], x.get("last_updated", 0)), reverse=True)
        
        # Сортируем по поисковому скору
        return sorted(standards, key=lambda x: x.get("search_score", 0), reverse=True)
    
    def _enrich_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обогащает результаты дополнительной информацией."""
        for result in results:
            # Добавляем информацию о применимости
            result["use_cases"] = self._extract_use_cases(result)
            
            # Добавляем метрики качества
            result["quality_score"] = self._calculate_quality_score(result)
            
            # Добавляем рекомендации по использованию
            result["recommendations"] = self._generate_usage_recommendations(result)
        
        return results
    
    def _extract_use_cases(self, standard: Dict[str, Any]) -> List[str]:
        """Извлекает случаи использования стандарта."""
        use_cases = []
        
        # На основе категории
        category_use_cases = {
            "development": ["Разработка компонентов", "Code review", "Архитектурные решения"],
            "quality": ["Тестирование", "Валидация", "Контроль качества"],
            "process": ["Оптимизация процессов", "Автоматизация", "Стандартизация"],
            "design": ["Проектирование интерфейсов", "UX исследования", "Прототипирование"]
        }
        
        category = standard["category"]
        if category in category_use_cases:
            use_cases.extend(category_use_cases[category])
        
        return use_cases[:3]  # Топ 3 случая использования
    
    def _calculate_quality_score(self, standard: Dict[str, Any]) -> float:
        """Вычисляет оценку качества стандарта."""
        score = 0.0
        
        # Полнота описания
        if len(standard["description"]) > 100:
            score += 0.3
        
        # Наличие тегов
        if len(standard["tags"]) > 3:
            score += 0.2
        
        # Размер документа
        if standard["size"] > 1000:
            score += 0.2
        
        # Наличие автора
        if standard["author"] != "Неизвестен":
            score += 0.1
        
        # Активный статус
        if standard["status"] == "active":
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_usage_recommendations(self, standard: Dict[str, Any]) -> List[str]:
        """Генерирует рекомендации по использованию стандарта."""
        recommendations = []
        
        if standard["category"] == "development":
            recommendations.append("Рекомендуется для технических проектов")
        
        if standard["quality_score"] > 0.7:
            recommendations.append("Высокое качество документации")
        
        if len(standard["dependencies"]) > 0:
            recommendations.append("Требует изучения связанных стандартов")
        
        return recommendations
    
    def _analyze_connections(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализирует связи между найденными стандартами."""
        if len(results) < 2:
            return {"total_connections": 0, "connection_types": []}
        
        connections = {
            "total_connections": 0,
            "connection_types": [],
            "clusters": []
        }
        
        # Группируем по категориям
        category_groups = {}
        for result in results:
            category = result["category"]
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(result["address"])
        
        # Анализируем кластеры
        for category, addresses in category_groups.items():
            if len(addresses) > 1:
                connections["clusters"].append({
                    "type": "category",
                    "category": category,
                    "members": addresses,
                    "size": len(addresses)
                })
        
        connections["total_connections"] = sum(cluster["size"] for cluster in connections["clusters"])
        
        return connections


def main():
    """Основная функция для вызова из MCP сервера."""
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python standards_navigator.py <json_args>")
        
        args = json.loads(sys.argv[1])
        
        navigator = StandardsNavigator()
        result = navigator.navigate_standards(
            query=args.get("query"),
            category=args.get("category"),
            related_to=args.get("relatedTo"),
            include_archived=args.get("includeArchived", False)
        )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Script execution failed: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()