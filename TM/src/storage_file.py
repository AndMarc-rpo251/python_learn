"""Хранилище: чтение и запись задач в JSON-файл (папка JSON)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from config import DATA_FILE
from core import Task


class JsonStorage:
    """Сохраняет и загружает список задач из JSON-файла."""

    def __init__(self, path: Path = DATA_FILE):
        self.path = Path(path)
        # Создаём папку JSON, если её ещё нет
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[Task]:
        """Прочитать задачи. Нет файла -> пустой список."""
        if not self.path.exists():
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [Task.from_dict(item) for item in raw]
        except (json.JSONDecodeError, TypeError, ValueError):
            # Файл повреждён: сохраняем копию, чтобы не потерять данные,
            # и начинаем с чистого списка
            backup = self.path.with_suffix(".broken.json")
            os.replace(self.path, backup)
            print(f"[!] Файл данных повреждён, копия сохранена: {backup.name}")
            return []

    def save(self, tasks: list[Task]) -> None:
        """Записать задачи в файл.

        Пишем сначала во временный файл, затем заменяем основной:
        так при сбое посреди записи старые данные не теряются.
        """
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            # ensure_ascii=False - чтобы русский текст был читаемым в файле
            json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
