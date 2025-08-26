from PyQt6.QtWidgets import QDialog, QLabel, QTextEdit, QVBoxLayout, QPushButton
from elements.element import Element
from typing import List, Optional

class AddParagraphDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить текст")
        self.resize(600, 400)  # Увеличиваем размер окна
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()  # Заменяем QLineEdit на QTextEdit
        layout.addWidget(QLabel("Текст:"))
        layout.addWidget(self.text_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str]:
        text = self.text_edit.toPlainText()  # Изменяем метод получения текста
        return None, None, text