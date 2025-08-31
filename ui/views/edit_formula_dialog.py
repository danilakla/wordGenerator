from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton
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
        self.formula_field = QLineEdit(element.formula)
        layout.addWidget(QLabel("LaTeX Formula:"))
        layout.addWidget(self.formula_field)


        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)
    def open_url(self, url: str, checked=False):
        QDesktopServices.openUrl(QUrl(url))
    def get_data(self) -> Dict:
        return {
            'formula': self.formula_field.text(),
            'caption': self.element.caption
        }