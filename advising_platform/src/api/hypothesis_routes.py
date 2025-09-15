#!/usr/bin/env python3
"""
API маршруты для работы с гипотезами и их проверки на соответствие стандарту.
"""

import os
import json
from flask import Blueprint, request, jsonify, send_file, current_app
from advising_platform.src.tools.hypothesis_validator import HypothesisValidator

# Создаем Blueprint для маршрутов гипотез
hypothesis_routes = Blueprint('hypothesis_routes', __name__)

# Создаем экземпляр валидатора гипотез
hypothesis_validator = HypothesisValidator()

@hypothesis_routes.route('/validate', methods=['POST'])
def validate_hypothesis():
    """
    Проверяет гипотезу на соответствие стандарту.
    
    Принимает содержимое гипотезы в запросе и возвращает результат проверки.
    """
    try:
        # Получаем данные из запроса
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Необходимо предоставить содержимое гипотезы в поле "content"'}), 400
            
        # Получаем содержимое гипотезы
        content = data['content']
        
        # Проверяем гипотезу
        validation_result = hypothesis_validator.validate_hypothesis(content)
        
        # Возвращаем результат проверки
        return jsonify({
            'is_valid': validation_result['is_valid'],
            'missing_sections': validation_result.get('missing_sections', []),
            'issues': validation_result.get('issues', []),
            'suggestions': validation_result.get('suggestions', []),
            'extracted_sections': validation_result.get('extracted_sections', {})
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при проверке гипотезы: {e}")
        return jsonify({'error': str(e)}), 500

@hypothesis_routes.route('/report', methods=['POST'])
def generate_report():
    """
    Генерирует отчет о проверке гипотезы.
    
    Принимает содержимое гипотезы в запросе и возвращает отчет в формате Markdown.
    """
    try:
        # Получаем данные из запроса
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Необходимо предоставить содержимое гипотезы в поле "content"'}), 400
            
        # Получаем содержимое гипотезы
        content = data['content']
        
        # Проверяем гипотезу
        validation_result = hypothesis_validator.validate_hypothesis(content)
        
        # Генерируем отчет
        report = hypothesis_validator.generate_report(validation_result)
        
        # Возвращаем отчет
        return jsonify({'report': report}), 200
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при генерации отчета: {e}")
        return jsonify({'error': str(e)}), 500

@hypothesis_routes.route('/template', methods=['GET'])
def get_template():
    """
    Возвращает шаблон для создания гипотезы.
    """
    template = """# Гипотеза: [Краткое описание]

<!-- 🔒 PROTECTED SECTION: BEGIN -->
updated: [Дата обновления]  
based on: 2.2 hypothesis standard 14 may 2025 0740 cet by ai assistant
status: draft
<!-- 🔒 PROTECTED SECTION: END -->

---

## 📝 Метаданные гипотезы

```
ID: H-XXX
Автор: [Имя автора]
Дата создания: [дд.мм.гггг]
Последнее обновление: [дд.мм.гггг]
Статус: Предложена
Приоритет: [P0/P1/P2/P3]
Связанные гипотезы: [ID связанных гипотез]
Теги: [ключевые слова, разделенные запятыми]
```

## 🧪 Формулировка гипотезы (расширенный формат)

**Наблюдение:** [что мы заметили, какую проблему или возможность увидели]

Мы верим, что [действие/изменение] для [пользователь/сегмент] приведет к [ожидаемый результат].

Это произойдет, потому что [механизм/причинно-следственная связь].

Мы поймем, что это правда, когда увидим [измеримый критерий успеха].

**Риски и допущения:**
- [Риск 1]
- [Риск 2]
- [Допущение 1]
- [Допущение 2]

## 🔍 Метод проверки гипотезы

1. **Тип тестирования:** [A/B тест, пользовательские интервью, опрос, прототип]
2. **Временной период:** [продолжительность тестирования]
3. **Целевые метрики:**
   - Основная: [ключевая метрика]
   - Вторичные:
     - [Вторичная метрика 1]
     - [Вторичная метрика 2]

4. **Методология:**
   - [Описание процесса тестирования]
   - [Размер выборки]
   - [Критерии оценки]

## 🔄 Проверка соответствия критериям качественной гипотезы

1. **Конкретность:** [оценка]
2. **Тестируемость:** [оценка]
3. **Фальсифицируемость:** [оценка]
4. **Основанность на данных:** [оценка]
5. **Причинно-следственная связь:** [оценка]
6. **Временное ограничение:** [оценка]
7. **Компактность:** [оценка]

## 🔄 Результаты проверки и последующие шаги

[Заполняется после проведения тестирования]
"""
    
    return jsonify({'template': template}), 200


def register_routes(app):
    """
    Регистрирует маршруты API в приложении Flask.
    
    Args:
        app: Приложение Flask.
    """
    app.register_blueprint(hypothesis_routes, url_prefix='/api/hypothesis')
