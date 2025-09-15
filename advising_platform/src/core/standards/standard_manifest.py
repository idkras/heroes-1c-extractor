"""
Модуль определения и валидации мини-манифестов для стандартов.

Реализует концепцию мини-манифеста, который содержит ответы на ключевые вопросы:
- Зачем нужен стандарт?
- Какая боль его вызвала?
- Какие стандарты он отменяет или дополняет?
- Что будет, если его не соблюдать?

Автор: AI Assistant
Дата: 20 мая 2025
"""

import re
import os
import json
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Any, Tuple, Union, ClassVar

# Настройка логирования
logger = logging.getLogger("standard_manifest")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class ManifestSectionType(Enum):
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ManifestSectionType, чтобы эффективно решать соответствующие задачи в системе.
    
    Типы разделов манифеста."""
    PURPOSE = "purpose"  # Зачем нужен стандарт
    PAIN = "pain"  # Какая боль его вызвала
    RELATIONS = "relations"  # Какие стандарты он отменяет или дополняет
    CONSEQUENCES = "consequences"  # Что будет, если его не соблюдать
    UNKNOWN = "unknown"  # Неизвестный тип раздела


@dataclass
class ManifestSection:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ManifestSection, чтобы эффективно решать соответствующие задачи в системе.
    
    Раздел манифеста с контентом и метаданными."""
    
    type: ManifestSectionType
    title: str
    content: str
    line_start: int
    line_end: int
    
    def to_dict(self) -> Dict[str, Any]:
        """JTBD:
Я (разработчик) хочу использовать функцию to_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Преобразует раздел в словарь."""
        return {
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "line_start": self.line_start,
            "line_end": self.line_end
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ManifestSection':
        """JTBD:
Я (разработчик) хочу использовать функцию from_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Создает раздел из словаря."""
        return cls(
            type=ManifestSectionType(data.get("type", "unknown")),
            title=data.get("title", ""),
            content=data.get("content", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0)
        )


@dataclass
class StandardManifest:
    """
    Полное представление мини-манифеста стандарта со всеми необходимыми разделами.
    
    Содержит информацию о:
    - Цели стандарта (зачем он нужен)
    - Боли, которую он решает
    - Связях с другими стандартами
    - Последствиях несоблюдения
    """
    
    # Разделы манифеста
    purpose: Optional[ManifestSection] = None
    pain: Optional[ManifestSection] = None
    relations: Optional[ManifestSection] = None
    consequences: Optional[ManifestSection] = None
    
    # Исходный документ
    title: str = ""
    file_path: str = ""
    
    # Метаданные
    is_complete: bool = False
    missing_sections: List[str] = field(default_factory=list)
    
    # Регулярные выражения для разделов
    SECTION_PATTERNS: ClassVar[Dict[ManifestSectionType, List[str]]] = {
        ManifestSectionType.PURPOSE: [
            r"## Зачем(\s+нужен)?(\s+этот)?(\s+стандарт)?",
            r"## Цель(\s+стандарта)?",
            r"## Назначение(\s+стандарта)?",
            r"## Для чего(\s+нужен)?(\s+этот)?(\s+стандарт)?"
        ],
        ManifestSectionType.PAIN: [
            r"## Кака[яй](\s+боль)?(\s+проблема)?(\s+его)?(\s+вызвала)?",
            r"## Проблема(\s+которую)?(\s+решает)?(\s+стандарт)?",
            r"## Причина(\s+создания)?(\s+стандарта)?",
            r"## Болевая(\s+точка)?",
            r"## Болевые(\s+точки)?"
        ],
        ManifestSectionType.RELATIONS: [
            r"## Какие(\s+другие)?(\s+стандарты)?(\s+он)?(\s+отменяет)?(\s+или)?(\s+дополняет)?",
            r"## Связь(\s+с)?(\s+другими)?(\s+стандартами)?",
            r"## Отношение(\s+к)?(\s+другим)?(\s+стандартам)?",
            r"## Влияние(\s+на)?(\s+другие)?(\s+стандарты)?"
        ],
        ManifestSectionType.CONSEQUENCES: [
            r"## Что(\s+будет)?(\s+если)?(\s+его)?(\s+не)?(\s+соблюдать)?",
            r"## Последствия(\s+несоблюдения)?(\s+стандарта)?",
            r"## Риски(\s+при)?(\s+несоблюдении)?(\s+стандарта)?",
            r"## Опасности(\s+несоблюдения)?(\s+стандарта)?"
        ]
    }
    
    @staticmethod
    def match_section_type(heading: str) -> Tuple[ManifestSectionType, str]:
        """
        Определяет тип раздела по заголовку.
        
        Args:
            heading: Заголовок раздела
            
        Returns:
            Тип раздела и исходный заголовок
        """
        for section_type, patterns in StandardManifest.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, heading, re.IGNORECASE):
                    return section_type, heading
        
        return ManifestSectionType.UNKNOWN, heading
    
    @classmethod
    def from_markdown(cls, content: str, file_path: str = "") -> 'StandardManifest':
        """
        Создает манифест из Markdown-документа.
        
        Args:
            content: Содержимое Markdown-документа
            file_path: Путь к файлу
            
        Returns:
            Манифест стандарта
        """
        manifest = cls(file_path=file_path)
        
        # Разделяем документ на строки
        lines = content.split("\n")
        
        # Извлекаем заголовок документа
        title_line = next((line for line in lines if line.startswith("# ")), "")
        if title_line:
            manifest.title = title_line[2:].strip()
        
        # Индексы начала разделов
        section_starts = []
        
        # Находим все заголовки второго уровня
        for i, line in enumerate(lines):
            if line.startswith("## "):
                section_type, heading = cls.match_section_type(line)
                if section_type != ManifestSectionType.UNKNOWN:
                    section_starts.append((i, section_type, heading))
        
        # Извлекаем содержимое разделов
        for i, (line_idx, section_type, heading) in enumerate(section_starts):
            # Определяем конец раздела (начало следующего или конец файла)
            end_idx = section_starts[i + 1][0] - 1 if i + 1 < len(section_starts) else len(lines)
            
            # Извлекаем содержимое раздела
            section_content = "\n".join(lines[line_idx + 1:end_idx + 1]).strip()
            
            # Создаем раздел
            section = ManifestSection(
                type=section_type,
                title=heading[3:].strip(),  # Убираем "## "
                content=section_content,
                line_start=line_idx + 1,  # +1, чтобы пропустить заголовок
                line_end=end_idx
            )
            
            # Добавляем раздел в манифест
            if section_type == ManifestSectionType.PURPOSE:
                manifest.purpose = section
            elif section_type == ManifestSectionType.PAIN:
                manifest.pain = section
            elif section_type == ManifestSectionType.RELATIONS:
                manifest.relations = section
            elif section_type == ManifestSectionType.CONSEQUENCES:
                manifest.consequences = section
        
        # Проверяем полноту манифеста
        manifest.validate()
        
        return manifest
    
    def validate(self) -> bool:
        """
        Проверяет полноту манифеста.
        
        Returns:
            True, если манифест полный, иначе False
        """
        # Список отсутствующих разделов
        self.missing_sections = []
        
        # Проверяем наличие всех необходимых разделов
        if not self.purpose:
            self.missing_sections.append("Зачем нужен стандарт")
        
        if not self.pain:
            self.missing_sections.append("Какая боль его вызвала")
        
        if not self.relations:
            self.missing_sections.append("Какие стандарты он отменяет или дополняет")
        
        if not self.consequences:
            self.missing_sections.append("Что будет, если его не соблюдать")
        
        # Устанавливаем флаг полноты
        self.is_complete = len(self.missing_sections) == 0
        
        return self.is_complete
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует манифест в словарь.
        
        Returns:
            Словарь с данными манифеста
        """
        return {
            "title": self.title,
            "file_path": self.file_path,
            "is_complete": self.is_complete,
            "missing_sections": self.missing_sections,
            "purpose": self.purpose.to_dict() if self.purpose else None,
            "pain": self.pain.to_dict() if self.pain else None,
            "relations": self.relations.to_dict() if self.relations else None,
            "consequences": self.consequences.to_dict() if self.consequences else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StandardManifest':
        """
        Создает манифест из словаря.
        
        Args:
            data: Словарь с данными манифеста
            
        Returns:
            Манифест стандарта
        """
        manifest = cls(
            title=data.get("title", ""),
            file_path=data.get("file_path", ""),
            is_complete=data.get("is_complete", False),
            missing_sections=data.get("missing_sections", [])
        )
        
        # Восстанавливаем разделы
        if data.get("purpose"):
            manifest.purpose = ManifestSection.from_dict(data["purpose"])
        
        if data.get("pain"):
            manifest.pain = ManifestSection.from_dict(data["pain"])
        
        if data.get("relations"):
            manifest.relations = ManifestSection.from_dict(data["relations"])
        
        if data.get("consequences"):
            manifest.consequences = ManifestSection.from_dict(data["consequences"])
        
        return manifest
    
    def to_markdown(self) -> str:
        """
        Преобразует манифест в Markdown.
        
        Returns:
            Markdown-представление манифеста
        """
        lines = []
        
        # Добавляем заголовок документа
        if self.title:
            lines.append(f"# {self.title}")
            lines.append("")
        
        # Добавляем разделы манифеста
        for section_type, section in [
            (ManifestSectionType.PURPOSE, self.purpose),
            (ManifestSectionType.PAIN, self.pain),
            (ManifestSectionType.RELATIONS, self.relations),
            (ManifestSectionType.CONSEQUENCES, self.consequences)
        ]:
            if section:
                lines.append(f"## {section.title}")
                lines.append("")
                lines.append(section.content)
                lines.append("")
            else:
                # Добавляем заглушку для отсутствующего раздела
                if section_type == ManifestSectionType.PURPOSE:
                    lines.append("## Зачем нужен стандарт")
                    lines.append("")
                    lines.append("*Этот раздел необходимо заполнить*")
                    lines.append("")
                elif section_type == ManifestSectionType.PAIN:
                    lines.append("## Какая боль его вызвала")
                    lines.append("")
                    lines.append("*Этот раздел необходимо заполнить*")
                    lines.append("")
                elif section_type == ManifestSectionType.RELATIONS:
                    lines.append("## Какие стандарты он отменяет или дополняет")
                    lines.append("")
                    lines.append("*Этот раздел необходимо заполнить*")
                    lines.append("")
                elif section_type == ManifestSectionType.CONSEQUENCES:
                    lines.append("## Что будет, если его не соблюдать")
                    lines.append("")
                    lines.append("*Этот раздел необходимо заполнить*")
                    lines.append("")
        
        return "\n".join(lines)
    
    def generate_completion_suggestions(self) -> Dict[str, str]:
        """
        Генерирует предложения по заполнению отсутствующих разделов.
        
        Returns:
            Словарь с предложениями
        """
        suggestions = {}
        
        # Предложения для каждого отсутствующего раздела
        if not self.purpose:
            suggestions["purpose"] = (
                "Опишите, зачем нужен этот стандарт. Какие задачи он решает? "
                "Какие цели преследует? Какую пользу принесет его внедрение?"
            )
        
        if not self.pain:
            suggestions["pain"] = (
                "Опишите проблему или боль, которая вызвала необходимость создания стандарта. "
                "С какими трудностями сталкивались до его внедрения? "
                "Какие негативные паттерны он устраняет?"
            )
        
        if not self.relations:
            suggestions["relations"] = (
                "Укажите, какие существующие стандарты этот стандарт отменяет, дополняет или заменяет. "
                "Как он соотносится с другими стандартами? "
                "Есть ли конфликты или зависимости?"
            )
        
        if not self.consequences:
            suggestions["consequences"] = (
                "Опишите последствия несоблюдения стандарта. "
                "Какие риски возникают? Какие проблемы могут проявиться? "
                "Как это влияет на качество, производительность, безопасность или другие аспекты?"
            )
        
        return suggestions
    
    def update_section(
        self,
        section_type: ManifestSectionType,
        content: str,
        title: Optional[str] = None
    ) -> bool:
        """
        Обновляет раздел манифеста.
        
        Args:
            section_type: Тип раздела
            content: Новое содержимое
            title: Новый заголовок (если None, используется стандартный)
            
        Returns:
            True, если обновление успешно, иначе False
        """
        # Определяем стандартный заголовок для типа раздела
        if title is None:
            if section_type == ManifestSectionType.PURPOSE:
                title = "Зачем нужен стандарт"
            elif section_type == ManifestSectionType.PAIN:
                title = "Какая боль его вызвала"
            elif section_type == ManifestSectionType.RELATIONS:
                title = "Какие стандарты он отменяет или дополняет"
            elif section_type == ManifestSectionType.CONSEQUENCES:
                title = "Что будет, если его не соблюдать"
            else:
                return False
        
        # Создаем новый раздел
        section = ManifestSection(
            type=section_type,
            title=title,
            content=content,
            line_start=0,  # Будет обновлено при сохранении
            line_end=0     # Будет обновлено при сохранении
        )
        
        # Обновляем соответствующий раздел манифеста
        if section_type == ManifestSectionType.PURPOSE:
            self.purpose = section
        elif section_type == ManifestSectionType.PAIN:
            self.pain = section
        elif section_type == ManifestSectionType.RELATIONS:
            self.relations = section
        elif section_type == ManifestSectionType.CONSEQUENCES:
            self.consequences = section
        else:
            return False
        
        # Обновляем статус полноты
        self.validate()
        
        return True
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        Сохраняет манифест в файл.
        
        Args:
            file_path: Путь к файлу (если None, используется self.file_path)
            
        Returns:
            True, если сохранение успешно, иначе False
        """
        target_path = file_path if file_path is not None else self.file_path
        
        if not target_path:
            logger.error("Не указан путь для сохранения манифеста")
            return False
        
        try:
            # Подстраховка от None для типизации
            if target_path is None:
                logger.error("Не указан путь для сохранения манифеста")
                return False

            # Создаем директории, если их нет
            directory = os.path.dirname(os.path.abspath(target_path))
            os.makedirs(directory, exist_ok=True)
            
            # Формируем Markdown
            markdown = self.to_markdown()
            
            # Сохраняем в файл
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении манифеста в файл {target_path}: {e}")
            return False


