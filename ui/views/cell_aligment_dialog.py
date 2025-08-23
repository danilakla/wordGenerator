from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class CellAlignmentDialog(QDialog):
    def __init__(self, parent=None, current_data=None):
        super().__init__(parent)
        self.setWindowTitle("Выравнивание ячейки")
        align_layout = QVBoxLayout()

        # Горизонтальное выравнивание
        horiz_label = QLabel("Горизонтальное выравнивание:")
        self.horiz_combo = QComboBox()
        self.horiz_combo.addItems(["center", "left", "right", "justify"])
        align_layout.addWidget(horiz_label)
        align_layout.addWidget(self.horiz_combo)

        # Вертикальное выравнивание
        vert_label = QLabel("Вертикальное выравнивание:")
        self.vert_combo = QComboBox()
        self.vert_combo.addItems(["center", "top", "bottom", "both"])
        align_layout.addWidget(vert_label)
        align_layout.addWidget(self.vert_combo)

        # Установка текущих значений, если они есть
        if current_data:
            self.horiz_combo.setCurrentText(current_data.get('horizontal', 'center'))
            self.vert_combo.setCurrentText(current_data.get('vertical', 'center'))

        # Кнопка сохранения
        btn_save_align = QPushButton("Сохранить")
        btn_save_align.clicked.connect(self.accept)
        align_layout.addWidget(btn_save_align)

        self.setLayout(align_layout)

    def get_data(self):
        return {
            'horizontal': self.horiz_combo.currentText(),
            'vertical': self.vert_combo.currentText()
        }