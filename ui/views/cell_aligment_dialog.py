from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class CellAlignmentDialog(QDialog):
    def __init__(self, parent=None, current_data=None):
        super().__init__(parent)
        self.setWindowTitle("Выравнивание ячейки")
        align_layout = QVBoxLayout()
        # Добавьте mapping словари в ваш класс
        self.horiz_mapping = {
            "по центру": "center",
            "слева": "left", 
            "справа": "right",
            "по ширине": "justify"
            }

        self.vert_mapping = {
            "по центру": "center",
            "сверху": "top",
            "снизу": "bottom", 
            "оба": "both"
        }
        # Горизонтальное выравнивание
        horiz_label = QLabel("Горизонтальное выравнивание:")
        self.horiz_combo = QComboBox()
        self.horiz_combo.addItems(["по ширине","по центру", "слева", "справа"])  # Русские названия
        align_layout.addWidget(horiz_label)
        align_layout.addWidget(self.horiz_combo)
        
        vert_label = QLabel("Вертикальное выравнивание:")
        self.vert_combo = QComboBox()
        self.vert_combo.addItems(["по центру", "сверху", "снизу", "оба"])  # Русские названия
        align_layout.addWidget(vert_label)
        align_layout.addWidget(self.vert_combo)

        # Установка текущих значений, если они есть

        # Тогда установка значений будет такой:
        self.reverse_horiz_mapping = {v: k for k, v in self.horiz_mapping.items()}
        self.reverse_vert_mapping = {v: k for k, v in self.vert_mapping.items()}
        if current_data:
            horiz_value = current_data.get('horizontal', 'center')
            vert_value = current_data.get('vertical', 'center')
            
            self.horiz_combo.setCurrentText(self.reverse_horiz_mapping.get(horiz_value, 'по центру'))
            self.vert_combo.setCurrentText(self.reverse_vert_mapping.get(vert_value, 'по центру'))
            self.horiz_combo.setCurrentText(current_data.get('horizontal', 'center'))
            self.vert_combo.setCurrentText(current_data.get('vertical', 'center'))

        # Кнопка сохранения
        btn_save_align = QPushButton("Сохранить")
        btn_save_align.clicked.connect(self.accept)
        align_layout.addWidget(btn_save_align)

        self.setLayout(align_layout)

    def get_data(self):
        return {
            'horizontal': self.horiz_mapping[self.horiz_combo.currentText()],
            'vertical': self.vert_mapping[self.vert_combo.currentText()]
        }