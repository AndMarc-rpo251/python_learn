"""Небольшие вспомогательные функции без привязки к окну и файлам."""
from __future__ import annotations

from datetime import datetime

from config import STATUSES, PRIORITIES


def now_iso() -> str:
    """Текущее время в формате ISO (до секунд) - удобно хранить в JSON."""
    return datetime.now().isoformat(timespec="seconds")


def pretty_dt(iso: str) -> str:
    """'2026-11-04T15:00:00' -> '2026-11-04 15:00:00' (для показа в таблице)."""
    return iso.replace("T", " ")


# По каким значениям сортировать каждый столбец таблицы
SORT_KEYS = {
    "id": lambda t: t.id,
    "title": lambda t: t.title.casefold(),          # casefold - без учёта регистра
    "status": lambda t: STATUSES.index(t.status),   # порядок как в STATUSES, а не по алфавиту
    "priority": lambda t: PRIORITIES.index(t.priority),
    "updated": lambda t: t.updated_at,
}


def sort_tasks(tasks: list, column: str, descending: bool = False) -> list:
    """Вернуть задачи, отсортированные по столбцу. Исходный список не меняется."""
    return sorted(tasks, key=SORT_KEYS[column], reverse=descending)
