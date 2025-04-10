from GameBoard import GameBoardInterface
from GameController import GameController, opponent
from AIPlayer import AIPlayer
import tkinter as tk
from PIL import Image, ImageTk
from StatusDisplay import StatusDisplay
from MenuBar import MenuBar
import time

SCREEN_SIZE = 1000

class OthelloApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Othello")
        self.bg_image = Image.open("./layout/fond_bois.png")
        if hasattr(Image, 'Resampling'):
            self.bg_image = self.bg_image.resize((SCREEN_SIZE, SCREEN_SIZE), Image.Resampling.LANCZOS)
        else:
            self.bg_image = self.bg_image.resize((SCREEN_SIZE, SCREEN_SIZE), Image.ANTIALIAS)

        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        # Créer un Label pour l'image de fond
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)  # Assurer que l'image occupe toute la fenêtre

        # Initialiser les autres composants
        self.controller = GameController()  # Tu dois avoir un GameController défini ailleurs
        self.status_display = StatusDisplay(self)  # Assurez-vous que StatusDisplay est défini
        self.game_board = GameBoardInterface(self, self.controller)  # Assurez-vous que GameBoard est défini
        self.menu = MenuBar(self, self.controller)  # Assurez-vous que MenuBar est défini

        # Passer en mode plein écran
        self.attributes("-fullscreen", False)

        # Mettre à jour la taille de la fenêtre en fonction de l'écran
        self.update_window_size()

    def update_window_size(self):
        """ Met à jour la taille de la fenêtre pour qu'elle occupe tout l'écran. """

        # Mettre à jour la taille de la fenêtre
        self.geometry(f"{SCREEN_SIZE}x{SCREEN_SIZE}+0+0")

    def update_status(self, message, color="white"):
        self.status_display.update_status(message, color)


def main():
    # Print rules
    print("Welcome to Othello!")
    print("The game is played on a " + str(8) + "x" + str(8) + " board.")
    print("Turns alternate between White (X) and Red (O). White goes first.")
    print("To enable AI for a player, use the Game menu.")
    print("To change the AI type, use the AI menu. (Minimax, Greedy, Random)")

    app = OthelloApp()
    app.mainloop()


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

    board = GameController(size)
    human_color = None
    ai_player = {}
    if mode == "1":
        chosen = input("Choisissez votre couleur ('B' pour Noir ou 'W' pour Blanc, par défaut 'B') : ") or "B"

        # On convertit en couleur
        if chosen.upper() == 'B':
            human_color = 'O'
        elif chosen.upper() == 'W':
            human_color = 'X'

        ai_color = opponent(human_color)
        # Ici, on fixe une profondeur élevée tout en espérant que mtd(f) accélère la recherche
        ai_player[ai_color] = AIPlayer(ai_color, max_depth=8)
    else:
        ai_player['O'] = AIPlayer('O', max_depth=6)
        ai_player['X'] = AIPlayer('X', max_depth=6)

    current_color = 'O'
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
    score_black = board.count('O')
    score_white = board.count('X')
    print("Fin de la partie")
    print(f"Red : {score_black} - Blanc : {score_white}")
    if score_black > score_white:
        print("Le Rouge gagne !")
    elif score_white > score_black:
        print("Le Blanc gagne !")
    else:
        print("Match nul.")



if __name__ == "__main__":
    main()