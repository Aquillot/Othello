import tkinter as tk
from tkinter import font
from typing import NamedTuple
import random

# Player representation with symbol, name, and color
class Player(NamedTuple):
    symbol: str
    name: str
    color: str
    is_ai: bool = False

# Represents a move on the board
class Move(NamedTuple):
    row: int
    col: int
    symbol: str = ""

# Constants
BOARD_SIZE = 3
DEFAULT_PLAYERS = [
    Player(symbol="X", name="Red", color="#d31626"),
    Player(symbol="O", name="Blue", color="#0079c8"),
]

# ============================
# ===== Game Controller ======
# ============================

class GameController:
    """Handles the game logic and state"""
    def __init__(self, board_size=BOARD_SIZE, players=None):
        self.board_size = board_size
        self.players = players or DEFAULT_PLAYERS
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]
        self.game_won = False
        self.winner_combination = []
        self.ai_types = ["minimax", "random", "greedy"]
        self.player_ai_type = {player.symbol: "minimax" for player in self.players}
        self._initialize_board()

    def set_ai_type(self, player_index, ai_type):
        self.player_ai_type[self.players[player_index].symbol] = ai_type

    def _initialize_board(self):
        self.board_state = [[Move(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        self.winning_combinations = self._calculate_winning_combinations()

    def _calculate_winning_combinations(self):
        rows = [[(move.row, move.col) for move in row] for row in self.board_state]
        cols = [list(col) for col in zip(*rows)]
        diag1 = [rows[i][i] for i in range(self.board_size)]
        diag2 = [rows[i][self.board_size - i - 1] for i in range(self.board_size)]
        return rows + cols + [diag1, diag2]

    def is_valid_move(self, move: Move) -> bool:
        return not self.game_won and self.board_state[move.row][move.col].symbol == ""

    def apply_move(self, move: Move):
        row, col = move.row, move.col
        self.board_state[row][col] = move

        # Check if the move resulted in a win
        for combination in self.winning_combinations:
            symbols = {self.board_state[r][c].symbol for r, c in combination}
            if len(symbols) == 1 and "" not in symbols:
                self.game_won = True
                self.winner_combination = combination
                break

    def switch_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]

    def has_winner(self) -> str or bool:
        # Check all winning combinations to see if there is a winner
        for combination in self.winning_combinations:
            symbols = {self.board_state[r][c].symbol for r, c in combination}
            if len(symbols) == 1 and "" not in symbols:
                # Return the winning player's symbol
                return symbols.pop()

        return False

    def is_tie(self) -> bool:
        # Check if the game is a tie
        return not self.game_won and all(move.symbol for row in self.board_state for move in row)

    def reset_game(self):
        self._initialize_board()
        self.game_won = False
        self.winner_combination = []
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

    def toggle_ai(self, player_index):
        self.players[player_index] = self.players[player_index]._replace(is_ai=not self.players[player_index].is_ai)
        if self.current_player_index == player_index:  # Update current player if it's the one being toggled
            self.current_player = self.players[player_index]

    def minimax(self, depth, is_maximizing_player, alpha, beta):
        # If the game is won or finished, return a score
        if self.has_winner() == self.current_player.symbol:
            return 1  # AI wins
        elif self.has_winner() == self.get_opponent(self.current_player).symbol:
            return -1  # Opponent wins

        if self.is_tie():
            return 0  # Tie game

        if is_maximizing_player:
            max_eval = float('-inf')
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.board_state[r][c].symbol == "":
                        self.board_state[r][c] = Move(r, c, self.current_player.symbol)
                        eval = self.minimax(depth + 1, False, alpha, beta)
                        self.board_state[r][c] = Move(r, c, "")
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)  # Update alpha
                        if beta <= alpha:  # Pruning
                            break  # Prune the branch
            return max_eval
        else:
            min_eval = float('inf')
            opponent = self.get_opponent(self.current_player)
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.board_state[r][c].symbol == "":
                        self.board_state[r][c] = Move(r, c, opponent.symbol)
                        eval = self.minimax(depth + 1, True, alpha, beta)
                        self.board_state[r][c] = Move(r, c, "")
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)  # Update beta
                        if beta <= alpha:  # Pruning
                            break  # Prune the branch
            return min_eval

    def best_move(self):
        ai_type = self.player_ai_type[self.current_player.symbol]
        if ai_type == "random":
            return self.random_move()
        elif ai_type == "minimax":
            return self._minimax_best_move()
        elif ai_type == "greedy":
            return self.greedy_move()

    def greedy_move(self):
        # Check for a winning move for the AI
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board_state[r][c].symbol == "":  # Check if the cell is empty
                    move = Move(r, c, self.current_player.symbol)
                    self.board_state[r][c] = move
                    if self.has_winner() == self.current_player.symbol:  # AI can win
                        self.board_state[r][c] = Move(r, c, "")  # Reset move
                        return r, c  # Return the winning move
                    self.board_state[r][c] = Move(r, c, "")  # Reset move

        # Check for a blocking move (if the opponent can win)
        opponent = self.get_opponent(self.current_player)
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board_state[r][c].symbol == "":  # Check if the cell is empty
                    move = Move(r, c, opponent.symbol)
                    self.board_state[r][c] = move
                    if self.has_winner() == opponent.symbol:  # Opponent can win
                        self.board_state[r][c] = Move(r, c, "")  # Reset move
                        return r, c  # Block the opponent's winning move
                    self.board_state[r][c] = Move(r, c, "")  # Reset move

        # If no winning or blocking move, pick the first available move
        available_moves = [(r, c) for r in range(self.board_size) for c in range(self.board_size)
                           if self.board_state[r][c].symbol == ""]
        return available_moves[0] if available_moves else None  # Return the first available move

    def random_move(self):
        available_moves = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if
                           self.board_state[r][c].symbol == ""]
        return random.choice(available_moves) if available_moves else None

    def _minimax_best_move(self):
        best_value = float('-inf')
        best_move = None
        # Initialize alpha and beta for the search of the best move
        alpha = float('-inf')
        beta = float('inf')

        # Evaluate all possible moves and choose the one with the best evaluation
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board_state[r][c].symbol == "":
                    self.board_state[r][c] = Move(r, c, self.current_player.symbol)
                    move_value = self.minimax(0, False, alpha, beta)
                    self.board_state[r][c] = Move(r, c, "")
                    if move_value > best_value:
                        best_value = move_value
                        best_move = (r, c)

        return best_move

    def get_opponent(self, current_player):
        return self.players[1] if current_player == self.players[0] else self.players[0]


