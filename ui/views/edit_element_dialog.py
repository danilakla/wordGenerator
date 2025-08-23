# Updated edit_element_dialog.py with changes for Formula and Table.

import re
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit, QListWidget, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from elements.element import Element
from elements.header import Header
from elements.paragraph import Paragraph
from elements.table import Table, DataTable
from elements.image import Image
from elements.listing import Listing
from elements.list_element import ListElement
from elements.formula import Formula
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from typing import List, Dict

class EditElementDialog(QDialog):
    def __init__(self, element: Element, tree: List[Element]):
        super().__init__()
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
        self.element = element
        self.tree = tree
        self.fields: Dict[str, any] = {}
        self.setWindowTitle(f"Редактировать {type(element).__name__}")
        layout = QVBoxLayout()

        if isinstance(element, Header):
            self.fields['text'] = QLineEdit(element.text)
            layout.addWidget(QLabel("Текст:"))
            layout.addWidget(self.fields['text'])
        elif isinstance(element, Paragraph):
            self.fields['text'] = QLineEdit(element.text)
            layout.addWidget(QLabel("Текст:"))
            layout.addWidget(self.fields['text'])
        elif isinstance(element, Table):
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
            self.fields['table_widget'] = QTableWidget(len(element.data), len(element.data[0]) if element.data else 0)
            self.fields['table_widget'].cellClicked.connect(self.on_cell_clicked)
            for i, row in enumerate(element.data):
                for j, cell in enumerate(row):
                    item = QTableWidgetItem(cell.data)
                    horiz_key = next((k for k, v in self.WD_PARAGRAPH_ALIGNMENT_MAP.items() if v == cell.horizontal), 'center')
                    vert_key = next((k for k, v in self.WD_CELL_VERTICAL_ALIGNMENT_MAP.items() if v == cell.vertical), 'center')
                    item.setData(Qt.ItemDataRole.UserRole, {'horizontal': horiz_key, 'vertical': vert_key})
                    self.fields['table_widget'].setItem(i, j, item)
            layout.addWidget(QLabel("Таблица:"))
            layout.addWidget(self.fields['table_widget'])
            # Removed add row/col buttons
        elif isinstance(element, Image):
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
            self.fields['path'] = QLineEdit()
            btn_browse = QPushButton("Обзор")
            btn_browse.clicked.connect(self.browse_image)
            path_layout = QHBoxLayout()
            path_layout.addWidget(self.fields['path'])
            path_layout.addWidget(btn_browse)
            layout.addWidget(QLabel("Новый путь к картинке (опционально):"))
            layout.addLayout(path_layout)
        elif isinstance(element, Listing):
            self.fields['text'] = QTextEdit(element.text)
            layout.addWidget(QLabel("Содержимое:"))
            layout.addWidget(self.fields['text'])
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
        elif isinstance(element, ListElement):
            self.fields['list_type'] = QLineEdit(element.list_type)
            layout.addWidget(QLabel("Тип списка:"))
            layout.addWidget(self.fields['list_type'])
            self.fields['items_list'] = QListWidget()
            for item in element.items:
                self.fields['items_list'].addItem(item)
            layout.addWidget(QLabel("Элементы списка:"))
            layout.addWidget(self.fields['items_list'])
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
        elif isinstance(element, Formula):
            self.fields['formula'] = QLineEdit(element.formula)
            layout.addWidget(QLabel("Формула (LaTeX):"))
            layout.addWidget(self.fields['formula'])
            # Removed caption edit

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def on_cell_clicked(self, row, col):
        table_widget = self.fields['table_widget']
        item = table_widget.item(row, col)
        if not item:
            item = QTableWidgetItem("")
            table_widget.setItem(row, col, item)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.fields['path'].setText(path)

    def add_item(self):
        text = self.item_edit.text()
        if text:
            self.fields['items_list'].addItem(text)
            self.item_edit.clear()

    def remove_item(self):
        selected = self.fields['items_list'].selectedItems()
        if selected:
            for item in selected:
                self.fields['items_list'].takeItem(self.fields['items_list'].row(item))
    def extract_text_after_leading_numbers(self,text: str) -> str:
    
        cleaned_text = re.sub(r"^(\d+[\.\d]*\s*)+", "", text).strip()
        return cleaned_text if cleaned_text else text
    def clean_caption(self,caption: str) -> str:
        patterns = [
            r'^Таблица \d+\.\d+ – .+$',
            r'^Рисунок \d+\.\d+ – .+$',
            r'^Листинг \d+\.\d+ – .+$'
        ]

        # Проверяем соответствие хотя бы одному паттерну
        if any(re.match(pattern, caption) for pattern in patterns):
            return caption.split(" – ", 1)[-1].strip()
        return caption
    def get_data(self) -> Dict:
        data = {}
        if isinstance(self.element, Header) or isinstance(self.element, Paragraph):
            data['text'] = self.extract_text_after_leading_numbers(self.fields['text'].text())
        elif isinstance(self.element, Table):
            data['caption'] = self.clean_caption(self.fields['caption'].text())
            table_data = []
            for row in range(self.fields['table_widget'].rowCount()):
                row_data = []
                for col in range(self.fields['table_widget'].columnCount()):
                    item = self.fields['table_widget'].item(row, col)
                    text = item.text() if item else ""
                    align_data = item.data(Qt.ItemDataRole.UserRole) if item else None
                    horizontal_str = align_data.get('horizontal', 'center') if align_data else 'center'
                    vertical_str = align_data.get('vertical', 'center') if align_data else 'center'
                    horizontal = self.WD_PARAGRAPH_ALIGNMENT_MAP.get(horizontal_str, WD_PARAGRAPH_ALIGNMENT.CENTER)
                    vertical = self.WD_CELL_VERTICAL_ALIGNMENT_MAP.get(vertical_str, WD_CELL_VERTICAL_ALIGNMENT.CENTER)
                    row_data.append(DataTable(text, horizontal, vertical))
                table_data.append(row_data)
            data['data'] = table_data
        elif isinstance(self.element, Image):
            data['caption'] = self.clean_caption(self.fields['caption'].text())
            path = self.fields['path'].text()
            if path:
                data['image_path'] = path
        elif isinstance(self.element, Listing):
            data['text'] = self.fields['text'].toPlainText()
            data['caption'] = self.clean_caption(self.fields['caption'].text())
        elif isinstance(self.element, ListElement):
            data['list_type'] = self.fields['list_type'].text()
            data['items'] = [self.fields['items_list'].item(i).text() for i in range(self.fields['items_list'].count())]
        elif isinstance(self.element, Formula):
            data['formula'] = self.fields['formula'].text()
            # No caption
        return data