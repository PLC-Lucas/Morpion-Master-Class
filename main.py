import sys
from PyQt6.QtWidgets import QApplication
from Model.morpion_model import MorpionModel
from View.morpion_view import MorpionView
from Controller.morpion_controller import MorpionController

def main():
    app = QApplication(sys.argv)
    
    # Instanciation MVC
    model = MorpionModel()
    view = MorpionView()
    
    # On donne tout au contrôleur
    controller = MorpionController(model, view)
    
    # On connecte la vue au contrôleur (pour le closeEvent)
    view.set_controller(controller)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
