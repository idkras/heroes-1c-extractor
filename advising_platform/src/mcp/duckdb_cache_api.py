#!/usr/bin/env python3
"""
DuckDB Cache API - HTTP сервер для работы с DuckDB кешем
Обеспечивает чтение файлов из кеша вместо диска
"""

import duckdb
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

class DuckDBCacheAPI:
    def __init__(self, db_path="standards_system.duckdb", port=5004):
        self.db_path = db_path
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.setup_routes()
    
    def connect_db(self):
        """Подключение к DuckDB"""
        try:
            conn = duckdb.connect(self.db_path)
            return conn
        except Exception as e:
            print(f"❌ DuckDB connection failed: {e}")
            return None
    
    def get_file_from_cache(self, search_path):
        """Получение файла из кеша"""
        conn = self.connect_db()
        if not conn:
            return None
        
        try:
            # Пробуем найти по точному пути
            result = conn.execute("""
                SELECT id, name, content, path, word_count, category, description
                FROM standards 
                WHERE path = ? OR path LIKE ? OR name = ?
                LIMIT 1
            """, [search_path, f'%{Path(search_path).name}%', Path(search_path).stem]).fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1], 
                    'content': result[2],
                    'path': result[3],
                    'word_count': result[4],
                    'category': result[5],
                    'description': result[6],
                    'source': 'duckdb_cache'
                }
            return None
        except Exception as e:
            print(f"❌ Error reading from cache: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_files_from_cache(self):
        """Получение всех файлов из кеша"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
            results = conn.execute("""
                SELECT id, name, path, category, word_count, description
                FROM standards 
                ORDER BY name
            """).fetchall()
            
            return [{
                'id': row[0],
                'name': row[1],
                'path': row[2], 
                'category': row[3],
                'word_count': row[4],
                'description': row[5],
                'source': 'duckdb_cache'
            } for row in results]
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []
        finally:
            conn.close()
    
    def get_cache_stats(self):
        """Статистика кеша"""
        conn = self.connect_db()
        if not conn:
            return {'error': 'Cache not available', 'cache_available': False}
        
        try:
            count_result = conn.execute('SELECT COUNT(*) FROM standards').fetchone()
            words_result = conn.execute('SELECT SUM(word_count) FROM standards').fetchone()
            
            return {
                'total_files': count_result[0] if count_result else 0,
                'total_words': words_result[0] if words_result else 0,
                'cache_available': True,
                'db_path': self.db_path
            }
        except Exception as e:
            return {'error': str(e), 'cache_available': False}
        finally:
            conn.close()
    
    def setup_routes(self):
        """Настройка HTTP маршрутов"""
        
        @self.app.route('/api/cache/file', methods=['GET'])
        def get_file():
            """GET /api/cache/file?path=filename - получить файл из кеша"""
            file_path = request.args.get('path')
            if not file_path:
                return jsonify({'error': 'path parameter required'}), 400
            
            file_data = self.get_file_from_cache(file_path)
            if file_data:
                return jsonify({'success': True, 'file': file_data})
            else:
                return jsonify({'success': False, 'error': 'File not found in cache'}), 404
        
        @self.app.route('/api/cache/files', methods=['GET'])
        def get_all_files():
            """GET /api/cache/files - получить все файлы из кеша"""
            files = self.get_all_files_from_cache()
            return jsonify({'success': True, 'files': files, 'count': len(files)})
        
        @self.app.route('/api/cache/stats', methods=['GET'])
        def get_stats():
            """GET /api/cache/stats - статистика кеша"""
            stats = self.get_cache_stats()
            return jsonify({'success': True, 'stats': stats})
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """GET /health - проверка здоровья сервиса"""
            return jsonify({'status': 'ok', 'service': 'duckdb_cache_api'})
    
    def run(self):
        """Запуск HTTP сервера"""
        print(f'🚀 DuckDB Cache API starting on port {self.port}')
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

if __name__ == '__main__':
    # Запускаем API сервер
    api = DuckDBCacheAPI()
    api.run()