import math
import copy

# Directions pour explorer les 8 directions autour d'une case
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

def opponent(color):
    return '□' if color == '■' else '■'


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


class Board:
    def __init__(self, size=8):
        self.size = size
        self.weights = create_weights(size)
        # Initialisation de la grille avec des cases vides représentées par '.'
        self.grid = [['.' for _ in range(size)] for _ in range(size)]
        # Position initiale (les 4 pions centraux)
        mid1 = size // 2 - 1
        mid2 = size // 2
        self.grid[mid1][mid1] = '■'
        self.grid[mid1][mid2] = '□'
        self.grid[mid2][mid1] = '□'
        self.grid[mid2][mid2] = '■'

    def in_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

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

    def game_over(self):
        if self.is_full():
            return True
        if not self.get_legal_moves('□') and not self.get_legal_moves('■'):
            return True
        return False

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
        new_board = Board(self.size)
        new_board.grid = copy.deepcopy(self.grid)
        new_board.weights = self.weights
        return new_board


# Table de transposition pour mémoriser les résultats et éviter des recalculs
class TranspositionTable:
    def __init__(self):
        self.table = {}

    def hash_board(self, board):
        return tuple(tuple(row) for row in board.grid)

    def store(self, board, depth, value):
        key = self.hash_board(board)
        self.table[key] = (depth, value)

    def lookup(self, board, depth):
        key = self.hash_board(board)
        if key in self.table:
            stored_depth, value = self.table[key]

            # On ne remplace que si on a une recherche à une profondeur au moins aussi grande
            if stored_depth >= depth:
                return value
        return None


def order_moves(board, moves, current_color):
    """
    Pour chaque coup, on calcule un score qui combine :
      - Le poids de la case (issu de board.weights)
      - La mobilité de l'adversaire après le coup (nombre de coups légaux pour l'adversaire, à inverser)
      - Une évaluation courte de la position obtenue (en jouant le coup puis en évaluant avec profondeur 1)

    On retourne les coups triés par score décroissant.
    """
    ordered = []
    for move in moves:
        x, y = move
        # Critère 1 : poids de la case
        weight = board.weights[x][y]

        # Simuler le coup pour obtenir une position
        flips = board.make_move(move, current_color)
        # Critère 2 : mobilité adverse (moins il y a de coups pour l'adversaire, mieux c'est)
        opp_moves = len(board.get_legal_moves(opponent(current_color)))
        # On prend l'inverse, par exemple : -opp_moves
        mobility_score = -opp_moves

        # Critère 3 : recherche courte (évaluation de la position à profondeur 1)
        short_eval = board.evaluate(current_color)

        # On annule le coup pour restaurer le plateau
        board.undo_move(move, flips, current_color)

        # Score composite (les coefficients sont à ajuster)
        score = weight * 1.0 + mobility_score * 2.0 + short_eval * 0.5
        ordered.append((score, move))
    # Tri décroissant du score
    ordered.sort(key=lambda x: x[0], reverse=True)
    return [move for score, move in ordered]

