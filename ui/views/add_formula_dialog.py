from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QMessageBox, QSpinBox, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt
from elements.element import Element
from typing import List, Optional
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class AddFormulaDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить формулу")
        layout = QVBoxLayout()

        self.formula_edit = QLineEdit()
        layout.addWidget(QLabel("Формула (LaTeX):"))
        layout.addWidget(self.formula_edit)

        # self.caption_edit = QLineEdit()
        # layout.addWidget(QLabel("Подпись:"))
        # layout.addWidget(self.caption_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str, str]:
        formula = self.formula_edit.text()
        return None, None, formula, ""