"""A thread that scans a directory
"""
import PyQt5.QtCore as QtCore

from collectionmanager import db


class ScanDirectoryThread(QtCore.QThread):
    """Background thread that scans directories for media files
    """
    directoryScanned = QtCore.pyqtSignal()

    def __init__(self, parent):
        """The thread constructor.

        :param parent: The parent directory.
        """
        super().__init__(parent)

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
        db.Database().add_directory(self.directory)

        self.directoryScanned.emit()
