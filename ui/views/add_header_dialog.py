from PyQt6.QtWidgets import QMessageBox,QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton
from typing import List
from elements.element import Element
from elements.header import Header

class AddHeaderDialog(QDialog):
    def __init__(self, tree: List[Element], is_sub: bool):
        super().__init__()
        self.tree = tree
        self.is_sub = is_sub
        self.setWindowTitle("Добавить раздел" if not is_sub else "Добавить подраздел")
        self.resize(300,150)
        layout = QVBoxLayout()

        self.text_edit = QLineEdit()
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.text_edit)

        if not is_sub:
            self.level = 1
            self.parent_combo = None
            self.after_combo = QComboBox()
            self._populate_after_combo_for_top_level(self.after_combo, tree)
            layout.addWidget(QLabel("Укажите, после какого раздела он должен появиться:"))
            layout.addWidget(self.after_combo)
        else:
            self.level_combo = None
            self.parent_combo = QComboBox()
            self._populate_combo(self.parent_combo, tree, "")
            layout.addWidget(QLabel("Выберите раздел, в который хотите добавить новый :"))
            layout.addWidget(self.parent_combo)

            self.after_combo = QComboBox()
            layout.addWidget(QLabel("Укажите, после какого раздела он должен появиться:"))
            layout.addWidget(self.after_combo)

            self.parent_combo.currentIndexChanged.connect(self.update_after_combo)
            self.update_after_combo()

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.validate_and_accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def _populate_combo(self, combo: QComboBox, elements: List[Element], prefix: str):
        for elem in elements:
            if isinstance(elem, Header):
                combo.addItem(prefix + elem.text, elem)
                if hasattr(elem, 'children'):
                    self._populate_combo(combo, elem.children, prefix + "  ")

    def _populate_after_combo_for_top_level(self, combo: QComboBox, elements: List[Element]):
        for elem in elements:
            if isinstance(elem, Header) and elem.level == 1:
                combo.addItem(elem.text, elem)

    def update_after_combo(self, checked=False):
        self.after_combo.clear()
        idx = self.parent_combo.currentIndex()
        if idx >= 0:
            parent = self.parent_combo.itemData(idx)
            if parent and hasattr(parent, 'children'):
                for elem in parent.children:
                    if isinstance(elem, Header) and elem.level == parent.level + 1:
                        self.after_combo.addItem(elem.text, elem)
    def validate_and_accept(self, checked=False):
        """Validate input before accepting the dialog"""
        if self.validate_input():
            self.accept()
    def validate_input(self) -> bool:
        """Validate the input text"""
        text = self.text_edit.text().strip()
        
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
    def get_data(self):
        after = self.after_combo.currentData() if self.after_combo.currentIndex() >= 0 else None
        text = self.text_edit.text().strip()
        if self.is_sub:
            parent = self.parent_combo.currentData() if self.parent_combo.currentIndex() >= 0 else None
            level = parent.level + 1 if parent else 1
            return parent, after, text, level
        else:
            return None, after, text, self.level