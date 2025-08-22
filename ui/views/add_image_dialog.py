from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QFileDialog
from elements.element import Element
from typing import List, Optional

class AddImageDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить рисунок")
        layout = QVBoxLayout()

        self.caption_edit = QLineEdit()
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        self.path_edit = QLineEdit()
        btn_browse = QPushButton("Обзор")
        btn_browse.clicked.connect(self.browse_image)
        path_layout = QVBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(btn_browse)
        layout.addWidget(QLabel("Путь к картинке:"))
        layout.addLayout(path_layout)

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

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.path_edit.setText(path)

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
        path = self.path_edit.text()
        caption = self.caption_edit.text()
        return parent, after, path, caption