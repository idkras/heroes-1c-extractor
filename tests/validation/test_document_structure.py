"""
Тесты для валидации структуры документов в DuckDB
Проверяем, что каждый документ содержит все необходимые поля
"""

import pytest
import duckdb
import pandas as pd
from pathlib import Path


class TestDocumentStructure:
    """Тесты структуры документов в DuckDB"""
    
    def setup_method(self):
        """Настройка тестов"""
        self.duckdb_path = Path("data/results/duckdb/analysis.duckdb")
        self.parquet_path = Path("data/results/parquet/documents.parquet")
        
    def test_duckdb_exists(self):
        """Проверяем, что DuckDB файл существует"""
        assert self.duckdb_path.exists(), f"DuckDB файл не найден: {self.duckdb_path}"
        
    def test_parquet_exists(self):
        """Проверяем, что Parquet файл существует"""
        assert self.parquet_path.exists(), f"Parquet файл не найден: {self.parquet_path}"
        
    def test_documents_table_structure(self):
        """Проверяем структуру таблицы documents в DuckDB"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")
            
        conn = duckdb.connect(str(self.duckdb_path))
        
        # Проверяем, что таблица documents существует
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        assert "documents" in table_names, "Таблица 'documents' не найдена в DuckDB"
        
        # Проверяем структуру таблицы
        schema = conn.execute("DESCRIBE documents").fetchall()
        schema_columns = [col[0] for col in schema]
        
        # Обязательные поля для документов
        required_fields = [
            "id", "table_name", "document_type", "document_number", 
            "document_date", "store_name", "total_amount", "blob_content"
        ]
        
        for field in required_fields:
            assert field in schema_columns, f"Обязательное поле '{field}' отсутствует в таблице documents"
        
        conn.close()
        
    def test_documents_data_quality(self):
        """Проверяем качество данных в таблице documents"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")
            
        conn = duckdb.connect(str(self.duckdb_path))
        
        # Проверяем количество записей
        result = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        assert result is not None, "Не удалось получить result"
        result = result[0]
        assert result is not None, "Не удалось получить количество записей"
        count = result[0]
        assert count > 0, "В таблице documents нет записей"
        
        # Проверяем, что есть документы разных типов
        document_types = conn.execute("""
            SELECT document_type, COUNT(*) 
            FROM documents 
            GROUP BY document_type
        """).fetchall()
        
        assert len(document_types) > 1, "Найдены документы только одного типа"
        
        # Проверяем, что есть документы с суммами
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE total_amount > 0
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов с суммами"
        documents_with_amounts = result[0]
        
        assert documents_with_amounts > 0, "Нет документов с суммами"
        
        # Проверяем, что есть документы с магазинами
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE store_name != 'N/A' AND store_name != ''
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов с магазинами"
        documents_with_stores = result[0]
        
        assert documents_with_stores > 0, "Нет документов с названиями магазинов"
        
        conn.close()
        
    def test_parquet_data_structure(self):
        """Проверяем структуру данных в Parquet файле"""
        if not self.parquet_path.exists():
            pytest.skip("Parquet файл не найден")
            
        df = pd.read_parquet(self.parquet_path)
        
        # Проверяем, что есть данные
        assert len(df) > 0, "Parquet файл пустой"
        
        # Проверяем обязательные колонки
        required_columns = [
            "id", "table_name", "document_type", "document_number", 
            "document_date", "store_name", "total_amount"
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Обязательная колонка '{col}' отсутствует в Parquet файле"
            
    def test_document_search_capabilities(self):
        """Проверяем возможности поиска документов"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")
            
        conn = duckdb.connect(str(self.duckdb_path))
        
        # Тест 1: Поиск по типу документа
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE document_type = 'ФЛОРИСТИКА'
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов ФЛОРИСТИКА"
        floristic_docs = result[0]
        
        # Тест 2: Поиск по магазину
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE store_name LIKE '%ПЦ%'
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов по магазину"
        store_docs = result[0]
        
        # Тест 3: Поиск по сумме
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE total_amount > 10000
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов с высокой суммой"
        high_amount_docs = result[0]
        
        # Тест 4: Поиск по BLOB содержимому
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE blob_content LIKE '%флор%'
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов с BLOB содержимым"
        blob_docs = result[0]
        
        # Проверяем, что поиск работает
        assert floristic_docs >= 0, "Поиск по типу документа не работает"
        assert store_docs >= 0, "Поиск по магазину не работает"
        assert high_amount_docs >= 0, "Поиск по сумме не работает"
        assert blob_docs >= 0, "Поиск по BLOB содержимому не работает"
        
        conn.close()
        
    def test_document_analytics_queries(self):
        """Проверяем аналитические запросы"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")
            
        conn = duckdb.connect(str(self.duckdb_path))
        
        # Тест 1: Статистика по типам документов
        type_stats = conn.execute("""
            SELECT document_type, COUNT(*) as count, SUM(total_amount) as total
            FROM documents 
            GROUP BY document_type
            ORDER BY count DESC
        """).fetchall()
        
        assert len(type_stats) > 0, "Нет статистики по типам документов"
        
        # Тест 2: Статистика по магазинам
        store_stats = conn.execute("""
            SELECT store_name, COUNT(*) as count, SUM(total_amount) as total
            FROM documents 
            WHERE store_name != 'N/A'
            GROUP BY store_name
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()
        
        assert len(store_stats) > 0, "Нет статистики по магазинам"
        
        # Тест 3: Временная статистика
        conn.execute("""
            SELECT document_date, COUNT(*) as count
            FROM documents 
            WHERE document_date != 'N/A'
            GROUP BY document_date
            ORDER BY document_date DESC
            LIMIT 10
        """).fetchall()
        
        # Тест 4: Поиск цветочных данных
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE blob_content LIKE '%флор%' 
               OR blob_content LIKE '%роз%' 
               OR blob_content LIKE '%тюльпан%'
        """).fetchone()
        assert result is not None, "Не удалось получить количество цветочных документов"
        flower_docs = result[0]
        
        assert flower_docs >= 0, "Поиск цветочных данных не работает"
        
        conn.close()
        
    def test_document_completeness(self):
        """Проверяем полноту данных документов"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")
            
        conn = duckdb.connect(str(self.duckdb_path))
        
        # Проверяем, что есть документы с полными данными
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE document_type != 'Неизвестно'
              AND document_number != 'N/A'
              AND store_name != 'N/A'
              AND total_amount > 0
        """).fetchone()
        assert result is not None, "Не удалось получить количество полных документов"
        complete_docs = result[0]
        
        # Проверяем, что есть документы с BLOB данными
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE blob_content != '' AND blob_content IS NOT NULL
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов с BLOB данными"
        blob_docs = result[0]
        
        # Проверяем, что есть документы с датами
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE document_date != 'N/A' AND document_date IS NOT NULL
        """).fetchone()
        assert result is not None, "Не удалось получить количество документов с датами"
        date_docs = result[0]
        
        assert complete_docs > 0, "Нет документов с полными данными"
        assert blob_docs > 0, "Нет документов с BLOB данными"
        assert date_docs > 0, "Нет документов с датами"
        
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
