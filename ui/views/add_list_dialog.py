from PyQt6.QtWidgets import QDialog, QLabel, QListWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit
from elements.element import Element
from typing import List, Optional

class AddListDialog(QDialog):
    def __init__(self, tree: List[Element]):
        super().__init__()
        self.tree = tree
        self.setWindowTitle("Добавить список")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Чтобы отредактировать: введите новый текст, выделите элемент и нажмите 'Редактировать'."
            "\nЧтобы удалить: выберите элемент и нажмите 'Удалить'."
        ))
        self.items_list = QListWidget()
        layout.addWidget(QLabel("Элементы списка:"))
        layout.addWidget(self.items_list)

        add_item_layout = QHBoxLayout()
        self.item_edit = QLineEdit()
        self.item_edit.setPlaceholderText("Введите текст нового элемента или новый текст для редактирования")
            
        btn_add_item = QPushButton("Добавить элемент")
        btn_add_item.setToolTip("Введите текст и нажмите, чтобы добавить новый элемент")
        btn_add_item.clicked.connect(self.add_item)
        btn_edit_item = QPushButton("Редактировать элемент")
        btn_edit_item.setToolTip("Введите новый текст, выберите элемент и нажмите для замены")
        btn_edit_item.clicked.connect(self.edit_item)
        
        btn_remove_item = QPushButton("Удалить элемент")
        btn_remove_item.setToolTip("Выберите элемент в списке и нажмите, чтобы удалить его")
        btn_remove_item.clicked.connect(self.remove_item)
        add_item_layout.addWidget(self.item_edit)
        add_item_layout.addWidget(btn_add_item)
        add_item_layout.addWidget(btn_edit_item)
        add_item_layout.addWidget(btn_remove_item)
        layout.addLayout(add_item_layout)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def add_item(self, checked=False):
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

    def edit_item(self, checked=False):
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

    def remove_item(self, checked=False):
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

    def get_data(self):
        items = [self.items_list.item(i).text() for i in range(self.items_list.count())]
        list_type = "–"
        return None, None, items, list_type