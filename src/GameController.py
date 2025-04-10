from AIPlayer import *


import copy


# Directions pour explorer les 8 directions autour d'une case
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]


from Structures import Player

DEFAULT_PLAYERS = {
    "X":Player(symbol="X", name="White", color="#ffffff"),
    "O":Player(symbol="O", name="Black", color="#000000")
}

def create_weights(size):
    """
    Calcule dynamiquement la grille de poids pour un plateau de taille 'size'.
    Pour un 8x8, on obtient par exemple :
       [100, -20, 10,  5,  5, 10, -20, 100],
       [-20, -50, -2, -2, -2, -2, -50, -20],
       [10,  -2,  -1, -1, -1, -1,  -2,  10],
       [5,   -2,  -1, -1, -1, -1,  -2,   5],
       [5,   -2,  -1, -1, -1, -1,  -2,   5],
       [10,  -2,  -1, -1, -1, -1,  -2,  10],
       [-20, -50, -2, -2, -2, -2, -50, -20],
       [100, -20, 10,  5,  5, 10, -20, 100]
    Pour un plateau 4x4, nous pourrions avoir :
        [100, -20, -20, 100],
        [-20, -50, -50, -20],
        [-20, -50, -50, -20],
        [100, -20, -20, 100]
    (Les règles appliquées ici peuvent être ajustées en fonction des tests.)
    """
    weights = []
    for i in range(size):
        mirror_r = min(i, size - 1 - i)
        row = []
        for j in range(size):
            mirror_c = min(j, size - 1 - j)

            if mirror_r == 0:
                w = {0: 100, 1: -20, 2: 10}.get(mirror_c, 5)
            elif mirror_r == 1:
                w = {0: -20, 1: -50}.get(mirror_c, -2)
            else:
                w = 10 if mirror_r == 2 and mirror_c == 0 else -2 if mirror_c == 1 else -1 if mirror_c >= 2 else 5

            row.append(w)
        weights.append(row)
    return weights


class GameController:
    def __init__(self, size=8, players=DEFAULT_PLAYERS):
        self.size = size
        self.weights = create_weights(size)
        # Initialisation de la grille avec des cases vides représentées par '.'
        self.grid = [['.' for _ in range(size)] for _ in range(size)]
        # Position initiale (les 4 pions centraux)
        mid1 = size // 2 - 1
        mid2 = size // 2
        self.grid[mid1][mid1] = 'X'
        self.grid[mid1][mid2] = 'O'
        self.grid[mid2][mid1] = 'O'
        self.grid[mid2][mid2] = 'X'
        self.players = players
        self.current_color = 'O'  # Le joueur Noir commence
        self.players_AI = {"O":AIPlayer('O', max_depth=6),"X": AIPlayer('X', max_depth=6)}

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def getCurentPlayer(self):
        return self.players[self.current_color]

    def display(self, color=None):
        # On récupère les coups légaux
        legal_moves = self.get_legal_moves(color) if color else []

        # Affichage avec indices
        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for idx, row in enumerate(self.grid):
            print(f"{idx:2} ", end=" ")
            for jdx, cell in enumerate(row):
                if (idx, jdx) in legal_moves:
                    print(f"{self.count_flips(idx, jdx, color)} ", end=" ")
                else:
                    print(f"{cell} ", end=" ")
            print()

    # GameController
    def get_legal_moves(self, color):
        moves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.is_valid_move(x, y, color):
                    moves.append((x, y))

        # On retourne la liste des coups triés
        return moves

    def count_flips(self, x, y, color):
        """Compte le nombre de pions retournés pour un coup donné (utilisé pour l'affichage)"""
        flips = 0
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            count = 0
            while self.in_bounds(nx, ny) and self.grid[nx][ny] == opponent(color):
                count += 1
                nx += dx
                ny += dy
            if self.in_bounds(nx, ny) and self.grid[nx][ny] == color:
                flips += count
        return flips

    def is_valid_move(self, x, y, color):
        if self.grid[x][y] != '.':
            return False
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and self.grid[nx][ny] == opponent(color):
                nx += dx
                ny += dy
                while self.in_bounds(nx, ny):
                    if self.grid[nx][ny] == '.':
                        break
                    if self.grid[nx][ny] == color:
                        return True
                    nx += dx
                    ny += dy
        return False

    def make_move(self, move, color):
        """Applique le coup move=(x,y) et retourne la liste des positions retournées pour pouvoir annuler le coup"""
        x, y = move
        flips = []
        self.grid[x][y] = color
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            potential_flips = []
            while self.in_bounds(nx, ny) and self.grid[nx][ny] == opponent(color):
                potential_flips.append((nx, ny))
                nx += dx
                ny += dy
            if self.in_bounds(nx, ny) and self.grid[nx][ny] == color and potential_flips:
                for fx, fy in potential_flips:
                    self.grid[fx][fy] = color
                flips.extend(potential_flips)
        return flips

    def make_move_ai(self):
        """Joue un coup pour l'IA"""
        if self.players[self.current_color].is_ai:
            print(f"{self.current_color} réfléchit...")
            move = self.players_AI[self.current_color].choose_move(self)
            if move is not None:
                print(f"{self.current_color} joue {move}.")
                return move

    def toggle_ai(self, player_color):
        self.players[player_color] = self.players[player_color]._replace(is_ai=not self.players[player_color].is_ai)

    def undo_move(self, move, flips, color):
        """Annule le coup et restaure les pièces retournées"""
        x, y = move
        self.grid[x][y] = '.'
        for fx, fy in flips:
            self.grid[fx][fy] = opponent(color)

    def is_full(self):
        for row in self.grid:
            if '.' in row:
                return False
        return True

    def count(self, color):
        """Compte le nombre de pions d'une couleur sur le plateau"""
        return sum(row.count(color) for row in self.grid)

    # Used by AI
    def game_over(self):
        if self.is_full():
            return True
        if not self.get_legal_moves('O') and not self.get_legal_moves('X'):
            return True
        return False

    def switch_player(self):
        """Change le joueur courant"""
        self.current_color = opponent(self.current_color)

    def evaluate(self, color):
        """
        Fonction d'évaluation statique basée sur la grille de poids.
        (somme des poids des cases occupées par le joueur - somme des poids des cases occupées par l'adversaire)
        """
        score = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x][y] == color:
                    score += self.weights[x][y]
                elif self.grid[x][y] == opponent(color):
                    score -= self.weights[x][y]
        return score

    def clone(self):
        new_board = GameController(self.size)
        new_board.grid = copy.deepcopy(self.grid)
        new_board.weights = self.weights
        return new_board
