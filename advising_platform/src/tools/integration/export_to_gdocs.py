#!/usr/bin/env python3
"""
Экспортер Markdown в Google Docs
Позволяет экспортировать Markdown-файлы в Google Docs с сохранением форматирования
и структуры документа в соответствии с фирменным стилем.
"""

import os
import sys
import json
import argparse
import markdown
import mimetypes
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Google API
import google.auth
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

# Настройки для OAuth2
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]

# Каталог для хранения токенов и конфигурации
CONFIG_DIR = '.gdocs_export'
TOKEN_PATH = os.path.join(CONFIG_DIR, 'token.json')
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, 'credentials.json')
SERVICE_ACCOUNT_PATH = os.path.join(CONFIG_DIR, 'service_account.json')

# Константы
HEROES_FOLDER_NAME = 'HeroesGPT Reviews'
HEROES_BRAND_COLOR = {'red': 0.0, 'green': 0.34, 'blue': 0.70}  # #0056b3
DEFAULT_FONT_FAMILY = 'Arial'

# Стили для элементов документа
STYLES = {
    'title': {
        'fontSize': 28,
        'bold': True,
        'color': HEROES_BRAND_COLOR,
        'alignment': 'CENTER'
    },
    'heading1': {
        'fontSize': 24,
        'bold': True, 
        'color': HEROES_BRAND_COLOR,
        'spaceAbove': 20,
        'spaceBelow': 10
    },
    'heading2': {
        'fontSize': 18,
        'bold': True,
        'color': {'red': 0.0, 'green': 0.41, 'blue': 0.85},  # #0069d9
        'spaceAbove': 16,
        'spaceBelow': 8
    },
    'heading3': {
        'fontSize': 14,
        'bold': True,
        'color': {'red': 0.0, 'green': 0.48, 'blue': 1.0},  # #007bff
        'spaceAbove': 12,
        'spaceBelow': 6
    },
    'normal': {
        'fontSize': 11,
        'lineSpacing': 1.5
    },
    'code': {
        'fontFamily': 'Consolas',
        'fontSize': 10,
        'backgroundColor': {'red': 0.96, 'green': 0.96, 'blue': 0.96}  # #f5f5f5
    },
    'table': {
        'borderColor': {'red': 0.87, 'green': 0.87, 'blue': 0.87},  # #dddddd
        'headerBackgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}  # #f2f2f2
    },
    'blockquote': {
        'marginLeft': 20,
        'italics': True,
        'color': {'red': 0.33, 'green': 0.33, 'blue': 0.33},  # #555555
        'borderLeft': True,
        'borderLeftColor': HEROES_BRAND_COLOR,
        'borderLeftWidth': 4
    }
}


def get_credentials():
    """
    Получает учетные данные для доступа к Google API.
    Предпочтительно использует Service Account, если доступен,
    иначе пытается использовать OAuth2.
    
    Returns:
        Credentials: Объект с учетными данными
    """
    # Создаем директорию для конфигурации, если её нет
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Проверяем наличие Service Account
    if os.path.exists(SERVICE_ACCOUNT_PATH):
        return service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    
    # Иначе используем OAuth2
    creds = None
    
    # Проверяем наличие сохраненного токена
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_info(
            json.load(open(TOKEN_PATH)), SCOPES)
    
    # Проверяем валидность токена
    if creds and creds.valid:
        return creds
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # Если токена нет или он невалиден, запускаем процесс аутентификации
        if not os.path.exists(CREDENTIALS_PATH):
            print("Ошибка: Файл учетных данных OAuth2 не найден.")
            print(f"Пожалуйста, поместите credentials.json в {CONFIG_DIR}/")
            sys.exit(1)
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
    
    # Сохраняем токен для следующего использования
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())
    
    return creds


def find_or_create_folder(drive_service, folder_name, parent_id=None):
    """
    Находит или создает папку в Google Drive.
    
    Args:
        drive_service: Сервис Google Drive
        folder_name: Имя папки
        parent_id: ID родительской папки (если есть)
    
    Returns:
        str: ID папки
    """
    # Формируем запрос для поиска папки
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    response = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    
    # Проверяем, найдена ли папка
    folders = response.get('files', [])
    if folders:
        return folders[0]['id']
    
    # Если папка не найдена, создаем новую
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_id:
        folder_metadata['parents'] = [parent_id]
    
    folder = drive_service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    
    return folder.get('id')


