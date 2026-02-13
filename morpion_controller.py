import sys
import os
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QMessageBox

class MorpionController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # Audio
        self.players = {}
        self.init_audio("musique", 0.4)
        self.init_audio("clic", 0.8)
        self.init_audio("victoire", 1.0)
        self.jouer_musique_fond()

        # Connexions
        self.connect_signals()
        
        # Pour le message d'IA
        self.view.btn_ia_vs_player.clicked.connect(lambda: (self.jouer_son_clic(), QMessageBox.information(self.view, "IA", "L'IA arrive bientôt !")))
        self.view.btn_ia_vs_ia.clicked.connect(lambda: (self.jouer_son_clic(), QMessageBox.information(self.view, "IA", "L'IA contre l'IA arrive également bientôt !")))

    def init_audio(self, name, volume):
        player = QMediaPlayer()
        output = QAudioOutput()
        player.setAudioOutput(output)
        output.setVolume(volume)
        self.players[name] = (player, output)

    def play_sound(self, category, filename):
        # On est dans Controller/ donc on remonte d'un cran pour trouver Audio/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, filename)
        
        if os.path.exists(path):
            self.players[category][0].setSource(QUrl.fromLocalFile(path))
            self.players[category][0].play()
        else:
            print(f"⚠️ Son introuvable : {path}")

    def jouer_musique_fond(self):
        self.play_sound("musique", "Audio/City of Gamers - ChillGamingStudying Lofi Hip Hop Mix - (1 hour).mp3")
        self.players["musique"][0].setLoops(QMediaPlayer.Loops.Infinite)

    def jouer_son_clic(self): self.play_sound("clic", "Audio/Snes_pop.ogg.mp3")
    def jouer_son_victoire(self): self.play_sound("victoire", "Audio/gaining-experience-minecraft-sound-fx.wav")

    def connect_signals(self):
        # Menu
        self.view.btn_humain.clicked.connect(self.ouvrir_config_pseudos)
        self.view.btn_quitter.clicked.connect(self.view.close) # Appellera closeEvent de la Vue
        self.view.btn_musique.clicked.connect(self.music_on_off)
        
        # Config Pseudos
        self.view.btn_start.clicked.connect(self.valider_et_lancer)
        self.view.btn_retour.clicked.connect(lambda: (self.jouer_son_clic(), self.view.stack.setCurrentIndex(0)))
        
        # Suppression Pseudos
        for p in ["X", "O"]:
            # Rappel structure: (combo, line, check, btn_del)
            combo = self.view.inputs[p][0]
            btn_del = self.view.inputs[p][3]
            btn_del.clicked.connect(lambda checked, c=combo: self.supprimer_pseudo_selectionne(c))

        # Jeu (Grille)
        for i in range(9):
            self.view.boutons[i].clicked.connect(lambda _, x=i: self.clic_bouton(x))
            
        self.view.btn_menu.clicked.connect(self.quitter_match)

    def music_on_off(self):
        self.jouer_son_clic()
        p, _ = self.players["musique"]
        if p.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            p.pause()
            self.view.btn_musique.setText("MUSIQUE : OFF")
            self.view.update_music_button_style(False)
        else:
            p.play()
            self.view.btn_musique.setText("MUSIQUE : ON")
            self.view.update_music_button_style(True)

    def ouvrir_config_pseudos(self):
        self.jouer_son_clic()
        self.charger_pseudos_listes()
        for p in ["X", "O"]:
            _, line, check, _ = self.view.inputs[p]
            line.clear()
            check.setChecked(False)
        self.view.stack.setCurrentIndex(1)

    def charger_pseudos_listes(self):
        noms = self.model.charger_pseudos_fichier()
        for p in ["X", "O"]:
            combo = self.view.inputs[p][0]
            combo.clear()
            combo.addItems(noms)

    def valider_et_lancer(self):
        self.jouer_son_clic()
        for p in ["X", "O"]:
            combo, line, check, _ = self.view.inputs[p]
            nom = line.text().strip() or combo.currentText() or f"Joueur {p}"
            self.model.pseudos[p] = nom
            if check.isChecked() and line.text().strip():
                self.model.sauver_pseudo_fichier(nom)
        
        self.model.scores = {"X": 0, "O": 0}
        self.mettre_a_jour_affichage()
        self.view.stack.setCurrentIndex(2)

    def supprimer_pseudo_selectionne(self, combo):
        self.jouer_son_clic()
        pseudo = combo.currentText()
        if not pseudo or pseudo.startswith("Joueur"):
            return

        reponse = QMessageBox.question(self.view, "SUPPRESSION", f"Supprimer '{pseudo}' ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reponse == QMessageBox.StandardButton.Yes:
            self.model.supprimer_pseudo_fichier(pseudo)
            self.charger_pseudos_listes()

    def clic_bouton(self, index):
        if self.model.plateau[index] == "" and self.view.label_annonce.text() == "":
            self.model.plateau[index] = self.model.joueur_actuel
            
            # Update visuel
            couleur = "#E74C3C" if self.model.joueur_actuel == "X" else "#3498DB"
            self.view.boutons[index].setText(self.model.joueur_actuel)
            self.view.boutons[index].setStyleSheet(f"background-color: #34495E; color: {couleur}; border-radius: 20px; border: 3px solid {couleur};")
            
            if self.model.verifier_victoire():
                self.model.scores[self.model.joueur_actuel] += 3
                self.annoncer_resultat(f"🏆 {self.model.pseudos[self.model.joueur_actuel]} GAGNE ! +3 pts", "victoire")
                QTimer.singleShot(2500, self.rejouer_manche)
            elif "" not in self.model.plateau:
                self.model.scores["X"] += 1; self.model.scores["O"] += 1
                self.annoncer_resultat("🤝 MATCH NUL ! +1 pt", "nul")
                QTimer.singleShot(2500, self.rejouer_manche)
            else:
                self.model.joueur_actuel = "O" if self.model.joueur_actuel == "X" else "X"
                self.mettre_a_jour_affichage()

    def annoncer_resultat(self, message, son):
        self.view.label_annonce.setText(message)
        if son == "victoire": self.jouer_son_victoire()
        QTimer.singleShot(3500, lambda: self.view.label_annonce.setText(""))

    def mettre_a_jour_affichage(self):
        for p in ["X", "O"]:
            self.view.cards[p].setText(f"{self.model.pseudos[p]}\n{self.model.scores[p]} pts")
        self.view.label_info.setText(f"Tour de : {self.model.pseudos[self.model.joueur_actuel]}")

    def rejouer_manche(self):
        self.model.reset_plateau()
        for b in self.view.boutons:
            b.setText("")
            b.setStyleSheet("background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50;")
        self.mettre_a_jour_affichage()

    def quitter_match(self):
        self.jouer_son_clic()
        self.view.label_annonce.setText("")
        self.rejouer_manche()
        self.view.stack.setCurrentIndex(0)