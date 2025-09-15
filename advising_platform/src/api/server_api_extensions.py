"""
Расширение API-сервера для обслуживания веб-интерфейса HeroesGPT Bot Reviews

Данное расширение добавляет функциональность для:
1. Обслуживания статических файлов веб-интерфейса
2. Предоставления списка доступных обзоров
3. Сохранения и получения комментариев к обзорам
"""

import os
import json
import http.server
import socketserver
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import glob

# Настройки
HEROES_GPT_BOT_DIR = 'projects/heroes-gpt-bot'
STATIC_FILES_DIR = os.path.join(HEROES_GPT_BOT_DIR, 'src')
REVIEWS_DIR = HEROES_GPT_BOT_DIR
COMMENTS_FILE = os.path.join(HEROES_GPT_BOT_DIR, 'data/comments.json')

def init_comments_storage():
    """Инициализирует хранилище комментариев, если оно не существует."""
    os.makedirs(os.path.dirname(COMMENTS_FILE), exist_ok=True)
    if not os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

def get_reviews_list() -> List[Dict[str, str]]:
    """Получает список всех доступных обзоров."""
    reviews = []
    # Получаем все Markdown файлы в директории проекта
    md_files = glob.glob(f"{REVIEWS_DIR}/*.md")
    
    for file_path in md_files:
        # Исключаем служебные файлы, такие как README.md
        if os.path.basename(file_path) == "README.md":
            continue
            
        # Получаем базовое имя файла
        filename = os.path.basename(file_path)
        
        # Извлекаем метаданные из файла
        title = filename  # По умолчанию используем имя файла
        date = ""
        review_type = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Ищем заголовок в формате Markdown
                title_match = content.split('\n', 10)
                for line in title_match:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                # Извлекаем метаданные из YAML-фронтматтера
                if content.startswith('---'):
                    meta_end = content.find('---', 3)
                    if meta_end > 0:
                        meta_content = content[3:meta_end]
                        for line in meta_content.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                key = key.strip().lower()
                                value = value.strip()
                                
                                if key == 'date' or key == 'updated':
                                    date = value
                                elif key == 'type' or key == 'artifact type':
                                    review_type = value
        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {e}")
            
        # Добавляем обзор в список
        reviews.append({
            'id': filename,
            'title': title,
            'date': date,
            'type': review_type,
            'path': file_path
        })
    
    # Сортируем по дате (новые сверху)
    reviews.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
    
    return reviews

def get_review_content(review_id: str) -> Optional[Dict[str, Any]]:
    """Получает содержимое обзора по ID."""
    file_path = os.path.join(REVIEWS_DIR, review_id)
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            'id': review_id,
            'content': content,
            'path': file_path
        }
    except Exception as e:
        print(f"Ошибка при чтении файла {review_id}: {e}")
        return None

def get_comments(review_id: str) -> List[Dict[str, Any]]:
    """Получает все комментарии для указанного обзора."""
    init_comments_storage()
    
    try:
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            all_comments = json.load(f)
            
        return all_comments.get(review_id, [])
    except Exception as e:
        print(f"Ошибка при получении комментариев: {e}")
        return []

