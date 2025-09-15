#!/usr/bin/env python3
"""
API сервер Advising Platform.

Предоставляет API для работы со стандартами, задачами, инцидентами
и другими документами.
"""

import os
import sys
import argparse
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")

def create_app():
    """
    Создает и настраивает экземпляр приложения Flask.
    
    Returns:
        Настроенное приложение Flask.
    """
    app = Flask(__name__)
    CORS(app)
    
    # Регистрация маршрутов API
    try:
        # Настраиваем пути импорта
        import sys
        from pathlib import Path
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent  # Поднимаемся до корня проекта
        module_dir = current_dir.parent.parent  # advising_platform директория
        
        # Добавляем пути в sys.path если их там нет
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        if str(module_dir) not in sys.path:
            sys.path.insert(0, str(module_dir))
            
        # Регистрация маршрута для проверки статуса системы
        try:
            from src.api.routes.status import status_blueprint
            app.register_blueprint(status_blueprint, url_prefix='/api')
            logger.info("Status API зарегистрировано")
        except ImportError as e:
            logger.warning(f"Status API не зарегистрировано: {e}")
            
        # Регистрация маршрута для информации о реорганизации
        try:
            from src.api.routes.reorganization import reorganization_blueprint
            app.register_blueprint(reorganization_blueprint, url_prefix='/api')
            logger.info("Reorganization API зарегистрировано")
        except ImportError as e:
            logger.warning(f"Reorganization API не зарегистрировано: {e}")
            
        # Регистрация маршрута для работы с внешними API
        try:
            from src.api.routes.external_api import external_api_blueprint
            app.register_blueprint(external_api_blueprint, url_prefix='/api')
            logger.info("External API зарегистрировано")
        except ImportError as e:
            logger.warning(f"External API не зарегистрировано: {e}")
            
        # Маршруты для работы со стандартами
        from src.api.standards_routes import register_routes as register_standards_routes
        register_standards_routes(app)
        logger.info("Standards API зарегистрировано")
        
        # Маршруты для работы с гипотезами
        from src.api.hypothesis_routes import register_routes as register_hypothesis_routes
        register_hypothesis_routes(app)
        logger.info("Hypothesis API зарегистрировано")
        
        # Маршруты для работы с индексатором документов
        try:
            from src.api.indexer_routes import register_routes as register_indexer_routes
            register_indexer_routes(app)
            logger.info("Indexer API зарегистрировано")
        except ImportError as e:
            logger.warning(f"Indexer API не зарегистрировано: {e}")
        
        # Маршруты для работы с кэшем документов
        from src.api.cache_routes import register_routes as register_cache_routes
        register_cache_routes(app)
        logger.info("Cache API зарегистрировано")
        
        # Настраиваем интеграцию с системой архивации
        try:
            from src.cache.archive_integration import setup_archive_integration
            from src.cache.document_cache import DocumentCacheManager
            
            # Получаем экземпляр менеджера кэша
            cache_manager = DocumentCacheManager.get_instance()
            
            # Настраиваем интеграцию с архивацией
            setup_archive_integration(cache_manager, [
                '[standards .md]',
                '[todo · incidents]'
            ])
            
            logger.info("Интеграция кэша с системой архивации настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить интеграцию с архивацией: {e}")
            
        # Маршруты для валидации Todo документов
        try:
            from src.api.todo_routes import register_routes as register_todo_routes
            register_todo_routes(app)
            logger.info("Todo API зарегистрировано")
        except ImportError as e:
            logger.warning(f"Todo API не зарегистрировано: {e}")
        
        # Маршруты для работы с инициализатором контекста
        try:
            from src.api.context_routes import register_routes as register_context_routes
            register_context_routes(app)
            logger.info("Context API зарегистрировано")
        except ImportError as e:
            logger.warning(f"Context API не зарегистрировано: {e}")
        
    except ImportError as e:
        logger.error(f"Ошибка при импорте маршрутов API: {e}")
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Проверка работоспособности API."""
        return jsonify({"status": "ok"})
    
    return app

def main():
    """
    Основная функция для запуска API сервера.
    
    Обрабатывает аргументы командной строки и запускает сервер.
    """
    parser = argparse.ArgumentParser(description='API сервер Advising Platform')
    parser.add_argument('--host', default='0.0.0.0', help='Хост для прослушивания')
    parser.add_argument('--port', type=int, default=5003, help='Порт для прослушивания')
    parser.add_argument('--debug', action='store_true', help='Запуск в режиме отладки')
    parser.add_argument('--preload-context', action='store_true', help='Предзагрузка контекста при запуске')
    
    args = parser.parse_args()
    
    # Предзагрузка контекста, если запрошено
    if args.preload_context:
        try:
            from src.cache.context_initializer import initialize_context
            logger.info("Запуск предзагрузки контекста...")
            success = initialize_context(force=True)
            if success:
                logger.info("Контекст успешно предзагружен")
            else:
                logger.warning("Ошибка при предзагрузке контекста")
        except Exception as e:
            logger.error(f"Не удалось предзагрузить контекст: {e}")
    
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()