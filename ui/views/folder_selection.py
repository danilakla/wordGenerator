from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QFileDialog, QVBoxLayout

from services.document_service import DocumentService

class FolderSelectionDialog(QDialog):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Выбор папки для сохранения")
        layout = QVBoxLayout()
        self.label = QLabel("Выберите папку:")
        layout.addWidget(self.label)
        self.btn_select = QPushButton("Выбрать папку")
        self.btn_select.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select)
        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self.service.set_save_folder(folder)
            self.accept()