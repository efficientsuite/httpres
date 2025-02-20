from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QVBoxLayout, QSizePolicy, QGridLayout
from PyQt6.QtCore import Qt

class TagChip(QWidget):
    def __init__(self, text, remove_callback, parent=None):
        super().__init__(parent)
        self.text = text
        self.remove_callback = remove_callback
        self.init_ui()
    
    def init_ui(self):
        grid = QGridLayout(self)
        grid.setSizeConstraint(QGridLayout.SizeConstraint.SetFixedSize)  # Size the widget to its contents
        grid.setContentsMargins(4, 2, 4, 2)
        grid.setSpacing(0)
        
        self.label = QLabel(self.text, self)
        grid.addWidget(self.label, 0, 0)
        
        self.remove_button = QPushButton("x", self)
        self.remove_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.remove_button.setFlat(True)
        self.remove_button.clicked.connect(lambda: self.remove_callback(self))
        # Place the remove button in the same cell, aligned top-right
        grid.addWidget(self.remove_button, 0, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #aaa;
                border-radius: 10px;
                background-color: #eee;
                padding: 2px 4px;
            }
            QLabel {
                padding: 0;
                padding-right: 28px;
            }
        """)
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: black;
                border: none;
                padding: 0;
                margin: 0;
                margin-top: 2px;
                margin-right: 2px;
                width: 20px;
                height: 20px;
                font-size: 18px;
                color: red;
            }
            QPushButton:hover {
                background-color: #ccc;
            }
        """)

class TaggingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        # Layout to display tag chips
        self.tag_layout = QHBoxLayout()
        self.tag_layout.setSpacing(5)
        self.tag_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align all tags to the left
        main_layout.addLayout(self.tag_layout)
        
        # QLineEdit to add new tags
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Add scope...")
        self.input_line.returnPressed.connect(self.add_tag_from_input)
        main_layout.addWidget(self.input_line)
    
    def add_tag(self, tag_text):
        """Add a tag if it doesn't already exist."""
        if tag_text in self.tags:
            return
        self.tags.append(tag_text)
        chip = TagChip(tag_text, self.remove_tag)
        self.tag_layout.addWidget(chip)
    
    def add_tag_from_input(self):
        text = self.input_line.text().strip()
        if text:
            self.add_tag(text)
        self.input_line.clear()
    
    def remove_tag(self, chip_widget):
        """Remove a tag chip."""
        text = chip_widget.text
        if text in self.tags:
            self.tags.remove(text)
        chip_widget.setParent(None)
    
    def get_tags(self):
        return self.tags
    
    def clear_tags(self):
        """Clear all tag chips from the layout."""
        self.tags = []
        while self.tag_layout.count():
            item = self.tag_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def set_tags(self, tags_list):
        self.clear_tags()
        for tag in tags_list:
            self.add_tag(tag)