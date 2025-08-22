from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton
from elements.element import Element
from typing import List, Optional

class AddFormulaDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить формулу")
        layout = QVBoxLayout()

        self.formula_edit = QLineEdit()
        layout.addWidget(QLabel("Формула (LaTeX):"))
        layout.addWidget(self.formula_edit)

        self.caption_edit = QLineEdit()
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        self.parent_combo = QComboBox()
        self._populate_combo(self.parent_combo, tree, "")
        layout.addWidget(QLabel("Родитель:"))
        layout.addWidget(self.parent_combo)

        self.after_combo = QComboBox()
        layout.addWidget(QLabel("После какого:"))
        layout.addWidget(self.after_combo)

        self.parent_combo.currentIndexChanged.connect(self.update_after_combo)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _populate_combo(self, combo: QComboBox, elements: List[Element], prefix: str):
        for elem in elements:
            combo.addItem(prefix + str(type(elem).__name__) + ": " + (elem.text if hasattr(elem, 'text') else elem.caption if hasattr(elem, 'caption') else ""), elem)
            if hasattr(elem, 'children'):
                self._populate_combo(combo, elem.children, prefix + "  ")

    def update_after_combo(self):
        self.after_combo.clear()
        idx = self.parent_combo.currentIndex()
        if idx >= 0:
            parent = self.parent_combo.itemData(idx)
            if parent and hasattr(parent, 'children'):
                self._populate_combo(self.after_combo, parent.children, "")

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str, str]:
        parent = self.parent_combo.currentData()
        after = self.after_combo.currentData()
        formula = self.formula_edit.text()
        caption = self.caption_edit.text()
        return parent, after, formula, caption