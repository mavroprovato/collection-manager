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
import collectionmanager.ui.track_details as track_details


class TrackDetailDialog(QtWidgets.QDialog, track_details.Ui_Dialog):
    """The dialog that enables editing of track details.
    """
    def __init__(self, parent):
        """Constructor for the track detail dialog.

        :param parent: The parent widget.
        """
        super(TrackDetailDialog, self).__init__(parent)

        self.setupUi()

    def setupUi(self, **kwargs):
        super(TrackDetailDialog, self).setupUi(self)

        self.buttonBox.rejected.connect(self.close)


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
