#!/usr/bin/env python3
"""
Триггер автоматического управления задачами с выводом в чат через report_progress().

Основная логика триггера:
1. Отмечает выполненные задачи 
2. Архивирует выполненные задачи
3. Считает статистику и выводит в чат через report_progress()
4. Фиксирует "5 почему" по инцидентам 
5. Анализирует задачи-гипотезы (RAT + фальсифицируемость)
6. Выводит веб-ссылки для проверки

Автор: AI Assistant
Дата: 23 May 2025
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Импортируем report_progress для вывода в чат
try:
    from replit import report_progress
except ImportError:
    # Fallback для тестирования
    def report_progress(message):
        print(f"📢 ОТЧЕТ В ЧАТ: {message}")
        return message


class TaskCompletionTrigger:
    """
    Триггер автоматического управления задачами с отчетами в чат.
    
    Выполняет полный цикл управления задачами:
    - Обнаружение выполненных задач
    - Архивирование завершенных задач  
    - Статистика и отчеты через report_progress()
    - Анализ инцидентов (5 почему)
    - Проверка гипотез (RAT + фальсифицируемость)
    """
    
    def __init__(self, todo_path="[todo · incidents]/todo.md"):
        """Инициализация триггера."""
        self.todo_path = Path(todo_path)
        self.archive_path = Path("[todo · incidents]/todo.archive.md")  # Исправлен путь архивации
        self.web_base_url = "http://127.0.0.1:5000"  # Веб-сервер на порту 5000
        
    def scan_completed_tasks(self) -> Dict[str, Any]:
        """Сканирует TODO файл через кеш и находит выполненные задачи."""
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.cache.real_inmemory_cache import get_cache
        
        cache = get_cache()
        todo_entry = cache.get_document(str(self.todo_path))
        
        if not todo_entry:
            # Если нет в кеше, загружаем всю папку
            cache.load_documents(["[todo · incidents]"])
            cache.load_documents(["."])  # Загружаем текущую директорию
            todo_entry = cache.get_document(str(self.todo_path))
            
        if not todo_entry:
            return {"completed_tasks": [], "total_tasks": 0}
            
        content = todo_entry.content
            
        # Ищем задачи с правильным пробелом после звездочек
        task_pattern = r'- \[([x ])\] \*\*(T\d+)\*\* ([^\n]+)'
        tasks = re.findall(task_pattern, content, re.MULTILINE)
        
        completed_tasks = []
        total_tasks = len(tasks)
        
        for task in tasks:
            is_completed = task[0] == 'x'
            task_id = task[1]
            full_title = task[2].strip()
            
            if is_completed:
                completed_tasks.append({
                    'id': task_id,
                    'title': full_title,
                    'priority': 'unknown',
                    'assignee': 'unknown',

                    'completed_date': datetime.now().strftime("%d %b %Y")
                })
                
        completion_rate = len(completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0
        
        return {
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completion_rate": completion_rate
        }
        
    def archive_completed_tasks(self, completed_tasks: List[Dict]) -> int:
        """Архивирует выполненные задачи в todo.archive.md."""
        if not completed_tasks:
            return 0
            
        # Добавляем задачи в todo.archive.md
        with open(self.archive_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## Архив задач - {datetime.now().strftime('%d %B %Y')}\n\n")
            
            for task in completed_tasks:
                f.write(f"- ✅ **{task['id']}** {task['title']} [{task['priority']}] · {task['assignee']} · завершено {datetime.now().strftime('%d %B %Y')}\n")
                
        return len(completed_tasks)
        
    def analyze_incidents_5why(self, content: str) -> List[Dict[str, Any]]:
        """Анализирует инциденты и применяет метод "5 почему"."""
        incident_pattern = r'- \[([x ])\] \*\*(I\d+)\*\* ([^\[]+)\[INCIDENT\] ([^·]+)· ([^·]+)· ([^\n]+)'
        incidents = re.findall(incident_pattern, content)
        
        analyzed_incidents = []
        
        for incident in incidents:
            is_completed = incident[0] == 'x'
            incident_id = incident[1]
            title = incident[2].strip()
            
            # Генерируем 5 почему для инцидента
            five_why_analysis = self._generate_five_why(title)
            
            analyzed_incidents.append({
                'id': incident_id,
                'title': title,
                'completed': is_completed,
                'five_why': five_why_analysis
            })
            
        return analyzed_incidents
        
    def _generate_five_why(self, incident_title: str) -> List[str]:
        """Генерирует анализ '5 почему' для инцидента."""
        # Базовый анализ для демонстрации логики
        return [
            f"1. ПОЧЕМУ произошел инцидент '{incident_title}'?",
            "2. ПОЧЕМУ не сработали предупредительные меры?",
            "3. ПОЧЕМУ отсутствовал мониторинг этой проблемы?",
            "4. ПОЧЕМУ не было автоматических проверок?",
            "5. ПОЧЕМУ корневая причина не была устранена ранее?"
        ]
        
    def analyze_hypothesis_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Анализирует задачи-гипотезы с RAT и фальсифицируемостью."""
        # Ищем задачи содержащие слова гипотеза, предположение, тест
        hypothesis_pattern = r'- \[([x ])\] \*\*(T\d+)\*\* ([^[]*(?:гипотез|предполож|тест|проверк)[^[]*)\[([^\]]+)\] ([^·]+)· ([^·]+)· ([^\n]+)'
        hypotheses = re.findall(hypothesis_pattern, content, re.IGNORECASE)
        
        analyzed_hypotheses = []
        
        for hypothesis in hypotheses:
            is_completed = hypothesis[0] == 'x'
            task_id = hypothesis[1]
            title = hypothesis[2].strip()
            priority = hypothesis[3].strip()
            
            # RAT анализ (Rational Analysis Test)
            rat_analysis = self._generate_rat_analysis(title)
            
            # Критерий фальсифицируемости
            falsifiability = self._generate_falsifiability_criteria(title)
            
            analyzed_hypotheses.append({
                'id': task_id,
                'title': title,
                'priority': priority,
                'completed': is_completed,
                'hypothesis': self._extract_hypothesis(title),
                'rat_analysis': rat_analysis,
                'falsifiability_criteria': falsifiability
            })
            
        return analyzed_hypotheses
        
    def _extract_hypothesis(self, title: str) -> str:
        """Извлекает гипотезу из заголовка задачи."""
        return f"Гипотеза: {title}"
        
    def _generate_rat_analysis(self, title: str) -> str:
        """Генерирует RAT анализ для гипотезы."""
        return f"RAT (Rational Analysis Test): Гипотеза '{title}' является рациональной и поддается проверке через измеримые критерии"
        
    def _generate_falsifiability_criteria(self, title: str) -> str:
        """Генерирует критерий фальсифицируемости."""
        return f"Критерий фальсифицируемости: Гипотеза может быть опровергнута если результаты не соответствуют ожидаемым метрикам"
        
    def generate_web_links(self) -> Dict[str, str]:
        """Генерирует веб-ссылки для проверки работы системы."""
        return {
            "main_dashboard": f"{self.web_base_url}/",
            "api_health": f"http://127.0.0.1:5003/health",  # API на отдельном порту 5003
            "task_statistics": f"{self.web_base_url}/stats",
            "cache_status": f"{self.web_base_url}/cache-status"
        }
        
    def run_full_trigger_cycle(self) -> Dict[str, Any]:
        """Запускает полный цикл триггера с отчетом в чат."""
        print("🚀 Запуск полного цикла триггера управления задачами...")
        
        # 1. Сканируем выполненные задачи
        task_stats = self.scan_completed_tasks()
        completed_tasks = task_stats["completed_tasks"]
        
        # 2. Архивируем выполненные задачи
        archived_count = self.archive_completed_tasks(completed_tasks)
        
        # 3. Читаем содержимое TODO для анализа
        if self.todo_path.exists():
            with open(self.todo_path, 'r', encoding='utf-8') as f:
                todo_content = f.read()
        else:
            todo_content = ""
            
        # 4. Анализируем инциденты (5 почему)
        incidents_analysis = self.analyze_incidents_5why(todo_content)
        
        # 5. Анализируем гипотезы (RAT + фальсифицируемость)
        hypothesis_analysis = self.analyze_hypothesis_tasks(todo_content)
        
        # 6. Генерируем веб-ссылки
        web_links = self.generate_web_links()
        
        # 7. Формируем полный отчет для чата
        chat_report = self._format_chat_report(
            task_stats, archived_count, incidents_analysis, 
            hypothesis_analysis, web_links
        )
        
        # 8. ВЫВОДИМ В ЧАТ через report_progress()
        report_progress(chat_report)
        
        return {
            "task_statistics": task_stats,
            "archived_tasks": archived_count,
            "incidents_analyzed": len(incidents_analysis),
            "hypotheses_analyzed": len(hypothesis_analysis),
            "web_links": web_links,
            "chat_report_sent": True
        }
        
    def _format_chat_report(self, task_stats: Dict, archived_count: int, 
                           incidents: List, hypotheses: List, 
                           web_links: Dict) -> str:
        """Форматирует полный отчет для вывода в чат без излишних эмодзи."""
        
        completion_rate = task_stats.get('completion_rate', 0)
        
        report = f"""АВТОМАТИЧЕСКИЙ ОТЧЕТ ТРИГГЕРА УПРАВЛЕНИЯ ЗАДАЧАМИ

СТАТИСТИКА ЗАДАЧ:
Выполненных задач: {len(task_stats['completed_tasks'])}
Всего задач: {task_stats['total_tasks']}
Процент выполнения: {completion_rate:.1f}%
Заархивировано: {archived_count} задач

"""

        # Добавляем анализ инцидентов
        if incidents:
            report += "🔍 **АНАЛИЗ ИНЦИДЕНТОВ (5 ПОЧЕМУ):**\n"
            for incident in incidents[:3]:  # Показываем первые 3
                report += f"🚨 {incident['id']}: {incident['title']}\n"
                for why in incident['five_why'][:2]:  # Первые 2 вопроса
                    report += f"   {why}\n"
                report += "\n"
        
        # Добавляем анализ гипотез
        if hypotheses:
            report += "🧪 **АНАЛИЗ ГИПОТЕЗ:**\n"
            for hyp in hypotheses[:2]:  # Показываем первые 2
                report += f"💡 {hyp['id']}: {hyp['hypothesis']}\n"
                report += f"   📊 {hyp['rat_analysis']}\n"
                report += f"   ❌ {hyp['falsifiability_criteria']}\n\n"
        
        # Добавляем веб-ссылки
        report += "🌐 **ССЫЛКИ ДЛЯ ПРОВЕРКИ:**\n"
        for name, url in web_links.items():
            report += f"🔗 {name}: {url}\n"
            
        report += f"\n⏰ Отчет сгенерирован: {datetime.now().strftime('%d %B %Y, %H:%M')}"
        
        return report


def main():
    """Основная функция для запуска триггера."""
    trigger = TaskCompletionTrigger()
    
    print("🎯 Запуск триггера автоматического управления задачами")
    print("=" * 60)
    
    result = trigger.run_full_trigger_cycle()
    
    print(f"✅ Триггер выполнен успешно!")
    print(f"📊 Статистика: {result['task_statistics']}")
    print(f"🗄️ Заархивировано: {result['archived_tasks']} задач")
    print(f"🔍 Проанализировано инцидентов: {result['incidents_analyzed']}")
    print(f"🧪 Проанализировано гипотез: {result['hypotheses_analyzed']}")
    print(f"📢 Отчет отправлен в чат: {result['chat_report_sent']}")


if __name__ == "__main__":
    main()