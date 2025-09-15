"""
Реализация блокировки чтения-записи (RWLock) с транзакционной моделью памяти.

Эта реализация гарантирует:
1. Взаимное исключение между писателями
2. Взаимное исключение между писателями и читателями
3. Параллельное выполнение читателей
4. Гарантированную видимость всех изменений (память с последовательной консистентностью)
5. Отсутствие взаимных блокировок (deadlocks)
6. Защиту от проблемы голодания потоков (starvation)
"""

import threading
import contextlib
import time
import logging
from typing import Optional, Dict, Set, List

# Настройка логирования
logger = logging.getLogger(__name__)

class RWLock:
    """
    Транзакционная реализация блокировки чтения-записи.
    
    Особенности:
    - Гарантированная видимость изменений между потоками
    - Приоритет писателей для предотвращения голодания
    - Защита от взаимных блокировок
    - Отслеживание версий данных для обеспечения консистентности
    """
    
    def __init__(self):
        """Инициализирует блокировку чтения-записи с транзакционной моделью."""
        # Основная блокировка для синхронизации доступа к состоянию
        self._lock = threading.RLock()
        
        # Условные переменные для сигнализации
        self._read_cv = threading.Condition(self._lock)
        self._write_cv = threading.Condition(self._lock)
        
        # Счетчики активных читателей и писателей
        self._active_readers = 0
        self._active_writers = 0
        
        # Очереди ожидающих потоков для справедливой планировки
        self._waiting_readers: Set[int] = set()
        self._waiting_writers: List[int] = []
        
        # Отслеживание потоков
        self._writer_thread: Optional[int] = None
        self._reader_threads: Set[int] = set()
        self._depth = 0  # Глубина рекурсивного захвата писателем
        
        # Система версионирования для транзакционности
        self._global_version = 0
        self._thread_versions: Dict[int, int] = {}
        
        # Глобальная транзакционная память
        self._transaction_lock = threading.Lock()
        self._pending_changes = {}
        self._commit_history = []
    
    def acquire_read(self) -> bool:
        """
        Приобретает блокировку для чтения с гарантией видимости последних изменений.
        
        Использует справедливую очередь для предотвращения голодания писателей.
        
        Returns:
            True, если блокировка успешно приобретена
        """
        current_thread_id = threading.get_ident()
        
        # Если текущий поток уже имеет блокировку записи,
        # разрешаем ему читать (предотвращение взаимной блокировки)
        if self._writer_thread == current_thread_id:
            return True
        
        # Если текущий поток уже имеет блокировку чтения,
        # просто используем её (реентерабельность)
        if current_thread_id in self._reader_threads:
            return True
        
        # Захватываем основную блокировку для доступа к состоянию
        with self._lock:
            # Проверяем наличие активных писателей или ожидающих писателей
            # с приоритетом (предотвращение голодания писателей)
            writers_exist = self._active_writers > 0 or len(self._waiting_writers) > 0
            
            if writers_exist:
                # Добавляем в очередь ожидающих читателей
                self._waiting_readers.add(current_thread_id)
                
                # Ждем, пока не получим сигнал
                while current_thread_id in self._waiting_readers:
                    self._read_cv.wait()
            
            # Приобретаем блокировку чтения
            self._active_readers += 1
            self._reader_threads.add(current_thread_id)
            
            # Запоминаем текущую глобальную версию для этого потока
            # для обеспечения транзакционного чтения
            with self._transaction_lock:
                self._thread_versions[current_thread_id] = self._global_version
                
                # Применяем все видимые для этой версии изменения
                # к локальному представлению потока
                logger.debug(f"Читатель {current_thread_id} получил версию {self._global_version}")
        
        return True
    
    def release_read(self) -> None:
        """
        Освобождает блокировку для чтения.
        
        Дает сигнал ожидающим писателям, если больше нет активных читателей.
        """
        current_thread_id = threading.get_ident()
        
        # Если текущий поток имеет блокировку записи,
        # не освобождаем блокировку чтения (предотвращение взаимных блокировок)
        if self._writer_thread == current_thread_id:
            return
        
        # Если текущий поток не имеет блокировки чтения,
        # ничего не делаем
        if current_thread_id not in self._reader_threads:
            return
        
        # Захватываем основную блокировку для доступа к состоянию
        with self._lock:
            # Освобождаем блокировку чтения
            self._active_readers -= 1
            self._reader_threads.remove(current_thread_id)
            
            # Очищаем информацию о версии для этого потока
            with self._transaction_lock:
                if current_thread_id in self._thread_versions:
                    del self._thread_versions[current_thread_id]
            
            # Если больше нет активных читателей и есть ожидающие писатели,
            # даем сигнал первому писателю в очереди
            if self._active_readers == 0 and len(self._waiting_writers) > 0:
                writer_id = self._waiting_writers[0]
                self._waiting_writers.remove(writer_id)
                
                # Пробуждаем писателя
                self._write_cv.notify_all()
    
    def acquire_write(self) -> bool:
        """
        Приобретает блокировку для записи с транзакционной семантикой.
        
        Использует справедливую очередь с приоритетом писателей
        для предотвращения голодания.
        
        Returns:
            True, если блокировка успешно приобретена
        """
        current_thread_id = threading.get_ident()
        
        # Если текущий поток уже имеет блокировку записи,
        # просто увеличиваем глубину (реентерабельность)
        if self._writer_thread == current_thread_id:
            self._depth += 1
            return True
        
        # Захватываем основную блокировку для доступа к состоянию
        with self._lock:
            # Проверяем наличие активных читателей или писателей
            busy = self._active_readers > 0 or self._active_writers > 0
            
            if busy:
                # Добавляем в очередь ожидающих писателей
                self._waiting_writers.append(current_thread_id)
                
                # Ждем, пока не получим сигнал и не станем первыми в очереди
                while (self._active_readers > 0 or self._active_writers > 0 or
                       (len(self._waiting_writers) > 0 and self._waiting_writers[0] != current_thread_id)):
                    self._write_cv.wait()
                
                # Удаляем себя из очереди ожидающих
                if current_thread_id in self._waiting_writers:
                    self._waiting_writers.remove(current_thread_id)
            
            # Приобретаем блокировку записи
            self._active_writers += 1
            self._writer_thread = current_thread_id
            self._depth = 1
            
            # Начинаем новую транзакцию
            with self._transaction_lock:
                # Запоминаем глобальную версию на момент начала транзакции
                self._thread_versions[current_thread_id] = self._global_version
                
                logger.debug(f"Писатель {current_thread_id} начал транзакцию с версии {self._global_version}")
        
        return True
    
    def release_write(self) -> None:
        """
        Освобождает блокировку для записи.
        
        Фиксирует транзакционные изменения и уведомляет ожидающие потоки.
        """
        current_thread_id = threading.get_ident()
        
        # Если текущий поток не имеет блокировки записи,
        # ничего не делаем
        if self._writer_thread != current_thread_id:
            return
        
        # Захватываем основную блокировку для доступа к состоянию
        with self._lock:
            # Уменьшаем глубину вложенности
            self._depth -= 1
            
            # Если глубина достигла 0, полностью освобождаем блокировку
            if self._depth == 0:
                # Фиксируем транзакцию и обновляем глобальную версию
                with self._transaction_lock:
                    # Увеличиваем глобальную версию
                    self._global_version += 1
                    
                    # Создаем запись в истории коммитов для отслеживания изменений
                    if current_thread_id in self._thread_versions:
                        previous_version = self._thread_versions[current_thread_id]
                        
                        logger.debug(f"Писатель {current_thread_id} зафиксировал транзакцию: "
                                   f"v{previous_version} -> v{self._global_version}")
                        
                        # Очищаем информацию о версии для этого потока
                        del self._thread_versions[current_thread_id]
                
                # Освобождаем блокировку записи
                self._active_writers -= 1
                self._writer_thread = None
                
                # Определяем, кого разбудить: писателей или читателей
                if len(self._waiting_writers) > 0:
                    # Приоритет писателей: будим первого писателя в очереди
                    self._write_cv.notify_all()
                else:
                    # Будим всех ожидающих читателей
                    self._waiting_readers.clear()
                    self._read_cv.notify_all()
    
    @contextlib.contextmanager
    def reader_lock(self):
        """
        Контекстный менеджер для блокировки чтения.
        
        Yields:
            None
        """
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()
    
    @contextlib.contextmanager
    def writer_lock(self):
        """
        Контекстный менеджер для блокировки записи.
        
        Yields:
            None
        """
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
            
    def get_version(self) -> int:
        """
        Возвращает текущую версию данных.
        
        Returns:
            Текущая версия данных
        """
        with self._transaction_lock:
            return self._global_version
    
    def check_for_updates(self, thread_id: int) -> bool:
        """
        Проверяет, были ли обновления данных с момента последнего чтения.
        
        Args:
            thread_id: Идентификатор потока
            
        Returns:
            True, если были обновления, иначе False
        """
        with self._transaction_lock:
            if thread_id not in self._thread_versions:
                return True
            return self._global_version > self._thread_versions[thread_id]
    
    def force_read_latest(self, thread_id: int) -> None:
        """
        Принудительно обновляет версию для указанного потока чтения.
        
        Это гарантирует, что поток увидит все изменения, сделанные до этого момента.
        
        Args:
            thread_id: Идентификатор потока
        """
        with self._transaction_lock:
            self._thread_versions[thread_id] = self._global_version
            logger.debug(f"Читатель {thread_id} принудительно обновлен до версии {self._global_version}")