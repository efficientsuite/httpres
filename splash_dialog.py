import os
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QDialogButtonBox, QLineEdit,
    QDialog, QPushButton, QFileDialog, QStyle
)
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from fonts import load_custom_font
from styles import get_styles
from resources import resource_path


def create_collections_folder():
    # Create collections folder if it doesn't exist
    if not os.path.exists('collections'):
        os.makedirs('collections')
    # Create default.json if it doesn't exist
    if not os.path.exists('collections/default.json'):
        with open('collections/default.json', 'w') as f:
            f.write('')


def open_splash_screen():
    create_collections_folder()
    load_custom_font("Roboto-Regular.ttf")
    # Create a custom dialog for password input
    dialog = QDialog()

    # set max height and width
    dialog.setMaximumSize(1024, 768)

    # Apply styles
    dialog.setWindowTitle('httpRes')
    dialog.setWindowIcon(QIcon(resource_path('images/icon.png')))
    dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
    dialog.setStyleSheet('background-color: #ffffff;')

    # Create main vertical layout
    main_layout = QVBoxLayout(dialog)

    # Apply styles
    rsc_path = resource_path('')
    stylesheet = get_styles(rsc_path)
    dialog.setStyleSheet(stylesheet)

    # Add banner image at the top
    banner_label = QLabel()
    banner_pixmap = QPixmap(resource_path('images/splash_banner.png'))
    banner_pixmap = banner_pixmap.scaled(1024, 128, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    banner_label.setPixmap(banner_pixmap)
    banner_label.setFixedSize(1024, 128)
    banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(banner_label)
    
    # Use QFormLayout for consistent label/field alignment (added directly to main_layout)
    form_layout = QFormLayout()
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    form_layout.setSpacing(10)
    form_layout.setContentsMargins(30, 30, 30, 0)
    
    # File selection
    def browse_file():
        file_path, _ = QFileDialog.getOpenFileName(dialog, "Select File", "collections", "JSON Files (*.json);;All Files (*)")
        if file_path:
            selected_file_lineedit.setText(file_path)

    def create_new_collection():
        base_name = "collections/new_collection"
        ext = ".json"
        default_name = base_name + ext
        if os.path.exists(default_name):
            i = 2
            while os.path.exists(f"{base_name}_{i}{ext}"):
                i += 1
            default_name = f"{base_name}_{i}{ext}"
            
        file_path, _ = QFileDialog.getSaveFileName(
            dialog,
            "Create New Collection",
            default_name,
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            selected_file_lineedit.setText(file_path)
            # Automatically select the new collection as the default import file
            QApplication.instance().last_collection = file_path
    
    selected_file_lineedit = QLineEdit()
    selected_file_lineedit.setReadOnly(True)
    selected_file_lineedit.setText(QApplication.instance().settings.get('last_collection', 'collections/default.json'))
    
    browse_button = QPushButton()
    browse_button.setIcon(dialog.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
    browse_button.setIconSize(QSize(16, 16))
    browse_button.setFixedSize(30, 30)
    browse_button.clicked.connect(browse_file)
    
    new_collection_button = QPushButton()
    new_collection_button.setIcon(dialog.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    new_collection_button.setIconSize(QSize(16, 16))
    new_collection_button.setFixedSize(30, 30)
    new_collection_button.clicked.connect(create_new_collection)
    
    file_hbox = QHBoxLayout()
    file_hbox.addWidget(selected_file_lineedit)
    file_hbox.addWidget(browse_button)
    file_hbox.addWidget(new_collection_button)
    
    form_layout.addRow("Collection file:", file_hbox)
    
    # Password input
    password_input = QLineEdit()
    password_input.setEchoMode(QLineEdit.EchoMode.Password)
    form_layout.addRow("Password:", password_input)
    
    # Button box at the bottom of the form
    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    button_box.button(QDialogButtonBox.StandardButton.Ok).setMinimumWidth(100)
    button_box.button(QDialogButtonBox.StandardButton.Cancel).setMinimumWidth(100)
    form_layout.addRow("", button_box)
    
    # Add form layout directly to the main layout
    main_layout.addLayout(form_layout)
    
    # Add some spacing and then add the web view underneath.
    web_view = QWebEngineView()
    web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
    web_view.setUrl(QUrl("https://httpres.com/news.html?theme=" + QApplication.instance().settings.get('theme', 'Dark')))
    main_layout.addWidget(web_view)
    
    # Set default file for import
    QApplication.instance().last_collection = 'collections/default.json'
    
    def on_accept():
        QApplication.instance().last_collection = selected_file_lineedit.text()
        dialog.accept()
    
    def on_reject():
        dialog.reject()
    
    button_box.accepted.connect(on_accept)
    button_box.rejected.connect(on_reject)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return True, password_input.text()
    else:
        return False, None
