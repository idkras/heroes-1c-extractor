#!/usr/bin/env python3
"""
Инструмент для бенчмаркинга in-memory индексатора.
Сравнивает производительность с существующим решением.
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Any, List, Tuple, Optional
import statistics

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Импортируем in-memory индексатор
from advising_platform.advising_platform.src.core.inmemory_indexer import InMemoryIndexer

# URL API-сервера для сравнения
API_BASE_URL = "http://localhost:5001/api"

class BenchmarkRunner:
    """Класс для запуска бенчмарков и сравнения результатов."""
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.indexer = InMemoryIndexer()
        self.results = {
            'api': {},
            'inmemory': {},
            'comparison': {}
        }
    
    def prepare_data(self, directories: List[str]):
        """
        Индексирует данные для тестирования.
        
        Args:
            directories: Список директорий для индексации
        """
        print("Подготовка данных для тестирования...")
        
        total_docs = 0
        for directory in directories:
            if not os.path.exists(directory):
                print(f"Директория не существует: {directory}")
                continue
            
            print(f"Индексация директории: {directory}")
            docs_count = self.indexer.index_directory(directory)
            total_docs += docs_count
            print(f"  - Проиндексировано {docs_count} документов")
        
        print(f"Всего проиндексировано: {total_docs} документов")
        
        # Выводим статистику индексатора
        stats = self.indexer.get_statistics()
        print("\nСтатистика индексатора:")
        print(f"  - Всего документов: {stats['total_documents']}")
        print(f"  - Типы документов: {stats['document_types']}")
        print(f"  - Всего задач: {stats['total_tasks']}")
        print(f"  - Всего инцидентов: {stats['total_incidents']}")
        print(f"  - Логических ID: {stats['logical_ids']}")
        print(f"  - Проиндексированных слов: {stats['indexed_words']}")
    
    def make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], float]:
        # Инициализация пустого словаря параметров, если они не предоставлены
        if params is None:
            params = {}
        """
        Выполняет запрос к API и измеряет время выполнения.
        
        Args:
            endpoint: API-эндпоинт
            params: Параметры запроса
            
        Returns:
            Кортеж (результат запроса, время выполнения в секундах)
        """
        url = f"{self.api_url}/{endpoint}"
        
        start_time = time.time()
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            print(f"Ошибка API запроса: {e}")
            result = {"error": str(e)}
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return result, execution_time
    
    def bench_api_search(self, query: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Выполняет бенчмарк поиска через API.
        
        Args:
            query: Поисковый запрос
            iterations: Количество повторений
            
        Returns:
            Словарь с результатами бенчмарка
        """
        print(f"API поиск: '{query}' x {iterations} iterations")
        
        times = []
        results = None
        
        for i in range(iterations):
            result, execution_time = self.make_api_request('search', {'q': query})
            times.append(execution_time)
            
            if i == 0:
                results = result
            
            print(f"  - Итерация {i+1}: {execution_time:.6f} сек")
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  - Среднее время: {avg_time:.6f} сек")
        print(f"  - Медиана: {median_time:.6f} сек")
        print(f"  - Мин/Макс: {min_time:.6f}/{max_time:.6f} сек")
        
        return {
            'query': query,
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'results': results
        }
    
    def bench_inmemory_search(self, query: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Выполняет бенчмарк поиска через in-memory индексатор.
        
        Args:
            query: Поисковый запрос
            iterations: Количество повторений
            
        Returns:
            Словарь с результатами бенчмарка
        """
        print(f"In-Memory поиск: '{query}' x {iterations} iterations")
        
        times = []
        results = None
        
        for i in range(iterations):
            start_time = time.time()
            result = self.indexer.search(query)
            end_time = time.time()
            
            execution_time = end_time - start_time
            times.append(execution_time)
            
            if i == 0:
                results = result
            
            print(f"  - Итерация {i+1}: {execution_time:.6f} сек")
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  - Среднее время: {avg_time:.6f} сек")
        print(f"  - Медиана: {median_time:.6f} сек")
        print(f"  - Мин/Макс: {min_time:.6f}/{max_time:.6f} сек")
        
        return {
            'query': query,
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'results': results
        }
    
    def bench_api_get_document(self, path: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Выполняет бенчмарк получения документа через API.
        
        Args:
            path: Путь к документу
            iterations: Количество повторений
            
        Returns:
            Словарь с результатами бенчмарка
        """
        print(f"API получение документа: '{path}' x {iterations} iterations")
        
        times = []
        results = None
        
        for i in range(iterations):
            result, execution_time = self.make_api_request(f'file/{path}')
            times.append(execution_time)
            
            if i == 0:
                results = result
            
            print(f"  - Итерация {i+1}: {execution_time:.6f} сек")
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  - Среднее время: {avg_time:.6f} сек")
        print(f"  - Медиана: {median_time:.6f} сек")
        print(f"  - Мин/Макс: {min_time:.6f}/{max_time:.6f} сек")
        
        return {
            'path': path,
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'results': results
        }
    
    def bench_inmemory_get_document(self, path: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Выполняет бенчмарк получения документа через in-memory индексатор.
        
        Args:
            path: Путь к документу
            iterations: Количество повторений
            
        Returns:
            Словарь с результатами бенчмарка
        """
        print(f"In-Memory получение документа: '{path}' x {iterations} iterations")
        
        times = []
        results = None
        
        for i in range(iterations):
            start_time = time.time()
            result = self.indexer.get_document(path)
            end_time = time.time()
            
            execution_time = end_time - start_time
            times.append(execution_time)
            
            if i == 0:
                results = result
            
            print(f"  - Итерация {i+1}: {execution_time:.6f} сек")
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  - Среднее время: {avg_time:.6f} сек")
        print(f"  - Медиана: {median_time:.6f} сек")
        print(f"  - Мин/Макс: {min_time:.6f}/{max_time:.6f} сек")
        
        return {
            'path': path,
            'iterations': iterations,
            'times': times,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'results': results
        }
    
    def run_search_benchmarks(self, queries: List[str], iterations: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Запускает бенчмарки поиска для обоих методов.
        
        Args:
            queries: Список поисковых запросов
            iterations: Количество повторений
            
        Returns:
            Словарь с результатами бенчмарков
        """
        search_results = {
            'api': {},
            'inmemory': {},
            'comparison': {}
        }
        
        for query in queries:
            print(f"\nБенчмаркинг поиска для запроса: '{query}'")
            
            # Тестируем API
            api_result = self.bench_api_search(query, iterations)
            search_results['api'][query] = api_result
            
            # Тестируем in-memory
            inmemory_result = self.bench_inmemory_search(query, iterations)
            search_results['inmemory'][query] = inmemory_result
            
            # Сравниваем результаты
            if api_result['avg_time'] > 0:
                speedup = api_result['avg_time'] / inmemory_result['avg_time']
                search_results['comparison'][query] = {
                    'api_avg_time': api_result['avg_time'],
                    'inmemory_avg_time': inmemory_result['avg_time'],
                    'speedup': speedup
                }
                print(f"  - Ускорение: {speedup:.2f}x")
            else:
                search_results['comparison'][query] = {
                    'api_avg_time': api_result['avg_time'],
                    'inmemory_avg_time': inmemory_result['avg_time'],
                    'speedup': 'N/A'
                }
                print("  - Невозможно вычислить ускорение: деление на ноль")
        
        return search_results
    
    def run_get_document_benchmarks(self, paths: List[str], iterations: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Запускает бенчмарки получения документов для обоих методов.
        
        Args:
            paths: Список путей к документам
            iterations: Количество повторений
            
        Returns:
            Словарь с результатами бенчмарков
        """
        get_doc_results = {
            'api': {},
            'inmemory': {},
            'comparison': {}
        }
        
        for path in paths:
            print(f"\nБенчмаркинг получения документа: '{path}'")
            
            # Тестируем API
            api_result = self.bench_api_get_document(path, iterations)
            get_doc_results['api'][path] = api_result
            
            # Тестируем in-memory
            inmemory_result = self.bench_inmemory_get_document(path, iterations)
            get_doc_results['inmemory'][path] = inmemory_result
            
            # Сравниваем результаты
            if api_result['avg_time'] > 0:
                speedup = api_result['avg_time'] / inmemory_result['avg_time']
                get_doc_results['comparison'][path] = {
                    'api_avg_time': api_result['avg_time'],
                    'inmemory_avg_time': inmemory_result['avg_time'],
                    'speedup': speedup
                }
                print(f"  - Ускорение: {speedup:.2f}x")
            else:
                get_doc_results['comparison'][path] = {
                    'api_avg_time': api_result['avg_time'],
                    'inmemory_avg_time': inmemory_result['avg_time'],
                    'speedup': 'N/A'
                }
                print("  - Невозможно вычислить ускорение: деление на ноль")
        
        return get_doc_results
    
    def run_all_benchmarks(self):
        """Запускает все бенчмарки и сохраняет результаты."""
        print("Запуск всех бенчмарков...")
        
        # Тестовые запросы
        search_queries = [
            "standard",
            "incident",
            "task master",
            "alarm AND ai",
            "илья красинский",
            "[alarm]"
        ]
        
        # Тестовые пути к документам
        doc_paths = [
            "[todo · incidents]/todo.md",
            "[todo · incidents]/todo.archive.md",
            "[todo · incidents]/ai.incidents.md",
            "[standards .md]/0. core standards/0.0 task master 10 may 2226 cet by ilya krasinsky.md",
            "[standards .md]/1. process · goalmap · task · incidents · tickets · qa/1.1 ai incident standard 14 may 2025 0505 cet by ai assistant.md"
        ]
        
        # Запускаем бенчмарки поиска
        print("\n--- Benchmarking Search ---")
        search_results = self.run_search_benchmarks(search_queries, iterations=5)
        self.results['search'] = search_results
        
        # Запускаем бенчмарки получения документов
        print("\n--- Benchmarking Get Document ---")
        get_doc_results = self.run_get_document_benchmarks(doc_paths, iterations=5)
        self.results['get_document'] = get_doc_results
        
        # Генерируем отчет
        self.generate_report()
    
    def generate_report(self) -> str:
        """
        Генерирует отчет о результатах бенчмарков.
        
        Returns:
            Строка с отчетом в формате Markdown
        """
        print("\nГенерация отчета о производительности...")
        
        report = "# Отчет о производительности in-memory индексатора\n\n"
        report += f"Дата: {time.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        report += "## Статистика индексатора\n\n"
        stats = self.indexer.get_statistics()
        report += f"- Всего документов: {stats['total_documents']}\n"
        report += f"- Типы документов: {stats['document_types']}\n"
        report += f"- Всего задач: {stats['total_tasks']}\n"
        report += f"- Всего инцидентов: {stats['total_incidents']}\n"
        report += f"- Логических ID: {stats['logical_ids']}\n"
        report += f"- Проиндексированных слов: {stats['indexed_words']}\n"
        
        report += "\n## Результаты поиска\n\n"
        report += "| Запрос | API (сек) | In-Memory (сек) | Ускорение |\n"
        report += "|--------|-----------|-----------------|------------|\n"
        
        for query, result in self.results['search']['comparison'].items():
            api_time = f"{result['api_avg_time']:.6f}" if isinstance(result['api_avg_time'], (int, float)) else result['api_avg_time']
            inmemory_time = f"{result['inmemory_avg_time']:.6f}" if isinstance(result['inmemory_avg_time'], (int, float)) else result['inmemory_avg_time']
            speedup = f"{result['speedup']:.2f}x" if isinstance(result['speedup'], (int, float)) else result['speedup']
            report += f"| {query} | {api_time} | {inmemory_time} | {speedup} |\n"
        
        report += "\n## Результаты получения документов\n\n"
        report += "| Документ | API (сек) | In-Memory (сек) | Ускорение |\n"
        report += "|----------|-----------|-----------------|------------|\n"
        
        for path, result in self.results['get_document']['comparison'].items():
            api_time = f"{result['api_avg_time']:.6f}" if isinstance(result['api_avg_time'], (int, float)) else result['api_avg_time']
            inmemory_time = f"{result['inmemory_avg_time']:.6f}" if isinstance(result['inmemory_avg_time'], (int, float)) else result['inmemory_avg_time']
            speedup = f"{result['speedup']:.2f}x" if isinstance(result['speedup'], (int, float)) else result['speedup']
            report += f"| {path} | {api_time} | {inmemory_time} | {speedup} |\n"
        
        report += "\n## Выводы\n\n"
        
        # Вычисляем среднее ускорение
        search_speedups = [result['speedup'] for result in self.results['search']['comparison'].values() 
                         if isinstance(result['speedup'], (int, float))]
        doc_speedups = [result['speedup'] for result in self.results['get_document']['comparison'].values() 
                       if isinstance(result['speedup'], (int, float))]
        
        all_speedups = search_speedups + doc_speedups
        
        if all_speedups:
            avg_speedup = sum(all_speedups) / len(all_speedups)
            max_speedup = max(all_speedups)
            min_speedup = min(all_speedups)
            
            report += f"- Среднее ускорение: **{avg_speedup:.2f}x**\n"
            report += f"- Максимальное ускорение: **{max_speedup:.2f}x**\n"
            report += f"- Минимальное ускорение: **{min_speedup:.2f}x**\n"
            
            if avg_speedup >= 10:
                report += "\nIn-memory индексатор обеспечивает **значительное ускорение** (более 10x) по сравнению с существующим API. "
                report += "Это позволяет существенно повысить отзывчивость системы при работе с большими документами.\n"
            elif avg_speedup >= 5:
                report += "\nIn-memory индексатор обеспечивает **хорошее ускорение** (5-10x) по сравнению с существующим API. "
                report += "Это заметно улучшает производительность системы при работе с документами.\n"
            else:
                report += "\nIn-memory индексатор обеспечивает **умеренное ускорение** по сравнению с существующим API. "
                report += "Дальнейшая оптимизация может быть необходима для достижения целевого ускорения 10-100x.\n"
        else:
            report += "Невозможно вычислить среднее ускорение из-за отсутствия данных.\n"
        
        # Сохраняем отчет в файл
        report_path = "benchmarks_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Отчет сохранен в файле: {report_path}")
        
        return report

def main():
    """Основная функция скрипта."""
    print("Запуск бенчмаркинга in-memory индексатора...")
    
    # Директории для индексации
    directories = [
        ".",
        "[standards .md]",
        "[todo · incidents]",
    ]
    
    # Создаем экземпляр класса BenchmarkRunner
    runner = BenchmarkRunner()
    
    # Подготавливаем данные
    runner.prepare_data(directories)
    
    # Запускаем все бенчмарки
    runner.run_all_benchmarks()
    
    print("\nБенчмаркинг завершен.")

if __name__ == "__main__":
    main()