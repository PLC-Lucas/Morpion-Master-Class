import os
import random

class MorpionModel:
    def __init__(self):
        self.joueur_actuel = "X"
        self.pseudos = {"X": "Joueur X", "O": "Joueur O"}
        self.scores = {"X": 0, "O": 0}
        self.plateau = [""] * 9
        self.path_pseudos = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pseudos.txt")

    def verifier_victoire(self):
        v = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(self.plateau[a] == self.plateau[b] == self.plateau[c] != "" for a,b,c in v)

    def reset_plateau(self):
        self.plateau = [""] * 9
        self.joueur_actuel = "X"

    def charger_pseudos_fichier(self):
        """Lit le fichier pseudos.txt avec une sécurité sur l'encodage."""
        if os.path.exists(self.path_pseudos):
            try:
                # On essaie en utf-8 d'abord
                with open(self.path_pseudos, "r", encoding="utf-8") as f:
                    return sorted(list(set([l.strip() for l in f.read().splitlines() if l.strip()])))
            except UnicodeDecodeError:
                # Si ça rate, on essaie l'encodage Windows classique
                with open(self.path_pseudos, "r", encoding="latin-1") as f:
                    return sorted(list(set([l.strip() for l in f.read().splitlines() if l.strip()])))
        return []
    
    def sauver_pseudo_fichier(self, nom):
        existants = self.charger_pseudos_fichier()
        if nom not in existants:
            with open(self.path_pseudos, "a", encoding="utf-8") as f:
                f.write(nom + "\n")

    def supprimer_pseudo_fichier(self, pseudo_a_suppr):
        if os.path.exists(self.path_pseudos):
            lignes = []
            try:
                with open(self.path_pseudos, "r", encoding="utf-8") as f:
                    lignes = f.read().splitlines()
            except UnicodeDecodeError:
                with open(self.path_pseudos, "r", encoding="latin-1") as f:
                    lignes = f.read().splitlines()
            
            with open(self.path_pseudos, "w", encoding="utf-8") as f:
                for l in lignes:
                    if l.strip() != pseudo_a_suppr:
                        f.write(l + "\n")

    # --- IA LOGIQUE (Nayla & Hugo) ---
    def get_possibilities(self):
        return [i for i, case in enumerate(self.plateau) if case == ""]

    def simuler_victoire(self, index, joueur):
        v = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        plateau_temp = self.plateau[:]
        plateau_temp[index] = joueur
        return any(plateau_temp[a] == plateau_temp[b] == plateau_temp[c] == joueur for a,b,c in v)
