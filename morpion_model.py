import os

class MorpionModel:
    def __init__(self):
        """
        Gère les données : plateau, scores, pseudos.
        """
        self.joueur_actuel = "X"
        self.pseudos = {"X": "Joueur X", "O": "Joueur O"}
        self.scores = {"X": 0, "O": 0}
        self.plateau = [""] * 9

    def verifier_victoire(self):
        """Vérifie les combinaisons gagnantes."""
        v = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(self.plateau[a] == self.plateau[b] == self.plateau[c] != "" for a,b,c in v)

    def reset_plateau(self):
        """Remet le plateau à zéro pour une nouvelle manche."""
        self.plateau = [""] * 9
        self.joueur_actuel = "X"

    def charger_pseudos_fichier(self):
        """Lit le fichier pseudos.txt et retourne une liste."""
        if os.path.exists("pseudos.txt"):
            with open("pseudos.txt", "r") as f:
                return sorted(list(set(f.read().splitlines())))
        return []

    def sauver_pseudo_fichier(self, nom):
        """Ajoute un pseudo au fichier."""
        existants = self.charger_pseudos_fichier()
        if nom not in existants:
            with open("pseudos.txt", "a") as f:
                f.write(nom + "\n")

    def supprimer_pseudo_fichier(self, pseudo_a_suppr):
        """Réécrit le fichier sans le pseudo supprimé."""
        if os.path.exists("pseudos.txt"):
            with open("pseudos.txt", "r") as f:
                lignes = f.read().splitlines()
            with open("pseudos.txt", "w") as f:
                for l in lignes:
                    if l != pseudo_a_suppr:
                        f.write(l + "\n")