class StandardManifestValidator:
    """
    Валидатор манифестов стандартов.
    
    Проверяет Markdown-документы на соответствие требованиям к мини-манифестам
    и формирует отчеты о соответствии.
    """
    
    def __init__(self, base_dir: str = "[standards .md]"):
        """
        Инициализация валидатора.
        
        Args:
            base_dir: Базовая директория стандартов
        """
        self.base_dir = base_dir
        self.validation_results = {}
    
    def validate_file(self, file_path: str) -> Tuple[bool, StandardManifest]:
        """
        Проверяет файл на соответствие требованиям к мини-манифестам.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Кортеж (результат проверки, манифест)
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                logger.error(f"Файл {file_path} не существует")
                empty_manifest = StandardManifest()
                empty_manifest.file_path = file_path
                return False, empty_manifest
            
            # Читаем содержимое файла
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Создаем манифест
            manifest = StandardManifest.from_markdown(content, file_path)
            
            # Сохраняем результат проверки
            self.validation_results[file_path] = manifest.is_complete
            
            return manifest.is_complete, manifest
        except Exception as e:
            logger.error(f"Ошибка при проверке файла {file_path}: {e}")
            empty_manifest = StandardManifest()
            empty_manifest.file_path = file_path
            return False, empty_manifest
    
    def validate_directory(self, directory: str = None) -> Dict[str, bool]:
        """
        Проверяет все Markdown-файлы в директории.
        
        Args:
            directory: Путь к директории (если None, используется self.base_dir)
            
        Returns:
            Словарь {путь к файлу: результат проверки}
        """
        if directory is None:
            directory = self.base_dir
        
        results = {}
        
        try:
            # Проверяем существование директории
            if not os.path.exists(directory):
                logger.error(f"Директория {directory} не существует")
                return results
            
            # Обходим все файлы в директории
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        is_valid, _ = self.validate_file(file_path)
                        results[file_path] = is_valid
        except Exception as e:
            logger.error(f"Ошибка при проверке директории {directory}: {e}")
        
        return results
    
    def generate_validation_report(self, directory: str = None) -> Dict[str, Any]:
        """
        Генерирует отчет о проверке директории.
        
        Args:
            directory: Путь к директории (если None, используется self.base_dir)
            
        Returns:
            Словарь с данными отчета
        """
        if directory is None:
            directory = self.base_dir
        
        # Выполняем проверку, если она не была выполнена ранее
        if not self.validation_results:
            self.validate_directory(directory)
        
        # Собираем статистику
        total_files = len(self.validation_results)
        valid_files = sum(self.validation_results.values())
        invalid_files = total_files - valid_files
        
        # Собираем информацию о некорректных файлах
        invalid_file_details = {}
        for file_path, is_valid in self.validation_results.items():
            if not is_valid:
                # Получаем манифест для этого файла
                _, manifest = self.validate_file(file_path)
                
                # Сохраняем детали
                invalid_file_details[file_path] = {
                    "missing_sections": manifest.missing_sections,
                    "suggestions": manifest.generate_completion_suggestions()
                }
        
        # Формируем отчет
        report = {
            "directory": directory,
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "compliance_rate": valid_files / total_files if total_files > 0 else 0,
            "invalid_file_details": invalid_file_details
        }
        
        return report


class StandardTemplate:
    """
    Шаблоны для стандартов с мини-манифестами.
    
    Предоставляет готовые шаблоны для создания новых стандартов
    с учетом требований к мини-манифестам.
    """
    
    @staticmethod
    def get_basic_template(title: str) -> str:
        """
        Получает базовый шаблон стандарта.
        
        Args:
            title: Заголовок стандарта
            
        Returns:
            Шаблон в формате Markdown
        """
        return f"""# {title}