def create_document(drive_service, docs_service, title, folder_id=None):
    """
    Создает новый документ Google Docs.
    
    Args:
        drive_service: Сервис Google Drive
        docs_service: Сервис Google Docs
        title: Название документа
        folder_id: ID папки для размещения документа
    
    Returns:
        tuple: (document_id, document_url)
    """
    # Создаем пустой документ
    document = docs_service.documents().create(
        body={'title': title}
    ).execute()
    
    document_id = document.get('documentId')
    
    # Если указана папка, перемещаем документ в неё
    if folder_id:
        file = drive_service.files().get(
            fileId=document_id,
            fields='parents'
        ).execute()
        
        previous_parents = ','.join(file.get('parents'))
        
        # Перемещаем файл в указанную папку
        drive_service.files().update(
            fileId=document_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
    
    # Получаем ссылку на документ
    document_url = f"https://docs.google.com/document/d/{document_id}/edit"
    
    return document_id, document_url


def parse_markdown(md_content):
    """
    Парсит Markdown-контент и преобразует его в структуру для Google Docs API.
    
    Args:
        md_content: Содержимое Markdown-файла
    
    Returns:
        list: Список элементов для создания документа
    """
    # Конвертируем Markdown в HTML для анализа структуры
    html = markdown.markdown(md_content, extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.attr_list'
    ])
    
    # TODO: Реализовать полный парсинг HTML в структуру для Google Docs API
    # В данной версии реализуем базовое преобразование
    
    # Разбиваем контент на строки для анализа
    lines = md_content.split('\n')
    requests = []
    current_position = 1  # Начальная позиция (1 - после заголовка)
    
    # Проходим по каждой строке
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Пропускаем пустые строки
        if not line:
            i += 1
            continue
        
        # Обработка заголовков
        if line.startswith('#'):
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
            
            if level > 6:
                level = 6
            
            heading_text = line[level:].strip()
            style_key = f'heading{level}' if level <= 3 else 'heading3'
            
            requests.append({
                'insertText': {
                    'location': {'index': current_position},
                    'text': heading_text + '\n'
                }
            })
            
            end_index = current_position + len(heading_text) + 1
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_position,
                        'endIndex': end_index - 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': f'HEADING_{level}',
                        'spaceAbove': {'magnitude': STYLES[style_key]['spaceAbove'], 'unit': 'PT'},
                        'spaceBelow': {'magnitude': STYLES[style_key]['spaceBelow'], 'unit': 'PT'}
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow'
                }
            })
            
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': current_position,
                        'endIndex': end_index - 1
                    },
                    'textStyle': {
                        'fontSize': {'magnitude': STYLES[style_key]['fontSize'], 'unit': 'PT'},
                        'bold': STYLES[style_key]['bold'],
                        'foregroundColor': STYLES[style_key]['color']
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })
            
            current_position = end_index
            i += 1
            continue
        
        # Обработка списков
        if line.startswith('- ') or line.startswith('* ') or (line[0].isdigit() and line[1:].startswith('. ')):
            list_items = []
            is_ordered = line[0].isdigit()
            
            # Собираем элементы списка
            while i < len(lines) and (lines[i].strip().startswith('- ') or 
                                    lines[i].strip().startswith('* ') or
                                    (lines[i].strip() and lines[i].strip()[0].isdigit() and 
                                     lines[i].strip()[1:].startswith('. '))):
                item_text = lines[i].strip()
                if is_ordered:
                    # Удаляем номер и точку
                    item_text = item_text[item_text.find('.')+1:].strip()
                else:
                    # Удаляем маркер
                    item_text = item_text[1:].strip()
                
                list_items.append(item_text)
                i += 1
            
            # Создаем элементы списка
            list_text = ""
            for item in list_items:
                list_text += item + "\n"
            
            requests.append({
                'insertText': {
                    'location': {'index': current_position},
                    'text': list_text
                }
            })
            
            # Применяем стиль списка к каждому элементу
            for j, item in enumerate(list_items):
                item_start = current_position + sum(len(item) + 1 for item in list_items[:j])
                item_end = item_start + len(item)
                
                requests.append({
                    'createParagraphBullets': {
                        'range': {
                            'startIndex': item_start,
                            'endIndex': item_end + 1
                        },
                        'bulletPreset': 'NUMBERED_DIGIT_PERIOD' if is_ordered else 'BULLET_DISC_CIRCLE_SQUARE'
                    }
                })
            
            current_position += len(list_text)
            continue
        
        # Обработка блоков кода
        if line.startswith('```'):
            # Получаем язык программирования (если указан)
            lang = line[3:].strip()
            code_block = []
            i += 1
            
            # Собираем весь код до закрывающих ```
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_block.append(lines[i])
                i += 1
            
            i += 1  # Пропускаем закрывающий ```
            
            # Объединяем весь код в одну строку с переносами
            code_text = '\n'.join(code_block) + '\n'
            
            requests.append({
                'insertText': {
                    'location': {'index': current_position},
                    'text': code_text
                }
            })
            
            # Применяем стиль кода
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': current_position,
                        'endIndex': current_position + len(code_text) - 1
                    },
                    'textStyle': {
                        'fontFamily': STYLES['code']['fontFamily'],
                        'fontSize': {'magnitude': STYLES['code']['fontSize'], 'unit': 'PT'}
                    },
                    'fields': 'fontFamily,fontSize'
                }
            })
            
            # Добавляем фон для блока кода
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_position,
                        'endIndex': current_position + len(code_text)
                    },
                    'paragraphStyle': {
                        'shading': {
                            'backgroundColor': STYLES['code']['backgroundColor']
                        }
                    },
                    'fields': 'shading.backgroundColor'
                }
            })
            
            current_position += len(code_text)
            continue
        
        # Обработка таблиц пока не реализована полностью
        # TODO: Добавить полную поддержку таблиц Markdown
        if line.startswith('|') and line.endswith('|'):
            # Простое определение таблицы - первая строка и следующая должна содержать разделители
            if i + 1 < len(lines) and lines[i+1].strip().startswith('|') and lines[i+1].strip().endswith('|'):
                separator_line = lines[i+1].strip()
                if all(c == '|' or c == '-' or c == ':' or c == ' ' for c in separator_line):
                    # Это таблица, пропускаем сложную обработку в этой версии
                    # и добавляем как простой текст с предупреждением
                    requests.append({
                        'insertText': {
                            'location': {'index': current_position},
                            'text': "Таблица будет поддержана в следующей версии\n\n"
                        }
                    })
                    
                    # Пропускаем строки таблицы
                    while i < len(lines) and lines[i].strip().startswith('|'):
                        i += 1
                    
                    current_position += len("Таблица будет поддержана в следующей версии\n\n")
                    continue
        
        # Обработка цитат
        if line.startswith('>'):
            quote_lines = []
            
            # Собираем все строки цитаты
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_text = lines[i].strip()[1:].strip()  # Удаляем символ '>' и пробелы
                quote_lines.append(quote_text)
                i += 1
            
            # Объединяем все строки цитаты
            quote_text = ' '.join(quote_lines) + '\n'
            
            requests.append({
                'insertText': {
                    'location': {'index': current_position},
                    'text': quote_text
                }
            })
            
            # Применяем стиль цитаты
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_position,
                        'endIndex': current_position + len(quote_text)
                    },
                    'paragraphStyle': {
                        'indentStart': {'magnitude': STYLES['blockquote']['marginLeft'], 'unit': 'PT'},
                        'borderLeft': {
                            'color': STYLES['blockquote']['borderLeftColor'],
                            'width': {'magnitude': STYLES['blockquote']['borderLeftWidth'], 'unit': 'PT'},
                            'padding': {'magnitude': 4, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        }
                    },
                    'fields': 'indentStart,borderLeft'
                }
            })
            
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': current_position,
                        'endIndex': current_position + len(quote_text) - 1
                    },
                    'textStyle': {
                        'italic': STYLES['blockquote']['italics'],
                        'foregroundColor': STYLES['blockquote']['color']
                    },
                    'fields': 'italic,foregroundColor'
                }
            })
            
            current_position += len(quote_text)
            continue
        
        # Обычный параграф
        paragraph_lines = []
        paragraph_lines.append(line)
        i += 1
        
        # Собираем многострочный параграф
        while i < len(lines) and lines[i].strip() and not (
            lines[i].strip().startswith('#') or
            lines[i].strip().startswith('- ') or
            lines[i].strip().startswith('* ') or
            (lines[i].strip() and lines[i].strip()[0].isdigit() and lines[i].strip()[1:].startswith('. ')) or
            lines[i].strip().startswith('```') or
            lines[i].strip().startswith('|') or
            lines[i].strip().startswith('>')
        ):
            paragraph_lines.append(lines[i].strip())
            i += 1
        
        paragraph_text = ' '.join(paragraph_lines) + '\n'
        
        # TODO: Обработка спецсимволов внутри параграфа (**жирный**, *курсив*, [ссылка](url))
        
        requests.append({
            'insertText': {
                'location': {'index': current_position},
                'text': paragraph_text
            }
        })
        
        # Применяем стиль для обычного текста
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': current_position,
                    'endIndex': current_position + len(paragraph_text)
                },
                'paragraphStyle': {
                    'lineSpacing': STYLES['normal']['lineSpacing'] * 100
                },
                'fields': 'lineSpacing'
            }
        })
        
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': current_position,
                    'endIndex': current_position + len(paragraph_text) - 1
                },
                'textStyle': {
                    'fontSize': {'magnitude': STYLES['normal']['fontSize'], 'unit': 'PT'},
                    'fontFamily': DEFAULT_FONT_FAMILY
                },
                'fields': 'fontSize,fontFamily'
            }
        })
        
        current_position += len(paragraph_text)
    
    return requests