def add_comment(review_id: str, author: str, text: str, highlighted_text: Optional[str] = None) -> bool:
    """Добавляет новый комментарий к обзору."""
    init_comments_storage()
    
    try:
        # Загружаем существующие комментарии
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            all_comments = json.load(f)
        
        # Создаем запись для обзора, если она еще не существует
        if review_id not in all_comments:
            all_comments[review_id] = []
        
        # Добавляем новый комментарий
        new_comment = {
            'id': f"{len(all_comments[review_id]) + 1}",
            'author': author,
            'text': text,
            'highlighted_text': highlighted_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        all_comments[review_id].append(new_comment)
        
        # Сохраняем обновленные комментарии
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_comments, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Ошибка при добавлении комментария: {e}")
        return False

def serve_static_file(path: str) -> Tuple[int, Dict[str, str], bytes]:
    """Обслуживает статический файл."""
    # Преобразуем путь для избежания обхода директории
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith('..'):
        return 403, {'Content-Type': 'text/plain'}, b'Forbidden'
    
    # Полный путь к файлу
    file_path = os.path.join(STATIC_FILES_DIR, normalized_path)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return 404, {'Content-Type': 'text/plain'}, b'File not found'
    
    # Определение типа содержимого на основе расширения файла
    content_type = 'text/plain'
    if file_path.endswith('.html'):
        content_type = 'text/html'
    elif file_path.endswith('.js'):
        content_type = 'application/javascript'
    elif file_path.endswith('.css'):
        content_type = 'text/css'
    elif file_path.endswith('.json'):
        content_type = 'application/json'
    elif file_path.endswith('.png'):
        content_type = 'image/png'
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif file_path.endswith('.svg'):
        content_type = 'image/svg+xml'
    
    # Чтение файла
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return 200, {'Content-Type': content_type}, content
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return 500, {'Content-Type': 'text/plain'}, f'Error reading file: {str(e)}'.encode('utf-8')

def register_api_extensions(http_handler_class):
    """
    Расширяет обработчик HTTP-запросов дополнительными маршрутами.
    
    Args:
        http_handler_class: Класс обработчика HTTP-запросов, который нужно расширить
    """
    original_do_get = http_handler_class.do_GET
    
    def extended_do_get(self):
        """Расширенный метод обработки GET-запросов."""
        # Разбор пути запроса
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        # Обработка запросов к API интерфейса HeroesGPT Bot Reviews
        if path == '/api/reviews/list':
            # Получение списка всех обзоров
            reviews = get_reviews_list()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'reviews': reviews}).encode('utf-8'))
            return
            
        elif path.startswith('/api/reviews/content/'):
            # Получение содержимого конкретного обзора
            review_id = path[len('/api/reviews/content/'):]
            review_id = urllib.parse.unquote(review_id)
            
            review = get_review_content(review_id)
            if review:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(review).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Review not found'}).encode('utf-8'))
            return
            
        elif path.startswith('/api/reviews/comments/'):
            # Получение комментариев к обзору
            review_id = path[len('/api/reviews/comments/'):]
            review_id = urllib.parse.unquote(review_id)
            
            comments = get_comments(review_id)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'comments': comments}).encode('utf-8'))
            return
            
        elif path == '/api/heroes-gpt-bot/static':
            # Обслуживание статических файлов
            file_path = query.get('path', [''])[0]
            if not file_path:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing path parameter'}).encode('utf-8'))
                return
            
            status, headers, content = serve_static_file(file_path)
            self.send_response(status)
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(content)
            return
            
        elif path == '/api/heroes-gpt-bot/web':
            # Перенаправление на веб-интерфейс
            self.send_response(302)
            self.send_header('Location', f'/api/heroes-gpt-bot/static?path=index.html')
            self.end_headers()
            return
        
        # Если путь не соответствует ни одному из расширений, используем оригинальный обработчик
        original_do_get(self)
    
    # Заменяем оригинальный метод расширенным
    http_handler_class.do_GET = extended_do_get
    
    # Добавляем обработку POST-запросов для комментариев
    original_do_post = getattr(http_handler_class, 'do_POST', lambda self: self.send_error(405))
    
    def extended_do_post(self):
        """Расширенный метод обработки POST-запросов."""
        # Разбор пути запроса
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/reviews/comments/add':
            # Получение длины данных
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                # Парсинг JSON-данных
                data = json.loads(post_data)
                
                # Проверка обязательных полей
                if 'review_id' not in data or 'author' not in data or 'text' not in data:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode('utf-8'))
                    return
                
                # Добавление комментария
                success = add_comment(
                    data['review_id'],
                    data['author'],
                    data['text'],
                    data.get('highlighted_text')
                )
                
                if success:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Failed to add comment'}).encode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return
        
        # Если путь не соответствует ни одному из расширений, используем оригинальный обработчик
        original_do_post(self)
    
    # Заменяем оригинальный метод расширенным
    http_handler_class.do_POST = extended_do_post

# Пример использования:
# register_api_extensions(BaseHTTPRequestHandler)