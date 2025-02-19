import tkinter as tk
from tkinter import font

class StatusDisplay(tk.Label):
    def __init__(self, parent):
        available_fonts = list(font.families())
        custom_font = ("Ubuntu", 28, "bold") if "Ubuntu" in available_fonts else ("Arial", 24, "bold")
        super().__init__(parent, text="Tic-Tac-Toe", font=custom_font, fg="black")
        self.pack(pady=(12, 8))

    def update_status(self, message, color="black"):
        self.config(text=message, fg=color)
