#!/usr/bin/env python3
"""
Модуль для автоматического исправления метаданных в стандартах.

Обеспечивает соответствие всех стандартов требованиям Registry Standard
с корректными полями: type, version, status, updated.

Автор: AI Assistant
Дата: 22 May 2025
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class StandardsMetadataFixer:
    """Класс для исправления метаданных в файлах стандартов."""
    
    def __init__(self, standards_directory: str = '[standards .md]'):
        """
        Инициализирует фиксатор метаданных.
        
        Args:
            standards_directory: Путь к директории стандартов
        """
        self.standards_dir = Path(standards_directory)
        self.required_fields = {
            'type': 'standard',
            'version': '1.0',
            'status': 'active',
            'updated': datetime.now().strftime('%d %B %Y')
        }
        
        self.statistics = {
            'files_processed': 0,
            'files_fixed': 0,
            'errors': 0,
            'missing_metadata': []
        }
        
    def analyze_standards_metadata(self) -> Dict:
        """
        Анализирует метаданные во всех стандартах.
        
        Returns:
            Dict: Статистика анализа метаданных
        """
        logger.info("Начинаем анализ метаданных стандартов")
        
        if not self.standards_dir.exists():
            logger.error(f"Директория стандартов не найдена: {self.standards_dir}")
            return {'error': 'Directory not found'}
        
        standards_files = list(self.standards_dir.rglob('*.md'))
        missing_metadata = []
        
        for standard_file in standards_files:
            try:
                self.statistics['files_processed'] += 1
                content = standard_file.read_text(encoding='utf-8', errors='ignore')
                
                missing_fields = self._check_missing_metadata(content)
                if missing_fields:
                    missing_metadata.append({
                        'file': str(standard_file),
                        'missing': missing_fields
                    })
                    
            except Exception as e:
                logger.error(f"Ошибка анализа файла {standard_file}: {e}")
                self.statistics['errors'] += 1
        
        self.statistics['missing_metadata'] = missing_metadata
        
        logger.info(f"Анализ завершен: {len(standards_files)} файлов, "
                   f"{len(missing_metadata)} требуют исправления")
        
        return {
            'total_files': len(standards_files),
            'files_need_fixing': len(missing_metadata),
            'missing_metadata': missing_metadata[:5],  # Первые 5 для обзора
            'statistics': self.statistics
        }
    
    def fix_standards_metadata(self, dry_run: bool = True) -> Dict:
        """
        Исправляет метаданные во всех стандартах.
        
        Args:
            dry_run: Если True, только показывает что будет исправлено
            
        Returns:
            Dict: Результаты исправления
        """
        logger.info(f"Начинаем исправление метаданных (dry_run={dry_run})")
        
        analysis = self.analyze_standards_metadata()
        if 'error' in analysis:
            return analysis
            
        fixed_files = []
        
        for item in analysis['missing_metadata']:
            try:
                file_path = Path(item['file'])
                missing_fields = item['missing']
                
                if not dry_run:
                    result = self._fix_file_metadata(file_path, missing_fields)
                    if result:
                        fixed_files.append(str(file_path))
                        self.statistics['files_fixed'] += 1
                else:
                    # В dry_run режиме только показываем что исправим
                    fixed_files.append(f"WOULD FIX: {file_path}")
                    
            except Exception as e:
                logger.error(f"Ошибка исправления файла {item['file']}: {e}")
                self.statistics['errors'] += 1
        
        result = {
            'dry_run': dry_run,
            'files_analyzed': analysis['total_files'],
            'files_fixed': len(fixed_files),
            'fixed_files': fixed_files[:10],  # Первые 10
            'statistics': self.statistics
        }
        
        logger.info(f"Исправление завершено: {len(fixed_files)} файлов")
        return result
    
    def _check_missing_metadata(self, content: str) -> List[str]:
        """Проверяет какие метаданные отсутствуют в файле."""
        missing = []
        
        for field in self.required_fields:
            pattern = rf'^{field}:\s*'
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                missing.append(field)
                
        return missing
    
    def _fix_file_metadata(self, file_path: Path, missing_fields: List[str]) -> bool:
        """
        Исправляет метаданные в конкретном файле.
        
        Args:
            file_path: Путь к файлу
            missing_fields: Список отсутствующих полей
            
        Returns:
            bool: True если исправление успешно
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Создаем блок метаданных
            metadata_block = self._create_metadata_block(missing_fields)
            
            # Добавляем метаданные в начало файла
            if content.startswith('#'):
                # Файл начинается с заголовка
                lines = content.split('\n')
                title_line = lines[0]
                rest_content = '\n'.join(lines[1:])
                
                new_content = f"{title_line}\n\n{metadata_block}\n{rest_content}"
            else:
                # Добавляем метаданные в начало
                new_content = f"{metadata_block}\n\n{content}"
            
            # Записываем исправленный файл
            file_path.write_text(new_content, encoding='utf-8')
            
            logger.info(f"Исправлены метаданные в файле: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка исправления файла {file_path}: {e}")
            return False
    
    def _create_metadata_block(self, missing_fields: List[str]) -> str:
        """Создает блок метаданных для добавления в файл."""
        metadata_lines = []
        
        for field in missing_fields:
            if field in self.required_fields:
                value = self.required_fields[field]
                metadata_lines.append(f"{field}: {value}")
        
        return '\n'.join(metadata_lines)
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику работы фиксатора."""
        return self.statistics


def fix_all_standards_metadata(dry_run: bool = True) -> Dict:
    """
    Удобная функция для исправления метаданных всех стандартов.
    
    Args:
        dry_run: Если True, только показывает что будет исправлено
        
    Returns:
        Dict: Результаты исправления
    """
    fixer = StandardsMetadataFixer()
    return fixer.fix_standards_metadata(dry_run=dry_run)


if __name__ == '__main__':
    # Тестируем анализ метаданных
    fixer = StandardsMetadataFixer()
    
    print("=== АНАЛИЗ МЕТАДАННЫХ СТАНДАРТОВ ===")
    analysis = fixer.analyze_standards_metadata()
    
    print(f"Всего файлов: {analysis.get('total_files', 0)}")
    print(f"Требуют исправления: {analysis.get('files_need_fixing', 0)}")
    
    if analysis.get('missing_metadata'):
        print("\nПримеры файлов с отсутствующими метаданными:")
        for item in analysis['missing_metadata']:
            print(f"  {Path(item['file']).name}: {item['missing']}")
    
    print("\n=== ТЕСТОВОЕ ИСПРАВЛЕНИЕ (DRY RUN) ===")
    dry_result = fixer.fix_standards_metadata(dry_run=True)
    
    print(f"Файлов для исправления: {dry_result.get('files_fixed', 0)}")
    if dry_result.get('fixed_files'):
        print("Примеры файлов для исправления:")
        for file in dry_result['fixed_files'][:3]:
            print(f"  {file}")