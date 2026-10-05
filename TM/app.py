"""
                                     === Основной файл приложения ===

                                     === Версия приложения: 0.1.0 ===
"""


from storage_file import load_tasks, save_tasks
from view import show_menu, show_collection
from core import add_task, edit_task, delete_tasks
from config import NAME_FILE_SAVES
from utils import insure_saves_file

collection = []


def app():
    name_file = NAME_FILE_SAVES
    insure_saves_file(name_file)
    collection.extend(load_tasks(name_file))

    is_running = True

    while is_running:
        show_menu()
        choice_user = input("Введите ваш выбор: ")

        match choice_user:

            case "1":
                show_collection(collection)

            case "2":
                add_task(collection)
                save_tasks(collection, name_file)

            case "3":
                show_collection(collection)
                edit_task(collection)
                save_tasks(collection, name_file)

            case "4":
                show_collection(collection)
                delete_tasks(collection)
                save_tasks(collection, name_file)

            case "5":
                save_tasks(collection, name_file)
                is_running = False
                print("До побачиня!")

            case _:
                print("Такого пункта нет...")