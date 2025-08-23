# document_choice.py
from PyQt6.QtWidgets import QDialog, QRadioButton, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout
from services.document_service import DocumentService

class DocumentChoiceDialog(QDialog):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Создать или загрузить документ")
        layout = QVBoxLayout()

        self.radio_new = QRadioButton("Создать новый документ")
        self.radio_new.setChecked(True)
        self.radio_load = QRadioButton("Загрузить существующий")
        layout.addWidget(self.radio_new)
        layout.addWidget(self.radio_load)

        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Имя нового документа")
        layout.addWidget(self.new_name)

        self.load_path = QLineEdit()
        self.load_path.setPlaceholderText("Путь к файлу")
        self.btn_browse = QPushButton("Обзор")
        self.btn_browse.clicked.connect(self.browse_file)
        self.load_layout = QHBoxLayout()
        self.load_layout.addWidget(self.load_path)
        self.load_layout.addWidget(self.btn_browse)
        layout.addLayout(self.load_layout)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.process_choice)
        layout.addWidget(btn_ok)

        self.setLayout(layout)

        self.radio_new.toggled.connect(self.update_visibility)
        self.radio_load.toggled.connect(self.update_visibility)
        self.update_visibility()

    def update_visibility(self):
        self.new_name.setVisible(self.radio_new.isChecked())
        self.load_path.setVisible(self.radio_load.isChecked())
        self.btn_browse.setVisible(self.radio_load.isChecked())

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Word files (*.docx)")
        if path:
            self.load_path.setText(path)

    def process_choice(self):
        if self.radio_new.isChecked():
            name = self.new_name.text()
            if name:
                self.service.create_new_document(name)
                self.accept()
        elif self.radio_load.isChecked():
            path = self.load_path.text()
            if path:
                self.service.load_document(path)
                self.accept()