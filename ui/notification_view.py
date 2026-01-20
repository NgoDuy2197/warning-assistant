from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGraphicsDropShadowEffect, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QIcon
import ui.styles as styles
import os
import sys

class NotificationPopup(QWidget):
    def __init__(self, title, content, notif_type="info", icon=None, custom_color=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Max dimensions for popup
        self.MAX_WIDTH = 400
        self.MAX_HEIGHT = 400
        
        # UI Layout
        self.layout = QVBoxLayout(self)
        self.container = QWidget()
        self.container.setObjectName("PopupContainer")
        self.container.setStyleSheet(styles.get_notification_popup_style(notif_type, custom_color))
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 15)
        container_layout.setSpacing(10)
        
        # Header (Icon + Title)
        header_layout = QHBoxLayout()
        
        # Resolve icon path for Dev and PyInstaller
        if hasattr(sys, '_MEIPASS'):
             icon_path = os.path.join(sys._MEIPASS, "ui/images/logo.png")
        else:
             icon_path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
        
        # Priority: Custom Icon > Logo File > Default Type Icon
        use_custom_icon = icon and icon != "DEFAULT"
        
        if use_custom_icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 32px;")
        # elif os.path.exists(icon_path):
        #     icon_label = QLabel()
        #     pixmap = QIcon(icon_path).pixmap(32, 32)
        #     icon_label.setPixmap(pixmap)
        else:
            icons = {"danger": "🚨", "important": "🔥", "warning": "⚠️", "info": "ℹ️"}
            icon_label = QLabel(icons.get(notif_type, "ℹ️"))
            icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel(title)
        title_label.setObjectName("TitleLabel")
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        container_layout.addLayout(header_layout)
        
        # Content with Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_label = QLabel(content)
        content_label.setObjectName("ContentLabel")
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.scroll.setWidget(content_label)
        container_layout.addWidget(self.scroll)
        
        # Bottom Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("OK")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(80, 35)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        container_layout.addLayout(btn_layout)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.container.setGraphicsEffect(shadow)
        
        self.layout.addWidget(self.container)
        
        # Dynamic sizing
        self.adjustSize()
        width = min(self.width(), self.MAX_WIDTH)
        height = min(self.height(), self.MAX_HEIGHT)
        self.setFixedSize(width, height)
        
        self._set_position()

        # Animation
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _set_position(self):
        screen = self.screen().availableGeometry()
        x = screen.width() - self.width() - 30
        y = screen.height() - self.height() - 30
        self.move(x, y)

    def show_animated(self):
        self.show()
        self.animation.start()
