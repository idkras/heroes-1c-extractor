#!/usr/bin/env python3
"""
Инструмент для автоматического анализа и установления связей между документами.

Этот скрипт анализирует документы (задачи, инциденты, стандарты) и
устанавливает логические связи между ними на основе:
1. Текстового содержимого (семантический анализ)
2. Упоминаний других документов
3. Похожих тем и категорий
4. Временных меток и хронологии

Использование:
    python -m advising_platform.src.tools.document_relation_analyzer [опции]
    
Опции:
    --analyze-all               Анализировать все документы
    --analyze-document [path]   Анализировать конкретный документ
    --visualize                 Создать визуализацию связей
    --export [format]           Экспортировать связи (json, csv, markdown)
    --threshold [0.0-1.0]       Порог схожести для установления связи (по умолчанию 0.75)
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("document_relation_analyzer")

# Константы
RELATION_TYPES = {
    "MENTIONS": "упоминает",
    "SIMILAR_CONTENT": "имеет схожий контент с",
    "DEPENDS_ON": "зависит от",
    "PART_OF": "является частью",
    "RELATED_TO": "связан с",
    "SUPERSEDES": "заменяет",
    "IMPLEMENTS": "реализует",
    "DERIVES_FROM": "следует из",
    "REFERENCES_STANDARD": "ссылается на стандарт",
    "REQUIRES_TASK": "требует выполнения задачи",
    "ADDRESSES_INCIDENT": "исправляет инцидент",
    "RELATED_STANDARD": "связан с другим стандартом",
    "CAUSED_BY": "вызван",
    "RESOLVES": "решает",
    "CONTINUES": "продолжает",
    "DUPLICATES": "дублирует"
}

class DocumentRelation:
    """Представляет связь между двумя документами."""
    
    def __init__(self, source_id: str, target_id: str, relation_type: str,
                 confidence: float, metadata: Optional[Dict[str, Any]] = None):
        """
        Инициализирует связь между документами.
        
        Args:
            source_id: Логический ID исходного документа
            target_id: Логический ID целевого документа
            relation_type: Тип связи из RELATION_TYPES
            confidence: Уверенность в связи (0.0-1.0)
            metadata: Дополнительная информация о связи
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.confidence = confidence
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует связь в словарь для сериализации."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentRelation':
        """Создает объект связи из словаря."""
        relation = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=data["relation_type"],
            confidence=data["confidence"],
            metadata=data.get("metadata", {})
        )
        relation.created_at = data.get("created_at", datetime.now().isoformat())
        return relation
    
    def __str__(self) -> str:
        """Строковое представление связи."""
        return f"{self.source_id} {RELATION_TYPES.get(self.relation_type, self.relation_type)} {self.target_id} (уверенность: {self.confidence:.2f})"


