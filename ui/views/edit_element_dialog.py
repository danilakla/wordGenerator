import re
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
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
from ui.views.edit_formula_dialog import EditFormulaDialog
from typing import List, Dict

from util.text_util import TextUtils


class EditElementDialog(QDialog):
    def __init__(self, element: Element, tree: List[Element]):
        super().__init__()
        self.element = element
        self.tree = tree
        self.fields: Dict[str, any] = {}
        self.setWindowTitle(f"Edit {type(element).__name__}")
        layout = QVBoxLayout()

        if isinstance(element, Header):
            self.fields['text'] = QLineEdit(TextUtils.extract_text_after_leading_numbers(element.text))
            layout.addWidget(QLabel("""Название:"""))
            layout.addWidget(self.fields['text'])
            self.resize(300,100)  # Увеличиваем размер диалога формулы

        elif isinstance(element, Paragraph):
            self.fields['text'] = QTextEdit(element.text)  # Заменяем QLineEdit на QTextEdit
            layout.addWidget(QLabel("""Текст: (При редактировании текста просто вносите изменения — новые абзацы создавать не нужно.)"""))
            layout.addWidget(self.fields['text'])
            self.resize(800, 600)  # Увеличиваем размер диалога формулы
            
        elif isinstance(element, Table):
            dialog = EditTableDialog(element)
            dialog.resize(800, 600)  # Увеличиваем размер диалога таблицы
            self.fields['table_dialog'] = dialog
        elif isinstance(element, Image):
            self.resize(300,200)
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
            self.fields['path'] = QLineEdit()
            btn_browse = QPushButton("Browse")
            btn_browse.clicked.connect(self.browse_image)
            path_layout = QHBoxLayout()
            path_layout.addWidget(self.fields['path'])
            path_layout.addWidget(btn_browse)
            layout.addWidget(QLabel("Путь к картинке:"))
            layout.addLayout(path_layout)
        elif isinstance(element, Listing):
            self.fields['text'] = QTextEdit(element.text)  # Заменяем QTextEdit на QTextEdit
            self.fields['caption'] = QLineEdit(TextUtils.clean_caption(element.caption))
            layout.addWidget(QLabel("Содержимое: Укажите скрипт (код)."))
            layout.addWidget(self.fields['text'])
            layout.addWidget(QLabel("Подпись:"))
            layout.addWidget(self.fields['caption'])
            self.resize(800, 600)
        elif isinstance(element, ListElement):
            dialog = EditListDialog(element)
            dialog.resize(500, 400)  # Увеличиваем размер диалога списка
            self.fields['list_dialog'] = dialog
        elif isinstance(element, Formula):
            dialog = EditFormulaDialog(element)
            dialog.resize(300,150)  # Увеличиваем размер диалога формулы
            self.fields['formula_dialog'] = dialog

        if not isinstance(element, (Table, ListElement, Formula)):
            btn_save = QPushButton("Save")
            btn_save.clicked.connect(self.accept)
            layout.addWidget(btn_save)

        self.setLayout(layout)

    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.fields['path'].setText(file_name)

    def get_data(self) -> Dict:
        data = {}
        if isinstance(self.element, Header):
            data['text'] = TextUtils.extract_text_after_leading_numbers(self.fields['text'].text())
        elif isinstance(self.element, Paragraph):
            data['text'] = self.fields['text'].toPlainText()  # Изменяем метод получения текста
        elif isinstance(self.element, Table):
            data = self.fields['table_dialog'].get_data()
        elif isinstance(self.element, Image):
            data['caption'] = TextUtils.clean_caption(self.fields['caption'].text())
            path = self.fields['path'].text()
            if path:
                data['image_path'] = path
        elif isinstance(self.element, Listing):
            data['text'] = self.fields['text'].toPlainText()  # Изменяем метод получения текста
            data['caption'] = TextUtils.clean_caption(self.fields['caption'].text())
        elif isinstance(self.element, ListElement):
            data = self.fields['list_dialog'].get_data()
        elif isinstance(self.element, Formula):
            data = self.fields['formula_dialog'].get_data()
        return data

    def exec(self):
        if isinstance(self.element, (Table, ListElement, Formula)):
            return self.fields['table_dialog' if isinstance(self.element, Table) else 'list_dialog' if isinstance(self.element, ListElement) else 'formula_dialog'].exec()
        return super().exec()