#!/usr/bin/env python3
"""
Модуль для сбора и отображения статистики по задачам.
Предоставляет функции для отслеживания прогресса выполнения и визуализации данных.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("advising_platform.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("task_statistics")

# Константы
TODO_FILE = "todo.md"
STATS_FILE = ".task_stats.json"
COMPLETED_TASK_MARKER = "- [x]"
PENDING_TASK_MARKER = "- [ ]"

class TaskStatisticsManager:
    """Менеджер статистики задач для отслеживания и анализа прогресса."""
    
    def __init__(self, todo_file: str = TODO_FILE, stats_file: str = STATS_FILE):
        """
        Инициализация менеджера статистики задач.
        
        Args:
            todo_file: Путь к файлу со списком задач
            stats_file: Путь к файлу со статистикой
        """
        self.todo_file = todo_file
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """
        Загружает статистику из файла.
        
        Returns:
            Dict[str, Any]: Статистика по задачам
        """
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка при загрузке статистики: {e}")
        
        # Если файл не существует или произошла ошибка, возвращаем структуру по умолчанию
        return {
            "last_update": datetime.now().isoformat(),
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate": 0,
            "categories": {},
            "history": [],
            "recently_completed": []
        }
    
    def _save_stats(self) -> bool:
        """
        Сохраняет статистику в файл.
        
        Returns:
            bool: True в случае успеха, иначе False
        """
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении статистики: {e}")
            return False
    
    def update_statistics(self) -> Dict[str, Any]:
        """
        Обновляет статистику на основе текущего состояния задач.
        
        Returns:
            Dict[str, Any]: Обновленная статистика
        """
        if not os.path.exists(self.todo_file):
            logger.error(f"Файл {self.todo_file} не найден")
            return self.stats
        
        try:
            # Загружаем содержимое файла задач
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Анализируем содержимое
            completed_tasks = []
            pending_tasks = []
            categories = {}
            
            # Ищем задачи в формате "- [x] Текст задачи" или "- [ ] Текст задачи"
            for line in content.split('\n'):
                if line.strip().startswith(COMPLETED_TASK_MARKER):
                    task_text = line.strip()[len(COMPLETED_TASK_MARKER):].strip()
                    completed_tasks.append(task_text)
                    
                    # Определяем категорию
                    category = self._extract_category(line)
                    if category:
                        if category not in categories:
                            categories[category] = {"total": 0, "completed": 0, "pending": 0}
                        categories[category]["total"] += 1
                        categories[category]["completed"] += 1
                
                elif line.strip().startswith(PENDING_TASK_MARKER):
                    task_text = line.strip()[len(PENDING_TASK_MARKER):].strip()
                    pending_tasks.append(task_text)
                    
                    # Определяем категорию
                    category = self._extract_category(line)
                    if category:
                        if category not in categories:
                            categories[category] = {"total": 0, "completed": 0, "pending": 0}
                        categories[category]["total"] += 1
                        categories[category]["pending"] += 1
            
            # Получаем текущее время
            now = datetime.now()
            
            # Формируем обновленную статистику
            total_tasks = len(completed_tasks) + len(pending_tasks)
            completion_rate = 0 if total_tasks == 0 else (len(completed_tasks) / total_tasks) * 100
            
            # Находим новые выполненные задачи
            new_completed = []
            for task in completed_tasks:
                if task not in [entry["task"] for entry in self.stats.get("recently_completed", [])]:
                    new_completed.append({
                        "task": task,
                        "completed_at": now.isoformat()
                    })
            
            # Ограничиваем список недавно выполненных задач
            recently_completed = new_completed + self.stats.get("recently_completed", [])
            recently_completed = recently_completed[:20]  # Хранить только 20 последних
            
            # Обновляем историю
            history_entry = {
                "timestamp": now.isoformat(),
                "total_tasks": total_tasks,
                "completed_tasks": len(completed_tasks),
                "pending_tasks": len(pending_tasks),
                "completion_rate": completion_rate
            }
            
            history = self.stats.get("history", [])
            history.append(history_entry)
            
            # Оставляем историю только за последние 30 дней
            cutoff_date = (now - timedelta(days=30)).isoformat()
            history = [entry for entry in history if entry["timestamp"] >= cutoff_date]
            
            # Формируем обновленную статистику
            self.stats = {
                "last_update": now.isoformat(),
                "total_tasks": total_tasks,
                "completed_tasks": len(completed_tasks),
                "pending_tasks": len(pending_tasks),
                "completion_rate": completion_rate,
                "categories": categories,
                "history": history,
                "recently_completed": recently_completed
            }
            
            # Сохраняем статистику
            self._save_stats()
            
            logger.info(f"Статистика обновлена: {len(completed_tasks)} выполненных, {len(pending_tasks)} ожидающих, {completion_rate:.1f}% выполнено")
            
            return self.stats
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении статистики: {e}")
            return self.stats
    
    def _extract_category(self, task_line: str) -> Optional[str]:
        """
        Извлекает категорию задачи из строки.
        
        Args:
            task_line: Строка с задачей
            
        Returns:
            Optional[str]: Категория задачи или None, если не удалось определить
        """
        # Пытаемся извлечь категорию из тегов [Категория]
        category_match = re.search(r'\[([^\]]+)\]', task_line)
        if category_match:
            return category_match.group(1)
        
        return None
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        Возвращает сводку статистики по задачам.
        
        Returns:
            Dict[str, Any]: Сводка статистики
        """
        # Обновляем статистику перед формированием сводки
        self.update_statistics()
        
        # Вычисляем тренды
        trend_data = self._calculate_trends()
        
        # Формируем сводку
        summary = {
            "last_update": self.stats["last_update"],
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "pending_tasks": self.stats["pending_tasks"],
            "completion_rate": self.stats["completion_rate"],
            "recently_completed": self.stats["recently_completed"][:5],  # Только 5 последних
            "categories": self._get_top_categories(5),  # Топ-5 категорий
            "trends": trend_data
        }
        
        return summary
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """
        Вычисляет тренды на основе исторических данных.
        
        Returns:
            Dict[str, Any]: Данные о трендах
        """
        history = self.stats.get("history", [])
        if not history or len(history) < 2:
            return {
                "completion_trend": 0,
                "task_count_trend": 0
            }
        
        # Берем последние записи для расчета тренда за последнюю неделю
        now = datetime.now()
        week_ago = (now - timedelta(days=7)).isoformat()
        
        # Получаем записи за последнюю неделю
        recent_entries = [entry for entry in history if entry["timestamp"] >= week_ago]
        
        if not recent_entries:
            return {
                "completion_trend": 0,
                "task_count_trend": 0
            }
        
        # Вычисляем изменение процента выполнения
        first_entry = recent_entries[0]
        last_entry = recent_entries[-1]
        
        completion_trend = last_entry["completion_rate"] - first_entry["completion_rate"]
        task_count_trend = last_entry["total_tasks"] - first_entry["total_tasks"]
        
        return {
            "completion_trend": completion_trend,
            "task_count_trend": task_count_trend
        }
    
    def _get_top_categories(self, limit: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает топ категорий по количеству задач.
        
        Args:
            limit: Количество категорий для возврата
            
        Returns:
            Dict[str, Dict[str, Any]]: Топ категорий
        """
        categories = self.stats.get("categories", {})
        
        # Сортируем категории по общему количеству задач
        sorted_categories = sorted(
            categories.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        
        # Возвращаем топ категорий
        return {
            name: data for name, data in sorted_categories[:limit]
        }
    
    def generate_html_report(self, output_file: str = "task_stats_report.html") -> str:
        """
        Генерирует HTML-отчет по статистике задач.
        
        Args:
            output_file: Путь к выходному файлу
            
        Returns:
            str: Путь к сгенерированному файлу
        """
        try:
            # Обновляем статистику
            self.update_statistics()
            
            # Получаем данные для отчета
            stats_summary = self.get_statistics_summary()
            
            # Формируем HTML-отчет
            html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Статистика по задачам</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; }}
        .summary-cards {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }}
        .card {{ background-color: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; min-width: 200px; }}
        .card-title {{ font-size: 16px; color: #666; margin-bottom: 10px; }}
        .card-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .trend-positive {{ color: green; }}
        .trend-negative {{ color: red; }}
        .trend-neutral {{ color: gray; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .progress-bar {{ height: 20px; background-color: #e0e0e0; border-radius: 10px; overflow: hidden; margin-top: 5px; }}
        .progress {{ height: 100%; background-color: #4CAF50; border-radius: 10px; }}
        .updated-at {{ color: #666; font-size: 14px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Статистика по задачам</h1>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-title">Всего задач</div>
                <div class="card-value">{stats_summary['total_tasks']}</div>
                <div class="trend-{self._get_trend_class(stats_summary['trends']['task_count_trend'])}">
                    {self._format_trend(stats_summary['trends']['task_count_trend'])}
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Выполнено задач</div>
                <div class="card-value">{stats_summary['completed_tasks']}</div>
            </div>
            
            <div class="card">
                <div class="card-title">В работе</div>
                <div class="card-value">{stats_summary['pending_tasks']}</div>
            </div>
            
            <div class="card">
                <div class="card-title">Процент выполнения</div>
                <div class="card-value">{stats_summary['completion_rate']:.1f}%</div>
                <div class="trend-{self._get_trend_class(stats_summary['trends']['completion_trend'])}">
                    {self._format_trend(stats_summary['trends']['completion_trend'], is_percent=True)}
                </div>
                <div class="progress-bar">
                    <div class="progress" style="width: {stats_summary['completion_rate']}%;"></div>
                </div>
            </div>
        </div>
        
        <h2>Недавно выполненные задачи</h2>
        <table>
            <thead>
                <tr>
                    <th>Задача</th>
                    <th>Дата выполнения</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for task in stats_summary['recently_completed']:
                completed_at = datetime.fromisoformat(task['completed_at']).strftime("%d.%m.%Y %H:%M")
                html_content += f"""
                <tr>
                    <td>{task['task']}</td>
                    <td>{completed_at}</td>
                </tr>"""
            
            html_content += """
            </tbody>
        </table>
        
        <h2>Статистика по категориям</h2>
        <table>
            <thead>
                <tr>
                    <th>Категория</th>
                    <th>Всего задач</th>
                    <th>Выполнено</th>
                    <th>В работе</th>
                    <th>Прогресс</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for category, data in stats_summary['categories'].items():
                completion_percent = 0 if data["total"] == 0 else (data["completed"] / data["total"]) * 100
                html_content += f"""
                <tr>
                    <td>{category}</td>
                    <td>{data['total']}</td>
                    <td>{data['completed']}</td>
                    <td>{data['pending']}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress" style="width: {completion_percent}%;"></div>
                        </div>
                    </td>
                </tr>"""
            
            # Форматируем дату последнего обновления
            last_update = datetime.fromisoformat(stats_summary['last_update']).strftime("%d.%m.%Y %H:%M:%S")
            
            html_content += f"""
            </tbody>
        </table>
        
        <div class="updated-at">Последнее обновление: {last_update}</div>
    </div>
</body>
</html>
"""
            
            # Сохраняем отчет в файл
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML-отчет по статистике задач сохранен в {output_file}")
            
            return output_file
        
        except Exception as e:
            logger.error(f"Ошибка при генерации HTML-отчета: {e}")
            return ""
    
    def _get_trend_class(self, value: float) -> str:
        """
        Возвращает класс для отображения тренда.
        
        Args:
            value: Значение тренда
            
        Returns:
            str: Класс для отображения тренда
        """
        if abs(value) < 0.5:
            return "neutral"
        return "positive" if value > 0 else "negative"
    
    def _format_trend(self, value: float, is_percent: bool = False) -> str:
        """
        Форматирует значение тренда для отображения.
        
        Args:
            value: Значение тренда
            is_percent: Является ли значение процентом
            
        Returns:
            str: Отформатированное значение тренда
        """
        if abs(value) < 0.5:
            return "Без изменений"
        
        sign = "+" if value > 0 else ""
        if is_percent:
            return f"{sign}{value:.1f}%"
        else:
            return f"{sign}{int(value)}"

    def update_task_status_in_todo(self, task_description: str, completed: bool = True) -> bool:
        """
        Обновляет статус задачи в файле todo.md.
        
        Args:
            task_description: Описание задачи для поиска
            completed: True для отметки задачи как выполненной, False для отметки как невыполненной
            
        Returns:
            bool: True в случае успеха, иначе False
        """
        if not os.path.exists(self.todo_file):
            logger.error(f"Файл {self.todo_file} не найден")
            return False
        
        try:
            # Загружаем содержимое файла задач
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            task_found = False
            new_lines = []
            
            for line in lines:
                # Ищем строку, содержащую описание задачи
                if task_description in line:
                    # Определяем, является ли задача отмеченной или нет
                    is_completed = line.strip().startswith(COMPLETED_TASK_MARKER)
                    
                    # Если статус задачи уже соответствует нужному, не меняем его
                    if completed == is_completed:
                        new_lines.append(line)
                        task_found = True
                        continue
                    
                    # Меняем статус задачи
                    if completed:
                        # Отмечаем задачу как выполненную
                        new_line = line.replace(PENDING_TASK_MARKER, COMPLETED_TASK_MARKER, 1)
                    else:
                        # Отмечаем задачу как невыполненную
                        new_line = line.replace(COMPLETED_TASK_MARKER, PENDING_TASK_MARKER, 1)
                    
                    new_lines.append(new_line)
                    task_found = True
                else:
                    new_lines.append(line)
            
            # Если задача не найдена, возвращаем False
            if not task_found:
                logger.warning(f"Задача '{task_description}' не найдена в файле {self.todo_file}")
                return False
            
            # Записываем обновленное содержимое
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            # Обновляем статистику
            self.update_statistics()
            
            logger.info(f"Задача '{task_description}' отмечена как {('выполненная' if completed else 'невыполненная')}")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса задачи: {e}")
            return False

def main():
    """Основная функция модуля."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Управление статистикой задач')
    parser.add_argument('--update', action='store_true', help='Обновить статистику задач')
    parser.add_argument('--report', action='store_true', help='Сгенерировать HTML-отчет')
    parser.add_argument('--output', default='task_stats_report.html', help='Путь к выходному файлу отчета')
    parser.add_argument('--complete', help='Отметить задачу как выполненную')
    parser.add_argument('--reopen', help='Отметить задачу как невыполненную')
    
    args = parser.parse_args()
    
    # Создаем менеджер статистики
    stats_manager = TaskStatisticsManager()
    
    if args.update:
        # Обновляем статистику
        stats = stats_manager.update_statistics()
        print(f"Статистика обновлена: {stats['completed_tasks']} выполненных, {stats['pending_tasks']} ожидающих, {stats['completion_rate']:.1f}% выполнено")
    
    if args.report:
        # Генерируем отчет
        report_file = stats_manager.generate_html_report(args.output)
        if report_file:
            print(f"Отчет сгенерирован: {report_file}")
    
    if args.complete:
        # Отмечаем задачу как выполненную
        success = stats_manager.update_task_status_in_todo(args.complete, True)
        if success:
            print(f"Задача '{args.complete}' отмечена как выполненная")
        else:
            print(f"Не удалось отметить задачу '{args.complete}' как выполненную")
    
    if args.reopen:
        # Отмечаем задачу как невыполненную
        success = stats_manager.update_task_status_in_todo(args.reopen, False)
        if success:
            print(f"Задача '{args.reopen}' отмечена как невыполненная")
        else:
            print(f"Не удалось отметить задачу '{args.reopen}' как невыполненную")
    
    # Если не указаны аргументы, выводим справку
    if not (args.update or args.report or args.complete or args.reopen):
        parser.print_help()

if __name__ == "__main__":
    main()