"""Ядро: модель задачи и логика (добавить / изменить / удалить / найти).

Модуль ничего не знает ни об окне, ни о файлах: хранилище передаётся снаружи
(см. storage_file.JsonStorage), поэтому логику легко тестировать.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field

from config import STATUSES, PRIORITIES
from utils import now_iso


# slots=True - объекты занимают меньше памяти и быстрее обращаются к полям
@dataclass(slots=True)
class Task:
    """Одна задача. dataclass сам создаёт __init__, __repr__ и сравнение."""
    id: int
    title: str
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        """Задача -> словарь для записи в JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Словарь из JSON -> задача.

        Лишние ключи игнорируем, а отсутствующие заполняются значениями
        по умолчанию - так старые файлы не ломаются при добавлении новых полей.
        """
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)


def validate(title: str | None = None, status: str | None = None,
             priority: str | None = None) -> None:
    """Проверить значения полей; при ошибке бросает ValueError.

    None означает «поле не передано» - его не проверяем.
    """
    if title is not None and not title.strip():
        raise ValueError("Название задачи не может быть пустым")
    if status is not None and status not in STATUSES:
        raise ValueError(f"Статус должен быть одним из: {STATUSES}")
    if priority is not None and priority not in PRIORITIES:
        raise ValueError(f"Приоритет должен быть одним из: {PRIORITIES}")


class TaskManager:
    """Добавление, удаление, редактирование и поиск. Каждое изменение сразу сохраняется."""

    def __init__(self, storage):
        """storage - любой объект с методами load() -> list[Task] и save(list[Task])."""
        self.storage = storage
        self.tasks: list[Task] = []
        self._by_id: dict[int, Task] = {}   # индекс для мгновенного поиска по id
        self.reload()

    # ---------- вспомогательные методы ----------
    def reload(self) -> None:
        """Перечитать задачи с диска и перестроить индекс.

        Вызывается перед каждым изменением: если программа открыта в двух окнах,
        изменения одного окна не затирают изменения другого.
        """
        self.tasks = self.storage.load()
        self._by_id = {t.id: t for t in self.tasks}

    def _next_id(self) -> int:
        """Следующий свободный id (максимальный + 1, чтобы id не повторялись)."""
        return max(self._by_id, default=0) + 1

    def _save(self) -> None:
        self.storage.save(self.tasks)

    def get(self, task_id: int) -> Task | None:
        """Найти задачу по id, либо None."""
        return self._by_id.get(task_id)

    # ---------- основные операции ----------
    def add(self, title: str, description: str = "", priority: str = "medium",
            status: str = "todo") -> Task:
        """Добавить новую задачу."""
        validate(title=title, status=status, priority=priority)
        self.reload()  # берём свежие данные, чтобы id не пересеклись
        task = Task(id=self._next_id(), title=title.strip(), description=description.strip(),
                    priority=priority, status=status)
        self.tasks.append(task)
        self._by_id[task.id] = task
        self._save()
        return task

    def delete(self, task_id: int) -> bool:
        """Удалить задачу. True - удалена, False - такой задачи нет."""
        self.reload()
        task = self._by_id.pop(task_id, None)
        if task is None:
            return False
        self.tasks.remove(task)
        self._save()
        return True

    def edit(self, task_id: int, title: str | None = None, description: str | None = None,
             status: str | None = None, priority: str | None = None) -> Task | None:
        """Изменить поля задачи. None = «поле не менять». Нет такой задачи -> None."""
        # Сначала проверяем всё, потом применяем - чтобы не получить
        # наполовину изменённую задачу при ошибке
        validate(title=title, status=status, priority=priority)
        self.reload()
        task = self.get(task_id)
        if task is None:
            return None
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        task.updated_at = now_iso()
        self._save()
        return task

    def list(self, status: str | None = None, query: str = "") -> list[Task]:
        """Список задач. status - фильтр по статусу, query - поиск по названию и описанию."""
        query = query.strip().casefold()
        return [
            t for t in self.tasks
            if (status is None or t.status == status)
            and (not query or query in t.title.casefold() or query in t.description.casefold())
        ]

    def stats(self) -> tuple[int, int]:
        """(всего задач, выполнено)."""
        return len(self.tasks), sum(1 for t in self.tasks if t.status == "done")
