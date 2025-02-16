import os

light = {
    "text": "#111111",
    "button_text": "#111111",
    "bg1": "#f1f1f1",
    "bg2": "#fefefe",
    "accent1": "#488AD9",
    "accent2": "#7ABAFF",
    "border": "#999999"
}

dark = {
    "text": "#FFFFFF",
    "button_text": "#111111",
    "bg1": "#0E161B",
    "bg2": "#0D1318",
    "accent1": "#488AD9",
    "accent2": "#7ABAFF",
    "border": "#222222"
}

theme = light

def get_theme():
    return theme

def set_theme(t):
    global theme
    theme = light if t == "Light" else dark

def get_styles(resource_path):
    images_path = os.path.join(resource_path, "images")
    open_image = os.path.join(images_path, 'close.png')
    open_image = open_image.replace("\\", "/")
    open_image_hover = os.path.join(images_path, 'close_hover.png')
    open_image_hover = open_image_hover.replace("\\", "/")
    return f"""
        QWidget {{
            font-family: 'Roboto';
            font-size: 18px;
            color: {theme["text"]};
        }}
        QPushButton {{
            font-family: 'Roboto';
            font-size: 19px;
        }}
        QLineEdit, QComboBox, QTreeWidget, QTextEdit, QPlainTextEdit {{
            font-family: 'RobotoMono'; 
            font-size: 18px;
        }}
        QSplitter::handle {{
            background-color: {theme["bg1"]};
        }}
        QWidget {{
            background-color: {theme["bg1"]};
            border: 0;
            outline: 0;
        }}
        QLabel {{
            color: {theme["text"]};
            font-weight: normal;
        }}
        QLineEdit, QComboBox, QTreeWidget, QTextEdit {{
            border: 1px solid {theme["border"]};
            padding: 5px;
            color: {theme["text"]}; 
            background-color: {theme["bg2"]};
        }}
        QPlainTextEdit {{
            border: 1px solid {theme["border"]};
            padding: 5px;
            color: {theme["text"]}; 
            background-color: {theme["bg2"]};
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme["bg2"]};
            color: {theme["text"]};
            border: 1px solid {theme["border"]};
        }}
        QComboBox QAbstractItemView::item {{
            height: 30px;
            color: {theme["text"]};
        }}
        QTreeWidget::item {{
            height: 30px;
            color: {theme["text"]};
        }}
        QTreeWidget::item:selected {{
            background-color: {theme["accent2"]};
            color: {theme["button_text"]};
        }}
        QTreeWidget::item:selected:active {{
            background-color: {theme["accent2"]};
            color: {theme["button_text"]};
        }}
        QTreeWidget {{
            color: {theme["text"]};
            border: 1px solid {theme["border"]};
        }}
        QScrollArea {{
            border: none;
        }}
        QTabBar {{
            border-left: 1px solid {theme["border"]};
        }}
        QTabBar::tab {{
            font-family: 'Roboto';
            font-size: 19px;
            height: 38px;
            color: {theme["text"]};
            margin-left: 1px;
            padding-left: 22px;
            padding-right: 18px;
            border-top: 1px solid {theme["border"]};
            border-bottom: 1px solid {theme["border"]};
            border-right: 1px solid {theme["border"]};
        }}
        QTabBar::tab:selected {{
            background-color: {theme["bg1"]};
            border-bottom: 0;
            border-top: 3px solid {theme["accent1"]};
        }}
        QTabBar::close-button {{
            image: url('{open_image}');
            subcontrol-position: right;
        }}
        QTabBar::close-button:hover {{
            image: url('{open_image_hover}');
        }}
        QWidget::pane {{
            border: 1px solid {theme["border"]};
            margin-top: -1px;
        }}
        QPushButton {{
            background-color: {theme["accent1"]};
            color: {theme["button_text"]};
            border: 1px solid {theme["border"]};
            padding: 8px;
            max-width: 320px;
        }}
        QPushButton:hover {{
            background-color: {theme["accent2"]};
        }}
    """