"""
Простой шаблонизатор для рендеринга HTML-шаблонов.

Поддерживает базовую подстановку переменных, условные выражения и циклы.
Используется для отображения шаблонов Medium-style интерфейса.

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional

# Настройка логирования
logger = logging.getLogger("template_engine")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Путь к директории с шаблонами
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Рендерит шаблон с заданным контекстом.
    
    Args:
        template_name: Имя шаблона
        context: Словарь с данными для подстановки
        
    Returns:
        str: Отрендеренный HTML
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    
    if not os.path.exists(template_path):
        logger.error(f"Шаблон не найден: {template_path}")
        return f"<p>Ошибка: шаблон {template_name} не найден</p>"
    
    try:
        # Читаем содержимое шаблона
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Обрабатываем блоки {% if ... %} ... {% endif %}
        template = _process_if_blocks(template, context)
        
        # Обрабатываем блоки {% for ... in ... %} ... {% endfor %}
        template = _process_for_blocks(template, context)
        
        # Подставляем значения переменных {{ var }}
        template = _substitute_variables(template, context)
        
        return template
    
    except Exception as e:
        logger.error(f"Ошибка при рендеринге шаблона {template_name}: {str(e)}")
        return f"<p>Ошибка при рендеринге шаблона: {str(e)}</p>"

def _process_if_blocks(template: str, context: Dict[str, Any]) -> str:
    """
    Обрабатывает блоки {% if ... %} ... {% endif %} в шаблоне.
    
    Args:
        template: Исходный шаблон
        context: Словарь с данными для подстановки
        
    Returns:
        str: Шаблон с обработанными if-блоками
    """
    pattern = r'{%\s*if\s+(.+?)\s*%}(.*?){%\s*endif\s*%}'
    
    def replace_if(match):
        condition = match.group(1)
        content = match.group(2)
        
        try:
            # Проверяем условие
            if _evaluate_condition(condition, context):
                return content
            else:
                return ''
        except Exception as e:
            logger.error(f"Ошибка при обработке условия {condition}: {str(e)}")
            return f"<p>Ошибка в условии: {condition}</p>"
    
    return re.sub(pattern, replace_if, template, flags=re.DOTALL)

def _process_for_blocks(template: str, context: Dict[str, Any]) -> str:
    """
    Обрабатывает блоки {% for ... in ... %} ... {% endfor %} в шаблоне.
    
    Args:
        template: Исходный шаблон
        context: Словарь с данными для подстановки
        
    Returns:
        str: Шаблон с обработанными for-блоками
    """
    pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
    
    def replace_for(match):
        var_name = match.group(1)
        collection_name = match.group(2)
        content = match.group(3)
        
        try:
            collection = context.get(collection_name, [])
            
            if not collection:
                return ''
            
            result = []
            for item in collection:
                # Создаем временный контекст с переменной цикла
                temp_context = dict(context)
                temp_context[var_name] = item
                
                # Рекурсивно обрабатываем содержимое цикла
                processed_content = _substitute_variables(content, temp_context)
                result.append(processed_content)
            
            return ''.join(result)
        except Exception as e:
            logger.error(f"Ошибка при обработке цикла for {var_name} in {collection_name}: {str(e)}")
            return f"<p>Ошибка в цикле: for {var_name} in {collection_name}</p>"
    
    return re.sub(pattern, replace_for, template, flags=re.DOTALL)

def _substitute_variables(template: str, context: Dict[str, Any]) -> str:
    """
    Подставляет значения переменных {{ var }} в шаблоне.
    
    Args:
        template: Исходный шаблон
        context: Словарь с данными для подстановки
        
    Returns:
        str: Шаблон с подставленными значениями переменных
    """
    pattern = r'{{(.*?)}}'
    
    def replace_var(match):
        var_name = match.group(1).strip()
        
        try:
            # Проверяем, есть ли переменная с таким именем в контексте
            if var_name in context:
                value = context[var_name]
                
                # Если значение помечено как "safe", не экранируем его
                if var_name.endswith('|safe'):
                    return str(value)
                
                # В противном случае экранируем специальные символы HTML
                return _escape_html(str(value))
            else:
                logger.warning(f"Переменная {var_name} не найдена в контексте")
                return ''
        except Exception as e:
            logger.error(f"Ошибка при подстановке переменной {var_name}: {str(e)}")
            return f"<p>Ошибка в переменной: {var_name}</p>"
    
    return re.sub(pattern, replace_var, template)

def _evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
    """
    Оценивает условие в блоке {% if ... %}.
    
    Args:
        condition: Условие
        context: Словарь с данными для подстановки
        
    Returns:
        bool: Результат проверки условия
    """
    # Простая проверка на наличие переменной
    if condition in context:
        return bool(context[condition])
    
    # Проверка отрицания
    if condition.startswith('not ') and condition[4:] in context:
        return not bool(context[condition[4:]])
    
    # Проверка равенства
    if ' == ' in condition:
        left, right = condition.split(' == ')
        left = left.strip()
        right = right.strip()
        
        if left in context:
            left_value = context[left]
        elif left.startswith('"') and left.endswith('"'):
            left_value = left[1:-1]
        else:
            try:
                left_value = eval(left)
            except:
                left_value = left
        
        if right in context:
            right_value = context[right]
        elif right.startswith('"') and right.endswith('"'):
            right_value = right[1:-1]
        else:
            try:
                right_value = eval(right)
            except:
                right_value = right
        
        return left_value == right_value
    
    # Проверка неравенства
    if ' != ' in condition:
        left, right = condition.split(' != ')
        left = left.strip()
        right = right.strip()
        
        if left in context:
            left_value = context[left]
        elif left.startswith('"') and left.endswith('"'):
            left_value = left[1:-1]
        else:
            try:
                left_value = eval(left)
            except:
                left_value = left
        
        if right in context:
            right_value = context[right]
        elif right.startswith('"') and right.endswith('"'):
            right_value = right[1:-1]
        else:
            try:
                right_value = eval(right)
            except:
                right_value = right
        
        return left_value != right_value
    
    # По умолчанию возвращаем False
    return False

def _escape_html(text: str) -> str:
    """
    Экранирует специальные символы HTML.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Экранированный текст
    """
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')