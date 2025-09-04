import os
from PyQt6.QtWidgets import QDialog, QMessageBox,QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QFileDialog
from elements.element import Element
from typing import List, Optional
class AddImageDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить рисунок")
        layout = QVBoxLayout()
        self.resize(300,200)
        self.caption_edit = QLineEdit()
        layout.addWidget(QLabel("Подпись:"))
        layout.addWidget(self.caption_edit)

        self.path_edit = QLineEdit()
        btn_browse = QPushButton("Обзор")
        btn_browse.clicked.connect(self.browse_image)
        path_layout = QVBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(btn_browse)
        layout.addWidget(QLabel("Путь к картинке:"))
        layout.addLayout(path_layout)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.validate_and_accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)
    def validate_input(self) -> bool:
        """Validate the input path"""
        path = self.path_edit.text().strip()
        
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
    def validate_and_accept(self,checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input():
            self.accept()
    def browse_image(self, checked=False):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.path_edit.setText(path)

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str, str]:
        path = self.path_edit.text()
        caption = self.caption_edit.text()
        return None, None, path, caption