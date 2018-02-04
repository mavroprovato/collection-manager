"""
The application module
"""
import datetime
import mutagen.mp3
import PyQt5.Qt as Qt
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import sys

import collectionmanager.database as database
import collectionmanager.models as models
import collectionmanager.ui.main_window as main_window
import collectionmanager.ui.main_widget as main_widget
import collectionmanager.ui.track_details as track_details
import collectionmanager.track_info as track_info


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
        """Set up the user interface.

        :param kwargs:
        """
        super(TrackDetailDialog, self).setupUi(self)

        self.buttonBox.rejected.connect(self.close)

    def set_file(self, file_path):
        """Set the dialog information from a file.

        :param file_path: The file path.
        """
        info = track_info.TrackInfo(file_path)

        self.summaryLabel.setText(self.get_track_summary(info))

        self.nameLineEdit.setText(info.name)
        self.artistLineEdit.setText(info.artist)
        self.albumArtistEdit.setText(info.album_artist)
        self.albumLineEdit.setText(info.album)
        self.yearLineEdit.setText(str(info.year))
        self.trackNumberLineEdit.setText(str(info.track_number))

        self.fileInfoLabel.setText(self.get_file_info_text(info))

    @staticmethod
    def get_track_summary(info):
        """Return the track summary from the file info.

        :param info: The file info
        :return: The track summary as a string.
        """
        summary = ""
        if info.name:
            summary = "<b>{}</b>".format(info.name)
        else:
            return summary
        if info.artist:
            summary += " by <b>{}</b>".format(info.artist)
        else:
            return summary
        if info.album:
            summary += " on <b>{}</b>".format(info.album)

        return summary

    @staticmethod
    def get_file_info_text(info):
        """Returns the file info text to be displayed in the file info label

        :param info: The file info.
        :return: The file info text.
        """
        timedelta_str = str(datetime.timedelta(seconds=round(info.info.length)))
        if timedelta_str.startswith("0:"):
            timedelta_str = timedelta_str[2:]
        return """
            <table>
                <tr><td><b>Length:</b></td><td>{}</td>
                <tr><td><b>Bit rate:</b></td><td>{} Kbps</td>
                <tr><td><b>Bit rate mode:</b></td><td>{}</td>
                <tr><td><b>Sample rate:</b></td><td>{}</td>
                <tr><td><b>Encoder:</b></td><td>{}</td>
            </table>
        """.format(
            timedelta_str,
            round(info.info.bitrate / 1000),
            {
                mutagen.mp3.BitrateMode.UNKNOWN: 'Unknown',
                mutagen.mp3.BitrateMode.CBR: 'Constant Bitrate',
                mutagen.mp3.BitrateMode.VBR: 'Variable Bitrate',
                mutagen.mp3.BitrateMode.ABR: 'Average Bitrate',
            }[info.info.bitrate_mode],
            info.info.sample_rate,
            info.info.encoder_info
        )


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
