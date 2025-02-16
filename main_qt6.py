import sys
import json
import weakref
import uuid
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox, QTreeWidget, QDialog,
    QTreeWidgetItem, QInputDialog, QScrollArea, QFrame,
    QMenu, QTabWidget, QSplitter, QSizePolicy, QShortcut, QPlainTextEdit, QTabBar, QStatusBar
)
from PyQt6.QtGui import QIcon, QKeySequence, QFontDatabase, QFont, QGuiApplication
from PyQt6.QtCore import Qt, QEvent
from components.QNameLineEdit import QNameLineEdit
from components.QUrlLineEdit import QUrlLineEdit
from components.QHeadersTextEdit import QHeadersTextEdit
from components.QBodyTextEdit import QBodyTextEdit
from components.QResponseTextEdit import QResponseTextEdit
from fonts import load_custom_font
from styles import set_theme, get_styles, get_theme
from settings_dialog import SettingsDialog
from auth_dialog import AuthDialog
from storage import load_settings, import_from_file, export_to_file
from splash_dialog import open_splash_screen
import subprocess
from connection import request
from helpers import pretty_response_code
from QTabTitle import QTabTitle

# Enable High DPI scaling
QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    
class HttpClient(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.selected_item = None
        self.loaded_item = None
        import_from_file(self, QApplication.instance().last_collection, True)
        self.tree_widget.expandAll()
      

    def init_ui(self):
        self.setWindowTitle('httpRes - Secure HTTP Client v1.0.0')
        self.setWindowIcon(QIcon('images/icon.png'))
        load_custom_font("Roboto-Regular.ttf")
        load_custom_font("RobotoMono-Regular.ttf")
        self.resize(1600, 900)
        # Using primaryScreen instead of deprecated desktop()
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.availableGeometry() if screen else self.geometry()
        if self.width() > screen_size.width() * 0.7 or self.height() > screen_size.height() * 0.7:
            self.resize(int(screen_size.width() * 0.7), int(screen_size.height() * 0.7))

        # Center the window on the primary screen
        if screen:
            center = screen.availableGeometry().center()
            self.move(center - self.rect().center())

        # Main layout
        main_layout = QHBoxLayout()
        
        # Tree Widget for organizing requests and folders
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.open_context_menu)
        QApplication.instance().tree_widget = self.tree_widget
        
        # Enable drag and drop
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)
        self.tree_widget.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

        # Connect the item expanded and collapsed signals
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        self.tree_widget.itemCollapsed.connect(self.on_item_collapsed)

        # Wrap the tree widget in a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidget(self.tree_widget)

        # Create a container widget for the buttons
        button_container = QWidget(self)
        button_layout = QVBoxLayout(button_container)

        # Settings Button
        self.settings_button = QPushButton('Settings', self)
        self.settings_button.setFixedWidth(150)
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)
        button_layout.setAlignment(self.settings_button, Qt.AlignmentFlag.AlignCenter)

        # Hyperlink to the GitHub repository
        link = f"<a href=\"https://httpres.com\" style=\"color: {get_theme()['accent1']};\">Visit httpRes.com</a>"
        self.website_link = QLabel(link, self)
        self.website_link.setOpenExternalLinks(True)
        button_layout.addWidget(self.website_link)
        button_layout.setAlignment(self.website_link, Qt.AlignmentFlag.AlignCenter)

        # Tab widget for multiple requests
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabBar().installEventFilter(self)

        left_container = QWidget(self)
        left_layout = QVBoxLayout(left_container)
        left_layout.addWidget(self.scroll_area)
        left_layout.addWidget(button_container)

        # pull the left_layout up a bit
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        # Create a container layout to hold the main content and the status bar.
        container_layout = QVBoxLayout()
        container_layout.addLayout(main_layout)

        # Add a status bar at the bottom.
        self.status_bar = QStatusBar(self)
        self.status_bar.setFixedHeight(30)  # Ensure the status bar height is 30px
        self.status_bar.showMessage("Ready")
        container_layout.addWidget(self.status_bar)
        QApplication.instance().status_bar = self.status_bar

        self.setLayout(container_layout)

        # Apply styles
        self.setStyleSheet(get_styles())

        # Shortcut for saving with Ctrl+S
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_tab)

        # Shortcut for executing with Ctrl+Return
        execute_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        execute_shortcut.activated.connect(self.send_request)

        # Shortcut for closing tabs with Ctrl+W
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))
            

    def eventFilter(self, source, event):
        '''Override the eventFilter method to handle middle-click tab close.'''
        if event.type() == QEvent.Type.MouseButtonPress and source is self.tab_widget.tabBar():
            if event.button() == Qt.MouseButton.MiddleButton:
                tab_index = source.tabAt(event.pos())
                if tab_index != -1:
                    self.tab_widget.removeTab(tab_index)
                    return True
        return super().eventFilter(source, event)
    

    def on_item_expanded(self, item):
        """Change the icon of the folder to indicate it is open."""
        if item.data(1, 0) == 'folder':
            item.setIcon(0, QIcon('images/opened_folder.png'))
    

    def on_item_collapsed(self, item):
        """Change the icon of the folder to indicate it is closed."""
        if item.data(1, 0) == 'folder':
            item.setIcon(0, QIcon('images/closed_folder.png'))
    

    def open_context_menu(self, position):
        """Open the context menu at the given position."""
        item = self.tree_widget.itemAt(position)
        if item:
            self.selected_item = item

        menu = QMenu()
        add_folder_action = menu.addAction("Add Folder")
        add_request_action = menu.addAction("Add Request")
        rename_action = menu.addAction("Rename")
        remove_action = menu.addAction("Remove")

        add_folder_action.triggered.connect(self.add_folder)
        add_request_action.triggered.connect(self.add_request)
        rename_action.triggered.connect(self.rename_item)
        remove_action.triggered.connect(self.remove_item)

        menu.exec(self.tree_widget.viewport().mapToGlobal(position))


    def rename_item(self):
        """Rename the selected item."""
        if self.selected_item:
            current_name = self.selected_item.text(0)
            new_name, ok = QInputDialog.getText(self, 'Rename Item', 'Enter new name:', text=current_name)
            if ok and new_name:
                self.selected_item.setText(0, new_name)
                data = self.selected_item.data(2, 0) or {}
                data['name'] = new_name
                self.selected_item.setData(2, 0, data)
                req_id = data.get('id')
                for index in range(self.tab_widget.count()):
                    tab = self.tab_widget.widget(index)
                    if hasattr(tab, "request_id") and tab.request_id == req_id:
                        tab.dirty = True
                        tab_title_widget = QTabTitle(new_name + '*')
                        self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.LeftSide, tab_title_widget)
                        name_line = tab.findChild(QNameLineEdit)
                        if name_line:
                            name_line.setText(new_name)
            

    def add_folder(self):
        """Add a new folder to the tree."""
        folder_name, ok = QInputDialog.getText(self, 'Add Folder', 'Enter folder name:')
        if ok and folder_name:
            folder_item = QTreeWidgetItem(self.tree_widget, [folder_name])
            folder_item.setIcon(0, QIcon('images/closed_folder.png'))
            folder_item.setData(1, 0, 'folder')
            self.tree_widget.addTopLevelItem(folder_item)


    def add_request(self):
        """Add a new HTTP request to the selected folder."""
        if not self.selected_item or self.selected_item.data(1, 0) != 'folder':
            QMessageBox.warning(self, 'Warning', 'Please select a folder to add a request.')
            return
        request_name, ok = QInputDialog.getText(self, 'Add Request', 'Enter request name:')
        if ok and request_name:
            request_data = {
                'url': '',
                'method': 'GET',
                'headers':'''Accept: application/json\nContent-Type: application/json''',
                'body': '',
                'id': str(uuid.uuid4())
            }
            request_item = QTreeWidgetItem(self.selected_item, [request_name])
            request_item.setIcon(0, QIcon('images/request_get.png'))
            request_item.setData(1, 0, 'request')
            request_item.setData(2, 0, request_data)
            self.selected_item.addChild(request_item)


    def remove_item(self):
        """Remove the selected item from the tree."""
        if self.selected_item:
            index = self.tree_widget.indexOfTopLevelItem(self.selected_item)
            if index != -1:
                self.tree_widget.takeTopLevelItem(index)
            else:
                parent = self.selected_item.parent()
                if parent:
                    parent.removeChild(self.selected_item)


    def load_custom_font(self, font_path):
        """Load a custom font from a file."""
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                custom_font = font_families[0]
                QApplication.setFont(QFont(custom_font))


    def on_tree_item_clicked(self, item):
        """Handle tree item selection."""
        if item.data(1, 0) == 'folder':
            self.selected_item = item
        else:
            self.selected_item = item
            self.loaded_item = item
            self.open_request_in_tab(item)


    def open_request_in_tab(self, item):
        """Open the request in a new tab."""
        self.loaded_item = item
        request_data = item.data(2, 0)
        if request_data:
            for index in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(index)
                if hasattr(tab, "request_id") and tab.request_id == request_data.get('id'):
                    self.tab_widget.setCurrentIndex(index)
                    return

            tab = QWidget()
            tab.request_id = request_data.get('id')
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(5, 5, 5, 5)
            tab_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            method_combo = QComboBox(tab)
            method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE'])
            method_combo.setCurrentText(request_data.get('method', 'GET'))
            method_combo.setFixedHeight(42)

            url_input = QUrlLineEdit(tab)
            url_input.setText(request_data.get('url', ''))
            url_input.setPlaceholderText('Enter URL...')
            url_input.setFixedHeight(42)
            url_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            auth_button = QPushButton('🔒 Configure', tab)
            auth_button.setFixedHeight(42)
            auth_button.clicked.connect(lambda: self.open_auth(request_data))

            send_button = QPushButton('Send Request', tab)
            send_button.setFixedHeight(42)
            send_button.clicked.connect(lambda: self.send_request())

            input_buttons_layout = QHBoxLayout()
            input_buttons_layout.setContentsMargins(0, 0, 0, 0)
            input_buttons_layout.setSpacing(10)
            input_buttons_layout.addWidget(method_combo)
            input_buttons_layout.addWidget(url_input, 1)
            input_buttons_layout.addWidget(auth_button)
            input_buttons_layout.addWidget(send_button)

            headers_label = QLabel('Headers:')
            headers_label.setMaximumHeight(22)
            headers_input = QHeadersTextEdit(tab)
            headers_input.setPlainText(request_data.get('headers', ''))
            headers_input.setPlaceholderText(
                'Enter (key:value) pairs. One per line...\n\nExample:\nAccept: application/json\nContent-Type: application/json')
            headers_input.setMaximumHeight(140)
            headers_layout = QVBoxLayout()
            headers_layout.setContentsMargins(0, 0, 0, 0)
            headers_layout.addWidget(headers_label)
            headers_layout.addWidget(headers_input)

            body_label = QLabel('Body:')
            body_input = QBodyTextEdit(tab)
            body_input.setPlainText(request_data.get('body', ''))
            body_input.setPlaceholderText('Enter request body here (for POST/PUT requests)')
            body_input.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            body_layout = QVBoxLayout()
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.addWidget(body_label)
            body_layout.addWidget(body_input)

            headers_body_widget = QWidget()
            headers_body_layout = QVBoxLayout(headers_body_widget)
            headers_body_layout.setContentsMargins(0, 0, 0, 0)
            headers_body_layout.addLayout(headers_layout)
            headers_body_layout.addLayout(body_layout)

            response_label = QLabel('Response:')
            response_output = QResponseTextEdit(tab)
            response_output.setPlaceholderText('Response will be displayed here...')
            response_output.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

            response_layout = QVBoxLayout()
            response_layout.setContentsMargins(0, 0, 0, 0)
            response_layout.addWidget(response_label)
            response_layout.addWidget(response_output)

            response_widget = QWidget()
            response_widget.setLayout(response_layout)

            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.addWidget(headers_body_widget)
            splitter.addWidget(response_widget)

            tab_layout.addLayout(input_buttons_layout)
            tab_layout.addWidget(splitter)
            tab_layout.setStretchFactor(splitter, 1)

            index = self.tab_widget.addTab(tab, "")
            tab_title_widget = QTabTitle(request_data.get('name', 'New Request'))
            self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.LeftSide, tab_title_widget)
            tab.dirty = False

            weak_item = weakref.ref(item)
            url_input.textChanged.connect(lambda: self.set_dirty(tab, weak_item))
            method_combo.currentTextChanged.connect(lambda: self.set_dirty(tab, weak_item))
            headers_input.textChanged.connect(lambda: self.set_dirty(tab, weak_item))
            body_input.textChanged.connect(lambda: self.set_dirty(tab, weak_item))

            self.tab_widget.setCurrentIndex(index)


    def set_dirty(self, tab, weak_item):
        """Mark the current tab as dirty and update the tab title."""
        tab.dirty = True
        current_index = self.tab_widget.indexOf(tab)
        if current_index != -1:
            item = weak_item()
            if item is not None:
                tab_title = None
                if hasattr(item, 'text'):
                    tab_title = item.text(0)
                if hasattr(item, 'currentText'):
                    tab_title = item.currentText()
                if hasattr(item, 'toPlainText'):
                    tab_title = item.toPlainText()
                if tab_title and not tab_title.endswith('*'):
                    tab_title += '*'
                if tab_title:
                    self.tab_widget.tabBar().setTabButton(current_index, QTabBar.ButtonPosition.LeftSide, QTabTitle(tab_title))
                else:
                    self.tab_widget.tabBar().setTabButton(current_index, QTabBar.ButtonPosition.LeftSide, QTabTitle('Untitled*'))
            else:
                print("Item has been deleted.")


    def save_current_tab(self):
        """Save the current tab's request data and export automatically."""
        current_tab_index = self.tab_widget.currentIndex()
        current_tab = self.tab_widget.widget(current_tab_index)

        if current_tab and hasattr(current_tab, 'dirty') and current_tab.dirty:
            url_input = current_tab.findChild(QUrlLineEdit)
            method_combo = current_tab.findChild(QComboBox)
            headers_input = current_tab.findChild(QHeadersTextEdit)
            body_input = current_tab.findChild(QBodyTextEdit)

            new_data = {
                'url': url_input.text(),
                'method': method_combo.currentText(),
                'headers': headers_input.toPlainText(),
                'body': body_input.toPlainText()
            }

            old_data = self.loaded_item.data(2, 0) or {}
            old_data.update(new_data)
            self.loaded_item.setData(2, 0, old_data)
            self.loaded_item.setText(0, old_data.get('name', 'New Request'))
            current_tab.dirty = False

            tab_title = self.loaded_item.text(0)
            current_tab_index = self.tab_widget.indexOf(current_tab)
            self.tab_widget.tabBar().setTabButton(current_tab_index, QTabBar.ButtonPosition.LeftSide, QTabTitle(tab_title))

            export_to_file(self, QApplication.instance().last_collection)
            QMessageBox.information(self, 'Success', 'Request saved successfully!')


    def close_tab(self, index):
        """Close the tab at the given index."""
        self.tab_widget.removeTab(index)


    def send_request(self):
        """Send the HTTP request with certificate and proxy handling."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return

        send_request_button = current_tab.findChildren(QPushButton)[1]
        url_input = current_tab.findChild(QUrlLineEdit)
        method_combo = current_tab.findChild(QComboBox)
        headers_input = current_tab.findChild(QHeadersTextEdit)
        body_input = current_tab.findChild(QBodyTextEdit)
        response_output = current_tab.findChild(QResponseTextEdit)

        url = url_input.text()
        method = method_combo.currentText()
        headers = headers_input.toPlainText()
        body = body_input.toPlainText()
        response_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        send_request_button.setEnabled(False)
        response_output.setPlainText('Sending...')

        request_data = self.loaded_item.data(2, 0) or {}
        request_data.update({
            'url': url,
            'method': method,
            'headers': headers,
            'body': body
        })

        try:
            response_code, res, auth_usage_details, curl_command = request(request_data)
            response_output.setPlainText('')
            stdout = ''
            stderr = ''
            if isinstance(res, dict):
                stdout = res.get('stdout', '')
                stderr = res.get('stderr', '')
            else:
                stdout = res.stdout if res.stdout else ''
                stderr = res.stderr if res.stderr else ''
            if stdout != '' and stdout == '':
                if stderr != '':
                    response_output.setPlainText('🚫 Error:\n\n' + stderr)
                else:
                    response_output.setPlainText('Unknown Error. Empty response.')
            else:
                if stdout != '':
                    response_output.setPlainText(stdout)
                    response_output.formatJSON()

                response_code = pretty_response_code(response_code)
                response_output.setPlainText('C̲o̲d̲e̲: ' + response_code + '\n\nD̲a̲t̲a̲:\n\n' + response_output.toPlainText())
                
                if auth_usage_details:
                    response_output.setPlainText(response_output.toPlainText() + '\n\n\nA̲u̲t̲h̲e̲n̲t̲i̲c̲a̲t̲i̲o̲n̲: 🔒\n\n' + auth_usage_details)
                
                if stderr != '':
                    connection_data = stderr
                    connection_data = connection_data.replace("200 OK", "200 OK ✅")
                    connection_data = connection_data.replace("TLSv", "🔒TLSv")
                    connection_data = connection_data.replace("SSL", "🔒SSL")
                    connection_data = connection_data.replace("Server certificate", "🪪Server certificate")
                    connection_data = connection_data.replace("Certificate", "🪪Certificate")
                    connection_data = connection_data.replace("hello", "🖐️hello")
                    response_output.setPlainText(response_output.toPlainText() + '\n\n\nC̲o̲n̲n̲e̲c̲t̲i̲o̲n̲ 🤝\n\n' + connection_data)

                if curl_command:
                    response_output.setPlainText(response_output.toPlainText() + '\n\n\nC̲URL Command Used 🆑\n\n' + ' '.join(curl_command))
                
        except subprocess.CalledProcessError as e:
            response_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            response_output.setPlainText(f'Request failed:\n\n{str(e)}')
        except json.JSONDecodeError:
            response_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            response_output.setPlainText('Invalid JSON in request body.\n\nThe request was not sent.')
        except Exception as e:
            response_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            response_output.setPlainText(f'An unknown error occurred:\n\n{str(e)}')

        send_request_button.setEnabled(True)


    def open_settings(self):
        """Opens a settings dialog with options to add certificates and proxies."""
        dialog = SettingsDialog(self)
        dialog.exec()


    def open_auth(self, request_data):
        """Opens an auth dialog with options to add various types of authentication/authorization."""
        if 'auth' not in request_data:
            request_data['auth'] = {}
        dialog = AuthDialog(request_data, self)
        dialog.set_data(request_data['auth'])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            request_data['auth'] = data
            if self.loaded_item:
                self.loaded_item.setData(2, 0, request_data)
            current_tab = self.tab_widget.currentWidget()
            if current_tab:
                current_tab.dirty = True
                index = self.tab_widget.currentIndex()
                tab_title = self.tab_widget.tabText(index)
                if not tab_title.endswith('*'):
                    self.tab_widget.tabBar().setTabButton(index, QTabBar.ButtonPosition.LeftSide, QTabTitle(tab_title + '*'))
    

    def load_request_data(self, request_data):
        url_input = self.findChild(QUrlLineEdit)
        method_combo = self.findChild(QComboBox)
        headers_input = self.findChild(QHeadersTextEdit)
        body_input = self.findChild(QBodyTextEdit)
        url_input.setText(request_data.get('url', ''))
        method_combo.setCurrentText(request_data.get('method', ''))
        headers_input.setPlainText(request_data.get('headers', ''))
        body_input.setPlainText(request_data.get('body', ''))
        print(f"Loaded headers: {request_data.get('headers', '')}")
        print(f"Headers input text after setting: {headers_input.toPlainText()}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_settings()
    set_theme(QApplication.instance().settings.get('theme', 'Light'))
    accepted, password = open_splash_screen()
    if accepted:
        QApplication.instance().password = password
        client = HttpClient()
        client.show()
        sys.exit(app.exec())
    else:
        sys.exit()