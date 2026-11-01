"""Графический интерфейс эмулятора на tkinter."""
import tkinter as tk
from tkinter import scrolledtext

PROMPT = "$ "
FONT = ("Courier", 12)
TITLE_TEMPLATE = "Эмулятор - [{}]"
OUTPUT_ROWS = 24
OUTPUT_COLS = 90
BG_COLOR = "#1e1e1e"
OUTPUT_COLOR = "#7ec699"
INPUT_COLOR = "#c792ea"

class App:
    """Окно: область вывода сверху, строка ввода снизу."""

    def __init__(self, shell):
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(TITLE_TEMPLATE.format(shell.vfs.name))
        self.output = scrolledtext.ScrolledText(
            self.root, state = "disabled", font = FONT,
            height = OUTPUT_ROWS, width = OUTPUT_COLS,
            bg=BG_COLOR, fg=OUTPUT_COLOR
        )
        self.output.pack(fill = "both",expand=True)
        self.entry = tk.Entry(self.root, font = FONT,bg=BG_COLOR,
            fg=INPUT_COLOR, insertbackground=INPUT_COLOR
        )
        self.entry.pack(fill = "x")
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

    def write(self, text):
        """Добавить текст (и перевод строки) в область вывода."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.configure(state="disabled")
        self.output.see(tk.END)

    def on_enter(self, event):
        """Обработать нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_line(line)

    def run_line(self, line):
        """Показать введённую строку и результат её выполнения."""
        self.write(PROMPT + line)
        result = self.shell.execute(line)
        if result:
            self.write(result)
        if not self.shell.running:
            self.root.destroy()

    def run(self):
        """Запустить цикл окна, если exit ещё не был вызван."""
        if self.shell.running:
            self.root.mainloop()
