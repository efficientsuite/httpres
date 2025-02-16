import os
import json
import sys
from PyQt5.QtWidgets import (
    QApplication, 
    QMessageBox,
    QFileDialog
)
from encryption import encrypt_json, decrypt_json
from helpers import tree_to_dict, dict_to_tree

def load_settings():
    """Load certificates, proxies, and theme from settings.json without encryption."""
    try:
        if not os.path.exists('settings.json'):
            with open('settings.json', 'w') as f:
                json.dump({'theme': 'Light'}, f, indent=4)
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        QApplication.instance().settings = settings
        return settings
    except Exception as e:
        print(e)
        return None


def save_settings(self, theme, current_password, new_password, confirm_password):
    '''Save settings and change password if requested.'''
    tmp_password = QApplication.instance().password  # Store the current password
    last_collection = QApplication.instance().last_collection

    # Validate inputs
    if tmp_password is None:
        return
    if tmp_password != current_password:
        return
    if theme not in ['Light', 'Dark']:
        return
    
    # If a new password is provided, attempt to change it
    if new_password and len(new_password) > 0:
        if new_password != confirm_password:
            QMessageBox.critical(self, 'Error', 'New password and confirmation do not match.')
            return
        if current_password != tmp_password:
            QMessageBox.critical(self, 'Error', 'Current password is incorrect.')
            return
        try:
            QApplication.instance().password = new_password
            # Verify the new password by exporting and importing collections
            filename = export_to_file(self)
            import_from_file(self, filename, expand_all=True)
        except Exception as e:
            QApplication.instance().password = tmp_password  # Revert on error
            QMessageBox.critical(self, 'Error', f'Password change failed: {e}')
            return

    settings = {'theme': theme, 'last_collection': last_collection}
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)
    QApplication.instance().settings = settings
    self.close()

def create_collections_folder():
    if not os.path.exists('collections'):
        os.makedirs('collections')

def export_to_file(self, file_name=None):
    """Export collections as encrypted JSON."""
    tree_widget = QApplication.instance().tree_widget
    create_collections_folder()
    if not file_name:
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', 'collections/default.json', 'JSON Files (*.json)')
    if file_name:
        data = tree_to_dict(self, tree_widget)
        password = QApplication.instance().password
        encrypted_data = encrypt_json(data, password)
        with open(file_name, 'w') as f:
            json.dump(encrypted_data, f, indent=4)
    return file_name

def import_from_file(self, file_name=None, expand_all=True):
    """Import collections from encrypted JSON."""
    tree_widget = QApplication.instance().tree_widget
    create_collections_folder()

    if QApplication.instance().last_collection:
        if not os.path.exists(QApplication.instance().last_collection):
            # create empty file
            with open(QApplication.instance().last_collection, 'w') as f:
                f.write('')
            file_name = QApplication.instance().last_collection

    if not file_name:
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', 'collections/default.json', 'JSON Files (*.json)')
    if file_name:
        try:
            password = QApplication.instance().password
            tree_widget.clear()
            with open(file_name, 'r+') as f:
                if os.stat(file_name).st_size != 0:
                    encrypted_data = json.load(f)
                    data, success = decrypt_json(encrypted_data, password)
                    if not success:
                        raise Exception("Decryption failed")
                    dict_to_tree(self, data, tree_widget)
                    if expand_all:
                        tree_widget.expandAll()
                self.loaded_item = None
                self.selected_item = None
            QApplication.instance().last_collection = file_name
            QApplication.instance().status_bar.showMessage("📚 Collection File: " + file_name)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, 'Error', 'Failed to load/decrypt collection data.\n\nIf you cannot remember your password you must delete collections/default.json and start over.')
            sys.exit()
    
    QApplication.instance().status_bar.showMessage("📚 Collection File: " + file_name)
    