def add_title_page(requests, title, filename, date):
    """
    Добавляет титульную страницу в документ.
    
    Args:
        requests: Список запросов к API Google Docs
        title: Заголовок документа
        filename: Имя исходного файла
        date: Дата создания документа
    
    Returns:
        list: Обновленный список запросов
    """
    # Добавляем логотип (используем заголовок как изображение в этой версии)
    logo_text = "HeroesGPT Review"
    requests.insert(0, {
        'insertText': {
            'location': {'index': 1},
            'text': logo_text + '\n\n'
        }
    })
    
    logo_end_index = 1 + len(logo_text) + 2
    
    requests.insert(1, {
        'updateTextStyle': {
            'range': {
                'startIndex': 1,
                'endIndex': 1 + len(logo_text)
            },
            'textStyle': {
                'fontSize': {'magnitude': 14, 'unit': 'PT'},
                'foregroundColor': HEROES_BRAND_COLOR,
                'bold': True
            },
            'fields': 'fontSize,foregroundColor,bold'
        }
    })
    
    # Добавляем заголовок
    requests.insert(2, {
        'insertText': {
            'location': {'index': logo_end_index},
            'text': title + '\n\n'
        }
    })
    
    title_end_index = logo_end_index + len(title) + 2
    
    requests.insert(3, {
        'updateTextStyle': {
            'range': {
                'startIndex': logo_end_index,
                'endIndex': logo_end_index + len(title)
            },
            'textStyle': {
                'fontSize': {'magnitude': STYLES['title']['fontSize'], 'unit': 'PT'},
                'foregroundColor': STYLES['title']['color'],
                'bold': STYLES['title']['bold']
            },
            'fields': 'fontSize,foregroundColor,bold'
        }
    })
    
    requests.insert(4, {
        'updateParagraphStyle': {
            'range': {
                'startIndex': logo_end_index,
                'endIndex': logo_end_index + len(title)
            },
            'paragraphStyle': {
                'alignment': STYLES['title']['alignment']
            },
            'fields': 'alignment'
        }
    })
    
    # Добавляем метаданные
    metadata_text = f"Исходный файл: {filename}\nДата создания: {date}\n\n"
    requests.insert(5, {
        'insertText': {
            'location': {'index': title_end_index},
            'text': metadata_text
        }
    })
    
    metadata_end_index = title_end_index + len(metadata_text)
    
    requests.insert(6, {
        'updateTextStyle': {
            'range': {
                'startIndex': title_end_index,
                'endIndex': title_end_index + len(metadata_text) - 2
            },
            'textStyle': {
                'fontSize': {'magnitude': 10, 'unit': 'PT'},
                'foregroundColor': {'red': 0.5, 'green': 0.5, 'blue': 0.5}
            },
            'fields': 'fontSize,foregroundColor'
        }
    })
    
    # Добавляем разрыв страницы
    requests.insert(7, {
        'insertPageBreak': {
            'location': {
                'index': metadata_end_index
            }
        }
    })
    
    # Сдвигаем все остальные индексы на длину добавленного содержимого
    offset = metadata_end_index
    for i in range(8, len(requests)):
        if 'insertText' in requests[i]:
            requests[i]['insertText']['location']['index'] += offset
        elif 'updateTextStyle' in requests[i]:
            requests[i]['updateTextStyle']['range']['startIndex'] += offset
            requests[i]['updateTextStyle']['range']['endIndex'] += offset
        elif 'updateParagraphStyle' in requests[i]:
            requests[i]['updateParagraphStyle']['range']['startIndex'] += offset
            requests[i]['updateParagraphStyle']['range']['endIndex'] += offset
    
    return requests


