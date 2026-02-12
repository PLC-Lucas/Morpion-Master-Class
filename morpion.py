import sys
import os
from PyQt6.QtWidgets import (QWidget, QGridLayout, QPushButton, QMessageBox, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QStackedWidget, 
                             QCheckBox, QApplication)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class MorpionPyQt(QWidget):
    def __init__(self):
        """
        Docstring for __init__
        
        :param self: Description
        """
        super().__init__()
        # --- DONNÉES DE JEU ---
        self.joueur_actuel = "X"
        self.pseudos = {"X": "Joueur X", "O": "Joueur O"}
        self.scores = {"X": 0, "O": 0}
        self.plateau = [""] * 9
        self.boutons = []

        # --- SYSTÈME AUDIO ---
        self.players = {}
        self.init_audio("musique", 0.4)
        self.init_audio("clic", 0.8)
        self.init_audio("victoire", 1.0)
        
        self.jouer_musique_fond()

        # --- INTERFACE ---
        self.stack = QStackedWidget(self) # Permet de switcher entre les pages (menu, config pseudos, jeu)
        self.initUI()

    def init_audio(self, name, volume):
        """
        Docstring for init_audio
        
        :param self: Description
        :param name: Description
        :param volume: Description
        """
        player = QMediaPlayer()
        output = QAudioOutput()
        player.setAudioOutput(output)
        output.setVolume(volume)
        self.players[name] = (player, output) # stocke les players dans un dict pour les réutiliser facilement

    def initUI(self):
        """
        Docstring for initUI
        
        :param self: Description
        """
        self.setWindowTitle("Morpion Master Class")
        self.setMinimumSize(600, 900)
        self.setStyleSheet("background-color: #2C3E50;")

        self.page_menu = QWidget()
        self.page_pseudos = QWidget()
        self.page_jeu = QWidget()

        self.setup_menu()            # Page 0
        self.setup_config_pseudos()  # Page 1
        self.setup_grille_jeu()      # Page 2

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_pseudos)
        self.stack.addWidget(self.page_jeu)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.stack)

    def setup_menu(self):
        """
        Docstring for setup_menu
        
        :param self: Description
        """
        layout = self.center_content(self.page_menu)
        
        titre = QLabel("MORPION\nMASTER CLASS")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre.setStyleSheet("color: #F1C40F; font-size: 50px; font-weight: bold; margin-bottom: 50px;")
        
        style_bleu = """
            QPushButton { background-color: #3498DB; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 15px; margin: 10px; }
            QPushButton:hover { background-color: #2980B9; }
        """
        
        btn_ia_vs_player = QPushButton("JOUER CONTRE L'IA")
        btn_ia_vs_player.setStyleSheet(style_bleu)
        btn_ia_vs_player.clicked.connect(lambda: (self.jouer_son_clic(), QMessageBox.information(self, "IA", "L'IA arrive bientôt !")))
            
        btn_ia_vs_ia = QPushButton("IA VS IA")
        btn_ia_vs_ia.setStyleSheet(style_bleu)
        btn_ia_vs_ia.clicked.connect(lambda: (self.jouer_son_clic(), QMessageBox.information(self, "IA", "L'IA contre l'IA arrive  également bientôt !")))
        
        btn_humain = QPushButton("JOUER CONTRE UN AMI")
        btn_humain.setStyleSheet(style_bleu)
        btn_humain.clicked.connect(self.ouvrir_config_pseudos)
        
        self.btn_musique = QPushButton("MUSIQUE : ON")
        self.update_music_button_style(True)
        self.btn_musique.clicked.connect(self.music_on_off)
        
        btn_quitter = QPushButton("QUITTER LE JEU")
        btn_quitter.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 15px; margin: 10px; }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_quitter.clicked.connect(self.close)

        layout.addWidget(titre)
        layout.addWidget(btn_ia_vs_player)
        layout.addWidget(btn_ia_vs_ia)
        layout.addWidget(btn_humain)
        layout.addWidget(self.btn_musique)
        layout.addWidget(btn_quitter)

    def setup_config_pseudos(self):
        """
        Docstring for setup_config_pseudos
        
        :param self: Description
        """
        layout = self.center_content(self.page_pseudos, width=400)
        style_in = "background-color: #ECF0F1; color: #2C3E50; border-radius: 5px; padding: 12px; font-size: 16px;"

        layout.addWidget(QLabel("RÉGLAGES DES JOUEURS", styleSheet="color: white; font-size: 26px; font-weight: bold; margin-bottom: 20px;"))

        self.inputs = {}
        for p, color in [("X", "#E74C3C"), ("O", "#3498DB")]:
            layout.addWidget(QLabel(f"JOUEUR {p} :", styleSheet=f"color: {color}; font-weight: bold; font-size: 16px;"))
            
            combo_layout = QHBoxLayout()
            combo = QComboBox()
            combo.setStyleSheet(style_in)
            
            btn_del = QPushButton("🗑️")
            btn_del.setFixedWidth(45)
            btn_del.setStyleSheet("""
                QPushButton { background-color: #E74C3C; color: white; padding: 8px; border-radius: 5px; }
                QPushButton:hover { background-color: #C0392B; }
            """)
            btn_del.clicked.connect(lambda checked, c=combo: self.supprimer_pseudo_selectionne(c))
            
            combo_layout.addWidget(combo)
            combo_layout.addWidget(btn_del)
            layout.addLayout(combo_layout)

            input_line_layout = QHBoxLayout()
            line = QLineEdit()
            line.setPlaceholderText(f"Nouveau pseudo {p}...")
            line.setMaxLength(15)
            line.setStyleSheet(style_in)
            
            lbl_count = QLabel("")
            lbl_count.setStyleSheet("color: #BDC3C7; font-size: 12px; font-weight: bold;")
            lbl_count.setFixedWidth(40)
            line.textChanged.connect(lambda text, l=lbl_count: self.update_char_count(text, l))
            
            input_line_layout.addWidget(line)
            input_line_layout.addWidget(lbl_count)
            layout.addLayout(input_line_layout)
            
            check = QCheckBox("Enregistrer ce pseudo", styleSheet="color: white;")
            layout.addWidget(check)
            layout.addSpacing(15)
            
            self.inputs[p] = (combo, line, check)

        btn_start = QPushButton("LANCER LE MATCH")
        btn_start.setStyleSheet("QPushButton { background-color: #27AE60; color: white; font-size: 18px; font-weight: bold; padding: 15px; border-radius: 10px; } QPushButton:hover { background-color: #219150; }")
        btn_start.clicked.connect(self.valider_et_lancer)
        
        btn_retour = QPushButton("RETOUR")
        btn_retour.setStyleSheet("QPushButton { background-color: #7F8C8D; color: white; padding: 10px; border-radius: 10px; } QPushButton:hover { background-color: #636E72; }")
        btn_retour.clicked.connect(lambda: (self.jouer_son_clic(), self.stack.setCurrentIndex(0)))

        layout.addWidget(btn_start)
        layout.addWidget(btn_retour)

    def setup_grille_jeu(self):
        """
        Docstring for setup_grille_jeu
        
        :param self: Description
        """
        layout = self.center_content(self.page_jeu, width=600)
        score_layout = QHBoxLayout()
        self.cards = {}
        for p in ["X", "O"]:
            lbl = QLabel(f"{p}\n0 pts")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumSize(220, 90)
            lbl.setStyleSheet("background-color: #34495E; color: white; font-size: 18px; font-weight: bold; border-radius: 15px; border: 2px solid #F1C40F;")
            self.cards[p] = lbl
            score_layout.addWidget(lbl)
            if p == "X": score_layout.addStretch()
        layout.addLayout(score_layout)

        self.label_info = QLabel("C'est parti !")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_info.setStyleSheet("color: #ECF0F1; font-size: 24px; margin: 20px;")
        layout.addWidget(self.label_info)

        grille = QGridLayout(); grille.setSpacing(15)
        for i in range(9):
            btn = QPushButton("")
            btn.setFixedSize(140, 140)
            btn.setFont(QFont('Arial', 45, QFont.Weight.Bold))
            btn.setStyleSheet("QPushButton { background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50; }")
            btn.clicked.connect(lambda _, x=i: self.clic_bouton(x))
            grille.addWidget(btn, i // 3, i % 3)
            self.boutons.append(btn)
        layout.addLayout(grille)

        btn_menu = QPushButton("RETOURNER AU MENU")
        btn_menu.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-weight: bold; padding: 15px; border-radius: 10px; margin-top: 30px; } QPushButton:hover { background-color: #C0392B; }")
        btn_menu.clicked.connect(self.quitter_match)
        layout.addWidget(btn_menu)

        self.label_annonce = QLabel("")
        self.label_annonce.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_annonce.setMinimumHeight(80)
        self.label_annonce.setStyleSheet("color: #F1C40F; font-size: 26px; font-weight: bold;")
        layout.addWidget(self.label_annonce)

    # --- LOGIQUE ---
    def music_on_off(self):
        """
        Docstring for music_on_off
        
        :param self: Description
        """
        self.jouer_son_clic()
        p, _ = self.players["musique"]
        if p.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            p.pause()
            self.btn_musique.setText("MUSIQUE : OFF")
            self.update_music_button_style(False)
        else:
            p.play()
            self.btn_musique.setText("MUSIQUE : ON")
            self.update_music_button_style(True)

    def update_music_button_style(self, is_on):
        """
        Docstring for update_music_button_style
        
        :param self: Description
        :param is_on: Description
        """
        color = "#F1C40F" if is_on else "#95A5A6" 
        hover = "#D4AC0D" if is_on else "#7F8C8D"
        self.btn_musique.setStyleSheet(f"QPushButton {{ background-color: {color}; color: #2C3E50; font-size: 18px; font-weight: bold; padding: 15px; border-radius: 15px; margin: 10px; }} QPushButton:hover {{ background-color: {hover}; }}")

    def update_char_count(self, text, label):
        """
        Docstring for update_char_count
        
        :param self: Description
        :param text: Description
        :param label: Description
        """
        count = len(text)
        label.setText(f"{count}/15" if count > 0 else "")

    def center_content(self, page, width=450):
        """
        Docstring for center_content
        
        :param self: Description
        :param page: Description
        :param width: Description
        """
        container = QWidget(); container.setFixedWidth(width)
        layout_v = QVBoxLayout(container)
        layout_h = QHBoxLayout()
        layout_h.addStretch(); layout_h.addWidget(container); layout_h.addStretch()
        page_layout = QVBoxLayout(page)
        page_layout.addStretch(); page_layout.addLayout(layout_h); page_layout.addStretch()
        return layout_v

    # --- LE DOUBLE CHECK EST ICI ---
    def closeEvent(self, event):
        """
        Docstring for closeEvent
        
        :param self: Description
        :param event: Description
        """
        
        """ Déclenché par btn_quitter ou la croix rouge """
        self.jouer_son_clic()
        reponse = QMessageBox.question(
            self, "QUITTER", 
            "Es-tu sûr de vouloir fermer le jeu ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reponse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def clic_bouton(self, index):
        """
        Docstring for clic_bouton
        
        :param self: Description
        :param index: Description
        """
        if self.plateau[index] == "" and self.label_annonce.text() == "":
            self.plateau[index] = self.joueur_actuel
            couleur = "#E74C3C" if self.joueur_actuel == "X" else "#3498DB"
            self.boutons[index].setText(self.joueur_actuel)
            self.boutons[index].setStyleSheet(f"background-color: #34495E; color: {couleur}; border-radius: 20px; border: 3px solid {couleur};")
            if self.verifier_victoire():
                self.scores[self.joueur_actuel] += 3
                self.annoncer_resultat(f"🏆 {self.pseudos[self.joueur_actuel]} GAGNE ! +3 pts", "victoire")
                QTimer.singleShot(2500, self.rejouer_manche)
            elif "" not in self.plateau:
                self.scores["X"] += 1; self.scores["O"] += 1
                self.annoncer_resultat("🤝 MATCH NUL ! +1 pt", "nul")
                QTimer.singleShot(2500, self.rejouer_manche)
            else:
                self.joueur_actuel = "O" if self.joueur_actuel == "X" else "X"
                self.mettre_a_jour_affichage()

    def verifier_victoire(self):
        """
        Docstring for verifier_victoire
        
        :param self: Description
        """
        v = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(self.plateau[a] == self.plateau[b] == self.plateau[c] != "" for a,b,c in v)

    def annoncer_resultat(self, message, son):
        """
        Docstring for annoncer_resultat
        
        :param self: Description
        :param message: Description
        :param son: Description
        """
        self.label_annonce.setText(message)
        if son == "victoire": self.jouer_son_victoire()
        QTimer.singleShot(3500, lambda: self.label_annonce.setText(""))

    def mettre_a_jour_affichage(self):
        for p in ["X", "O"]: self.cards[p].setText(f"{self.pseudos[p]}\n{self.scores[p]} pts")
        self.label_info.setText(f"Tour de : {self.pseudos[self.joueur_actuel]}")

    def rejouer_manche(self):
        self.plateau = [""] * 9
        self.joueur_actuel = "X"
        for b in self.boutons:
            b.setText(""); b.setStyleSheet("background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50;")
        self.mettre_a_jour_affichage()

    def quitter_match(self):
        self.jouer_son_clic()
        self.label_annonce.setText("")
        self.rejouer_manche()
        self.stack.setCurrentIndex(0)

    # --- AUDIO & DATA ---
    def play_sound(self, category, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, filename)
        
        if os.path.exists(path):
            self.players[category][0].setSource(QUrl.fromLocalFile(path))
            self.players[category][0].play()
        else:
            print(f"⚠️ Son introuvable : {filename}")
            print(f"🔍 J'ai cherché ici : {path}")

    def jouer_musique_fond(self):
        self.play_sound("musique", "Audio/City of Gamers - ChillGamingStudying Lofi Hip Hop Mix - (1 hour).mp3")
        self.players["musique"][0].setLoops(QMediaPlayer.Loops.Infinite)

    def jouer_son_clic(self): self.play_sound("clic", "Audio/Snes_pop.ogg.mp3")
    def jouer_son_victoire(self): self.play_sound("victoire", "Audio/gaining-experience-minecraft-sound-fx.wav")

    def charger_pseudos_listes(self):
        if os.path.exists("pseudos.txt"):
            with open("pseudos.txt", "r") as f:
                noms = sorted(list(set(f.read().splitlines())))
                for p in ["X", "O"]:
                    self.inputs[p][0].clear()
                    self.inputs[p][0].addItems(noms)

    def ouvrir_config_pseudos(self):
        self.jouer_son_clic()
        self.charger_pseudos_listes()
        for p in ["X", "O"]:
            _, line, check = self.inputs[p]
            line.clear()
            check.setChecked(False)
        self.stack.setCurrentIndex(1)

    def valider_et_lancer(self):
        self.jouer_son_clic()
        for p in ["X", "O"]:
            combo, line, check = self.inputs[p]
            nom = line.text().strip() or combo.currentText() or f"Joueur {p}"
            self.pseudos[p] = nom
            if check.isChecked() and line.text().strip():
                self.sauver_en_fichier(nom)
        self.scores = {"X": 0, "O": 0}
        self.mettre_a_jour_affichage()
        self.stack.setCurrentIndex(2)

    def sauver_en_fichier(self, nom):
        existants = []
        if os.path.exists("pseudos.txt"):
            with open("pseudos.txt", "r") as f:
                existants = f.read().splitlines()
        if nom not in existants:
            with open("pseudos.txt", "a") as f:
                f.write(nom + "\n")

    def supprimer_pseudo_selectionne(self, combo):
        self.jouer_son_clic()
        pseudo_a_suppr = combo.currentText()
        if not pseudo_a_suppr or pseudo_a_suppr.startswith("Joueur"):
            return

        reponse = QMessageBox.question(self, "SUPPRESSION", f"Supprimer '{pseudo_a_suppr}' de la liste ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reponse == QMessageBox.StandardButton.Yes:
            if os.path.exists("pseudos.txt"):
                with open("pseudos.txt", "r") as f:
                    lignes = f.read().splitlines()
                with open("pseudos.txt", "w") as f:
                    for l in lignes:
                        if l != pseudo_a_suppr: f.write(l + "\n")
                self.charger_pseudos_listes()