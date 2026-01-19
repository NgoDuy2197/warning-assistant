from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from ui.notification_view import NotificationPopup

class NotificationService(QObject):
    notification_triggered = pyqtSignal(dict)

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start(10000) # Check every 10 seconds
        self.active_popups = []

    def check_notifications(self):
        now = datetime.now()
        notifications = self.settings_manager.get_notifications()
        modified = False

        for i, notif in enumerate(notifications):
            if not notif.get("active", True):
                continue
            
            should_trigger = False
            last_triggered_str = notif.get("last_triggered")
            last_triggered = datetime.fromisoformat(last_triggered_str) if last_triggered_str else None
            
            freq = notif.get("freq")
            
            if freq == "once":
                notif_time = datetime.fromisoformat(notif.get("time"))
                if now >= notif_time and not last_triggered:
                    should_trigger = True
                    notif["active"] = False # Done
            
            elif freq == "daily":
                notif_time_str = notif.get("time") # HH:mm
                target_time = now.replace(hour=int(notif_time_str[:2]), minute=int(notif_time_str[3:]), second=0, microsecond=0)
                
                if now >= target_time:
                    if not last_triggered or last_triggered.date() < now.date():
                        should_trigger = True
            
            elif freq == "repeat":
                repeat_min = int(notif.get("repeat_min", 1))
                if not last_triggered:
                    # First time: trigger if enough time passed since creation or logic below
                    # Let's say we trigger after repeat_min from creation or start
                    # To keep it simple: if not triggered yet, use creation_time
                    last_event = datetime.fromisoformat(notif.get("created_at", now.isoformat()))
                else:
                    last_event = last_triggered
                
                if now >= last_event + timedelta(minutes=repeat_min):
                    should_trigger = True

            if should_trigger:
                self.trigger(notif)
                notif["last_triggered"] = now.isoformat()
                modified = True
        
        if modified:
            self.settings_manager.save_data()

    def trigger(self, notif):
        # Clean up closed popups first
        self.active_popups = [p for p in self.active_popups if p.isVisible()]
        
        # Check if a notification with the same title is already showing
        for p in self.active_popups:
            if p.windowTitle() == notif["title"]:
                return # Don't trigger if already showing
        
        popup = NotificationPopup(notif["title"], notif["content"], notif["type"])
        popup.show_animated()
        self.active_popups.append(popup)
        self.notification_triggered.emit(notif)
