from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton
from elements.element import Element
from typing import List, Optional

class AddParagraphDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить текст")
        layout = QVBoxLayout()

        self.text_edit = QLineEdit()
        layout.addWidget(QLabel("Текст:"))
        layout.addWidget(self.text_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str]:
        text = self.text_edit.text()
        return None, None, text