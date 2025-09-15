#!/usr/bin/env python3
"""
Модуль управления персональностями AI ассистента.

Обеспечивает:
1. Загрузку доступных персональностей
2. Определение активной персональности
3. Переключение между персональностями
4. Автоматическое определение подходящей персональности на основе контекста
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Импортируем модуль пользовательских настроек
from .user_preferences import user_preferences

# Настройка логирования
logger = logging.getLogger(__name__)

# Пути к файлам конфигурации
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
PERSONALITIES_FILE = os.path.join(CONFIG_DIR, 'personalities.json')


class PersonalityManager:
    """Класс для управления персональностями AI ассистента."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для управления персональностями."""
        if cls._instance is None:
            cls._instance = super(PersonalityManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует менеджер персональностей."""
        if getattr(self, '_initialized', False):
            return
        
        self._personalities = {}
        self._default_personality = None
        self._active_personality = None
        self._load_personalities()
        self._initialize_active_personality()
        self._initialized = True
        logger.info("Инициализирован менеджер персональностей")
    
    def _load_personalities(self) -> None:
        """Загружает персональности из файла конфигурации."""
        try:
            if os.path.exists(PERSONALITIES_FILE):
                with open(PERSONALITIES_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Загружаем все персональности
                    personalities_data = config.get('personalities', [])
                    for personality_data in personalities_data:
                        name = personality_data.get('name')
                        if name:
                            self._personalities[name] = personality_data
                    
                    # Устанавливаем персональность по умолчанию
                    self._default_personality = config.get('defaultPersonality')
                    if self._default_personality not in self._personalities:
                        self._default_personality = next(iter(self._personalities)) if self._personalities else None
                    
                    logger.info(f"Загружено {len(self._personalities)} персональностей")
                    
            else:
                logger.warning(f"Файл персональностей не найден: {PERSONALITIES_FILE}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке персональностей: {e}")
    
    def _initialize_active_personality(self) -> None:
        """Инициализирует активную персональность на основе пользовательских настроек."""
        personality_settings = user_preferences._preferences.get('personalitySettings', {})
        active_personality_name = personality_settings.get('activePersonality')
        
        if active_personality_name and active_personality_name in self._personalities:
            self._active_personality = active_personality_name
            logger.info(f"Установлена активная персональность: {active_personality_name}")
        else:
            self._active_personality = self._default_personality
            logger.info(f"Установлена персональность по умолчанию: {self._default_personality}")
    
    def get_personalities(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает все доступные персональности."""
        return self._personalities
    
    def get_personality(self, name: str) -> Optional[Dict[str, Any]]:
        """Возвращает детали указанной персональности."""
        return self._personalities.get(name)
    
    def get_active_personality_name(self) -> Optional[str]:
        """Возвращает имя активной персональности."""
        return self._active_personality
    
    def get_active_personality(self) -> Optional[Dict[str, Any]]:
        """Возвращает детали активной персональности."""
        if self._active_personality:
            return self._personalities.get(self._active_personality)
        return None
    
    def switch_personality(self, name: str) -> bool:
        """Переключается на указанную персональность."""
        if name not in self._personalities:
            logger.warning(f"Персональность не найдена: {name}")
            return False
        
        # Обновляем активную персональность
        previous = self._active_personality
        self._active_personality = name
        
        # Обновляем настройки пользователя
        personality_settings = user_preferences._preferences.get('personalitySettings', {})
        personality_settings['activePersonality'] = name
        personality_settings['lastSwitchTime'] = datetime.now().isoformat()
        
        # Добавляем запись в историю
        history = personality_settings.get('personalityHistory', [])
        history.append({
            'name': name,
            'activatedAt': datetime.now().isoformat()
        })
        
        # Ограничиваем историю до 10 последних записей
        if len(history) > 10:
            history = history[-10:]
        
        personality_settings['personalityHistory'] = history
        user_preferences._preferences['personalitySettings'] = personality_settings
        user_preferences._save_preferences()
        
        logger.info(f"Персональность изменена: {previous} -> {name}")
        return True
    
    def detect_personality_from_message(self, message: str) -> Optional[str]:
        """Определяет персональность на основе сообщения пользователя."""
        if not message:
            return None
        
        message = message.lower()
        
        # Проверяем обращение по имени в начале сообщения
        for name in self._personalities.keys():
            pattern = f"^{name}[,\\s]"
            if re.match(pattern, message):
                logger.info(f"Обнаружено обращение по имени: {name}")
                return name
        
        # Проверяем явные команды на переключение
        switch_patterns = [
            r"переключись в режим (\w+)",
            r"стань (\w+)",
            r"работай как (\w+)",
            r"будь (\w+)"
        ]
        
        for pattern in switch_patterns:
            match = re.search(pattern, message)
            if match:
                personality_name = match.group(1).lower()
                if personality_name in self._personalities:
                    logger.info(f"Обнаружена команда на переключение: {personality_name}")
                    return personality_name
        
        # Проверяем триггеры персональностей
        personality_settings = user_preferences._preferences.get('personalitySettings', {})
        personality_triggers = personality_settings.get('personalityTriggers', {})
        
        for personality_name, triggers in personality_triggers.items():
            for trigger in triggers:
                if trigger.lower() in message:
                    logger.info(f"Обнаружен триггер для персональности: {personality_name}")
                    return personality_name
        
        return None
    
    def should_auto_switch(self) -> bool:
        """Проверяет, нужно ли автоматически переключать персональность."""
        system_behavior = user_preferences._preferences.get('systemBehavior', {})
        return system_behavior.get('autoSwitchPersonality', False)
    
    def should_confirm_switch(self) -> bool:
        """Проверяет, нужно ли подтверждать переключение персональности."""
        system_behavior = user_preferences._preferences.get('systemBehavior', {})
        return system_behavior.get('confirmPersonalitySwitch', True)
    
    def format_confirmation_message(self, personality_name: str) -> str:
        """Форматирует сообщение о подтверждении переключения персональности."""
        personality = self.get_personality(personality_name)
        if not personality:
            return f"Переключаюсь в режим {personality_name}."
        
        tone = personality.get('communicationStyle', {}).get('tone', '')
        examples = personality.get('communicationStyle', {}).get('examples', [])
        
        if examples:
            return examples[0]
        else:
            return f"Переключаюсь в {tone} режим {personality_name}."


# Создаем глобальный экземпляр для удобного импорта
personality_manager = PersonalityManager()


def get_active_personality() -> Dict[str, Any]:
    """Утилитарная функция для получения активной персональности."""
    return personality_manager.get_active_personality() or {}


def detect_and_switch_personality(message: str) -> Optional[str]:
    """
    Определяет и переключает персональность на основе сообщения пользователя.
    
    Возвращает сообщение подтверждения, если персональность изменилась,
    или None, если персональность не изменилась.
    """
    detected = personality_manager.detect_personality_from_message(message)
    
    if detected and detected != personality_manager.get_active_personality_name():
        if personality_manager.should_auto_switch():
            personality_manager.switch_personality(detected)
            
            if personality_manager.should_confirm_switch():
                return personality_manager.format_confirmation_message(detected)
    
    return None


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO)
    
    # Переключение персональности
    personality_manager.switch_personality("монстр")
    print(f"Активная персональность: {personality_manager.get_active_personality_name()}")
    
    # Определение персональности из сообщения
    message = "Малыш, помоги мне разобраться с индексацией"
    detected = personality_manager.detect_personality_from_message(message)
    print(f"Определена персональность: {detected}")
    
    # Автоматическое переключение
    confirmation = detect_and_switch_personality(message)
    if confirmation:
        print(f"Сообщение подтверждения: {confirmation}")
        
    # Проверка активной персональности
    print(f"Новая активная персональность: {personality_manager.get_active_personality_name()}")