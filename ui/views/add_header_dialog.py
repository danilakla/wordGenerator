from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton
from typing import List
from elements.element import Element
from elements.header import Header
class AddHeaderDialog(QDialog):
    def __init__(self, tree: List[Element], is_sub: bool):
        super().__init__()
        self.tree = tree
        self.is_sub = is_sub
        self.setWindowTitle("Добавить раздел" if not is_sub else "Добавить подраздел")
        layout = QVBoxLayout()

        self.text_edit = QLineEdit()
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.text_edit)

        if not is_sub:
            # Level is always 1, no parent, after top-level headers
            self.level = 1
            self.parent_combo = None
            self.after_combo = QComboBox()
            self._populate_after_combo_for_top_level(self.after_combo, tree)
            layout.addWidget(QLabel("После какого:"))
            layout.addWidget(self.after_combo)
        else:
            # Level = parent.level + 1, parent combo, after children
            self.level_combo = None
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
            if isinstance(elem, Header):
                combo.addItem(prefix + elem.text, elem)
                if hasattr(elem, 'children'):
                    self._populate_combo(combo, elem.children, prefix + "  ")

    def _populate_after_combo_for_top_level(self, combo: QComboBox, elements: List[Element]):
        for elem in elements:
            if isinstance(elem, Header) and elem.level == 1:
                combo.addItem(elem.text, elem)

    def update_after_combo(self):
        self.after_combo.clear()
        idx = self.parent_combo.currentIndex()
        if idx >= 0:
            parent = self.parent_combo.itemData(idx)
            if parent and hasattr(parent, 'children'):
                self._populate_combo(self.after_combo, parent.children, "")

    def get_data(self):
        after = self.after_combo.currentData() if self.after_combo.currentIndex() >= 0 else None
        text = self.text_edit.text()
        if self.is_sub:
            parent = self.parent_combo.currentData() if self.parent_combo.currentIndex() >= 0 else None
            level = parent.level + 1 if parent else 1
            return parent, after, text, level
        else:
            return None, after, text, self.level