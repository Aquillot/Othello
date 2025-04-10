import tkinter as tk
from tkinter import font,PhotoImage

from PIL import ImageTk,Image

from Structures import Move

SIZE_BOX = 1
HEIGHT = 1
class GameBoardInterface(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        self.AI = False
        frame = tk.Frame(parent, bg="black", borderwidth=50, relief="solid")  # Bordure noire
        frame.pack(padx=10, pady=10)  # Ajoute un léger espace autour

        super().__init__(frame)
        self.parent = parent
        self.cells = {}
        self.transparent = ImageTk.PhotoImage(Image.open("./layout/transparent.png").resize((50*HEIGHT, 50*HEIGHT)))
        # Préchargement des images des joueurs
        self.player_images = {
            "X": ImageTk.PhotoImage(Image.open("./layout/jeton_x.png").resize((50*HEIGHT, 50*HEIGHT))),
            "O": ImageTk.PhotoImage(Image.open("./layout/jeton_o.png").resize((50*HEIGHT, 50*HEIGHT)))
        }
        self._initialize_gui()
        self.pack(expand=True, fill="both")
        self.legal_moves = []

    def _initialize_gui(self):
        self.legal_moves = self.controller.get_legal_moves(self.controller.current_color)

        for row in range(self.controller.size):
            for col in range(self.controller.size):
                photo = self.player_images.get(self.controller.grid[row][col])
                button = tk.Button(
                    self, font=("Noto Color Emoji", 36), text="",image=self.transparent,
                    relief="flat", highlightthickness=1, highlightbackground="black", activebackground="#1a6420",
                    bg="#0b2b0c",width=SIZE_BOX, height=SIZE_BOX,
                )
                if photo:
                    print(self.controller.grid[row][col], "coordinates", row, col)
                    button.config(
                        fg="#0b2b0c",
                        image=photo, text="", compound="center",
                        highlightthickness=1, highlightbackground="black", width=SIZE_BOX, height=SIZE_BOX,
                    )
                    button.image_ref = photo
                if (col,row) in self.legal_moves:
                    button.config(
                        fg="#ff2b0c",
                        image=self.transparent, text="·", compound="center",
                        highlightthickness=1, highlightbackground="black", width=SIZE_BOX, height=SIZE_BOX,
                    )
                    button.image_ref = photo
                self.cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self._handle_click)
                button.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
        for i in range(self.controller.size):
            self.grid_rowconfigure(i, weight=0, minsize=50)
            self.grid_columnconfigure(i, weight=0, minsize=50)


    def update_board(self, color):
        self.legal_moves = self.controller.get_legal_moves(self.controller.current_color)
        if color == "O":
            colorText = "#ff2b0c"
        else:
            colorText = "#ffffff"

        for button in self.cells.keys():
            row, col = self.cells[button]
            photo = self.player_images.get(self.controller.grid[row][col])
            button.config(
                fg="#0b2b0c",
                image=photo, text="", compound="center",
                highlightthickness=1, highlightbackground="black", width=SIZE_BOX, height=SIZE_BOX,
            )
            button.image_ref = photo
            if (row,col) in self.legal_moves:

                button.config(
                    fg=colorText,
                    image=self.transparent, text="·", compound="center",
                    highlightthickness=1, highlightbackground="black", width=SIZE_BOX, height=SIZE_BOX,
                )
                button.image_ref = photo

    def _handle_click(self, event):
        button = event.widget
        row, col = self.cells[button]
        move_with_color = (row, col, self.controller.current_color)
        self.legal_moves = self.controller.get_legal_moves(self.controller.current_color)
        if self.legal_moves == []:
            print("no legal moves switching player")
            self.controller.switch_player()
            self.legal_moves = self.controller.get_legal_moves(self.controller.current_color)
            if self.legal_moves == []:
                self.parent.update_status("Game Tied!", "red")
                self.after(2000, self.parent.menu.reset_game)
                return
        move = move_with_color[:2]
        if move in self.legal_moves:
            flips = self.controller.make_move(move, self.controller.current_color)
            self._update_cell(button, move_with_color, flips)

            if self.controller.game_over():
                score_black = self.controller.count('O')
                score_white = self.controller.count('X')
                if score_black > score_white:
                    self.parent.update_status(f"{self.controller.getCurentPlayer().name} Wins! with {score_black} against {score_white}", "red")
                elif score_black < score_white:
                    self.parent.update_status(f"{self.controller.getCurentPlayer().name} Wins! with {score_white} against {score_black}", "white")
                else:
                    self.parent.update_status("Game Tied!", "red")
                self.after(2000, self.parent.menu.reset_game)
            else:
                self.controller.switch_player()
                self.parent.update_status(f"{self.controller.getCurentPlayer().name}'s Turn", self.controller.players[self.controller.current_color].color)
                self.after(200, self.ai_move)
            self.update_board(self.controller.current_color)

    def _update_cell(self, button, move, flips):
        photo = self.player_images.get(move[2])

        button.config(
            fg="#0b2b0c",
            image=photo, compound="center", text="",
            highlightthickness=1, highlightbackground="black",width=SIZE_BOX, height=SIZE_BOX
        )
        button.image_ref = photo
        for flip in flips:
            flip_button = next(b for b, pos in self.cells.items() if pos == flip)
            flip_button.config(
                fg="#0b2b0c", image=photo, compound="center", text="",
                highlightthickness=1, highlightbackground="black",width=SIZE_BOX, height=SIZE_BOX
            )
            flip_button.image_ref = photo


    def ai_move(self):
        if self.controller.getCurentPlayer().is_ai:
            move_pos = self.controller.make_move_ai()
            if move_pos:
                row, col = move_pos
                move = (row, col, self.controller.current_color)
                self._handle_click(type('', (), {'widget': next(button for button, pos in self.cells.items() if pos == (row, col))})())


    def reset_board(self):
        for button in self.cells.keys():
            button.config(text="", fg="#0b2b0c", highlightbackground="#0b2b0c")

        # If the current player is an AI, make the AI move
        if self.controller.getCurentPlayer().is_ai:
            self.ai_move()