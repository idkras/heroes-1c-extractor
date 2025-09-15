#!/usr/bin/env python3
"""
Расширенный триггер стандартов с детальной статистикой по типам документов в кеше.

Цель: Показывать полную аналитику состава кеша для мониторинга и оптимизации системы:
- Стандарты по папкам
- Задачи (включая гипотезы/задачи-гипотезы)
- Инциденты
- Детальная разбивка по категориям

Автор: AI Assistant  
Дата: 22 May 2025
Задача: T012
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class DocumentTypeAnalyzer:
    """Анализатор типов документов для детальной статистики кеша."""
    
    def __init__(self):
        """Инициализация анализатора."""
        self.base_path = Path(".")
        self.cache_managers = []
        self._initialize_cache_managers()
    
    def _initialize_cache_managers(self):
        """Инициализирует доступные менеджеры кеша."""
        try:
            # Пытаемся подключить различные кеш-модули с правильными путями
            import sys
            sys.path.append('.')
            
            from src.cache.real_inmemory_cache import get_cache
            
            # Используем новый единый RealInMemoryCache
            self.cache = get_cache()
            self.cache_managers = [
                ('real_inmemory_cache', self.cache)
            ]
            logger.info(f"Инициализировано {len(self.cache_managers)} кеш-менеджеров")
            
        except ImportError as e:
            logger.warning(f"Не удалось импортировать кеш-модули: {e}")
            # Создаем пустой список, анализ файловой системы все равно работает
            self.cache_managers = []
    
    def analyze_file_type(self, file_path: str) -> Dict[str, Any]:
        """
        Анализирует тип файла и извлекает метаданные.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Dict с информацией о типе и метаданных
        """
        path_lower = file_path.lower()
        
        # Определяем тип документа
        if '[standards .md]' in file_path:
            return self._analyze_standard(file_path)
        elif '[todo · incidents]' in file_path and 'todo' in path_lower:
            return self._analyze_task_or_hypothesis(file_path)
        elif '[todo · incidents]' in file_path and 'incident' in path_lower:
            return self._analyze_incident(file_path)
        elif 'projects' in path_lower:
            return self._analyze_project(file_path)
        else:
            return {
                'type': 'other',
                'category': 'other',
                'subcategory': 'unknown',
                'size': self._get_file_size(file_path)
            }
    
    def _analyze_standard(self, file_path: str) -> Dict[str, Any]:
        """Анализирует файл стандарта с фильтрацией архивов и бэкапов."""
        # Проверяем является ли это архивом или бэкапом
        path_lower = file_path.lower()
        
        # Исключаем архивы и бэкапы
        archive_keywords = [
            'archive', 'backup', 'consolidated', 'template', 
            '20250512', '20250513', '20250514', '20250510',
            'backups_', 'ik', 'ai never use', 'rename_backup'
        ]
        
        for keyword in archive_keywords:
            if keyword in path_lower:
                return {
                    'type': 'archive',
                    'category': 'archives',
                    'subcategory': 'archived_standard',
                    'folder': self._extract_folder_name(file_path),
                    'size': self._get_file_size(file_path)
                }
        
        # Определяем подкатегорию активного стандарта по структуре папок
        path_parts = file_path.split('/')
        subcategory = 'general'
        
        # Анализируем активные папки согласно структуре
        for part in path_parts:
            part_lower = part.lower()
            
            if '0. core' in part_lower:
                subcategory = 'core_standards'
            elif '1. process' in part_lower or 'goalmap' in part_lower:
                subcategory = 'process_standards'
            elif '2. projects' in part_lower or 'context' in part_lower:
                subcategory = 'project_standards'
            elif '3. scenario' in part_lower or 'jtbd' in part_lower:
                subcategory = 'scenario_standards'
            elif '4. dev' in part_lower or 'design' in part_lower:
                subcategory = 'dev_standards'
            elif '6. advising' in part_lower or 'review' in part_lower:
                subcategory = 'advising_standards'
            elif '8. auto' in part_lower or 'n8n' in part_lower:
                subcategory = 'automation_standards'
            elif 'registry' in part_lower:
                subcategory = 'registry_standards'
            elif 'task' in part_lower or 'master' in part_lower:
                subcategory = 'task_master_standards'
        
        return {
            'type': 'standard',
            'category': 'standards',
            'subcategory': subcategory,
            'folder': self._extract_folder_name(file_path),
            'size': self._get_file_size(file_path),
            'is_active': True
        }
    
    def _analyze_task_or_hypothesis(self, file_path: str) -> Dict[str, Any]:
        """Анализирует файл задачи или гипотезы."""
        content = self._read_file_content(file_path)
        
        # Проверяем является ли это гипотезой
        is_hypothesis = False
        if content:
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in [
                'гипотез', 'hypothesis', 'предполож', 'assume', 'эксперимент'
            ]):
                is_hypothesis = True
        
        # Извлекаем приоритет задачи
        priority = self._extract_task_priority(content or '')
        
        return {
            'type': 'hypothesis' if is_hypothesis else 'task',
            'category': 'tasks',
            'subcategory': 'hypothesis' if is_hypothesis else 'regular_task',
            'priority': priority,
            'size': self._get_file_size(file_path)
        }
    
    def _analyze_incident(self, file_path: str) -> Dict[str, Any]:
        """Анализирует файл инцидента."""
        content = self._read_file_content(file_path)
        
        # Определяем серьезность инцидента
        severity = 'medium'
        if content:
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in [
                'критический', 'critical', 'blocker', 'urgent'
            ]):
                severity = 'high'
            elif any(keyword in content_lower for keyword in [
                'minor', 'низкий', 'small'
            ]):
                severity = 'low'
        
        return {
            'type': 'incident',
            'category': 'incidents',
            'subcategory': f'{severity}_severity',
            'severity': severity,
            'size': self._get_file_size(file_path)
        }
    
    def _analyze_project(self, file_path: str) -> Dict[str, Any]:
        """Анализирует файл проекта."""
        return {
            'type': 'project',
            'category': 'projects',
            'subcategory': 'project_file',
            'size': self._get_file_size(file_path)
        }
    
    def _extract_task_priority(self, content: str) -> str:
        """Извлекает приоритет задачи из содержимого."""
        if not content:
            return 'unknown'
        
        content_lower = content.lower()
        
        if '🚨' in content or 'alarm' in content_lower:
            return 'alarm'
        elif '🔴' in content or 'blocker' in content_lower:
            return 'blocker'
        elif '🟠' in content or 'asap' in content_lower:
            return 'asap'
        elif '🔍' in content or 'research' in content_lower:
            return 'research'
        elif '⭐' in content or 'exciter' in content_lower:
            return 'exciter'
        elif '🟢' in content or 'small' in content_lower:
            return 'small'
        else:
            return 'normal'
    
    def _extract_folder_name(self, file_path: str) -> str:
        """Извлекает имя папки из пути."""
        path_parts = file_path.split('/')
        for part in path_parts:
            if '[' in part and ']' in part:
                return part
        return 'root'
    
    def _get_file_size(self, file_path: str) -> int:
        """Получает размер файла."""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """Читает содержимое файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return None


