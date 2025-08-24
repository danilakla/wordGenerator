import re
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QStyledItemDelegate, QStyle,
                             QMessageBox)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from elements.table import Table, DataTable
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from typing import Dict, Optional, List, Tuple

from ui.views.cell_aligment_dialog import CellAlignmentDialog

class BorderDelegate(QStyledItemDelegate):
    def __init__(self, table_data, parent=None):
        super().__init__(parent)
        self.table_data = table_data

    def paint(self, painter: QPainter, option, index):
        row, col = index.row(), index.column()
        if row >= len(self.table_data) or col >= len(self.table_data[0]):
            super().paint(painter, option, index)
            return
            
        cell = self.table_data[row][col]
        
        # Определяем, является ли это основной ячейкой (с данными)
        is_main_cell = self.is_main_cell(row, col, cell)
        
        # Для неосновных ячеек объединенной группы рисуем серый фон
        if not is_main_cell and cell.parent_col is not None and cell.parent_row is not None:
            painter.fillRect(option.rect, QBrush(QColor(240, 240, 240)))
        
        # Рисуем текст только для основной ячейки
        if is_main_cell:
            super().paint(painter, option, index)
        else:
            # Для неосновных ячеек просто рисуем границы
            painter.fillRect(option.rect, QBrush(QColor(240, 240, 240)))
        
        # Рисуем границы
        painter.save()
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        painter.setPen(pen)
        self.draw_borders(painter, option.rect, row, col, cell)
        painter.restore()

    def is_main_cell(self, row: int, col: int, cell: DataTable) -> bool:
        """Определяет, является ли ячейка основной (той, где отображается контент)"""
        if cell.parent_col is None or cell.parent_row is None:
            return True
        
        # Основная ячейка - та, у которой координаты совпадают с parent_col/parent_row
        return row == cell.parent_row and col == cell.parent_col

    def draw_borders(self, painter: QPainter, rect: QRect, row: int, col: int, cell: DataTable):
        # Рисуем верхнюю границу (всегда)
        painter.drawLine(rect.topLeft(), rect.topRight())
        
        # Рисуем левую границу (всегда)
        painter.drawLine(rect.topLeft(), rect.bottomLeft())
        
        # Проверяем, нужно ли рисовать правую границу
        draw_right = True
        if col + 1 < len(self.table_data[0]):
            right_cell = self.table_data[row][col + 1]
            if (right_cell.parent_col is not None and right_cell.parent_row is not None and
                right_cell.parent_col == cell.parent_col and right_cell.parent_row == cell.parent_row):
                draw_right = False
        
        if draw_right:
            painter.drawLine(rect.topRight(), rect.bottomRight())
        
        # Проверяем, нужно ли рисовать нижнюю границу
        draw_bottom = True
        if row + 1 < len(self.table_data):
            bottom_cell = self.table_data[row + 1][col]
            if (bottom_cell.parent_col is not None and bottom_cell.parent_row is not None and
                bottom_cell.parent_col == cell.parent_col and bottom_cell.parent_row == cell.parent_row):
                draw_bottom = False
        
        if draw_bottom:
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())


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
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
        self.table_widget.itemChanged.connect(self.on_item_changed)
        
        # Устанавливаем кастомный делегат для управления границами
        self.delegate = BorderDelegate(self.table.data, self.table_widget)
        self.table_widget.setItemDelegate(self.delegate)
        
        # Заполняем таблицу
        self.populate_table()

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

    def populate_table(self):
        """Заполняет таблицу данными, учитывая объединенные ячейки"""
        self.table_widget.blockSignals(True)  # Блокируем сигналы чтобы избежать рекурсии
        
        for i, row in enumerate(self.table.data):
            for j, cell in enumerate(row):
                # Определяем, является ли это основной ячейкой объединенной группы
                is_main_cell = self.is_main_cell(i, j, cell)
                
                if is_main_cell:
                    # Для основной ячейки создаем обычный item с данными
                    item = QTableWidgetItem(cell.data)
                else:
                    # Для неосновных ячеек создаем пустой item
                    item = QTableWidgetItem(cell.data)
                    item.setFlags(Qt.ItemFlag.NoItemFlags)  # Делаем ячейку недоступной для редактирования
                
                # Сохраняем информацию о выравнивании
                horiz_key = next((k for k, v in self.WD_PARAGRAPH_ALIGNMENT_MAP.items() if v == cell.horizontal), 'center')
                vert_key = next((k for k, v in self.WD_CELL_VERTICAL_ALIGNMENT_MAP.items() if v == cell.vertical), 'center')
                item.setData(Qt.ItemDataRole.UserRole, {'horizontal': horiz_key, 'vertical': vert_key})
                
                self.table_widget.setItem(i, j, item)
        
        self.table_widget.blockSignals(False)

    def is_main_cell(self, row: int, col: int, cell: DataTable) -> bool:
        """Определяет, является ли ячейка основной в объединенной группе"""
        if cell.parent_col is None or cell.parent_row is None:
            return True
        return row == cell.parent_row and col == cell.parent_col

    def get_merged_cells(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Возвращает список всех ячеек, объединенных с данной"""
        cell = self.table.data[row][col]
        if cell.parent_col is None or cell.parent_row is None:
            return [(row, col)]
        
        merged_cells = []
        parent_row, parent_col = cell.parent_row, cell.parent_col
        
        for i in range(len(self.table.data)):
            for j in range(len(self.table.data[0])):
                other_cell = self.table.data[i][j]
                if (other_cell.parent_col == parent_col and 
                    other_cell.parent_row == parent_row):
                    merged_cells.append((i, j))
        
        return merged_cells

    def on_cell_clicked(self, row, col):
        """Обработка клика по ячейке"""
        cell = self.table.data[row][col]
        
        # Если это не основная ячейка объединенной группы, перенаправляем фокус на основную
        if not self.is_main_cell(row, col, cell) and cell.parent_col is not None and cell.parent_row is not None:
            main_row, main_col = cell.parent_row, cell.parent_col
            self.table_widget.setCurrentCell(main_row, main_col)
            return
            
        table_widget = self.table_widget
        item = table_widget.item(row, col)
        if not item:
            item = QTableWidgetItem(cell.data)
            table_widget.setItem(row, col, item)

    def on_item_changed(self, item):
        """Обработка изменения содержимого ячейки - синхронизация объединенных ячеек"""
        if not item:
            return
            
        row, col = self.get_item_position(item)
        if row is None or col is None:
            return
            
        cell = self.table.data[row][col]
        
        # Если это основная ячейка объединенной группы, синхронизируем данные
        if self.is_main_cell(row, col, cell) and cell.parent_col is not None and cell.parent_row is not None:
            merged_cells = self.get_merged_cells(row, col)
            
            self.table_widget.blockSignals(True)
            for merged_row, merged_col in merged_cells:
                    merged_item = self.table_widget.item(merged_row, merged_col)
                    if merged_item:
                        merged_item.setText(item.text())
            self.table_widget.blockSignals(False)

    def get_item_position(self, item) -> Tuple[Optional[int], Optional[int]]:
        """Возвращает позицию item в таблице"""
        for row in range(self.table_widget.rowCount()):
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.item(row, col) == item:
                    return row, col
        return None, None

    def update_align_button(self):
        selected = self.table_widget.selectedItems()
        self.btn_align.setEnabled(bool(selected))

    def open_align_dialog(self):
        selected = self.table_widget.selectedItems()
        if not selected:
            return

        # Используем выравнивание первой выделенной ячейки
        first_item = selected[0]
        align_dialog = CellAlignmentDialog(self, first_item.data(Qt.ItemDataRole.UserRole))
        if align_dialog.exec():
            align_data = align_dialog.get_data()

            # Применяем выравнивание ко всем выделенным ячейкам
            self.table_widget.blockSignals(True)
            for item in selected:
                row, col = self.get_item_position(item)
                if row is not None and col is not None:
                    cell = self.table.data[row][col]

                    # Если это объединенная группа, применяем ко всем ячейкам группы
                    if cell.parent_col is not None and cell.parent_row is not None:
                        merged_cells = self.get_merged_cells(row, col)
                        for merged_row, merged_col in merged_cells:
                            merged_item = self.table_widget.item(merged_row, merged_col)
                            if merged_item:
                                merged_item.setData(Qt.ItemDataRole.UserRole, align_data)
                                merged_item.setText(item.text())
                    else:
                        # Одиночная ячейка
                        item.setData(Qt.ItemDataRole.UserRole, align_data)
                        merged_item.setText(item.text())

            self.table_widget.blockSignals(False)
            self.table_widget.viewport().update()

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
                orig_cell = self.table.data[row][col] if row < len(self.table.data) and col < len(self.table.data[0]) else None
                parent_col = orig_cell.parent_col if orig_cell else None
                parent_row = orig_cell.parent_row if orig_cell else None
                row_data.append(DataTable(text, horizontal, vertical, parent_col=parent_col, parent_row=parent_row))
            table_data.append(row_data)
        data['data'] = table_data
        return data