## Зачем нужен стандарт

*Опишите, зачем нужен этот стандарт. Какие задачи он решает? Какие цели преследует? Какую пользу принесет его внедрение?*

## Какая боль его вызвала

*Опишите проблему или боль, которая вызвала необходимость создания стандарта. С какими трудностями сталкивались до его внедрения? Какие негативные паттерны он устраняет?*

## Какие стандарты он отменяет или дополняет

*Укажите, какие существующие стандарты этот стандарт отменяет, дополняет или заменяет. Как он соотносится с другими стандартами? Есть ли конфликты или зависимости?*

## Что будет, если его не соблюдать

*Опишите последствия несоблюдения стандарта. Какие риски возникают? Какие проблемы могут проявиться? Как это влияет на качество, производительность, безопасность или другие аспекты?*

## Содержание стандарта

*Здесь начинается непосредственное содержание стандарта...*
"""
    
    @staticmethod
    def get_process_template(title: str) -> str:
        """
        Получает шаблон стандарта процесса.
        
        Args:
            title: Заголовок стандарта
            
        Returns:
            Шаблон в формате Markdown
        """
        return f"""# {title}

## Зачем нужен стандарт

*Опишите, зачем нужен этот стандарт процесса. Какие задачи он решает? Какие цели преследует? Какую пользу принесет его внедрение?*

