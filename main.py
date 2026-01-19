import sys
from PyQt6.QtWidgets import QApplication
from storage.settings_manager import SettingsManager
from i18n.translator import translator
from ui.main_window import MainWindow
from services.notification_service import NotificationService

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Warning Assistant")
    
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
