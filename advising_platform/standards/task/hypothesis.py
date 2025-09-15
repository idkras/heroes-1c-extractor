"""
Модуль для работы с гипотезами в соответствии со стандартом гипотез.

Реализует централизованное управление гипотезами, обеспечивая их создание,
проверку и анализ согласно актуальному стандарту.
"""

import re
import logging
import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Set

from advising_platform.standards.core.traceable import implements_standard

# Настройка логирования
logger = logging.getLogger(__name__)

# Статусы гипотез
HYPOTHESIS_STATUSES = [
    "NEW",          # Новая гипотеза
    "IN_PROGRESS",  # Гипотеза в процессе проверки
    "CONFIRMED",    # Гипотеза подтверждена
    "REJECTED",     # Гипотеза отклонена
    "UNCERTAIN"     # Результат неоднозначен
]


@implements_standard("hypothesis", "1.2", "structure")
class Hypothesis:
    """Класс для представления гипотезы по стандарту 1.2."""
    
    def __init__(
        self,
        id: str,
        statement: str,
        context: str = "",
        status: str = "NEW",
        verification_method: str = "",
        experiment_design: str = "",
        expected_results: str = "",
        actual_results: str = "",
        conclusion: str = "",
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        tags: Optional[List[str]] = None,
        related_incidents: Optional[List[str]] = None
    ):
        """
        Инициализирует гипотезу.
        
        Args:
            id: Уникальный идентификатор гипотезы
            statement: Формулировка гипотезы
            context: Контекст, в котором возникла гипотеза
            status: Статус гипотезы
            verification_method: Метод проверки гипотезы
            experiment_design: Дизайн эксперимента для проверки
            expected_results: Ожидаемые результаты
            actual_results: Фактические результаты
            conclusion: Заключение по результатам проверки
            created_at: Дата создания гипотезы
            updated_at: Дата последнего обновления гипотезы
            tags: Теги гипотезы
            related_incidents: Связанные инциденты
        """
        self.id = id
        self.statement = statement
        self.context = context
        self.status = status if status in HYPOTHESIS_STATUSES else "NEW"
        self.verification_method = verification_method
        self.experiment_design = experiment_design
        self.expected_results = expected_results
        self.actual_results = actual_results
        self.conclusion = conclusion
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or datetime.datetime.now()
        self.tags = tags or []
        self.related_incidents = related_incidents or []
    
    @implements_standard("hypothesis", "1.2", "serialization")
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует гипотезу в словарь.
        
        Returns:
            Словарь с данными гипотезы
        """
        return {
            "id": self.id,
            "statement": self.statement,
            "context": self.context,
            "status": self.status,
            "verification_method": self.verification_method,
            "experiment_design": self.experiment_design,
            "expected_results": self.expected_results,
            "actual_results": self.actual_results,
            "conclusion": self.conclusion,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tags": self.tags,
            "related_incidents": self.related_incidents
        }
    
    @classmethod
    @implements_standard("hypothesis", "1.2", "deserialization")
    def from_dict(cls, data: Dict[str, Any]) -> 'Hypothesis':
        """
        Создает гипотезу из словаря.
        
        Args:
            data: Словарь с данными гипотезы
        
        Returns:
            Объект гипотезы
        """
        # Преобразуем строковые даты в объекты datetime
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                created_at = datetime.datetime.now()
        
        updated_at = None
        if data.get("updated_at"):
            try:
                updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                updated_at = datetime.datetime.now()
        
        return cls(
            id=data.get("id", ""),
            statement=data.get("statement", ""),
            context=data.get("context", ""),
            status=data.get("status", "NEW"),
            verification_method=data.get("verification_method", ""),
            experiment_design=data.get("experiment_design", ""),
            expected_results=data.get("expected_results", ""),
            actual_results=data.get("actual_results", ""),
            conclusion=data.get("conclusion", ""),
            created_at=created_at,
            updated_at=updated_at,
            tags=data.get("tags", []),
            related_incidents=data.get("related_incidents", [])
        )
    
    @implements_standard("hypothesis", "1.2", "formatting")
    def to_markdown(self) -> str:
        """
        Преобразует гипотезу в формат Markdown.
        
        Returns:
            Строка с гипотезой в формате Markdown
        """
        created_at_str = self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "N/A"
        updated_at_str = self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else "N/A"
        
        markdown = f"""# 🧪 Гипотеза: {self.statement}

## Метаданные
- **Идентификатор:** {self.id}
- **Статус:** {self.status}
- **Создана:** {created_at_str}
- **Обновлена:** {updated_at_str}
- **Теги:** {', '.join(self.tags) if self.tags else "Нет тегов"}

## Контекст
{self.context}

## Метод проверки
{self.verification_method}

## Дизайн эксперимента
{self.experiment_design}

