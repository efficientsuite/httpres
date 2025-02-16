import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTabWidget, QDialog, QMessageBox, QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from storage import load_settings, save_settings
from resources import resource_path

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
      
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon(resource_path('images/icon.png')))
        self.resize(350, 380)
         # If the window exceeds 60% of the screen size, resize it to 60% of the screen size
        screen_size = QApplication.desktop().screenGeometry()
        if self.width() > screen_size.width() * 0.6 or self.height() > screen_size.height() * 0.6:
            self.resize(int(screen_size.width() * 0.6), int(screen_size.height() * 0.6))
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

        # Load settings
        self.settings = load_settings()
        if self.settings is None:
          return
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Tab widget for settings; removed Certificates and Proxies tabs
        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().setStyleSheet("QTabBar::tab { min-width: 100px; padding-left: 10px; padding-right: 10px; }")
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.tabCloseRequested.connect(lambda index: self.tab_widget.removeTab(index))
        
        # Removed: Certificates tab and Proxies tab
        # Add Password tab
        self.password_tab = QWidget()
        password_layout = QVBoxLayout(self.password_tab)
        password_layout.setContentsMargins(20, 20, 20, 20)
        self.current_password_label = QLabel('Current Password:')
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_label = QLabel('New Password:')
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_label = QLabel('Confirm New Password:')
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.current_password_label)
        password_layout.addWidget(self.current_password_input)
        password_layout.addWidget(self.new_password_label)
        password_layout.addWidget(self.new_password_input)
        password_layout.addWidget(self.confirm_password_label)
        password_layout.addWidget(self.confirm_password_input)
        password_layout.setAlignment(Qt.AlignTop)
        self.tab_widget.addTab(self.password_tab, 'Password')
        
        # Theme tab
        self.theme_tab = QWidget()
        theme_layout = QVBoxLayout(self.theme_tab)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        self.theme_label = QLabel('Select Theme:')
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Light', 'Dark'])
        self.theme_combo.setCurrentText(QApplication.instance().settings.get('theme', 'Dark'))
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.setAlignment(Qt.AlignTop)
        self.tab_widget.addTab(self.theme_tab, 'Theme')
        
        # Add tab widget to the main layout
        main_layout.addWidget(self.tab_widget)
        
        # Update save button to use only theme and password inputs
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.setStyleSheet('QPushButton { background-color: #ccc; } QPushButton:hover { background-color: #ddd; }')
        self.cancel_button.clicked.connect(self.close)
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(lambda: save_settings(self,
            self.theme_combo.currentText(),
            self.current_password_input.text(),
            self.new_password_input.text(),
            self.confirm_password_input.text()))
       
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        button_layout.setAlignment(Qt.AlignRight)
        main_layout.addLayout(button_layout)
        
        # Set the main layout to the dialog
        self.setLayout(main_layout)

