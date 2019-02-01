import datetime

import mutagen.mp3
from PyQt5 import QtWidgets as QtWidgets

from collectionmanager import track_info as track_info
from collectionmanager.ui import track_details as track_details


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
        self.yearLineEdit.setText(info.year)
        self.trackNumberLineEdit.setText(info.track_number)
        self.diskNumberLineEdit.setText(info.disc_number)

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