## Ожидаемые результаты
{self.expected_results}

## Фактические результаты
{self.actual_results}

## Заключение
{self.conclusion}

## Связанные инциденты
{', '.join([f"[{incident}](abstract://incident:{incident})" for incident in self.related_incidents]) if self.related_incidents else "Нет связанных инцидентов"}
"""
        
        return markdown
    
    @classmethod
    @implements_standard("hypothesis", "1.2", "parsing")
    def from_markdown(cls, markdown: str) -> Optional['Hypothesis']:
        """
        Создает гипотезу из формата Markdown.
        
        Args:
            markdown: Строка с гипотезой в формате Markdown
        
        Returns:
            Объект гипотезы или None, если парсинг не удался
        """
        try:
            # Извлекаем заголовок (формулировку гипотезы)
            title_match = re.search(r'#\s+🧪\s+Гипотеза:\s+(.*?)$', markdown, re.MULTILINE)
            if not title_match:
                logger.warning("Не удалось найти заголовок гипотезы в Markdown")
                return None
            
            statement = title_match.group(1).strip()
            
            # Извлекаем идентификатор
            id_match = re.search(r'\*\*Идентификатор:\*\*\s+(.*?)$', markdown, re.MULTILINE)
            id = id_match.group(1).strip() if id_match else f"hypothesis_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Извлекаем статус
            status_match = re.search(r'\*\*Статус:\*\*\s+(.*?)$', markdown, re.MULTILINE)
            status = status_match.group(1).strip() if status_match else "NEW"
            
            # Извлекаем даты
            created_match = re.search(r'\*\*Создана:\*\*\s+(.*?)$', markdown, re.MULTILINE)
            created_at = None
            if created_match and created_match.group(1).strip() != "N/A":
                try:
                    created_at = datetime.datetime.strptime(created_match.group(1).strip(), "%Y-%m-%d %H:%M")
                except ValueError:
                    created_at = datetime.datetime.now()
            else:
                created_at = datetime.datetime.now()
            
            updated_match = re.search(r'\*\*Обновлена:\*\*\s+(.*?)$', markdown, re.MULTILINE)
            updated_at = None
            if updated_match and updated_match.group(1).strip() != "N/A":
                try:
                    updated_at = datetime.datetime.strptime(updated_match.group(1).strip(), "%Y-%m-%d %H:%M")
                except ValueError:
                    updated_at = datetime.datetime.now()
            else:
                updated_at = datetime.datetime.now()
            
            # Извлекаем теги
            tags_match = re.search(r'\*\*Теги:\*\*\s+(.*?)$', markdown, re.MULTILINE)
            tags = []
            if tags_match and tags_match.group(1).strip() != "Нет тегов":
                tags = [tag.strip() for tag in tags_match.group(1).split(',')]
            
            # Извлекаем секции
            context = cls._extract_section(markdown, "Контекст")
            verification_method = cls._extract_section(markdown, "Метод проверки")
            experiment_design = cls._extract_section(markdown, "Дизайн эксперимента")
            expected_results = cls._extract_section(markdown, "Ожидаемые результаты")
            actual_results = cls._extract_section(markdown, "Фактические результаты")
            conclusion = cls._extract_section(markdown, "Заключение")
            
            # Извлекаем связанные инциденты
            related_incidents = []
            related_section = cls._extract_section(markdown, "Связанные инциденты")
            if related_section and related_section != "Нет связанных инцидентов":
                # Ищем идентификаторы инцидентов в абстрактных ссылках
                incident_matches = re.finditer(r'\[([^\]]+)\]\(abstract://incident:([^\)]+)\)', related_section)
                for match in incident_matches:
                    incident_id = match.group(2).strip()
                    related_incidents.append(incident_id)
            
            return cls(
                id=id,
                statement=statement,
                context=context,
                status=status,
                verification_method=verification_method,
                experiment_design=experiment_design,
                expected_results=expected_results,
                actual_results=actual_results,
                conclusion=conclusion,
                created_at=created_at,
                updated_at=updated_at,
                tags=tags,
                related_incidents=related_incidents
            )
        
        except Exception as e:
            logger.error(f"Ошибка при парсинге гипотезы из Markdown: {e}")
            return None
    
    @staticmethod
    def _extract_section(markdown: str, section_name: str) -> str:
        """
        Извлекает содержимое секции из Markdown.
        
        Args:
            markdown: Строка в формате Markdown
            section_name: Название секции
        
        Returns:
            Содержимое секции или пустая строка, если секция не найдена
        """
        pattern = rf'## {re.escape(section_name)}\n(.*?)(?:\n##|\Z)'
        match = re.search(pattern, markdown, re.DOTALL)
        return match.group(1).strip() if match else ""


@implements_standard("hypothesis", "1.2", "storage")
class HypothesisStorage:
    """Хранилище гипотез в соответствии со стандартом Hypothesis v1.2."""
    
    _instance = None
    
    def __new__(cls):
        """Создает синглтон для управления гипотезами."""
        if cls._instance is None:
            cls._instance = super(HypothesisStorage, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализирует хранилище гипотез."""
        if getattr(self, '_initialized', False):
            return
        
        self._hypotheses = {}
        self._initialized = True
        logger.info("Инициализировано хранилище гипотез")
    
    @implements_standard("hypothesis", "1.2", "creation")
    def create_hypothesis(self, hypothesis: Hypothesis) -> str:
        """
        Создает новую гипотезу в хранилище.
        
        Args:
            hypothesis: Объект гипотезы
        
        Returns:
            Идентификатор созданной гипотезы
        """
        # Добавляем гипотезу в хранилище
        self._hypotheses[hypothesis.id] = hypothesis
        
        logger.info(f"Создана новая гипотеза: {hypothesis.id}")
        return hypothesis.id
    
    @implements_standard("hypothesis", "1.2", "retrieval")
    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """
        Возвращает гипотезу по идентификатору.
        
        Args:
            hypothesis_id: Идентификатор гипотезы
        
        Returns:
            Объект гипотезы или None, если гипотеза не найдена
        """
        return self._hypotheses.get(hypothesis_id)
    
    @implements_standard("hypothesis", "1.2", "retrieval")
    def get_all_hypotheses(self) -> List[Hypothesis]:
        """
        Возвращает список всех гипотез.
        
        Returns:
            Список всех гипотез
        """
        return list(self._hypotheses.values())
    
    @implements_standard("hypothesis", "1.2", "update")
    def update_hypothesis(self, hypothesis: Hypothesis) -> bool:
        """
        Обновляет существующую гипотезу.
        
        Args:
            hypothesis: Обновленный объект гипотезы
        
        Returns:
            True, если обновление прошло успешно, иначе False
        """
        if hypothesis.id not in self._hypotheses:
            logger.warning(f"Гипотеза не найдена: {hypothesis.id}")
            return False
        
        # Обновляем дату последнего обновления
        hypothesis.updated_at = datetime.datetime.now()
        
        # Обновляем гипотезу в хранилище
        self._hypotheses[hypothesis.id] = hypothesis
        
        logger.info(f"Обновлена гипотеза: {hypothesis.id}")
        return True
    
    @implements_standard("hypothesis", "1.2", "filtering")
    def find_hypotheses_by_status(self, status: str) -> List[Hypothesis]:
        """
        Находит гипотезы с указанным статусом.
        
        Args:
            status: Статус гипотез
        
        Returns:
            Список гипотез с указанным статусом
        """
        return [h for h in self._hypotheses.values() if h.status == status]
    
    @implements_standard("hypothesis", "1.2", "filtering")
    def find_hypotheses_by_tag(self, tag: str) -> List[Hypothesis]:
        """
        Находит гипотезы с указанным тегом.
        
        Args:
            tag: Тег для поиска
        
        Returns:
            Список гипотез с указанным тегом
        """
        return [h for h in self._hypotheses.values() if tag in h.tags]
    
    @implements_standard("hypothesis", "1.2", "filtering")
    def find_hypotheses_by_incident(self, incident_id: str) -> List[Hypothesis]:
        """
        Находит гипотезы, связанные с указанным инцидентом.
        
        Args:
            incident_id: Идентификатор инцидента
        
        Returns:
            Список гипотез, связанных с указанным инцидентом
        """
        return [h for h in self._hypotheses.values() if incident_id in h.related_incidents]
    
    @implements_standard("hypothesis", "1.2", "deletion")
    def delete_hypothesis(self, hypothesis_id: str) -> bool:
        """
        Удаляет гипотезу.
        
        Args:
            hypothesis_id: Идентификатор гипотезы
        
        Returns:
            True, если удаление прошло успешно, иначе False
        """
        if hypothesis_id not in self._hypotheses:
            logger.warning(f"Гипотеза не найдена: {hypothesis_id}")
            return False
        
        # Удаляем гипотезу из хранилища
        del self._hypotheses[hypothesis_id]
        
        logger.info(f"Удалена гипотеза: {hypothesis_id}")
        return True


