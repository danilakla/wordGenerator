from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
import requests, sys, os, hashlib, uuid, platform

from util.hwid_validate import get_hwid

SERVER_BASE = "https://93.125.104.173:8444"  # твой реальный бекенд




def get_exe_hash():
    
    exe = sys.argv[0]
    with open(exe, "rb") as f:
        p=hashlib.sha256(f.read()).hexdigest()
        print(p)
        return p


class LicenseDialog(QDialog):
    def __init__(self,service):
        
        super().__init__()
        self.setWindowTitle("Активация продукта")
        self.setMinimumWidth(400)
        self.service=service
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
        
        self.btn_free = QPushButton("Попробовать бесплатно")
        self.btn_free.clicked.connect(self.try_free)
        layout.addWidget(self.btn_free)


        self.token_path = os.path.join(os.path.dirname(sys.argv[0]), "license.key")
        self.token = None
    def try_free(self, checked=False):
        """Метод для пробного периода - просто пропускаем активацию"""
        # Показываем информационное сообщение
        QMessageBox.information(self, "Пробный период", 
                              "Во время бесплатного режима вы можете добавить только 7 элементов.\n"
                              "По достижении лимита программа будет автоматически закрыта,\n"
                              "при этом до достижения лимита вы можете просмотреть полученный результат в PDF.")

        # Создаем фиктивный токен для пробного режима
        self.token = "trial_mode_activated"
        self.service.active=True
        # Принимаем диалог (пропускаем активацию)
        self.accept()
    
    def try_validate(self, checked=False):
        print( get_hwid())
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
