#!/usr/bin/env python3
"""
Модуль для работы с пользовательскими настройками.

Этот модуль обеспечивает:
1. Загрузку пользовательских настроек из конфигурационного файла
2. Проверку и применение предпочтений пользователя
3. Правильное обращение к пользователю согласно предпочтениям
4. Сохранение обновленных настроек
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Настройка логирования
logger = logging.getLogger(__name__)

# Пути к файлам конфигурации
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
PREFERENCES_FILE = os.path.join(CONFIG_DIR, 'user_preferences.json')

# Значения по умолчанию
DEFAULT_PREFERENCES = {
    "userNames": {
        "aliases": [],
        "preferredName": None,
        "lastUpdated": datetime.now().isoformat()
    },
    "communicationPreferences": {
        "language": "ru",
        "formality": "formal",
        "style": "professional"
    },
    "notificationSettings": {
        "incidentCreation": True,
        "hypothesisFailure": True,
        "standardUpdates": True
    },
    "displayPreferences": {
        "theme": "light",
        "fontFamily": "Inter",
        "fontSize": "medium"
    },
    "systemBehavior": {
        "proactiveAnalysis": True,
        "autoInjectFiveWhys": True,
        "autoArchiveAfterDays": 3
    }
}


class UserPreferences:
    """Класс для работы с пользовательскими настройками."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для управления пользовательскими настройками."""
        if cls._instance is None:
            cls._instance = super(UserPreferences, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует менеджер пользовательских настроек."""
        if getattr(self, '_initialized', False):
            return
        
        self._preferences = DEFAULT_PREFERENCES.copy()
        self._load_preferences()
        self._initialized = True
        logger.info("Инициализирован менеджер пользовательских настроек")
    
    def _load_preferences(self) -> None:
        """Загружает пользовательские настройки из файла."""
        try:
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                    loaded_preferences = json.load(f)
                    # Обновляем предпочтения из файла, сохраняя структуру по умолчанию
                    self._update_nested_dict(self._preferences, loaded_preferences)
                logger.info("Настройки пользователя загружены успешно")
            else:
                # self._preferences уже инициализирован значениями по умолчанию
                os.makedirs(CONFIG_DIR, exist_ok=True)
                self._save_preferences()
                logger.info("Созданы настройки пользователя по умолчанию")
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек пользователя: {e}")
            # self._preferences уже инициализирован значениями по умолчанию
    
    def _update_nested_dict(self, target_dict: Dict[str, Any], source_dict: Dict[str, Any]) -> None:
        """Рекурсивно обновляет вложенный словарь, сохраняя структуру."""
        for key, value in source_dict.items():
            if key in target_dict and isinstance(value, dict) and isinstance(target_dict[key], dict):
                self._update_nested_dict(target_dict[key], value)
            else:
                target_dict[key] = value
    
    def _save_preferences(self) -> None:
        """Сохраняет пользовательские настройки в файл."""
        try:
            with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._preferences, f, ensure_ascii=False, indent=2)
            logger.info("Настройки пользователя сохранены успешно")
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек пользователя: {e}")
    
    def get_user_names(self) -> Dict[str, Any]:
        """Возвращает информацию об именах пользователя."""
        return self._preferences.get("userNames", DEFAULT_PREFERENCES["userNames"])
    
    def get_preferred_name(self) -> Optional[str]:
        """Возвращает предпочтительное имя пользователя."""
        user_names = self.get_user_names()
        return user_names.get("preferredName")
    
    def get_user_aliases(self) -> List[str]:
        """Возвращает все псевдонимы пользователя."""
        user_names = self.get_user_names()
        return user_names.get("aliases", [])
    
    def add_user_alias(self, alias: str) -> None:
        """Добавляет новый псевдоним пользователя."""
        if not alias:
            return
        
        user_names = self.get_user_names()
        aliases = user_names.get("aliases", [])
        
        if alias not in aliases:
            aliases.append(alias)
            user_names["aliases"] = aliases
            user_names["lastUpdated"] = datetime.now().isoformat()
            self._preferences["userNames"] = user_names
            self._save_preferences()
            logger.info(f"Добавлен новый псевдоним пользователя: {alias}")
    
    def set_preferred_name(self, name: str) -> None:
        """Устанавливает предпочтительное имя пользователя."""
        if not name:
            return
        
        user_names = self.get_user_names()
        user_names["preferredName"] = name
        user_names["lastUpdated"] = datetime.now().isoformat()
        
        # Если имя не в списке псевдонимов, добавляем его
        if name not in user_names.get("aliases", []):
            self.add_user_alias(name)
        
        self._preferences["userNames"] = user_names
        self._save_preferences()
        logger.info(f"Установлено предпочтительное имя пользователя: {name}")
    
    def get_communication_style(self) -> Dict[str, str]:
        """Возвращает предпочтения пользователя по стилю коммуникации."""
        return self._preferences.get("communicationPreferences", 
                                    DEFAULT_PREFERENCES["communicationPreferences"])
    
    def get_notification_settings(self) -> Dict[str, bool]:
        """Возвращает настройки уведомлений пользователя."""
        return self._preferences.get("notificationSettings", 
                                    DEFAULT_PREFERENCES["notificationSettings"])
    
    def get_system_behavior(self) -> Dict[str, Union[bool, int]]:
        """Возвращает настройки поведения системы."""
        return self._preferences.get("systemBehavior", 
                                    DEFAULT_PREFERENCES["systemBehavior"])
    
    def should_auto_inject_five_whys(self) -> bool:
        """Проверяет, должен ли анализ '5 почему' автоматически выводиться в чат."""
        system_behavior = self.get_system_behavior()
        return bool(system_behavior.get("autoInjectFiveWhys", True))
    
    def get_display_preferences(self) -> Dict[str, str]:
        """Возвращает предпочтения пользователя по отображению."""
        return self._preferences.get("displayPreferences", 
                                    DEFAULT_PREFERENCES["displayPreferences"])
    
    def update_setting(self, category: str, setting: str, value: Any) -> None:
        """Обновляет конкретную настройку в указанной категории."""
        if category not in self._preferences:
            self._preferences[category] = {}
        
        self._preferences[category][setting] = value
        self._save_preferences()
        logger.info(f"Обновлена настройка {category}.{setting} = {value}")
    
    def format_user_address(self) -> str:
        """Форматирует обращение к пользователю на основе предпочтений."""
        preferred_name = self.get_preferred_name()
        if preferred_name:
            return preferred_name
        
        aliases = self.get_user_aliases()
        if aliases:
            return aliases[0]
        
        return ""


# Создаем глобальный экземпляр для удобного импорта
user_preferences = UserPreferences()


def get_user_address() -> str:
    """Утилитарная функция для получения правильного обращения к пользователю."""
    return user_preferences.format_user_address()


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO)
    
    # Добавление псевдонимов
    user_preferences.add_user_alias("малыш")
    user_preferences.add_user_alias("монстр")
    
    # Установка предпочтительного имени
    user_preferences.set_preferred_name("малыш")
    
    # Получение обращения к пользователю
    address = get_user_address()
    print(f"Обращение к пользователю: {address}")
    
    # Проверка настроек
    print(f"Псевдонимы пользователя: {user_preferences.get_user_aliases()}")
    print(f"Автоматический вывод '5 почему': {user_preferences.should_auto_inject_five_whys()}")