# Создаем глобальный экземпляр для удобного импорта
hypothesis_storage = HypothesisStorage()


# Функции-хелперы для работы с гипотезами
@implements_standard("hypothesis", "1.2", "creation")
def create_hypothesis(
    statement: str,
    context: str = "",
    verification_method: str = "",
    experiment_design: str = "",
    expected_results: str = "",
    tags: Optional[List[str]] = None,
    related_incidents: Optional[List[str]] = None
) -> str:
    """
    Создает новую гипотезу.
    
    Args:
        statement: Формулировка гипотезы
        context: Контекст, в котором возникла гипотеза
        verification_method: Метод проверки гипотезы
        experiment_design: Дизайн эксперимента для проверки
        expected_results: Ожидаемые результаты
        tags: Теги гипотезы
        related_incidents: Связанные инциденты
    
    Returns:
        Идентификатор созданной гипотезы
    """
    # Генерируем уникальный идентификатор
    hypothesis_id = f"hypothesis_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Создаем объект гипотезы
    hypothesis = Hypothesis(
        id=hypothesis_id,
        statement=statement,
        context=context,
        verification_method=verification_method,
        experiment_design=experiment_design,
        expected_results=expected_results,
        tags=tags or [],
        related_incidents=related_incidents or []
    )
    
    # Добавляем гипотезу в хранилище
    return hypothesis_storage.create_hypothesis(hypothesis)


