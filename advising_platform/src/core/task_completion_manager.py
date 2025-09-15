"""
Менеджер завершения задач с интеграцией report_progress.

Цель: Обеспечить единую точку управления завершением задач
с поддержкой TDD принципов и RealInMemoryCache.
"""

def report_progress(summary: str):
    """
    Функция для отчета о прогрессе задач.
    
    Args:
        summary: Краткое описание прогресса
    """
    print(f"📊 Progress: {summary}")
    return True

class TaskCompletionManager:
    """Менеджер завершения задач."""
    
    def __init__(self):
        """Инициализация менеджера."""
        self.completed_tasks = []
    
    def complete_task(self, task_id: str, summary: str = ""):
        """
        Завершает задачу и сообщает о прогрессе.
        
        Args:
            task_id: ID задачи
            summary: Описание завершения
        """
        self.completed_tasks.append(task_id)
        if summary:
            report_progress(summary)
        return True
    
    def get_completed_tasks(self):
        """Возвращает список завершенных задач."""
        return self.completed_tasks