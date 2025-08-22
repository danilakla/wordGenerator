from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap("path/to/splash_image.png"))  # Замените на реальное изображение
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        QTimer.singleShot(3000, self.close)