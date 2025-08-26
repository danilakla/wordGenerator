from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton
from elements.formula import Formula
from typing import Dict

class EditFormulaDialog(QDialog):
    def __init__(self, element: Formula):
        super().__init__()
        self.element = element
        self.setWindowTitle("Edit Formula")
        layout = QVBoxLayout()

        self.formula_field = QLineEdit(element.formula)
        layout.addWidget(QLabel("LaTeX Formula:"))
        layout.addWidget(self.formula_field)

        self.caption_field = QLineEdit(element.caption)
        layout.addWidget(QLabel("Caption:"))
        layout.addWidget(self.caption_field)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def get_data(self) -> Dict:
        return {
            'formula': self.formula_field.text(),
            'caption': self.caption_field.text()
        }