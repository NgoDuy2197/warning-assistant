import os
import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from storage.settings_manager import SettingsManager
from i18n.translator import translator
from ui.main_window import MainWindow
from services.notification_service import NotificationService

def main():
    # Fix Taskbar Icon on Windows
    myappid = 'einvoice.warning.assistant.1.0'
    try:
        if os.name == 'nt':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except (ImportError, AttributeError):
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("Assistant")
    
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
        
    icon_path = resource_path("ui/images/logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Initialize Storage
    settings_manager = SettingsManager()
    
    # Initialize i18n
    lang = settings_manager.get_setting("language", "vi_VN")
    translator.set_language(lang)
    
    # Initialize Services
    notif_service = NotificationService(settings_manager)
    
    # Initialize UI
    window = MainWindow(settings_manager)
    
    # Connect service to UI if needed (e.g. to refresh list status)
    notif_service.notification_triggered.connect(lambda _: window.load_notification_list())
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
