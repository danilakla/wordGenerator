# Updated tree_view.py - no changes needed, as per request.

from elements.element import Element
from elements.formula import Formula
from elements.header import Header
from elements.image import Image
from elements.list_element import ListElement
from elements.listing import Listing
from elements.paragraph import Paragraph
from elements.table import Table
from services.document_service import DocumentService

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton, QStackedWidget, QScrollArea, QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from docx2pdf import convert
import tempfile
import os
import fitz  # PyMuPDF
from typing import List

class TreeViewWidget(QWidget):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        layout = QVBoxLayout()

        self.stack = QStackedWidget()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Дерево элементов")
        self.stack.addWidget(self.tree)

        self.pdf_widget = QWidget()
        pdf_layout = QVBoxLayout(self.pdf_widget)

        self.page_label = QLabel("Страница: 0/0")
        pdf_layout.addWidget(self.page_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.pdf_container = QWidget()
        self.pdf_layout = QVBoxLayout(self.pdf_container)
        self.pdf_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.pdf_container)
        pdf_layout.addWidget(self.scroll_area)

        self.stack.addWidget(self.pdf_widget)

        layout.addWidget(self.stack)

        self.btn_pdf = QPushButton("Показать в PDF")
        self.btn_pdf.clicked.connect(self.toggle_pdf)
        layout.addWidget(self.btn_pdf)

        self.setLayout(layout)
        self.is_pdf_mode = False
        self.current_page = 0
        self.total_pages = 0
        self.temp_files_to_cleanup = []
        self.pdf_pages = []
        self.current_pdf_path = None

    def populate_tree(self):
        self.tree.clear()
        tree = self.service.get_tree()
        self._add_items(self.tree.invisibleRootItem(), tree)
    

    def _add_items(self, parent_item: QTreeWidgetItem, elements: List[Element]):
        for elem in elements:
            item = QTreeWidgetItem(parent_item)
            if isinstance(elem, Header):
                item.setText(0, f"Раздел: {elem.text}" if elem.level == 1 else f"Подраздел: {elem.text}")

            elif isinstance(elem, Paragraph):
                item.setText(0, f"Обычный Текст: {elem.text[:20]}...")
            elif isinstance(elem, Table):
                item.setText(0, f"Таблица: {elem.caption}")
            elif isinstance(elem, Image):
                item.setText(0, f"Рисунок: {elem.caption}")
            elif isinstance(elem, Listing):
                item.setText(0, f"Листинг: {elem.caption}")
            elif isinstance(elem, ListElement):
                item.setText(0, f"Список: {len(elem.items)} кол-во; первый: {elem.items[0]}")
            elif isinstance(elem, Formula):
                item.setText(0, f"Формула: {elem.caption}")
            item.setData(0, Qt.ItemDataRole.UserRole, elem)
            if hasattr(elem, 'children'):
                self._add_items(item, elem.children)

    def toggle_pdf(self):
        if self.is_pdf_mode:
            self.btn_pdf.setText("Показать в PDF")
            self.stack.setCurrentIndex(0)
            self.cleanup_temp_files()
            self.clear_pdf_pages()
            self.is_pdf_mode = False
        else:
            self.btn_pdf.setText("Показать дерево элементов")
            self.show_pdf()
            self.stack.setCurrentIndex(1)
            self.is_pdf_mode = True

    def show_pdf(self):
        temp_pdf_path = None
        temp_wrd_path =None
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
                
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_wrd:
                temp_wrd_path = temp_wrd.name
            self.service.temp_save_d(temp_wrd_path)
            convert(temp_wrd_path, temp_pdf_path)

            self.temp_files_to_cleanup.append(temp_pdf_path)
            self.temp_files_to_cleanup.append(temp_wrd_path)
            self.current_pdf_path = temp_pdf_path

            self.load_all_pdf_pages()

        except Exception as e:
            print(f"Ошибка: {e}")

    def load_all_pdf_pages(self):
        try:
            doc = fitz.open(self.current_pdf_path)
            self.total_pages = len(doc)

            self.clear_pdf_pages()
            self.pdf_pages = []

            for page_number in range(self.total_pages):
                page = doc.load_page(page_number)
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                scaled_pixmap = pixmap.scaled(800, 1000, 
                                              Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                page_label = QLabel()
                page_label.setPixmap(scaled_pixmap)
                page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                page_label.setStyleSheet("margin: 10px; border: 1px solid #ccc;")
                page_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                self.pdf_pages.append(page_label)
                self.pdf_layout.addWidget(page_label)

            self.update_page_info(0)
            self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        except Exception as e:
            print(f"Ошибка загрузки страниц: {e}")

    def on_scroll(self, value):
        if not self.pdf_pages:
            return

        scroll_position = value
        current_page = 0
        max_visible_area = 0

        for i, page_label in enumerate(self.pdf_pages):
            page_pos = page_label.mapTo(self.scroll_area, page_label.pos()).y()
            page_height = page_label.height()
            visible_height = min(page_pos + page_height, scroll_position + self.scroll_area.height()) - max(page_pos, scroll_position)
            if visible_height > max_visible_area:
                max_visible_area = visible_height
                current_page = i

        if current_page != self.current_page:
            self.current_page = current_page
            self.update_page_info(current_page)

    def update_page_info(self, page_number):
        self.page_label.setText(f"Страница: {page_number + 1}/{self.total_pages}")

    def clear_pdf_pages(self):
        for i in reversed(range(self.pdf_layout.count())): 
            widget = self.pdf_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.pdf_pages = []

    def cleanup_temp_files(self):
        files_to_remove = self.temp_files_to_cleanup.copy()
        self.temp_files_to_cleanup = []
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Ошибка удаления файла {file_path}: {e}")