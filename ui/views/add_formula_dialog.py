from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QMessageBox, QSpinBox, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt
from elements.element import Element
from typing import List, Optional
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from PyQt6.QtCore import QUrl

from PyQt6.QtGui import QDesktopServices

class AddFormulaDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить формулу")
        layout = QVBoxLayout()
        video_label = QLabel(
            'Чтобы понять, как пользоваться сервисом ниже, можно посмотреть видео. Просто нажмите на ссылку, и откроется ролик: '
            '<a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1">Watch Tutorial Video</a>'
        )
        video_label.setOpenExternalLinks(True)
        video_label.linkActivated.connect(self.open_url)
        layout.addWidget(video_label)
        
        editor_label = QLabel(
            'Если нужно собрать формулу и вставить её в текст, есть удобный онлайн-сервис. Переходите по ссылке, и он откроется: '
            '<a href="https://latexeditor.lagrida.com/">LaTeX Equation Editor</a>'
        )
        editor_label.setOpenExternalLinks(True)
        editor_label.linkActivated.connect(self.open_url)
        layout.addWidget(editor_label)

        # Add spacing for better readability
        layout.addSpacing(10)

        
        self.formula_edit = QLineEdit()
        layout.addWidget(QLabel("Формула (LaTeX):"))
        layout.addWidget(self.formula_edit)



        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)
    def open_url(self, url: str, checked=False):
        QDesktopServices.openUrl(QUrl(url))
    def get_data(self) -> tuple[Optional[Element], Optional[Element], str, str]:
        formula = self.formula_edit.text()
        return None, None, formula, ""