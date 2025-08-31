from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from elements.element import Element
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from elements.table import DataTable
from typing import List, Optional

from ui.views.cell_aligment_dialog import CellAlignmentDialog

class AddTableDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить таблицу")
        layout = QVBoxLayout()

        self.caption_edit = QLineEdit()
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        size_layout = QHBoxLayout()
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setValue(2)
        size_layout.addWidget(QLabel("Строки:"))
        size_layout.addWidget(self.rows_spin)

        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setValue(2)
        size_layout.addWidget(QLabel("Столбцы:"))
        size_layout.addWidget(self.cols_spin)

        btn_set_size = QPushButton("Установить размер")
        btn_set_size.clicked.connect(self.set_table_size)
        size_layout.addWidget(btn_set_size)
        layout.addLayout(size_layout)

        self.table_widget = QTableWidget(0, 0)
        layout.addWidget(self.table_widget)

        self.btn_align = QPushButton("Настроить выравнивание")
        self.btn_align.clicked.connect(self.open_align_dialog)
        self.btn_align.setEnabled(False)
        layout.addWidget(self.btn_align)

        self.table_widget.itemSelectionChanged.connect(self.update_align_button)

        add_layout = QHBoxLayout()
        btn_add_row = QPushButton("Добавить строку")
        
        btn_add_row.clicked.connect(    lambda checked=False: self.table_widget.setColumnCount(self.table_widget.columnCount() + 1)
)
        add_layout.addWidget(btn_add_row)

        btn_add_col = QPushButton("Добавить столбец")
        btn_add_col.clicked.connect(lambda checked=False: self.table_widget.setColumnCount(self.table_widget.columnCount() + 1))
        add_layout.addWidget(btn_add_col)
        layout.addLayout(add_layout)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def set_table_size(self, checked=False):
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        self.table_widget.setRowCount(rows)
        self.table_widget.setColumnCount(cols)
        for r in range(rows):
            for c in range(cols):
                if not self.table_widget.item(r, c):
                    item = QTableWidgetItem("")
                    self.table_widget.setItem(r, c, item)

    def update_align_button(self, checked=False):
        selected = self.table_widget.selectedItems()
        self.btn_align.setEnabled(bool(selected))

    def open_align_dialog(self, checked=False):
        selected = self.table_widget.selectedItems()
        if not selected:
            return
        # Используем выравнивание первой выделенной ячейки как начальное значение
        first_item = selected[0]
        align_dialog = CellAlignmentDialog(self, first_item.data(Qt.ItemDataRole.UserRole))
        if align_dialog.exec():
            align_data = align_dialog.get_data()
            # Применяем выравнивание ко всем выделенным ячейкам
            for item in selected:
                item.setData(Qt.ItemDataRole.UserRole, align_data)

    def get_data(self):
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
                row_data.append(DataTable(text, horizontal, vertical,1,col,row))
            data.append(row_data)
        return None, None, data, caption