import tkinter as tk

class MenuBar(tk.Menu):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent

        game_menu = tk.Menu(self, tearoff=0)
        ai_menu = tk.Menu(self, tearoff=0)
        ai_red_menu = tk.Menu(ai_menu, tearoff=0)
        ai_blue_menu = tk.Menu(ai_menu, tearoff=0)

        game_menu.add_command(label="Play Again", command=self.reset_game)
        game_menu.add_command(label="Toggle Red AI", command=lambda: self.toggle_ai(0))
        game_menu.add_command(label="Toggle Blue AI", command=lambda: self.toggle_ai(1))
        ai_menu.add_cascade(label="Red AI Type", menu=ai_red_menu)
        ai_menu.add_cascade(label="Blue AI Type", menu=ai_blue_menu)
        # Make Minimax the default AI type for the red player

        ai_red_algo = tk.StringVar()
        ai_blue_algo = tk.StringVar()
        ai_red_menu.add_radiobutton(label="Minimax", variable=ai_red_algo, value="minimax")
        ai_red_menu.add_radiobutton(label="Greedy", variable=ai_red_algo, value="greedy")
        ai_red_menu.add_radiobutton(label="Random", variable=ai_red_algo, value="random")
        ai_blue_menu.add_radiobutton(label="Minimax", variable=ai_blue_algo, value="minimax")
        ai_blue_menu.add_radiobutton(label="Greedy", variable=ai_blue_algo, value="greedy")
        ai_blue_menu.add_radiobutton(label="Random", variable=ai_blue_algo, value="random")
        ai_red_algo.set("minimax")
        ai_blue_algo.set("minimax")
        ai_red_algo.trace("w", lambda *args: self.controller.set_ai_type(0, ai_red_algo.get()))
        ai_blue_algo.trace("w", lambda *args: self.controller.set_ai_type(1, ai_blue_algo.get()))

        self.add_cascade(label="Game", menu=game_menu)
        self.add_cascade(label="AI", menu=ai_menu)

        parent.config(menu=self)

    def reset_game(self):
        self.controller.reset_game()
        self.parent.game_board.reset_board()
        self.parent.update_status("Tic-Tac-Toe")

    def toggle_ai(self, index):
        self.controller.toggle_ai(index)
        if self.controller.current_player.is_ai:
            self.parent.update_status(f"{self.controller.current_player.name}'s Turn")
            self.parent.game_board.ai_move()