from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
class ControlPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        btn_add_header = QPushButton("Добавить раздел")
        btn_add_header.clicked.connect(self.main_window.add_header)
        layout.addWidget(btn_add_header)

        btn_add_subheader = QPushButton("Добавить подраздел")
        btn_add_subheader.clicked.connect(self.main_window.add_subheader)
        layout.addWidget(btn_add_subheader)

        btn_add_text = QPushButton("Добавить текст")
        btn_add_text.clicked.connect(self.main_window.add_text)
        layout.addWidget(btn_add_text)

        btn_add_table = QPushButton("Добавить таблицу")
        btn_add_table.clicked.connect(self.main_window.add_table)
        layout.addWidget(btn_add_table)

        btn_add_image = QPushButton("Добавить рисунок")
        btn_add_image.clicked.connect(self.main_window.add_image)
        layout.addWidget(btn_add_image)

        btn_add_listing = QPushButton("Добавить листинг")
        btn_add_listing.clicked.connect(self.main_window.add_listing)
        layout.addWidget(btn_add_listing)

        btn_add_list = QPushButton("Добавить список")
        btn_add_list.clicked.connect(self.main_window.add_list)
        layout.addWidget(btn_add_list)

        btn_add_formula = QPushButton("Добавить формулу")
        btn_add_formula.clicked.connect(self.main_window.add_formula)
        layout.addWidget(btn_add_formula)

        btn_remove = QPushButton("Удалить элемент")
        btn_remove.clicked.connect(self.main_window.remove_element)
        layout.addWidget(btn_remove)

        btn_edit = QPushButton("Редактировать элемент")
        btn_edit.clicked.connect(self.main_window.edit_element)
        layout.addWidget(btn_edit)

        btn_move = QPushButton("Переместить элемент")
        btn_move.clicked.connect(self.main_window.move_element)
        layout.addWidget(btn_move)

        btn_save = QPushButton("Сохранить документ")
        btn_save.clicked.connect(self.main_window.save_document)
        layout.addWidget(btn_save)

        self.setLayout(layout)