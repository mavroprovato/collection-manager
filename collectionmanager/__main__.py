"""Launches the application user interface.
"""
import sys

import PyQt5.QtWidgets as QtWidgets

from .windows import main as main_window

APP_NAME = 'collection-manager'


def main():
    """The main entry point of the application.
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = main_window.MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
