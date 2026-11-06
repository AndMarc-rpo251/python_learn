"""Настройки проекта: версия, пути, справочники и параметры окна.

Здесь нет логики - только константы. Чтобы поменять подпись, цвет или размер окна,
достаточно изменить этот файл.
"""
import os
import sys
from pathlib import Path

__version__ = "1.0.1"

# ---------- пути ----------
if getattr(sys, "frozen", False):
    # Программа собрана PyInstaller-ом в .exe: папку JSON держим рядом с .exe
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Обычный запуск: config.py лежит в TM/src, значит корень проекта - на уровень выше
    BASE_DIR = Path(__file__).resolve().parents[1]

# Файл с данными. Путь можно переопределить переменной окружения TM_DATA_FILE
DATA_FILE = Path(os.environ.get("TM_DATA_FILE", BASE_DIR / "JSON" / "tasks.json"))

# ---------- справочники ----------
# Допустимые значения - единый источник правды для всего приложения
STATUSES = ("todo", "in_progress", "done")
PRIORITIES = ("low", "medium", "high")

# Подписи для пользователя (внутри JSON лежат английские значения)
STATUS_LABEL = {"todo": "К выполнению", "in_progress": "В работе", "done": "Готово"}
PRIORITY_LABEL = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}
# Обратные словари: из подписи в выпадающем списке получаем значение для JSON
LABEL_TO_STATUS = {v: k for k, v in STATUS_LABEL.items()}
LABEL_TO_PRIORITY = {v: k for k, v in PRIORITY_LABEL.items()}

ALL_FILTER = "Все"  # пункт фильтра «показывать всё»

# ---------- параметры окна ----------
WINDOW_SIZE = "900x580"
WINDOW_MIN_SIZE = (700, 440)
SEARCH_DELAY_MS = 200       # пауза после ввода в поиск, прежде чем обновить таблицу
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))
ICON_FILE = RESOURCE_DIR / "icon.ico"

# Столбцы таблицы: ключ -> (заголовок, ширина)
COLUMNS = {
    "id": ("ID", 50),
    "title": ("Название", 330),
    "status": ("Статус", 120),
    "priority": ("Приоритет", 100),
    "updated": ("Изменена", 150),
}

# Цвета строк таблицы
COLOR_DONE = "gray"
COLOR_HIGH = "#b00020"
