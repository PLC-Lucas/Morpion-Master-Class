# This code is adapted from the user's provided Pygame example.

def _verifier_vainqueur(p, joueur):
    """
    Vérifie s'il y a un vainqueur sur un plateau 2D.
    :param p: Le plateau de jeu (liste 2D de 3x3).
    :param joueur: Le symbole du joueur à vérifier ('X' or 'O').
    :return: True si le joueur a gagné, False sinon.
    """
    # Vérification des lignes
    for ligne in p:
        if ligne.count(joueur) == 3:
            return True
    # Vérification des colonnes
    for col in range(3):
        if p[0][col] == joueur and p[1][col] == joueur and p[2][col] == joueur:
            return True
    # Vérification des diagonales
    if p[0][0] == joueur and p[1][1] == joueur and p[2][2] == joueur:
        return True
    if p[0][2] == joueur and p[1][1] == joueur and p[2][0] == joueur:
        return True
    return False

def _plateau_plein(p):
    """
    Vérifie si le plateau 2D est plein.
    :param p: Le plateau de jeu (liste 2D de 3x3).
    :return: True si le plateau est plein, False sinon.
    """
    for ligne in p:
        if ' ' in ligne:
            return False
    return True

class MinMaxIA:
    """
    Classe pour l'IA Min-Max.
    Prend les symboles du joueur IA et du joueur humain pour rester flexible.
    """
    def __init__(self, ai_symbol='O', human_symbol='X'):
        self.ai_symbol = ai_symbol
        self.human_symbol = human_symbol

    def _minimax(self, p, est_max):
        """
        L'algorithme récursif Min-Max.
        :param p: Le plateau de jeu (liste 2D).
        :param est_max: Booléen, True si c'est le tour du joueur maximisant (IA), False sinon.
        :return: Le score du plateau.
        """
        if _verifier_vainqueur(p, self.ai_symbol):
            return 1
        if _verifier_vainqueur(p, self.human_symbol):
            return -1
        if _plateau_plein(p):
            return 0

        if est_max:
            meilleur = -1000
            for i in range(3):
                for j in range(3):
                    if p[i][j] == ' ':
                        p[i][j] = self.ai_symbol
                        score = self._minimax(p, False)
                        p[i][j] = ' '
                        meilleur = max(meilleur, score)
            return meilleur
        else:  # Tour du joueur minimisant
            meilleur = 1000
            for i in range(3):
                for j in range(3):
                    if p[i][j] == ' ':
                        p[i][j] = self.human_symbol
                        score = self._minimax(p, True)
                        p[i][j] = ' '
                        meilleur = min(meilleur, score)
            return meilleur

    def get_best_move(self, plateau_1d):
        """
        Calcule et retourne le meilleur coup pour l'IA.
        :param plateau_1d: Le plateau de jeu actuel (liste 1D de 9 cases).
        :return: L'index (0-8) du meilleur coup à jouer.
        """
        # Convertit le plateau 1D de l'application (avec "") en plateau 2D pour l'algo (avec ' ').
        plateau_2d = [[' ' for _ in range(3)] for _ in range(3)]
        for i in range(9):
            if plateau_1d[i] != "":
                plateau_2d[i // 3][i % 3] = plateau_1d[i]

        meilleur_score = -1000
        meilleur_move_index = -1

        # Si le plateau est vide, jouer au centre est une bonne optimisation.
        if all(c == "" for c in plateau_1d):
            return 4

        for i in range(3):
            for j in range(3):
                if plateau_2d[i][j] == ' ':
                    plateau_2d[i][j] = self.ai_symbol
                    score = self._minimax(plateau_2d, False)
                    plateau_2d[i][j] = ' '  # Annuler le coup

                    if score > meilleur_score:
                        meilleur_score = score
                        meilleur_move_index = i * 3 + j
        
        return meilleur_move_index
