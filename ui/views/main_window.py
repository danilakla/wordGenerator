from PyQt6.QtWidgets import QMainWindow, QSplitter, QMessageBox
from services.document_service import DocumentService
from ui.views.add_header_dialog import AddHeaderDialog
from ui.views.add_list_dialog import AddListDialog
from ui.views.add_listing_dialog import AddListingDialog
from ui.views.add_table_dialog import AddTableDialog
from ui.views.edit_element_dialog import EditElementDialog
from ui.views.move_element_dialog import MoveElementDialog
from .tree_view import TreeViewWidget
from .control_panel import ControlPanel
from .add_paragraph_dialog import AddParagraphDialog
from .add_image_dialog import AddImageDialog
from .add_formula_dialog import AddFormulaDialog
from PyQt6.QtCore import Qt
from elements.header import Header
from elements.paragraph import Paragraph
from elements.table import Table
from elements.image import Image
from elements.listing import Listing
from elements.list_element import ListElement
from elements.formula import Formula

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
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if not self.service.active:
                self.service.save_document()
            event.accept()  # allow closing
        else:
            event.ignore()  # cancel close
            
    def get_selected_element(self):
        selected = self.tree_view.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент в дереве, после которого нужно вставить новый элемент")
            return None
        return selected[0].data(0, Qt.ItemDataRole.UserRole)

    def add_header(self, checked=False):
        try:
            dialog = AddHeaderDialog(self.service.get_tree(), is_sub=False)
            if dialog.exec():
                parent, after, text, level = dialog.get_data()
                self.service.add_header(parent, text, level, after)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_subheader(self, checked=False):
        try:
            dialog = AddHeaderDialog(self.service.get_tree(), is_sub=True)
            if dialog.exec():
                parent, after, text, level = dialog.get_data()
                self.service.add_header(parent, text, level, after)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_text(self, checked=False):
        try:
            selected_elem = self.get_selected_element()
            if not selected_elem:
                return
            dialog = AddParagraphDialog(self.service.get_tree())
            if dialog.exec():
                _, _, paragraphs = dialog.get_data()
                for paragraph_text in paragraphs:
                    selected_elem=self.service.add_paragraph(selected_elem, paragraph_text, None)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_table(self, checked=False):
        try:
            selected_elem = self.get_selected_element()
            if not selected_elem:
                return
            dialog = AddTableDialog(self.service.get_tree())
            if dialog.exec():
                _, _, data, caption = dialog.get_data()
                self.service.add_table(selected_elem, data, caption, None)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_image(self, checked=False):
        try:
            selected_elem = self.get_selected_element()
            if not selected_elem:
                return
            dialog = AddImageDialog(self.service.get_tree())
            if dialog.exec():
                _, _, path, caption = dialog.get_data()
                self.service.add_image(selected_elem, path, caption, None)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_listing(self, checked=False):
        try:
            selected_elem = self.get_selected_element()
            if not selected_elem:
                return
            dialog = AddListingDialog(self.service.get_tree())
            if dialog.exec():
                _, _, text, caption = dialog.get_data()
                self.service.add_listing(selected_elem, text, caption, None)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_list(self, checked=False):
        try:
            selected_elem = self.get_selected_element()
            if not selected_elem:
                return
            dialog = AddListDialog(self.service.get_tree())
            if dialog.exec():
                _, _, items, list_type = dialog.get_data()
                self.service.add_list(selected_elem, items, list_type, None)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def add_formula(self, checked=False):
        try:
            selected_elem = self.get_selected_element()
            if not selected_elem:
                return
            dialog = AddFormulaDialog(self.service.get_tree())
            if dialog.exec():
                _, _, formula, caption = dialog.get_data()
                self.service.add_formula(selected_elem, formula, caption, None)
                self.tree_view.populate_tree()
        except Exception as e:
            self.handle_error(e)

    def remove_element(self, checked=False):
        try:
            selected = self.tree_view.tree.selectedItems()
            if not selected:
                QMessageBox.warning(self, "Ошибка", "Выберите элемент")
                return

            elem = selected[0].data(0, Qt.ItemDataRole.UserRole)
            if not elem:
                QMessageBox.warning(self, "Ошибка", "Выбранный элемент недействителен")
                return

            # Формируем описание элемента для подтверждения
            elem_type = type(elem).__name__
            elem_description = ""
            if isinstance(elem, Header):
                elem_description = f"Раздел: {elem.text[:50]}" + ("..." if len(elem.text) > 50 else "")
            elif isinstance(elem, Paragraph):
                elem_description = f"Обычный Текст: {elem.text[:50]}" + ("..." if len(elem.text) > 50 else "")
            elif isinstance(elem, Table):
                elem_description = f"Таблица: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
            elif isinstance(elem, Image):
                elem_description = f"Рисунок: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
            elif isinstance(elem, Listing):
                elem_description = f"Листинг: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")
            elif isinstance(elem, ListElement):
                elem_description = f"Список: {elem.list_type} (элементов: {len(elem.items)})"
            elif isinstance(elem, Formula):
                elem_description = f"Формула: {elem.caption[:50]}" + ("..." if len(elem.caption) > 50 else "")

            # Проверяем наличие дочерних элементов для заголовков
            if isinstance(elem, Header) and elem.children:
                QMessageBox.warning(self, "Ошибка", f"Нельзя удалить Раздел '{elem_description}' с дочерними элементами")
                return

            # Диалог подтверждения
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить элемент?\nТип: {elem_type}\nОписание: {elem_description}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.service.remove_element(elem)
                self.tree_view.populate_tree()
            else:
                QMessageBox.information(self, "Отмена", "Удаление отменено")
        except Exception as e:
            self.handle_error(e)

    def edit_element(self, checked=False):
        try:
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
        except Exception as e:
            self.handle_error(e)

    def move_element(self, checked=False):
        try:
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
        except Exception as e:
            self.handle_error(e)

    def save_document(self, checked=False):
        try:
            self.service.save_document()
            QMessageBox.information(self, "Сохранено", "Документ сохранен")
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, exception: Exception):
        """Обрабатывает ошибку и выполняет аварийное сохранение."""
        if not self.service.active:
            emergency_path = self.service.emergency_save()
            error_message = f"Произошла ошибка: {str(exception)}\n"
            if emergency_path:
                error_message += f"Документ сохранен в: {emergency_path}"
            else:
                error_message += "Не удалось выполнить аварийное сохранение документа."
            QMessageBox.critical(self, "Ошибка", error_message)