"""
                    === Функции для добавления, удаления и редактирования задач ===

                                    === Версия приложения: 0.1.0 ===
"""

from utils import check_confirm

### Удаление задач
def delete_tasks(task_collection):
    delete_task = input("Введите номер задачи: ")

    if check_confirm(delete_task, task_collection):
        task_collection.pop(int(delete_task) - 1)
        print(f"Задача {delete_task} удалена!")
    else:
        print("Неверный номер задачи!")

### Редактирование задач
def edit_task(task_collection):
    edit_task_number = input("Введите номер задачи: ")

    if check_confirm(edit_task_number, task_collection):
        edit_name = input("Новое имя задачи: ").strip()
        edit_content = input("Новое содержимое задачи: ").strip()

        if not edit_name:
            print("Название задачи не может быть пустым!")
            return

        if not edit_content:
            print("Содержимое задачи не может быть пустым!")
            return

        task_collection[int(edit_task_number) - 1] = (
            f"{edit_name} | {edit_content}\n"
        )

        print(f"Задача «{edit_name}» успешно изменена!")

### Добавление задач
def add_task(task_collection):
    task_name = input("Введите имя задачи: ").strip()
    task_content = input("Введите содержимое задачи: ").strip()

    if not task_name:
        print("Имя задачи не может быть пустым!")
        return

    if not task_content:
        print("Содержимое задачи не может быть пустым!")
        return

    full_task = f"{task_name} | {task_content}"
    task_collection.append(full_task + "\n")
    print(f"Задача «{task_name}» успешно добавлена!")