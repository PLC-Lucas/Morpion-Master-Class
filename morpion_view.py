from PyQt6.QtWidgets import (QWidget, QGridLayout, QPushButton, QMessageBox, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QStackedWidget, 
                             QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MorpionView(QWidget):
    def __init__(self):
        """
        Gère l'affichage uniquement.
        """
        super().__init__()
        self.controller = None  # Référence vers le contrôleur
        
        self.setWindowTitle("Morpion Master Class")
        self.setMinimumSize(600, 900)
        self.setStyleSheet("background-color: #2C3E50;")

        # --- ÉLÉMENTS GRAPHIQUES ---
        self.boutons = [] # Liste des 9 boutons du jeu
        self.inputs = {}  # Pour stocker les champs textes des pseudos
        self.cards = {}   # Pour l'affichage des scores

        self.stack = QStackedWidget(self)
        
        # Création des pages
        self.page_menu = QWidget()
        self.page_pseudos = QWidget()
        self.page_jeu = QWidget()

        # Appel des setups (copiés de ton code)
        self.setup_menu()
        self.setup_config_pseudos()
        self.setup_grille_jeu()

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_pseudos)
        self.stack.addWidget(self.page_jeu)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.stack)

    def set_controller(self, controller):
        """Permet à la vue d'appeler le contrôleur (pour le son de fermeture)."""
        self.controller = controller

    def center_content(self, page, width=450):
        container = QWidget(); container.setFixedWidth(width)
        layout_v = QVBoxLayout(container)
        layout_h = QHBoxLayout()
        layout_h.addStretch(); layout_h.addWidget(container); layout_h.addStretch()
        page_layout = QVBoxLayout(page)
        page_layout.addStretch(); page_layout.addLayout(layout_h); page_layout.addStretch()
        return layout_v

    def setup_menu(self):
        layout = self.center_content(self.page_menu)
        
        titre = QLabel("MORPION\nMASTER CLASS")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre.setStyleSheet("color: #F1C40F; font-size: 50px; font-weight: bold; margin-bottom: 50px;")
        
        style_bleu = """
            QPushButton { background-color: #3498DB; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 15px; margin: 10px; }
            QPushButton:hover { background-color: #2980B9; }
        """
        
        self.btn_ia_vs_player = QPushButton("JOUER CONTRE L'IA")
        self.btn_ia_vs_player.setStyleSheet(style_bleu)
            
        self.btn_ia_vs_ia = QPushButton("IA VS IA")
        self.btn_ia_vs_ia.setStyleSheet(style_bleu)
        
        self.btn_humain = QPushButton("JOUER CONTRE UN AMI")
        self.btn_humain.setStyleSheet(style_bleu)
        
        self.btn_musique = QPushButton("MUSIQUE : ON")
        # On initialise le style par défaut
        self.update_music_button_style(True)
        
        self.btn_quitter = QPushButton("QUITTER LE JEU")
        self.btn_quitter.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 15px; margin: 10px; }
            QPushButton:hover { background-color: #C0392B; }
        """)

        layout.addWidget(titre)
        layout.addWidget(self.btn_ia_vs_player)
        layout.addWidget(self.btn_ia_vs_ia)
        layout.addWidget(self.btn_humain)
        layout.addWidget(self.btn_musique)
        layout.addWidget(self.btn_quitter)

    def setup_config_pseudos(self):
        layout = self.center_content(self.page_pseudos, width=400)
        style_in = "background-color: #ECF0F1; color: #2C3E50; border-radius: 5px; padding: 12px; font-size: 16px;"

        layout.addWidget(QLabel("RÉGLAGES DES JOUEURS", styleSheet="color: white; font-size: 26px; font-weight: bold; margin-bottom: 20px;"))

        for p, color in [("X", "#E74C3C"), ("O", "#3498DB")]:
            layout.addWidget(QLabel(f"JOUEUR {p} :", styleSheet=f"color: {color}; font-weight: bold; font-size: 16px;"))
            
            combo_layout = QHBoxLayout()
            combo = QComboBox()
            combo.setStyleSheet(style_in)
            
            btn_del = QPushButton("🗑️")
            btn_del.setFixedWidth(45)
            btn_del.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; padding: 8px; border-radius: 5px; } QPushButton:hover { background-color: #C0392B; }")
            
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
            
            # Connexion locale pour l'UI pure (compteur de caractères)
            line.textChanged.connect(lambda text, l=lbl_count: self.update_char_count(text, l))
            
            input_line_layout.addWidget(line)
            input_line_layout.addWidget(lbl_count)
            layout.addLayout(input_line_layout)
            
            check = QCheckBox("Enregistrer ce pseudo", styleSheet="color: white;")
            layout.addWidget(check)
            layout.addSpacing(15)
            
            # On stocke tout dans self.inputs pour le controller
            # Structure : self.inputs["X"] = (combo, line, check, btn_del)
            self.inputs[p] = (combo, line, check, btn_del)

        self.btn_start = QPushButton("LANCER LE MATCH")
        self.btn_start.setStyleSheet("QPushButton { background-color: #27AE60; color: white; font-size: 18px; font-weight: bold; padding: 15px; border-radius: 10px; } QPushButton:hover { background-color: #219150; }")
        
        self.btn_retour = QPushButton("RETOUR")
        self.btn_retour.setStyleSheet("QPushButton { background-color: #7F8C8D; color: white; padding: 10px; border-radius: 10px; } QPushButton:hover { background-color: #636E72; }")

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_retour)

    def setup_grille_jeu(self):
        layout = self.center_content(self.page_jeu, width=600)
        score_layout = QHBoxLayout()
        
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
        # CRUCIAL : On remplit la liste self.boutons ICI
        for i in range(9):
            btn = QPushButton("")
            btn.setFixedSize(140, 140)
            btn.setFont(QFont('Arial', 45, QFont.Weight.Bold))
            btn.setStyleSheet("QPushButton { background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50; }")
            grille.addWidget(btn, i // 3, i % 3)
            self.boutons.append(btn) # IMPORTANT
            
        layout.addLayout(grille)

        self.btn_menu = QPushButton("RETOURNER AU MENU")
        self.btn_menu.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-weight: bold; padding: 15px; border-radius: 10px; margin-top: 30px; } QPushButton:hover { background-color: #C0392B; }")
        layout.addWidget(self.btn_menu)

        self.label_annonce = QLabel("")
        self.label_annonce.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_annonce.setMinimumHeight(80)
        self.label_annonce.setStyleSheet("color: #F1C40F; font-size: 26px; font-weight: bold;")
        layout.addWidget(self.label_annonce)

    def update_music_button_style(self, is_on):
        color = "#F1C40F" if is_on else "#95A5A6" 
        hover = "#D4AC0D" if is_on else "#7F8C8D"
        self.btn_musique.setStyleSheet(f"QPushButton {{ background-color: {color}; color: #2C3E50; font-size: 18px; font-weight: bold; padding: 15px; border-radius: 15px; margin: 10px; }} QPushButton:hover {{ background-color: {hover}; }}")

    def update_char_count(self, text, label):
        count = len(text)
        label.setText(f"{count}/15" if count > 0 else "")

    def closeEvent(self, event):
        """Gère la fermeture avec la croix rouge."""
        if self.controller:
            self.controller.jouer_son_clic()
            
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