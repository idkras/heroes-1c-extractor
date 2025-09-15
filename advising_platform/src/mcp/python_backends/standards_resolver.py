#!/usr/bin/env python3
"""
Standards Resolver Backend

JTBD: Я (resolver) хочу преобразовать логические адреса стандартов в актуальный контент,
чтобы AI Assistant получал правильную информацию для применения методологий.

Интеграция с UnifiedKeyResolver и RealInMemoryCache для максимальной производительности.

Автор: AI Assistant  
Дата: 26 May 2025
"""

import sys
import json
import os
from pathlib import Path

# Добавляем путь к модулям advising_platform
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent.parent  # Поднимаемся до корня проекта
sys.path.insert(0, str(project_root))

# Импортируем модули напрямую
from src.standards_system import UnifiedStandardsSystem

class StandardsResolver:
    """
    JTBD: Я (класс) хочу резолвить логические адреса стандартов,
    чтобы предоставить структурированный контент по запросу MCP клиента.
    """
    
    def __init__(self):
        """Инициализация резолвера с DuckDB системой"""
        self.standards_system = UnifiedStandardsSystem()
        self.operation_log = []
    
    def resolve_standard(self, address: str, format_type: str = "full", context: str = None) -> dict:
        """
        JTBD: Я (метод) хочу резолвить адрес стандарта в контент,
        чтобы вернуть структурированную информацию в нужном формате.
        """
        try:
            # Используем DuckDB систему для поиска стандарта
            if self.standards_system and self.standards_system.conn:
                result = self.standards_system._execute_safe(
                    "SELECT * FROM standards WHERE name LIKE ? OR path LIKE ? OR content LIKE ? LIMIT 1",
                    [f"%{address}%", f"%{address}%", f"%{address}%"]
                )
                
                if result:
                    row = result.fetchone()
                    if row:
                        columns = [desc[0] for desc in result.description] if result.description else []
                        standard_data = dict(zip(columns, row))
                        
                        return {
                            "success": True,
                            "address": address,
                            "standard": {
                                "name": standard_data.get('name', 'Unknown'),
                                "path": standard_data.get('path', ''),
                                "category": standard_data.get('category', ''),
                                "content": standard_data.get('content', '')[:500] + "..." if len(standard_data.get('content', '')) > 500 else standard_data.get('content', ''),
                                "metadata": {
                                    "version": standard_data.get('version', ''),
                                    "author": standard_data.get('author', ''),
                                    "complexity_score": standard_data.get('complexity_score', 0)
                                }
                            },
                            "format": format_type
                        }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Resolution failed: {str(e)}",
                "address": address
            }
    
    def _format_content(self, content: str, format_type: str, context: str, metadata: dict) -> dict:
        """
        JTBD: Я (форматер) хочу преобразовать контент в нужный формат,
        чтобы AI Assistant получил информацию в удобном виде.
        """
        result = {
            "raw": content if format_type == "full" else None
        }
        
        if format_type == "summary":
            result["summary"] = self._extract_summary(content)
            result["key_points"] = self._extract_key_points(content)
            result["jtbd_scenarios"] = self._extract_jtbd_scenarios(content)
            
        elif format_type == "checklist":
            result["checklist"] = self._extract_checklist(content)
            result["requirements"] = self._extract_requirements(content)
            result["validation_criteria"] = self._extract_validation_criteria(content)
            
        elif format_type == "full":
            result["summary"] = self._extract_summary(content)
            result["key_points"] = self._extract_key_points(content)
            result["jtbd_scenarios"] = self._extract_jtbd_scenarios(content)
            result["checklist"] = self._extract_checklist(content)
            result["requirements"] = self._extract_requirements(content)
            
        # Применяем контекстную фильтрацию если указан контекст
        if context:
            result = self._apply_context_filter(result, context)
            
        return result
    
    def _extract_summary(self, content: str) -> str:
        """Извлекает краткое описание стандарта."""
        lines = content.split('\n')
        
        # Ищем цель документа или описание
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in ['цель документа', 'описание', 'jtbd']):
                # Берем следующие 3-5 строк как описание
                summary_lines = []
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        summary_lines.append(lines[j].strip())
                    elif summary_lines:  # Прерываем если уже есть контент и встретили пустую строку
                        break
                return ' '.join(summary_lines)
        
        
        for line in lines[:10]:
            if line.strip() and not line.startswith('#') and len(line.strip()) > 50:
                return line.strip()
                
        return "Краткое описание недоступно"
    
    def _extract_key_points(self, content: str) -> list:
        """Извлекает ключевые пункты из стандарта."""
        key_points = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Ищем списки и важные пункты
            if (line.startswith('- ') or line.startswith('* ') or 
                line.startswith('✅') or line.startswith('❌') or
                '**' in line):
                clean_line = line.lstrip('- *✅❌ ').strip()
                if len(clean_line) > 10:  # Фильтруем слишком короткие
                    key_points.append(clean_line)
        
        return key_points[:10]  # Топ 10 пунктов
    
    def _extract_jtbd_scenarios(self, content: str) -> list:
        """Извлекает JTBD сценарии из стандарта."""
        scenarios = []
        lines = content.split('\n')
        
        current_scenario = {}
        in_jtbd_section = False
        
        for line in lines:
            line = line.strip()
            
            if 'jtbd' in line.lower() and ('сценари' in line.lower() or 'scenario' in line.lower()):
                in_jtbd_section = True
                continue
                
            if in_jtbd_section:
                if line.startswith('**Когда**'):
                    if current_scenario:
                        scenarios.append(current_scenario)
                    current_scenario = {"when": line.replace('**Когда**', '').strip()}
                elif line.startswith('**Роль**'):
                    current_scenario["role"] = line.replace('**Роль**', '').strip()
                elif line.startswith('**Хочет**'):
                    current_scenario["wants"] = line.replace('**Хочет**', '').strip()
                elif line.startswith('**Создаёт**'):
                    current_scenario["creates"] = line.replace('**Создаёт**', '').strip()
                    scenarios.append(current_scenario)
                    current_scenario = {}
                elif line.startswith('#') and scenarios:
                    break  # Закончилась секция JTBD
        
        return scenarios
    
    def _extract_checklist(self, content: str) -> list:
        """Извлекает чек-листы из стандарта."""
        checklist = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Ищем чек-боксы
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                item = line.replace('- [ ]', '').replace('- [x]', '').strip()
                if len(item) > 5:
                    checklist.append({
                        "item": item,
                        "completed": '[x]' in line
                    })
        
        return checklist
    
    def _extract_requirements(self, content: str) -> list:
        """Извлекает требования из стандарта."""
        requirements = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(marker in line.lower() for marker in [
                'требование', 'обязательно', 'должен', 'необходимо',
                'requirement', 'must', 'shall', 'required'
            ]):
                if len(line) > 15:
                    requirements.append(line)
        
        return requirements[:15]  # Топ 15 требований
    
    def _extract_validation_criteria(self, content: str) -> list:
        """Извлекает критерии валидации."""
        criteria = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(marker in line.lower() for marker in [
                'критерий', 'проверка', 'валидация', 'тест',
                'criteria', 'validation', 'check', 'test'
            ]):
                if len(line) > 10:
                    criteria.append(line)
        
        return criteria[:10]
    
    def _apply_context_filter(self, result: dict, context: str) -> dict:
        """Применяет контекстную фильтрацию к результату."""
        context_lower = context.lower()
        
        # Фильтруем ключевые пункты по контексту
        if "key_points" in result:
            filtered_points = []
            for point in result["key_points"]:
                if any(word in point.lower() for word in context_lower.split()):
                    filtered_points.append(point)
            result["key_points"] = filtered_points
        
        # Добавляем контекстную релевантность
        result["context_relevance"] = self._calculate_relevance(result, context)
        
        return result
    
    def _calculate_relevance(self, result: dict, context: str) -> float:
        """Вычисляет релевантность контента к контексту."""
        context_words = set(context.lower().split())
        content_text = str(result).lower()
        
        matches = sum(1 for word in context_words if word in content_text)
        return min(matches / len(context_words), 1.0) if context_words else 0.0
    
    def _get_similar_standards(self, address: str) -> list:
        """Предлагает похожие стандарты при ошибке поиска."""
        search_term = address.replace("abstract://standard:", "").replace("_", " ")
        
        available_standards = []
        for logical_addr, canonical in self.resolver._logical_map.items():
            if search_term.lower() in logical_addr.lower():
                available_standards.append(logical_addr)
        
        return available_standards[:5]


def main():
    """Основная функция для вызова из MCP сервера."""
    try:
        # Получаем аргументы из command line
        if len(sys.argv) != 2:
            raise ValueError("Usage: python standards_resolver.py <json_args>")
        
        args = json.loads(sys.argv[1])
        
        # Создаем resolver и выполняем запрос
        resolver = StandardsResolver()
        result = resolver.resolve_standard(
            address=args.get("address"),
            format_type=args.get("format", "full"),
            context=args.get("context")
        )
        
        # Выводим результат как JSON
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