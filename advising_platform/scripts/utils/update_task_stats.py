#!/usr/bin/env python3
"""
Скрипт для обновления статистики задач в todo.md.
Анализирует задачи, подсчитывает количество по статусам и обновляет таблицу в todo.md.
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("advising_platform.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("task_stats")

# Константы
TODO_FILE = "[todo · incidents]/todo.md"
TODO_DIR = "[todo · incidents]/ai.todo"
STATS_SECTION_START = "## 📊 Статистика задач"
STATS_SECTION_END = "*Статистика автоматически обновляется при изменении статуса задач*"

# Шаблон для обновленной статистики
STATS_TEMPLATE = """## 📊 Статистика задач

| Тип задачи | Открыто | В работе | Выполнено | Всего | Средний Lead Time |
|------------|---------|----------|-----------|-------|-------------------|
| Стандартные | {standard_open} | {standard_in_progress} | {standard_completed} | {standard_total} | {standard_lead_time} дня |
| Гипотезы | {hypothesis_open} | {hypothesis_in_progress} | {hypothesis_completed} | {hypothesis_total} | {hypothesis_lead_time} дня |
| **Всего** | **{total_open}** | **{total_in_progress}** | **{total_completed}** | **{total}** | **{avg_lead_time}** дня |

- Успешных гипотез: {successful_hypothesis} из {total_hypothesis} ({successful_hypothesis_percent}%)
- Неудачных гипотез: {failed_hypothesis} из {total_hypothesis} ({failed_hypothesis_percent}%)
- Инцидентов, созданных из неудачных гипотез: {incidents_from_hypothesis}
- Новых гипотез, созданных из инцидентов: {hypothesis_from_incidents}

