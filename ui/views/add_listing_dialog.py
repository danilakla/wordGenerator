from PyQt6.QtWidgets import QDialog, QLabel,QMessageBox, QLineEdit, QTextEdit, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout
from elements.element import Element
from typing import List, Optional
class AddListingDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить листинг")
        self.resize(600, 500)  # Увеличиваем размер окна
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()  # Заменяем QLineEdit на QTextEdit
        layout.addWidget(QLabel("Содержимое: Укажите скрипт (код)."))
        layout.addWidget(self.text_edit)

        self.caption_edit = QLineEdit()
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.validate_and_accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)
    def validate_and_accept(self, checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input():
            self.accept()
    def validate_input(self) -> bool:
        """Validate the input text"""
        text = self.text_edit.toPlainText()
        
        # Check for empty string or only spaces
        if not text:
            QMessageBox.warning(self, "Ошибка", "Невозможно отправить пустую строку или только пробелы!")
            return False
        
        return True
    def get_data(self):
        text = self.text_edit.toPlainText()  # Изменяем метод получения текста
        caption = self.caption_edit.text()
        return None, None, text, caption