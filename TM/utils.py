"""
                                 === Функции проверки подтверждения ===

                                    === Версия приложения: 0.1.0 ===
"""
import sys
import os
from tkinter.messagebox import RETRY

### Проверка подтверждения
def check_confirm(select_task, task_list):
    if select_task.isdigit():
        if 0 < int(select_task) <= len(task_list):
            return True
        else:
            print(f"Задачи с номером {select_task} нет в списке!")
            return False
    else:
        print("Введите именно номер задачи!")
        return False

def get_base_din():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.realpath(__file__))

def insure_saves_file(name_file):
    if not os.path.exists(name_file):
        with open(name_file, 'w') as f:
            f.write("")
