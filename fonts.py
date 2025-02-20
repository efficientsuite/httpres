import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from resources import resource_path

def load_custom_font(font_filename):
    """Load a custom font from a file."""
    font_id = QFontDatabase.addApplicationFont(os.path.join(resource_path('fonts'), font_filename))
    if font_id != -1:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            custom_font = font_families[0]
            font = QFont(custom_font)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            QApplication.setFont(font)