def add_headers_footers(document_id, docs_service, title):
    """
    Добавляет верхний и нижний колонтитулы в документ.
    
    Args:
        document_id: ID документа
        docs_service: Сервис Google Docs
        title: Заголовок для колонтитула
    """
    # В текущей версии API Google Docs нет прямого способа установки колонтитулов
    # TODO: Реализовать через createHeader/createFooter, когда они станут доступны
    pass


def update_document_with_markdown(md_file, doc_id, docs_service):
    """
    Обновляет документ Google Docs содержимым из Markdown-файла.
    
    Args:
        md_file: Путь к Markdown-файлу
        doc_id: ID документа Google Docs
        docs_service: Сервис Google Docs
    
    Returns:
        bool: True если обновление успешно, иначе False
    """
    try:
        # Читаем содержимое Markdown-файла
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Получаем заголовок из имени файла или первой строки содержимого
        filename = os.path.basename(md_file)
        title = filename
        
        # Проверяем, есть ли заголовок первого уровня в начале файла
        lines = md_content.split('\n')
        if lines and lines[0].startswith('# '):
            title = lines[0][2:].strip()
        
        # Получаем дату создания
        date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Парсим Markdown-контент
        requests = parse_markdown(md_content)
        
        # Добавляем титульную страницу
        requests = add_title_page(requests, title, filename, date)
        
        # Обновляем документ
        result = docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        # Добавляем колонтитулы
        add_headers_footers(doc_id, docs_service, title)
        
        return True
    except Exception as e:
        print(f"Ошибка при обновлении документа: {str(e)}")
        return False


