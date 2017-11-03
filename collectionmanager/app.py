"""
The application module
"""
import PyQt5.Qt as Qt
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import sys

import collectionmanager.database as database
import collectionmanager.models as models
import collectionmanager.ui.main_window as main_window
import collectionmanager.ui.main_widget as main_widget


class MainWidget(QtWidgets.QWidget, main_widget.Ui_Form):
    """The main application widget
    """
    def __init__(self, parent, db):
        """Constructor for the main application window.

        :param parent: The parent window.
        """
        super(MainWidget, self).__init__(parent)

        self.trackModel = models.TrackModel(self, db)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWidget, self).setupUi(self)

        self.trackTableView.setModel(self.trackModel)
        self.trackModel.refresh()


class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    """The main application window
    """
    def __init__(self, parent=None):
        """Constructor for the main application window.

        :param parent: The parent window.
        """
        super(MainWindow, self).__init__(parent)

        self.db = database.Database(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation))
        self.mainWidget = MainWidget(self, self.db)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWindow, self).setupUi(self)

        self.setCentralWidget(self.mainWidget)

        self.fileOpenAction.triggered.connect(self.open_directory)
        self.fileQuitAction.triggered.connect(QtWidgets.qApp.quit)

    def open_directory(self):
        """Called when the user selects a directory to open.
        """
        directory = Qt.QFileDialog.getExistingDirectory(parent=self)
        if directory:
            self.db.add_directory(directory)
            self.db.save()
            self.mainWidget.trackModel.refresh()


def main():
    """The main entry point of the application.
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('collection-manager')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
