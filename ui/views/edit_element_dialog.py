from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit, QListWidget, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem
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
            for i, row in enumerate(element.data):
                for j, cell in enumerate(row):
                    self.fields['table_widget'].setItem(i, j, QTableWidgetItem(cell.data))
            layout.addWidget(QLabel("Таблица:"))
            layout.addWidget(self.fields['table_widget'])
            btn_add_row = QPushButton("Добавить строку")
            btn_add_row.clicked.connect(lambda: self.fields['table_widget'].setRowCount(self.fields['table_widget'].rowCount() + 1))
            layout.addWidget(btn_add_row)
            btn_add_col = QPushButton("Добавить столбец")
            btn_add_col.clicked.connect(lambda: self.fields['table_widget'].setColumnCount(self.fields['table_widget'].columnCount() + 1))
            layout.addWidget(btn_add_col)
        elif isinstance(element, Image):
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
            self.fields['path'] = QLineEdit()  # Предполагаем, что путь не хранится, но для редактирования允许 выбрать новый
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
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

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

    def get_data(self) -> Dict:
        data = {}
        if isinstance(self.element, Header) or isinstance(self.element, Paragraph):
            data['text'] = self.fields['text'].text()
        elif isinstance(self.element, Table):
            data['caption'] = self.fields['caption'].text()
            table_data = []
            default_horizontal = WD_PARAGRAPH_ALIGNMENT.CENTER
            default_vertical = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for row in range(self.fields['table_widget'].rowCount()):
                row_data = []
                for col in range(self.fields['table_widget'].columnCount()):
                    item = self.fields['table_widget'].item(row, col)
                    text = item.text() if item else ""
                    row_data.append(DataTable(text, default_horizontal, default_vertical))
                table_data.append(row_data)
            data['data'] = table_data
        elif isinstance(self.element, Image):
            data['caption'] = self.fields['caption'].text()
            path = self.fields['path'].text()
            if path:
                data['image_path'] = path
        elif isinstance(self.element, Listing):
            data['text'] = self.fields['text'].toPlainText()
            data['caption'] = self.fields['caption'].text()
        elif isinstance(self.element, ListElement):
            data['list_type'] = self.fields['list_type'].text()
            data['items'] = [self.fields['items_list'].item(i).text() for i in range(self.fields['items_list'].count())]
        elif isinstance(self.element, Formula):
            data['formula'] = self.fields['formula'].text()
            data['caption'] = self.fields['caption'].text()
        return data