from PyQt6.QtWidgets import QDialog, QMessageBox,QLabel, QLineEdit, QVBoxLayout, QPushButton
from elements.formula import Formula
from typing import Dict
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

class EditFormulaDialog(QDialog):
    def __init__(self, element: Formula):
        super().__init__()
        self.element = element
        self.setWindowTitle("Edit Formula")
        layout = QVBoxLayout()
        video_label = QLabel(
            'Чтобы отредактировать формулу, сначала посмотри обучающий туториал: '
            '<a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1">Watch Tutorial Video</a>'
        )
        video_label.setOpenExternalLinks(True)
        video_label.linkActivated.connect(self.open_url)
        layout.addWidget(video_label)

        # Add LaTeX equation editor link
        editor_label = QLabel(
            'Если нужно собрать формулу и вставить её в текст, есть удобный онлайн-сервис. Переходите по ссылке, и он откроется. '
            '<a href="https://latexeditor.lagrida.com/">LaTeX Equation Editor</a>'
        )
        editor_label.setOpenExternalLinks(True)
        editor_label.linkActivated.connect(self.open_url)
        layout.addWidget(editor_label)

        # Add spacing for better readability
        layout.addSpacing(10)
        self.formula_field = QLineEdit()
        layout.addWidget(QLabel("LaTeX Formula:"))
        layout.addWidget(self.formula_field)


        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.validate_and_accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)
    def validate_input(self) -> bool:
        """Validate that formula field is not empty"""
        formula = self.formula_field.text().strip()
        
        # Check for empty formula
        if not formula:
            QMessageBox.warning(self, "Ошибка", "Поле формулы не может быть пустым! Введите формулу в формате LaTeX.")
            return False
        
        return True

    def validate_and_accept(self, checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input():
            self.accept()
    def open_url(self, url: str, checked=False):
        QDesktopServices.openUrl(QUrl(url))
    def get_data(self) -> Dict:
        return {
            'formula': self.formula_field.text(),
            'caption': self.element.caption
        }