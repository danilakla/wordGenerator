from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from elements.element import Element
from elements.header import Header
from elements.table import Table
from elements.image import Image
from elements.listing import Listing
from elements.list_element import ListElement
from elements.formula import Formula
from elements.paragraph import Paragraph

from typing import List, Optional

class MoveElementDialog(QDialog):
    def __init__(self, tree: List[Element], element: Element):
        super().__init__()
        self.setWindowTitle("Move Element")
        self.resize(600, 400)  # Better window size
        self.tree = tree
        self.element = element
        self.is_header = isinstance(element, Header)
        layout = QVBoxLayout()

        if self.is_header:
            label_text = "Выберите раздел/подраздел, который будет являться родительским"
        else:
            label_text = "Выберите после какого элемента нужно расположить ранее выбранный элемент."

        layout.addWidget (QLabel(label_text))

        self.parent_tree = QTreeWidget()
        self.parent_tree.setHeaderLabel("Tree")
        if self.is_header:
           self._populate_tree_for_header(self.parent_tree.invisibleRootItem(), tree)
        
        else:
           self._populate_tree(self.parent_tree.invisibleRootItem(), tree)
        
        if self.is_header:
            root_item = QTreeWidgetItem(self.parent_tree)
            root_item.setText(0, "Root (None)")
            root_item.setData(0, Qt.ItemDataRole.UserRole, None)
            root_item.setFlags(root_item.flags() | Qt.ItemFlag.ItemIsSelectable)
        layout.addWidget(self.parent_tree)

        self.parent_tree.itemSelectionChanged.connect(self.update_after_list)

        if self.is_header:
            layout.addWidget(QLabel("Пожалуйста, выберите элемент, после которого вы хотите добавить новый:"))
            self.after_list = QListWidget()
            layout.addWidget(self.after_list)
        else:
            self.after_list = None

        btn_save = QPushButton("Move")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _populate_tree(self, parent_item: QTreeWidgetItem, elements: List[Element]):
        for elem in elements:
            if elem == self.element:
                continue
            item = QTreeWidgetItem(parent_item)
            item.setText(0, self._get_element_text(elem))
            item.setData(0, Qt.ItemDataRole.UserRole, elem)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable)
            if hasattr(elem, 'children'):
                self._populate_tree(item, elem.children)
    def _populate_tree_for_header(self, parent_item: QTreeWidgetItem, elements: List[Element]):
        for elem in elements:
            if elem == self.element or not isinstance(elem,Header):
                continue
            item = QTreeWidgetItem(parent_item)
            item.setText(0, self._get_element_text(elem))
            item.setData(0, Qt.ItemDataRole.UserRole, elem)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable)
            if hasattr(elem, 'children'):
                self._populate_tree_for_header(item, elem.children)

    def update_after_list(self, checked=False):
        if not self.is_header:
            return
        self.after_list.clear()
        selected = self.parent_tree.selectedItems()
        if not selected:
            return
        parent = selected[0].data(0, Qt.ItemDataRole.UserRole)
        item = QListWidgetItem("None")
        item.setData(Qt.ItemDataRole.UserRole, None)
        self.after_list.addItem(item)
        children = []
        if parent is None:
            children = [e for e in self.tree if isinstance(e, Header) and e != self.element]
        else:
            children = [e for e in parent.children if isinstance(e, Header) and e != self.element]
        for elem in children:
            item = QListWidgetItem(self._get_element_text(elem))
            item.setData(Qt.ItemDataRole.UserRole, elem)
            self.after_list.addItem(item)

    def _get_element_text(self, elem: Element) -> str:
        if isinstance(elem, Header):
            return f"Раздел: {elem.text[:50]}" + ("..." if len(elem.text) > 50 else "")
        elif isinstance(elem, Paragraph):
            return f"Обычный Текст: {elem.text[:50]}" + ("..." if len(elem.text) > 50 else "")
        elif isinstance(elem, Table):
            return f"Таблица: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
        elif isinstance(elem, Image):
            return f"Рисунок: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
        elif isinstance(elem, Listing):
            return f"Листинг: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
        elif isinstance(elem, ListElement):
            return f"Список: {elem.list_type} (items: {len(elem.items)})"
        elif isinstance(elem, Formula):
            return f"Формула: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
        return type(elem).__name__

    def get_data(self):
        selected_pos = self.parent_tree.selectedItems()
        if not selected_pos:
            return None, None
        pos = selected_pos[0].data(0, Qt.ItemDataRole.UserRole)
        if self.is_header:
            selected_after = self.after_list.selectedItems()
            after = selected_after[0].data(Qt.ItemDataRole.UserRole) if selected_after else None
            return pos, after
        else:
            return pos, None