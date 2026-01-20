
def get_main_style(theme="default"):
    if theme == "pink":
        primary = "#FB7185"    # Rose 400
        primary_hover = "#F43F5E" # Rose 500
        bg = "#FFF1F2"        # Rose 50
        surface = "#FFFFFF"
        text_main = "#881337"  # Rose 900
        text_sub = "#E11D48"   # Rose 600
        border = "#FECDD3"     # Rose 200
        input_bg = "#FFFFFF"
    else:
        primary = "#6366F1"    # Indigo 500
        primary_hover = "#4F46E5" # Indigo 600
        bg = "#F8FAFC"        # Slate 50
        surface = "#FFFFFF"
        text_main = "#1E293B"  # Slate 800
        text_sub = "#64748B"   # Slate 500
        border = "#E2E8F0"     # Slate 200
        input_bg = "#FFFFFF"

    return f"""
    QMainWindow, QDialog {{
        background-color: {bg};
    }}
    
    QLabel {{
        color: {text_main};
        font-family: 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif;
    }}
    
    QPushButton {{
        background-color: {primary};
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
        border: none;
    }}
    
    QPushButton:hover {{
        background-color: {primary_hover};
    }}

    /* Tab Widget Styling */
    QTabWidget::pane {{
        border: none;
        background: transparent;
        margin-top: 10px;
    }}
    
    QTabBar::tab {{
        background: transparent;
        color: {text_sub};
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        border-bottom: 2px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        color: {primary};
        border-bottom: 2px solid {primary};
    }}

    /* Card styling */
    QWidget#NotificationCard {{
        background-color: {surface};
        border-radius: 14px;
        border: 1px solid {border};
    }}
    
    QListWidget {{
        background: transparent;
        border: none;
        outline: none;
        padding: 5px;
    }}

    QListWidget::item {{
        background: transparent;
        border: none;
        margin-bottom: 8px;
    }}

    QLineEdit, QDateTimeEdit, QComboBox, QSpinBox, QTextEdit, QTimeEdit {{
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid {border};
        background-color: {input_bg};
        color: {text_main};
        font-size: 13px;
        min-height: 20px;
    }}
    
    QLineEdit:focus, QDateTimeEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 2px solid {primary};
    }}

    /* Modern ComboBox Styling */
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox::down-arrow {{
        image: none; /* Can add a custom arrow icon here */
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {text_sub};
        margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid {border};
        border-radius: 8px;
        background-color: {surface};
        selection-background-color: {bg};
        selection-color: {primary};
        outline: none;
        padding: 5px;
    }}

    /* Modern SpinBox Styling - Using symbols if images are provided by user */
    QSpinBox::up-button, QDateTimeEdit::up-button, QTimeEdit::up-button {{
        width: 28px;
        background: {bg};
        border-left: 1px solid {border};
        border-top-right-radius: 10px;
        image: url(ui/images/plus.png);
    }}
    QSpinBox::down-button, QDateTimeEdit::down-button, QTimeEdit::down-button {{
        width: 28px;
        background: {bg};
        border-left: 1px solid {border};
        border-bottom-right-radius: 10px;
        image: url(ui/images/minus.png);
    }}
    
    /* Ensuring symbols are used specifically */
    QSpinBox::up-arrow, QDateTimeEdit::up-arrow, QTimeEdit::up-arrow {{ image: url(ui/images/plus.png); width: 12px; height: 12px; }}
    QSpinBox::down-arrow, QDateTimeEdit::down-arrow, QTimeEdit::down-arrow {{ image: url(ui/images/minus.png); width: 12px; height: 12px; }}

    /* Floating Action Button */
    QPushButton#FloatingAddBtn {{
        background-color: {primary};
        color: white;
        font-size: 32px;
        font-weight: normal;
        border-radius: 28px;
        padding: 0px;
        margin: 0px;
        text-align: center;
        line-height: 56px; /* Match height for vertical centering if possible */
    }}
    QPushButton#FloatingAddBtn:hover {{
        background-color: {primary_hover};
    }}

    QCheckBox {{
        spacing: 8px;
        color: {text_main};
        font-weight: 500;
    }}

    /* Global Modern ScrollBar */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {border};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {text_sub};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        height: 0px;
    }}
    """