class DocumentRelationAnalyzer:
    """
    Анализатор связей между документами.
    
    Использует различные методы анализа для установления
    логических связей между документами.
    """
    
    def __init__(self, similarity_threshold: float = 0.75):
        """
        Инициализирует анализатор связей.
        
        Args:
            similarity_threshold: Порог схожести для установления связи (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.relations: List[DocumentRelation] = []
        self.abstract_ids_map: Dict[str, str] = {}  # abstract_id -> path
        self.path_to_abstract_map: Dict[str, str] = {}  # path -> abstract_id
        self.document_cache: Dict[str, Dict[str, Any]] = {}  # path -> document data
        self.logger = logger
    
    def load_abstract_ids(self, from_indexer=None) -> None:
        """
        Загружает сопоставление логических и физических идентификаторов.
        
        Args:
            from_indexer: Опциональный объект индексатора для получения абстрактных ID
        """
        try:
            # Если передан индексатор, берем данные из него
            if from_indexer is not None and hasattr(from_indexer, 'abstractions'):
                for abstract_id, path in from_indexer.abstractions.items():
                    self.abstract_ids_map[abstract_id] = path
                    self.path_to_abstract_map[path] = abstract_id
                self.logger.info(f"Загружено {len(self.abstract_ids_map)} логических идентификаторов из индексатора")
                return
            
            # Иначе пытаемся загрузить из файла
            abstraction_file = Path("data/abstractions.json")
            if abstraction_file.exists():
                with open(abstraction_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for abstract_id, path in data.items():
                        self.abstract_ids_map[abstract_id] = path
                        self.path_to_abstract_map[path] = abstract_id
                self.logger.info(f"Загружено {len(self.abstract_ids_map)} логических идентификаторов из файла")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке абстрактных идентификаторов: {e}")
    
    def analyze_document(self, path: str) -> List[DocumentRelation]:
        """
        Анализирует документ и определяет его связи с другими документами.
        
        Args:
            path: Путь к документу для анализа
            
        Returns:
            Список найденных связей (DocumentRelation)
        """
        self.logger.info(f"Анализ документа: {path}")
        document_relations = []
        
        try:
            # Получаем содержимое документа
            if path not in self.document_cache:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.document_cache[path] = {
                    "content": content,
                    "filename": os.path.basename(path),
                    "directory": os.path.dirname(path),
                    "last_modified": os.path.getmtime(path)
                }
            
            doc_data = self.document_cache[path]
            
            # Получаем или генерируем логический ID документа
            source_id = self.path_to_abstract_map.get(path)
            if not source_id:
                # Генерируем временный ID на основе пути, если нет логического ID
                basename = os.path.basename(path)
                directory = os.path.dirname(path)
                if "standard" in basename.lower() or directory.startswith("[standards"):
                    source_id = f"temp:standard:{basename.replace(' ', '_').replace('.md', '')}"
                elif "incident" in basename.lower() or "incidents" in directory.lower():
                    source_id = f"temp:incident:{basename.replace(' ', '_').replace('.md', '')}"
                elif "task" in basename.lower() or "todo" in basename.lower():
                    source_id = f"temp:task:{basename.replace(' ', '_').replace('.md', '')}"
                else:
                    source_id = f"temp:document:{basename.replace(' ', '_').replace('.md', '')}"
            
            # Находим явные ссылки на другие документы
            explicit_relations = self._find_explicit_references(doc_data["content"], source_id)
            document_relations.extend(explicit_relations)
            
            # Находим семантически похожие документы
            similarity_relations = self._find_similar_documents(path, source_id, doc_data["content"])
            document_relations.extend(similarity_relations)
            
            # Находим хронологические связи и зависимости
            temporal_relations = self._find_temporal_relations(path, source_id, doc_data)
            document_relations.extend(temporal_relations)
            
            self.logger.info(f"Найдено {len(document_relations)} связей для документа {path}")
            
            # Добавляем найденные связи в общий список
            for relation in document_relations:
                if relation not in self.relations:
                    self.relations.append(relation)
                    
            return document_relations
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе документа {path}: {e}")
            return []

    def _find_explicit_references(self, content: str, source_id: str) -> List[DocumentRelation]:
        """
        Находит явные ссылки на другие документы в содержимом.
        
        Args:
            content: Текст документа
            source_id: Логический ID исходного документа
            
        Returns:
            Список связей на основе явных ссылок
        """
        relations = []
        
        # Ищем Markdown-ссылки [текст](путь)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for link_text, link_target in markdown_links:
            # Проверяем, является ли ссылка абстрактным идентификатором
            if link_target.startswith("abstract://"):
                # Преобразуем abstract://standard:name в standard:name
                target_id = link_target.replace("abstract://", "")
                relation_type = "MENTIONS"
                
                # Определяем тип связи на основе контекста содержимого документа
                if any(keyword in link_text.lower() for keyword in ["основан", "based on", "версия", "based"]):
                    relation_type = "DERIVES_FROM"
                elif any(keyword in link_text.lower() for keyword in ["реализует", "implements", "выполняет"]):
                    relation_type = "IMPLEMENTS"
                elif any(keyword in link_text.lower() for keyword in ["заменяет", "supersedes", "новая версия", "обновляет"]):
                    relation_type = "SUPERSEDES"
                elif any(keyword in link_text.lower() for keyword in ["инцидент", "incident", "проблема", "issue"]):
                    relation_type = "RELATED_TO"
                elif any(keyword in link_text.lower() for keyword in ["требует", "needs", "зависит", "depends"]):
                    relation_type = "DEPENDS_ON"
                elif any(keyword in link_text.lower() for keyword in ["связанные", "связанный", "related"]):
                    relation_type = "RELATED_TO"
                
                # Определяем тип связи на основе префиксов идентификаторов
                source_type = source_id.split(":")[0] if ":" in source_id else ""
                target_type = target_id.split(":")[0] if ":" in target_id else ""
                
                # Устанавливаем более специфичные типы связей на основе типов документов
                if source_type == "incident" and target_type == "standard":
                    if relation_type == "MENTIONS":
                        relation_type = "REFERENCES_STANDARD"
                elif source_type == "incident" and target_type == "task":
                    relation_type = "REQUIRES_TASK"
                elif source_type == "task" and target_type == "incident":
                    relation_type = "ADDRESSES_INCIDENT"
                elif source_type == "standard" and target_type == "standard":
                    if relation_type == "MENTIONS":
                        relation_type = "RELATED_STANDARD"
                
                relations.append(DocumentRelation(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=relation_type,
                    confidence=1.0,  # Максимальная уверенность для явных ссылок
                    metadata={"link_text": link_text}
                ))
            else:
                # Проверяем, есть ли физический путь в нашем маппинге
                if link_target in self.path_to_abstract_map:
                    target_id = self.path_to_abstract_map[link_target]
                    relations.append(DocumentRelation(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type="MENTIONS",
                        confidence=1.0,
                        metadata={"link_text": link_text}
                    ))
        
        # Ищем упоминания других документов по названию или ключевым словам
        # TODO: реализовать в будущем с использованием NLP
        
        return relations

    def _find_similar_documents(self, path: str, source_id: str, content: str) -> List[DocumentRelation]:
        """
        Находит семантически похожие документы.
        
        Args:
            path: Путь к исходному документу
            source_id: Логический ID исходного документа
            content: Содержимое исходного документа
            
        Returns:
            Список связей на основе семантической схожести
        """
        # На данном этапе реализуем простое сравнение по ключевым словам
        # В будущем здесь будет использоваться векторное сравнение эмбеддингов
        
        # Ключевые слова для анализа
        keywords = self._extract_keywords(content, max_keywords=10)
        
        relations = []
        
        # В будущей версии здесь будет доступ к индексированным документам
        # Сейчас просто возвращаем пустой список
        
        return relations

    def _find_temporal_relations(self, path: str, source_id: str, doc_data: Dict[str, Any]) -> List[DocumentRelation]:
        """
        Находит хронологические связи между документами.
        
        Args:
            path: Путь к исходному документу
            source_id: Логический ID исходного документа
            doc_data: Данные документа
            
        Returns:
            Список связей на основе хронологии и зависимостей
        """
        # Базовая реализация для примера, будет расширяться в будущем
        
        relations = []
        
        # Ищем даты типа "updated: 14 May 2025"
        content = doc_data["content"]
        update_matches = re.findall(r'updated:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})', content)
        previous_matches = re.findall(r'previous(?:\s+version)?:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})', content)
        
        # TODO: Анализ хронологических связей будет реализован в будущих версиях
        
        return relations

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """
        Извлекает ключевые слова из содержимого документа.
        
        Args:
            content: Текст документа
            max_keywords: Максимальное количество ключевых слов
            
        Returns:
            Список ключевых слов
        """
        # Простая реализация извлечения ключевых слов
        # В реальной системе здесь будет использоваться более сложный алгоритм
        
        # Очищаем текст от Markdown-разметки
        text = re.sub(r'\[.*?\]\(.*?\)', '', content)  # Удаляем ссылки
        text = re.sub(r'#', '', text)  # Удаляем символы заголовков
        text = re.sub(r'\*\*|\*|__|\|', '', text)  # Удаляем разметку выделения
        
        # Разбиваем на слова и фильтруем
        words = re.findall(r'\b[а-яА-Яa-zA-Z]{4,}\b', text.lower())
        
        # Удаляем стоп-слова (в реальной системе список будет больше)
        stop_words = {'and', 'the', 'is', 'of', 'to', 'для', 'при', 'это', 'как', 'что'}
        filtered_words = [word for word in words if word not in stop_words]
        
        # Подсчитываем частоту слов
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Сортируем по частоте и берем top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:max_keywords]]
        
    def save_relations(self, output_file: str) -> None:
        """
        Сохраняет все найденные связи в файл.
        
        Args:
            output_file: Путь к файлу для сохранения связей
        """
        try:
            data = [relation.to_dict() for relation in self.relations]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Связи сохранены в {output_file}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении связей: {e}")
    
    def load_relations(self, input_file: str) -> None:
        """
        Загружает связи из файла.
        
        Args:
            input_file: Путь к файлу с сохраненными связями
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.relations = [DocumentRelation.from_dict(item) for item in data]
            self.logger.info(f"Загружено {len(self.relations)} связей из {input_file}")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке связей: {e}")
    
    def export_relations(self, format_type: str, output_file: str) -> None:
        """
        Экспортирует связи в различных форматах.
        
        Args:
            format_type: Формат экспорта (json, csv, markdown)
            output_file: Путь к файлу для экспорта
        """
        if format_type == 'json':
            self.save_relations(output_file)
        elif format_type == 'csv':
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("source_id,target_id,relation_type,confidence,created_at\n")
                    for relation in self.relations:
                        f.write(f"{relation.source_id},{relation.target_id},{relation.relation_type},{relation.confidence},{relation.created_at}\n")
                self.logger.info(f"Связи экспортированы в CSV: {output_file}")
            except Exception as e:
                self.logger.error(f"Ошибка при экспорте в CSV: {e}")
        elif format_type == 'markdown':
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("# Связи между документами\n\n")
                    f.write("| Исходный документ | Связь | Целевой документ | Уверенность |\n")
                    f.write("|---|---|---|---|\n")
                    for relation in self.relations:
                        f.write(f"| {relation.source_id} | {RELATION_TYPES.get(relation.relation_type, relation.relation_type)} | {relation.target_id} | {relation.confidence:.2f} |\n")
                self.logger.info(f"Связи экспортированы в Markdown: {output_file}")
            except Exception as e:
                self.logger.error(f"Ошибка при экспорте в Markdown: {e}")
        else:
            self.logger.error(f"Неподдерживаемый формат экспорта: {format_type}")


