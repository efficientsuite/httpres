from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

class QTabTitle(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)
        label = QLabel(text, self)
        label.setStyleSheet('max-width: 290px; background-color: none;')
        layout.addWidget(label)