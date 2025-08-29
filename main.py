import sys, hashlib
from PyQt6.QtWidgets import QApplication
from services.document_service import DocumentService
from ui.views.license_dialog import LicenseDialog
from ui.views.splash_screen import SplashScreen
from ui.views.folder_selection import FolderSelectionDialog
from ui.views.document_choice import DocumentChoiceDialog
from ui.views.main_window import MainWindow
from config_hash import EXPECTED_HASH   # 🔹 импорт хэша


def check_debug():
    if sys.gettrace() is not None:
        sys.exit("Debugging detected")


def check_integrity():
    with open(sys.argv[0], "rb") as f:
        data = f.read()
    if hashlib.sha256(data).hexdigest() != EXPECTED_HASH:
        sys.exit("Файл поврежден")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 🔹 перед запуском GUI проверяем лицензию
    license_dialog = LicenseDialog()
    if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
        sys.exit(0)

    service = DocumentService()
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
        service.emergency_save(f"Произошла непредвиденная ошибка:\n{e}")
        sys.exit(1)
