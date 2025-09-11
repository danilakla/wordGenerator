# ui/views/notification_message.py
import requests
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from datetime import datetime

class NotificationMessage(QDialog):
    def __init__(self, message: str, updated_at: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Уведомление")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Сообщение
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 🔹 по центру
        layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Дата/время
        try:
            dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            pretty_time = dt.strftime("%d.%m.%Y %H:%M:%S")
        except Exception:
            pretty_time = updated_at

        time_label = QLabel(f"Время создания сообщения: {pretty_time}")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 🔹 тоже по центру
        layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    @staticmethod
    def check_and_show(parent=None):
        """Делает запрос и, если есть сообщение, показывает диалог"""
        try:
            resp = requests.get(
                "https://93.125.104.173:8444/message",
                verify=False,  # -k из curl
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                message = data.get("message")
                updated_at = data.get("updated_at")
                if message and message.strip():
                    dlg = NotificationMessage(message, updated_at, parent)
                    dlg.exec()
        except Exception:
            pass  # молча игнорируем ошибки сети