## Какая боль его вызвала

*Опишите проблему или боль, которая вызвала необходимость создания стандарта. С какими трудностями сталкивались до его внедрения? Какие негативные паттерны он устраняет?*

## Какие стандарты он отменяет или дополняет

*Укажите, какие существующие стандарты этот стандарт отменяет, дополняет или заменяет. Как он соотносится с другими стандартами? Есть ли конфликты или зависимости?*

## Что будет, если его не соблюдать

*Опишите последствия несоблюдения стандарта. Какие риски возникают? Какие проблемы могут проявиться? Как это влияет на качество, производительность, безопасность или другие аспекты?*

## Шаги процесса

1. **Шаг 1**
   - Описание действия
   - Ответственные
   - Результат

2. **Шаг 2**
   - Описание действия
   - Ответственные
   - Результат

3. **Шаг 3**
   - Описание действия
   - Ответственные
   - Результат

## Критерии качества

- Критерий 1: описание
- Критерий 2: описание
- Критерий 3: описание

## Примеры и шаблоны

*Приложите примеры и шаблоны, если применимо*
"""
    
    @staticmethod
    def get_code_template(title: str) -> str:
        """
        Получает шаблон стандарта кода.
        
        Args:
            title: Заголовок стандарта
            
        Returns:
            Шаблон в формате Markdown
        """
        return f"""# {title}

