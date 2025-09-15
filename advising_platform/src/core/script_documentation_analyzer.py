#!/usr/bin/env python3
"""
Модуль для анализа документации существующих скриптов.
Помогает предотвратить создание дублирующих решений, сканируя имеющуюся документацию.

Автор: AI Assistant
Дата: 21 мая 2025
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

# Настройка логирования
logger = logging.getLogger(__name__)

class ScriptDocumentationAnalyzer:
    """
    Анализатор документации скриптов.
    Сканирует документацию существующих скриптов и определяет релевантные решения.
    """
    
    def __init__(self, scripts_dirs: Optional[List[str]] = None):
        """
        Инициализирует анализатор документации скриптов.
        
        Args:
            scripts_dirs: Список директорий для сканирования документации скриптов
                          (если None, используются стандартные директории)
        """
        # Список директорий для сканирования
        self.scripts_dirs = scripts_dirs or [
            "advising_platform/src",
            "scripts",
            ".",
        ]
        
        # Кеш найденных скриптов, чтобы не сканировать повторно
        self._scripts_cache: Dict[str, Dict[str, Any]] = {}
        
        # Кеш для сопоставления ключевых слов и скриптов
        self._keyword_to_scripts: Dict[str, List[str]] = {}
        
        # Список расширений скриптов для сканирования
        self.script_extensions = ['.py', '.js', '.sh']
        
        # Инициализация кеша
        self._init_cache()
    
    def _init_cache(self) -> None:
        """Инициализирует кеш скриптов."""
        if self._scripts_cache:
            return  # Кеш уже инициализирован
        
        logger.info("Инициализация кеша документации скриптов...")
        
        # Сканируем все директории
        for dir_path in self.scripts_dirs:
            if not os.path.exists(dir_path):
                logger.warning(f"Директория {dir_path} не существует")
                continue
            
            self._scan_directory(dir_path)
        
        logger.info(f"Кеш документации скриптов инициализирован: найдено {len(self._scripts_cache)} скриптов")
    
    def _scan_directory(self, dir_path: str) -> None:
        """
        Сканирует директорию на наличие скриптов.
        
        Args:
            dir_path: Путь к директории
        """
        for root, _, files in os.walk(dir_path):
            for file in files:
                # Проверяем расширение файла
                if any(file.endswith(ext) for ext in self.script_extensions):
                    file_path = os.path.join(root, file)
                    self._analyze_script_file(file_path)
    
    def _analyze_script_file(self, file_path: str) -> None:
        """
        Анализирует документацию скрипта.
        
        Args:
            file_path: Путь к файлу скрипта
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем docstring из файла
            docstring = self._extract_docstring(content)
            
            if not docstring:
                return  # Нет документации, пропускаем файл
            
            # Извлекаем ключевые слова из docstring
            keywords = self._extract_keywords(docstring)
            
            # Добавляем скрипт в кеш
            script_name = os.path.basename(file_path)
            self._scripts_cache[file_path] = {
                'name': script_name,
                'path': file_path,
                'docstring': docstring,
                'keywords': keywords
            }
            
            # Обновляем маппинг ключевых слов
            for keyword in keywords:
                if keyword not in self._keyword_to_scripts:
                    self._keyword_to_scripts[keyword] = []
                if file_path not in self._keyword_to_scripts[keyword]:
                    self._keyword_to_scripts[keyword].append(file_path)
        
        except Exception as e:
            logger.error(f"Ошибка при анализе скрипта {file_path}: {e}")
    
    def _extract_docstring(self, content: str) -> str:
        """
        Извлекает docstring из содержимого файла.
        
        Args:
            content: Содержимое файла
        
        Returns:
            str: Docstring или пустая строка, если не найден
        """
        # Регулярное выражение для извлечения docstring (как для Python, так и для JavaScript)
        patterns = [
            r'"""(.*?)"""',  # Python multi-line docstring
            r"'''(.*?)'''",  # Python multi-line docstring (альтернативный синтаксис)
            r'/\*\*(.*?)\*/',  # JavaScript multi-line comment
            r'///(.*?)$'  # JavaScript single-line documentation comment
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                # Возвращаем первый найденный docstring
                return matches[0].strip()
        
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Извлекает ключевые слова из текста.
        
        Args:
            text: Текст для анализа
        
        Returns:
            List[str]: Список ключевых слов
        """
        # Разбиваем текст на слова и очищаем от знаков препинания
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Список стоп-слов (слова, которые не являются ключевыми)
        stop_words = {'и', 'в', 'на', 'с', 'для', 'по', 'к', 'от', 'из', 'или', 'a', 'the', 'and', 'in', 'on', 'for', 'to', 'from', 'of', 'or'}
        
        # Фильтруем слова, чтобы исключить стоп-слова и короткие слова
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Добавляем также ключевые фразы (биграммы и триграммы)
        phrases = []
        words = text.lower().split()
        if len(words) >= 2:
            for i in range(len(words) - 1):
                phrases.append(f"{words[i]} {words[i+1]}")
        if len(words) >= 3:
            for i in range(len(words) - 2):
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Объединяем ключевые слова и фразы
        all_keywords = list(set(keywords + phrases))
        
        return all_keywords
    
    def find_similar_scripts(self, task_description: str, threshold: int = 3) -> List[Dict[str, Any]]:
        """
        Находит скрипты, похожие на описание задачи.
        
        Args:
            task_description: Описание задачи
            threshold: Минимальное количество совпадающих ключевых слов
        
        Returns:
            List[Dict[str, Any]]: Список похожих скриптов с метаданными
        """
        # Извлекаем ключевые слова из описания задачи
        task_keywords = self._extract_keywords(task_description)
        
        # Счетчик скриптов по количеству совпадающих ключевых слов
        script_matches: Dict[str, int] = {}
        
        # Подсчитываем количество совпадающих ключевых слов для каждого скрипта
        for keyword in task_keywords:
            if keyword in self._keyword_to_scripts:
                for script_path in self._keyword_to_scripts[keyword]:
                    if script_path not in script_matches:
                        script_matches[script_path] = 0
                    script_matches[script_path] += 1
        
        # Фильтруем скрипты по порогу
        filtered_scripts = {path: count for path, count in script_matches.items() if count >= threshold}
        
        # Сортируем скрипты по количеству совпадений (по убыванию)
        sorted_scripts = sorted(filtered_scripts.items(), key=lambda x: x[1], reverse=True)
        
        # Формируем результат
        similar_scripts = []
        for script_path, match_count in sorted_scripts:
            script_info = self._scripts_cache[script_path].copy()
            script_info['match_count'] = match_count
            script_info['matched_keywords'] = [kw for kw in task_keywords if kw in self._scripts_cache[script_path]['keywords']]
            similar_scripts.append(script_info)
        
        return similar_scripts
    
    def get_script_summary(self, script_path: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает сводную информацию о скрипте.
        
        Args:
            script_path: Путь к скрипту
        
        Returns:
            Optional[Dict[str, Any]]: Сводная информация о скрипте или None, если скрипт не найден
        """
        if script_path in self._scripts_cache:
            return self._scripts_cache[script_path]
        return None
    
    def refresh_cache(self) -> None:
        """JTBD:
Я (разработчик) хочу использовать функцию refresh_cache, чтобы эффективно выполнить соответствующую операцию.
         
         Обновляет кеш скриптов."""
        self._scripts_cache = {}
        self._keyword_to_scripts = {}
        self._init_cache()

# Глобальный экземпляр анализатора
_analyzer: Optional[ScriptDocumentationAnalyzer] = None

def get_analyzer() -> ScriptDocumentationAnalyzer:
    """
    Возвращает глобальный экземпляр анализатора документации скриптов.
    
    Returns:
        ScriptDocumentationAnalyzer: Экземпляр анализатора
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = ScriptDocumentationAnalyzer()
    return _analyzer

def find_similar_scripts(task_description: str, threshold: int = 3) -> List[Dict[str, Any]]:
    """
    Находит скрипты, похожие на описание задачи.
    
    Args:
        task_description: Описание задачи
        threshold: Минимальное количество совпадающих ключевых слов
    
    Returns:
        List[Dict[str, Any]]: Список похожих скриптов с метаданными
    """
    analyzer = get_analyzer()
    return analyzer.find_similar_scripts(task_description, threshold)

def get_script_summary(script_path: str) -> Optional[Dict[str, Any]]:
    """
    Возвращает сводную информацию о скрипте.
    
    Args:
        script_path: Путь к скрипту
    
    Returns:
        Optional[Dict[str, Any]]: Сводная информация о скрипте или None, если скрипт не найден
    """
    analyzer = get_analyzer()
    return analyzer.get_script_summary(script_path)

def refresh_scripts_cache() -> None:
    """JTBD:
Я (разработчик) хочу использовать функцию refresh_scripts_cache, чтобы эффективно выполнить соответствующую операцию.
     
     Обновляет кеш скриптов."""
    if _analyzer:
        _analyzer.refresh_cache()