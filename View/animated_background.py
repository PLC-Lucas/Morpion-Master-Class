import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPainterPath
from PyQt6.QtCore import QTimer, Qt

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 900)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Laisse passer les clics
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)  # Environ 30 images par seconde

        self.time = 0
        # On définit nos vagues : (couleur, amplitude, fréquence, vitesse)
        # J'ai repris les couleurs de ton interface pour que ça matche bien
        self.waves = [
            {'color': QColor(142, 68, 173, 40), 'amplitude': 60, 'frequency': 0.008, 'speed': 0.015}, # Violet Deep
            {'color': QColor(233, 30, 99, 30), 'amplitude': 70, 'frequency': 0.006, 'speed': 0.02},   # Rose Pink
            {'color': QColor(52, 152, 219, 30), 'amplitude': 50, 'frequency': 0.01, 'speed': 0.01}    # Bleu Cyan
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Le fond de base, bien sombre
        painter.fillRect(self.rect(), QColor("#2C3E50"))

        for wave in self.waves:
            path = QPainterPath()
            path.moveTo(0, self.height())
            for x in range(self.width() + 1):
                y = self.height() / 1.8 + wave['amplitude'] * math.sin(x * wave['frequency'] + self.time * wave['speed'])
                path.lineTo(x, y)
            path.lineTo(self.width(), self.height())
            path.closeSubpath()
            
            painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(wave['color']); painter.drawPath(path)

    def update_animation(self):
        self.time += 1
        self.update() # Demande à redessiner le widget