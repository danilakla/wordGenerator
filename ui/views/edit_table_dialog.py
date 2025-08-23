import re
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from elements.table import Table, DataTable
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from typing import Dict

from ui.views.cell_aligment_dialog import CellAlignmentDialog

class EditTableDialog(QDialog):
    def __init__(self, table: Table):
        super().__init__()
        self.table = table
        self.setWindowTitle("Редактировать таблицу")
        self.WD_PARAGRAPH_ALIGNMENT_MAP = {
            "center": WD_PARAGRAPH_ALIGNMENT.CENTER,
            "left": WD_PARAGRAPH_ALIGNMENT.LEFT,
            "right": WD_PARAGRAPH_ALIGNMENT.RIGHT,
            "justify": WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        }
        self.WD_CELL_VERTICAL_ALIGNMENT_MAP = {
            "center": WD_CELL_VERTICAL_ALIGNMENT.CENTER,
            "top": WD_CELL_VERTICAL_ALIGNMENT.TOP,
            "bottom": WD_CELL_VERTICAL_ALIGNMENT.BOTTOM,
            "both": WD_CELL_VERTICAL_ALIGNMENT.BOTH
        }
        layout = QVBoxLayout()

        # Подпись таблицы
        self.caption_edit = QLineEdit(self.table.caption)
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        # Таблица
        self.table_widget = QTableWidget(len(self.table.data), len(self.table.data[0]) if self.table.data else 0)
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
        for i, row in enumerate(self.table.data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell.data)
                horiz_key = next((k for k, v in self.WD_PARAGRAPH_ALIGNMENT_MAP.items() if v == cell.horizontal), 'center')
                vert_key = next((k for k, v in self.WD_CELL_VERTICAL_ALIGNMENT_MAP.items() if v == cell.vertical), 'center')
                item.setData(Qt.ItemDataRole.UserRole, {'horizontal': horiz_key, 'vertical': vert_key})
                self.table_widget.setItem(i, j, item)
        layout.addWidget(QLabel("Таблица:"))
        layout.addWidget(self.table_widget)

        # Кнопка выравнивания
        self.btn_align = QPushButton("Настроить выравнивание")
        self.btn_align.clicked.connect(self.open_align_dialog)
        self.btn_align.setEnabled(False)
        layout.addWidget(self.btn_align)

        self.table_widget.itemSelectionChanged.connect(self.update_align_button)

        # Кнопка сохранения
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def on_cell_clicked(self, row, col):
        table_widget = self.table_widget
        item = table_widget.item(row, col)
        if not item:
            item = QTableWidgetItem("")
            table_widget.setItem(row, col, item)

    def update_align_button(self):
        selected = self.table_widget.selectedItems()
        self.btn_align.setEnabled(bool(selected))

    def open_align_dialog(self):
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

    def clean_caption(self, caption: str) -> str:
        patterns = [
            r'^Таблица \d+\.\d+ – .+$',
            r'^Рисунок \d+\.\d+ – .+$',
            r'^Листинг \d+\.\d+ – .+$'
        ]
        if any(re.match(pattern, caption) for pattern in patterns):
            return caption.split(" – ", 1)[-1].strip()
        return caption

    def get_data(self) -> Dict:
        data = {}
        data['caption'] = self.clean_caption(self.caption_edit.text())
        table_data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                text = item.text() if item else ""
                align_data = item.data(Qt.ItemDataRole.UserRole) if item else None
                horizontal_str = align_data.get('horizontal', 'center') if align_data else 'center'
                vertical_str = align_data.get('vertical', 'center') if align_data else 'center'
                horizontal = self.WD_PARAGRAPH_ALIGNMENT_MAP.get(horizontal_str, WD_PARAGRAPH_ALIGNMENT.CENTER)
                vertical = self.WD_CELL_VERTICAL_ALIGNMENT_MAP.get(vertical_str, WD_CELL_VERTICAL_ALIGNMENT.CENTER)
                row_data.append(DataTable(text, horizontal, vertical))
            table_data.append(row_data)
        data['data'] = table_data
        return data