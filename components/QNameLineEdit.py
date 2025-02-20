from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt

class QNameLineEdit(QLineEdit):

    # add the syntax highlighter to the text edit
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            # Insert two spaces instead of a tab character
            self.insertPlainText('  ')  # Two spaces
            return  # Prevent the default tab behavior
        super().keyPressEvent(event)  # Call the base class method for other keys
