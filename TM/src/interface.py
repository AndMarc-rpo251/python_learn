"""Task Manager - точка входа и сборка проекта.

Запуск (из папки TM):

    python src/interface.py

Проект разбит на модули (все лежат рядом, в папке src):
    config.py       - версия, пути, подписи, параметры окна
    utils.py        - мелкие помощники (время, сортировка)
    core.py         - модель Task и логика TaskManager
    storage_file.py - чтение/запись JSON (папка JSON)
    view.py         - окно tkinter
    interface.py    - этот файл: собирает всё вместе и запускает окно
"""
import sys

try:
    import tkinter  # noqa: F401  (только проверяем, что tkinter установлен)
except ImportError as err:
    # На Linux tkinter ставится отдельно от Python
    print(f"Не удалось загрузить tkinter: {err}")
    print("Linux: sudo apt install python3-tk")
    sys.exit(1)

from core import TaskManager
from storage_file import JsonStorage
from view import App


def main() -> None:
    """Собрать части проекта и запустить окно."""
    storage = JsonStorage()         # где хранить: JSON/tasks.json
    manager = TaskManager(storage)  # что делать с задачами
    App(manager).mainloop()         # как показывать


if __name__ == "__main__":
    main()
