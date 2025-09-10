from PyQt6.QtWidgets import QDialog,QMessageBox, QComboBox,QLabel, QPushButton, QFileDialog, QVBoxLayout, QGroupBox
from PyQt6.QtCore import Qt
from services.document_service import DocumentService

class FolderSelectionDialog(QDialog):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Выбор папки для сохранения")
        self.resize(500, 200)  # Увеличиваем размер окна
        
        layout = QVBoxLayout()
        uni_group = QGroupBox("Выберите ваш университет")
        uni_layout = QVBoxLayout()

        uni_label = QLabel("Если вашего университета нет в списке — выберите пункт по умолчанию")
        uni_layout.addWidget(uni_label)

        self.university_selector = QComboBox()
        # Словарь для маппинга RU → EN
        self.universities = {
            "По умолчанию": "",
            "БГУ — Белорусский государственный университет": "BSU",
            "БГТУ — Белорусский государственный технологический университет": "BSTU",
            "БГЭУ — Белорусский государственный экономический университет": "BSEU",
            "БНТУ — Белорусский национальный технический университет": "BNTU",
            "БГУИР — Белорусский государственный университет информатики и радиоэлектроники": "BSUIR",
        }

        # Добавляем все ключи (русские названия)
        self.university_selector.addItems(self.universities.keys())
        uni_layout.addWidget(self.university_selector)

        uni_group.setLayout(uni_layout)
        layout.addWidget(uni_group)
        
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

    def select_folder(self, checked=False):
        selected_uni_ru = self.university_selector.currentText()
        selected_uni_en = self.universities[selected_uni_ru]

        # if selected_uni_en == "":
        #     QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите университет из списка.")
        #     return

        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if folder:
            # Сохраняем выбор
            self.service.set_save_folder(folder)
            self.service.university=selected_uni_en  # предположим, у сервиса есть такой метод
            self.accept()