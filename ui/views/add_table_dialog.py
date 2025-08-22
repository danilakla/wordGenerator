from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from elements.element import Element
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from elements.table import DataTable
from typing import List, Optional

class AddTableDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        layout = QVBoxLayout()

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

        self.table_widget = QTableWidget(2, 2)  # Начально 2x2
        layout.addWidget(self.table_widget)

        add_layout = QHBoxLayout()
        btn_add_row = QPushButton("Добавить строку")
        btn_add_row.clicked.connect(lambda: self.table_widget.setRowCount(self.table_widget.rowCount() + 1))
        add_layout.addWidget(btn_add_row)

        btn_add_col = QPushButton("Добавить столбец")
        btn_add_col.clicked.connect(lambda: self.table_widget.setColumnCount(self.table_widget.columnCount() + 1))
        add_layout.addWidget(btn_add_col)
        layout.addLayout(add_layout)

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

    def get_data(self):
        parent = self.parent_combo.currentData()
        after = self.after_combo.currentData()
        caption = self.caption_edit.text()
        data = []
        default_horizontal = WD_PARAGRAPH_ALIGNMENT.CENTER
        default_vertical = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                text = item.text() if item else ""
                row_data.append(DataTable(text, default_horizontal, default_vertical))
            data.append(row_data)
        return parent, after, data, caption