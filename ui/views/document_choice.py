from PyQt6.QtWidgets import QDialog, QRadioButton, QLineEdit, QMessageBox, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QButtonGroup

class DocumentChoiceDialog(QDialog):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setWindowTitle("Создать или загрузить документ")
        self.resize(600, 400)

        layout = QVBoxLayout()

        # Радио кнопки
        self.radio_new = QRadioButton("Создать новый документ")
        self.radio_load = QRadioButton("""Загрузка существующего документа (Программа может обработать документ только при условии, 
                                       что он соответствует установленным стандартам оформления. 
                                       Документ должен содержать разделы и их содержимое.)""")
        if self.service.active:
            self.radio_load.setEnabled(False)
            
        self.radio_new.setChecked(True)

        # Объединяем в группу, чтобы только одна могла быть выбрана
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_new)
        self.radio_group.addButton(self.radio_load)

        layout.addWidget(self.radio_new)
        layout.addWidget(self.radio_load)

        # Поля для нового документа
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя нового документа:"))
        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Введите имя документа")
        name_layout.addWidget(self.new_name)
        layout.addLayout(name_layout)

        # Поля для загрузки
        path_layout = QHBoxLayout()
        self.load_path = QLineEdit()
        self.load_path.setPlaceholderText("Путь к файлу")
        self.btn_browse = QPushButton("Обзор")
        self.btn_browse.clicked.connect(self.browse_file)
        path_layout.addWidget(self.load_path)
        path_layout.addWidget(self.btn_browse)
        layout.addLayout(path_layout)

        # Кнопка подтверждения
        btn_ok = QPushButton("Продолжить")
        btn_ok.clicked.connect(self.process_choice)
        layout.addWidget(btn_ok)

        self.setLayout(layout)

        self.radio_new.toggled.connect(self.update_visibility)
        self.radio_load.toggled.connect(self.update_visibility)
        self.update_visibility()

    def update_visibility(self, checked=False):
        self.new_name.setEnabled(self.radio_new.isChecked())
        self.load_path.setEnabled(self.radio_load.isChecked())
        self.btn_browse.setEnabled(self.radio_load.isChecked())

    def browse_file(self, checked=False):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Word files (*.docx)")
        if path:
            self.load_path.setText(path)

    def process_choice(self, checked=False):
        if self.radio_new.isChecked():
            name = self.new_name.text()
            if name:
                self.service.create_new_document(name)
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Введите имя документа")
        elif self.radio_load.isChecked():
            path = self.load_path.text()
            if path:
                try:
                    self.service.load_document(path)
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить документ: {str(e)}")
            else:
                QMessageBox.warning(self, "Ошибка", "Выберите файл для загрузки")
