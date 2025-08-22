from PyQt6.QtWidgets import QDialog, QRadioButton, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout

from services.document_service import DocumentService
from PyQt6.QtWidgets import QDialog, QRadioButton, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout

class DocumentChoiceDialog(QDialog):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Создать или загрузить документ")
        layout = QVBoxLayout()

        self.radio_new = QRadioButton("Создать новый документ")
        self.radio_load = QRadioButton("Загрузить существующий")
        layout.addWidget(self.radio_new)
        layout.addWidget(self.radio_load)

        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Имя нового документа")
        layout.addWidget(self.new_name)

        self.load_path = QLineEdit()
        self.load_path.setPlaceholderText("Путь к файлу")
        btn_browse = QPushButton("Обзор")
        btn_browse.clicked.connect(self.browse_file)
        load_layout = QHBoxLayout()
        load_layout.addWidget(self.load_path)
        load_layout.addWidget(btn_browse)
        layout.addLayout(load_layout)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.process_choice)
        layout.addWidget(btn_ok)

        self.setLayout(layout)

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