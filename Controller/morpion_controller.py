import os, random
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QMessageBox

class MorpionController:
    def __init__(self, model, view):
        self.model, self.view = model, view
        self.mode_jeu = "HUMAIN" 
        self.players = {}
        self.prochain_starter = None # Pour savoir qui commence (Pile ou Face / Gagnant)
        self.en_animation = False # Pour bloquer les clics pendant le pile ou face
        self.playlist = []
        self.charger_playlist()
        for n, v in [("musique", 0.4), ("clic", 0.8), ("victoire", 1.0)]: self.init_audio(n, v)
        self.jouer_musique_fond()
        self.connect_signals()

    def charger_playlist(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Audio")
        if os.path.exists(path):
            excl = ["Snes_pop.ogg.wav", "gaining-experience-minecraft-sound-fx.wav"]
            self.playlist = [f for f in os.listdir(path) if f.endswith((".mp3", ".wav")) and f not in excl]

    def init_audio(self, name, vol):
        p = QMediaPlayer(); o = QAudioOutput(); p.setAudioOutput(o); o.setVolume(vol)
        self.players[name] = (p, o)
        if name == "musique": p.mediaStatusChanged.connect(self.check_music_end)

    def play_sound(self, cat, file):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file)
        if os.path.exists(path):
            self.players[cat][0].setSource(QUrl.fromLocalFile(path))
            self.players[cat][0].play()

    def check_music_end(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia: self.jouer_musique_fond()

    def jouer_musique_fond(self): 
        if self.playlist:
            self.play_sound("musique", f"Audio/{random.choice(self.playlist)}")

    def jouer_son_clic(self): self.play_sound("clic", "Audio/Snes_pop.ogg.wav")
    
    def jouer_son_victoire(self): self.play_sound("victoire", "Audio/gaining-experience-minecraft-sound-fx.wav")

    def connect_signals(self):
            v = self.view
            v.btn_humain.clicked.connect(lambda: self.start_mode("HUMAIN"))
            v.btn_ia_vs_player.clicked.connect(lambda: self.start_mode("IA"))
            v.btn_ia_vs_ia.clicked.connect(lambda: self.start_mode("IA_VS_IA"))
            v.btn_quitter.clicked.connect(v.close)
            v.btn_musique.clicked.connect(self.music_on_off)
            v.btn_start.clicked.connect(self.valider_et_lancer)
            v.btn_retour.clicked.connect(lambda: (self.jouer_son_clic(), v.stack.setCurrentIndex(0)))
            v.btn_lancer_ia.clicked.connect(self.valider_ia_vs_ia)
            v.btn_retour_ia.clicked.connect(lambda: (self.jouer_son_clic(), v.stack.setCurrentIndex(0)))
            v.btn_menu.clicked.connect(self.quitter_match)
            for i in range(9): v.boutons[i].clicked.connect(lambda _, x=i: self.clic_bouton(x))
            for p in ["X", "O"]: v.inputs[p][3].clicked.connect(lambda _, p_symbol=p: self.suppr_pseudo(p_symbol))

    def start_mode(self, mode):
        self.jouer_son_clic()
        self.mode_jeu = mode
        
        # Reset : On affiche tout par défaut
        self.view.containers["X"].show()
        self.view.containers["O"].show()

        if mode == "IA":
            # Mode JOUEUR (X) vs NAYLA (O)
            self.view.label_titre_section.setText("DÉFI CONTRE QUEEN NAYLA")
            # On cache le bloc O car Nayla est fixe
            self.view.containers["O"].hide()
            self.model.pseudos["O"] = "Queen Nayla (AI)"
            self.ouvrir_config_pseudos()

        elif mode == "IA_VS_IA":
            # On charge les noms d'IA et on affiche la page de sélection
            ai_names = self.charger_ai_names()
            for p in ["X", "O"]: self.view.ia_selectors[p].clear(); self.view.ia_selectors[p].addItems(ai_names)
            self.view.stack.setCurrentIndex(3) # Page IA Selection

        else: # Mode HUMAIN
            self.view.label_titre_section.setText("MATCH ENTRE AMIS")
            self.ouvrir_config_pseudos()

    def ouvrir_config_pseudos(self):
        noms = self.model.charger_pseudos_fichier()
        for p in ["X", "O"]:
            c, l, ch, _ = self.view.inputs[p]; c.clear(); c.addItems(noms); l.clear(); ch.setChecked(False)
        self.view.stack.setCurrentIndex(1)

    def charger_ai_names(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_names.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f: return [l.strip() for l in f.readlines() if l.strip()]
        return ["IA 1", "IA 2"]

    def valider_ia_vs_ia(self):
        self.model.pseudos = {"X": self.view.ia_selectors["X"].currentText(), "O": self.view.ia_selectors["O"].currentText()}
        self.lancer_partie_generique()

    def valider_et_lancer(self):
        self.jouer_son_clic()
        for p in ["X", "O"]:
            # Si c'est l'IA, on ne touche pas à son nom
            if (self.mode_jeu == "IA" and p == "O") or (self.mode_jeu == "IA_VS_IA"):
                continue
            
            c, l, ch, _ = self.view.inputs[p]
            nom = l.text().strip() or c.currentText() or f"Joueur {p}"
            self.model.pseudos[p] = nom
            if ch.isChecked() and l.text().strip(): self.model.sauver_pseudo_fichier(nom)
        
        self.lancer_partie_generique()

    def lancer_partie_generique(self):
        self.jouer_son_clic()
        # SÉCURITÉ : On nettoie le plateau et les boutons avant de commencer
        self.model.reset_plateau()
        for b in self.view.boutons: 
            b.setText(""); b.setStyleSheet("background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50;")
            
        self.model.scores = {"X": 0, "O": 0}
        self.prochain_starter = None # Reset pour faire un pile ou face au début
        self.mettre_a_jour_affichage()
        self.view.stack.setCurrentIndex(2)
        self.lancer_pile_ou_face()

    def lancer_pile_ou_face(self):
        self.en_animation = True
        self.view.label_annonce.setText("Qui va commencer ?")
        # On attend un peu pour que le joueur lise
        QTimer.singleShot(1200, self.start_coin_toss_animation)

    def start_coin_toss_animation(self):
        self.view.label_annonce.setText("🎲...")
        self.anim_timer = QTimer()
        self.anim_steps = 0
        self.anim_timer.timeout.connect(self.anim_tick)
        self.anim_timer.start(100) # Interval de base

    def anim_tick(self):
        # SÉCURITÉ : Si on a quitté la page de jeu, on coupe l'animation
        if self.view.stack.currentIndex() != 2:
            self.anim_timer.stop()
            return

        self.anim_steps += 1
        
        # Ralentissement progressif
        if self.anim_steps > 20: self.anim_timer.setInterval(400)
        elif self.anim_steps > 15: self.anim_timer.setInterval(250)
        elif self.anim_steps > 10: self.anim_timer.setInterval(150)

        t = "X" if self.anim_steps % 2 == 0 else "O"
        pseudo = self.model.pseudos.get(t, t)
        self.view.label_annonce.setText(f"🎲 {pseudo}...")
        
        if self.anim_steps > 22: # Fin de l'animation
            self.anim_timer.stop()
            winner = self.prochain_starter if self.prochain_starter else random.choice(["X", "O"])
            self.model.joueur_actuel = winner
            winner_pseudo = self.model.pseudos[winner]
            self.view.label_annonce.setText(f"▶️ {winner_pseudo} commence !")
            self.mettre_a_jour_affichage()
            QTimer.singleShot(2000, self.fin_anim_pile_face) # Laisse le temps de lire

    def fin_anim_pile_face(self):
        self.view.label_annonce.setText("")
        self.en_animation = False
        if (self.mode_jeu == "IA" and self.model.joueur_actuel == "O") or self.mode_jeu == "IA_VS_IA":
            self.ia_move()

    def clic_bouton(self, i):
        if self.en_animation: return # On bloque si ça tourne
        # SÉCURITÉ : Si on n'est pas sur la page de jeu, on ne fait rien (bloque les clics fantômes IA)
        if self.view.stack.currentIndex() != 2: return

        m, v = self.model, self.view
        if m.plateau[i] == "" and v.label_annonce.text() == "":
            m.plateau[i] = m.joueur_actuel
            c = "#E74C3C" if m.joueur_actuel == "X" else "#3498DB"
            v.boutons[i].setText(m.joueur_actuel)
            v.boutons[i].setStyleSheet(f"background-color: #34495E; color: {c}; border-radius: 20px; border: 3px solid {c};")
            
            if m.verifier_victoire(): self.fin_manche("VICTOIRE")
            elif "" not in m.plateau: self.fin_manche("NUL")
            else:
                m.joueur_actuel = "O" if m.joueur_actuel == "X" else "X"
                self.mettre_a_jour_affichage()
                if (self.mode_jeu == "IA" and m.joueur_actuel == "O") or self.mode_jeu == "IA_VS_IA":
                    QTimer.singleShot(700, self.ia_move)

    def ia_move(self):
        # SÉCURITÉ : Si on a quitté la partie, l'IA ne doit plus jouer
        if self.view.stack.currentIndex() != 2: return

        if self.view.label_annonce.text() != "": return
        m = self.model
        ia, adv = m.joueur_actuel, ("X" if m.joueur_actuel == "O" else "O")
        pos = m.get_possibilities()
        if not pos: return
        for p in pos:
            if m.simuler_victoire(p, ia): self.clic_bouton(p); return
        for p in pos:
            if m.simuler_victoire(p, adv): self.clic_bouton(p); return
        self.clic_bouton(4 if 4 in pos else random.choice(pos))

    def fin_manche(self, res):
        m, v = self.model, self.view
        if res == "VICTOIRE": 
            m.scores[m.joueur_actuel] += 3; msg = f"🏆 {m.pseudos[m.joueur_actuel]} GAGNE !"
            self.prochain_starter = m.joueur_actuel # Le gagnant commence
            self.jouer_son_victoire()
        else: 
            m.scores["X"] += 1; m.scores["O"] += 1; msg = "🤝 MATCH NUL !"
            self.prochain_starter = random.choice(["X", "O"]) # Random si nul
        v.label_annonce.setText(msg)
        QTimer.singleShot(2500, self.reset_manche)

    def reset_manche(self):
        self.model.reset_plateau(); self.view.label_annonce.setText("")
        for b in self.view.boutons: b.setText(""); b.setStyleSheet("background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50;")
        
        # On relance le pile ou face (qui utilisera self.prochain_starter)
        self.lancer_pile_ou_face()

    def mettre_a_jour_affichage(self):
        for p in ["X", "O"]: self.view.cards[p].setText(f"{self.model.pseudos[p]}\n{self.model.scores[p]} pts")
        self.view.label_info.setText(f"Tour de : {self.model.pseudos[self.model.joueur_actuel]}")

    def music_on_off(self):
        p = self.players["musique"][0]; self.jouer_son_clic()
        if p.playbackState() == QMediaPlayer.PlaybackState.PlayingState: p.pause(); self.view.btn_musique.setText("MUSIQUE : OFF"); self.view.update_music_button_style(False)
        else: p.play(); self.view.btn_musique.setText("MUSIQUE : ON"); self.view.update_music_button_style(True)

    def suppr_pseudo(self, player_symbol):
        self.jouer_son_clic()
        combo = self.view.inputs[player_symbol][0]
        p = combo.currentText()
        try:
            if p and not p.startswith("Joueur") and "IA" not in p:
                if QMessageBox.question(self.view, "Suppression", f"Supprimer '{p}' définitivement ?") == QMessageBox.StandardButton.Yes:
                    self.model.supprimer_pseudo_fichier(p)
                    self.ouvrir_config_pseudos()
        except Exception as e:
            print(f"Erreur lors de la suppression : {e}")

    def quitter_match(self):
        self.jouer_son_clic()
        if QMessageBox.question(self.view, "Menu", "Quitter le match ?") == QMessageBox.StandardButton.Yes:
            self.model.reset_plateau(); self.view.label_annonce.setText("")
            for b in self.view.boutons: b.setText(""); b.setStyleSheet("background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50;")
            self.view.stack.setCurrentIndex(0)
