"""
The application module
"""
import PyQt5.QtWidgets as QtWidgets
import sys

import collectionmanager.ui.main_window as main_window


class CollectionManagerApp(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    """
    The application class
    """
    def __init__(self, parent=None):
        """Constructor for the main application class.

        :param parent: The parent window.
        """
        super(CollectionManagerApp, self).__init__(parent)

        self.setupUi(self)

        # Connect the application actions
        self.actionQuit.triggered.connect(QtWidgets.qApp.quit)


def main():
    """
    The main entry point of the application.
    """
    app = QtWidgets.QApplication(sys.argv)
    form = CollectionManagerApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()