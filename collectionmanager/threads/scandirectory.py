"""A thread that scans a directory
"""
import PyQt5.QtCore as QtCore


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
