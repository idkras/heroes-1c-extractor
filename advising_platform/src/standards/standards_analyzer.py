#!/usr/bin/env python3
"""
Анализатор дублирующихся стандартов для объединения в сильные единые стандарты.

Анализирует папки 3, 4 и dev на предмет пересечений и предлагает
план объединения дублирующихся стандартов.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class StandardsDuplicationAnalyzer:
    """Анализатор дублирующихся стандартов."""
    
    def __init__(self, standards_directory: str = '[standards .md]'):
        """
        Инициализирует анализатор.
        
        Args:
            standards_directory: Путь к директории стандартов
        """
        self.standards_dir = Path(standards_directory)
        self.target_folders = [
            '3. communication',
            '4. interface · design', 
            '2. dev'
        ]
        
        self.analysis_results = {
            'folders_analyzed': {},
            'detected_overlaps': [],
            'consolidation_plan': [],
            'statistics': {}
        }
        
    def analyze_all_folders(self) -> Dict:
        """
        Анализирует все целевые папки на предмет дублирования.
        
        Returns:
            Dict: Результаты анализа дублирования
        """
        logger.info("Начинаем анализ дублирующихся стандартов")
        
        # Анализируем каждую папку
        for folder in self.target_folders:
            folder_path = self.standards_dir / folder
            if folder_path.exists():
                folder_analysis = self._analyze_folder(folder_path, folder)
                self.analysis_results['folders_analyzed'][folder] = folder_analysis
            else:
                logger.warning(f"Папка не найдена: {folder_path}")
        
        # Выявляем пересечения между папками
        self._detect_overlaps()
        
        # Создаем план консолидации
        self._create_consolidation_plan()
        
        # Статистика
        self._calculate_statistics()
        
        return self.analysis_results
    
    def _analyze_folder(self, folder_path: Path, folder_name: str) -> Dict:
        """Анализирует отдельную папку стандартов."""
        logger.info(f"Анализируем папку: {folder_name}")
        
        md_files = list(folder_path.rglob('*.md'))
        folder_analysis = {
            'total_files': len(md_files),
            'standards': [],
            'key_themes': set(),
            'methodologies': set()
        }
        
        for md_file in md_files:
            if '[archive]' in str(md_file):
                continue  # Пропускаем архивные файлы
                
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                standard_info = self._extract_standard_info(md_file, content)
                folder_analysis['standards'].append(standard_info)
                
                # Собираем ключевые темы
                folder_analysis['key_themes'].update(standard_info['themes'])
                folder_analysis['methodologies'].update(standard_info['methodologies'])
                
            except Exception as e:
                logger.error(f"Ошибка анализа файла {md_file}: {e}")
        
        # Конвертируем sets в lists для JSON
        folder_analysis['key_themes'] = list(folder_analysis['key_themes'])
        folder_analysis['methodologies'] = list(folder_analysis['methodologies'])
        
        return folder_analysis
    
    def _extract_standard_info(self, file_path: Path, content: str) -> Dict:
        """Извлекает информацию о стандарте из содержимого файла."""
        # Извлекаем основную информацию
        title = self._extract_title(content)
        themes = self._extract_themes(content)
        methodologies = self._extract_methodologies(content)
        
        return {
            'file': str(file_path),
            'name': file_path.name,
            'title': title,
            'themes': themes,
            'methodologies': methodologies,
            'size': len(content),
            'lines': len(content.split('\n'))
        }
    
    def _extract_title(self, content: str) -> str:
        """Извлекает заголовок стандарта."""
        lines = content.split('\n')
        for line in lines[:10]:  # Ищем в первых 10 строках
            if line.startswith('#'):
                return line.strip('# ').strip()
        return "Untitled Standard"
    
    def _extract_themes(self, content: str) -> List[str]:
        """Извлекает ключевые темы из содержимого."""
        themes = set()
        content_lower = content.lower()
        
        # Ключевые темы для поиска
        theme_keywords = {
            'user-centric': ['пользователь', 'user', 'клиент', 'ux', 'эмпатия'],
            'quality': ['качество', 'quality', 'qa', 'тестирование', 'проверка'],
            'communication': ['коммуникация', 'общение', 'тон', 'стиль', 'диалог'],
            'design': ['дизайн', 'интерфейс', 'interface', 'ui', 'визуал'],
            'development': ['разработка', 'код', 'tdd', 'программирование', 'dev'],
            'methodology': ['методология', 'подход', 'процесс', 'фреймворк', 'стандарт'],
            'b2b': ['b2b', 'бизнес', 'корпоративный', 'компания'],
            'automation': ['автоматизация', 'automation', 'скрипт', 'bot']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.add(theme)
        
        return list(themes)
    
    def _extract_methodologies(self, content: str) -> List[str]:
        """Извлекает методологии из содержимого."""
        methodologies = set()
        content_lower = content.lower()
        
        # Известные методологии
        methodology_patterns = [
            'tdd', 'test-driven', 'red-green-refactor',
            'jtbd', 'jobs to be done',
            'radar', 'comprehensive',
            'registry standard', 'task master',
            'five why', '5 почему',
            'web qa', 'quality assurance'
        ]
        
        for pattern in methodology_patterns:
            if pattern in content_lower:
                methodologies.add(pattern)
        
        return list(methodologies)
    
    def _detect_overlaps(self):
        """Выявляет пересечения между папками."""
        logger.info("Выявляем пересечения между папками")
        
        folders = list(self.analysis_results['folders_analyzed'].keys())
        
        for i, folder1 in enumerate(folders):
            for folder2 in folders[i+1:]:
                overlap = self._find_folder_overlap(folder1, folder2)
                if overlap['overlap_score'] > 0.3:  # Порог значимого пересечения
                    self.analysis_results['detected_overlaps'].append(overlap)
    
    def _find_folder_overlap(self, folder1: str, folder2: str) -> Dict:
        """Находит пересечение между двумя папками."""
        data1 = self.analysis_results['folders_analyzed'][folder1]
        data2 = self.analysis_results['folders_analyzed'][folder2]
        
        # Пересечение тем
        themes1 = set(data1['key_themes'])
        themes2 = set(data2['key_themes'])
        common_themes = themes1.intersection(themes2)
        
        # Пересечение методологий
        methods1 = set(data1['methodologies'])
        methods2 = set(data2['methodologies'])
        common_methods = methods1.intersection(methods2)
        
        # Рассчитываем оценку пересечения
        total_themes = len(themes1.union(themes2))
        total_methods = len(methods1.union(methods2))
        
        overlap_score = 0
        if total_themes > 0:
            overlap_score += len(common_themes) / total_themes * 0.6
        if total_methods > 0:
            overlap_score += len(common_methods) / total_methods * 0.4
        
        return {
            'folder1': folder1,
            'folder2': folder2,
            'common_themes': list(common_themes),
            'common_methodologies': list(common_methods),
            'overlap_score': overlap_score,
            'recommendation': 'consolidate' if overlap_score > 0.5 else 'monitor'
        }
    
    def _create_consolidation_plan(self):
        """Создает план консолидации дублирующихся стандартов."""
        logger.info("Создаем план консолидации")
        
        high_overlap = [o for o in self.analysis_results['detected_overlaps'] 
                       if o['overlap_score'] > 0.5]
        
        for overlap in high_overlap:
            plan_item = {
                'source_folders': [overlap['folder1'], overlap['folder2']],
                'common_elements': {
                    'themes': overlap['common_themes'],
                    'methodologies': overlap['common_methodologies']
                },
                'proposed_unified_standard': self._generate_unified_standard_name(overlap),
                'priority': 'high' if overlap['overlap_score'] > 0.7 else 'medium',
                'complexity': self._estimate_complexity(overlap)
            }
            
            self.analysis_results['consolidation_plan'].append(plan_item)
    
    def _generate_unified_standard_name(self, overlap: Dict) -> str:
        """Генерирует название для объединенного стандарта."""
        themes = overlap['common_themes']
        
        if 'user-centric' in themes and 'quality' in themes:
            return "User-Centric Quality Framework"
        elif 'communication' in themes and 'design' in themes:
            return "Communication & Interface Design Standard"
        elif 'development' in themes and 'methodology' in themes:
            return "Development Methodology Framework"
        else:
            return f"Unified {'-'.join(themes[:2]).title()} Standard"
    
    def _estimate_complexity(self, overlap: Dict) -> str:
        """Оценивает сложность объединения стандартов."""
        score = overlap['overlap_score']
        
        if score > 0.8:
            return "low"  # Высокое пересечение = простое объединение
        elif score > 0.6:
            return "medium"
        else:
            return "high"  # Низкое пересечение = сложное объединение
    
    def _calculate_statistics(self):
        """Рассчитывает статистику анализа."""
        stats = {
            'total_folders_analyzed': len(self.analysis_results['folders_analyzed']),
            'total_standards_found': 0,
            'total_overlaps_detected': len(self.analysis_results['detected_overlaps']),
            'high_priority_consolidations': 0
        }
        
        for folder_data in self.analysis_results['folders_analyzed'].values():
            stats['total_standards_found'] += folder_data['total_files']
        
        stats['high_priority_consolidations'] = len([
            p for p in self.analysis_results['consolidation_plan'] 
            if p['priority'] == 'high'
        ])
        
        self.analysis_results['statistics'] = stats


def analyze_standards_duplication() -> Dict:
    """
    Удобная функция для анализа дублирования стандартов.
    
    Returns:
        Dict: Результаты анализа
    """
    analyzer = StandardsDuplicationAnalyzer()
    return analyzer.analyze_all_folders()


if __name__ == '__main__':
    # Запускаем анализ
    print("=== АНАЛИЗ ДУБЛИРУЮЩИХСЯ СТАНДАРТОВ ===")
    
    results = analyze_standards_duplication()
    
    print(f"📊 Статистика:")
    stats = results['statistics']
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 Обнаруженные пересечения:")
    for overlap in results['detected_overlaps']:
        print(f"   {overlap['folder1']} ↔ {overlap['folder2']}: "
              f"оценка {overlap['overlap_score']:.2f}")
    
    print(f"\n📋 План консолидации:")
    for plan in results['consolidation_plan']:
        print(f"   {plan['proposed_unified_standard']} "
              f"(приоритет: {plan['priority']})")