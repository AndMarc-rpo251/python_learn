"""Окно программы на tkinter: диалог задачи (TaskDialog) и главное окно (App).

Здесь только отображение. Вся логика - в core.py, хранение - в storage_file.py.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    __version__, STATUSES, PRIORITIES, STATUS_LABEL, PRIORITY_LABEL,
    LABEL_TO_STATUS, LABEL_TO_PRIORITY, ALL_FILTER, COLUMNS, WINDOW_SIZE,
    WINDOW_MIN_SIZE, SEARCH_DELAY_MS, COLOR_DONE, COLOR_HIGH,
)
from core import Task, TaskManager
from utils import pretty_dt, sort_tasks


class TaskDialog(tk.Toplevel):
    """Модальное окно для добавления и редактирования задачи.

    После закрытия поле `result` содержит словарь с данными
    или None, если пользователь нажал «Отмена».
    """

    def __init__(self, parent, title: str, task: Task | None = None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)   # окно всегда поверх родителя
        self.result: dict | None = None

        frame = ttk.Frame(self, padding=12)
        frame.grid(sticky="nsew")

        # --- Название ---
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w", pady=4)
        self.title_var = tk.StringVar(value=task.title if task else "")
        self.title_entry = ttk.Entry(frame, textvariable=self.title_var, width=45)
        self.title_entry.grid(row=0, column=1, pady=4)

        # --- Описание (многострочное поле) ---
        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky="nw", pady=4)
        self.desc_text = tk.Text(frame, width=45, height=6, wrap="word")
        self.desc_text.grid(row=1, column=1, pady=4)
        if task:
            self.desc_text.insert("1.0", task.description)

        # --- Статус и приоритет: два одинаковых выпадающих списка ---
        self.status_var = self._combo(
            frame, 2, "Статус:", STATUSES, STATUS_LABEL, task.status if task else "todo")
        self.priority_var = self._combo(
            frame, 3, "Приоритет:", PRIORITIES, PRIORITY_LABEL, task.priority if task else "medium")

        # --- Кнопки ---
        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(buttons, text="Сохранить", command=self._on_ok).pack(side="left", padx=4)
        ttk.Button(buttons, text="Отмена", command=self.destroy).pack(side="left")

        # Escape закрывает окно; Ctrl+Enter сохраняет (обычный Enter нужен в описании)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-Return>", lambda e: self._on_ok())

        self.title_entry.focus_set()
        self.grab_set()  # блокируем главное окно, пока открыт диалог

    @staticmethod
    def _combo(frame, row: int, caption: str, values: tuple, labels: dict, current: str) -> tk.StringVar:
        """Создать подпись + выпадающий список; вернуть переменную с выбранной подписью."""
        ttk.Label(frame, text=caption).grid(row=row, column=0, sticky="w", pady=4)
        var = tk.StringVar(value=labels[current])
        ttk.Combobox(frame, textvariable=var, state="readonly", width=42,
                     values=[labels[v] for v in values]).grid(row=row, column=1, sticky="w", pady=4)
        return var

    def _on_ok(self) -> None:
        """Проверить ввод и сохранить результат."""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Ошибка", "Название не может быть пустым", parent=self)
            self.title_entry.focus_set()
            return
        self.result = {
            "title": title,
            # "end-1c" - весь текст без автоматического перевода строки в конце
            "description": self.desc_text.get("1.0", "end-1c"),
            "status": LABEL_TO_STATUS[self.status_var.get()],
            "priority": LABEL_TO_PRIORITY[self.priority_var.get()],
        }
        self.destroy()


class App(tk.Tk):
    """Главное окно приложения."""

    def __init__(self, manager: TaskManager):
        super().__init__()
        self.title(f"Task Manager {__version__}")
        try:
            if ICON_FILE.exists():
                self.iconbitmap(str(ICON_FILE))
        except tk.TclError:
            pass
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)
        self.manager = manager

        # Текущая сортировка: по какому столбцу и в какую сторону
        self.sort_col = "id"
        self.sort_desc = False
        self._search_job = None   # отложенное обновление после ввода в поиск

        # Переменные, связанные с полями ввода
        self.filter_var = tk.StringVar(value=ALL_FILTER)
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self._build_toolbar()
        self._build_filters()
        self._build_table()
        self._build_details()
        ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(8, 2)
                  ).pack(fill="x", side="bottom")

        # Ввод в поиск: обновляем таблицу не на каждую букву, а когда пользователь
        # на мгновение замолчал (так окно не «дёргается» при быстром наборе)
        self.search_var.trace_add("write", lambda *_: self._schedule_refresh())

        # Горячие клавиши (Delete и Enter привязаны к таблице в _build_table,
        # чтобы не срабатывать, когда пользователь печатает в поле поиска)
        self.bind("<Control-n>", lambda e: self.add_task())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<F5>", lambda e: self.reload())

        self.refresh()

    # ---------- построение интерфейса ----------
    def _build_toolbar(self) -> None:
        """Верхняя панель с кнопками действий."""
        bar = ttk.Frame(self, padding=(8, 8, 8, 0))
        bar.pack(fill="x")
        for text, command in (("Добавить", self.add_task), ("Редактировать", self.edit_task),
                              ("Готово ✓", self.toggle_done), ("Удалить", self.delete_task)):
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=(0, 6))

    def _build_filters(self) -> None:
        """Строка поиска и фильтра по статусу."""
        bar = ttk.Frame(self, padding=(8, 8, 8, 0))
        bar.pack(fill="x")
        ttk.Label(bar, text="Поиск:").pack(side="left")
        self.search_entry = ttk.Entry(bar, textvariable=self.search_var, width=30)
        self.search_entry.pack(side="left", padx=(4, 16))

        ttk.Label(bar, text="Показывать:").pack(side="left")
        flt = ttk.Combobox(bar, textvariable=self.filter_var, state="readonly", width=16,
                           values=[ALL_FILTER] + [STATUS_LABEL[s] for s in STATUSES])
        flt.pack(side="left", padx=4)
        flt.bind("<<ComboboxSelected>>", lambda e: self.refresh())

    def _build_table(self) -> None:
        """Таблица задач со скроллбаром."""
        wrap = ttk.Frame(self, padding=8)
        wrap.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(wrap, columns=list(COLUMNS), show="headings", selectmode="browse")
        for col, (_, width) in COLUMNS.items():
            self.tree.column(col, width=width, anchor="w" if col == "title" else "center")
        self._update_headings()

        scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Цвета строк: выполненные - серым, высокий приоритет - красным
        self.tree.tag_configure("done", foreground=COLOR_DONE)
        self.tree.tag_configure("high", foreground=COLOR_HIGH)

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._show_details())
        self.tree.bind("<Double-1>", lambda e: self.edit_task())
        self.tree.bind("<Return>", lambda e: self.edit_task())
        self.tree.bind("<Delete>", lambda e: self.delete_task())

    def _build_details(self) -> None:
        """Нижняя панель с описанием выбранной задачи."""
        box = ttk.LabelFrame(self, text="Описание выбранной задачи", padding=6)
        box.pack(fill="x", padx=8, pady=(0, 4))
        # Текст только для чтения (state=disabled), меняем его через _show_details
        self.details = tk.Text(box, height=4, wrap="word", state="disabled")
        self.details.pack(fill="x")

    def _update_headings(self) -> None:
        """Перерисовать заголовки столбцов; у столбца сортировки - стрелка ▲/▼."""
        for col, (text, _) in COLUMNS.items():
            arrow = (" ▼" if self.sort_desc else " ▲") if col == self.sort_col else ""
            self.tree.heading(col, text=text + arrow, command=lambda c=col: self.sort_by(c))

    # ---------- обновление данных на экране ----------
    def _schedule_refresh(self) -> None:
        """Отложить обновление таблицы; повторный вызов отменяет предыдущий."""
        if self._search_job is not None:
            self.after_cancel(self._search_job)
        self._search_job = self.after(SEARCH_DELAY_MS, self.refresh)

    def refresh(self, select_id: int | None = None) -> None:
        """Перерисовать таблицу с учётом поиска, фильтра и сортировки.

        select_id - какую задачу выделить после обновления;
        если не указан, сохраняем текущее выделение.
        """
        self._search_job = None
        if select_id is None:
            current = self._selected_task()
            select_id = current.id if current else None

        self.tree.delete(*self.tree.get_children())  # один вызов вместо цикла

        status = LABEL_TO_STATUS.get(self.filter_var.get())  # для «Все» будет None
        tasks = sort_tasks(self.manager.list(status, self.search_var.get()),
                           self.sort_col, self.sort_desc)
        for t in tasks:
            # Тег определяет цвет строки
            tag = "done" if t.status == "done" else ("high" if t.priority == "high" else "")
            self.tree.insert("", "end", iid=str(t.id), tags=(tag,), values=(
                t.id, t.title, STATUS_LABEL[t.status], PRIORITY_LABEL[t.priority],
                pretty_dt(t.updated_at)))

        if select_id is not None and self.tree.exists(str(select_id)):
            self.tree.selection_set(str(select_id))
            self.tree.see(str(select_id))

        total, done = self.manager.stats()
        self.status_var.set(f"Показано: {len(tasks)} из {total} | выполнено: {done} | "
                            f"F5 - обновить | v{__version__}")
        self._show_details()

    def _show_details(self) -> None:
        """Показать описание выбранной задачи в нижней панели."""
        task = self._selected_task()
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        if task:
            self.details.insert("1.0", task.description or "(без описания)")
        self.details.configure(state="disabled")

    def _selected_task(self) -> Task | None:
        """Задача, выбранная в таблице, либо None."""
        sel = self.tree.selection()
        return self.manager.get(int(sel[0])) if sel else None

    def _need_selection(self) -> None:
        messagebox.showinfo("Задача не выбрана", "Сначала выберите задачу в таблице", parent=self)

    # ---------- действия ----------
    def sort_by(self, col: str) -> None:
        """Клик по заголовку: сортировать по столбцу (повторный клик - в обратную сторону)."""
        if col == self.sort_col:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_col, self.sort_desc = col, False
        self._update_headings()
        self.refresh()

    def reload(self) -> None:
        """F5: перечитать файл (если данные изменила другая копия программы)."""
        self.manager.reload()
        self.refresh()

    def add_task(self) -> None:
        dlg = TaskDialog(self, "Новая задача")
        self.wait_window(dlg)  # ждём закрытия диалога
        if dlg.result is None:
            return
        try:
            task = self.manager.add(**dlg.result)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e), parent=self)
            return
        self.refresh(select_id=task.id)
        self.tree.focus_set()

    def edit_task(self) -> None:
        task = self._selected_task()
        if task is None:
            self._need_selection()
            return
        dlg = TaskDialog(self, f"Задача #{task.id}", task)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self._apply_edit(task.id, **dlg.result)

    def toggle_done(self) -> None:
        """Кнопка «Готово»: отметить выполненной (если уже выполнена - вернуть в «К выполнению»)."""
        task = self._selected_task()
        if task is None:
            self._need_selection()
            return
        self._apply_edit(task.id, status="todo" if task.status == "done" else "done")

    def _apply_edit(self, task_id: int, **fields) -> None:
        """Применить изменения к задаче и обновить экран."""
        try:
            updated = self.manager.edit(task_id, **fields)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e), parent=self)
            return
        if updated is None:
            messagebox.showinfo("Задача не найдена",
                                "Эта задача уже удалена (возможно, в другом окне).", parent=self)
            self.refresh()
            return
        self.refresh(select_id=task_id)
        self.tree.focus_set()

    def delete_task(self) -> None:
        task = self._selected_task()
        if task is None:
            return
        # Подтверждение, чтобы не удалить случайно
        if messagebox.askyesno("Удаление", f"Удалить задачу «{task.title}»?", parent=self):
            self.manager.delete(task.id)
            self.refresh()
            self.tree.focus_set()
