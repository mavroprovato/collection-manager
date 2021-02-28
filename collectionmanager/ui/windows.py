"""
The main application window
"""
import PyQt5.Qt as Qt
import PyQt5.QtWidgets as QtWidgets

from collectionmanager.threads import scandirectory
import collectionmanager.ui.ui.main_window as main_window
from collectionmanager.ui.widgets import MainWidget


class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    """The main application window
    """
    def __init__(self, parent=None):
        """Constructor for the main application window.

        :param parent: The parent widget.
        """
        super(MainWindow, self).__init__(parent)

        self.mainWidget = MainWidget(self)
        self.scanDirectoryThread = scandirectory.ScanDirectoryThread(self)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWindow, self).setupUi(self)

        self.setCentralWidget(self.mainWidget)

        # Set up the actions
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
