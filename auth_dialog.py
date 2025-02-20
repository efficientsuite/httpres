from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTabWidget, QDialog, QComboBox, QStackedWidget, QCheckBox, QTextEdit, QFileDialog, QStyle
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from tag_widget import TaggingWidget
from resources import resource_path

class AuthDialog(QDialog):
    def __init__(self, request_data, parent=None):
        super().__init__(parent)
        self.request_data = request_data
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowTitle('Configure Request: ' + request_data.get('name', ''))
        self.setWindowIcon(QIcon(resource_path(('images/icon.png'))))
        self.resize(800, 600)
        screen_size = QApplication.primaryScreen().geometry()
        if self.width() > screen_size.width() * 0.6 or self.height() > screen_size.height() * 0.6:
            self.resize(int(screen_size.width() * 0.6), int(screen_size.height() * 0.6))
        self.move(QApplication.primaryScreen().availableGeometry().center() - self.rect().center())
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Tab widget
        self.tab_widget = QTabWidget(self)

        # Content margin
        self.tab_widget.setStyleSheet('QTabWidget::pane { padding: 10px; }')

        # Bearer tab
        self.bearer_tab = QWidget()
        bearer_layout = QVBoxLayout(self.bearer_tab)
        bearer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align to top
        
        bearer_label = QLabel("Bearer Token")
        self.bearer_token_input = QLineEdit(self.bearer_tab)
        self.bearer_token_input.setPlaceholderText("<token>")
        bearer_layout.addWidget(bearer_label)
        bearer_layout.addWidget(self.bearer_token_input)
       
        # OAuth tab
        self.oauth_tab = QWidget()
        oauth_layout = QVBoxLayout(self.oauth_tab)
        oauth_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align to top
        
        token_url_label = QLabel("Token URL")
        self.token_url_input = QLineEdit(self.oauth_tab)
        self.token_url_input.setPlaceholderText("https://domain.com/oauth/token")
        oauth_layout.addWidget(token_url_label)
        oauth_layout.addWidget(self.token_url_input)
        
        grant_type_label = QLabel("Grant Type")
        self.grant_type_combo = QComboBox(self.oauth_tab)
        self.grant_type_combo.addItems(["Client Credentials", "Authorization Code", "Password", "Implicit"])
        oauth_layout.addWidget(grant_type_label)
        oauth_layout.addWidget(self.grant_type_combo)
        
        # Create a stacked widget to hold different sets of input fields
        self.stacked_widget = QStackedWidget(self.oauth_tab)
        oauth_layout.addWidget(self.stacked_widget)
        
        # Create input fields for each grant type
        self.client_credentials_widget = QWidget()
        client_credentials_layout = QVBoxLayout(self.client_credentials_widget)
        client_credentials_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align to top
        client_credentials_layout.addWidget(QLabel("Client ID"))
        self.client_id_input = QLineEdit()
        client_credentials_layout.addWidget(self.client_id_input)
        client_credentials_layout.addWidget(QLabel("Client Secret"))
        self.client_secret_input = QLineEdit()
        client_credentials_layout.addWidget(self.client_secret_input)
        
        self.authorization_code_widget = QWidget()
        authorization_code_layout = QVBoxLayout(self.authorization_code_widget)
        self.authorization_code_input = QLineEdit()
        authorization_code_layout.addWidget(self.authorization_code_input)
        authorization_code_layout.addWidget(QLabel("Authorization Code"))
        authorization_code_layout.addWidget(QLineEdit())
        
        self.password_widget = QWidget()
        password_layout = QVBoxLayout(self.password_widget)
        password_layout.addWidget(QLabel("Username"))
        password_layout.addWidget(QLineEdit())
        password_layout.addWidget(QLabel("Password"))
        password_layout.addWidget(QLineEdit())
        
        self.implicit_widget = QWidget()
        implicit_layout = QVBoxLayout(self.implicit_widget)
        implicit_layout.addWidget(QLabel("Implicit Grant Type"))
        
        # Add widgets to the stacked widget
        self.stacked_widget.addWidget(self.client_credentials_widget)
        self.stacked_widget.addWidget(self.authorization_code_widget)
        self.stacked_widget.addWidget(self.password_widget)
        self.stacked_widget.addWidget(self.implicit_widget)
        
        # Connect combobox selection change to a function to switch the stacked widget
        self.grant_type_combo.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # Replace previous scopes area with tagging widget
        scope_label = QLabel("Scopes")
        oauth_layout.addWidget(scope_label)
        self.tagging_widget = TaggingWidget(self.oauth_tab)
        oauth_layout.addWidget(self.tagging_widget)
        
        # Certificate tab
        self.certificate_tab = QWidget()
        certificate_layout = QVBoxLayout(self.certificate_tab)
        certificate_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align to top

        # CA Certificate
        ca_certificate_label = QLabel("CA Certificate")
        
        ca_certificate_hbox = QHBoxLayout()
        self.ca_certificate_input = QLineEdit(self.certificate_tab)
        self.ca_certificate_input.setPlaceholderText("<Path/To/CA.pem>")
        
        ca_certificate_browse_button = QPushButton(self.certificate_tab)
        ca_certificate_browse_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        ca_certificate_browse_button.setIconSize(QSize(22, 24))
        ca_certificate_browse_button.setFixedSize(24, 36)
        ca_certificate_browse_button.clicked.connect(lambda: self.load_file(self.ca_certificate_input))
        
        ca_certificate_hbox.addWidget(self.ca_certificate_input)
        ca_certificate_hbox.addWidget(ca_certificate_browse_button)
        
        certificate_layout.addWidget(ca_certificate_label)
        certificate_layout.addLayout(ca_certificate_hbox)

        # Client Certificate
        client_certificate_label = QLabel("Client Certificate")
        client_certificate_label.setStyleSheet('QLabel { margin-top: 20px; }')
        
        client_certificate_hbox = QHBoxLayout()
        self.client_certificate_input = QLineEdit(self.certificate_tab)
        self.client_certificate_input.setPlaceholderText("<Path/To/Client.pem>")
        
        client_certificate_browse_button = QPushButton(self.certificate_tab)
        client_certificate_browse_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        client_certificate_browse_button.setIconSize(QSize(22, 24))
        client_certificate_browse_button.setFixedSize(24, 36)
        client_certificate_browse_button.clicked.connect(lambda: self.load_file(self.client_certificate_input))
        
        client_certificate_hbox.addWidget(self.client_certificate_input)
        client_certificate_hbox.addWidget(client_certificate_browse_button)
        
        certificate_layout.addWidget(client_certificate_label)
        certificate_layout.addLayout(client_certificate_hbox)

        # Private Key
        private_key_label = QLabel("Private Key")
        private_key_label.setStyleSheet('QLabel { margin-top: 20px; }')
        
        private_key_hbox = QHBoxLayout()
        self.private_key_input = QLineEdit(self.certificate_tab)
        self.private_key_input.setPlaceholderText("<Path/To/Private.pem>")
        
        private_key_browse_button = QPushButton(self.certificate_tab)
        private_key_browse_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        private_key_browse_button.setIconSize(QSize(22, 24))
        private_key_browse_button.setFixedSize(24, 36)
        private_key_browse_button.clicked.connect(lambda: self.load_file(self.private_key_input))
        
        private_key_hbox.addWidget(self.private_key_input)
        private_key_hbox.addWidget(private_key_browse_button)
        
        certificate_layout.addWidget(private_key_label)
        certificate_layout.addLayout(private_key_hbox)

        private_key_password_label = QLabel("Private Key Password")
        private_key_password_label.setStyleSheet('QLabel { margin-top: 20px; }')
        self.private_key_password_input = QLineEdit(self.certificate_tab)
        self.private_key_password_input.setPlaceholderText("<Password1234>")
        self.private_key_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        certificate_layout.addWidget(private_key_password_label)
        certificate_layout.addWidget(self.private_key_password_input)

        self.verify_checkbox = QCheckBox("Verify Server Key (Against system keystore)", self.certificate_tab)
        self.verify_checkbox.setStyleSheet('QCheckBox { margin-top: 20px; }')
        certificate_layout.addWidget(self.verify_checkbox)

        # Basic tab
        self.basic_tab = QWidget()
        basic_layout = QVBoxLayout(self.basic_tab)
        basic_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align to top
        
        username_label = QLabel("Username")
        self.username_input = QLineEdit(self.basic_tab)
        self.username_input.setPlaceholderText("Username")
        basic_layout.addWidget(username_label)
        basic_layout.addWidget(self.username_input)
        
        password_label = QLabel("Password")
        self.password_input = QLineEdit(self.basic_tab)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        basic_layout.addWidget(password_label)
        basic_layout.addWidget(self.password_input)
        
        # Add new Proxy tab
        self.proxy_tab = QWidget()
        proxy_layout = QVBoxLayout(self.proxy_tab)
        proxy_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        proxy_host_label = QLabel("Proxy Host")
        self.proxy_host_input = QLineEdit(self.proxy_tab)
        self.proxy_host_input.setPlaceholderText("Proxy Host")
        proxy_layout.addWidget(proxy_host_label)
        proxy_layout.addWidget(self.proxy_host_input)
        proxy_port_label = QLabel("Proxy Port")
        self.proxy_port_input = QLineEdit(self.proxy_tab)
        self.proxy_port_input.setPlaceholderText("Proxy Port")
        proxy_layout.addWidget(proxy_port_label)
        proxy_layout.addWidget(self.proxy_port_input)
        proxy_username_label = QLabel("Proxy Username")
        self.proxy_username_input = QLineEdit(self.proxy_tab)
        self.proxy_username_input.setPlaceholderText("Proxy Username")
        proxy_layout.addWidget(proxy_username_label)
        proxy_layout.addWidget(self.proxy_username_input)
        proxy_password_label = QLabel("Proxy Password")
        self.proxy_password_input = QLineEdit(self.proxy_tab)
        self.proxy_password_input.setPlaceholderText("Proxy Password")
        self.proxy_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        proxy_layout.addWidget(proxy_password_label)
        proxy_layout.addWidget(self.proxy_password_input)
        
        # Add tabs to the tab widget
        self.tab_widget.addTab(self.bearer_tab, 'Bearer')
        self.tab_widget.addTab(self.oauth_tab, 'OAuth 2.0')
        self.tab_widget.addTab(self.certificate_tab, 'Certificate')
        self.tab_widget.addTab(self.basic_tab, 'Basic')
        self.tab_widget.addTab(self.proxy_tab, 'Proxy')
        
        # Store base titles and add padding via stylesheet
        self.base_tab_titles = ['Bearer', 'OAuth 2.0', 'Certificate', 'Basic', 'Proxy']
        self.tab_widget.tabBar().setStyleSheet("QTabBar::tab { min-width: 100px; padding-left: 10px; padding-right: 10px; }")
        
        # Connect currentChanged to update_tab_titles and update titles initially
        self.tab_widget.currentChanged.connect(self.update_tab_titles)
        self.update_tab_titles(self.tab_widget.currentIndex())
        
        # Connect editingFinished signal on each field to update checkmarks when focus is lost
        fields = [
            self.bearer_token_input, self.token_url_input,
            self.client_id_input, self.client_secret_input,
            self.authorization_code_input,
            self.client_certificate_input, self.ca_certificate_input,
            self.private_key_input, self.private_key_password_input,
            self.username_input, self.password_input,
            self.proxy_host_input, self.proxy_port_input,
            self.proxy_username_input, self.proxy_password_input
        ]
        for field in fields:
            field.editingFinished.connect(lambda: self.update_tab_titles(self.tab_widget.currentIndex()))
        
        # Add tab widget to the main layout
        main_layout.addWidget(self.tab_widget)
        
        # Add save, cancel, clear all, copy all, and paste all buttons
        button_layout = QHBoxLayout()
        self.clear_all_button = QPushButton("Clear All", self)
        self.clear_all_button.setStyleSheet('QPushButton { background-color: #ccc; } QPushButton:hover { background-color: #ddd; }')
        self.clear_all_button.clicked.connect(self.clear_all_fields)
        button_layout.addWidget(self.clear_all_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.copy_all_button = QPushButton("Copy All", self)
        self.copy_all_button.setStyleSheet('QPushButton { background-color: #ccc; } QPushButton:hover { background-color: #ddd; }')
        self.copy_all_button.clicked.connect(self.copy_all_fields)
        button_layout.addWidget(self.copy_all_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.paste_all_button = QPushButton("Paste All", self)
        self.paste_all_button.setStyleSheet('QPushButton { background-color: #ccc; } QPushButton:hover { background-color: #ddd; }')
        self.paste_all_button.clicked.connect(self.paste_all_fields)
        button_layout.addWidget(self.paste_all_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        button_layout.addStretch()  # Push following widgets to the right
        self.encyption_used_label = QLabel('🔒 All plain-text fields are encrypted.')
        button_layout.addWidget(self.encyption_used_label)
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.setStyleSheet('QPushButton { background-color: #ccc; } QPushButton:hover { background-color: #ddd; }')
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save)
        button_layout.addWidget(self.save_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)
        
        # Set the main layout to the dialog
        self.setLayout(main_layout)


    def load_file(self, line_edit):
        """Load file path into the specified QLineEdit."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            line_edit.setText(file_path)


    def update_tab_titles(self, index):
        # Update each tab: set text to base title and, if any field in the tab has data, set an icon from images/checkmark.png.
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabText(i, self.base_tab_titles[i])
            if self._has_data(i):
                self.tab_widget.setTabIcon(i, QIcon(resource_path('images/checkmark.png')))
            else:
                self.tab_widget.setTabIcon(i, QIcon())


    def _has_data(self, index):
        # Check if any text field in the specified tab has a non-empty value
        if index == 0:
            # Bearer tab
            return bool(self.bearer_token_input.text().strip())
        elif index == 1:
            # OAuth tab
            return any([
                self.token_url_input.text().strip(),
                self.client_id_input.text().strip(),
                self.client_secret_input.text().strip(),
                self.authorization_code_input.text().strip()
            ])
        elif index == 2:
            # Certificate tab
            return any([
                self.client_certificate_input.text().strip(),
                self.ca_certificate_input.text().strip(),
                self.private_key_input.text().strip(),
                self.private_key_password_input.text().strip()
            ])
        elif index == 3:
            # Basic tab
            return any([
                self.username_input.text().strip(),
                self.password_input.text().strip()
            ])
        elif index == 4:
            # Proxy tab
            return any([
                self.proxy_host_input.text().strip(),
                self.proxy_port_input.text().strip(),
                self.proxy_username_input.text().strip(),
                self.proxy_password_input.text().strip()
            ])
        return False


    def save(self):
        '''Save the data and close the dialog.'''
        data = self.get_data()
        self.request_data.update(data)
        self.accept()  # Trigger the accepted state instead of just closing


    def get_data(self):
        # Return a nested dictionary capturing all auth data and the active method
        return {
            'active': self.base_tab_titles[self.tab_widget.currentIndex()],
            'bearer': {
                'token': self.bearer_token_input.text()
            },
            'oauth': {
                'token_url': self.token_url_input.text(),
                'grant_type': self.grant_type_combo.currentText(),
                'client_id': self.client_id_input.text(),
                'client_secret': self.client_secret_input.text(),
                'authorization_code': self.authorization_code_input.text(),
                'scopes': self.tagging_widget.get_tags()
            },
            'certificate': {
                'client_certificate': self.client_certificate_input.text(),
                'ca_certificate': self.ca_certificate_input.text(),
                'private_key': self.private_key_input.text(),
                'private_key_password': self.private_key_password_input.text(),
                'verify': self.verify_checkbox.isChecked()
            },
            'basic': {
                'username': self.username_input.text(),
                'password': self.password_input.text()
            },
            'proxy': {
                'host': self.proxy_host_input.text(),
                'port': self.proxy_port_input.text(),
                'username': self.proxy_username_input.text(),
                'password': self.proxy_password_input.text()
            }
        }


    def set_data(self, data):
        # Load nested data into respective auth fields
        bearer = data.get('bearer', {})
        oauth = data.get('oauth', {})
        certificate = data.get('certificate', {})
        basic = data.get('basic', {})
        proxy = data.get('proxy', {})
        self.bearer_token_input.setText(bearer.get('token', ''))
        self.token_url_input.setText(oauth.get('token_url', ''))
        self.grant_type_combo.setCurrentText(oauth.get('grant_type', 'Client Credentials'))
        self.client_id_input.setText(oauth.get('client_id', ''))
        self.client_secret_input.setText(oauth.get('client_secret', ''))
        self.authorization_code_input.setText(oauth.get('authorization_code', ''))
        self.tagging_widget.set_tags(oauth.get('scopes', []))
        self.client_certificate_input.setText(certificate.get('client_certificate', ''))
        self.ca_certificate_input.setText(certificate.get('ca_certificate', ''))
        self.private_key_input.setText(certificate.get('private_key', ''))
        self.private_key_password_input.setText(certificate.get('private_key_password', ''))
        self.verify_checkbox.setChecked(certificate.get('verify', False))
        self.username_input.setText(basic.get('username', ''))
        self.password_input.setText(basic.get('password', ''))
        self.proxy_host_input.setText(proxy.get('host', ''))
        self.proxy_port_input.setText(proxy.get('port', ''))
        self.proxy_username_input.setText(proxy.get('username', ''))
        self.proxy_password_input.setText(proxy.get('password', ''))
        # Set active tab based on provided value
        active = data.get('active', 'Bearer')
        if active in self.base_tab_titles:
            self.tab_widget.setCurrentIndex(self.base_tab_titles.index(active))
        self.update_tab_titles(self.tab_widget.currentIndex())


    def clear_all_fields(self):
        """Clear all text fields in the auth dialog."""
        fields = [
            self.bearer_token_input, self.token_url_input,
            self.client_id_input, self.client_secret_input,
            self.authorization_code_input,
            self.client_certificate_input, self.ca_certificate_input,
            self.private_key_input, self.private_key_password_input,
            self.username_input, self.password_input,
            self.proxy_host_input, self.proxy_port_input,
            self.proxy_username_input, self.proxy_password_input
        ]
        for field in fields:
            field.clear()
        self.tagging_widget.set_tags([])  # Clear scopes


    def copy_all_fields(self):
        """Copy all auth fields data to the clipboard as JSON."""
        import json
        data = self.get_data()
        json_data = json.dumps(data, indent=2)
        QApplication.instance().clipboard().setText(json_data)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Copy Successful", "All fields successfully copied.\nNote: Data is not copied to the system clipboard.")


    def paste_all_fields(self):
        """Paste all auth fields data from the clipboard."""
        import json
        clipboard_text = QApplication.instance().clipboard().text()
        from PyQt6.QtWidgets import QMessageBox
        try:
            data = json.loads(clipboard_text)
            self.set_data(data)
            QMessageBox.information(self, "Paste Successful", "All fields successfully pasted.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Paste Error", "The application clipboard does not contain data.")