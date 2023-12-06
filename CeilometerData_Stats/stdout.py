from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QTextCursor


class TextRedirector(object):
    def __init__(self, text_widget):
        """Constructor"""
        self.output = text_widget

    def write(self, string):
        """Add text to the end and ensure it's visible"""
        self.output.moveCursor(QTextCursor.End)
        self.output.insertPlainText(string)
        self.output.moveCursor(QTextCursor.End)
        QApplication.processEvents()
        
    def flush(self):
        """Flush method for compatibility with stdout"""
        pass
