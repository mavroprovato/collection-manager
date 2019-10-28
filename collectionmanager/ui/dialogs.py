import datetime

from PyQt5 import QtWidgets as QtWidgets

from ..ui.ui import track_details
from ..db import models


class TrackDetailDialog(QtWidgets.QDialog, track_details.Ui_Dialog):
    """The dialog that enables editing of track details.
    """
    def __init__(self, parent):
        """Constructor for the track detail dialog.

        :param parent: The parent widget.
        """
        super(TrackDetailDialog, self).__init__(parent)

        self.setupUi()
        self.track = None

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs:
        """
        super(TrackDetailDialog, self).setupUi(self)

        self.buttonBox.rejected.connect(self.close)

    def set_track(self, track: models.Track):
        """Set the dialog information from a track.

        :param track: The track.
        """
        self.track = track

        self.set_summary_tab()
        self.set_information_tab()

    def set_summary_tab(self):
        """Set the UI elements of the summary tab
        """
        # if self.track.album_art is not None:
        #     pix_map = QPixmap()
        #     pix_map.loadFromData(self.track_info.album_art.data)
        #     self.album_cover_label.setPixmap(pix_map)
        self.summary_label.setText(self.get_track_summary())
        timedelta_str = str(datetime.timedelta(seconds=round(self.track.length)))
        if timedelta_str.startswith("0:"):
            timedelta_str = timedelta_str[2:]
        self.label_value_label.setText(timedelta_str)
        self.bit_rate_value_label.setText('{} Kbps'.format(round(self.track.encoder_info['bitrate'] / 1000)))
        self.bit_rate_mode_value_label.setText({
            'BitrateMode.UNKNOWN': 'Unknown',
            'BitrateMode.CBR': 'Constant Bitrate',
            'BitrateMode.VBR': 'Variable Bitrate',
            'BitrateMode.ABR': 'Average Bitrate',
        }[self.track.encoder_info['bitrate_mode']])
        self.sample_rate_value_label.setText(str(self.track.encoder_info['sample_rate']))
        self.encoder_value_label.setText(self.track.encoder_info['encoder_info'])

    def set_information_tab(self):
        """Set the UI elements of the details tab
        """
        self.name_line_edit.setText(self.track.name)
        self.artist_line_edit.setText(self.track.track_artist.name)
        self.album_artist_edit.setText(self.track.album_artist.name)
        self.album_line_edit.setText(self.track.album.name)
        self.year_line_edit.setText(str(self.track.album.year))
        self.track_number_line_eEdit.setText(str(self.track.number))
        self.disk_number_line_edit.setText(str(self.track.disk_number))

    def get_track_summary(self):
        """Return the track summary from the file info.

        :return: The track summary as a string.
        """
        summary = ""
        if self.track.name:
            if self.track.name:
                summary = "<b>{}</b>".format(self.track.name)
            else:
                return summary
            if self.track.track_artist:
                summary += " by <b>{}</b>".format(self.track.track_artist.name)
            else:
                return summary
            if self.track.album:
                summary += " on <b>{}</b>".format(self.track.album.name)

        return summary
