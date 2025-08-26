from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QFileDialog, QVBoxLayout, QGroupBox
from PyQt6.QtCore import Qt
from services.document_service import DocumentService

class FolderSelectionDialog(QDialog):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Выбор папки для сохранения")
        self.resize(500, 200)  # Увеличиваем размер окна
        
        layout = QVBoxLayout()
        
        # Группа для выбора папки
        group = QGroupBox("Выберите папку для сохранения документов")
        group_layout = QVBoxLayout()
        
        group_layout.addWidget(QLabel("Папка будет использоваться для сохранения всех создаваемых документов"))
        
        self.btn_select = QPushButton("Выбрать папку")
        self.btn_select.clicked.connect(self.select_folder)
        group_layout.addWidget(self.btn_select)
        
        group.setLayout(group_layout)
        layout.addWidget(group)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if folder:
            self.service.set_save_folder(folder)
            self.accept()