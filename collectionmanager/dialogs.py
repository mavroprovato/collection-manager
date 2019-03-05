import datetime

import mutagen.mp3
from PyQt5 import QtWidgets as QtWidgets
from PyQt5.QtGui import QPixmap

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
        self.track_info = None

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
        self.track_info = track_info.TrackInfo(file_path)

        self.set_summary_tab()
        self.set_details_tab()

    def set_summary_tab(self):
        """Set the UI elements of the summary tab
        """
        if self.track_info.album_art is not None:
            pix_map = QPixmap()
            pix_map.loadFromData(self.track_info.album_art.data)
            self.album_cover_label.setPixmap(pix_map)
        self.summary_label.setText(self.get_track_summary())
        timedelta_str = str(datetime.timedelta(seconds=round(self.track_info.length)))
        if timedelta_str.startswith("0:"):
            timedelta_str = timedelta_str[2:]
        self.label_value_label.setText(timedelta_str)
        self.bit_rate_value_label.setText('{} Kbps'.format(round(self.track_info.bitrate / 1000)))
        self.bit_rate_mode_value_label.setText({
            mutagen.mp3.BitrateMode.UNKNOWN: 'Unknown',
            mutagen.mp3.BitrateMode.CBR: 'Constant Bitrate',
            mutagen.mp3.BitrateMode.VBR: 'Variable Bitrate',
            mutagen.mp3.BitrateMode.ABR: 'Average Bitrate',
        }[self.track_info.bitrate_mode])
        self.sample_rate_value_label.setText(str(self.track_info.sample_rate))
        self.encoder_value_label.setText(self.track_info.encoder_info)

    def set_details_tab(self):
        """Set the UI elements of the details tab
        """
        self.name_line_edit.setText(self.track_info.name)
        self.artist_line_edit.setText(self.track_info.artist)
        self.album_artist_edit.setText(self.track_info.album_artist)
        self.album_line_edit.setText(self.track_info.album)
        self.year_line_edit.setText(self.track_info.year)
        self.track_number_line_eEdit.setText(self.track_info.track_number)
        self.disk_number_line_edit.setText(self.track_info.disk_number)

    def get_track_summary(self):
        """Return the track summary from the file info.

        :return: The track summary as a string.
        """
        summary = ""
        if self.track_info:
            if self.track_info.name:
                summary = "<b>{}</b>".format(self.track_info.name)
            else:
                return summary
            if self.track_info.artist:
                summary += " by <b>{}</b>".format(self.track_info.artist)
            else:
                return summary
            if self.track_info.album:
                summary += " on <b>{}</b>".format(self.track_info.album)

        return summary