@implements_standard("hypothesis", "1.2", "verification")
def verify_hypothesis(
    hypothesis_id: str,
    actual_results: str,
    conclusion: str,
    status: str
) -> bool:
    """
    Верифицирует гипотезу.
    
    Args:
        hypothesis_id: Идентификатор гипотезы
        actual_results: Фактические результаты проверки
        conclusion: Заключение по результатам проверки
        status: Новый статус гипотезы (CONFIRMED, REJECTED, UNCERTAIN)
    
    Returns:
        True, если верификация прошла успешно, иначе False
    """
    # Проверяем корректность статуса
    if status not in ["CONFIRMED", "REJECTED", "UNCERTAIN"]:
        logger.warning(f"Некорректный статус верификации: {status}")
        return False
    
    # Получаем гипотезу
    hypothesis = hypothesis_storage.get_hypothesis(hypothesis_id)
    if not hypothesis:
        logger.warning(f"Гипотеза не найдена: {hypothesis_id}")
        return False
    
    # Обновляем гипотезу
    hypothesis.actual_results = actual_results
    hypothesis.conclusion = conclusion
    hypothesis.status = status
    
    # Сохраняем изменения
    return hypothesis_storage.update_hypothesis(hypothesis)


@implements_standard("hypothesis", "1.2", "relation")
def add_incident_to_hypothesis(hypothesis_id: str, incident_id: str) -> bool:
    """
    Добавляет связь с инцидентом к гипотезе.
    
    Args:
        hypothesis_id: Идентификатор гипотезы
        incident_id: Идентификатор инцидента
    
    Returns:
        True, если добавление прошло успешно, иначе False
    """
    # Получаем гипотезу
    hypothesis = hypothesis_storage.get_hypothesis(hypothesis_id)
    if not hypothesis:
        logger.warning(f"Гипотеза не найдена: {hypothesis_id}")
        return False
    
    # Добавляем связь с инцидентом
    if incident_id not in hypothesis.related_incidents:
        hypothesis.related_incidents.append(incident_id)
    
    # Сохраняем изменения
    return hypothesis_storage.update_hypothesis(hypothesis)


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Создаем гипотезу
    hypothesis_id = create_hypothesis(
        statement="Использование кэширования документов улучшит производительность системы на 30%",
        context="В настоящее время система испытывает проблемы с производительностью при работе с большим количеством документов.",
        verification_method="A/B тестирование на подмножестве пользователей",
        experiment_design="1. Реализовать механизм кэширования документов\n2. Настроить A/B тестирование\n3. Сравнить производительность систем с кэшированием и без него",
        expected_results="Ожидается улучшение производительности на 30% при работе с большим количеством документов",
        tags=["performance", "caching", "optimization"],
        related_incidents=["incident_performance_20250510"]
    )
    
    print(f"Создана гипотеза: {hypothesis_id}")
    
    # Получаем гипотезу
    hypothesis = hypothesis_storage.get_hypothesis(hypothesis_id)
    if hypothesis:
        print(f"Формулировка гипотезы: {hypothesis.statement}")
        
        # Верифицируем гипотезу
        verify_hypothesis(
            hypothesis_id=hypothesis_id,
            actual_results="Реализация кэширования документов улучшила производительность системы на 25-28% при работе с большим количеством документов.",
            conclusion="Гипотеза в целом подтверждена, хотя улучшение производительности несколько ниже ожидаемого.",
            status="CONFIRMED"
        )
        
        # Получаем обновленную гипотезу
        updated_hypothesis = hypothesis_storage.get_hypothesis(hypothesis_id)
        if updated_hypothesis:
            print(f"Статус гипотезы: {updated_hypothesis.status}")
            print(f"Заключение: {updated_hypothesis.conclusion}")
            
            # Выводим гипотезу в формате Markdown
            markdown = updated_hypothesis.to_markdown()
            print("\nГипотеза в формате Markdown:")
            print(markdown)