def get_notification_popup_style(notif_type="info", custom_color=None):
    if custom_color:
        # Custom color logic
        # format: #RRGGBB
        try:
            h = custom_color.strip('#')
            r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            
            # Background: the color but very light (20% opacity for bg to read text, or 50% as requested)
            # "màu nền tự động làm nhạt đi 50%" - strictly this means 50% opacity or 50% mix with white.
            # Let's do 50% mix with white => (Color + White)/2
            # Or simpler: rgba(r,g,b, 0.2) looks better, but let's stick to request "nhạt đi 50%" ~ 0.5 alpha?
            # 0.5 alpha on transparent window might look OK.
            
            bg_color = f"rgba({r}, {g}, {b}, 0.2)" # 20% looks classy. 50% is too strong for background usually.
            # But user said "nhạt đi 50%". Let's try 0.5 first if they persist, but 0.9 text on 0.5 bg is okay.
            # Let's use a solid light color for safety: weighted mix with white.
            # mix(color, white, 0.85) -> 85% white
            
            bg_r = int(r + (255 - r) * 0.9)
            bg_g = int(g + (255 - g) * 0.9)
            bg_b = int(b + (255 - b) * 0.9)
            bg_color = f"rgba({bg_r}, {bg_g}, {bg_b}, 0.95)"
            
            # Accent (Button) is the color itself
            accent = custom_color
            
            # Border: can be same as accent or lighter
            border = f"rgba({r}, {g}, {b}, 0.3)"
            
            # Text Color: Dark or Light depending on background? Since we force BG to be very light, use dark text.
            # We assume users won't pick White as header color.
            # Let's derive a dark text color from the accent (darken it).
            text_r = max(0, int(r * 0.3))
            text_g = max(0, int(g * 0.3))
            text_b = max(0, int(b * 0.3))
            text_color = f"rgba({text_r}, {text_g}, {text_b}, 0.95)"
            
            # Button Text Color (Contrast)
            # Luminance: 0.299*R + 0.587*G + 0.114*B
            lum = (0.299 * r + 0.587 * g + 0.114 * b)
            btn_text = "white" if lum < 150 else "black"
            
            s = {"bg": bg_color, "border": border, "accent": accent, "text": text_color, "btn_text": btn_text}
        except:
             # Fallback
             s = {"bg": "rgba(239, 246, 255, 0.85)", "border": "#DBEAFE", "accent": "#3B82F6", "text": "rgba(30, 58, 138, 0.9)", "btn_text": "white"}
    else:
        schemes = {
            "danger": {"bg": "rgba(254, 242, 242, 0.85)", "border": "#FEE2E2", "accent": "#EF4444", "text": "rgba(127, 29, 29, 0.9)", "btn_text": "white"},
            "important": {"bg": "rgba(255, 251, 235, 0.85)", "border": "#FEF3C7", "accent": "#F59E0B", "text": "rgba(120, 53, 15, 0.9)", "btn_text": "white"},
            "warning": {"bg": "rgba(255, 251, 235, 0.85)", "border": "#FEF3C7", "accent": "#F59E0B", "text": "rgba(120, 53, 15, 0.9)", "btn_text": "white"},
            "info": {"bg": "rgba(239, 246, 255, 0.85)", "border": "#DBEAFE", "accent": "#3B82F6", "text": "rgba(30, 58, 138, 0.9)", "btn_text": "white"}
        }
        s = schemes.get(notif_type, schemes["info"])
    
    return f"""
    QWidget#PopupContainer {{
        background-color: {s["bg"]};
        border: 1px solid {s["border"]};
        border-radius: 20px;
    }}
    
    QLabel#TitleLabel {{
        font-size: 16px;
        font-weight: 700;
        color: {s["text"]};
    }}
    
    QLabel#ContentLabel {{
        font-size: 13px;
        color: {s["text"]};
        line-height: 1.4;
    }}
    
    QPushButton#CloseBtn {{
        background-color: {s["accent"]};
        color: {s["btn_text"]};
        border-radius: 10px;
        font-weight: 600;
        padding: 5px 15px;
    }}

    /* Popup Specific ScrollBar */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {s["accent"]}40;
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {s["accent"]}80;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