## Зачем нужен стандарт

*Опишите, зачем нужен этот стандарт кода. Какие задачи он решает? Какие цели преследует? Какую пользу принесет его внедрение?*

## Какая боль его вызвала

*Опишите проблему или боль, которая вызвала необходимость создания стандарта. С какими трудностями сталкивались до его внедрения? Какие негативные паттерны он устраняет?*

## Какие стандарты он отменяет или дополняет

*Укажите, какие существующие стандарты этот стандарт отменяет, дополняет или заменяет. Как он соотносится с другими стандартами? Есть ли конфликты или зависимости?*

## Что будет, если его не соблюдать

*Опишите последствия несоблюдения стандарта. Какие риски возникают? Какие проблемы могут проявиться? Как это влияет на качество, производительность, безопасность или другие аспекты?*

## Правила

### Правило 1: Название правила

```python
# Неправильно
def bad_example():
    # Пример плохого кода
    pass

# Правильно
def good_example():
    # Пример хорошего кода
    pass
```

Объяснение правила и причины его введения.

### Правило 2: Название правила

```python
# Неправильно
def another_bad_example():
    # Пример плохого кода
    pass

# Правильно
def another_good_example():
    # Пример хорошего кода
    pass
```

Объяснение правила и причины его введения.

## Инструменты и автоматизация

