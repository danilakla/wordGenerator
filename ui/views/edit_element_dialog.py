import re
from PyQt6.QtWidgets import QDialog, QHBoxLayout,QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
from PyQt6.QtCore import Qt
from elements.element import Element
from elements.header import Header
from elements.paragraph import Paragraph
from elements.table import Table
from elements.image import Image
from elements.listing import Listing
from elements.list_element import ListElement
from elements.formula import Formula
from ui.views.edit_table_dialog import EditTableDialog
from ui.views.edit_list_dialog import EditListDialog
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
            dialog = EditTableDialog(element)
            self.fields['table_dialog'] = dialog
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
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Содержимое:"))
            layout.addWidget(self.fields['text'])
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
        elif isinstance(element, ListElement):
            dialog = EditListDialog(element)
            self.fields['list_dialog'] = dialog
        elif isinstance(element, Formula):
            self.fields['formula'] = QLineEdit(element.formula)
            layout.addWidget(QLabel("Формула:"))
            layout.addWidget(self.fields['formula'])

        if not isinstance(element, (Table, ListElement)):
            btn_save = QPushButton("Сохранить")
            btn_save.clicked.connect(self.accept)
            layout.addWidget(btn_save)

        self.setLayout(layout)

    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.fields['path'].setText(file_name)

    def extract_text_after_leading_numbers(self, text: str) -> str:
        cleaned_text = re.sub(r"^(\d+[\.\d]*\s*)+", "", text).strip()
        return cleaned_text if cleaned_text else text

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
        if isinstance(self.element, Header) or isinstance(self.element, Paragraph):
            data['text'] = self.extract_text_after_leading_numbers(self.fields['text'].text())
        elif isinstance(self.element, Table):
            data = self.fields['table_dialog'].get_data()
        elif isinstance(self.element, Image):
            data['caption'] = self.clean_caption(self.fields['caption'].text())
            path = self.fields['path'].text()
            if path:
                data['image_path'] = path
        elif isinstance(self.element, Listing):
            data['text'] = self.fields['text'].toPlainText()
            data['caption'] = self.clean_caption(self.fields['caption'].text())
        elif isinstance(self.element, ListElement):
            data = self.fields['list_dialog'].get_data()
        elif isinstance(self.element, Formula):
            data['formula'] = self.fields['formula'].text()
        return data

    def exec(self):
        if isinstance(self.element, (Table, ListElement)):
            return self.fields['table_dialog' if isinstance(self.element, Table) else 'list_dialog'].exec()
        return super().exec()