def share_document(drive_service, doc_id, access_type='anyone', role='reader', email=None):
    """
    Настраивает доступ к документу.
    
    Args:
        drive_service: Сервис Google Drive
        doc_id: ID документа
        access_type: Тип доступа ('user', 'group', 'domain', 'anyone')
        role: Роль ('owner', 'writer', 'commenter', 'reader')
        email: Email пользователя или группы (для access_type 'user' или 'group')
    
    Returns:
        dict: Информация о настройке доступа
    """
    permission = {
        'type': access_type,
        'role': role
    }
    
    if access_type in ['user', 'group'] and email:
        permission['emailAddress'] = email
    
    return drive_service.permissions().create(
        fileId=doc_id,
        body=permission,
        fields='id'
    ).execute()


def export_to_google_docs(md_file, title=None, access_type='anyone', role='reader', email=None):
    """
    Экспортирует Markdown-файл в Google Docs.
    
    Args:
        md_file: Путь к Markdown-файлу
        title: Название документа Google Docs (опционально)
        access_type: Тип доступа к документу
        role: Роль для доступа
        email: Email для отправки доступа (если access_type = 'user' или 'group')
    
    Returns:
        str: URL документа Google Docs или None в случае ошибки
    """
    try:
        # Проверяем наличие файла
        if not os.path.exists(md_file):
            print(f"Ошибка: Файл {md_file} не найден.")
            return None
        
        # Получаем название документа
        if not title:
            # Используем имя файла без расширения или первый заголовок из содержимого
            filename = os.path.basename(md_file)
            title = os.path.splitext(filename)[0]
            
            # Проверяем, есть ли заголовок первого уровня в начале файла
            with open(md_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# '):
                    title = first_line[2:].strip()
        
        # Получаем учетные данные и создаем сервисы
        creds = get_credentials()
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)
        
        # Находим или создаем папку для обзоров
        folder_id = find_or_create_folder(drive_service, HEROES_FOLDER_NAME)
        
        # Создаем новый документ
        doc_id, doc_url = create_document(drive_service, docs_service, title, folder_id)
        
        # Обновляем документ содержимым из Markdown
        if update_document_with_markdown(md_file, doc_id, docs_service):
            # Настраиваем доступ к документу
            share_document(drive_service, doc_id, access_type, role, email)
            
            print(f"Документ успешно создан: {doc_url}")
            return doc_url
        else:
            print("Ошибка при обновлении документа.")
            return None
    
    except Exception as e:
        print(f"Ошибка при экспорте в Google Docs: {str(e)}")
        return None


