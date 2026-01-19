from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QListWidgetItem, QTabWidget,
                             QLabel, QComboBox, QCheckBox, QDialog, QLineEdit, 
                             QTextEdit, QDateTimeEdit, QSpinBox, QTimeEdit, 
                             QSystemTrayIcon, QMenu, QApplication, QMessageBox,
                             QKeySequenceEdit, QFileDialog)
from PyQt6.QtCore import Qt, QDateTime, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut
import shutil
from i18n.translator import translator
from services.autostart_service import AutostartService
import ui.styles as styles
from datetime import datetime
import os
import random

class AddNotifDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.setWindowTitle(translator.t("btn_add") if not initial_data else "Edit Notification")
        self.resize(420, 550)
        self.initial_data = initial_data
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Title
        layout.addWidget(QLabel(translator.t("label_title")))
        self.title_input = QTextEdit()
        self.title_input.setMaximumHeight(80)
        layout.addWidget(self.title_input)
        
        # Content
        layout.addWidget(QLabel(translator.t("label_content")))
        self.content_input = QTextEdit()
        self.content_input.setMaximumHeight(100)
        layout.addWidget(self.content_input)
        
        # Type
        layout.addWidget(QLabel(translator.t("label_type")))
        self.type_combo = QComboBox()
        self.type_combo.addItem(translator.t("notif_type_info"), "info")
        self.type_combo.addItem(translator.t("notif_type_warning"), "warning")
        self.type_combo.addItem(translator.t("notif_type_important"), "important")
        self.type_combo.addItem(translator.t("notif_type_danger"), "danger")
        layout.addWidget(self.type_combo)
        
        # Frequency
        layout.addWidget(QLabel(translator.t("label_frequency")))
        self.freq_combo = QComboBox()
        self.freq_combo.addItem(translator.t("notif_freq_once"), "once")
        self.freq_combo.addItem(translator.t("notif_freq_daily"), "daily")
        self.freq_combo.addItem(translator.t("notif_freq_repeat"), "repeat")
        self.freq_combo.currentIndexChanged.connect(self.on_freq_changed)
        layout.addWidget(self.freq_combo)
        
        # Time Inputs
        self.time_stack = QWidget()
        self.time_stack_layout = QVBoxLayout(self.time_stack)
        self.time_stack_layout.setContentsMargins(0, 0, 0, 0)
        
        self.datetime_picker = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_picker.setCalendarPopup(True)
        self.datetime_picker.setDisplayFormat(translator.t("date_display_format"))
        self.time_stack_layout.addWidget(self.datetime_picker)
        
        self.time_picker = QTimeEdit()
        self.time_picker.hide()
        self.time_stack_layout.addWidget(self.time_picker)
        
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 1440)
        self.repeat_spin.setSuffix(f" {translator.t('notif_freq_repeat')}")
        self.repeat_spin.hide()
        self.time_stack_layout.addWidget(self.repeat_spin)
        
        layout.addWidget(self.time_stack)
        
        # Actions
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        save_btn = QPushButton(translator.t("btn_save"))
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(translator.t("btn_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        if initial_data:
            self.load_data(initial_data)

    def accept(self):
        title = self.title_input.toPlainText().strip()
        if not title:
            return
            
        if len(title) > 125:
            QMessageBox.warning(self, translator.t("msg_error"), translator.t("error_title_length"))
            return
            
        if title.count('\n') > 3:
            QMessageBox.warning(self, translator.t("msg_error"), translator.t("error_title_lines"))
            return
            
        super().accept()

    def load_data(self, data):
        self.title_input.setText(data.get("title", ""))
        self.content_input.setText(data.get("content", ""))
        
        idx = self.type_combo.findData(data.get("type"))
        if idx >= 0: self.type_combo.setCurrentIndex(idx)
        
        freq = data.get("freq")
        idx = self.freq_combo.findData(freq)
        if idx >= 0: self.freq_combo.setCurrentIndex(idx)
        
        if freq == "once":
            self.datetime_picker.setDateTime(QDateTime.fromString(data.get("time"), Qt.DateFormat.ISODate))
        elif freq == "daily":
            # Fix for daily time format HH:mm
            t = datetime.strptime(data.get("time"), "%H:%M")
            self.time_picker.setTime(QDateTime.currentDateTime().replace(hour=t.hour, minute=t.minute).time())
        elif freq == "repeat":
            self.repeat_spin.setValue(data.get("repeat_min", 1))
        
        self.on_freq_changed()

    def on_freq_changed(self):
        freq = self.freq_combo.currentData()
        self.datetime_picker.setVisible(freq == "once")
        self.time_picker.setVisible(freq == "daily")
        self.repeat_spin.setVisible(freq == "repeat")

    def get_data(self):
        freq = self.freq_combo.currentData()
        time_val = ""
        if freq == "once":
            time_val = self.datetime_picker.dateTime().toPyDateTime().isoformat()
        elif freq == "daily":
            time_val = self.time_picker.time().toString("HH:mm")
            
        now_iso = datetime.now().isoformat()
        data = {
            "title": self.title_input.toPlainText().strip(),
            "content": self.content_input.toPlainText(),
            "type": self.type_combo.currentData(),
            "freq": freq,
            "time": time_val,
            "repeat_min": self.repeat_spin.value(),
            "active": True, # Always activate on save/edit
            "created_at": self.initial_data.get("created_at", now_iso) if self.initial_data else now_iso,
            "updated_at": now_iso,
            "last_triggered": None # Reset last_triggered to ensure it re-triggers if conditions met
        }
        return data

class MainWindow(QMainWindow):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        
        # Set Window Icon
        self.logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.ico")
        if os.path.exists(self.logo_path):
            self.setWindowIcon(QIcon(self.logo_path))
        
        self.init_tray()
        self.init_ui()
        self.setup_global_shortcuts()
        self.apply_theme()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(self.logo_path):
            self.tray_icon.setIcon(QIcon(self.logo_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("appointment-new"))
        
        tray_menu = QMenu()
        
        add_action = QAction(translator.t("btn_add"), self)
        add_action.triggered.connect(self.add_notification)
        
        show_action = QAction(translator.t("tray_show"), self)
        show_action.triggered.connect(self.show_normal)
        
        exit_action = QAction(translator.t("tray_exit"), self)
        exit_action.triggered.connect(self.exit_app)
        
        tray_menu.addAction(add_action)
        tray_menu.addSeparator()
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_normal()

    def show_normal(self):
        self.show()
        self.setWindowState(Qt.WindowState.WindowActive)
        self.activateWindow()

    def exit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                self.hide()
                event.ignore()

    def init_ui(self):
        self.setWindowTitle(translator.t("app_title"))
        self.resize(550, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # TAB 1: Notifications
        self.notif_tab = QWidget()
        self.notif_container_layout = QVBoxLayout(self.notif_tab)
        self.notif_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # We use a container to host the list and the floating button
        self.list_container = QWidget()
        self.list_container_layout = QVBoxLayout(self.list_container)
        self.list_container_layout.setContentsMargins(0, 10, 0, 0)
        
        self.notif_list = QListWidget()
        self.notif_list.setSpacing(8)
        self.notif_list.itemClicked.connect(self.on_notif_clicked)
        self.list_container_layout.addWidget(self.notif_list)
        
        # Watermark Background Text
        contacts = ["duynq18@fpt.com", "duynq2197@gmail.com", "0961218897"]
        self.watermark = QLabel(random.choice(contacts), self.notif_tab)
        self.watermark.setObjectName("BackgroundWatermark")
        self.watermark.setStyleSheet("color: rgba(100, 116, 139, 15); font-size: 24px; font-weight: bold;")
        self.watermark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.watermark.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.watermark.lower() # Send to back
        
        self.notif_container_layout.addWidget(self.list_container)
        
        # Floating Add Button
        self.floating_add_btn = QPushButton("+", self.notif_tab)
        self.floating_add_btn.setObjectName("FloatingAddBtn")
        self.floating_add_btn.setFixedSize(56, 56)
        self.floating_add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.floating_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-size: 32px;
                border-radius: 28px;
                padding: 0px;
                margin: 0px;
                text-align: center;
                /* Vertical centering trick for icons/symbols */
                padding-bottom: 7px; 
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.floating_add_btn.clicked.connect(self.add_notification)
        self.floating_add_btn.raise_()
        
        # Position floating button (will be updated in resizeEvent)
        self.tabs.addTab(self.notif_tab, translator.t("tab_notifications"))
        
        # TAB 2: Settings
        self.settings_tab = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_tab)
        self.settings_layout.setContentsMargins(10, 20, 10, 20)
        self.settings_layout.setSpacing(15)
        
        # Language
        self.settings_layout.addWidget(QLabel(f"<b>{translator.t('label_language')}</b>"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Tiếng Việt 🇻🇳", "vi_VN")
        self.lang_combo.addItem("English 🇺🇸", "en_US")
        self.lang_combo.addItem("中文 🇨🇳", "zh_CN")
        current_lang = self.settings_manager.get_setting("language", "vi_VN")
        idx = self.lang_combo.findData(current_lang)
        self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        self.settings_layout.addWidget(self.lang_combo)
        
        # Theme
        self.settings_layout.addWidget(QLabel("<b>Giao diện (Theme)</b>"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(translator.t("btn_theme_default"), "default")
        self.theme_combo.addItem(translator.t("btn_theme_pink"), "pink")
        current_theme = self.settings_manager.get_setting("theme", "default")
        idx = self.theme_combo.findData(current_theme)
        self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.currentIndexChanged.connect(lambda: self.change_theme(self.theme_combo.currentData()))
        self.settings_layout.addWidget(self.theme_combo)
        
        # Autostart
        self.autostart_chk = QCheckBox(translator.t("label_autostart"))
        self.autostart_chk.setChecked(self.settings_manager.get_setting("autostart", False))
        self.autostart_chk.toggled.connect(self.toggle_autostart)
        self.settings_layout.addWidget(self.autostart_chk)
        
        # Shortcut Configuration
        self.settings_layout.addWidget(QLabel(f"<b>{translator.t('label_shortcut')}</b>"))
        self.shortcut_input = QKeySequenceEdit()
        current_shortcut = self.settings_manager.get_setting("shortcut", "Ctrl+Shift+A")
        self.shortcut_input.setKeySequence(QKeySequence(current_shortcut))
        self.shortcut_input.keySequenceChanged.connect(self.update_shortcut)
        self.settings_layout.addWidget(self.shortcut_input)
        
        # Import / Backup
        self.settings_layout.addSpacing(10)
        btn_container = QHBoxLayout()
        
        self.btn_import = QPushButton(translator.t("btn_import"))
        self.btn_import.setStyleSheet("background-color: #64748B; color: white; padding: 10px; border-radius: 5px;")
        self.btn_import.clicked.connect(self.import_data)
        
        self.btn_backup = QPushButton(translator.t("btn_backup"))
        self.btn_backup.setStyleSheet("background-color: #64748B; color: white; padding: 10px; border-radius: 5px;")
        self.btn_backup.clicked.connect(self.backup_data)
        
        btn_container.addWidget(self.btn_import)
        btn_container.addWidget(self.btn_backup)
        self.settings_layout.addLayout(btn_container)
        
        self.settings_layout.addStretch()
        self.tabs.addTab(self.settings_tab, translator.t("tab_settings"))
        
        self.load_notification_list()
        QTimer.singleShot(10, self.update_floating_btn_pos)

    def apply_theme(self):
        theme = self.settings_manager.get_setting("theme", "default")
        self.setStyleSheet(styles.get_main_style(theme))

    def change_theme(self, theme):
        self.settings_manager.set_setting("theme", theme)
        self.apply_theme()

    def change_language(self):
        lang = self.lang_combo.currentData()
        self.settings_manager.set_setting("language", lang)
        translator.set_language(lang)
        self.init_ui()
        self.apply_theme()

    def toggle_autostart(self, checked):
        AutostartService.set_autostart(checked)
        self.settings_manager.set_setting("autostart", checked)

    def load_notification_list(self):
        self.notif_list.clear()
        notifications = self.settings_manager.get_notifications()
        
        # Sort by updated_at or created_at descending
        sorted_notifs = sorted(
            enumerate(notifications), 
            key=lambda x: x[1].get("updated_at", x[1].get("created_at", "")), 
            reverse=True
        )
        
        for ui_idx, (real_idx, notif) in enumerate(sorted_notifs):
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, real_idx) # Store original index
            widget = self.create_notif_widget(real_idx, notif)
            item.setSizeHint(widget.sizeHint())
            self.notif_list.addItem(item)
            self.notif_list.setItemWidget(item, widget)

    def on_notif_clicked(self, item):
        real_idx = item.data(Qt.ItemDataRole.UserRole)
        if real_idx is not None:
            self.edit_notification(real_idx)

    def update_shortcut(self, key_sequence):
        shortcut_str = key_sequence.toString()
        self.settings_manager.set_setting("shortcut", shortcut_str)
        self.setup_global_shortcuts()

    def setup_global_shortcuts(self):
        # Clean old shortcut if exists
        if hasattr(self, 'add_shortcut_obj'):
            self.add_shortcut_obj.setEnabled(False)
            self.add_shortcut_obj.deleteLater()
            
        shortcut_str = self.settings_manager.get_setting("shortcut", "Ctrl+Shift+A")
        # Note: This QShortcut works when window is focused. 
        # For a true system-wide global shortcut on Windows, we could use RegisterHotKey.
        self.add_shortcut_obj = QShortcut(QKeySequence(shortcut_str), self)
        self.add_shortcut_obj.activated.connect(self.add_notification)

    def backup_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, translator.t("msg_backup_title"), "__user_data_backup.txt", "Text Files (*.txt)"
        )
        if file_path:
            try:
                shutil.copy2(self.settings_manager.DATA_FILE, file_path)
                QMessageBox.information(self, "Success", translator.t("msg_backup_success"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Backup failed: {str(e)}")

    def import_data(self):
        if QMessageBox.question(self, "Confirm", translator.t("msg_import_confirm")) == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self, translator.t("msg_import_title"), "", "Text Files (*.txt)"
            )
            if file_path:
                try:
                    shutil.copy2(file_path, self.settings_manager.DATA_FILE)
                    # Reload data
                    self.settings_manager.data = self.settings_manager._load_data()
                    self.load_notification_list()
                    QMessageBox.information(self, "Success", translator.t("msg_import_success"))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Import failed: {str(e)}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(50, self.update_floating_btn_pos)

    def update_floating_btn_pos(self):
        if not hasattr(self, 'floating_add_btn') or self.floating_add_btn is None:
            return
            
        tab_rect = self.notif_tab.rect()
        if tab_rect.width() > 50:
            btn_size = self.floating_add_btn.size()
            x = tab_rect.width() - btn_size.width() - 25
            y = tab_rect.height() - btn_size.height() - 25
            self.floating_add_btn.move(x, y)
            self.floating_add_btn.raise_()
            self.floating_add_btn.show()
            
        # Update watermark position
        if hasattr(self, 'watermark'):
            self.watermark.resize(self.notif_tab.size())
            self.watermark.move(0, 0)
            self.watermark.lower()

    def format_time(self, time_str, freq):
        if freq == "repeat":
            return "" # repeat_min is shown separately
        if not time_str: return ""
        
        try:
            lang = self.settings_manager.get_setting("language", "vi_VN")
            is_en = lang == "en_US"
            fmt = "%m/%d/%Y %H:%M:%S" if is_en else "%d/%m/%Y %H:%M:%S"
            
            if freq == "once":
                dt = datetime.fromisoformat(time_str)
                return dt.strftime(fmt)
            elif freq == "daily":
                return time_str # HH:mm
        except:
            return time_str
        return time_str

    def create_notif_widget(self, index, notif):
        widget = QWidget()
        widget.setObjectName("NotificationCard")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        accent = {"danger": "#EF4444", "important": "#F59E0B", "warning": "#F59E0B", "info": "#3B82F6"}.get(notif['type'], "#3B82F6")
        
        indicator = QWidget()
        indicator.setFixedSize(6, 40)
        indicator.setStyleSheet(f"background-color: {accent}; border-radius: 3px;")
        layout.addWidget(indicator)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        title = QLabel(notif['title'])
        title.setStyleSheet("font-weight: 700; font-size: 14px;")
        title.setWordWrap(True)
        
        time_display = self.format_time(notif['time'], notif['freq'])
        if notif['freq'] == 'repeat':
            time_display = f"Every {notif['repeat_min']} min"
            
        status_text = translator.t("status_running") if notif['active'] else translator.t("status_disabled")
        details = QLabel(f"{translator.t('notif_type_' + notif['type'])} • {time_display} • {status_text}")
        details.setStyleSheet("color: #64748B; font-size: 12px;")
        details.setWordWrap(True)
        
        info_layout.addWidget(title)
        info_layout.addWidget(details)
        layout.addLayout(info_layout, 1) # Give priority to text layout
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Status Circle Toggle Button
        toggle_btn = QPushButton()
        toggle_btn.setFixedSize(28, 28)
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        status_color = '#10B981' if notif['active'] else '#94A3B8'
        status_tip = translator.t("btn_off") if notif['active'] else translator.t("btn_on")
        toggle_btn.setToolTip(status_tip)
        
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {status_color};
                border-radius: 14px;
                border: 2px solid white;
            }}
            QPushButton:hover {{
                border-color: {status_color}dd;
            }}
        """)
        toggle_btn.clicked.connect(lambda: self.toggle_notification(index))
        actions_layout.addWidget(toggle_btn)

        # Circular Delete Button
        btn_del = QPushButton(translator.t("btn_delete_short"))
        btn_del.setFixedSize(50, 50)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip(translator.t("btn_delete"))
        btn_del.setStyleSheet("""
            QPushButton { 
                background-color: #FFFFFF; 
                color: #B91C1C; 
                border-radius: 14px; 
                border: 2px solid white;
                font-size: 12px;
                margin: 1px;
                padding: 1px;
            }
            QPushButton:hover { background-color: #FECACA; }
        """)
        btn_del.clicked.connect(lambda: self.delete_notification(index))
        actions_layout.addWidget(btn_del)
        
        layout.addLayout(actions_layout)
        return widget

    def add_notification(self):
        dialog = AddNotifDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["title"]:
                self.settings_manager.add_notification(data)
                self.load_notification_list()

    def edit_notification(self, index):
        notifs = self.settings_manager.get_notifications()
        if 0 <= index < len(notifs):
            dialog = AddNotifDialog(self, initial_data=notifs[index])
            if dialog.exec():
                self.settings_manager.update_notification(index, dialog.get_data())
                self.load_notification_list()

    def toggle_notification(self, index):
        notifs = self.settings_manager.get_notifications()
        notif = notifs[index]
        notif['active'] = not notif['active']
        notif['updated_at'] = datetime.now().isoformat()
        self.settings_manager.update_notification(index, notif)
        self.load_notification_list()

    def delete_notification(self, index):
        self.settings_manager.remove_notification(index)
        self.load_notification_list()