*Опишите инструменты и средства автоматизации для проверки соответствия стандарту*
"""
    
    @staticmethod
    def get_design_template(title: str) -> str:
        """
        Получает шаблон стандарта дизайна.
        
        Args:
            title: Заголовок стандарта
            
        Returns:
            Шаблон в формате Markdown
        """
        return f"""# {title}

## Зачем нужен стандарт

*Опишите, зачем нужен этот стандарт дизайна. Какие задачи он решает? Какие цели преследует? Какую пользу принесет его внедрение?*

## Какая боль его вызвала

*Опишите проблему или боль, которая вызвала необходимость создания стандарта. С какими трудностями сталкивались до его внедрения? Какие негативные паттерны он устраняет?*

## Какие стандарты он отменяет или дополняет

*Укажите, какие существующие стандарты этот стандарт отменяет, дополняет или заменяет. Как он соотносится с другими стандартами? Есть ли конфликты или зависимости?*

## Что будет, если его не соблюдать

*Опишите последствия несоблюдения стандарта. Какие риски возникают? Какие проблемы могут проявиться? Как это влияет на качество, производительность, безопасность или другие аспекты?*

## Принципы дизайна

- **Принцип 1:** описание
- **Принцип 2:** описание
- **Принцип 3:** описание

## Компоненты и элементы

### Компонент 1

![Компонент 1](ссылка_на_изображение)

- Описание
- Использование
- Ограничения

### Компонент 2

![Компонент 2](ссылка_на_изображение)

- Описание
- Использование
- Ограничения

## Примеры и ресурсы

*Приложите примеры и ссылки на дополнительные ресурсы*
"""


def main():
    """JTBD:
