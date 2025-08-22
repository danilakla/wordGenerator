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

        self.level_combo = QComboBox()
        self.level_combo.addItems(["1", "2", "3", "4"])  # Уровни заголовков
        layout.addWidget(QLabel("Уровень:"))
        layout.addWidget(self.level_combo)

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
                self._populate_combo(combo, elem.children, prefix + "  ")

    def update_after_combo(self):
        self.after_combo.clear()
        idx = self.parent_combo.currentIndex()
        if idx >= 0:
            parent = self.parent_combo.itemData(idx)
            if parent:
                self._populate_combo(self.after_combo, parent.children, "")

    def get_data(self):
        parent = self.parent_combo.currentData() if self.parent_combo.currentIndex() >= 0 else None
        after = self.after_combo.currentData() if self.after_combo.currentIndex() >= 0 else None
        text = self.text_edit.text()
        level = int(self.level_combo.currentText())
        return parent, after, text, level