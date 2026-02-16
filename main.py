import sys
from PyQt6.QtWidgets import QApplication
from Model.morpion_model import MorpionModel
from View.morpion_view import MorpionView
from Controller.morpion_controller import MorpionController

def main():
    app = QApplication(sys.argv)

    model = MorpionModel()
    view = MorpionView()

    controller = MorpionController(model, view)

    view.set_controller(controller)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
