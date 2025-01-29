"""Tic-Tac-Toe game using Python and Tkinter."""

import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


# Player representation with symbol, name, and color
class Player(NamedTuple):
    symbol: str
    name: str
    color: str


# Represents a move on the board
class Move(NamedTuple):
    row: int
    col: int
    symbol: str = ""  # Default empty symbol


# Constants
BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(symbol="X", name="Red", color="#d31626"),
    Player(symbol="O", name="Blue", color="#0079c8"),
)


class TicTacToeGame:
    """Handles the game logic for Tic-Tac-Toe."""

    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self.players = cycle(players)  # Alternating players
        self.board_size = board_size
        self.current_player = next(self.players)
        self.winner_combination = []
        self.board_state = []  # Tracks moves on the board
        self.game_won = False
        self.winning_combinations = []
        self._initialize_board()

    def _initialize_board(self):
        """Set up the board with empty moves and generate winning combinations."""
        self.board_state = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self.winning_combinations = self._calculate_winning_combinations()

    def _calculate_winning_combinations(self):
        """Compute all possible winning move combinations."""
        rows = [[(move.row, move.col) for move in row] for row in self.board_state]
        columns = [list(col) for col in zip(*rows)]
        diagonal_1 = [row[i] for i, row in enumerate(rows)]
        diagonal_2 = [col[j] for j, col in enumerate(reversed(columns))]

        return rows + columns + [diagonal_1, diagonal_2]

    def switch_player(self):
        """Switch to the next player."""
        self.current_player = next(self.players)

    def is_valid_move(self, move: Move) -> bool:
        """Check if a move is valid."""
        row, col = move.row, move.col
        return not self.game_won and self.board_state[row][col].symbol == ""

    def apply_move(self, move: Move):
        """Apply a move to the board and check for a winner."""
        row, col = move.row, move.col
        self.board_state[row][col] = move

        for combination in self.winning_combinations:
            symbols = {self.board_state[r][c].symbol for r, c in combination}
            if len(symbols) == 1 and "" not in symbols:  # Winning condition met
                self.game_won = True
                self.winner_combination = combination
                break

    def has_winner(self) -> bool:
        """Return True if there is a winner."""
        return self.game_won

    def is_tie(self) -> bool:
        """Return True if the game is tied (board is full and no winner)."""
        return not self.game_won and all(move.symbol for row in self.board_state for move in row)

    def reset_game(self):
        """Reset the game state for a new round."""
        self._initialize_board()
        self.game_won = False
        self.winner_combination = []


class TicTacToeGUI(tk.Tk):
    """Graphical interface for Tic-Tac-Toe using Tkinter."""

    def __init__(self, game: TicTacToeGame):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.game = game
        self.cells = {}  # Mapping of buttons to board positions
        self._initialize_menu()
        self._initialize_display()
        self._initialize_board()

    def _initialize_menu(self):
        """Create the game menu with a restart option."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        game_menu = tk.Menu(menu_bar)
        game_menu.add_command(label="Play Again", command=self.reset_board)
        menu_bar.add_cascade(label="Game", menu=game_menu)

    def _initialize_display(self):
        """Create the label that displays game status messages."""
        display_frame = tk.Frame(self)
        display_frame.pack(fill=tk.X)

        available_fonts = list(font.families())
        custom_font = ("Ubuntu", 28, "bold") if "Ubuntu" in available_fonts else ("Arial", 24, "bold")

        self.status_display = tk.Label(display_frame, text="Tic-Tac-Toe", font=custom_font)
        self.status_display.pack(pady=(12, 8))

    def _initialize_board(self):
        """Create the Tic-Tac-Toe grid."""
        grid_frame = tk.Frame(self)
        grid_frame.pack(padx=15, pady=(0, 10))

        for row in range(self.game.board_size):
            self.rowconfigure(row, weight=1)
            self.columnconfigure(row, weight=1)
            for col in range(self.game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=2,
                    height=1,
                    highlightbackground="#fafbf8",
                    highlightthickness=3,
                    border=0,
                )
                self.cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self._handle_move)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _handle_move(self, event):
        """Handle a player's move when they click a cell."""
        clicked_button = event.widget
        row, col = self.cells[clicked_button]
        move = Move(row, col, self.game.current_player.symbol)

        if self.game.is_valid_move(move):
            self._update_cell(clicked_button)
            self.game.apply_move(move)

            if self.game.is_tie():
                self._update_status("Game Tied!", "red")
            elif self.game.has_winner():
                self._highlight_winning_cells()
                self._update_status(f"Player {self.game.current_player.name} Wins!", self.game.current_player.color)
            else:
                self.game.switch_player()
                self._update_status(f"{self.game.current_player.name}'s Turn")

    def _update_cell(self, clicked_button):
        """Update the UI when a move is made."""
        clicked_button.config(text=self.game.current_player.symbol, fg=self.game.current_player.color)

    def _update_status(self, message, color="black"):
        """Update the status message."""
        self.status_display.config(text=message, fg=color)

    def _highlight_winning_cells(self):
        """Highlight the winning combination on the board."""
        for button, position in self.cells.items():
            if position in self.game.winner_combination:
                button.config(highlightbackground="#27a327")

    def reset_board(self):
        """Reset the board and game state."""
        self.game.reset_game()
        self._update_status("Tic-Tac-Toe")
        for button in self.cells.keys():
            button.config(highlightbackground="#fafbf8", text="", fg="black")


def main():
    """Launch the Tic-Tac-Toe game."""
    game = TicTacToeGame()
    board = TicTacToeGUI(game)
    board.mainloop()


if __name__ == "__main__":
    main()
