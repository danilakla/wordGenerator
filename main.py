import sys, hashlib
from PyQt6.QtWidgets import QApplication
from services.document_service import DocumentService
from ui.views.license_dialog import LicenseDialog
from ui.views.notification_message import NotificationMessage
from ui.views.splash_screen import SplashScreen
from ui.views.folder_selection import FolderSelectionDialog
from ui.views.document_choice import DocumentChoiceDialog
from ui.views.main_window import MainWindow


def check_debug():
    if sys.gettrace() is not None:
        sys.exit("Debugging detected")




if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 🔹 перед запуском GUI проверяем лицензию
    NotificationMessage.check_and_show()
    service = DocumentService()

    license_dialog = LicenseDialog(service)
    if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
        sys.exit(0)

    try:
        check_debug()
        splash = SplashScreen()
        splash.show()

        folder_dialog = FolderSelectionDialog(service)
        if folder_dialog.exec():
            doc_choice = DocumentChoiceDialog(service)
            if doc_choice.exec():
                main_window = MainWindow(service)
                main_window.showMaximized()
                splash.close()
                sys.exit(app.exec())
        else:
            sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        if not service.active:
            service.emergency_save(f"Произошла непредвиденная ошибка:\n{e}")
        sys.exit(1)
