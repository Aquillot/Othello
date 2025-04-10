import tkinter as tk

class MenuBar(tk.Menu):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent

        game_menu = tk.Menu(self, tearoff=0)
        ai_menu = tk.Menu(self, tearoff=0)
        ai_red_menu = tk.Menu(ai_menu, tearoff=0)
        ai_white_menu = tk.Menu(ai_menu, tearoff=0)

        game_menu.add_command(label="Play Again", command=self.reset_game)
        game_menu.add_command(label="Toggle WHITE AI", command=lambda: self.toggle_ai("X"))
        game_menu.add_command(label="Toggle RED AI", command=lambda: self.toggle_ai("O"))
        ai_menu.add_cascade(label="Red AI Type", menu=ai_red_menu)
        ai_menu.add_cascade(label="White AI Type", menu=ai_white_menu)
        # Make Minimax the default AI type for the red player

        ai_red_algo = tk.StringVar()
        ai_white_algo = tk.StringVar()
        ai_red_menu.add_radiobutton(label="Minimax", variable=ai_red_algo, value="minimax")
        ai_white_menu.add_radiobutton(label="Minimax", variable=ai_white_algo, value="minimax")
        ai_red_algo.set("minimax")
        ai_white_algo.set("minimax")
        ai_red_algo.trace_add("write", lambda *args: self.controller.set_ai_type(0, ai_red_algo.get()))
        ai_white_algo.trace_add("write", lambda *args: self.controller.set_ai_type(1, ai_white_algo.get()))

        self.add_cascade(label="Game", menu=game_menu)
        self.add_cascade(label="AI", menu=ai_menu)

        parent.config(menu=self)

    def reset_game(self):
        self.controller.reset_game()
        self.parent.game_board.reset_board()
        self.parent.update_status("Othello")

    def toggle_ai(self, index):
        self.controller.toggle_ai(index)
        if self.controller.getCurentPlayer().is_ai:
            self.parent.update_status(f"{self.controller.getCurentPlayer().name}'s turn")
            self.parent.game_board.ai_move()