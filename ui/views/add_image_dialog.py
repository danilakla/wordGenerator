from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QFileDialog
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
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.path_edit.setText(path)

    def get_data(self) -> tuple[Optional[Element], Optional[Element], str, str]:
        path = self.path_edit.text()
        caption = self.caption_edit.text()
        return None, None, path, caption