"""
Модули для работы с задачами и гипотезами в соответствии со стандартами.

Включает реализации для управления задачами, отслеживания их статусов
и работы с гипотезами согласно актуальным стандартам.
"""

from advising_platform.standards.task.todo_manager import (
    todo_storage,
    create_todo,
    update_todo_status,
    get_todos_by_status,
    get_todos_by_priority
)

from advising_platform.standards.task.hypothesis import (
    Hypothesis,
    hypothesis_storage,
    create_hypothesis,
    verify_hypothesis,
    add_incident_to_hypothesis
)

__all__ = [
    'todo_storage',
    'create_todo',
    'update_todo_status',
    'get_todos_by_status',
    'get_todos_by_priority',
    'Hypothesis',
    'hypothesis_storage',
    'create_hypothesis',
    'verify_hypothesis',
    'add_incident_to_hypothesis'
]