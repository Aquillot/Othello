import tkinter as tk
from tkinter import font,PhotoImage
from Structures import Move
from PIL import ImageTk,Image
class GameBoard(tk.Frame):
    def __init__(self, parent, controller):
        frame = tk.Frame(parent, bg="black", borderwidth=50, relief="solid")  # Bordure noire
        frame.pack(padx=10, pady=10)  # Ajoute un léger espace autour
        super().__init__(frame)
        self.controller = controller
        self.parent = parent
        self.cells = {}
        self._initialize_gui()
        # Préchargement des images des joueurs
        self.player_images = {
            "X": ImageTk.PhotoImage(Image.open("./layout/jeton_x.png").resize((100, 100))),
            "O": ImageTk.PhotoImage(Image.open("./layout/jeton_o.png").resize((100, 100)))
        }

        self.pack()

    def _initialize_gui(self):
        for row in range(self.controller.board_size[0]):
            for col in range(self.controller.board_size[1]):
                button = tk.Button(
                    self, text="", font=("Noto Color Emoji",36), width=3, height=2,
                    relief="flat", highlightthickness=1, highlightbackground="black",activebackground="#1a6420", bg="#0b2b0c",
                )
                self.cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self._handle_click)
                button.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")

    def _handle_click(self, event):
        button = event.widget
        row, col = self.cells[button]
        move = Move(row, col, self.controller.current_player.symbol)

        if self.controller.is_valid_move(move):
            self._update_cell(button, move)
            self.controller.apply_move(move)

            if self.controller.has_winner():
                self.parent.update_status(f"{self.controller.current_player.name} Wins!", self.controller.current_player.color)
                self._highlight_winning_cells()
                self.after(2000, self.parent.menu.reset_game)
            elif self.controller.is_tie():
                self.parent.update_status("Game Tied!", "red")
                self.after(2000, self.parent.menu.reset_game)
            else:
                self.controller.switch_player()
                self.parent.update_status(f"{self.controller.current_player.name}'s Turn")
                self.after(200, self.ai_move)

    def _update_cell(self, button, move):
        photo = self.player_images.get(move.symbol)

        if photo:
            button.config(
                fg=self.controller.current_player.color,
                image=photo, compound="center",
                highlightthickness=1, highlightbackground="black"
            )
            button.image_ref = photo
        else :
            print(move.symbol)


    def _highlight_winning_cells(self):
        for button, pos in self.cells.items():
            if pos in self.controller.winner_combination:
                button.config(highlightbackground="#0b2b0c")

    def ai_move(self):
        if self.controller.current_player.is_ai:
            move_pos = self.controller.best_move()
            if move_pos:
                row, col = move_pos
                move = Move(row, col, self.controller.current_player.symbol)
                self._handle_click(type('', (), {'widget': next(button for button, pos in self.cells.items() if pos == (row, col))})())

    def reset_board(self):
        for button in self.cells.keys():
            button.config(text="", fg="#0b2b0c", highlightbackground="#0b2b0c")

        # If the current player is an AI, make the AI move
        if self.controller.current_player.is_ai:
            self.ai_move()