def main():
    """Точка входа для запуска из командной строки."""
    parser = argparse.ArgumentParser(description='Анализатор связей между документами')
    parser.add_argument('--analyze-all', action='store_true', help='Анализировать все документы')
    parser.add_argument('--analyze-document', help='Анализировать конкретный документ')
    parser.add_argument('--visualize', action='store_true', help='Создать визуализацию связей')
    parser.add_argument('--export', help='Экспортировать связи (json, csv, markdown)')
    parser.add_argument('--threshold', type=float, default=0.75, help='Порог схожести (0.0-1.0)')
    parser.add_argument('--output', default='data/document_relations.json', help='Выходной файл')
    
    args = parser.parse_args()
    
    # Создаем анализатор
    analyzer = DocumentRelationAnalyzer(similarity_threshold=args.threshold)
    
    # Загружаем абстрактные идентификаторы
    analyzer.load_abstract_ids()
    
    if args.analyze_document:
        # Анализируем указанный документ
        analyzer.analyze_document(args.analyze_document)
    elif args.analyze_all:
        # Анализируем все документы в основных директориях
        dirs_to_analyze = [
            "[standards .md]",
            "[todo · incidents]",
            "[todo · incidents]/ai.incidents"
        ]
        
        total_docs = 0
        total_relations = 0
        
        for directory in dirs_to_analyze:
            if os.path.exists(directory):
                logger.info(f"Анализ документов в директории: {directory}")
                
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            relations = analyzer.analyze_document(file_path)
                            total_docs += 1
                            total_relations += len(relations)
                            
                logger.info(f"Проанализировано {total_docs} документов, найдено {total_relations} связей")
    
    # Экспортируем результаты при необходимости
    if args.export:
        analyzer.export_relations(args.export, args.output)
    
    # Визуализируем связи при необходимости
    if args.visualize:
        try:
            # Создаем файл в формате DOT для Graphviz
            dot_file = args.output.replace('.json', '.dot')
            with open(dot_file, 'w', encoding='utf-8') as f:
                f.write("digraph document_relations {\n")
                f.write("  rankdir=LR;\n")
                f.write("  node [shape=box, style=filled, fillcolor=lightblue];\n")
                
                # Группируем узлы по типам документов
                document_types = {}
                for relation in analyzer.relations:
                    source_type = relation.source_id.split(':')[0] if ':' in relation.source_id else 'unknown'
                    target_type = relation.target_id.split(':')[0] if ':' in relation.target_id else 'unknown'
                    
                    if source_type not in document_types:
                        document_types[source_type] = set()
                    if target_type not in document_types:
                        document_types[target_type] = set()
                    
                    document_types[source_type].add(relation.source_id)
                    document_types[target_type].add(relation.target_id)
                
                # Определяем цвета для разных типов документов
                type_colors = {
                    'task': 'lightblue',
                    'incident': 'salmon',
                    'standard': 'lightgreen',
                    'unknown': 'lightgray'
                }
                
                # Создаем подграфы для каждого типа документов
                for doc_type, docs in document_types.items():
                    color = type_colors.get(doc_type, 'lightgray')
                    f.write(f'  subgraph cluster_{doc_type} {{\n')
                    f.write(f'    label="{doc_type}";\n')
                    f.write(f'    node [fillcolor={color}];\n')
                    for doc_id in docs:
                        label = doc_id.split(':')[1] if ':' in doc_id else doc_id
                        f.write(f'    "{doc_id}" [label="{label}"];\n')
                    f.write('  }\n')
                
                # Добавляем ребра
                for relation in analyzer.relations:
                    relation_type = RELATION_TYPES.get(relation.relation_type, relation.relation_type)
                    f.write(f'  "{relation.source_id}" -> "{relation.target_id}" [label="{relation_type}"];\n')
                
                f.write("}\n")
            
            logger.info(f"Визуализация связей сохранена в формате DOT: {dot_file}")
            logger.info("Используйте Graphviz для конвертации в PNG или SVG: dot -Tpng -o relations.png relations.dot")
        except Exception as e:
            logger.error(f"Ошибка при создании визуализации: {e}")


if __name__ == '__main__':
    main()