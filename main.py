import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from morpion import MorpionPyQt

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12))
    jeu = MorpionPyQt()
    jeu.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()