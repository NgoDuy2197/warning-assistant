import json
import os
import sys
from pathlib import Path

class SettingsManager:
    @staticmethod
    def _get_app_data_dir():
        """Get the application data directory based on the OS"""
        if sys.platform == "win32":
            # Windows: %APPDATA%\Assistant
            app_data = os.getenv("APPDATA")
            if not app_data:
                app_data = os.path.expanduser("~\\AppData\\Roaming")
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/Assistant
            app_data = os.path.expanduser("~/Library/Application Support")
        else:
            # Linux: ~/.local/share/Assistant
            app_data = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        
        app_dir = os.path.join(app_data, "Assistant")
        
        # Create directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)
        
        return app_dir
    
    def __init__(self):
        # Set DATA_FILE to the full path in app data directory
        self.DATA_FILE = os.path.join(self._get_app_data_dir(), "__user_data.txt")
        
        # Migration: Move old data file to new location if exists
        self._migrate_old_data_file()
        
        self.data = self._load_data()
    
    def _migrate_old_data_file(self):
        """Migrate old data file from project directory to app data directory"""
        old_file_path = "__user_data.txt"
        
        # If old file exists and new file doesn't exist, move it
        if os.path.exists(old_file_path) and not os.path.exists(self.DATA_FILE):
            try:
                import shutil
                shutil.copy2(old_file_path, self.DATA_FILE)
                print(f"Migrated data from {old_file_path} to {self.DATA_FILE}")
                # Optionally, you can delete the old file after successful migration
                # os.remove(old_file_path)
            except Exception as e:
                print(f"Error migrating data file: {e}")

    def _load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
        
        # Default data
        return {
            "notifications": [],
            "settings": {
                "theme": "default", # "default" or "pink"
                "language": "vi_VN", # "vi_VN", "en_US", "zh_CN"
                "autostart": False
            }
        }

    def save_data(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")

    # Notifications helper
    def get_notifications(self):
        return self.data.get("notifications", [])

    def add_notification(self, notification):
        self.data["notifications"].append(notification)
        self.save_data()

    def update_notification(self, index, updated_notif):
        if 0 <= index < len(self.data["notifications"]):
            self.data["notifications"][index] = updated_notif
            self.save_data()

    def remove_notification(self, index):
        if 0 <= index < len(self.data["notifications"]):
            self.data["notifications"].pop(index)
            self.save_data()

    # Settings helper
    def get_setting(self, key, default=None):
        return self.data.get("settings", {}).get(key, default)

    def set_setting(self, key, value):
        self.data["settings"][key] = value
        self.save_data()
