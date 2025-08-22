from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from elements.element import Element
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from elements.table import DataTable
from typing import List, Optional

class AddTableDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить таблицу")
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
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
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

    def on_cell_clicked(self, row, col):
        item = self.table_widget.item(row, col)
        if not item:
            item = QTableWidgetItem("")
            self.table_widget.setItem(row, col, item)

        # Диалог для выбора alignment
        align_dialog = QDialog(self)
        align_dialog.setWindowTitle("Выравнивание ячейки")
        align_layout = QVBoxLayout()

        horiz_label = QLabel("Горизонтальное выравнивание:")
        self.horiz_combo = QComboBox()
        self.horiz_combo.addItems(["center", "left", "right", "justify"])
        align_layout.addWidget(horiz_label)
        align_layout.addWidget(self.horiz_combo)

        vert_label = QLabel("Вертикальное выравнивание:")
        self.vert_combo = QComboBox()
        self.vert_combo.addItems(["center", "top", "bottom", "both"])
        align_layout.addWidget(vert_label)
        align_layout.addWidget(self.vert_combo)

        # Загрузить текущие значения если есть
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.horiz_combo.setCurrentText(data.get('horizontal', 'center'))
            self.vert_combo.setCurrentText(data.get('vertical', 'center'))

        btn_save_align = QPushButton("Сохранить")
        btn_save_align.clicked.connect(align_dialog.accept)
        align_layout.addWidget(btn_save_align)

        align_dialog.setLayout(align_layout)

        if align_dialog.exec():
            horizontal = self.horiz_combo.currentText()
            vertical = self.vert_combo.currentText()
            item.setData(Qt.ItemDataRole.UserRole, {'horizontal': horizontal, 'vertical': vertical})

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
        WD_PARAGRAPH_ALIGNMENT_MAP = {
            "center": WD_PARAGRAPH_ALIGNMENT.CENTER,
            "left": WD_PARAGRAPH_ALIGNMENT.LEFT,
            "right": WD_PARAGRAPH_ALIGNMENT.RIGHT,
            "justify": WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        }
        WD_CELL_VERTICAL_ALIGNMENT_MAP = {
            "center": WD_CELL_VERTICAL_ALIGNMENT.CENTER,
            "top": WD_CELL_VERTICAL_ALIGNMENT.TOP,
            "bottom": WD_CELL_VERTICAL_ALIGNMENT.BOTTOM,
            "both": WD_CELL_VERTICAL_ALIGNMENT.BOTH
        }
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                text = item.text() if item else ""
                align_data = item.data(Qt.ItemDataRole.UserRole) if item else None
                horizontal_str = align_data.get('horizontal', 'center') if align_data else 'center'
                vertical_str = align_data.get('vertical', 'center') if align_data else 'center'
                horizontal = WD_PARAGRAPH_ALIGNMENT_MAP.get(horizontal_str, WD_PARAGRAPH_ALIGNMENT.CENTER)
                vertical = WD_CELL_VERTICAL_ALIGNMENT_MAP.get(vertical_str, WD_CELL_VERTICAL_ALIGNMENT.CENTER)
                row_data.append(DataTable(text, horizontal, vertical))
            data.append(row_data)
        return parent, after, data, caption