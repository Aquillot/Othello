from typing import NamedTuple

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