from PyQt6.QtWidgets import QMainWindow, QSplitter, QMessageBox

from services.document_service import DocumentService
from ui.views.add_header_dialog import AddHeaderDialog
from ui.views.add_table_dialog import AddTableDialog
from ui.views.edit_element_dialog import EditElementDialog
from ui.views.move_element_dialog import MoveElementDialog
from .tree_view import TreeViewWidget
from .control_panel import ControlPanel
from .add_paragraph_dialog import AddParagraphDialog
from .add_image_dialog import AddImageDialog
from .add_listing_dialog import AddListingDialog
from .add_list_dialog import AddListDialog
from .add_formula_dialog import AddFormulaDialog
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, service: DocumentService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Word Document Manager")
        splitter = QSplitter()
        self.tree_view = TreeViewWidget(service)
        splitter.addWidget(self.tree_view)
        self.control_panel = ControlPanel(self)
        splitter.addWidget(self.control_panel)
        self.setCentralWidget(splitter)
        self.tree_view.populate_tree()

    def add_header(self):
        dialog = AddHeaderDialog(self.service.get_tree(), is_sub=False)
        if dialog.exec():
            parent, after, text, level = dialog.get_data()
            self.service.add_header(parent, text, level, after)
            self.tree_view.populate_tree()

    def add_subheader(self):
        dialog = AddHeaderDialog(self.service.get_tree(), is_sub=True)
        if dialog.exec():
            parent, after, text, level = dialog.get_data()
            self.service.add_header(parent, text, level, after)
            self.tree_view.populate_tree()

    def add_text(self):
        dialog = AddParagraphDialog(self.service.get_tree())
        if dialog.exec():
            parent, after, text = dialog.get_data()
            self.service.add_paragraph(parent, text, after)
            self.tree_view.populate_tree()

    def add_table(self):
        dialog = AddTableDialog(self.service.get_tree())
        if dialog.exec():
            parent, after, data, caption = dialog.get_data()
            self.service.add_table(parent, data, caption, after)
            self.tree_view.populate_tree()

    def add_image(self):
        dialog = AddImageDialog(self.service.get_tree())
        if dialog.exec():
            parent, after, path, caption = dialog.get_data()
            self.service.add_image(parent, path, caption, after)
            self.tree_view.populate_tree()

    def add_listing(self):
        dialog = AddListingDialog(self.service.get_tree())
        if dialog.exec():
            parent, after, text, caption = dialog.get_data()
            self.service.add_listing(parent, text, caption, after)
            self.tree_view.populate_tree()

    def add_list(self):
        dialog = AddListDialog(self.service.get_tree())
        if dialog.exec():
            parent, after, items, list_type = dialog.get_data()
            self.service.add_list(parent, items, list_type, after)
            self.tree_view.populate_tree()

    def add_formula(self):
        dialog = AddFormulaDialog(self.service.get_tree())
        if dialog.exec():
            parent, after, formula, caption = dialog.get_data()
            self.service.add_formula(parent, formula, caption, after)
            self.tree_view.populate_tree()

    def remove_element(self):
        selected = self.tree_view.tree.selectedItems()
        if selected:
            elem = selected[0].data(0, Qt.ItemDataRole.UserRole)
            if elem:
                self.service.remove_element(elem)
                self.tree_view.populate_tree()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент")

    def edit_element(self):
        selected = self.tree_view.tree.selectedItems()
        if selected:
            elem = selected[0].data(0, Qt.ItemDataRole.UserRole)
            if elem:
                dialog = EditElementDialog(elem, self.service.get_tree())
                if dialog.exec():
                    new_data = dialog.get_data()
                    self.service.update_element(elem, new_data)
                    self.tree_view.populate_tree()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент")

    def move_element(self):
        selected = self.tree_view.tree.selectedItems()
        if selected:
            elem = selected[0].data(0, Qt.ItemDataRole.UserRole)
            if elem:
                dialog = MoveElementDialog(self.service.get_tree(), elem)
                if dialog.exec():
                    new_parent, after = dialog.get_data()
                    self.service.move_element(elem, new_parent, after)
                    self.tree_view.populate_tree()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент")

    def save_document(self):
        self.service.save_document()
        QMessageBox.information(self, "Сохранено", "Документ сохранен")