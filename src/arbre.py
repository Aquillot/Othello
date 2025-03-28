import numpy as np

class Arbre:
    def __init__(self, pos=None, val=None):
        if pos is None or val is None:
            self.enfants = []
        else:
            self.pos = pos
            self.val = val
            self.enfants = []

    def ajoutEnfant(self,enfant):
        self.enfants.append(enfant)