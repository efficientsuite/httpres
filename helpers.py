from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidgetItem
from resources import resource_path

def item_to_dict(self, item):
    """Convert a QTreeWidgetItem into a dictionary."""
    item_data = {
        'name': item.text(0),
        'type': item.data(1, 0)
    }

    if item.data(1, 0) == 'request':
        request_data = item.data(2, 0)
        if request_data:
            request_data['name'] = item.text(0)
            item_data['request'] = request_data
        return item_data

    # If it's a folder, process its children recursively
    children = []
    for i in range(item.childCount()):
        child_item = item.child(i)
        children.append(item_to_dict(self, child_item))

    if children:
        item_data['children'] = children

    return item_data


def tree_to_dict(self, tree_widget):
    data = []
    for i in range(tree_widget.topLevelItemCount()):
        item = tree_widget.topLevelItem(i)
        data.append(item_to_dict(self, item))
    return data


def dict_to_tree(self, data, tree_widget):
    '''Column 0 is the name, column 1 is the type, and column 2 is the request data.'''
    for item_data in data:
        # Get the request data if it exists
        request_data = item_data.get('request', {})
        
        # Create a new item with the name
        item = QTreeWidgetItem(tree_widget, [item_data['name']])

        # Set the icon based on the type
        if item_data['type'] == 'folder':
            item.setIcon(0, QIcon(resource_path('images/closed_folder.png')))
        if item_data['type'] == 'request':
            if request_data.get('method', 'GET') == 'GET':
                item.setIcon(0, QIcon(resource_path('images/request_get.png')))
            elif request_data.get('method') == 'POST':
                item.setIcon(0, QIcon(resource_path('images/request_post.png')))
            elif request_data.get('method') == 'PUT':
                item.setIcon(0, QIcon(resource_path('images/request_put.png')))
            elif request_data.get('method') == 'DELETE':
                item.setIcon(0, QIcon(resource_path('images/request_delete.png')))

        # Store the type in the first column
        item.setData(1, 0, item_data['type'])

        # Store the request data in the second column if it's a request
        if item_data['type'] == 'request':
            item.setData(2, 0, request_data)
            
        if 'children' in item_data:  # FUCKED
            dict_to_tree(self, item_data['children'], item)

def pretty_response_code(response_code):
    # replace 200 with 200 OK ✅
    response_code = response_code.replace("200", "200 OK ✅")
    # replace 201 with 201 Created ✅
    response_code = response_code.replace("201", "201 Created ✅")
    # replace 204 with 204 No Content ✅
    response_code = response_code.replace("204", "204 No Content ✅")
    # replace 400 with 400 Bad Request 
    response_code = response_code.replace("400", "400 Bad Request 🚫")
    # replace 401 with 401 Unauthorized
    response_code = response_code.replace("401", "401 Unauthorized 🚫")
    # replace 403 with 403 Forbidden
    response_code = response_code.replace("403", "403 Forbidden 🚫")
    # replace 404 with 404 Not Found
    response_code = response_code.replace("404", "404 Not Found 🚫")
    # replace 405 with 405 Method Not Allowed
    response_code = response_code.replace("405", "405 Method Not Allowed 🚫")
    # replace 500 with 500 🚫
    response_code = response_code.replace("500", "500 🚫")
    # replace 502 with 502 Bad Gateway
    response_code = response_code.replace("502", "502 Bad Gateway 🚫")
    # replace 503 with 503 Service Unavailable
    response_code = response_code.replace("503", "503 Service Unavailable 🚫")
    # replace 504 with 504 Gateway Timeout
    response_code = response_code.replace("504", "504 Gateway Timeout 🚫")
    # replace 505 with 505 HTTP Version Not Supported
    response_code = response_code.replace("505", "505 HTTP Version Not Supported 🚫")
    return response_code