# IA basée sur NegaMax avec élagage alpha‑bêta et optimisée avec la méthode mtd(f)
class AIPlayer:
    def __init__(self, color, max_depth=4):
        self.color = color
        self.max_depth = max_depth
        self.tt = TranspositionTable()

    def mtdf(self, board, depth, first_guess):
        """
        Implémente l'algorithme mtd(f) (multipasses) qui réalise une série de recherches à fenêtre nulle.
        Cette méthode utilise une recherche en profondeur avec une fenêtre [beta-1, beta] très étroite,
        ce qui accélère l'élagage sans réduire la profondeur.
        """
        g = first_guess # Première estimation de l'évaluation de la position
        lowerbound = -math.inf
        upperbound = math.inf
        while lowerbound < upperbound:
            beta = g + 1 if g == lowerbound else g # Ajustement dynamique de beta
            g = self.nega_max(board, depth, beta - 1, beta, self.color)
            if g < beta:
                upperbound = g # On resserre la borne supérieure
            else:
                lowerbound = g # On resserre la borne inférieure
            if lowerbound == upperbound:
                break
        return g


    def nega_max(self, board, depth, alpha, beta, current_color):
        """
        Le NegaMax est une version plus légère (en code) du Minimax. Au lieu d'avoir deux valeurs
        (gain de MAX et gain de MIN), on inverse simplement le signe du score à chaque tour.
        """
        if depth == 0 or board.game_over():
            return board.evaluate(self.color)

        # Si on a déjà évalué cette position, on retourne la valeur
        tt_val = self.tt.lookup(board, depth)
        if tt_val is not None:
            return tt_val

        max_value = -math.inf
        legal_moves = board.get_legal_moves(current_color)
        if not legal_moves:
            # Pas de coup possible, on passe le tour et on joue pour l'adversaire
            value = -self.nega_max(board, depth - 1, -beta, -alpha, opponent(current_color))
            max_value = max(max_value, value)
            alpha = max(alpha, value)
        else:
            legal_moves = order_moves(board, legal_moves, current_color)
            for move in legal_moves:
                flips = board.make_move(move, current_color)
                value = -self.nega_max(board, depth - 1, -beta, -alpha, opponent(current_color))
                board.undo_move(move, flips, current_color)
                max_value = max(max_value, value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # coupure beta

        # On mémorise la valeur dans la table de transposition
        self.tt.store(board, depth, max_value)
        return max_value

    def choose_move(self, board):
        """
        Choisit le meilleur coup parmi les coups légaux en utilisant la méthode mtd(f) pour évaluer chaque coup.
        On part d'un premier guess à 0 et on évalue le résultat obtenu pour chaque coup.
        """
        best_move = None
        best_value = -math.inf
        first_guess = 0
        legal_moves = board.get_legal_moves(self.color)
        legal_moves = order_moves(board, legal_moves, self.color)
        if not legal_moves:
            return None
        for move in legal_moves:
            flips = board.make_move(move, self.color)
            # On évalue la position résultante avec mtd(f)
            value = -self.mtdf(board, self.max_depth - 1, first_guess)
            board.undo_move(move, flips, self.color)
            if value > best_value:
                best_value = value
                best_move = move
                first_guess = value  # Amélioration du guess pour la prochaine recherche
        return best_move


def play_console_game():
    try:
        size = int(input("Entrez la taille du plateau (pair, minimum 4, par défaut 8) : ") or "8")
    except ValueError:
        size = 8
    if size < 4 or size % 2 != 0:
        print("La taille doit être un nombre pair >= 4. On prend 8 par défaut.")
        size = 8

    print("Choisissez le mode de jeu :")
    print("1 - Joueur vs IA")
    print("2 - IA vs IA")
    mode = input("Votre choix (1 ou 2, par défaut 1) : ") or "1"

    board = Board(size)
    human_color = None
    ai_player = {}
    if mode == "1":
        chosen = input("Choisissez votre couleur ('B' pour Noir ou 'W' pour Blanc, par défaut 'B') : ") or "B"

        # On convertit en couleur
        if chosen.upper() == 'B':
            human_color = '□'
        elif chosen.upper() == 'W':
            human_color = '■'

        ai_color = opponent(human_color)
        # Ici, on fixe une profondeur élevée tout en espérant que mtd(f) accélère la recherche
        ai_player[ai_color] = AIPlayer(ai_color, max_depth=8)
    else:
        ai_player['□'] = AIPlayer('□', max_depth=6)
        ai_player['■'] = AIPlayer('■', max_depth=6)

    current_color = '□'
    while not board.game_over():
        board.display(current_color)
        legal_moves = board.get_legal_moves(current_color)
        if legal_moves:
            print(f"C'est le tour de {current_color}. Coups possibles : {legal_moves}")
            if mode == "1" and current_color == human_color:
                valid = False
                while not valid:
                    try:
                        move_input = input("Entrez vos coordonnées (ligne colonne) : ")
                        x, y = map(int, move_input.strip().split())
                        if (x, y) in legal_moves:
                            move = (x, y)
                            valid = True
                        else:
                            print("Coup invalide. Réessayez.")
                    except Exception:
                        print("Entrée incorrecte, réessayez.")
            else:
                print(f"L'IA ({current_color}) réfléchit...")
                move = ai_player[current_color].choose_move(board)
                if move is None:
                    print(f"{current_color} n'a pas de coup légal et passe son tour.")
            if legal_moves and move is not None:
                flips = board.make_move(move, current_color)
                print(f"{current_color} joue {move}.")
        else:
            print(f"{current_color} n'a aucun coup légal et passe son tour.")
        current_color = opponent(current_color)

    board.display()
    score_black = board.count('□')
    score_white = board.count('■')
    print("Fin de la partie")
    print(f"Noir : {score_black} - Blanc : {score_white}")
    if score_black > score_white:
        print("Le Noir gagne !")
    elif score_white > score_black:
        print("Le Blanc gagne !")
    else:
        print("Match nul.")

if __name__ == "__main__":
    play_console_game()
