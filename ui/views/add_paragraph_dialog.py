from PyQt6.QtWidgets import QDialog, QLabel, QTextEdit, QVBoxLayout, QPushButton,QMessageBox
from elements.element import Element
from typing import List, Optional

class AddParagraphDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить текст")
        self.resize(600, 400)  # Увеличиваем размер окна
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()  # Заменяем QLineEdit на QTextEdit
        layout.addWidget(QLabel("""Текст: (Нажмите Enter, чтобы начать новый абзац. 
                                Каждый раз, когда вы нажимаете Enter, программа воспринимает текст дальше как отдельный параграф. 
                                Так можно легко написать несколько абзацев подряд.)"""))
        layout.addWidget(self.text_edit)

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

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str]:
        text = self.text_edit.toPlainText()  # Изменяем метод получения текста
        paragraphs = text.split('\n')
        
        # Убираем пустые абзацы (если пользователь оставил пустые строки)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return None, None, paragraphs