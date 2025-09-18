"""
Тесты для notebook по AI QA стандарту
Автоматическая проверка качества notebook с данными из 1С
"""

import pytest
import pandas as pd
import duckdb
import nbformat
from pathlib import Path
import subprocess
import sys
import re


class TestNotebookQA:
    """Тест-кейсы для проверки качества notebook по AI QA стандарту"""
    
    @pytest.fixture
    def notebook_path(self):
        """Путь к notebook файлу"""
        return Path(__file__).parent.parent.parent / "notebooks" / "parquet_analysis.ipynb"
    
    @pytest.fixture
    def data_paths(self):
        """Пути к данным 1С"""
        return {
            'documents_parquet': Path(__file__).parent.parent.parent / "data" / "results" / "parquet" / "documents.parquet",
            'analysis_duckdb': Path(__file__).parent.parent.parent / "data" / "results" / "duckdb" / "analysis.duckdb",
            'test_flowers_parquet': Path(__file__).parent.parent.parent / "data" / "results" / "test_flowers.parquet",
            'test_flowers_duckdb': Path(__file__).parent.parent.parent / "data" / "results" / "test_flowers.duckdb"
        }
    
    def test_notebook_exists(self, notebook_path):
        """Test Case 1: Проверка существования notebook"""
        assert notebook_path.exists(), f"Notebook не найден: {notebook_path}"
    
    def test_notebook_syntax(self, notebook_path):
        """Test Case 2: Проверка синтаксиса notebook"""
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Проверяем каждую ячейку с кодом
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == 'code':
                # Проверяем на синтаксические ошибки в f-string
                code = cell.source
                
                # Проверяем на проблемные f-string конструкции
                problematic_patterns = [
                    r"f'[^']*\{[^}]*'[^}]*\}'",  # f'...{row['key']}...'
                    r'f"[^"]*\{[^"]*"[^"]*\}',   # f"...{row["key"]}..."
                ]
                
                for pattern in problematic_patterns:
                    matches = re.findall(pattern, code)
                    assert len(matches) == 0, f"Найдены проблемные f-string в ячейке {i}: {matches}"
    
    def test_data_files_exist(self, data_paths):
        """Test Case 3: Проверка существования файлов данных"""
        for name, path in data_paths.items():
            assert path.exists(), f"Файл данных не найден: {name} - {path}"
    
    def test_parquet_data_quality(self, data_paths):
        """Test Case 4: Проверка качества данных в Parquet файлах"""
        # Проверяем documents.parquet
        if data_paths['documents_parquet'].exists():
            df = pd.read_parquet(data_paths['documents_parquet'])
            
            # Критерии качества
            assert len(df) > 0, "Parquet файл пустой"
            assert len(df.columns) > 0, "Нет колонок в Parquet файле"
            assert 'table_name' in df.columns, "Отсутствует колонка table_name"
            assert 'field__NUMBER' in df.columns, "Отсутствует колонка field__NUMBER"
            
            # Проверяем типы данных
            assert df['table_name'].dtype == 'object', "Неправильный тип для table_name"
            assert df['field__NUMBER'].dtype == 'object', "Неправильный тип для field__NUMBER"
        
        # Проверяем test_flowers.parquet
        if data_paths['test_flowers_parquet'].exists():
            df = pd.read_parquet(data_paths['test_flowers_parquet'])
            
            assert len(df) > 0, "Test flowers файл пустой"
            assert 'flower_type' in df.columns, "Отсутствует колонка flower_type"
            assert 'store' in df.columns, "Отсутствует колонка store"
            assert 'amount' in df.columns, "Отсутствует колонка amount"
    
    def test_duckdb_data_quality(self, data_paths):
        """Test Case 5: Проверка качества данных в DuckDB файлах"""
        # Проверяем analysis.duckdb
        if data_paths['analysis_duckdb'].exists():
            conn = duckdb.connect(str(data_paths['analysis_duckdb']))
            
            # Проверяем таблицы
            tables = conn.execute('SHOW TABLES').fetchall()
            assert len(tables) > 0, "Нет таблиц в DuckDB"
            
            # Проверяем основную таблицу documents
            for table_name, in tables:
                count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
                assert count > 0, f"Таблица {table_name} пустая"
            
            conn.close()
        
        # Проверяем test_flowers.duckdb
        if data_paths['test_flowers_duckdb'].exists():
            conn = duckdb.connect(str(data_paths['test_flowers_duckdb']))
            
            tables = conn.execute('SHOW TABLES').fetchall()
            assert len(tables) > 0, "Нет таблиц в test_flowers.duckdb"
            
            conn.close()
    
    def test_notebook_execution(self, notebook_path):
        """Test Case 6: Проверка выполнения notebook"""
        # Запускаем notebook через nbconvert
        try:
            result = subprocess.run([
                sys.executable, '-m', 'nbconvert', 
                '--to', 'notebook', 
                '--execute', 
                '--output', '/tmp/test_output.ipynb',
                str(notebook_path)
            ], capture_output=True, text=True, timeout=60)
            
            assert result.returncode == 0, f"Ошибка выполнения notebook: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Notebook выполняется слишком долго")
        except Exception as e:
            pytest.fail(f"Ошибка при выполнении notebook: {e}")
    
    def test_data_consistency(self, data_paths):
        """Test Case 7: Проверка консистентности данных между Parquet и DuckDB"""
        if (data_paths['documents_parquet'].exists() and 
            data_paths['analysis_duckdb'].exists()):
            
            # Загружаем данные из Parquet
            df_parquet = pd.read_parquet(data_paths['documents_parquet'])
            
            # Загружаем данные из DuckDB
            conn = duckdb.connect(str(data_paths['analysis_duckdb']))
            df_duckdb = conn.execute('SELECT * FROM documents').fetchdf()
            conn.close()
            
            # Проверяем консистентность
            assert len(df_parquet) == len(df_duckdb), "Разное количество записей в Parquet и DuckDB"
            assert list(df_parquet.columns) == list(df_duckdb.columns), "Разные колонки в Parquet и DuckDB"
    
    def test_flower_data_quality(self, data_paths):
        """Test Case 8: Проверка качества данных о цветах"""
        if data_paths['test_flowers_parquet'].exists():
            df = pd.read_parquet(data_paths['test_flowers_parquet'])
            
            # Проверяем обязательные поля
            required_fields = ['document_id', 'flower_type', 'store', 'amount']
            for field in required_fields:
                assert field in df.columns, f"Отсутствует обязательное поле: {field}"
            
            # Проверяем типы данных
            assert df['amount'].dtype in ['float64', 'int64'], "Неправильный тип для amount"
            assert df['flower_type'].dtype == 'object', "Неправильный тип для flower_type"
            assert df['store'].dtype == 'object', "Неправильный тип для store"
            
            # Проверяем значения
            assert df['amount'].min() > 0, "Отрицательные суммы"
            assert len(df['flower_type'].unique()) > 0, "Нет разнообразия в типах цветов"
            assert len(df['store'].unique()) > 0, "Нет разнообразия в магазинах"
    
    def test_performance(self, data_paths):
        """Test Case 9: Проверка производительности загрузки данных"""
        import time
        
        # Тестируем время загрузки Parquet
        if data_paths['documents_parquet'].exists():
            start_time = time.time()
            df = pd.read_parquet(data_paths['documents_parquet'])
            load_time = time.time() - start_time
            
            assert load_time < 5.0, f"Слишком медленная загрузка Parquet: {load_time:.2f}s"
            assert len(df) > 0, "Parquet файл пустой"
        
        # Тестируем время загрузки DuckDB
        if data_paths['analysis_duckdb'].exists():
            start_time = time.time()
            conn = duckdb.connect(str(data_paths['analysis_duckdb']))
            df = conn.execute('SELECT * FROM documents').fetchdf()
            conn.close()
            load_time = time.time() - start_time
            
            assert load_time < 3.0, f"Слишком медленная загрузка DuckDB: {load_time:.2f}s"
            assert len(df) > 0, "DuckDB файл пустой"
    
    def test_error_handling(self, notebook_path):
        """Test Case 10: Проверка обработки ошибок в notebook"""
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Проверяем наличие обработки ошибок
        error_handling_patterns = [
            r'if.*\.exists\(\):',
            r'else:',
            r'except.*:',
            r'try:'
        ]
        
        has_error_handling = False
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                code = cell.source
                for pattern in error_handling_patterns:
                    if re.search(pattern, code):
                        has_error_handling = True
                        break
        
        assert has_error_handling, "Отсутствует обработка ошибок в notebook"