def setup_gdocs_export():
    """
    Настраивает окружение для экспорта в Google Docs.
    Создает необходимые директории и проверяет наличие учетных данных.
    """
    # Создаем директорию для конфигурации
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Проверяем наличие учетных данных
    if not (os.path.exists(SERVICE_ACCOUNT_PATH) or os.path.exists(CREDENTIALS_PATH)):
        print("Внимание: Файлы учетных данных не найдены.")
        print(f"Для работы с Google Docs API требуется:")
        print(f"1. Создать проект в Google Cloud Console")
        print(f"2. Включить Google Drive API и Google Docs API")
        print(f"3. Создать учетные данные (Service Account или OAuth)")
        print(f"4. Сохранить файл учетных данных как:")
        print(f"   - {SERVICE_ACCOUNT_PATH} (для Service Account)")
        print(f"   - или {CREDENTIALS_PATH} (для OAuth)")
        return False
    
    return True


def main():
    """Основная функция для работы из командной строки"""
    parser = argparse.ArgumentParser(description='Экспортер Markdown в Google Docs')
    parser.add_argument('input_file', help='Путь к Markdown-файлу')
    parser.add_argument('--title', '-t', help='Название документа (по умолчанию - имя файла)')
    parser.add_argument('--access', '-a', choices=['anyone', 'user', 'group', 'domain'], 
                        default='anyone', help='Тип доступа к документу')
    parser.add_argument('--role', '-r', choices=['reader', 'commenter', 'writer'], 
                        default='reader', help='Роль для доступа')
    parser.add_argument('--email', '-e', help='Email для доступа (для типов user и group)')
    parser.add_argument('--setup', '-s', action='store_true', 
                        help='Настроить окружение для экспорта')
    
    args = parser.parse_args()
    
    if args.setup:
        if setup_gdocs_export():
            print("Окружение успешно настроено.")
        return
    
    # Проверяем корректность параметров
    if args.access in ['user', 'group'] and not args.email:
        print("Ошибка: Для типа доступа 'user' или 'group' требуется указать email.")
        return
    
    # Экспортируем файл
    doc_url = export_to_google_docs(
        args.input_file, 
        title=args.title,
        access_type=args.access,
        role=args.role,
        email=args.email
    )
    
    if doc_url:
        print(f"Документ доступен по ссылке: {doc_url}")


if __name__ == '__main__':
    main()