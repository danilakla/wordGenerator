# Updated tree_view.py - simplified version

from elements.element import Element
from elements.formula import Formula
from elements.header import Header
from elements.image import Image
from elements.list_element import ListElement
from elements.listing import Listing
from elements.paragraph import Paragraph
from elements.table import Table
from services.document_service import DocumentService

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from docx2pdf import convert
import tempfile
import os
import webbrowser
from typing import List

class TreeViewWidget(QWidget):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Дерево элементов")
        layout.addWidget(self.tree)

        # Single button to open PDF in browser
        self.btn_open_pdf = QPushButton("Открыть в PDF")
        self.btn_open_pdf.clicked.connect(self.open_pdf_in_browser)
        layout.addWidget(self.btn_open_pdf)

        self.setLayout(layout)
        self.temp_files_to_cleanup = []

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

    def open_pdf_in_browser(self, checked=False):
        """Open PDF in default browser instead of showing in-app"""
        temp_pdf_path = None
        temp_wrd_path = None
        self.closeEvent()
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
                
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_wrd:
                temp_wrd_path = temp_wrd.name
            
            # Save document and convert to PDF
            self.service.temp_save_d(temp_wrd_path)
            convert(temp_wrd_path, temp_pdf_path)

            # Add to cleanup list
            self.temp_files_to_cleanup.append(temp_pdf_path)
            self.temp_files_to_cleanup.append(temp_wrd_path)

            # Open PDF in browser using file URL
            pdf_url = f"file:///{os.path.abspath(temp_pdf_path).replace(os.sep, '/')}"
            webbrowser.open(pdf_url)
            
            print(f"PDF opened in browser: {temp_pdf_path}")

        except Exception as e:
            print(f"Ошибка при открытии PDF: {e}")
            # Cleanup on error
            self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        files_to_remove = self.temp_files_to_cleanup.copy()
        self.temp_files_to_cleanup = []
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Ошибка удаления файла {file_path}: {e}")

    def closeEvent(self):
        """Clean up temp files when widget is closed"""
        self.cleanup_temp_files()