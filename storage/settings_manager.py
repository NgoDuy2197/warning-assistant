import json
import os

class SettingsManager:
    DATA_FILE = "__user_data.txt"

    def __init__(self):
        self.data = self._load_data()

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
