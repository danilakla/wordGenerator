from PyQt6.QtWidgets import QDialog, QLabel, QListWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from elements.list_element import ListElement
from typing import List

class EditListDialog(QDialog):
    def __init__(self, list_element: ListElement):
        super().__init__()
        self.list_element = list_element
        self.setWindowTitle("Редактировать список")
        layout = QVBoxLayout()

        # Список элементов
        self.items_list = QListWidget()
        layout.addWidget(QLabel("Элементы списка:"))
        layout.addWidget(self.items_list)

        # Заполняем список текущими элементами
        for item in list_element.items:
            self.items_list.addItem(item)

        # Поле для ввода/редактирования элемента
        add_item_layout = QHBoxLayout()
        self.item_edit = QLineEdit()
        btn_add_item = QPushButton("Добавить элемент")
        btn_add_item.clicked.connect(self.add_item)
        btn_edit_item = QPushButton("Редактировать элемент")
        btn_edit_item.clicked.connect(self.edit_item)
        btn_remove_item = QPushButton("Удалить элемент")
        btn_remove_item.clicked.connect(self.remove_item)
        add_item_layout.addWidget(self.item_edit)
        add_item_layout.addWidget(btn_add_item)
        add_item_layout.addWidget(btn_edit_item)
        add_item_layout.addWidget(btn_remove_item)
        layout.addLayout(add_item_layout)

        # Кнопка сохранения
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)
        self.update_item_separators()

    def add_item(self):
        text = self.item_edit.text().strip()
        if text:
            # Первая буква маленькая
            text = text[0].lower() + text[1:] if len(text) > 1 else text.lower()
            # Очистка существующих окончаний
            if text.endswith(";") or text.endswith("."):
                text = text[:-1]
            # Добавляем элемент
            self.items_list.addItem(text)
            self.item_edit.clear()
            self.update_item_separators()

    def edit_item(self):
        selected = self.items_list.selectedItems()
        if selected:
            text = self.item_edit.text().strip()
            if text:
                # Первая буква маленькая
                text = text[0].lower() + text[1:] if len(text) > 1 else text.lower()
                # Очистка существующих окончаний
                if text.endswith(";") or text.endswith("."):
                    text = text[:-1]
                # Обновляем выделенный элемент
                selected[0].setText(text)
                self.item_edit.clear()
                self.update_item_separators()

    def remove_item(self):
        selected = self.items_list.selectedItems()
        if selected:
            for item in selected:
                self.items_list.takeItem(self.items_list.row(item))
            self.update_item_separators()

    def update_item_separators(self):
        """Обновляет разделители (; или .) для элементов списка."""
        count = self.items_list.count()
        for i in range(count):
            item = self.items_list.item(i)
            base_text = item.text().rstrip(";.")
            if i < count - 1:
                item.setText(base_text + ";")
            else:
                item.setText(base_text + ".")

    def get_data(self) -> dict:
        items = [self.items_list.item(i).text() for i in range(self.items_list.count())]
        return {"list_type": self.list_element.list_type, "items": items}