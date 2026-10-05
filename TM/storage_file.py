"""
                                === Функции для сохранения и загрузки ===

                                    === Версия приложения: 0.1.0 ===
"""

### Сохранение задач
def save_tasks(task_collection, name_file):
    with open(name_file, "w", encoding="utf-8") as file:
        file.writelines(task_collection)

### Загрузка задач
def load_tasks(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        return []