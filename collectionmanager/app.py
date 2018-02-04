"""
The application module
"""
import sys

import PyQt5.Qt as Qt
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

import collectionmanager.database as database
import collectionmanager.models as models
import collectionmanager.ui.main_widget as main_widget
import collectionmanager.ui.main_window as main_window
from collectionmanager.dialogs import TrackDetailDialog


class MainWidget(QtWidgets.QWidget, main_widget.Ui_Form):
    """The main application widget
    """
    def __init__(self, parent, db):
        """Constructor for the main application window.

        :param parent: The parent widget.
        """
        super(MainWidget, self).__init__(parent)

        self.trackModel = models.TrackModel(self, db)
        self.trackDetailsDialog = TrackDetailDialog(self)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWidget, self).setupUi(self)

        self.trackTableView.setModel(self.trackModel)
        self.trackTableView.doubleClicked.connect(self.track_table_double_clicked)
        self.trackModel.refresh()

    def track_table_double_clicked(self, index):
        """Called when the track table is double clicked.

        :param index: The model index.
        """
        file_path = self.trackModel.file_path_for(index)
        self.trackDetailsDialog.set_file(file_path)
        self.trackDetailsDialog.exec_()


class ScanDirectoryThread(QtCore.QThread):
    """Background thread that scans directories for media files
    """
    directoryScanned = QtCore.pyqtSignal()

    def __init__(self, parent, db):
        """The thread constructor.

        :param parent: The parent directory.
        :param db: The database connection.
        """
        super(ScanDirectoryThread, self).__init__(parent)

        self.db = db
        self.directory = None

    def scan_directory(self, directory):
        """Scan a directory.

        :param directory: The directory to scan.
        """
        self.directory = directory

        if not self.isRunning():
            self.start()

    def run(self):
        """The main thread actions.
        """
        self.db.add_directory(self.directory)
        self.db.save()

        self.directoryScanned.emit()


class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    """The main application window
    """
    def __init__(self, parent=None):
        """Constructor for the main application window.

        :param parent: The parent widget.
        """
        super(MainWindow, self).__init__(parent)

        self.db = database.Database(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation))
        self.mainWidget = MainWidget(self, self.db)
        self.scanDirectoryThread = ScanDirectoryThread(self, self.db)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWindow, self).setupUi(self)

        self.setCentralWidget(self.mainWidget)

        self.fileOpenAction.triggered.connect(self.open_directory)
        self.fileQuitAction.triggered.connect(QtWidgets.qApp.quit)

        self.scanDirectoryThread.directoryScanned.connect(self.directory_scanned)

    def open_directory(self):
        """Called when the user selects a directory to open.
        """
        directory = Qt.QFileDialog.getExistingDirectory(parent=self)
        if directory:
            self.scanDirectoryThread.scan_directory(directory)

    def directory_scanned(self):
        """Called when a directory has been scanned.
        """
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
