from PyQt6.QtWidgets import QApplication
import sys
from services.document_service import DocumentService
from ui.views.splash_screen import SplashScreen
from ui.views.folder_selection import FolderSelectionDialog
from ui.views.document_choice import DocumentChoiceDialog
from ui.views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    service = DocumentService()

    splash = SplashScreen()
    splash.show()

    folder_dialog = FolderSelectionDialog(service)
    if folder_dialog.exec():
        doc_choice = DocumentChoiceDialog(service)
        if doc_choice.exec():
            main_window = MainWindow(service)
            main_window.show()
            splash.close()
            sys.exit(app.exec())
    else:
        sys.exit(0)