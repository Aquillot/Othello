import tkinter as tk
from tkinter import font
from PIL import ImageTk,Image

class StatusDisplay(tk.Label):
    def __init__(self, parent):
        available_fonts = list(font.families())
        custom_font = ("Ubuntu", 50, "bold") if "Ubuntu" in available_fonts else ("Arial", 50, "bold")
        super().__init__(parent, text="Othello", font=custom_font,highlightthickness=0, bg="black")
        self.pack(anchor="w", padx=20, pady=(12, 8))

    def update_status(self, message, color="#0b2b0c"):
        self.config(text=message, fg=color)