# ============================
# === Graphical Interface ===
# ============================

class GameBoard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.cells = {}
        self._initialize_gui()
        self.pack(padx=15, pady=(0, 10))

    def _initialize_gui(self):
        for row in range(self.controller.board_size):
            for col in range(self.controller.board_size):
                button = tk.Button(
                    self, text="", font=font.Font(size=36, weight="bold"), width=2, height=1,
                    highlightbackground="#fafbf8", highlightthickness=3, border=0
                )
                self.cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self._handle_click)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

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
        button.config(text=move.symbol, fg=self.controller.current_player.color)

    def _highlight_winning_cells(self):
        for button, pos in self.cells.items():
            if pos in self.controller.winner_combination:
                button.config(highlightbackground="#27a327")

    def ai_move(self):
        if self.controller.current_player.is_ai:
            move_pos = self.controller.best_move()
            if move_pos:
                row, col = move_pos
                move = Move(row, col, self.controller.current_player.symbol)
                self._handle_click(type('', (), {'widget': next(button for button, pos in self.cells.items() if pos == (row, col))})())

    def reset_board(self):
        for button in self.cells.keys():
            button.config(text="", fg="black", highlightbackground="#fafbf8")

        # If the current player is an AI, make the AI move
        if self.controller.current_player.is_ai:
            self.ai_move()

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

class StatusDisplay(tk.Label):
    def __init__(self, parent):
        available_fonts = list(font.families())
        custom_font = ("Ubuntu", 28, "bold") if "Ubuntu" in available_fonts else ("Arial", 24, "bold")
        super().__init__(parent, text="Tic-Tac-Toe", font=custom_font, fg="black")
        self.pack(pady=(12, 8))

    def update_status(self, message, color="black"):
        self.config(text=message, fg=color)

class TicTacToeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")

        self.controller = GameController()
        self.status_display = StatusDisplay(self)
        self.game_board = GameBoard(self, self.controller)
        self.menu = MenuBar(self, self.controller)

    def update_status(self, message, color="black"):
        self.status_display.update_status(message, color)

def main():
    app = TicTacToeApp()
    app.mainloop()

if __name__ == "__main__":
    main()