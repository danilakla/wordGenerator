from PyQt6.QtWidgets import QDialog, QLabel, QTextEdit, QVBoxLayout, QPushButton
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
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str]:
        text = self.text_edit.toPlainText()  # Изменяем метод получения текста
        paragraphs = text.split('\n')
        
        # Убираем пустые абзацы (если пользователь оставил пустые строки)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return None, None, paragraphs