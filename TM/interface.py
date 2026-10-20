import tkinter as tk
def press(value):
    if value == "=":
        try:
            result = eval(expression.get())
            expression.set(str(result))
        except:
            expression.set("Ошибка")
            window.after(1500, reset)

    elif value == "C":
        expression.set("")
    else:
        expression.set(expression.get() + value)


def reset():
    expression.set("")


window = tk.Tk()
window.title("Калькулятор")
window.geometry("300x400")
window.resizable(False, False)

expression = tk.StringVar()

display = tk.Entry(
    window,
    textvariable=expression,
    font=("Arial", 24),
    justify="right",
    state="readonly"
)
display.pack(fill="both", padx=10, pady=10, ipady=10)

buttons = [
    ("1", 1, 0), ("2", 1, 1), ("3", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("7", 3, 0), ("8", 3, 1), ("9", 3, 2), ("-", 3, 3),
    ("C", 4, 0), ("0", 4, 1), ("=", 4, 2), ("+", 4, 3),
]

frame = tk.Frame(window)
frame.pack(expand=True, fill="both", padx=10, pady=10)

for text, row, column in buttons:
    button = tk.Button(frame, text=text, font=("Arial", 20), command=lambda value=text: press(value))
    button.grid(
        row=row,
        column=column,
        sticky="nsew",
        padx=3,
        pady=3
    )

for i in range(4):
    frame.columnconfigure(i, weight=1)

for i in range(1, 5):
    frame.rowconfigure(i, weight=1)

window.mainloop()