class TestNotebookAIMetrics:
    """Тесты метрик качества по AI QA стандарту"""
    
    @pytest.fixture
    def data_paths(self):
        """Пути к данным 1С"""
        return {
            'documents_parquet': Path(__file__).parent.parent.parent / "data" / "results" / "parquet" / "documents.parquet",
            'analysis_duckdb': Path(__file__).parent.parent.parent / "data" / "results" / "duckdb" / "analysis.duckdb"
        }
    
    def test_accuracy_metric(self, data_paths):
        """Проверка метрики точности (Accuracy) - >95%"""
        if data_paths['documents_parquet'].exists():
            df = pd.read_parquet(data_paths['documents_parquet'])
            
            # Проверяем точность данных - считаем записи без NaN в ключевых полях
            total_records = len(df)
            key_fields = ['id', 'table_name', 'field__NUMBER']
            valid_records = len(df.dropna(subset=key_fields))
            accuracy = (valid_records / total_records) * 100
            
            assert accuracy >= 95.0, f"Точность данных {accuracy:.1f}% ниже требуемых 95%"
    
    def test_completeness_metric(self, data_paths):
        """Проверка метрики полноты данных - 100% для обязательных полей"""
        if data_paths['documents_parquet'].exists():
            df = pd.read_parquet(data_paths['documents_parquet'])
            
            # Обязательные поля
            required_fields = ['id', 'table_name', 'field__NUMBER']
            
            for field in required_fields:
                if field in df.columns:
                    completeness = (df[field].notna().sum() / len(df)) * 100
                    assert completeness == 100.0, f"Полнота поля {field}: {completeness:.1f}%"
    
    def test_consistency_metric(self, data_paths):
        """Проверка метрики консистентности данных"""
        if (data_paths['documents_parquet'].exists() and 
            data_paths['analysis_duckdb'].exists()):
            
            df_parquet = pd.read_parquet(data_paths['documents_parquet'])
            conn = duckdb.connect(str(data_paths['analysis_duckdb']))
            df_duckdb = conn.execute('SELECT * FROM documents').fetchdf()
            conn.close()
            
            # Проверяем консистентность
            assert len(df_parquet) == len(df_duckdb), "Несоответствие количества записей"
            assert list(df_parquet.columns) == list(df_duckdb.columns), "Несоответствие колонок"
    
    def test_performance_metric(self, data_paths):
        """Проверка метрики производительности - <5 секунд"""
        import time
        
        if data_paths['documents_parquet'].exists():
            start_time = time.time()
            pd.read_parquet(data_paths['documents_parquet'])
            load_time = time.time() - start_time
            
            assert load_time < 5.0, f"Время загрузки {load_time:.2f}s превышает 5 секунд"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
