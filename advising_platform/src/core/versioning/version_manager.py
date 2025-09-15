"""
Модуль управления версиями документов.

Предоставляет функционал для:
- Автоматического ведения истории изменений документов
- Архивирования старых версий 
- Создания diff-логов в структурированном формате
- Отслеживания авторства и причин изменений

Автор: AI Assistant
Дата: 20 мая 2025
"""

import os
import json
import shutil
import difflib
import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
import csv


class VersionInfo:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса VersionInfo, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для хранения информации о версии документа."""
    
    def __init__(
        self, 
        timestamp: float, 
        author: str, 
        reason: str, 
        file_path: str, 
        version: int
    ):
        """
        Инициализация объекта информации о версии.
        
        Args:
            timestamp: Временная метка создания версии
            author: Автор изменений
            reason: Причина изменений
            file_path: Путь к файлу
            version: Номер версии
        """
        self.timestamp = timestamp
        self.author = author
        self.reason = reason
        self.file_path = file_path
        self.version = version
        self.created_at = datetime.datetime.fromtimestamp(timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """JTBD:
Я (разработчик) хочу использовать функцию to_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Преобразует объект в словарь для сериализации."""
        return {
            "timestamp": self.timestamp,
            "author": self.author,
            "reason": self.reason,
            "file_path": self.file_path,
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionInfo':
        """JTBD:
Я (разработчик) хочу использовать функцию from_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Создает объект из словаря."""
        return cls(
            timestamp=data["timestamp"],
            author=data["author"],
            reason=data["reason"],
            file_path=data["file_path"],
            version=data["version"]
        )


class ChangelogEntry:
    """JTBD:
Я (разработчик) хочу использовать функциональность класса ChangelogEntry, чтобы эффективно решать соответствующие задачи в системе.
    
    Класс для представления записи в журнале изменений."""
    
    def __init__(
        self, 
        old_version: Optional[VersionInfo], 
        new_version: VersionInfo, 
        diff_summary: str
    ):
        """
        Инициализация записи журнала изменений.
        
        Args:
            old_version: Информация о старой версии (может быть None для первой версии)
            new_version: Информация о новой версии
            diff_summary: Краткое описание изменений
        """
        self.old_version = old_version
        self.new_version = new_version
        self.diff_summary = diff_summary
        self.timestamp = new_version.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """JTBD:
Я (разработчик) хочу использовать функцию to_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Преобразует объект в словарь для сериализации."""
        return {
            "old_version": self.old_version.to_dict() if self.old_version else None,
            "new_version": self.new_version.to_dict(),
            "diff_summary": self.diff_summary,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangelogEntry':
        """JTBD:
Я (разработчик) хочу использовать функцию from_dict, чтобы эффективно выполнить соответствующую операцию.
         
         Создает объект из словаря."""
        return cls(
            old_version=VersionInfo.from_dict(data["old_version"]) if data.get("old_version") else None,
            new_version=VersionInfo.from_dict(data["new_version"]),
            diff_summary=data["diff_summary"]
        )


class VersionManager:
    """
    Класс для управления версиями документов.
    
    Обеспечивает:
    - Создание новых версий при изменении документов
    - Архивирование старых версий
    - Ведение журнала изменений
    - Создание diff-логов между версиями
    """
    
    def __init__(self, base_dir: str = "."):
        """
        Инициализация менеджера версий.
        
        Args:
            base_dir: Базовая директория для хранения архивов и журналов
        """
        self.base_dir = base_dir
        self.archive_dir = os.path.join(base_dir, ".version_archive")
        self.changelog_dir = os.path.join(base_dir, ".changelog")
        
        # Создаем директории, если они не существуют
        os.makedirs(self.archive_dir, exist_ok=True)
        os.makedirs(self.changelog_dir, exist_ok=True)
        
        # Кеш для версий и журналов
        self.version_cache = {}
        self.changelog_cache = {}
        
        # Инициализируем кеши
        self._init_caches()
    
    def _init_caches(self):
        """Инициализирует кеши версий и журналов."""
        # Загружаем последние версии для каждого файла
        version_index_path = os.path.join(self.archive_dir, "version_index.json")
        if os.path.exists(version_index_path):
            try:
                with open(version_index_path, "r", encoding="utf-8") as f:
                    self.version_cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке индекса версий: {e}")
                self.version_cache = {}
        
        # Загружаем журналы изменений
        changelog_index_path = os.path.join(self.changelog_dir, "changelog_index.json")
        if os.path.exists(changelog_index_path):
            try:
                with open(changelog_index_path, "r", encoding="utf-8") as f:
                    self.changelog_cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке индекса журналов: {e}")
                self.changelog_cache = {}
    
    def _save_caches(self):
        """Сохраняет кеши версий и журналов."""
        # Сохраняем индекс версий
        version_index_path = os.path.join(self.archive_dir, "version_index.json")
        try:
            with open(version_index_path, "w", encoding="utf-8") as f:
                json.dump(self.version_cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка при сохранении индекса версий: {e}")
        
        # Сохраняем индекс журналов
        changelog_index_path = os.path.join(self.changelog_dir, "changelog_index.json")
        try:
            with open(changelog_index_path, "w", encoding="utf-8") as f:
                json.dump(self.changelog_cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка при сохранении индекса журналов: {e}")
    
    def get_next_version(self, file_path: str) -> int:
        """
        Получает следующий номер версии для файла.
        
        Args:
            file_path: Путь к файлу
        
        Returns:
            Следующий номер версии
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        if rel_path in self.version_cache:
            return self.version_cache[rel_path]["version"] + 1
        return 1
    
    def archive_version(
        self, 
        file_path: str, 
        author: str, 
        reason: str
    ) -> VersionInfo:
        """
        Архивирует текущую версию файла.
        
        Args:
            file_path: Путь к файлу
            author: Автор изменений
            reason: Причина изменений
        
        Returns:
            Информация о созданной версии
        
        Raises:
            FileNotFoundError: Если файл не найден
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")
        
        # Получаем относительный путь
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Получаем новый номер версии
        version = self.get_next_version(file_path)
        
        # Создаем информацию о версии
        timestamp = datetime.datetime.now().timestamp()
        version_info = VersionInfo(
            timestamp=timestamp,
            author=author,
            reason=reason,
            file_path=rel_path,
            version=version
        )
        
        # Создаем директорию для архива файла
        archive_file_dir = os.path.join(self.archive_dir, rel_path)
        os.makedirs(os.path.dirname(archive_file_dir), exist_ok=True)
        
        # Архивируем файл
        archive_file_path = f"{archive_file_dir}.v{version}"
        try:
            shutil.copy2(file_path, archive_file_path)
        except IOError as e:
            print(f"Ошибка при архивировании файла {file_path}: {e}")
            # Создаем пустую версию вместо возврата None
            return VersionInfo(
                timestamp=timestamp,
                author=author,
                reason=f"ОШИБКА АРХИВИРОВАНИЯ: {e}",
                file_path=rel_path,
                version=version
            )
        
        # Сохраняем информацию о версии
        version_info_path = f"{archive_file_path}.info.json"
        try:
            with open(version_info_path, "w", encoding="utf-8") as f:
                json.dump(version_info.to_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка при сохранении информации о версии {version_info_path}: {e}")
        
        # Обновляем кеш версий
        self.version_cache[rel_path] = version_info.to_dict()
        self._save_caches()
        
        return version_info
    
    def get_version_info(self, file_path: str, version: Optional[int] = None) -> VersionInfo:
        """
        Получает информацию о версии файла.
        
        Args:
            file_path: Путь к файлу
            version: Номер версии, если None - возвращает последнюю версию
        
        Returns:
            Информация о версии
        
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если версия не найдена
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        if rel_path not in self.version_cache:
            raise FileNotFoundError(f"Файл {file_path} не найден в архиве версий")
        
        if version is None:
            # Возвращаем последнюю версию
            version_data = self.version_cache[rel_path]
            return VersionInfo.from_dict(version_data)
        
        # Ищем указанную версию
        archive_file_path = os.path.join(self.archive_dir, f"{rel_path}.v{version}")
        version_info_path = f"{archive_file_path}.info.json"
        
        if not os.path.exists(version_info_path):
            raise ValueError(f"Версия {version} файла {file_path} не найдена")
        
        try:
            with open(version_info_path, "r", encoding="utf-8") as f:
                version_data = json.load(f)
            return VersionInfo.from_dict(version_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка при загрузке информации о версии {version_info_path}: {e}")
            raise ValueError(f"Ошибка при загрузке информации о версии {version}: {e}")
    
    def create_diff(self, file_path: str, old_version: int, new_version: int) -> str:
        """
        Создает diff между двумя версиями файла.
        
        Args:
            file_path: Путь к файлу
            old_version: Номер старой версии
            new_version: Номер новой версии
        
        Returns:
            Текст diff в формате unified diff
        
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если версия не найдена
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Получаем пути к архивным файлам
        old_archive_path = os.path.join(self.archive_dir, f"{rel_path}.v{old_version}")
        new_archive_path = os.path.join(self.archive_dir, f"{rel_path}.v{new_version}")
        
        if not os.path.exists(old_archive_path):
            raise ValueError(f"Версия {old_version} файла {file_path} не найдена")
        
        if not os.path.exists(new_archive_path):
            raise ValueError(f"Версия {new_version} файла {file_path} не найдена")
        
        # Читаем содержимое файлов
        try:
            with open(old_archive_path, "r", encoding="utf-8") as f:
                old_content = f.readlines()
            
            with open(new_archive_path, "r", encoding="utf-8") as f:
                new_content = f.readlines()
        except IOError as e:
            print(f"Ошибка при чтении архивных файлов: {e}")
            return ""
        
        # Создаем diff
        diff = difflib.unified_diff(
            old_content,
            new_content,
            fromfile=f"{rel_path}.v{old_version}",
            tofile=f"{rel_path}.v{new_version}",
            lineterm=""
        )
        
        return "\n".join(diff)
    
    def create_changelog_entry(
        self, 
        file_path: str, 
        old_version_info: Optional[VersionInfo], 
        new_version_info: VersionInfo
    ) -> ChangelogEntry:
        """
        Создает запись в журнале изменений.
        
        Args:
            file_path: Путь к файлу
            old_version_info: Информация о старой версии (None для первой версии)
            new_version_info: Информация о новой версии
        
        Returns:
            Запись журнала изменений
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Создаем diff, если есть старая версия
        diff_summary = ""
        if old_version_info:
            try:
                diff = self.create_diff(file_path, old_version_info.version, new_version_info.version)
                # Создаем краткую сводку изменений (первые 5 строк)
                diff_lines = diff.split("\n")
                if len(diff_lines) > 5:
                    diff_summary = "\n".join(diff_lines[:5]) + f"\n... и еще {len(diff_lines) - 5} строк"
                else:
                    diff_summary = diff
            except (ValueError, IOError) as e:
                print(f"Ошибка при создании diff: {e}")
                diff_summary = f"Ошибка при создании diff: {e}"
        else:
            diff_summary = "Создан новый файл"
        
        # Создаем запись журнала
        changelog_entry = ChangelogEntry(
            old_version=old_version_info,
            new_version=new_version_info,
            diff_summary=diff_summary
        )
        
        # Сохраняем запись в журнал
        changelog_file = os.path.join(self.changelog_dir, f"{rel_path}.changelog.json")
        os.makedirs(os.path.dirname(changelog_file), exist_ok=True)
        
        # Загружаем существующий журнал или создаем новый
        entries = []
        if os.path.exists(changelog_file):
            try:
                with open(changelog_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке журнала {changelog_file}: {e}")
                entries = []
        
        # Добавляем новую запись
        entries.append(changelog_entry.to_dict())
        
        # Сохраняем журнал
        try:
            with open(changelog_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка при сохранении журнала {changelog_file}: {e}")
        
        # Обновляем кеш журналов
        if rel_path not in self.changelog_cache:
            self.changelog_cache[rel_path] = []
        self.changelog_cache[rel_path].append(changelog_entry.to_dict())
        self._save_caches()
        
        return changelog_entry
    
    def get_changelog(self, file_path: str) -> List[ChangelogEntry]:
        """
        Получает журнал изменений для файла.
        
        Args:
            file_path: Путь к файлу
        
        Returns:
            Список записей журнала изменений
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        if rel_path not in self.changelog_cache:
            return []
        
        return [ChangelogEntry.from_dict(entry) for entry in self.changelog_cache[rel_path]]
    
    def export_changelog_to_markdown(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Экспортирует журнал изменений в формате Markdown.
        
        Args:
            file_path: Путь к файлу
            output_path: Путь для сохранения Markdown-файла (если None, возвращает текст)
        
        Returns:
            Текст Markdown, если output_path не указан
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Получаем журнал изменений
        changelog_entries = self.get_changelog(file_path)
        if not changelog_entries:
            md_content = f"# Журнал изменений для {rel_path}\n\nИстория изменений не найдена."
        else:
            # Формируем Markdown-документ
            md_content = f"# Журнал изменений для {rel_path}\n\n"
            
            for entry in sorted(changelog_entries, key=lambda x: x.timestamp, reverse=True):
                # Форматируем дату
                date_str = datetime.datetime.fromtimestamp(entry.timestamp).strftime("%d.%m.%Y %H:%M:%S")
                
                md_content += f"## Версия {entry.new_version.version} ({date_str})\n\n"
                md_content += f"**Автор:** {entry.new_version.author}\n\n"
                md_content += f"**Причина:** {entry.new_version.reason}\n\n"
                
                if entry.old_version:
                    md_content += "**Изменения:**\n\n```diff\n"
                    md_content += entry.diff_summary
                    md_content += "\n```\n\n"
                else:
                    md_content += "**Изменения:** Создан новый файл\n\n"
        
        # Сохраняем в файл, если указан путь
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                return f"Журнал изменений сохранен в {output_path}"
            except IOError as e:
                print(f"Ошибка при сохранении журнала в {output_path}: {e}")
                return f"Ошибка при сохранении журнала: {e}"
        
        return md_content
    
    def export_changelog_to_tsv(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Экспортирует журнал изменений в формате TSV.
        
        Args:
            file_path: Путь к файлу
            output_path: Путь для сохранения TSV-файла (если None, возвращает текст)
        
        Returns:
            Текст TSV, если output_path не указан
        """
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Получаем журнал изменений
        changelog_entries = self.get_changelog(file_path)
        
        if not changelog_entries:
            return f"История изменений для {rel_path} не найдена."
        
        # Подготавливаем данные для TSV
        rows = [
            ["Версия", "Дата", "Автор", "Причина", "Изменения"]
        ]
        
        for entry in sorted(changelog_entries, key=lambda x: x.timestamp):
            # Форматируем дату
            date_str = datetime.datetime.fromtimestamp(entry.timestamp).strftime("%d.%m.%Y %H:%M:%S")
            
            # Короткая сводка изменений (первая строка diff)
            changes = entry.diff_summary.split("\n")[0] if entry.diff_summary else "Создан новый файл"
            
            rows.append([
                str(entry.new_version.version),
                date_str,
                entry.new_version.author,
                entry.new_version.reason,
                changes
            ])
        
        # Формируем TSV
        tsv_content = ""
        for row in rows:
            tsv_content += "\t".join(row) + "\n"
        
        # Сохраняем в файл, если указан путь
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f, delimiter="\t")
                    writer.writerows(rows)
                return f"Журнал изменений сохранен в {output_path}"
            except IOError as e:
                print(f"Ошибка при сохранении журнала в {output_path}: {e}")
                return f"Ошибка при сохранении журнала: {e}"
        
        return tsv_content
    
    def create_new_version(
        self, 
        file_path: str, 
        author: str, 
        reason: str
    ) -> Tuple[VersionInfo, ChangelogEntry]:
        """
        Создает новую версию файла с записью в журнале изменений.
        
        Args:
            file_path: Путь к файлу
            author: Автор изменений
            reason: Причина изменений
        
        Returns:
            Кортеж (информация о версии, запись журнала изменений)
        
        Raises:
            FileNotFoundError: Если файл не найден
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")
        
        rel_path = os.path.relpath(file_path, self.base_dir)
        
        # Получаем информацию о текущей версии
        old_version_info = None
        if rel_path in self.version_cache:
            old_version = self.version_cache[rel_path]["version"]
            old_version_info = self.get_version_info(file_path, old_version)
        
        # Архивируем новую версию
        new_version_info = self.archive_version(file_path, author, reason)
        
        # Создаем запись в журнале изменений
        changelog_entry = self.create_changelog_entry(file_path, old_version_info, new_version_info)
        
        return new_version_info, changelog_entry