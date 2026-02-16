import os, random
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QMessageBox

class MorpionController:
    def __init__(self, model, view):
        self.model, self.view = model, view
        self.mode_jeu = "HUMAIN" # "HUMAIN", "IA", "IA_VS_IA"
        self.players = {}
        for n, v in [("musique", 0.4), ("clic", 0.8), ("victoire", 1.0)]: self.init_audio(n, v)
        self.jouer_musique_fond()
        self.connect_signals()

    def init_audio(self, name, vol):
        p = QMediaPlayer(); o = QAudioOutput(); p.setAudioOutput(o); o.setVolume(vol)
        self.players[name] = (p, o)

    def play_sound(self, cat, file):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
        if os.path.exists(path): self.players[cat][0].setSource(QUrl.fromLocalFile(path)); self.players[cat][0].play()

    def jouer_musique_fond(self): 
        self.play_sound("musique", "Audio/City of Gamers - ChillGamingStudying Lofi Hip Hop Mix - (1 hour).mp3")
        self.players["musique"][0].setLoops(-1)

    def jouer_son_clic(self): self.play_sound("clic", "Audio/Snes_pop.ogg.mp3")
    def jouer_son_victoire(self): self.play_sound("victoire", "Audio/gaining-experience-minecraft-sound-fx.wav")

    def connect_signals(self):
        v = self.view
        v.btn_humain.clicked.connect(lambda: self.start_mode("HUMAIN"))
        v.btn_ia_vs_player.clicked.connect(lambda: self.start_mode("IA"))
        v.btn_ia_vs_ia.clicked.connect(lambda: self.start_mode("IA_VS_IA"))
        v.btn_quitter.clicked.connect(v.close)
        v.btn_musique.clicked.connect(self.music_on_off)
        v.btn_start.clicked.connect(self.valider_et_lancer)
        v.btn_retour.clicked.connect(lambda: v.stack.setCurrentIndex(0))
        v.btn_menu.clicked.connect(self.quitter_match)
        for i in range(9): v.boutons[i].clicked.connect(lambda _, x=i: self.clic_bouton(x))
        for p in ["X", "O"]: v.inputs[p][3].clicked.connect(lambda _, c=v.inputs[p][0]: self.suppr_pseudo(c))

    def start_mode(self, mode):
        self.jouer_son_clic(); self.mode_jeu = mode
        if mode == "IA_VS_IA": 
            self.model.pseudos = {"X": "Hugo (IA)", "O": "Nayla (IA)"}
            self.valider_et_lancer()
        else:
            if mode == "IA": self.model.pseudos["O"] = "Nayla (IA)"
            self.ouvrir_config_pseudos()

    def ouvrir_config_pseudos(self):
        noms = self.model.charger_pseudos_fichier()
        for p in ["X", "O"]:
            c, l, ch, _ = self.view.inputs[p]; c.clear(); c.addItems(noms); l.clear(); ch.setChecked(False)
        self.view.stack.setCurrentIndex(1)

    def valider_et_lancer(self):
        for p in ["X", "O"]:
            if self.mode_jeu == "IA" and p == "O": continue
            c, l, ch, _ = self.view.inputs[p]
            nom = l.text().strip() or c.currentText() or f"Joueur {p}"
            self.model.pseudos[p] = nom
            if ch.isChecked() and l.text().strip(): self.model.sauver_pseudo_fichier(nom)
        self.model.scores = {"X": 0, "O": 0}; self.mettre_a_jour_affichage(); self.view.stack.setCurrentIndex(2)
        if self.mode_jeu == "IA_VS_IA": QTimer.singleShot(1000, self.ia_move)

    def clic_bouton(self, i):
        m, v = self.model, self.view
        if m.plateau[i] == "" and v.label_annonce.text() == "":
            m.plateau[i] = m.joueur_actuel
            c = "#E74C3C" if m.joueur_actuel == "X" else "#3498DB"
            v.boutons[i].setText(m.joueur_actuel)
            v.boutons[i].setStyleSheet(f"background-color: #34495E; color: {c}; border-radius: 20px; border: 3px solid {c};")
            
            if m.verifier_victoire(): self.fin_manche("VICTOIRE")
            elif "" not in m.plateau: self.fin_manche("NUL")
            else:
                m.joueur_actuel = "O" if m.joueur_actuel == "X" else "X"; self.mettre_a_jour_affichage()
                if (self.mode_jeu == "IA" and m.joueur_actuel == "O") or self.mode_jeu == "IA_VS_IA":
                    QTimer.singleShot(700, self.ia_move)

    def fin_manche(self, res):
        if res == "VICTOIRE": self.model.scores[self.model.joueur_actuel] += 3; msg = f"🏆 {self.model.pseudos[self.model.joueur_actuel]} GAGNE !"
        else: self.model.scores["X"] += 1; self.model.scores["O"] += 1; msg = "🤝 MATCH NUL !"
        self.view.label_annonce.setText(msg)
        if res == "VICTOIRE": self.jouer_son_victoire()
        QTimer.singleShot(2500, self.reset_match)

    def ia_move(self):
        """ Logique IA (Nayla/Hugo) + Optimisation (Rayan/Lucas) """
        if self.view.label_annonce.text() != "": return
        m, ia, adv = self.model, self.model.joueur_actuel, ("X" if self.model.joueur_actuel == "O" else "O")
        pos = m.get_possibilities()
        if not pos: return
        for p in pos:
            if m.simuler_victoire(p, ia): self.clic_bouton(p); return
        for p in pos:
            if m.simuler_victoire(p, adv): self.clic_bouton(p); return
        self.clic_bouton(4 if 4 in pos else random.choice(pos))

    def reset_match(self):
        self.model.reset_plateau(); self.view.label_annonce.setText("")
        for b in self.view.boutons: b.setText(""); b.setStyleSheet("background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50;")
        self.mettre_a_jour_affichage()
        if self.mode_jeu == "IA_VS_IA": QTimer.singleShot(800, self.ia_move)

    def mettre_a_jour_affichage(self):
        for p in ["X", "O"]: self.view.cards[p].setText(f"{self.model.pseudos[p]}\n{self.model.scores[p]} pts")
        self.view.label_info.setText(f"Tour de : {self.model.pseudos[self.model.joueur_actuel]}")

    def music_on_off(self):
        p = self.players["musique"][0]; self.jouer_son_clic()
        if p.playbackState() == QMediaPlayer.PlaybackState.PlayingState: p.pause(); self.view.btn_musique.setText("MUSIQUE : OFF"); self.view.update_music_button_style(False)
        else: p.play(); self.view.btn_musique.setText("MUSIQUE : ON"); self.view.update_music_button_style(True)

    def suppr_pseudo(self, c):
        p = c.currentText()
        if p and not p.startswith("Joueur") and "IA" not in p:
            if QMessageBox.question(self.view, "S", f"Suppr {p}?") == QMessageBox.StandardButton.Yes: self.model.supprimer_pseudo_fichier(p); self.ouvrir_config_pseudos()

    def quitter_match(self): self.jouer_son_clic(); self.reset_match(); self.view.stack.setCurrentIndex(0)
