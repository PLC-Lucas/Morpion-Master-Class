from PyQt6.QtWidgets import (QWidget, QGridLayout, QPushButton, QMessageBox, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QStackedWidget, 
                             QCheckBox, QStackedLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .animated_background import AnimatedBackground

class MorpionView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = None 
        self.setWindowTitle("Morpion Master Class")
        self.setMinimumSize(600, 900)
        self.setStyleSheet("background-color: #2C3E50;") # Fond statique par défaut

        self.style_combo_dark = """
            QComboBox {
                background-color: #34495E; color: #ECF0F1; border: 1px solid #7F8C8D;
                border-radius: 5px; padding: 10px; font-size: 16px;
            }
            QComboBox:hover { border: 1px solid #95A5A6; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #34495E; color: #ECF0F1;
                selection-background-color: #3498DB; border: 1px solid #7F8C8D;
            }
        """

        self.boutons = []
        self.inputs = {} 
        self.cards = {} 
        self.containers = {} # NOUVEAU : Pour stocker les blocs Joueur X et Joueur O
        self.ia_selectors = {} # Pour les combobox de sélection d'IA

        self.stack = QStackedWidget(self)
        self.stack.setStyleSheet("background: transparent;") # Rendre le stack transparent

        self.page_menu = QWidget()
        self.page_pseudos = QWidget()
        self.page_jeu = QWidget()
        self.page_ia_selection = QWidget() # Nouvelle page

        # Rendre les pages transparentes pour voir le fond animé
        for page in [self.page_menu, self.page_pseudos, self.page_jeu, self.page_ia_selection]:
            page.setStyleSheet("background: transparent;")

        self.setup_menu()
        self.setup_config_pseudos()
        self.setup_ia_selection()
        self.setup_grille_jeu()

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_pseudos)
        self.stack.addWidget(self.page_jeu)
        self.stack.addWidget(self.page_ia_selection)
        
        self.stack.currentChanged.connect(self.gerer_visibilite_fond)

        self.animated_bg = AnimatedBackground(self)
        self.animated_bg.lower() # On force le fond à aller tout derrière

        layout_principal = QStackedLayout(self)
        layout_principal.setStackingMode(QStackedLayout.StackingMode.StackAll)
        layout_principal.addWidget(self.animated_bg)
        layout_principal.addWidget(self.stack)
        self.stack.raise_() # On force l'interface à venir tout devant

    def gerer_visibilite_fond(self, index):
        # Affiche le fond animé UNIQUEMENT sur la page 0 (Menu)
        self.animated_bg.setVisible(index == 0)

    def set_controller(self, controller):
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
        
        style_bleu = """QPushButton { background-color: #3498DB; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 15px; margin: 10px; } QPushButton:hover { background-color: #2980B9; }"""
        
        self.btn_ia_vs_player = QPushButton("JOUER CONTRE L'IA")
        self.btn_ia_vs_player.setStyleSheet(style_bleu)
        self.btn_ia_vs_ia = QPushButton("IA VS IA")
        self.btn_ia_vs_ia.setStyleSheet(style_bleu)
        self.btn_humain = QPushButton("JOUER CONTRE UN AMI")
        self.btn_humain.setStyleSheet(style_bleu)
        self.btn_musique = QPushButton("MUSIQUE : ON")
        self.update_music_button_style(True)
        self.btn_quitter = QPushButton("QUITTER LE JEU")
        self.btn_quitter.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 15px; margin: 10px; } QPushButton:hover { background-color: #C0392B; }")

        layout.addWidget(titre)
        layout.addWidget(self.btn_ia_vs_player)
        layout.addWidget(self.btn_ia_vs_ia)
        layout.addWidget(self.btn_humain)
        layout.addWidget(self.btn_musique)
        layout.addWidget(self.btn_quitter)

    def setup_config_pseudos(self):
        # On utilise width=450 pour avoir de la place
        layout = self.center_content(self.page_pseudos, width=450)

        # --- TITRE DE SECTION DYNAMIQUE ---
        self.label_titre_section = QLabel("RÉGLAGES")
        self.label_titre_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titre_section.setStyleSheet("color: #F1C40F; font-size: 28px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(self.label_titre_section)

        style_in = "background-color: #ECF0F1; color: #2C3E50; border-radius: 5px; padding: 12px; font-size: 16px;"

        # --- BOUCLE DE CRÉATION DES BLOCS JOUEURS ---
        for p, color in [("X", "#E74C3C"), ("O", "#3498DB")]:
            # Conteneur individuel pour chaque joueur (pour pouvoir le cacher)
            container = QWidget()
            v_layout = QVBoxLayout(container)
            v_layout.setContentsMargins(0, 10, 0, 10) # Un peu d'espacement

            v_layout.addWidget(QLabel(f"JOUEUR {p} :", styleSheet=f"color: {color}; font-weight: bold; font-size: 16px;"))
            
            combo_layout = QHBoxLayout()
            combo = QComboBox()
            combo.setStyleSheet(self.style_combo_dark)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedWidth(45)
            btn_del.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; padding: 8px; border-radius: 5px; } QPushButton:hover { background-color: #C0392B; }")
            combo_layout.addWidget(combo)
            combo_layout.addWidget(btn_del)
            v_layout.addLayout(combo_layout)

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
            v_layout.addLayout(input_line_layout)
            
            check = QCheckBox("Enregistrer ce pseudo", styleSheet="color: white;")
            v_layout.addWidget(check)

            # Stockage
            self.inputs[p] = (combo, line, check, btn_del)
            self.containers[p] = container # On garde la ref du conteneur
            
            layout.addWidget(container) # On ajoute le conteneur au layout principal

        layout.addSpacing(20)
        self.btn_start = QPushButton("LANCER LE MATCH")
        self.btn_start.setStyleSheet("QPushButton { background-color: #27AE60; color: white; font-size: 18px; font-weight: bold; padding: 15px; border-radius: 10px; } QPushButton:hover { background-color: #219150; }")
        self.btn_retour = QPushButton("RETOUR")
        self.btn_retour.setStyleSheet("QPushButton { background-color: #7F8C8D; color: white; padding: 10px; border-radius: 10px; } QPushButton:hover { background-color: #636E72; }")

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_retour)

    def setup_ia_selection(self):
        layout = self.center_content(self.page_ia_selection, width=450)
        
        titre = QLabel("COMBAT D'IA")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre.setStyleSheet("color: #F1C40F; font-size: 28px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(titre)

        for p, color in [("X", "#E74C3C"), ("O", "#3498DB")]:
            layout.addWidget(QLabel(f"CHOISIR L'IA {p} :", styleSheet=f"color: {color}; font-weight: bold; font-size: 16px;"))
            combo = QComboBox()
            combo.setStyleSheet(self.style_combo_dark)
            self.ia_selectors[p] = combo
            layout.addWidget(combo)
            layout.addSpacing(15)

        self.btn_lancer_ia = QPushButton("FIGHT !")
        self.btn_lancer_ia.setStyleSheet("QPushButton { background-color: #8E44AD; color: white; font-size: 22px; font-weight: bold; padding: 20px; border-radius: 15px; margin-top: 20px; } QPushButton:hover { background-color: #9B59B6; }")
        layout.addWidget(self.btn_lancer_ia)

        self.btn_retour_ia = QPushButton("RETOUR AU MENU")
        self.btn_retour_ia.setStyleSheet("QPushButton { background-color: #7F8C8D; color: white; padding: 10px; border-radius: 10px; margin-top: 10px; } QPushButton:hover { background-color: #636E72; }")
        layout.addWidget(self.btn_retour_ia)

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
        for i in range(9):
            btn = QPushButton("")
            btn.setFixedSize(140, 140)
            btn.setFont(QFont('Arial', 45, QFont.Weight.Bold))
            btn.setStyleSheet("QPushButton { background-color: #34495E; color: white; border-radius: 20px; border: 3px solid #2C3E50; }")
            grille.addWidget(btn, i // 3, i % 3)
            self.boutons.append(btn)
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
        if self.controller: self.controller.jouer_son_clic()
        if QMessageBox.question(self, "QUITTER", "Es-tu sûr de vouloir fermer le jeu ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