Я (разработчик) хочу использовать функцию main, чтобы эффективно выполнить соответствующую операцию.
     
     Основная функция модуля."""
    import argparse
    
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description="Инструменты для работы с мини-манифестами стандартов")
    
    # Добавляем подкоманды
    subparsers = parser.add_subparsers(dest="command", help="Команда для выполнения")
    
    # Подкоманда для проверки файла
    validate_parser = subparsers.add_parser("validate", help="Проверить файл на соответствие требованиям к мини-манифестам")
    validate_parser.add_argument("file_path", help="Путь к файлу")
    
    # Подкоманда для проверки директории
    validate_dir_parser = subparsers.add_parser("validate-dir", help="Проверить директорию на соответствие требованиям к мини-манифестам")
    validate_dir_parser.add_argument("directory", nargs="?", default="[standards .md]", help="Путь к директории")
    
    # Подкоманда для создания шаблона
    template_parser = subparsers.add_parser("template", help="Создать шаблон стандарта")
    template_parser.add_argument("file_path", help="Путь к файлу")
    template_parser.add_argument("title", help="Заголовок стандарта")
    template_parser.add_argument("--type", choices=["basic", "process", "code", "design"], default="basic", help="Тип шаблона")
    
    # Подкоманда для обновления раздела манифеста
    update_parser = subparsers.add_parser("update-section", help="Обновить раздел манифеста")
    update_parser.add_argument("file_path", help="Путь к файлу")
    update_parser.add_argument("section", choices=["purpose", "pain", "relations", "consequences"], help="Тип раздела")
    update_parser.add_argument("content", help="Содержимое раздела")
    
    # Разбор аргументов
    args = parser.parse_args()
    
    # Выполняем команду
    if args.command == "validate":
        validator = StandardManifestValidator()
        is_valid, manifest = validator.validate_file(args.file_path)
        
        if is_valid:
            print(f"Файл {args.file_path} соответствует требованиям к мини-манифестам")
        else:
            print(f"Файл {args.file_path} не соответствует требованиям к мини-манифестам")
            print("Отсутствующие разделы:")
            for section in manifest.missing_sections:
                print(f"- {section}")
            
            print("\nРекомендации по заполнению:")
            for section, suggestion in manifest.generate_completion_suggestions().items():
                print(f"- {section.capitalize()}: {suggestion}")
    
    elif args.command == "validate-dir":
        validator = StandardManifestValidator()
        results = validator.validate_directory(args.directory)
        
        total_files = len(results)
        valid_files = sum(results.values())
        invalid_files = total_files - valid_files
        
        print(f"Проверено файлов: {total_files}")
        print(f"Соответствуют требованиям: {valid_files}")
        print(f"Не соответствуют требованиям: {invalid_files}")
        
        if invalid_files > 0:
            print("\nФайлы, не соответствующие требованиям:")
            for file_path, is_valid in results.items():
                if not is_valid:
                    print(f"- {file_path}")
    
    elif args.command == "template":
        # Выбираем шаблон в зависимости от типа
        if args.type == "basic":
            template = StandardTemplate.get_basic_template(args.title)
        elif args.type == "process":
            template = StandardTemplate.get_process_template(args.title)
        elif args.type == "code":
            template = StandardTemplate.get_code_template(args.title)
        elif args.type == "design":
            template = StandardTemplate.get_design_template(args.title)
        else:
            print(f"Неизвестный тип шаблона: {args.type}")
            return
        
        # Создаем директории, если их нет
        os.makedirs(os.path.dirname(os.path.abspath(args.file_path)), exist_ok=True)
        
        # Сохраняем шаблон в файл
        with open(args.file_path, "w", encoding="utf-8") as f:
            f.write(template)
        
        print(f"Шаблон стандарта создан в файле {args.file_path}")
    
    elif args.command == "update-section":
        # Проверяем существование файла
        if not os.path.exists(args.file_path):
            print(f"Файл {args.file_path} не существует")
            return
        
        # Читаем содержимое файла
        with open(args.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Создаем манифест
        manifest = StandardManifest.from_markdown(content, args.file_path)
        
        # Обновляем раздел
        section_type = ManifestSectionType(args.section)
        success = manifest.update_section(section_type, args.content)
        
        if success:
            # Сохраняем обновленный манифест
            manifest.save_to_file()
            print(f"Раздел {args.section} успешно обновлен в файле {args.file_path}")
        else:
            print(f"Ошибка при обновлении раздела {args.section} в файле {args.file_path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()