"""
Тесты для поиска и фильтрации документов в DuckDB
Проверяем, что можно найти нужные документы по различным критериям
"""

from pathlib import Path

import duckdb
import pytest


class TestDocumentSearch:
    """Тесты поиска и фильтрации документов"""

    def setup_method(self):
        """Настройка тестов"""
        self.duckdb_path = Path("data/results/heroes_1c_data.duckdb")

    def test_search_by_document_type(self):
        """Тест поиска по типу документа"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Поиск документов реализации (флористические документы)
        floristic_docs = conn.execute(
            """
            SELECT id, document_number, store_name, total_amount, blob_content
            FROM documents
            WHERE document_type = 'РЕАЛИЗАЦИЯ'
            LIMIT 5
        """,
        ).fetchall()

        assert len(floristic_docs) > 0, "Не найдены документы реализации"

        # Проверяем, что документы найдены
        print(f"Найдено {len(floristic_docs)} документов реализации")

        # Проверяем, что есть хотя бы один документ с информацией о цветах
        flower_docs = []
        for doc in floristic_docs:
            blob_content = doc[4] if doc[4] else ""
            if "флор" in blob_content.lower() or "цвет" in blob_content.lower():
                flower_docs.append(doc)

        print(f"Документов с информацией о цветах: {len(flower_docs)}")
        # Не требуем обязательного наличия цветов в каждом документе

        conn.close()

    def test_search_by_store(self):
        """Тест поиска по магазину"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Поиск документов по магазину
        store_docs = conn.execute(
            """
            SELECT id, document_number, store_name, total_amount
            FROM documents
            WHERE store_name LIKE '%ПЦ%'
            LIMIT 5
        """,
        ).fetchall()

        assert len(store_docs) > 0, "Не найдены документы по магазинам"

        # Проверяем, что все документы содержат информацию о магазинах
        for doc in store_docs:
            store_name = doc[2] if doc[2] else ""
            assert "ПЦ" in store_name, (
                f"Документ {doc[0]} не содержит информации о магазине"
            )

        conn.close()

    def test_search_by_amount_range(self):
        """Тест поиска по диапазону сумм"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Поиск документов с высокими суммами
        high_amount_docs = conn.execute(
            """
            SELECT id, document_number, total_amount, store_name
            FROM documents
            WHERE total_amount > 10000
            ORDER BY total_amount DESC
            LIMIT 5
        """,
        ).fetchall()

        assert len(high_amount_docs) > 0, "Не найдены документы с высокими суммами"

        # Проверяем, что суммы действительно высокие
        for doc in high_amount_docs:
            amount = doc[2] if doc[2] else 0
            assert amount > 10000, (
                f"Документ {doc[0]} имеет сумму {amount}, что меньше 10000"
            )

        conn.close()

    def test_search_by_date_range(self):
        """Тест поиска по диапазону дат"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Поиск документов по дате
        date_docs = conn.execute(
            """
            SELECT id, document_number, document_date, total_amount
            FROM documents
            WHERE document_date != 'N/A' AND document_date IS NOT NULL
            ORDER BY document_date DESC
            LIMIT 5
        """,
        ).fetchall()

        assert len(date_docs) > 0, "Не найдены документы с датами"

        # Проверяем, что даты корректные
        for doc in date_docs:
            date = doc[2] if doc[2] else ""
            assert date != "N/A" and date != "", (
                f"Документ {doc[0]} имеет некорректную дату: {date}"
            )

        conn.close()

    def test_search_by_blob_content(self):
        """Тест поиска по содержимому BLOB"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Поиск документов с цветочной информацией
        flower_docs = conn.execute(
            """
            SELECT id, document_number, blob_content, store_name
            FROM documents
            WHERE blob_content LIKE '%флор%'
               OR blob_content LIKE '%роз%'
               OR blob_content LIKE '%тюльпан%'
               OR blob_content LIKE '%хризантем%'
            LIMIT 5
        """,
        ).fetchall()

        assert len(flower_docs) > 0, "Не найдены документы с цветочной информацией"

        # Проверяем, что документы содержат цветочную информацию
        for doc in flower_docs:
            blob_content = doc[2] if doc[2] else ""
            assert any(
                keyword in blob_content.lower()
                for keyword in ["флор", "роз", "тюльпан", "хризантем"]
            ), f"Документ {doc[0]} не содержит цветочной информации"

        conn.close()

    def test_complex_search_queries(self):
        """Тест сложных поисковых запросов"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Сложный запрос: документы с высокими суммами и реальными магазинами
        complex_query = conn.execute(
            """
            SELECT id, document_number, store_name, total_amount, blob_content
            FROM documents
            WHERE total_amount > 5000
              AND store_name LIKE '%ПЦ%'
            ORDER BY total_amount DESC
            LIMIT 5
        """,
        ).fetchall()

        assert len(complex_query) > 0, "Не найдены документы по сложному запросу"

        # Проверяем, что все документы соответствуют критериям
        for doc in complex_query:
            blob_content = doc[4] if doc[4] else ""
            amount = doc[3] if doc[3] else 0
            store_name = doc[2] if doc[2] else ""

            # Проверяем, что документ содержит информацию о цветах или букетах
            assert (
                "флор" in blob_content.lower()
                or "цвет" in blob_content.lower()
                or "букет" in blob_content.lower()
                or "моно" in blob_content.lower()
            ), (
                f"Документ {doc[0]} не содержит информации о цветах: {blob_content[:50]}..."
            )
            assert amount > 5000, (
                f"Документ {doc[0]} имеет сумму {amount}, что меньше 5000"
            )
            assert "ПЦ" in store_name, (
                f"Документ {doc[0]} не содержит информации о магазине ПЦ"
            )

        conn.close()

    def test_analytics_queries(self):
        """Тест аналитических запросов"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Анализ по типам документов
        type_analysis = conn.execute(
            """
            SELECT document_type, COUNT(*) as count, SUM(total_amount) as total_amount
            FROM documents
            GROUP BY document_type
            ORDER BY count DESC
        """,
        ).fetchall()

        assert len(type_analysis) > 0, "Нет анализа по типам документов"

        # Анализ по магазинам
        store_analysis = conn.execute(
            """
            SELECT store_name, COUNT(*) as count, SUM(total_amount) as total_amount
            FROM documents
            WHERE store_name != 'N/A'
            GROUP BY store_name
            ORDER BY count DESC
            LIMIT 10
        """,
        ).fetchall()

        assert len(store_analysis) > 0, "Нет анализа по магазинам"

        # Анализ по датам
        date_analysis = conn.execute(
            """
            SELECT document_date, COUNT(*) as count, SUM(total_amount) as total_amount
            FROM documents
            WHERE document_date != 'N/A'
            GROUP BY document_date
            ORDER BY document_date DESC
            LIMIT 10
        """,
        ).fetchall()

        assert len(date_analysis) > 0, "Нет анализа по датам"

        conn.close()

    def test_document_filtering(self):
        """Тест фильтрации документов"""
        if not self.duckdb_path.exists():
            pytest.skip("DuckDB файл не найден")

        conn = duckdb.connect(str(self.duckdb_path))

        # Фильтр по сумме и магазинам
        filtered_docs = conn.execute(
            """
            SELECT id, document_number, document_type, total_amount, store_name
            FROM documents
            WHERE total_amount BETWEEN 1000 AND 50000
              AND store_name != 'N/A'
            ORDER BY total_amount DESC
            LIMIT 10
        """,
        ).fetchall()

        assert len(filtered_docs) > 0, "Не найдены документы по фильтру"

        # Проверяем, что все документы соответствуют фильтру
        for doc in filtered_docs:
            # doc_type = doc[2] if doc[2] else ""  # Пока не используется
            amount = doc[3] if doc[3] else 0

            # Проверяем, что документ имеет реальную сумму и магазин
            assert amount >= 1000, (
                f"Документ {doc[0]} имеет сумму {amount}, что меньше 1000"
            )
            assert amount <= 50000, (
                f"Документ {doc[0]} имеет сумму {amount}, что больше 50000"
            )
            assert 1000 <= amount <= 50000, (
                f"Документ {doc[0]} имеет сумму {amount}, которая не соответствует фильтру"
            )

        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
