from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
import requests, sys, os, hashlib, uuid, platform

SERVER_BASE = "https://93.125.104.173:8444"  # твой реальный бекенд
import hwid_validate



def get_hwid():
    info = hwid_validate.get_hwid()
    return info

def get_exe_hash():
    exe = sys.argv[0]
    with open(exe, "rb") as f:
        p=hashlib.sha256(f.read()).hexdigest()
        return p


class LicenseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Активация продукта")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        self.label = QLabel("Введите лицензионный ключ:")
        layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setPlaceholderText("XXXXX-XXXXX-XXXXX")
        layout.addWidget(self.input)

        self.btn_activate = QPushButton("Активировать")
        self.btn_activate.clicked.connect(self.try_activate)
        layout.addWidget(self.btn_activate)

        self.btn_retry = QPushButton("Повторить проверку")
        self.btn_retry.clicked.connect(self.try_validate)
        layout.addWidget(self.btn_retry)

        self.token_path = os.path.join(os.path.dirname(sys.argv[0]), "license.key")
        self.token = None

    def try_validate(self, checked=False):
        if not os.path.exists(self.token_path):
            QMessageBox.warning(self, "Ошибка", "Файл лицензии не найден.")
            return

        token = open(self.token_path, "r", encoding="utf-8").read().strip()
        hwid = get_hwid()
        exe_hash = get_exe_hash()

        try:
            r = requests.post(f"{SERVER_BASE}/license/validate",
                              json={"token": token, "hwid": hwid, "exe_hash": exe_hash}, timeout=6, verify=False)
            
            if r.ok:
                data = r.json()
                if data.get("ok"):
                    self.token = token
                    self.accept()
                    return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Сервер недоступен: {e}")
            return

        QMessageBox.warning(self, "Ошибка", "Лицензия недействительна.")
    # def _checK_style(self):
    #     token_path = os.path.join(os.path.dirname(sys.argv[0]), "license.key")
    #     if not os.path.exists(token_path):
    #         return False

    #     token = open(token_path, "r", encoding="utf-8").read().strip()
    #     hwid = get_hwid()
    #     exe_hash = get_exe_hash()

    #     try:
    #         r = requests.post(f"{SERVER_BASE}/license/validate",
    #                           json={"token": token, "hwid": hwid, "exe_hash": exe_hash}, timeout=6)
    #         if r.ok:
    #             data = r.json()
    #             if data.get("ok"):
    #                 self.token = token
    #                 self.accept()
    #                 return
    #     except Exception as e:
    #         return False




    def try_activate(self, checked=False):
        user_key = self.input.text().strip()
        if not user_key:
            QMessageBox.warning(self, "Ошибка", "Введите ключ!")
            return

        hwid = get_hwid()
        exe_hash = get_exe_hash()

        try:
            r = requests.post(f"{SERVER_BASE}/license/activate",
                              json={"key": user_key, "hwid": hwid, "exe_hash": exe_hash}, timeout=10, verify=False)
            data = r.json()
            if r.ok and data.get("ok"):
                token = data["token"]
                open(self.token_path, "w", encoding="utf-8").write(token)
                self.token = token
                QMessageBox.information(self, "Успех", "Активация прошла успешно!")
                self.accept()
                return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Сервер недоступен: {e}")
            return

        QMessageBox.warning(self, "Ошибка", "Неверный ключ или сервер отклонил активацию.")
