import math



def opponent(color):
    return 'O' if color == 'X' else 'X'

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
        score = weight * 2.0 + mobility_score * 2.0 + short_eval * 0.5
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



