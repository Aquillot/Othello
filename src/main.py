import tkinter as tk
from tkinter import font
from typing import NamedTuple

# Player representation with symbol, name, and color
class Player(NamedTuple):
    symbol: str
    name: str
    color: str
    is_ai: bool = False  # Default player is not an AI

# Represents a move on the board
class Move(NamedTuple):
    row: int
    col: int
    symbol: str = ""  # Default empty symbol

# Constants
BOARD_SIZE = 3
DEFAULT_PLAYERS = [
    Player(symbol="X", name="Red", color="#d31626"),
    Player(symbol="O", name="Blue", color="#0079c8"),
]

class TicTacToeGame(tk.Tk):
    """Handles the game logic and graphical interface for Tic-Tac-Toe."""

    def __init__(self, players=None, board_size=BOARD_SIZE):
        super().__init__()
        if players is None:
            players = DEFAULT_PLAYERS
        self.players = players
        self.board_size = board_size
        self.current_player_index = 0  # Start with the first player
        self.current_player = self.players[self.current_player_index]
        self.winner_combination = []
        self.board_state = []  # Tracks moves on the board
        self.game_won = False
        self.winning_combinations = []
        self._initialize_board()

        self.title("Tic-Tac-Toe")
        self.cells = {}  # Mapping of buttons to board positions
        self._initialize_menu()
        self._initialize_display()
        self._initialize_gui()

    def _initialize_board(self):
        """Set up the board with empty moves and generate winning combinations."""
        self.board_state = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self.winning_combinations = self._calculate_winning_combinations()

    def _initialize_menu(self):
        """Create the game menu with a restart option."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        game_menu = tk.Menu(menu_bar)
        game_menu.add_command(label="Play Again", command=self.reset_game)
        game_menu.add_command(label="Toggle Red AI", command=self.toggle_red_ai)
        game_menu.add_command(label="Toggle Blue AI", command=self.toggle_blue_ai)
        menu_bar.add_cascade(label="Game", menu=game_menu)

    def _initialize_display(self):
        """Create the label that displays game status messages."""
        display_frame = tk.Frame(self)
        display_frame.pack(fill=tk.X)

        available_fonts = list(font.families())
        custom_font = ("Ubuntu", 28, "bold") if "Ubuntu" in available_fonts else ("Arial", 24, "bold")

        self.status_display = tk.Label(display_frame, text="Tic-Tac-Toe", font=custom_font)
        self.status_display.pack(pady=(12, 8))

    def _initialize_gui(self):
        """Create the Tic-Tac-Toe grid."""
        grid_frame = tk.Frame(self)
        grid_frame.pack(padx=15, pady=(0, 10))

        for row in range(self.board_size):
            self.rowconfigure(row, weight=1)
            self.columnconfigure(row, weight=1)
            for col in range(self.board_size):
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
                button.bind("<ButtonPress-1>", self._handle_click)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def switch_player(self):
        """Switch to the next player by incrementing the index modulo 2."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]

    def _handle_click(self, event):
        """Handle a button click event."""
        button = event.widget
        row, col = self.cells[button]
        move = Move(row, col, self.current_player.symbol)
        self._handle_move(move)

    def _handle_move(self, move: Move):
        if self.is_valid_move(move):
            # Find the clicked button and update the cell
            button = next(button for button, position in self.cells.items() if position == (move.row, move.col))
            self._update_cell(button)
            self.apply_move(move)

            # If the game is over
            if self.is_tie():
                self._update_status("Game Tied!", "red")
                self.after(2000, self.reset_game) # Wait for a moment before resetting the game

            elif self.has_winner():
                print(f"Player {self.current_player.name} Wins!")
                self._highlight_winning_cells()
                self._update_status(f"Player {self.current_player.name} Wins!", self.current_player.color)
                self.after(2000, self.reset_game) # Wait for a moment before resetting the game


            # Switch to the next player
            else:
                self.switch_player()
                self._update_status(f"{self.current_player.name}'s Turn")
                if self.current_player.is_ai:
                    self.after(100, self.ai_move)

    def _update_cell(self, clicked_button):
        """Update the UI when a move is made."""
        clicked_button.config(text=self.current_player.symbol, fg=self.current_player.color)

    def _update_status(self, message, color="black"):
        """Update the status message."""
        self.status_display.config(text=message, fg=color)

    def _highlight_winning_cells(self):
        """Highlight the winning combination on the board."""
        for button, position in self.cells.items():
            if position in self.winner_combination:
                button.config(highlightbackground="#27a327")

    def reset_game(self):
        """Reset the game state for a new round."""
        self._initialize_board()
        self.game_won = False
        self.winner_combination = []
        self._update_status("Tic-Tac-Toe")
        for button in self.cells.keys():
            button.config(highlightbackground="#fafbf8", text="", fg="black")
        if self.current_player.is_ai:
            self.ai_move()

    def toggle_red_ai(self):
        """Toggle the AI for the Red player."""
        DEFAULT_PLAYERS[0] = Player(symbol="X", name="Red", color="#d31626", is_ai=not DEFAULT_PLAYERS[0].is_ai)
        if self.current_player_index == 0:
            self.ai_move()

    def toggle_blue_ai(self):
        """Toggle the AI for the Blue player."""
        DEFAULT_PLAYERS[1] = Player(symbol="O", name="Blue", color="#0079c8", is_ai=not DEFAULT_PLAYERS[1].is_ai)
        if self.current_player_index == 1:
            self.ai_move()

    def ai_move(self):
        """Make the AI move."""
        cell = self.best_move()
        row, col = cell
        move = Move(row, col, self.current_player.symbol)
        self._handle_move(move)

    def _calculate_winning_combinations(self):
        """Compute all possible winning move combinations."""
        rows = [[(move.row, move.col) for move in row] for row in self.board_state]
        columns = [list(col) for col in zip(*rows)]
        diagonal_1 = [row[i] for i, row in enumerate(rows)]
        diagonal_2 = [col[j] for j, col in enumerate(reversed(columns))]

        return rows + columns + [diagonal_1, diagonal_2]

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

    def minimax(self, depth, is_maximizing, alpha, beta):
        if self.has_winner():
            return 1 if self.current_player.symbol == 'O' else -1
        elif self.is_tie():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.board_state[row][col].symbol == "":
                        self.board_state[row][col] = Move(row, col, 'O')
                        score = self.minimax(depth + 1, False, alpha, beta)
                        self.board_state[row][col] = Move(row, col)
                        best_score = max(score, best_score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
            return best_score
        else:
            best_score = float('inf')
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.board_state[row][col].symbol == "":
                        self.board_state[row][col] = Move(row, col, 'X')
                        score = self.minimax(depth + 1, True, alpha, beta)
                        self.board_state[row][col] = Move(row, col)
                        best_score = min(score, best_score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
            return best_score

    def best_move(self):
        """Find the best move for the AI (Blue)."""
        best_score = -float('inf')
        move = None
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_state[row][col].symbol == "":
                    self.board_state[row][col] = Move(row, col, 'O')
                    score = self.minimax(0, False, -float('inf'), float('inf'))
                    self.board_state[row][col] = Move(row, col)
                    if score > best_score:
                        best_score = score
                        move = (row, col)
        return move

def main():
    """Launch the Tic-Tac-Toe game."""
    game = TicTacToeGame()
    game.mainloop()


if __name__ == "__main__":
    main()
