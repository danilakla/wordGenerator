from typing import List
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton, QStackedWidget
from docx2pdf import convert
import tempfile
import os

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
from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtCore import Qt
from docx2pdf import convert
import tempfile
import os
from typing import List
from elements.element import Element
from services.document_service import DocumentService

class TreeViewWidget(QWidget):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        layout = QVBoxLayout()

        self.stack = QStackedWidget()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Дерево элементов")
        self.stack.addWidget(self.tree)

        self.pdf_view = QWebEngineView()
        self.stack.addWidget(self.pdf_view)

        layout.addWidget(self.stack)

        btn_pdf = QPushButton("Показать в PDF")
        btn_pdf.clicked.connect(self.toggle_pdf)
        layout.addWidget(btn_pdf)

        self.setLayout(layout)
        self.is_pdf_mode = False

    def populate_tree(self):
        self.tree.clear()
        tree = self.service.get_tree()
        self._add_items(self.tree.invisibleRootItem(), tree)

    def _add_items(self, parent_item: QTreeWidgetItem, elements: List[Element]):
        for elem in elements:
            item = QTreeWidgetItem(parent_item)
            if isinstance(elem, Header):
                item.setText(0, f"Header {elem.level}: {elem.text}")
            elif isinstance(elem, Paragraph):
                item.setText(0, f"Paragraph: {elem.text[:20]}...")
            elif isinstance(elem, Table):
                item.setText(0, f"Table: {elem.caption}")
            elif isinstance(elem, Image):
                item.setText(0, f"Image: {elem.caption}")
            elif isinstance(elem, Listing):
                item.setText(0, f"Listing: {elem.caption}")
            elif isinstance(elem, ListElement):
                item.setText(0, f"List: {len(elem.items)} items")
            elif isinstance(elem, Formula):
                item.setText(0, f"Formula: {elem.caption}")
            item.setData(0, Qt.ItemDataRole.UserRole, elem)
            if hasattr(elem, 'children'):
                self._add_items(item, elem.children)

    def toggle_pdf(self):
        if self.is_pdf_mode:
            self.stack.setCurrentIndex(0)
            self.is_pdf_mode = False
        else:
            self.service.save_document()
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                convert(self.service.get_doc_path(), tmp.name)
                pdf_path = tmp.name
            self.pdf_view.setUrl(f"file://{pdf_path}")
            self.stack.setCurrentIndex(1)
            self.is_pdf_mode = True