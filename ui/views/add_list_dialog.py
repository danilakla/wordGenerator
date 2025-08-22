from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout
from elements.element import Element
from typing import List, Optional

class AddListDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить список")
        layout = QVBoxLayout()

        self.list_type_edit = QLineEdit()
        self.list_type_edit.setPlaceholderText("Тип списка, напр. '-' или '1.'")
        layout.addWidget(QLabel("Тип списка:"))
        layout.addWidget(self.list_type_edit)

        self.items_list = QListWidget()
        layout.addWidget(QLabel("Элементы списка:"))
        layout.addWidget(self.items_list)

        add_item_layout = QHBoxLayout()
        self.item_edit = QLineEdit()
        btn_add_item = QPushButton("Добавить элемент")
        btn_add_item.clicked.connect(self.add_item)
        btn_remove_item = QPushButton("Удалить элемент")
        btn_remove_item.clicked.connect(self.remove_item)
        add_item_layout.addWidget(self.item_edit)
        add_item_layout.addWidget(btn_add_item)
        add_item_layout.addWidget(btn_remove_item)
        layout.addLayout(add_item_layout)

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

    def add_item(self):
        text = self.item_edit.text()
        if text:
            self.items_list.addItem(text)
            self.item_edit.clear()

    def remove_item(self):
        selected = self.items_list.selectedItems()
        if selected:
            for item in selected:
                self.items_list.takeItem(self.items_list.row(item))

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

    def get_data(self) -> tuple[Optional[Element], Optional[Element], List[str], str]:
        parent = self.parent_combo.currentData()
        after = self.after_combo.currentData()
        items = [self.items_list.item(i).text() for i in range(self.items_list.count())]
        list_type = self.list_type_edit.text()
        return parent, after, items, list_type