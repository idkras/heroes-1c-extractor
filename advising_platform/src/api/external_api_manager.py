"""
Модуль для централизованного управления внешними API.

Этот модуль предоставляет единый интерфейс для работы с внешними API,
отвечает за управление ключами API, токенами доступа и общей
логикой взаимодействия с внешними сервисами.
"""

import os
import json
import logging
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("external_api.log")
    ]
)
logger = logging.getLogger("external_api_manager")

# Загружаем переменные окружения из .env файла
load_dotenv()

# Путь к файлу с секретами API
SECRETS_FILE = Path('.api_secrets.json')
BACKUP_SECRETS_FILE = Path('.api_secrets.backup.json')

class APISecretManager:
    """Менеджер для управления секретами API."""
    
    def __init__(self, secrets_file: Path = SECRETS_FILE):
        """
        Инициализирует менеджер секретов API.
        
        Args:
            secrets_file: Путь к файлу с секретами
        """
        self.secrets_file = secrets_file
        self.secrets = self._load_secrets()
        
        # Создаем резервную копию при инициализации
        self._backup_secrets()
    
    def _load_secrets(self) -> Dict[str, Any]:
        """
        Загружает секреты из файла.
        
        Returns:
            Словарь с секретами API
        """
        try:
            if self.secrets_file.exists():
                with open(self.secrets_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Файл с секретами {self.secrets_file} не найден. Создаем новый.")
                return {}
        except Exception as e:
            logger.error(f"Ошибка при загрузке секретов API: {str(e)}")
            # Попытка восстановления из резервной копии
            if BACKUP_SECRETS_FILE.exists():
                try:
                    with open(BACKUP_SECRETS_FILE, 'r') as f:
                        logger.info("Восстановление секретов из резервной копии.")
                        return json.load(f)
                except Exception:
                    logger.error("Не удалось восстановить из резервной копии.")
            return {}
    
    def _save_secrets(self) -> bool:
        """
        Сохраняет секреты в файл.
        
        Returns:
            True если сохранение успешно, иначе False
        """
        try:
            with open(self.secrets_file, 'w') as f:
                json.dump(self.secrets, f, indent=2)
            # Создаем резервную копию после успешного сохранения
            self._backup_secrets()
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении секретов API: {str(e)}")
            return False
    
    def _backup_secrets(self) -> bool:
        """
        Создает резервную копию секретов.
        
        Returns:
            True если создание резервной копии успешно, иначе False
        """
        try:
            if self.secrets and self.secrets_file.exists():
                with open(BACKUP_SECRETS_FILE, 'w') as f:
                    json.dump(self.secrets, f, indent=2)
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии секретов: {str(e)}")
            return False
    
    def get_secret(self, api_name: str, key_name: str = 'api_key') -> Optional[str]:
        """
        Получает секрет для указанного API.
        
        Args:
            api_name: Имя API
            key_name: Имя ключа
            
        Returns:
            Значение секрета или None, если секрет не найден
        """
        # Сначала проверяем переменные окружения
        env_var_name = f"{api_name.upper()}_{key_name.upper()}"
        env_value = os.environ.get(env_var_name)
        if env_value:
            return env_value
        
        # Затем проверяем файл с секретами
        if api_name in self.secrets and key_name in self.secrets[api_name]:
            return self.secrets[api_name][key_name]
        
        # Секрет не найден
        logger.warning(f"Секрет {key_name} для API {api_name} не найден")
        return None
    
    def set_secret(self, api_name: str, key_name: str, value: str) -> bool:
        """
        Устанавливает секрет для указанного API.
        
        Args:
            api_name: Имя API
            key_name: Имя ключа
            value: Значение секрета
            
        Returns:
            True если установка успешна, иначе False
        """
        if api_name not in self.secrets:
            self.secrets[api_name] = {}
        
        self.secrets[api_name][key_name] = value
        return self._save_secrets()
    
    def has_secret(self, api_name: str, key_name: str = 'api_key') -> bool:
        """
        Проверяет наличие секрета для указанного API.
        
        Args:
            api_name: Имя API
            key_name: Имя ключа
            
        Returns:
            True если секрет существует, иначе False
        """
        # Проверяем переменные окружения
        env_var_name = f"{api_name.upper()}_{key_name.upper()}"
        if env_var_name in os.environ:
            return True
        
        # Проверяем файл с секретами
        return api_name in self.secrets and key_name in self.secrets[api_name]
    
    def delete_secret(self, api_name: str, key_name: Optional[str] = None) -> bool:
        """
        Удаляет секрет для указанного API.
        
        Args:
            api_name: Имя API
            key_name: Имя ключа (если None, удаляет все секреты для API)
            
        Returns:
            True если удаление успешно, иначе False
        """
        if api_name not in self.secrets:
            return False
        
        if key_name is None:
            del self.secrets[api_name]
        elif key_name in self.secrets[api_name]:
            del self.secrets[api_name][key_name]
            if not self.secrets[api_name]:  # Если словарь пуст
                del self.secrets[api_name]
        else:
            return False
        
        return self._save_secrets()
    
    def list_apis(self) -> List[str]:
        """
        Возвращает список имен API, для которых есть секреты.
        
        Returns:
            Список имен API
        """
        return list(self.secrets.keys())
    
    def list_secrets(self, api_name: str) -> List[str]:
        """
        Возвращает список имен секретов для указанного API.
        
        Args:
            api_name: Имя API
            
        Returns:
            Список имен секретов или пустой список, если API не найден
        """
        return list(self.secrets.get(api_name, {}).keys())

class APIRequestManager:
    """Менеджер запросов к внешним API с механизмами повторных попыток и обработки ошибок."""
    
    def __init__(self, secret_manager: Optional[APISecretManager] = None):
        """
        Инициализирует менеджер запросов API.
        
        Args:
            secret_manager: Менеджер секретов API
        """
        self.secret_manager = secret_manager or APISecretManager()
        
        # Словарь для хранения счетчиков ограничения скорости запросов
        self.rate_limits = {}
    
    def make_request(self, api_name: str, request_func, *args, **kwargs):
        """
        Выполняет запрос к API с автоматическими повторными попытками и обработкой ошибок.
        
        Args:
            api_name: Имя API
            request_func: Функция для выполнения запроса
            *args: Позиционные аргументы для функции запроса
            **kwargs: Именованные аргументы для функции запроса
            
        Returns:
            Результат запроса или словарь с ошибкой в случае сбоя
        """
        max_retries = kwargs.pop('max_retries', 3)
        retry_delay = kwargs.pop('retry_delay', 1)
        exponential_backoff = kwargs.pop('exponential_backoff', True)
        
        # Проверяем наличие необходимых секретов
        api_key = self.secret_manager.get_secret(api_name)
        if api_key is None:
            logger.error(f"Отсутствует ключ API для {api_name}")
            return {'error': 'API_KEY_MISSING', 'message': f'Отсутствует ключ API для {api_name}'}
        
        # Добавляем ключ API в аргументы запроса
        # Это уже защищено проверкой выше, поэтому api_key не может быть None в этой точке
        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = f"Bearer {api_key}"
        else:
            kwargs['headers'] = {'Authorization': f"Bearer {api_key}"}
        
        # Проверяем ограничение скорости запросов
        if api_name in self.rate_limits and self.rate_limits[api_name]['count'] >= self.rate_limits[api_name]['limit']:
            time_since_reset = time.time() - self.rate_limits[api_name]['reset_time']
            if time_since_reset < self.rate_limits[api_name]['period']:
                wait_time = self.rate_limits[api_name]['period'] - time_since_reset
                logger.warning(f"Достигнут лимит запросов для {api_name}. Ожидание {wait_time:.2f} секунд.")
                time.sleep(wait_time)
                # Сбрасываем счетчик
                self.rate_limits[api_name]['count'] = 0
                self.rate_limits[api_name]['reset_time'] = time.time()
        
        # Выполняем запрос с повторными попытками
        for retry in range(max_retries):
            try:
                # Увеличиваем счетчик запросов
                if api_name in self.rate_limits:
                    self.rate_limits[api_name]['count'] += 1
                
                # Выполняем запрос
                response = request_func(*args, **kwargs)
                
                # Проверяем код ответа
                if hasattr(response, 'status_code') and 400 <= response.status_code < 600:
                    if response.status_code == 429:  # Too Many Requests
                        # Обновляем информацию о лимите запросов
                        if 'Retry-After' in response.headers:
                            retry_after = int(response.headers['Retry-After'])
                        else:
                            retry_after = retry_delay * (2 ** retry if exponential_backoff else 1)
                        
                        logger.warning(f"Превышен лимит запросов для {api_name}. Ожидание {retry_after} секунд.")
                        time.sleep(retry_after)
                        continue
                    
                    logger.error(f"Ошибка запроса к {api_name}: {response.status_code} - {response.text if hasattr(response, 'text') else ''}")
                    
                    if retry < max_retries - 1:
                        delay = retry_delay * (2 ** retry if exponential_backoff else 1)
                        logger.info(f"Повторная попытка через {delay} секунд...")
                        time.sleep(delay)
                        continue
                    
                    return {'error': f'API_ERROR_{response.status_code}', 'message': response.text if hasattr(response, 'text') else 'Unknown error'}
                
                return response
                
            except Exception as e:
                logger.error(f"Ошибка при запросе к {api_name}: {str(e)}")
                logger.debug(traceback.format_exc())
                
                if retry < max_retries - 1:
                    delay = retry_delay * (2 ** retry if exponential_backoff else 1)
                    logger.info(f"Повторная попытка через {delay} секунд...")
                    time.sleep(delay)
                    continue
                
                return {'error': 'REQUEST_EXCEPTION', 'message': str(e)}
        
        return {'error': 'MAX_RETRIES_EXCEEDED', 'message': f'Превышено максимальное количество попыток ({max_retries})'}
    
    def set_rate_limit(self, api_name: str, limit: int, period: int = 60):
        """
        Устанавливает ограничение скорости запросов для API.
        
        Args:
            api_name: Имя API
            limit: Максимальное количество запросов
            period: Период в секундах
        """
        self.rate_limits[api_name] = {
            'limit': limit,
            'period': period,
            'count': 0,
            'reset_time': time.time()
        }

# Экземпляр менеджера секретов для использования в других модулях
secret_manager = APISecretManager()

# Экземпляр менеджера запросов для использования в других модулях
request_manager = APIRequestManager(secret_manager)

# Инициализация API
def initialize_apis():
    """
    Инициализирует доступные API и проверяет наличие необходимых ключей.
    
    Returns:
        Dict[str, bool]: Словарь с результатами инициализации API
    """
    results = {}
    
    # Проверка API OpenAI
    results['openai'] = secret_manager.has_secret('openai')
    if not results['openai']:
        logger.warning("API ключ для OpenAI не найден")
    
    # Проверка API Slack
    results['slack'] = secret_manager.has_secret('slack')
    if not results['slack']:
        logger.warning("API ключ для Slack не найден")
    
    # Проверка API Stripe
    results['stripe'] = secret_manager.has_secret('stripe')
    if not results['stripe']:
        logger.warning("API ключ для Stripe не найден")
    
    # Проверка API Twilio
    results['twilio'] = secret_manager.has_secret('twilio')
    if not results['twilio']:
        logger.warning("API ключ для Twilio не найден")
    
    # Установка ограничений скорости запросов
    if results['openai']:
        request_manager.set_rate_limit('openai', 60, 60)  # 60 запросов в минуту
    
    if results['slack']:
        request_manager.set_rate_limit('slack', 50, 60)  # 50 запросов в минуту
    
    # Логирование результатов инициализации
    initialized_apis = [api for api, status in results.items() if status]
    if initialized_apis:
        logger.info(f"Инициализировано {len(initialized_apis)} токенов API: {', '.join(initialized_apis)}")
    else:
        logger.warning("Не инициализировано ни одного токена API")
    
    return results