import os
import re
from PyQt6.QtWidgets import QDialog,QMessageBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
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
            self.fields['text'] = QTextEdit()  # Заменяем QTextEdit на QTextEdit
            # print(f"Text from QTextEdit: {repr(element.text)}")
            self.fields['text'].setPlainText(element.text)
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

        if not isinstance(self.element, (Table, ListElement, Formula)):
            btn_save = QPushButton("Save")
            # For Header elements, use validate_and_accept, for others use accept
            if isinstance(self.element, Header):
                btn_save.clicked.connect(self.validate_and_accept)
            elif isinstance(self.element,Paragraph):
                btn_save.clicked.connect(self.validate_and_accept_paragraph)
            elif isinstance(self.element,Image):
                btn_save.clicked.connect(self.validate_and_accept_image)
            elif isinstance(self.element,Listing):
                btn_save.clicked.connect(self.validate_and_accept_listing)

            else:
                btn_save.clicked.connect(self.accept)
            layout.addWidget(btn_save)

        self.setLayout(layout)
    
    def validate_and_accept_listing(self, checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input_listing():
            self.accept()
    def validate_input_listing(self) -> bool:
        """Validate the input text"""
        text = self.fields['text'].toPlainText()
        
        # Check for empty string or only spaces
        if not text:
            QMessageBox.warning(self, "Ошибка", "Невозможно отправить пустую строку или только пробелы!")
            return False
        
        return True
    def validate_input_image(self) -> bool:
        """Validate the input path"""
        path = self.fields['path'].text().strip()
        
        # Check for empty path
        if not path:
            QMessageBox.warning(self, "Ошибка", "Путь к изображению не может быть пустым!")
            return False
        
        # Check if file exists
        if not os.path.exists(path):
            QMessageBox.warning(self, "Ошибка", f"Файл не существует:\n{path}")
            return False
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Ошибка", f"Указанный путь ведет к папке, а не к файлу:\n{path}")
            return False
        
        # Check if it's a valid image file extension
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
        file_extension = os.path.splitext(path)[1].lower()
        if file_extension not in valid_extensions:
            QMessageBox.warning(self, "Ошибка", 
                               f"Неподдерживаемый формат изображения: {file_extension}\n"
                               f"Поддерживаемые форматы: {', '.join(valid_extensions)}")
            return False
        
        return True
    def validate_and_accept_image(self,checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input_image():
            self.accept()
    
    def validate_input(self) -> bool:
        """Validate the input text for Header elements"""
        if isinstance(self.element, Header):
            text = self.fields['text'].text().strip()
            
            # Check for empty string or only spaces
            if not text:
                QMessageBox.warning(self, "Ошибка", "Невозможно отправить пустую строку или только пробелы!")
                return False
            
            # Check if text starts with a number
            if text[0].isdigit():
                QMessageBox.warning(self, "Ошибка", "Невозможно начать текст с цифры! Первый символ должен быть буквой.")
                return False
            
            # Check if first character is a letter
            if not text[0].isalpha():
                QMessageBox.warning(self, "Ошибка", "Первый символ должен быть буквой!")
                return False
            
        return True

    def validate_and_accept(self,checked=False):
        """Validate input before accepting the dialog (for Header elements)"""
        if self.validate_input():
            self.accept()

    def validate_and_accept_paragraph(self, checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input_paragraph():
            self.accept()
    def validate_input_paragraph(self) -> bool:
        """Validate the input text"""
        text = self.fields['text'].toPlainText()
        
        if not text:
            QMessageBox.warning(self, "Ошибка", "Невозможно отправить пустую строку или только пробелы!")
            return False
        
        return True
    def browse_image(self, checked=False):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.fields['path'].setText(file_name)

    def get_data(self) -> Dict:
        data = {}
        if isinstance(self.element, Header):
            data['text'] = TextUtils.extract_text_after_leading_numbers(self.fields['text'].text().strip())
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
            data['text'] = self.fields['text'].toPlainText() 
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