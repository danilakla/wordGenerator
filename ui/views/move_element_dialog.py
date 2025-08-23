from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton, QTextEdit, QListWidget, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem
from elements.element import Element

from typing import List, Dict
class MoveElementDialog(QDialog):
    def __init__(self, tree: List[Element], element: Element):
        super().__init__()
        self.tree = tree
        self.element = element
        layout = QVBoxLayout()

        self.parent_combo = QComboBox()
        self._populate_combo(self.parent_combo, tree, "")
        layout.addWidget(QLabel("Новый родитель:"))
        layout.addWidget(self.parent_combo)

        self.after_combo = QComboBox()
        layout.addWidget(QLabel("После какого:"))
        layout.addWidget(self.after_combo)

        self.parent_combo.currentIndexChanged.connect(self.update_after_combo)

        btn_save = QPushButton("Переместить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _populate_combo(self, combo: QComboBox, elements: List[Element], prefix: str):
        for elem in elements:
            if elem != self.element:  # Исключаем сам элемент
                combo.addItem(prefix + str(type(elem).__name__) + ": " + (elem.text if hasattr(elem, 'text') else ""), elem)
                if hasattr(elem, 'children'):
                    self._populate_combo(combo, elem.children, prefix + "  ")

    def update_after_combo(self):
        self.after_combo.clear()
        idx = self.parent_combo.currentIndex()
        if idx >= 0:
            parent = self.parent_combo.itemData(idx)
            if parent and hasattr(parent, 'children'):
                self._populate_combo(self.after_combo, parent.children, "")

    def get_data(self):
        parent = self.parent_combo.currentData()
        after = self.after_combo.currentData()
        return parent, after