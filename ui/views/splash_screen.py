from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap("resource/assets_task_01k39hhv1few2vap5008w20nee_1755888421_img_0.png"))  # Замените на реальное изображение
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        QTimer.singleShot(3000, self.close)