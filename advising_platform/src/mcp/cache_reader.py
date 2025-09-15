#!/usr/bin/env python3
"""
Simple DuckDB Cache Reader - CLI tool for reading files from cache
"""

import sys
import json
import duckdb
from pathlib import Path
from typing import List, Dict, Optional, Any

def read_file_from_cache(search_path, db_path="advising_platform/standards_system.duckdb"):
    """Читает файл из DuckDB кеша"""
    try:
        conn = duckdb.connect(db_path)
        
        # Поиск файла по пути или имени
        result = conn.execute("""
            SELECT id, name, content, path, word_count, category, description
            FROM standards 
            WHERE path = ? OR path LIKE ? OR name = ?
            LIMIT 1
        """, [search_path, f'%{Path(search_path).name}%', Path(search_path).stem]).fetchone()
        
        if result:
            return {
                'success': True,
                'file': {
                    'id': result[0],
                    'name': result[1], 
                    'content': result[2],
                    'path': result[3],
                    'word_count': result[4],
                    'category': result[5],
                    'description': result[6],
                    'source': 'duckdb_cache'
                }
            }
        else:
            return {'success': False, 'error': 'File not found in cache'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

def get_cache_stats(db_path="advising_platform/standards_system.duckdb"):
    """Получает статистику кеша"""
    try:
        conn = duckdb.connect(db_path)
        
        count_result = conn.execute('SELECT COUNT(*) FROM standards').fetchone()
        words_result = conn.execute('SELECT SUM(word_count) FROM standards').fetchone()
        
        return {
            'success': True,
            'stats': {
                'total_files': count_result[0] if count_result else 0,
                'total_words': words_result[0] if words_result else 0,
                'cache_available': True,
                'db_path': db_path
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'stats': {'cache_available': False}}
    finally:
        if 'conn' in locals():
            conn.close()

def list_all_files(db_path="advising_platform/standards_system.duckdb"):
    """Список всех файлов в кеше"""
    try:
        conn = duckdb.connect(db_path)
        
        results = conn.execute("""
            SELECT id, name, path, category, word_count, description
            FROM standards 
            ORDER BY name
        """).fetchall()
        
        files = [{
            'id': row[0],
            'name': row[1],
            'path': row[2], 
            'category': row[3],
            'word_count': row[4],
            'description': row[5],
            'source': 'duckdb_cache'
        } for row in results]
        
        return {'success': True, 'files': files, 'count': len(files)}
    except Exception as e:
        return {'success': False, 'error': str(e), 'files': []}
    finally:
        if 'conn' in locals():
            conn.close()

class CacheReader:
    """Class interface for DuckDB cache reading"""
    
    def __init__(self, db_path="standards_system.duckdb"):
        self.db_path = db_path
    
    def get_all_standards(self) -> List[Dict[str, Any]]:
        """Get all standards from cache"""
        try:
            conn = duckdb.connect(self.db_path)
            results = conn.execute("""
                SELECT id, name, content, path, word_count, category, description,
                       complexity, completeness, has_jtbd, has_ai_protocols, has_tdd_patterns
                FROM standards 
                ORDER BY name
            """).fetchall()
            
            standards = []
            for result in results:
                standards.append({
                    'id': result[0],
                    'name': result[1],
                    'content': result[2],
                    'path': result[3],
                    'word_count': result[4],
                    'category': result[5],
                    'description': result[6],
                    'complexity': result[7],
                    'completeness': result[8],
                    'has_jtbd': result[9],
                    'has_ai_protocols': result[10],
                    'has_tdd_patterns': result[11]
                })
            
            conn.close()
            return standards
        except Exception as e:
            return []
    
    def search_standards(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search standards by query"""
        try:
            conn = duckdb.connect(self.db_path)
            results = conn.execute("""
                SELECT id, name, content, path, word_count, category, description
                FROM standards 
                WHERE name ILIKE ? OR content ILIKE ? OR description ILIKE ?
                ORDER BY name
                LIMIT ?
            """, [f'%{query}%', f'%{query}%', f'%{query}%', limit]).fetchall()
            
            standards = []
            for result in results:
                standards.append({
                    'id': result[0],
                    'name': result[1],
                    'content': result[2],
                    'path': result[3],
                    'word_count': result[4],
                    'category': result[5],
                    'description': result[6]
                })
            
            conn.close()
            return standards
        except Exception as e:
            return []
    
    def get_standard_by_id(self, standard_id: str) -> Optional[Dict[str, Any]]:
        """Get specific standard by ID"""
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute("""
                SELECT id, name, content, path, word_count, category, description,
                       complexity, completeness, has_jtbd, has_ai_protocols, has_tdd_patterns
                FROM standards 
                WHERE id = ?
                LIMIT 1
            """, [standard_id]).fetchone()
            
            if result:
                standard = {
                    'id': result[0],
                    'name': result[1],
                    'content': result[2],
                    'path': result[3],
                    'word_count': result[4],
                    'category': result[5],
                    'description': result[6],
                    'complexity': result[7],
                    'completeness': result[8],
                    'has_jtbd': result[9],
                    'has_ai_protocols': result[10],
                    'has_tdd_patterns': result[11]
                }
                conn.close()
                return standard
            
            conn.close()
            return None
        except Exception as e:
            return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: cache_reader.py <command> [args]'}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'read' and len(sys.argv) >= 3:
        result = read_file_from_cache(sys.argv[2])
        print(json.dumps(result))
    elif command == 'stats':
        result = get_cache_stats()
        print(json.dumps(result))
    elif command == 'list':
        result = list_all_files()
        print(json.dumps(result))
    else:
        print(json.dumps({'error': f'Unknown command: {command}'}))
        sys.exit(1)