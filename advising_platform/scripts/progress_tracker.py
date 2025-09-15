#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Система отслеживания прогресса и достижений в проекте Advising Diagnostics.
Позволяет отслеживать и отмечать прогресс в работе над стандартами и проектами.
"""

import os
import json
import time
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/progress_tracker.log')
    ]
)

logger = logging.getLogger('progress_tracker')

# База данных SQLite для хранения данных о прогрессе и достижениях
DB_PATH = "progress_data.db"

# Определение достижений системы
ACHIEVEMENTS = [
    {
        "id": "founder",
        "name": "Основатель системы",
        "description": "Создан первый стандарт в системе",
        "requirements": {
            "type": "standards_count",
            "min_count": 1
        },
        "reward": 500,
        "icon": "trophy"
    },
    {
        "id": "architect",
        "name": "Архитектор процессов",
        "description": "Создано 5+ процессных стандартов",
        "requirements": {
            "type": "standards_count_by_type",
            "standard_type": "process",
            "min_count": 5
        },
        "reward": 750,
        "icon": "diagram-3"
    },
    {
        "id": "master_organizer",
        "name": "Мастер организации",
        "description": "Проведена валидация 10+ стандартов",
        "requirements": {
            "type": "validated_standards",
            "min_count": 10
        },
        "reward": 1000,
        "icon": "check2-circle"
    },
    {
        "id": "knowledge_integrator",
        "name": "Интегратор знаний",
        "description": "Интеграция с 3+ внешними системами",
        "requirements": {
            "type": "api_integrations",
            "min_count": 3
        },
        "reward": 1200,
        "icon": "link"
    },
    {
        "id": "diagnostics_expert",
        "name": "Эксперт диагностики",
        "description": "Создано 3+ проекта с диагностиками",
        "requirements": {
            "type": "projects_with_diagnostics",
            "min_count": 3
        },
        "reward": 1500,
        "icon": "graph-up"
    },
    {
        "id": "methodology_guru",
        "name": "Гуру методологий",
        "description": "Уровень системы 100% (все элементы внедрены)",
        "requirements": {
            "type": "system_completion",
            "min_percentage": 100
        },
        "reward": 2000,
        "icon": "mortarboard"
    },
    {
        "id": "versioning_master",
        "name": "Мастер версионирования",
        "description": "Управление 20+ версиями стандартов",
        "requirements": {
            "type": "versions_count",
            "min_count": 20
        },
        "reward": 800,
        "icon": "clock-history"
    },
    {
        "id": "archiving_expert",
        "name": "Эксперт архивирования",
        "description": "Архивирование 10+ устаревших стандартов",
        "requirements": {
            "type": "archived_standards",
            "min_count": 10
        },
        "reward": 600,
        "icon": "archive"
    },
    {
        "id": "system_integrator",
        "name": "Системный интегратор",
        "description": "Синхронизация с 3+ внешними репозиториями",
        "requirements": {
            "type": "git_syncs",
            "min_count": 3
        },
        "reward": 900,
        "icon": "github"
    },
    {
        "id": "standards_validator",
        "name": "Валидатор стандартов",
        "description": "Исправление 15+ ошибок в стандартах",
        "requirements": {
            "type": "fixed_validation_errors",
            "min_count": 15
        },
        "reward": 750,
        "icon": "shield-check"
    }
]

# Вехи прогресса (milestones)
MILESTONES = [
    {
        "id": "initial_setup",
        "name": "Начальная настройка",
        "description": "Настройка базовой структуры проекта",
        "target_percentage": 10,
        "reward": 200
    },
    {
        "id": "basic_standards",
        "name": "Базовые стандарты",
        "description": "Создание основных стандартов",
        "target_percentage": 25,
        "reward": 300
    },
    {
        "id": "process_implementation",
        "name": "Внедрение процессов",
        "description": "Внедрение процессных стандартов",
        "target_percentage": 50,
        "reward": 500
    },
    {
        "id": "api_integration",
        "name": "API Интеграция",
        "description": "Интеграция с внешними системами",
        "target_percentage": 75,
        "reward": 800
    },
    {
        "id": "complete_system",
        "name": "Полная система",
        "description": "Завершение всех элементов системы",
        "target_percentage": 100,
        "reward": 1500
    }
]

class ProgressTracker:
    """Класс для отслеживания прогресса и достижений в Advising Diagnostics."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Инициализирует трекер прогресса.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self) -> None:
        """Инициализирует базу данных для хранения прогресса и достижений."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Таблица для хранения прогресса
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key)
                )
            ''')
            
            # Таблица для хранения достижений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    unlocked BOOLEAN DEFAULT 0,
                    unlock_date TIMESTAMP,
                    progress INTEGER DEFAULT 0,
                    max_progress INTEGER NOT NULL,
                    reward INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица для хранения вех прогресса
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    milestone_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    reached BOOLEAN DEFAULT 0,
                    reach_date TIMESTAMP,
                    current_percentage INTEGER DEFAULT 0,
                    target_percentage INTEGER NOT NULL,
                    reward INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица для хранения статистики активности
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    standards_created INTEGER DEFAULT 0,
                    standards_validated INTEGER DEFAULT 0,
                    standards_archived INTEGER DEFAULT 0,
                    projects_created INTEGER DEFAULT 0,
                    api_calls INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица для хранения рейтингов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    comment TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для логов событий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Инициализация предопределенных достижений, если таблица пуста
            cursor.execute("SELECT COUNT(*) FROM achievements")
            if cursor.fetchone()[0] == 0:
                for achievement in ACHIEVEMENTS:
                    max_progress = achievement["requirements"].get("min_count", 0)
                    if "min_percentage" in achievement["requirements"]:
                        max_progress = achievement["requirements"]["min_percentage"]
                    
                    cursor.execute('''
                        INSERT INTO achievements (achievement_id, name, unlocked, progress, max_progress, reward)
                        VALUES (?, ?, 0, 0, ?, ?)
                    ''', (
                        achievement["id"],
                        achievement["name"],
                        max_progress,
                        achievement["reward"]
                    ))
            
            # Инициализация предопределенных вех, если таблица пуста
            cursor.execute("SELECT COUNT(*) FROM milestones")
            if cursor.fetchone()[0] == 0:
                for milestone in MILESTONES:
                    cursor.execute('''
                        INSERT INTO milestones (milestone_id, name, reached, current_percentage, target_percentage, reward)
                        VALUES (?, ?, 0, 0, ?, ?)
                    ''', (
                        milestone["id"],
                        milestone["name"],
                        milestone["target_percentage"],
                        milestone["reward"]
                    ))
            
            # Инициализация сегодняшней активности, если нет записи
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM activity_stats WHERE date = ?", (today,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO activity_stats (date, standards_created, standards_validated, standards_archived, projects_created, api_calls)
                    VALUES (?, 0, 0, 0, 0, 0)
                ''', (today,))
            
            self.conn.commit()
            logger.info("База данных прогресса успешно инициализирована")
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            if self.conn:
                self.conn.rollback()
    
    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_progress(self, category: str, key: str, default: int = 0) -> int:
        """
        Получает значение прогресса для указанной категории и ключа.
        
        Args:
            category: Категория прогресса (например, 'standards', 'projects', 'api')
            key: Ключ в рамках категории
            default: Значение по умолчанию, если запись не найдена
        
        Returns:
            Значение прогресса
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT value FROM progress WHERE category = ? AND key = ?
            ''', (category, key))
            
            result = cursor.fetchone()
            return result[0] if result else default
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении прогресса {category}.{key}: {e}")
            return default
    
    def update_progress(self, category: str, key: str, value: int) -> bool:
        """
        Обновляет значение прогресса для указанной категории и ключа.
        
        Args:
            category: Категория прогресса
            key: Ключ в рамках категории
            value: Новое значение прогресса
        
        Returns:
            True, если обновление успешно, иначе False
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO progress (category, key, value, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(category, key) DO UPDATE SET
                value = ?,
                last_updated = CURRENT_TIMESTAMP
            ''', (category, key, value, value))
            
            self.conn.commit()
            
            # Проверяем, не разблокирует ли это какие-либо достижения
            self.check_achievements()
            
            # Обновляем вехи прогресса
            self.update_milestones()
            
            # Логируем событие
            self.log_event("progress_update", f"Обновлен прогресс {category}.{key}", f"Новое значение: {value}")
            
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при обновлении прогресса {category}.{key}: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def increment_progress(self, category: str, key: str, increment: int = 1) -> bool:
        """
        Увеличивает значение прогресса для указанной категории и ключа.
        
        Args:
            category: Категория прогресса
            key: Ключ в рамках категории
            increment: Величина увеличения (по умолчанию 1)
        
        Returns:
            True, если обновление успешно, иначе False
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO progress (category, key, value, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(category, key) DO UPDATE SET
                value = value + ?,
                last_updated = CURRENT_TIMESTAMP
            ''', (category, key, increment, increment))
            
            self.conn.commit()
            
            # Обновляем статистику активности
            self.update_activity_stat(category, increment)
            
            # Проверяем, не разблокирует ли это какие-либо достижения
            self.check_achievements()
            
            # Обновляем вехи прогресса
            self.update_milestones()
            
            # Логируем событие
            self.log_event("progress_increment", f"Увеличен прогресс {category}.{key}", f"Инкремент: {increment}")
            
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при увеличении прогресса {category}.{key}: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def update_activity_stat(self, category: str, increment: int = 1) -> None:
        """
        Обновляет статистику активности за текущий день.
        
        Args:
            category: Категория активности
            increment: Величина увеличения (по умолчанию 1)
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = self.conn.cursor()
            
            # Определяем поле для обновления на основе категории
            field_mapping = {
                'standards': 'standards_created',
                'standards_validation': 'standards_validated',
                'standards_archive': 'standards_archived',
                'projects': 'projects_created',
                'api': 'api_calls'
            }
            
            field = field_mapping.get(category)
            if not field:
                return
            
            # Убеждаемся, что запись за сегодня существует
            cursor.execute("SELECT COUNT(*) FROM activity_stats WHERE date = ?", (today,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO activity_stats (date, standards_created, standards_validated, standards_archived, projects_created, api_calls)
                    VALUES (?, 0, 0, 0, 0, 0)
                ''', (today,))
            
            # Обновляем соответствующее поле
            cursor.execute(f'''
                UPDATE activity_stats SET {field} = {field} + ? WHERE date = ?
            ''', (increment, today))
            
            self.conn.commit()
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при обновлении статистики активности: {e}")
            if self.conn:
                self.conn.rollback()
    
    def check_achievements(self) -> List[Dict[str, Any]]:
        """
        Проверяет, не разблокированы ли новые достижения.
        
        Returns:
            Список новых разблокированных достижений
        """
        try:
            newly_unlocked = []
            cursor = self.conn.cursor()
            
            # Получаем все незаблокированные достижения
            cursor.execute("SELECT achievement_id, progress, max_progress FROM achievements WHERE unlocked = 0")
            locked_achievements = cursor.fetchall()
            
            for achievement_id, current_progress, max_progress in locked_achievements:
                # Находим определение достижения
                achievement_def = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), None)
                if not achievement_def:
                    continue
                
                # Проверяем условия разблокировки
                requirements = achievement_def["requirements"]
                requirement_type = requirements["type"]
                
                new_progress = 0
                
                if requirement_type == "standards_count":
                    new_progress = self.get_progress("standards", "total", 0)
                
                elif requirement_type == "standards_count_by_type":
                    standard_type = requirements["standard_type"]
                    new_progress = self.get_progress("standards", f"by_type_{standard_type}", 0)
                
                elif requirement_type == "validated_standards":
                    new_progress = self.get_progress("standards_validation", "total", 0)
                
                elif requirement_type == "api_integrations":
                    new_progress = self.get_progress("api", "integrations", 0)
                
                elif requirement_type == "projects_with_diagnostics":
                    new_progress = self.get_progress("projects", "with_diagnostics", 0)
                
                elif requirement_type == "system_completion":
                    # Рассчитываем общий прогресс системы
                    standards_progress = self.get_progress("standards", "completion_percentage", 0)
                    projects_progress = self.get_progress("projects", "completion_percentage", 0)
                    api_progress = self.get_progress("api", "completion_percentage", 0)
                    
                    total_items = 3
                    total_progress = (standards_progress + projects_progress + api_progress) / total_items
                    new_progress = int(total_progress)
                
                elif requirement_type == "versions_count":
                    new_progress = self.get_progress("standards", "versions_total", 0)
                
                elif requirement_type == "archived_standards":
                    new_progress = self.get_progress("standards_archive", "total", 0)
                
                elif requirement_type == "git_syncs":
                    new_progress = self.get_progress("git", "syncs", 0)
                
                elif requirement_type == "fixed_validation_errors":
                    new_progress = self.get_progress("standards_validation", "fixed_errors", 0)
                
                # Обновляем прогресс достижения
                cursor.execute('''
                    UPDATE achievements SET progress = ? WHERE achievement_id = ?
                ''', (new_progress, achievement_id))
                
                # Проверяем, выполнены ли условия разблокировки
                if new_progress >= max_progress:
                    cursor.execute('''
                        UPDATE achievements
                        SET unlocked = 1, unlock_date = CURRENT_TIMESTAMP
                        WHERE achievement_id = ?
                    ''', (achievement_id,))
                    
                    # Добавляем в список новых разблокированных достижений
                    achievement_data = {
                        "id": achievement_id,
                        "name": achievement_def["name"],
                        "description": achievement_def["description"],
                        "reward": achievement_def["reward"],
                        "icon": achievement_def.get("icon", "trophy")
                    }
                    newly_unlocked.append(achievement_data)
                    
                    # Логируем событие разблокировки достижения
                    self.log_event(
                        "achievement_unlocked",
                        f"Разблокировано достижение: {achievement_def['name']}",
                        f"Награда: {achievement_def['reward']} очков опыта"
                    )
            
            self.conn.commit()
            return newly_unlocked
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при проверке достижений: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def update_milestones(self) -> List[Dict[str, Any]]:
        """
        Обновляет прогресс вех и проверяет, не достигнуты ли новые вехи.
        
        Returns:
            Список новых достигнутых вех
        """
        try:
            newly_reached = []
            cursor = self.conn.cursor()
            
            # Рассчитываем текущий процент выполнения системы
            standards_progress = self.get_progress("standards", "completion_percentage", 0)
            projects_progress = self.get_progress("projects", "completion_percentage", 0)
            api_progress = self.get_progress("api", "completion_percentage", 0)
            
            total_items = 3
            system_progress = (standards_progress + projects_progress + api_progress) / total_items
            system_progress_percent = int(system_progress)
            
            # Получаем все недостигнутые вехи
            cursor.execute("SELECT milestone_id, target_percentage, reward FROM milestones WHERE reached = 0")
            unreached_milestones = cursor.fetchall()
            
            # Обновляем текущий процент для всех вех
            cursor.execute('''
                UPDATE milestones SET current_percentage = ?
            ''', (system_progress_percent,))
            
            for milestone_id, target_percentage, reward in unreached_milestones:
                if system_progress_percent >= target_percentage:
                    # Отмечаем веху как достигнутую
                    cursor.execute('''
                        UPDATE milestones
                        SET reached = 1, reach_date = CURRENT_TIMESTAMP
                        WHERE milestone_id = ?
                    ''', (milestone_id,))
                    
                    # Находим определение вехи
                    milestone_def = next((m for m in MILESTONES if m["id"] == milestone_id), None)
                    if milestone_def:
                        # Добавляем в список новых достигнутых вех
                        milestone_data = {
                            "id": milestone_id,
                            "name": milestone_def["name"],
                            "description": milestone_def["description"],
                            "reward": reward,
                            "target_percentage": target_percentage
                        }
                        newly_reached.append(milestone_data)
                        
                        # Логируем событие достижения вехи
                        self.log_event(
                            "milestone_reached",
                            f"Достигнута веха: {milestone_def['name']}",
                            f"Прогресс: {system_progress_percent}%, Награда: {reward} очков опыта"
                        )
            
            self.conn.commit()
            return newly_reached
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при обновлении вех прогресса: {e}")
            if self.conn:
                self.conn.rollback()
            return []
    
    def get_achievement_status(self, achievement_id: str = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Получает статус достижения или список всех достижений.
        
        Args:
            achievement_id: ID достижения или None для получения всех достижений
        
        Returns:
            Информация о достижении или список всех достижений
        """
        try:
            cursor = self.conn.cursor()
            
            if achievement_id:
                # Получаем статус одного достижения
                cursor.execute('''
                    SELECT achievement_id, name, unlocked, progress, max_progress, unlock_date, reward
                    FROM achievements WHERE achievement_id = ?
                ''', (achievement_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                achievement_def = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), {})
                
                return {
                    "id": row[0],
                    "name": row[1],
                    "unlocked": bool(row[2]),
                    "progress": row[3],
                    "max_progress": row[4],
                    "unlock_date": row[5],
                    "reward": row[6],
                    "description": achievement_def.get("description", ""),
                    "icon": achievement_def.get("icon", "trophy")
                }
            else:
                # Получаем статус всех достижений
                cursor.execute('''
                    SELECT achievement_id, name, unlocked, progress, max_progress, unlock_date, reward
                    FROM achievements
                ''')
                
                achievements = []
                for row in cursor.fetchall():
                    achievement_id = row[0]
                    achievement_def = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), {})
                    
                    achievements.append({
                        "id": achievement_id,
                        "name": row[1],
                        "unlocked": bool(row[2]),
                        "progress": row[3],
                        "max_progress": row[4],
                        "unlock_date": row[5],
                        "reward": row[6],
                        "description": achievement_def.get("description", ""),
                        "icon": achievement_def.get("icon", "trophy")
                    })
                
                return achievements
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении статуса достижений: {e}")
            return [] if achievement_id is None else None
    
    def get_milestone_status(self, milestone_id: str = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Получает статус вехи или список всех вех.
        
        Args:
            milestone_id: ID вехи или None для получения всех вех
        
        Returns:
            Информация о вехе или список всех вех
        """
        try:
            cursor = self.conn.cursor()
            
            if milestone_id:
                # Получаем статус одной вехи
                cursor.execute('''
                    SELECT milestone_id, name, reached, current_percentage, target_percentage, reach_date, reward
                    FROM milestones WHERE milestone_id = ?
                ''', (milestone_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                milestone_def = next((m for m in MILESTONES if m["id"] == milestone_id), {})
                
                return {
                    "id": row[0],
                    "name": row[1],
                    "reached": bool(row[2]),
                    "current_percentage": row[3],
                    "target_percentage": row[4],
                    "reach_date": row[5],
                    "reward": row[6],
                    "description": milestone_def.get("description", "")
                }
            else:
                # Получаем статус всех вех
                cursor.execute('''
                    SELECT milestone_id, name, reached, current_percentage, target_percentage, reach_date, reward
                    FROM milestones
                ''')
                
                milestones = []
                for row in cursor.fetchall():
                    milestone_id = row[0]
                    milestone_def = next((m for m in MILESTONES if m["id"] == milestone_id), {})
                    
                    milestones.append({
                        "id": milestone_id,
                        "name": row[1],
                        "reached": bool(row[2]),
                        "current_percentage": row[3],
                        "target_percentage": row[4],
                        "reach_date": row[5],
                        "reward": row[6],
                        "description": milestone_def.get("description", "")
                    })
                
                return milestones
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении статуса вех: {e}")
            return [] if milestone_id is None else None
    
    def get_activity_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Получает статистику активности за указанное количество дней.
        
        Args:
            days: Количество дней для получения статистики
        
        Returns:
            Список с данными активности по дням
        """
        try:
            cursor = self.conn.cursor()
            
            # Вычисляем дату начала периода
            start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
            
            cursor.execute('''
                SELECT date, standards_created, standards_validated, standards_archived, projects_created, api_calls
                FROM activity_stats
                WHERE date >= ?
                ORDER BY date
            ''', (start_date,))
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    "date": row[0],
                    "standards_created": row[1],
                    "standards_validated": row[2],
                    "standards_archived": row[3],
                    "projects_created": row[4],
                    "api_calls": row[5]
                })
            
            # Если не хватает данных для всех дней, дополняем нулями
            existing_dates = {stat["date"] for stat in stats}
            current_date = datetime.now()
            
            for i in range(days):
                date_str = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
                if date_str not in existing_dates:
                    stats.append({
                        "date": date_str,
                        "standards_created": 0,
                        "standards_validated": 0,
                        "standards_archived": 0,
                        "projects_created": 0,
                        "api_calls": 0
                    })
            
            # Сортируем по дате
            stats.sort(key=lambda x: x["date"])
            
            return stats
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении статистики активности: {e}")
            return []
    
    def add_rating(self, category: str, value: int, comment: str = None) -> bool:
        """
        Добавляет новую оценку в указанную категорию.
        
        Args:
            category: Категория оценки (например, 'system', 'standard', 'project')
            value: Значение оценки (обычно от 1 до 5)
            comment: Комментарий к оценке (опционально)
        
        Returns:
            True, если оценка успешно добавлена, иначе False
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO ratings (category, value, comment, date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (category, value, comment))
            
            self.conn.commit()
            
            # Логируем событие
            self.log_event("rating_added", f"Добавлена оценка для категории '{category}'", f"Значение: {value}, Комментарий: {comment}")
            
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении оценки: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_average_rating(self, category: str) -> float:
        """
        Получает среднюю оценку для указанной категории.
        
        Args:
            category: Категория оценки
        
        Returns:
            Средняя оценка или 0, если нет оценок
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT AVG(value) FROM ratings WHERE category = ?
            ''', (category,))
            
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении средней оценки для категории '{category}': {e}")
            return 0.0
    
    def log_event(self, event_type: str, description: str, details: str = None) -> bool:
        """
        Логирует событие в базу данных.
        
        Args:
            event_type: Тип события
            description: Описание события
            details: Дополнительные детали (опционально)
        
        Returns:
            True, если событие успешно залогировано, иначе False
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO event_logs (event_type, description, details, date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (event_type, description, details))
            
            self.conn.commit()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при логировании события: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_event_logs(self, event_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получает логи событий.
        
        Args:
            event_type: Тип события для фильтрации (опционально)
            limit: Максимальное количество логов
        
        Returns:
            Список логов событий
        """
        try:
            cursor = self.conn.cursor()
            
            if event_type:
                cursor.execute('''
                    SELECT id, event_type, description, details, date
                    FROM event_logs
                    WHERE event_type = ?
                    ORDER BY date DESC
                    LIMIT ?
                ''', (event_type, limit))
            else:
                cursor.execute('''
                    SELECT id, event_type, description, details, date
                    FROM event_logs
                    ORDER BY date DESC
                    LIMIT ?
                ''', (limit,))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "id": row[0],
                    "event_type": row[1],
                    "description": row[2],
                    "details": row[3],
                    "date": row[4]
                })
            
            return logs
        
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении логов событий: {e}")
            return []
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        Получает сводную информацию о состоянии системы.
        
        Returns:
            Словарь со сводными данными
        """
        try:
            # Собираем информацию о стандартах
            standards_total = self.get_progress("standards", "total", 0)
            standards_valid = self.get_progress("standards", "valid", 0)
            standards_invalid = standards_total - standards_valid
            
            # Собираем информацию о проектах
            projects_total = self.get_progress("projects", "total", 0)
            projects_completed = self.get_progress("projects", "completed", 0)
            projects_ongoing = projects_total - projects_completed
            
            # Собираем информацию об API
            api_total = self.get_progress("api", "total", 0)
            api_implemented = self.get_progress("api", "implemented", 0)
            api_pending = api_total - api_implemented
            
            # Рассчитываем проценты выполнения
            standards_percentage = (standards_valid / standards_total * 100) if standards_total > 0 else 0
            projects_percentage = (projects_completed / projects_total * 100) if projects_total > 0 else 0
            api_percentage = (api_implemented / api_total * 100) if api_total > 0 else 0
            
            # Обновляем процентные значения в базе для использования в расчетах достижений
            self.update_progress("standards", "completion_percentage", int(standards_percentage))
            self.update_progress("projects", "completion_percentage", int(projects_percentage))
            self.update_progress("api", "completion_percentage", int(api_percentage))
            
            # Рассчитываем общий прогресс
            total_elements = 3  # standards, projects, api
            system_progress = (standards_percentage + projects_percentage + api_percentage) / total_elements
            
            # Получаем информацию о достижениях
            achievements = self.get_achievement_status()
            unlocked_achievements = [a for a in achievements if a["unlocked"]]
            in_progress_achievements = [a for a in achievements if not a["unlocked"] and a["progress"] > 0]
            
            # Получаем информацию о вехах
            milestones = self.get_milestone_status()
            reached_milestones = [m for m in milestones if m["reached"]]
            
            # Получаем статистику активности за последнюю неделю
            activity_stats = self.get_activity_stats(7)
            
            # Собираем сводку
            summary = {
                "system_progress": round(system_progress, 1),
                "standards": {
                    "total": standards_total,
                    "valid": standards_valid,
                    "invalid": standards_invalid,
                    "percentage": round(standards_percentage, 1)
                },
                "projects": {
                    "total": projects_total,
                    "completed": projects_completed,
                    "ongoing": projects_ongoing,
                    "percentage": round(projects_percentage, 1)
                },
                "api": {
                    "total": api_total,
                    "implemented": api_implemented,
                    "pending": api_pending,
                    "percentage": round(api_percentage, 1)
                },
                "achievements": {
                    "total": len(achievements),
                    "unlocked": len(unlocked_achievements),
                    "in_progress": len(in_progress_achievements),
                    "percentage": round(len(unlocked_achievements) / len(achievements) * 100, 1) if achievements else 0
                },
                "milestones": {
                    "total": len(milestones),
                    "reached": len(reached_milestones),
                    "percentage": round(len(reached_milestones) / len(milestones) * 100, 1) if milestones else 0
                },
                "activity": {
                    "last_7_days": {
                        "standards_created": sum(day["standards_created"] for day in activity_stats),
                        "standards_validated": sum(day["standards_validated"] for day in activity_stats),
                        "standards_archived": sum(day["standards_archived"] for day in activity_stats)
                    }
                },
                "last_achievements": unlocked_achievements[:3] if unlocked_achievements else [],
                "next_milestones": [m for m in milestones if not m["reached"]][:2]
            }
            
            return summary
        
        except Exception as e:
            logger.error(f"Ошибка при получении сводки о системе: {e}")
            return {
                "error": str(e),
                "system_progress": 0,
                "standards": {"total": 0, "valid": 0, "invalid": 0, "percentage": 0},
                "projects": {"total": 0, "completed": 0, "ongoing": 0, "percentage": 0},
                "api": {"total": 0, "implemented": 0, "pending": 0, "percentage": 0},
                "achievements": {"total": 0, "unlocked": 0, "in_progress": 0, "percentage": 0},
                "milestones": {"total": 0, "reached": 0, "percentage": 0},
                "activity": {"last_7_days": {"standards_created": 0, "standards_validated": 0, "standards_archived": 0}},
                "last_achievements": [],
                "next_milestones": []
            }

def track_standard_action(action: str, standards_count: int = 1, standard_type: str = None) -> Dict[str, Any]:
    """
    Отслеживает действия со стандартами и обновляет прогресс.
    
    Args:
        action: Тип действия ('create', 'validate', 'archive')
        standards_count: Количество затронутых стандартов
        standard_type: Тип стандарта ('task_master', 'process', 'context', 'diagnostic')
    
    Returns:
        Словарь с информацией о разблокированных достижениях и достигнутых вехах
    """
    try:
        tracker = ProgressTracker()
        result = {"achievements": [], "milestones": []}
        
        if action == 'create':
            # Обновляем общее количество стандартов
            tracker.increment_progress("standards", "total", standards_count)
            
            # Если указан тип стандарта, обновляем счетчик для этого типа
            if standard_type:
                tracker.increment_progress("standards", f"by_type_{standard_type}", standards_count)
        
        elif action == 'validate':
            # Обновляем количество валидированных стандартов
            tracker.increment_progress("standards_validation", "total", standards_count)
            
            # Увеличиваем количество валидных стандартов
            tracker.increment_progress("standards", "valid", standards_count)
        
        elif action == 'archive':
            # Обновляем количество архивированных стандартов
            tracker.increment_progress("standards_archive", "total", standards_count)
        
        # Получаем информацию о разблокированных достижениях и достигнутых вехах
        newly_unlocked = tracker.check_achievements()
        newly_reached = tracker.update_milestones()
        
        if newly_unlocked:
            result["achievements"] = newly_unlocked
        
        if newly_reached:
            result["milestones"] = newly_reached
        
        # Закрываем соединение с базой данных
        tracker.close()
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при отслеживании действия со стандартом: {e}")
        return {"error": str(e), "achievements": [], "milestones": []}

def track_project_action(action: str, projects_count: int = 1, with_diagnostics: bool = False) -> Dict[str, Any]:
    """
    Отслеживает действия с проектами и обновляет прогресс.
    
    Args:
        action: Тип действия ('create', 'complete')
        projects_count: Количество затронутых проектов
        with_diagnostics: Имеют ли проекты диагностики
    
    Returns:
        Словарь с информацией о разблокированных достижениях и достигнутых вехах
    """
    try:
        tracker = ProgressTracker()
        result = {"achievements": [], "milestones": []}
        
        if action == 'create':
            # Обновляем общее количество проектов
            tracker.increment_progress("projects", "total", projects_count)
            
            # Если проекты с диагностиками, обновляем соответствующий счетчик
            if with_diagnostics:
                tracker.increment_progress("projects", "with_diagnostics", projects_count)
        
        elif action == 'complete':
            # Обновляем количество завершенных проектов
            tracker.increment_progress("projects", "completed", projects_count)
        
        # Получаем информацию о разблокированных достижениях и достигнутых вехах
        newly_unlocked = tracker.check_achievements()
        newly_reached = tracker.update_milestones()
        
        if newly_unlocked:
            result["achievements"] = newly_unlocked
        
        if newly_reached:
            result["milestones"] = newly_reached
        
        # Закрываем соединение с базой данных
        tracker.close()
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при отслеживании действия с проектом: {e}")
        return {"error": str(e), "achievements": [], "milestones": []}

def track_api_action(action: str, count: int = 1) -> Dict[str, Any]:
    """
    Отслеживает действия с API и обновляет прогресс.
    
    Args:
        action: Тип действия ('integrate', 'call')
        count: Количество интеграций или вызовов
    
    Returns:
        Словарь с информацией о разблокированных достижениях и достигнутых вехах
    """
    try:
        tracker = ProgressTracker()
        result = {"achievements": [], "milestones": []}
        
        if action == 'integrate':
            # Обновляем общее количество API
            tracker.increment_progress("api", "total", count)
            
            # Обновляем количество реализованных API
            tracker.increment_progress("api", "implemented", count)
            
            # Обновляем количество интеграций
            tracker.increment_progress("api", "integrations", count)
        
        elif action == 'call':
            # Обновляем количество вызовов API
            tracker.increment_progress("api", "calls", count)
        
        # Получаем информацию о разблокированных достижениях и достигнутых вехах
        newly_unlocked = tracker.check_achievements()
        newly_reached = tracker.update_milestones()
        
        if newly_unlocked:
            result["achievements"] = newly_unlocked
        
        if newly_reached:
            result["milestones"] = newly_reached
        
        # Закрываем соединение с базой данных
        tracker.close()
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при отслеживании действия с API: {e}")
        return {"error": str(e), "achievements": [], "milestones": []}

def track_git_action(action: str) -> Dict[str, Any]:
    """
    Отслеживает действия с Git и обновляет прогресс.
    
    Args:
        action: Тип действия ('sync')
    
    Returns:
        Словарь с информацией о разблокированных достижениях и достигнутых вехах
    """
    try:
        tracker = ProgressTracker()
        result = {"achievements": [], "milestones": []}
        
        if action == 'sync':
            # Обновляем количество синхронизаций с Git
            tracker.increment_progress("git", "syncs")
        
        # Получаем информацию о разблокированных достижениях и достигнутых вехах
        newly_unlocked = tracker.check_achievements()
        newly_reached = tracker.update_milestones()
        
        if newly_unlocked:
            result["achievements"] = newly_unlocked
        
        if newly_reached:
            result["milestones"] = newly_reached
        
        # Закрываем соединение с базой данных
        tracker.close()
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при отслеживании действия с Git: {e}")
        return {"error": str(e), "achievements": [], "milestones": []}

def get_system_status() -> Dict[str, Any]:
    """
    Получает текущий статус системы, включая прогресс, достижения и вехи.
    
    Returns:
        Словарь с информацией о статусе системы
    """
    try:
        tracker = ProgressTracker()
        result = tracker.get_system_summary()
        
        # Закрываем соединение с базой данных
        tracker.close()
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при получении статуса системы: {e}")
        return {"error": str(e)}

def main():
    """Основная функция для тестирования и инициализации."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Система отслеживания прогресса и достижений')
    parser.add_argument('--init', action='store_true', help='Инициализировать базу данных')
    parser.add_argument('--standard', choices=['create', 'validate', 'archive'], help='Отслеживание действия со стандартом')
    parser.add_argument('--project', choices=['create', 'complete'], help='Отслеживание действия с проектом')
    parser.add_argument('--api', choices=['integrate', 'call'], help='Отслеживание действия с API')
    parser.add_argument('--git', choices=['sync'], help='Отслеживание действия с Git')
    parser.add_argument('--status', action='store_true', help='Получить текущий статус системы')
    
    args = parser.parse_args()
    
    # Инициализация базы данных
    if args.init:
        tracker = ProgressTracker()
        tracker.close()
        print("База данных прогресса успешно инициализирована")
    
    # Отслеживание действия со стандартом
    elif args.standard:
        result = track_standard_action(args.standard)
        print(f"Результат действия со стандартом ({args.standard}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Отслеживание действия с проектом
    elif args.project:
        result = track_project_action(args.project)
        print(f"Результат действия с проектом ({args.project}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Отслеживание действия с API
    elif args.api:
        result = track_api_action(args.api)
        print(f"Результат действия с API ({args.api}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Отслеживание действия с Git
    elif args.git:
        result = track_git_action(args.git)
        print(f"Результат действия с Git ({args.git}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Получение текущего статуса системы
    elif args.status:
        status = get_system_status()
        print("Текущий статус системы:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    else:
        print("Используйте аргументы командной строки для выполнения действий. Запустите с --help для справки.")

if __name__ == "__main__":
    main()