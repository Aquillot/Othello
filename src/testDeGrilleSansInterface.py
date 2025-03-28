import numpy as np
from arbre import Arbre
from Structures import Player

DEFAULT_PLAYERS = [
    Player(symbol="🌑", name="White", color="#ffffff"),
    Player(symbol="🌕", name="Black", color="#000000"),
]
BOARD_SIZE = (3, 3)

class othelloGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self.grille = [[-1 for i in range(4)] for j in range(4)]
        # self.grille[3][3] = 0
        # self.grille[3][4] = 1
        # self.grille[4][3] = 1
        # self.grille[4][4] = 0
        self.grille[1][1] = 0
        self.grille[1][2] = 1
        self.grille[2][1] = 1
        self.grille[2][2] = 0
        self.player_turn = 0
        self.players = players
        self.board_size = board_size
        self.coup_possible = [[], []]
        self.coup_jouer = [(3, 3), (3, 4), (4, 3), (4, 4)]
        self.afficher_aide = True
        self.pos=Arbre()
        self.compteur=0
        self.grid=[[-1 for i in range(4)] for j in range(4)]
        self.grid[1][1] = 0
        self.grid[1][2] = 1
        self.grid[2][1] = 1
        self.grid[2][2] = 0
        self.possibilites(self.grid,self.player_turn,self.pos)
        print(self.compteur)

    def afficherGrille(self):
        if self.afficher_aide:
            self.connaitre_tous_les_coups_possibles_parcours_totale()
        for i in range(4):
            for j in range(4):
                if self.grille[i][j] == -1:
                    if self.afficher_aide:
                        try:
                            index = self.coup_possible[self.player_turn].index((i, j))
                            print(self.coup_possible[self.player_turn][index + 1], end=" ")
                        except ValueError:
                            print("_", end=" ")
                elif self.grille[i][j] == 0:
                    print(self.players[0].symbol, end=" ")
                else:
                    print(self.players[1].symbol, end=" ")
            print()

    def jouer(self, x, y):
        if self.grille[x][y] != -1:
            print("Coup impossible ! car la case est déjà occupée")
            return False
        if self.manger_ou_verifier_coup(x, y) == 0:
            print("Coup impossible ! car aucun pion n'est retourné")
            return False
        self.player_turn = (self.player_turn + 1 ) % 2
        self.coup_jouer.append((x, y))
        self.coup_possible = [[], []]
        return True

    def manger_ou_verifier_coup(self, x, y, verifier=False, player_turn=None):
        if player_turn is None:
            player_turn = self.player_turn
        nbPionsRetournes = 0
        # Dans les 8 directions possibles
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in directions:
            temp_dx = dx
            temp_dy = dy
            while 0 <= x + temp_dx < 4 and 0 <= y + temp_dy < 4 and self.grille[x + temp_dx][y + temp_dy] == (player_turn + 1) % 2 : # Python permet de faire des comparaisons folles
                # On continue dans cette direction
                temp_dx += dx
                temp_dy += dy
            # Si on est bloqué par un pion de notre couleur à la fin
            if  0 <= x + temp_dx < 4 and 0 <= y + temp_dy < 4 and self.grille[x + temp_dx][y + temp_dy] == player_turn and (temp_dx != dx or temp_dy != dy):
                # On retourne les pions
                while self.grille[x][y] != player_turn:
                    if not verifier:
                        self.grille[x][y] = player_turn
                    x += dx
                    y += dy
                    nbPionsRetournes += 1
        return nbPionsRetournes -1 # -1 car on retourne le pion joué

    # connaitre_tous_les_coups_possibles est une méthode qui permet de
    # connaitre tous les coups possibles pour le joueur actuel en parcourant les voisins des coups déjà joués
    # Mais cette méthode est dépréciée car elle est moins efficace que la méthode connaitre_tous_les_coups_possibles_parcours_totale
    #Je l'ai gardé car j'avais fais un test que de compléxité mais si on prends le nombre d'appel à la méthode manger_ou_verifier_coups
    # cette méthode est potentiellement plus efficace (en theorie, on fait des appels à manger_ou_verifier_coups que pour les cases vides adjacentes aux coups joués)
    def deprecated(self):
        # en connaissant les coups déjà joué, on peut réduire le champs de possibilité au case vide adjacent au coups joué
        coups_possibles = []
        for coup in self.coup_jouer:
            x, y = coup
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if 0 <= x + dx < 4 and 0 <= y + dy < 4 and self.grille[x + dx][y + dy] == -1:
                        if self.manger_ou_verifier_coup(x + dx, y + dy, verifier=True) > 0 and (x + dx, y + dy) not in coups_possibles:
                            coups_possibles.append((x + dx, y + dy))
        return coups_possibles

    def connaitre_tous_les_coups_possibles_parcours_totale(self, player_turn=None ):
        if player_turn is None:
            player_turn = self.player_turn
        for x in range(4):
            for y in range(4):
                if self.grille[x][y] == -1:
                    nombre_pions_retournes = self.manger_ou_verifier_coup(x, y, verifier=True, player_turn=player_turn)
                    if nombre_pions_retournes > 0 :
                        self.coup_possible[player_turn].append((x, y))
                        self.coup_possible[player_turn].append(nombre_pions_retournes)

    def partie_terminee(self):
        # Si il n'y a plus de case vide
        if len(self.coup_jouer) == 64:
            return True

        # Si aucun des joueurs ne peut jouer
        if len(self.coup_possible[0]) == 0 and len(self.coup_possible[1]) == 0:
            return True

        return False

    def gagnant(self):
        score = [0, 0]
        for i in range(4):
            for j in range(4):
                if self.grille[i][j] != -1:
                    score[self.grille[i][j]] += 1
        if score[0] > score[1]:
            return 0
        elif score[0] < score[1]:
            return 1
        else:
            return -1

    def jouerPartie(self):
        self.afficherGrille()
        while not self.partie_terminee():
            print("C'est au tour de ", self.players[self.player_turn].name)
            print("Les coups possibles sont : ", [i for i in self.coup_possible[self.player_turn] if type(i) == tuple])
            x, y = map(int, input("Entrez les coordonnées du coup à jouer : ").split())
            print(self.coup_possible)
            if (x, y) in self.coup_possible[self.player_turn]:
                self.jouer(x, y)
            else:
                print("Coup impossible !")
            self.afficherGrille()
        self.afficherGrille()
        gagnant = self.gagnant()
        if gagnant == -1:
            print("Match nul")
        else:
            print("Le gagnant est ", self.players[gagnant].name)

    def manger_ou_verifier_coup_test(self, x, y, player_turn, grid):
        nbPionsRetournes = 0
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in directions:
            temp_dx = dx
            temp_dy = dy
            while 0 <= x + temp_dx < 4 and 0 <= y + temp_dy < 4 and grid[x + temp_dx][y + temp_dy] == (player_turn + 1) % 2 : 
                temp_dx += dx
                temp_dy += dy
            if  0 <= x + temp_dx < 4 and 0 <= y + temp_dy < 4 and grid[x + temp_dx][y + temp_dy] == player_turn and (temp_dx != dx or temp_dy != dy):
                while grid[x][y] != player_turn:
                    x += dx
                    y += dy
                    nbPionsRetournes += 1
        return nbPionsRetournes-1

    def connaitre_tous_les_coups_possibles_parcours_totale_test(self, grid, player_turn ):
        cp=[]
        for x in range(4):
            for y in range(4):
                if grid[x][y] == -1:
                    nombre_pions_retournes = self.manger_ou_verifier_coup_test(x, y, player_turn, grid)
                    if nombre_pions_retournes > 0 :
                        cp.append((x, y))
                        cp.append(nombre_pions_retournes)
        return cp

    def jouer_test(self,grid,tour,tab,arbre):
        g=[[-1 for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                g[i][j]=grid[i][j]
        g[tab[0]][tab[1]]=tour
        return self.possibilites(g,(tour + 1 ) % 2,arbre)

    def possibilites(self,grid,tour,arbre):
        cp=self.connaitre_tous_les_coups_possibles_parcours_totale_test(grid,tour)
        self.compteur+=1
        while(len(cp)!=0):
            a=np.array([cp[0][0],cp[0][1]])
            b=cp[1]
            c=Arbre(a,b)
            self.jouer_test(grid,tour,a,c)
            arbre.ajoutEnfant(c)
            cp.pop(0)
            cp.pop(0)
        return arbre

if __name__ == "__main__":
    game = othelloGame()
    game.jouerPartie()