class EnhancedStandardsTrigger:
    """Расширенный триггер стандартов с детальной статистикой."""
    
    def __init__(self):
        """Инициализация триггера."""
        self.analyzer = DocumentTypeAnalyzer()
        self.statistics = {}
    
    def generate_detailed_cache_statistics(self) -> Dict[str, Any]:
        """
        Генерирует детальную статистику по типам документов в кеше.
        
        Returns:
            Детальная статистика кеша
        """
        logger.info("🔍 Генерация детальной статистики кеша...")
        
        statistics = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_documents': 0,
                'total_size_bytes': 0
            },
            'by_type': {
                'standards': {'count': 0, 'size': 0, 'subcategories': {}},
                'tasks': {'count': 0, 'size': 0, 'subcategories': {}},
                'hypotheses': {'count': 0, 'size': 0, 'subcategories': {}},
                'incidents': {'count': 0, 'size': 0, 'subcategories': {}},
                'projects': {'count': 0, 'size': 0, 'subcategories': {}},
                'others': {'count': 0, 'size': 0, 'subcategories': {}}
            },
            'by_folder': {},
            'by_priority': {},
            'by_severity': {},
            'cache_sources': []
        }
        
        # Анализируем файлы через различные источники
        self._analyze_filesystem_directly(statistics)
        self._analyze_cache_managers(statistics)
        
        # Вычисляем проценты
        self._calculate_percentages(statistics)
        
        return statistics
    
    def _analyze_filesystem_directly(self, statistics: Dict[str, Any]):
        """Анализирует файловую систему напрямую."""
        logger.debug("📁 Анализ файловой системы...")
        
        key_directories = [
            '[standards .md]',
            '[todo · incidents]',
            'projects',
            'cache'
        ]
        
        for directory in key_directories:
            if os.path.exists(directory):
                self._scan_directory(directory, statistics)
    
    def _scan_directory(self, directory: str, statistics: Dict[str, Any]):
        """Сканирует директорию и обновляет статистику."""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.md', '.txt', '.json')):
                        file_path = os.path.join(root, file)
                        self._process_file(file_path, statistics)
        except Exception as e:
            logger.warning(f"Ошибка при сканировании {directory}: {e}")
    
    def _process_file(self, file_path: str, statistics: Dict[str, Any]):
        """Обрабатывает один файл и обновляет статистику."""
        analysis = self.analyzer.analyze_file_type(file_path)
        
        # Обновляем общую статистику
        statistics['summary']['total_documents'] += 1
        statistics['summary']['total_size_bytes'] += analysis.get('size', 0)
        
        # Обновляем статистику по типам
        doc_type = analysis.get('type', 'other')
        category_key = doc_type + 's' if doc_type != 'other' else 'others'
        
        if category_key in statistics['by_type']:
            statistics['by_type'][category_key]['count'] += 1
            statistics['by_type'][category_key]['size'] += analysis.get('size', 0)
            
            # Подкатегории
            subcategory = analysis.get('subcategory', 'unknown')
            subcats = statistics['by_type'][category_key]['subcategories']
            if subcategory not in subcats:
                subcats[subcategory] = {'count': 0, 'size': 0}
            subcats[subcategory]['count'] += 1
            subcats[subcategory]['size'] += analysis.get('size', 0)
        
        # Статистика по папкам
        folder = analysis.get('folder', 'unknown')
        if folder not in statistics['by_folder']:
            statistics['by_folder'][folder] = {'count': 0, 'size': 0, 'types': {}}
        statistics['by_folder'][folder]['count'] += 1
        statistics['by_folder'][folder]['size'] += analysis.get('size', 0)
        
        if doc_type not in statistics['by_folder'][folder]['types']:
            statistics['by_folder'][folder]['types'][doc_type] = 0
        statistics['by_folder'][folder]['types'][doc_type] += 1
        
        # Статистика по приоритетам (для задач)
        if 'priority' in analysis:
            priority = analysis['priority']
            if priority not in statistics['by_priority']:
                statistics['by_priority'][priority] = {'count': 0, 'size': 0}
            statistics['by_priority'][priority]['count'] += 1
            statistics['by_priority'][priority]['size'] += analysis.get('size', 0)
        
        # Статистика по серьезности (для инцидентов)
        if 'severity' in analysis:
            severity = analysis['severity']
            if severity not in statistics['by_severity']:
                statistics['by_severity'][severity] = {'count': 0, 'size': 0}
            statistics['by_severity'][severity]['count'] += 1
            statistics['by_severity'][severity]['size'] += analysis.get('size', 0)
    
    def _analyze_cache_managers(self, statistics: Dict[str, Any]):
        """Анализирует данные из нового RealInMemoryCache."""
        logger.debug("💾 Анализ RealInMemoryCache...")
        
        try:
            # Загружаем документы в новый кеш если еще не загружены
            cache_stats = self.analyzer.cache.get_statistics()
            if cache_stats['total_documents'] == 0:
                logger.info("📥 Загружаем документы в RealInMemoryCache...")
                loaded = self.analyzer.cache.load_documents(['../[standards .md]', '../[todo · incidents]'])
                logger.info(f"✅ Загружено {loaded} документов в кеш")
                cache_stats = self.analyzer.cache.get_statistics()
            
            # Обновляем общую статистику
            statistics['summary']['total_documents'] += cache_stats['total_documents']
            statistics['summary']['total_size_bytes'] += int(cache_stats['memory_usage_mb'] * 1024 * 1024)
            
            # Анализируем документы по типам из кеша
            for doc_type, count in cache_stats.get('document_types', {}).items():
                if doc_type == 'standard':
                    statistics['by_type']['standards']['count'] += count
                elif doc_type == 'task':
                    statistics['by_type']['tasks']['count'] += count
                elif doc_type == 'incident':
                    statistics['by_type']['incidents']['count'] += count
                else:
                    statistics['by_type']['others']['count'] += count
            
            # Добавляем информацию об источнике кеша
            statistics['cache_sources'].append({
                'name': 'RealInMemoryCache',
                'total_files': cache_stats['total_documents'],
                'memory_usage_mb': cache_stats['memory_usage_mb'],
                'hit_rate_percent': cache_stats['hit_rate_percent'],
                'document_types': cache_stats.get('document_types', {}),
                'available': True,
                'status': 'active'
            })
            
            logger.info(f"✅ RealInMemoryCache: {cache_stats['total_documents']} документов, {cache_stats['memory_usage_mb']:.2f}MB")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка анализа RealInMemoryCache: {e}")
            statistics['cache_sources'].append({
                'name': 'RealInMemoryCache',
                'available': False,
                'error': str(e)
            })
    
    def _get_cache_stats(self, cache_class, cache_name: str) -> Optional[Dict]:
        """Получает статистику из конкретного кеша."""
        try:
            if cache_name == 'cache_storage':
                # CacheStorage требует путь к файлу
                cache_path = "cache/cache_entries.json"
                if os.path.exists(cache_path):
                    cache_instance = cache_class(cache_path)
                    return cache_instance.get_statistics()
            else:
                # Другие кеши могут инициализироваться без параметров
                cache_instance = cache_class()
                if hasattr(cache_instance, 'get_statistics'):
                    return cache_instance.get_statistics()
        except Exception as e:
            logger.debug(f"Не удалось получить статистику из {cache_name}: {e}")
        return None
    
    def _calculate_percentages(self, statistics: Dict[str, Any]):
        """Вычисляет процентные соотношения."""
        total = statistics['summary']['total_documents']
        if total == 0:
            return
        
        # Проценты по типам
        for type_name, type_data in statistics['by_type'].items():
            type_data['percentage'] = round((type_data['count'] / total) * 100, 1)
        
        # Проценты по папкам
        for folder_name, folder_data in statistics['by_folder'].items():
            folder_data['percentage'] = round((folder_data['count'] / total) * 100, 1)
    
    def format_statistics_report(self, statistics: Dict[str, Any]) -> str:
        """
        Форматирует статистику в читаемый отчет.
        
        Args:
            statistics: Данные статистики
            
        Returns:
            Форматированный отчет
        """
        report = []
        report.append("📊 === ДЕТАЛЬНАЯ СТАТИСТИКА КЕША ===")
        report.append(f"🕒 Время: {statistics['timestamp']}")
        report.append("")
        
        # Общая сводка
        summary = statistics['summary']
        total_size_mb = summary['total_size_bytes'] / (1024 * 1024)
        report.append(f"📈 ОБЩАЯ СВОДКА:")
        report.append(f"   📄 Всего документов: {summary['total_documents']}")
        report.append(f"   💾 Общий размер: {total_size_mb:.2f} MB")
        report.append("")
        
        # Статистика по типам
        report.append("📋 СТАТИСТИКА ПО ТИПАМ ДОКУМЕНТОВ:")
        for type_name, type_data in statistics['by_type'].items():
            if type_data['count'] > 0:
                size_mb = type_data['size'] / (1024 * 1024)
                report.append(f"   {self._get_type_emoji(type_name)} {type_name.upper()}: {type_data['count']} документов ({type_data.get('percentage', 0)}%) - {size_mb:.2f} MB")
                
                # Подкатегории
                for subcat, subcat_data in type_data['subcategories'].items():
                    subcat_size_mb = subcat_data['size'] / (1024 * 1024)
                    report.append(f"      └─ {subcat}: {subcat_data['count']} ({subcat_size_mb:.2f} MB)")
        report.append("")
        
        # Статистика по папкам
        report.append("📁 СТАТИСТИКА ПО ПАПКАМ:")
        for folder_name, folder_data in statistics['by_folder'].items():
            if folder_data['count'] > 0:
                size_mb = folder_data['size'] / (1024 * 1024)
                report.append(f"   📂 {folder_name}: {folder_data['count']} документов ({folder_data.get('percentage', 0)}%) - {size_mb:.2f} MB")
                
                # Типы в папке
                for doc_type, count in folder_data['types'].items():
                    report.append(f"      └─ {doc_type}: {count}")
        report.append("")
        
        # Статистика по приоритетам
        if statistics['by_priority']:
            report.append("🎯 СТАТИСТИКА ПО ПРИОРИТЕТАМ ЗАДАЧ:")
            for priority, priority_data in statistics['by_priority'].items():
                emoji = self._get_priority_emoji(priority)
                size_mb = priority_data['size'] / (1024 * 1024)
                report.append(f"   {emoji} {priority}: {priority_data['count']} задач - {size_mb:.2f} MB")
            report.append("")
        
        # Статистика по серьезности инцидентов
        if statistics['by_severity']:
            report.append("⚠️ СТАТИСТИКА ПО СЕРЬЕЗНОСТИ ИНЦИДЕНТОВ:")
            for severity, severity_data in statistics['by_severity'].items():
                emoji = self._get_severity_emoji(severity)
                size_mb = severity_data['size'] / (1024 * 1024)
                report.append(f"   {emoji} {severity}: {severity_data['count']} инцидентов - {size_mb:.2f} MB")
            report.append("")
        
        # Источники кеша
        if statistics['cache_sources']:
            report.append("💾 ИСТОЧНИКИ КЕША:")
            for source in statistics['cache_sources']:
                status = "✅" if source['available'] else "❌"
                report.append(f"   {status} {source['name']}")
                if source['available'] and 'stats' in source:
                    stats = source['stats']
                    if isinstance(stats, dict):
                        for key, value in stats.items():
                            if isinstance(value, (int, float, str)):
                                report.append(f"      └─ {key}: {value}")
        
        return "\n".join(report)
    
    def _get_type_emoji(self, type_name: str) -> str:
        """Возвращает эмодзи для типа документа."""
        emoji_map = {
            'standards': '📖',
            'tasks': '📝',
            'hypotheses': '🔬',
            'incidents': '🚨',
            'projects': '🗂️',
            'others': '📄'
        }
        return emoji_map.get(type_name, '📄')
    
    def _get_priority_emoji(self, priority: str) -> str:
        """Возвращает эмодзи для приоритета."""
        emoji_map = {
            'alarm': '🚨',
            'blocker': '🔴',
            'asap': '🟠',
            'research': '🔍',
            'exciter': '⭐',
            'small': '🟢',
            'normal': '⚪',
            'unknown': '❓'
        }
        return emoji_map.get(priority, '⚪')
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Возвращает эмодзи для серьезности."""
        emoji_map = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return emoji_map.get(severity, '🟡')
    
    def run_statistics_trigger(self) -> str:
        """
        Запускает триггер генерации статистики.
        
        Returns:
            Форматированный отчет
        """
        logger.info("🚀 Запуск расширенного триггера стандартов...")
        
        try:
            # Генерируем статистику
            statistics = self.generate_detailed_cache_statistics()
            
            # Форматируем отчет
            report = self.format_statistics_report(statistics)
            
            # Сохраняем статистику в файл
            self._save_statistics(statistics)
            
            logger.info("✅ Триггер стандартов успешно выполнен!")
            return report
            
        except Exception as e:
            error_msg = f"❌ Ошибка при выполнении триггера: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _save_statistics(self, statistics: Dict[str, Any]):
        """Сохраняет статистику в файл."""
        try:
            cache_dir = Path("cache")
            cache_dir.mkdir(exist_ok=True)
            
            stats_file = cache_dir / "enhanced_cache_statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(statistics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Статистика сохранена в {stats_file}")
        except Exception as e:
            logger.warning(f"Не удалось сохранить статистику: {e}")


def main():
    """Основная функция для запуска триггера."""
    trigger = EnhancedStandardsTrigger()
    report = trigger.run_statistics_trigger()
    print(report)
    return report


if __name__ == "__main__":
    main()