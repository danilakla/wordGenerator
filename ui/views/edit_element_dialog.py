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

class EditElementDialog(QDialog):
    def __init__(self, element: Element, tree: List[Element]):
        super().__init__()
        self.element = element
        self.tree = tree
        self.fields: Dict[str, any] = {}
        self.setWindowTitle(f"Edit {type(element).__name__}")
        layout = QVBoxLayout()

        if isinstance(element, Header):
            self.fields['text'] = QLineEdit(element.text)
            layout.addWidget(QLabel("Text:"))
            layout.addWidget(self.fields['text'])
        elif isinstance(element, Paragraph):
            self.fields['text'] = QLineEdit(element.text)
            layout.addWidget(QLabel("Text:"))
            layout.addWidget(self.fields['text'])
        elif isinstance(element, Table):
            dialog = EditTableDialog(element)
            self.fields['table_dialog'] = dialog
        elif isinstance(element, Image):
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Caption:"))
            layout.addWidget(self.fields['caption'])
            self.fields['path'] = QLineEdit()
            btn_browse = QPushButton("Browse")
            btn_browse.clicked.connect(self.browse_image)
            path_layout = QHBoxLayout()
            path_layout.addWidget(self.fields['path'])
            path_layout.addWidget(btn_browse)
            layout.addWidget(QLabel("New image path (optional):"))
            layout.addLayout(path_layout)
        elif isinstance(element, Listing):
            self.fields['text'] = QTextEdit(element.text)
            self.fields['caption'] = QLineEdit(element.caption)
            layout.addWidget(QLabel("Content:"))
            layout.addWidget(self.fields['text'])
            layout.addWidget(QLabel("Caption:"))
            layout.addWidget(self.fields['caption'])
        elif isinstance(element, ListElement):
            dialog = EditListDialog(element)
            self.fields['list_dialog'] = dialog
        elif isinstance(element, Formula):
            dialog = EditFormulaDialog(element)
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

    def extract_text_after_leading_numbers(self, text: str) -> str:
        cleaned_text = re.sub(r"^(\d+[\.\d]*\s*)+", "", text).strip()
        return cleaned_text if cleaned_text else text

    def clean_caption(self, caption: str) -> str:
        patterns = [
            r'^Table \d+\.\d+ – .+$',
            r'^Figure \d+\.\d+ – .+$',
            r'^Listing \d+\.\d+ – .+$'
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
            data = self.fields['formula_dialog'].get_data()
        return data

    def exec(self):
        if isinstance(self.element, (Table, ListElement, Formula)):
            return self.fields['table_dialog' if isinstance(self.element, Table) else 'list_dialog' if isinstance(self.element, ListElement) else 'formula_dialog'].exec()
        return super().exec()