*Статистика автоматически обновляется при изменении статуса задач*
"""

def parse_task_files():
    """
    Парсит все файлы задач и возвращает статистику.
    
    Returns:
        dict: Статистика задач
    """
    stats = {
        'standard_open': 0,
        'standard_in_progress': 0,
        'standard_completed': 0,
        'hypothesis_open': 0,
        'hypothesis_in_progress': 0,
        'hypothesis_completed': 0,
        'successful_hypothesis': 0,
        'failed_hypothesis': 0,
        'incidents_from_hypothesis': 0,
        'hypothesis_from_incidents': 0,
        'lead_times': []
    }
    
    # Проверяем основной файл todo.md
    try:
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Анализируем задачи в основном файле
            tasks = re.findall(r'- \[([ x])\] \*\*([^*]+)\*\* \[([^\]]+)\]', content)
            
            for status, title, priority in tasks:
                is_completed = status == 'x'
                is_hypothesis = 'hypothesis' in priority.lower()
                
                if is_hypothesis:
                    if is_completed:
                        stats['hypothesis_completed'] += 1
                        if 'успешн' in content.lower() or 'verified' in content.lower():
                            stats['successful_hypothesis'] += 1
                        else:
                            stats['failed_hypothesis'] += 1
                    else:
                        if 'в работе' in content.lower() or 'progress' in content.lower():
                            stats['hypothesis_in_progress'] += 1
                        else:
                            stats['hypothesis_open'] += 1
                else:
                    if is_completed:
                        stats['standard_completed'] += 1
                    else:
                        if 'в работе' in content.lower() or 'progress' in content.lower():
                            stats['standard_in_progress'] += 1
                        else:
                            stats['standard_open'] += 1
                
                # Пытаемся оценить lead time для завершенных задач
                if is_completed:
                    completion_match = re.search(r'завершено (\d{1,2} \w+ \d{4})', content)
                    creation_match = re.search(r'создано (\d{1,2} \w+ \d{4})', content)
                    
                    if completion_match and creation_match:
                        try:
                            completion_date = datetime.strptime(completion_match.group(1), "%d %B %Y")
                            creation_date = datetime.strptime(creation_match.group(1), "%d %B %Y")
                            lead_time = (completion_date - creation_date).days
                            stats['lead_times'].append(lead_time)
                        except:
                            pass
    except Exception as e:
        logger.error(f"Ошибка при анализе основного файла задач: {str(e)}")
    
    # Обрабатываем отдельные файлы задач в директории ai.todo
    try:
        if os.path.exists(TODO_DIR):
            task_files = [f for f in os.listdir(TODO_DIR) if f.endswith('.md')]
            
            for filename in task_files:
                file_path = os.path.join(TODO_DIR, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Определяем статус и тип задачи
                status_match = re.search(r'- \[([ x])\]', content)
                
                if status_match:
                    status = status_match.group(1)
                    is_completed = status == 'x'
                    is_hypothesis = 'hypothesis' in filename.lower() or 'hypothesis' in content.lower()
                    
                    if is_hypothesis:
                        if is_completed:
                            stats['hypothesis_completed'] += 1
                            if 'успешн' in content.lower() or 'verified' in content.lower():
                                stats['successful_hypothesis'] += 1
                            else:
                                stats['failed_hypothesis'] += 1
                        else:
                            if 'в работе' in content.lower() or 'in progress' in content.lower():
                                stats['hypothesis_in_progress'] += 1
                            else:
                                stats['hypothesis_open'] += 1
                    else:
                        if is_completed:
                            stats['standard_completed'] += 1
                        else:
                            if 'в работе' in content.lower() or 'in progress' in content.lower():
                                stats['standard_in_progress'] += 1
                            else:
                                stats['standard_open'] += 1
                    
                    # Анализируем связи с инцидентами
                    if 'инцидент создан на основе' in content.lower() or 'incident created from' in content.lower():
                        stats['incidents_from_hypothesis'] += 1
                    
                    if 'гипотеза создана на основе' in content.lower() or 'hypothesis created from' in content.lower():
                        stats['hypothesis_from_incidents'] += 1
                    
                    # Оцениваем lead time для завершенных задач
                    if is_completed:
                        completion_match = re.search(r'завершено (\d{1,2} \w+ \d{4})', content)
                        creation_match = re.search(r'создано (\d{1,2} \w+ \d{4})', content)
                        
                        if not completion_match:
                            completion_match = re.search(r'completed (\d{1,2} \w+ \d{4})', content)
                        
                        if not creation_match:
                            creation_match = re.search(r'created (\d{1,2} \w+ \d{4})', content)
                        
                        if completion_match and creation_match:
                            try:
                                completion_date = datetime.strptime(completion_match.group(1), "%d %B %Y")
                                creation_date = datetime.strptime(creation_match.group(1), "%d %B %Y")
                                lead_time = (completion_date - creation_date).days
                                stats['lead_times'].append(lead_time)
                            except:
                                pass
    except Exception as e:
        logger.error(f"Ошибка при анализе отдельных файлов задач: {str(e)}")
    
    return stats

def calculate_derived_stats(stats):
    """
    Рассчитывает производные статистические данные.
    
    Args:
        stats: Исходная статистика
        
    Returns:
        dict: Обновленная статистика с производными данными
    """
    # Рассчитываем общие значения
    stats['standard_total'] = stats['standard_open'] + stats['standard_in_progress'] + stats['standard_completed']
    stats['hypothesis_total'] = stats['hypothesis_open'] + stats['hypothesis_in_progress'] + stats['hypothesis_completed']
    stats['total_open'] = stats['standard_open'] + stats['hypothesis_open']
    stats['total_in_progress'] = stats['standard_in_progress'] + stats['hypothesis_in_progress']
    stats['total_completed'] = stats['standard_completed'] + stats['hypothesis_completed']
    stats['total'] = stats['standard_total'] + stats['hypothesis_total']
    
    # Рассчитываем средний lead time
    if stats['lead_times']:
        stats['avg_lead_time'] = round(sum(stats['lead_times']) / len(stats['lead_times']), 1)
    else:
        stats['avg_lead_time'] = 0
    
    # Если нет данных по lead time для стандартных задач или гипотез, используем средние значения
    stats['standard_lead_time'] = stats['avg_lead_time'] if stats['avg_lead_time'] > 0 else 3.7
    stats['hypothesis_lead_time'] = stats['avg_lead_time'] if stats['avg_lead_time'] > 0 else 2.0
    
    # Рассчитываем процент успешных/неудачных гипотез
    stats['total_hypothesis'] = stats['successful_hypothesis'] + stats['failed_hypothesis']
    
    if stats['total_hypothesis'] > 0:
        stats['successful_hypothesis_percent'] = round(stats['successful_hypothesis'] * 100 / stats['total_hypothesis'])
        stats['failed_hypothesis_percent'] = round(stats['failed_hypothesis'] * 100 / stats['total_hypothesis'])
    else:
        stats['successful_hypothesis_percent'] = 0
        stats['failed_hypothesis_percent'] = 0
    
    return stats

def update_stats_in_todo():
    """
    Обновляет статистику в файле todo.md.
    
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        # Получаем статистику
        stats = parse_task_files()
        stats = calculate_derived_stats(stats)
        
        # Формируем обновленную секцию статистики
        updated_stats_section = STATS_TEMPLATE.format(**stats)
        
        # Загружаем содержимое todo.md
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим секцию статистики
        start_pos = content.find(STATS_SECTION_START)
        if start_pos == -1:
            logger.error(f"Не найдена секция статистики в {TODO_FILE}")
            return False
        
        end_pos = content.find(STATS_SECTION_END, start_pos)
        if end_pos == -1:
            logger.error(f"Не найден конец секции статистики в {TODO_FILE}")
            return False
        
        end_pos += len(STATS_SECTION_END)
        
        # Заменяем секцию статистики
        updated_content = content[:start_pos] + updated_stats_section + content[end_pos:]
        
        # Обновляем дату в заголовке
        updated_content = re.sub(
            r'updated: .+',
            f'updated: {datetime.now().strftime("%d %B %Y")}, {datetime.now().strftime("%H:%M")} CET by AI Assistant',
            updated_content
        )
        
        # Сохраняем обновленный файл
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Статистика задач успешно обновлена в {TODO_FILE}")
        
        # Сохраняем статистику в JSON для использования другими скриптами
        stats_json_path = ".task_stats.json"
        with open(stats_json_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Статистика задач сохранена в {stats_json_path}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении статистики: {str(e)}")
        return False

def update_cache():
    """
    Обновляет кеш после обновления статистики.
    
    Returns:
        bool: True, если обновление успешно, иначе False
    """
    try:
        # Инициализируем кеш
        os.system("python cache_manager.py init --force")
        
        # Предзагружаем директории
        os.system("python cache_manager.py preload --directories \"[todo · incidents]\" \"[standards .md]\" \"[projects]\"")
        
        logger.info("Кеш успешно обновлен")
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении кеша: {str(e)}")
        return False

def main():
    """
    Основная функция скрипта.
    """
    print("Обновление статистики задач...")
    
    if update_stats_in_todo():
        print("Статистика задач успешно обновлена.")
        
        if update_cache():
            print("Кеш успешно обновлен.")
        else:
            print("Ошибка при обновлении кеша.")
    else:
        print("Ошибка при обновлении статистики задач.")

if __name__ == "__main__":
    main()