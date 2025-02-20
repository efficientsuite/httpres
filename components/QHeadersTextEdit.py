from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtWidgets import QPlainTextEdit

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        # Format for JSON strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#C28650"))
        
        # Format for JSON keys
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#3fafff"))
        
        # Format for JSON numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#C28650"))
        
        # Format for JSON null
        null_format = QTextCharFormat()
        null_format.setForeground(QColor("white")) 

        # Format for JSON boolean true
        true_format = QTextCharFormat()
        true_format.setForeground(QColor("green")) 

        # Format for JSON boolean false
        false_format = QTextCharFormat()
        false_format.setForeground(QColor("green")) 

        # Define regular expressions for JSON components
        self.highlighting_rules = [
            (QRegularExpression(r'"(?:[^"\\]|\\.)*"'), string_format),   # JSON strings
            (QRegularExpression(r'"(?:[^"\\]|\\.)*"\s*:'), key_format),  # JSON keys
            (QRegularExpression(r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b'), number_format),  # JSON numbers
            (QRegularExpression(r'":\s*null'), null_format),  # JSON null
            (QRegularExpression(r'":\s*true'), true_format),  # JSON boolean true
            (QRegularExpression(r'":\s*false'), false_format)  # JSON boolean false
        ]

    def highlightBlock(self, text):
        # Apply each rule to the text block
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, format)

class QHeadersTextEdit(QPlainTextEdit):

    # add the syntax highlighter to the text edit
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.highlighter = JsonHighlighter(self.document())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            # Insert two spaces instead of a tab character
            self.insertPlainText('  ')  # Two spaces
            return  # Prevent the default tab behavior
        super().keyPressEvent(event)  # Call the base class method for other keys
