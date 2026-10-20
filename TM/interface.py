
import tkinter as tk
import math

window = tk.Tk()
window.title("Калькулятор")
window.geometry("400x450")
window.resizable(False, False)

entry = tk.Entry(window, justify="right", font=("Arial", 18))
entry.pack(fill="x", padx=20, pady=10)

def add(value):
    entry.insert(tk.END, value)

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, result)
    except:
        entry.delete(0, tk.END)
        entry.insert(0, "Ошибка")

buttons = [
    "7", "8", "9", "/",
    "4", "5", "6", "*",
    "1", "2", "3", "-",
    "0", ".", "=", "+",
    "C"
]

actions = {
    "7": lambda: add("7"),
    "8": lambda: add("8"),
    "9": lambda: add("9"),
    "/": lambda: add("/"),
    "4": lambda: add("4"),
    "5": lambda: add("5"),
    "6": lambda: add("6"),
    "*": lambda: add("*"),
    "1": lambda: add("1"),
    "2": lambda: add("2"),
    "3": lambda: add("3"),
    "-": lambda: add("-"),
    "0": lambda: add("0"),
    ".": lambda: add("."),
    "=": calculate,
    "+": lambda: add("+"),
    "C": clear
}

canvas = tk.Frame(window, width=360, height=350)
canvas.pack()
canvas.pack_propagate(False)

radius = 125
center_x = 180
center_y = 175
button_size = 40

i = 0
total = len(buttons)

while i < total:
    angle = 2 * math.pi * i / total - math.pi / 2

    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)

    button = tk.Button(
        canvas,
        text=buttons[i],
        width=3,
        height=1,
        font=("Arial", 12),
        command=actions[buttons[i]]
    )

    button.place(
        x=x,
        y=y,
        anchor="center"
    )

    i += 1

window.mainloop()
