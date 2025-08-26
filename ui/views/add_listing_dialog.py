from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout
from elements.element import Element
from typing import List, Optional
class AddListingDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить листинг")
        self.resize(600, 500)  # Увеличиваем размер окна
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()  # Заменяем QLineEdit на QTextEdit
        layout.addWidget(QLabel("Содержимое:"))
        layout.addWidget(self.text_edit)

        self.caption_edit = QLineEdit()
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def get_data(self):
        text = self.text_edit.toPlainText()  # Изменяем метод получения текста
        caption = self.caption_edit.text()
        return None, None, text, caption